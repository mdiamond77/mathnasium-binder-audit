import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from config import INPUT_DIR, RADIUS_LOGIN_URL, STUDENT_REPORT_URL, CENTERS

CENTER_IDS = [c["radius_id"] for c in CENTERS.values()]


def _login(page) -> None:
    username = os.environ.get("RADIUS_USERNAME")
    password = os.environ.get("RADIUS_PASSWORD")
    if not username or not password:
        raise EnvironmentError("RADIUS_USERNAME and RADIUS_PASSWORD environment variables must be set.")
    page.goto(RADIUS_LOGIN_URL)
    page.fill("#UserName", username)
    page.fill("#Password", password)
    page.click("#login")
    page.wait_for_load_state("networkidle")


def download_student_report(page, month_label: str) -> Path:
    out_path = INPUT_DIR / "StudentReport_{}.xlsx".format(month_label)

    page.goto(STUDENT_REPORT_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # Set enrollment status to Enrolled (value "3")
    page.evaluate("""
        const dd = $('#enrollmentFiltersDropDownList').data('kendoDropDownList');
        dd.value('3');
        dd.trigger('change');
    """)
    page.wait_for_timeout(500)

    # Select both centers via Kendo MultiSelect
    page.evaluate(
        """(ids) => {
            const ms = $('#AllCenterListMultiSelect').data('kendoMultiSelect');
            ms.value(ids);
            ms.trigger('change');
        }""",
        json.dumps(CENTER_IDS),
    )
    page.wait_for_timeout(500)

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    with page.expect_download(timeout=60000) as dl:
        page.click("#btnExport")
    dl.value.save_as(out_path)

    return out_path


def download_reports(month_label: str) -> dict:
    INPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with browser:
            context = browser.new_context(accept_downloads=True)
            with context:
                page = context.new_page()
                _login(page)
                student_path = download_student_report(page, month_label)

    return {"student_report": student_path}
