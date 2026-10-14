import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "run_audit.py"
SPEC = importlib.util.spec_from_file_location("run_audit", MODULE)
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)

class RunAuditTests(unittest.TestCase):
    def setUp(self):
        self.env = {"SLOT":"morning","EVENT_NAME":"schedule","SCHEDULE":"30 0 * * *","RUN_ID":"123","RUN_ATTEMPT":"2","COMMIT_SHA":"abc123"}

    def test_records_utc_and_nepal_times(self):
        now = datetime(2026,10,14,0,30,tzinfo=timezone.utc)
        result = audit_module.build_audit(self.env, now)
        self.assertEqual(result["started_at_utc"], "2026-10-14T00:30:00+00:00")
        self.assertEqual(result["started_at_nepal"], "2026-10-14T06:15:00+05:45")
        self.assertEqual(result["run_attempt"], 2)

    def test_rejects_invalid_slot(self):
        with self.assertRaisesRegex(ValueError,"SLOT"):
            audit_module.build_audit({**self.env,"SLOT":"night"})

    def test_rejects_missing_run_identity(self):
        with self.assertRaisesRegex(ValueError,"RUN_ID"):
            audit_module.build_audit({**self.env,"RUN_ID":""})

    def test_rejects_naive_timestamp(self):
        with self.assertRaisesRegex(ValueError,"timezone-aware"):
            audit_module.build_audit(self.env,datetime(2026,10,14))

if __name__ == "__main__":
    unittest.main()
