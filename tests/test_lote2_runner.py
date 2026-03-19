import os
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lote2.lote2_runner import LEGACY_MODE_ENV_VAR, Lote2Runner


class FakeLedger:
    def __init__(self) -> None:
        self.run_id = "legacy-run-id"
        self.ledger_path = Path("memory://legacy-ledger")
        self.events: list[dict] = []
        self.finished_events: list[dict] = []
        self.ledger_degraded = False

    def emit(self, event_type: str, stage: str, status: str, payload: dict):
        event = {
            "event_type": event_type,
            "stage": stage,
            "status": status,
            "payload": payload,
        }
        self.events.append(event)
        return event

    def emit_run_finished(self, final_outcome: str, evidence_level: str = "NONE", summary: str = "", **extra_payload):
        event = {
            "final_outcome": final_outcome,
            "evidence_level": evidence_level,
            "summary": summary,
            **extra_payload,
        }
        self.finished_events.append(event)
        return event

    def ensure_not_degraded(self, context: str) -> None:
        return None


class Lote2RunnerTests(unittest.TestCase):
    def test_lote2_is_blocked_without_explicit_legacy_flag(self) -> None:
        previous_flag = os.environ.pop(LEGACY_MODE_ENV_VAR, None)
        ledger = FakeLedger()
        runner = Lote2Runner(adapter=object(), client=object(), ledger=ledger)

        try:
            with self.assertRaises(RuntimeError):
                runner.run("comando legado")
        finally:
            if previous_flag is not None:
                os.environ[LEGACY_MODE_ENV_VAR] = previous_flag

        self.assertTrue(any(event["event_type"] == "POLICY_CHECK" and event["status"] == "FAIL" for event in ledger.events))
        self.assertEqual(ledger.finished_events[-1]["final_outcome"], "SECURITY_VIOLATION")


if __name__ == "__main__":
    unittest.main()
