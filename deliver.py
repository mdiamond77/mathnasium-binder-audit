import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import CENTERS, CC_RECIPIENT

COLS = ["student_name", "last_progress_check", "last_assessment", "days_since", "status", "reason"]
HEADERS = ["Student Name", "Last Progress Check", "Last Assessment", "Days Since Last Milestone", "Status", "Reason"]


def _th(text: str) -> str:
    return "<th style='padding:6px 12px;border:1px solid #ddd;background:#f5f5f5;text-align:left;'>{}</th>".format(text)


def _td(text: str) -> str:
    return "<td style='padding:6px 12px;border:1px solid #ddd;'>{}</td>".format(text)


def _table(rows: list[dict]) -> str:
    header_html = "".join(_th(h) for h in HEADERS)
    if rows:
        body_html = "".join(
            "<tr>" + "".join(_td(row.get(c, "")) for c in COLS) + "</tr>"
            for row in rows
        )
    else:
        body_html = "<tr><td colspan='{}' style='color:#888;font-style:italic;padding:6px 12px;'>No students flagged.</td></tr>".format(len(HEADERS))
    return (
        "<table style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px;'>"
        "<tr>{}</tr>{}</table>"
    ).format(header_html, body_html)


def build_html(center_name: str, month_label: str, rows: list[dict]) -> str:
    divider = "<hr style='border:none;border-top:2px solid #ccc;margin:24px 0;'>"
    if rows:
        body = (
            "<p>Hi Team,</p>"
            "<p>Below is your binder audit list of active students who have not had a recent "
            "progress check or assessment. Please review and take any needed action.</p>"
            "{divider}{table}{divider}"
            "<p style='color:#999;font-size:12px;'><em>This email sends automatically on the 15th of each month. "
            "Questions? Contact matt.diamond@mathnasium.com.</em></p>"
        ).format(divider=divider, table=_table(rows))
    else:
        body = (
            "<p>Hi Team,</p>"
            "<p>Good news \u2014 no active students were flagged in this month\u2019s binder audit.</p>"
            "<p style='color:#999;font-size:12px;'><em>This email sends automatically on the 15th of each month. "
            "Questions? Contact matt.diamond@mathnasium.com.</em></p>"
        )
    return (
        "<html><body style='font-family:Arial,sans-serif;font-size:14px;max-width:900px;margin:0 auto;padding:20px;'>"
        "{}</body></html>"
    ).format(body)


def send_email(center_name: str, month_label: str, html: str) -> None:
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    if not smtp_user or not smtp_password:
        raise EnvironmentError("SMTP_USER and SMTP_PASSWORD environment variables must be set.")

    recipient = CENTERS[center_name]["recipient"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Binder Audit \u2014 {} \u2014 {}".format(center_name, month_label)
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Cc"] = CC_RECIPIENT

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [recipient, CC_RECIPIENT], msg.as_string())


def deliver(center_data: dict, month_label: str) -> None:
    for center_name, rows in center_data.items():
        html = build_html(center_name, month_label, rows)
        send_email(center_name, month_label, html)
        status = "({} flagged)".format(len(rows)) if rows else "(no students flagged)"
        print("Sent email for {} {}".format(center_name, status))
