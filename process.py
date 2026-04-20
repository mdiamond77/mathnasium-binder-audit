from datetime import date
from pathlib import Path

import pandas as pd

from config import (
    COL_STUDENT_NAME,
    COL_ENROLLMENT,
    COL_CENTER,
    COL_LAST_PROGRESS_CHECK,
    COL_LAST_ASSESSMENT,
    CENTERS,
    THRESHOLD_DAYS,
)

STATUS_NEVER   = "Never assessed / no recorded milestone"
STATUS_60      = "Check-in approaching"
STATUS_90      = "Overdue"
STATUS_120     = "Way overdue — immediate action required"

STATUS_ORDER = {
    STATUS_120:  0,
    STATUS_90:   1,
    STATUS_60:   2,
    STATUS_NEVER: 3,
}


def _assign_status(days: int | None) -> str:
    if days is None:
        return STATUS_NEVER
    if days >= 120:
        return STATUS_120
    if days >= 90:
        return STATUS_90
    return STATUS_60


def _reason(days: int | None, status: str) -> str:
    if status == STATUS_NEVER or days is None or (isinstance(days, float) and pd.isna(days)):
        return "No recorded progress check or assessment — Never assessed"
    return "No milestone in {} days — {}".format(int(days), status)


def process(student_report_path: Path, today: date = None) -> dict:
    if today is None:
        today = date.today()

    df = pd.read_excel(student_report_path)

    # Filter to enrolled only
    df = df[df[COL_ENROLLMENT] == "Enrolled"].copy()

    # Parse date columns
    df[COL_LAST_PROGRESS_CHECK] = pd.to_datetime(df[COL_LAST_PROGRESS_CHECK], errors="coerce")
    df[COL_LAST_ASSESSMENT]     = pd.to_datetime(df[COL_LAST_ASSESSMENT],     errors="coerce")

    # Compute most recent milestone date
    df["most_recent_date"] = df[[COL_LAST_PROGRESS_CHECK, COL_LAST_ASSESSMENT]].max(axis=1)

    # Compute days since milestone (None if no milestone)
    def days_since(row):
        if pd.isna(row["most_recent_date"]):
            return None
        return (today - row["most_recent_date"].date()).days

    df["days_since"] = df.apply(days_since, axis=1)

    # Keep only flagged students: >= threshold days or no milestone at all
    df = df[
        df["days_since"].isna() |
        (df["days_since"] >= THRESHOLD_DAYS)
    ].copy()

    # Assign status and reason
    df["status"] = df["days_since"].apply(_assign_status)
    df["reason"] = df.apply(lambda r: _reason(r["days_since"], r["status"]), axis=1)

    # Format date columns for display
    def fmt_date(val):
        if pd.isna(val):
            return ""
        return val.strftime("%-m/%-d/%Y")

    df["pc_display"]    = df[COL_LAST_PROGRESS_CHECK].apply(fmt_date)
    df["assess_display"] = df[COL_LAST_ASSESSMENT].apply(fmt_date)
    df["days_display"]  = df["days_since"].apply(lambda d: str(int(d)) if d is not None else "")

    center_data = {}
    for center_name in CENTERS:
        center_df = df[df[COL_CENTER] == center_name].copy()

        # Sort: by status bucket, then by days descending (never assessed: alphabetical)
        center_df["status_order"] = center_df["status"].map(STATUS_ORDER)
        never_mask = center_df["status"] == STATUS_NEVER

        sorted_parts = []
        if (~never_mask).any():
            non_never = center_df[~never_mask].sort_values(
                ["status_order", "days_since"], ascending=[True, False]
            )
            sorted_parts.append(non_never)
        if never_mask.any():
            never_df = center_df[never_mask].sort_values(COL_STUDENT_NAME)
            sorted_parts.append(never_df)

        if sorted_parts:
            center_df = pd.concat(sorted_parts)

        rows = []
        for _, row in center_df.iterrows():
            rows.append({
                "student_name":        row[COL_STUDENT_NAME],
                "last_progress_check": row["pc_display"],
                "last_assessment":     row["assess_display"],
                "days_since":          row["days_display"],
                "status":              row["status"],
                "reason":              row["reason"],
            })

        center_data[center_name] = rows

    return center_data
