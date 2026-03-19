import os
import tempfile
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lote2.ledger import L2Ledger
from src.lote2.validate_ledger import validate_ledger


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "ledger"


class ValidateLedgerTests(unittest.TestCase):
    def test_accepts_valid_fixture(self) -> None:
        self.assertTrue(validate_ledger(FIXTURES_DIR / "valid_l2_ledger.jsonl"))

    def test_rejects_invalid_fixture(self) -> None:
        self.assertFalse(validate_ledger(FIXTURES_DIR / "invalid_l2_ledger.jsonl"))

    def test_accepts_hmac_backed_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            previous_key = os.environ.get("AIOS_LEDGER_HMAC_KEY")
            os.environ["AIOS_LEDGER_HMAC_KEY"] = "test-hmac-key"
            try:
                ledger = L2Ledger(ledger_path=ledger_path)
                ledger.emit("LLM_CALL", "PROVIDER", "OK", {
                    "instruction": "fixture",
                    "intent_phase": "OPEN",
                    "intent_kind": "WRITE_FILE_TEXT",
                })
                ledger.emit_run_finished(
                    final_outcome="SUCCESS",
                    evidence_level="STRONG_DETERMINISTIC_PROVED",
                    summary="fixture ok",
                    intent_phase="CLOSE",
                )
                self.assertTrue(validate_ledger(ledger_path))
            finally:
                if previous_key is None:
                    os.environ.pop("AIOS_LEDGER_HMAC_KEY", None)
                else:
                    os.environ["AIOS_LEDGER_HMAC_KEY"] = previous_key


if __name__ == "__main__":
    unittest.main()
