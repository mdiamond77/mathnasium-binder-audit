from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"

RADIUS_LOGIN_URL = "https://radius.mathnasium.com"
STUDENT_REPORT_URL = "https://radius.mathnasium.com/StudentReport"

CENTERS = {
    "Englewood": {"radius_id": "2428", "recipient": "englewood@mathnasium.com"},
    "Teaneck":   {"radius_id": "2871", "recipient": "teaneck@mathnasium.com"},
}
CC_RECIPIENT = "matt.diamond@mathnasium.com"

# Column names verified from real Radius Student Report export (2026-04-19)
COL_STUDENT_NAME        = "Student Name"
COL_ENROLLMENT          = "Enrollment Status"
COL_CENTER              = "Center"
COL_LAST_PROGRESS_CHECK = "Last Progress Check"
COL_LAST_ASSESSMENT     = "Last Assessment"
COL_LAST_ATTENDANCE     = "Last Attendance"

THRESHOLD_DAYS = 60
