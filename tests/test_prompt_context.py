import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prompt_context import (
    RawLedgerPromptingError,
    assert_not_raw_ledger_source,
    build_deterministic_prompt_context,
)


class PromptContextTests(unittest.TestCase):
    def test_rejects_raw_ledger_source(self) -> None:
        with self.assertRaises(RawLedgerPromptingError):
            assert_not_raw_ledger_source("artifacts/l2/l2_execution_ledger.jsonl")

    def test_builds_deterministic_context(self) -> None:
        context = build_deterministic_prompt_context("  resumo seguro  ")
        self.assertEqual(context["source"], "deterministic_summary")
        self.assertEqual(context["summary"], "resumo seguro")
