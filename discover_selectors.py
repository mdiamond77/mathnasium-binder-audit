"""
Temporary headed browser script to inspect the Radius Student Report page.
Run with:
    RADIUS_USERNAME="your@email.com" RADIUS_PASSWORD="yourpass" python discover_selectors.py

This opens the Student Report in a real browser window so you can:
  1. Use DevTools (Cmd+Option+I) to inspect filter dropdowns and buttons
  2. Download a sample Excel export and check the exact column names

What to record:
  - ID of the Enrollment Status filter (e.g. #SomeDropDownList) and the value for "Enrolled"
  - ID of the Center multi-select (likely #AllCenterListMultiSelect)
  - ID of the Search button (likely #btnsearch)
  - ID of the Export/Excel button (likely #btnExport)
  - Exact column names in the downloaded Excel for:
      * Student Name
      * Center
      * Enrollment Status
      * Last Progress Check date
      * Last Assessment date
"""
import os
from playwright.sync_api import sync_playwright

USERNAME = os.environ.get("RADIUS_USERNAME")
PASSWORD = os.environ.get("RADIUS_PASSWORD")

RADIUS_LOGIN_URL = "https://radius.mathnasium.com"
STUDENT_REPORT_URL = "https://radius.mathnasium.com/StudentReport"

if not USERNAME or not PASSWORD:
    raise EnvironmentError("Set RADIUS_USERNAME and RADIUS_PASSWORD environment variables first.")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    with browser:
        context = browser.new_context(accept_downloads=True)
        with context:
            page = context.new_page()

            print("\n[1/3] Logging into Radius...")
            page.goto(RADIUS_LOGIN_URL)
            page.fill("#UserName", USERNAME)
            page.fill("#Password", PASSWORD)
            page.click("#login")
            page.wait_for_load_state("networkidle")
            print("      Logged in.")

            print("\n[2/3] Navigating to Student Report...")
            page.goto(STUDENT_REPORT_URL)
            page.wait_for_load_state("networkidle")
            print("      Page loaded. Browser window is open.")

            print("\n[3/3] WHAT TO DO NOW:")
            print("  - Open DevTools (Cmd+Option+I → Elements tab)")
            print("  - Find and record the ID of:")
            print("      * Enrollment Status filter dropdown")
            print("      * Center multi-select (or single select)")
            print("      * Search button")
            print("      * Excel export button")
            print("  - Set filters to: Enrolled, both centers")
            print("  - Click Search, then Export to Excel")
            print("  - Open the downloaded file and note the EXACT column headers")
            print("\nPress Enter here when done exploring.")
            input()

print("\nDone. Paste your findings back to Claude.")
