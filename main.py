import argparse
import traceback
from datetime import date

from download import download_reports
from process import process
from deliver import deliver
from run_log import write_log


def get_month_label(month_str: str) -> str:
    year, month = month_str.split("-")
    month_name = date(int(year), int(month), 1).strftime("%B")
    return "{} {}".format(month_name, year)


def main():
    parser = argparse.ArgumentParser(description="Run Binder Audit automation.")
    parser.add_argument(
        "--trigger",
        default="auto",
        choices=["auto", "manual"],
        help="How this run was triggered (default: auto)",
    )
    parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to process in YYYY-MM format (default: current month)",
    )
    args = parser.parse_args()

    month_str = args.month
    month_label = get_month_label(month_str)

    print("Running Binder Audit for {}".format(month_label))

    try:
        print("Downloading Student Report...")
        paths = download_reports(month_label)

        print("Processing data...")
        center_data = process(paths["student_report"])

        print("Sending emails...")
        deliver(center_data, month_label)

        write_log(month_str, success=True, trigger=args.trigger)
        print("Done.")

    except Exception as e:
        error_msg = traceback.format_exc()
        print("ERROR: {}".format(e))
        print(error_msg)
        write_log(month_str, success=False, trigger=args.trigger, error=error_msg)
        raise


if __name__ == "__main__":
    main()
