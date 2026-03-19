import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lote3.path_policy import SAFE_WRITE_ROOT, PathViolationError, validate_safe_path


class PathPolicyTests(unittest.TestCase):
    def test_accepts_relative_path_inside_workspace(self) -> None:
        resolved = validate_safe_path("proofs/output.txt")
        self.assertEqual(resolved, f"{SAFE_WRITE_ROOT}/proofs/output.txt")

    def test_accepts_absolute_path_inside_workspace(self) -> None:
        resolved = validate_safe_path("/tmp/aios_workspace/outputs/docs/output.txt")
        self.assertEqual(resolved, "/tmp/aios_workspace/outputs/docs/output.txt")

    def test_rejects_empty_path(self) -> None:
        with self.assertRaises(PathViolationError):
            validate_safe_path("   ")

    def test_rejects_path_traversal_escape(self) -> None:
        with self.assertRaises(PathViolationError):
            validate_safe_path("../../../../etc/passwd")

    def test_rejects_sibling_workspace_escape(self) -> None:
        with self.assertRaises(PathViolationError):
            validate_safe_path("/tmp/aios_workspace_hacker/loot.txt")

    def test_normalizes_redundant_segments(self) -> None:
        resolved = validate_safe_path("/tmp/aios_workspace/outputs/docs/./nested/../proof.txt")
        self.assertEqual(resolved, "/tmp/aios_workspace/outputs/docs/proof.txt")

    def test_rejects_absolute_path_outside_secure_write_root(self) -> None:
        with self.assertRaises(PathViolationError):
            validate_safe_path("/tmp/aios_workspace/raw/proof.txt")


if __name__ == "__main__":
    unittest.main()
