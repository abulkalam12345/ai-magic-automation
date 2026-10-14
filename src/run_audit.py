"""Write a timestamped audit record for one draft workflow execution."""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

def build_audit(environment: dict[str, str], now: datetime | None = None) -> dict:
    slot = environment.get("SLOT", "")
    if slot not in {"morning", "evening"}:
        raise ValueError("SLOT must be morning or evening")
    if not environment.get("EVENT_NAME"):
        raise ValueError("EVENT_NAME is required")
    if not environment.get("RUN_ID", "").isdigit() or not environment.get("COMMIT_SHA"):
        raise ValueError("RUN_ID and COMMIT_SHA are required")
    attempt = environment.get("RUN_ATTEMPT", "1")
    if not attempt.isdigit() or int(attempt) < 1:
        raise ValueError("RUN_ATTEMPT must be a positive integer")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Audit timestamp must be timezone-aware")
    return {
        "slot": slot, "event": environment["EVENT_NAME"],
        "schedule_cron": environment.get("SCHEDULE") or None,
        "started_at_utc": current.astimezone(timezone.utc).isoformat(),
        "started_at_nepal": current.astimezone(ZoneInfo("Asia/Kathmandu")).isoformat(),
        "run_id": environment["RUN_ID"], "run_attempt": int(attempt),
        "commit_sha": environment["COMMIT_SHA"],
        "note": "GitHub scheduled events may be delayed or dropped; this records actual start time, not a guaranteed execution time."
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/drafts/_run-audit.json"))
    args = parser.parse_args()
    audit = build_audit(dict(os.environ))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps(audit, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
