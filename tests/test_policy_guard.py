import sys
import unittest
import warnings
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lote3 import policy_guard
from src.lote3.policy_guard import evaluate_write_intent


class PolicyGuardTests(unittest.TestCase):
    def test_shadow_mode_records_blockable_findings_without_blocking(self) -> None:
        result = evaluate_write_intent(
            "/tmp/aios_workspace/outputs/proof.sh",
            "echo hi",
            mode="shadow",
        )

        self.assertEqual(result.mode, "shadow")
        self.assertEqual(result.action, "warning")
        self.assertTrue(result.has_blockable_findings)
        self.assertFalse(result.should_block)

    def test_enforce_mode_blocks_blockable_findings(self) -> None:
        result = evaluate_write_intent(
            "/tmp/aios_workspace/outputs/proof.sh",
            "echo hi",
            mode="enforce",
        )

        self.assertEqual(result.mode, "enforce")
        self.assertEqual(result.action, "blocked_enforcing")
        self.assertTrue(result.has_blockable_findings)
        self.assertTrue(result.should_block)

    def test_enforce_mode_keeps_warning_only_findings_non_blocking(self) -> None:
        result = evaluate_write_intent(
            "/tmp/aios_workspace/outputs/proof.txt",
            "#!/bin/bash\necho hi",
            mode="enforce",
        )

        self.assertEqual(result.action, "warning")
        self.assertFalse(result.has_blockable_findings)
        self.assertFalse(result.should_block)

    def test_invalid_mode_warns_and_degrades_to_shadow(self) -> None:
        previous_flag = policy_guard._INVALID_MODE_WARNING_EMITTED
        policy_guard._INVALID_MODE_WARNING_EMITTED = False
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = evaluate_write_intent(
                    "/tmp/aios_workspace/outputs/proof.sh",
                    "echo hi",
                    mode="invalid-mode",
                )
                evaluate_write_intent(
                    "/tmp/aios_workspace/outputs/proof.sh",
                    "echo hi",
                    mode="invalid-mode",
                )
        finally:
            policy_guard._INVALID_MODE_WARNING_EMITTED = previous_flag

        self.assertEqual(result.mode, "shadow")
        self.assertEqual(result.action, "warning")
        self.assertTrue(result.has_blockable_findings)
        self.assertFalse(result.should_block)
        self.assertEqual(len(caught), 1)
        self.assertIn("degradando para 'shadow'", str(caught[0].message))


if __name__ == "__main__":
    unittest.main()
