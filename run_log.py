import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent / "run_log.json"


def read_log() -> list:
    if not LOG_PATH.exists():
        return []
    try:
        with open(LOG_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def write_log(month: str, success: bool, trigger: str = "auto", error: str = "") -> None:
    log = read_log()
    log.append({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trigger": trigger,
        "month": month,
        "success": success,
        "error": error,
    })
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
