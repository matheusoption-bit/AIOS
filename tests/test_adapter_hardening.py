import warnings
import unittest

from infra.sandbox.adapter import (
    E2BSandboxAdapter,
    E2BUnsafeAdminSandboxAdapter,
    MutationSpec,
    UnsafeSandboxOperationError,
)


class AdapterHardeningTests(unittest.TestCase):
    def test_default_adapter_blocks_unsafe_primitives(self) -> None:
        adapter = E2BSandboxAdapter()

        with self.assertRaises(UnsafeSandboxOperationError):
            getattr(adapter, "run_command")("echo hello", 1.0)

        with self.assertRaises(UnsafeSandboxOperationError):
            getattr(adapter, "apply_mutation")(MutationSpec(script="echo hello"))

        with self.assertRaises(UnsafeSandboxOperationError):
            getattr(adapter, "list_files")("/tmp")

        with self.assertRaises(UnsafeSandboxOperationError):
            getattr(adapter, "read_file")("/tmp/proof.txt")

    def test_explicit_admin_adapter_keeps_legacy_behavior(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            adapter = E2BUnsafeAdminSandboxAdapter()

        result = getattr(adapter, "run_command")("echo hello", 1.0)
        self.assertEqual(result.status, "ERROR")
        self.assertEqual(result.stderr, "Sandbox not created")


if __name__ == "__main__":
    unittest.main()
