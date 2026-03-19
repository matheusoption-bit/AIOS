import warnings
import unittest

from infra.sandbox.adapter import (
    E2BSandboxAdapter,
    E2BUnsafeAdminSandboxAdapter,
    MutationSpec,
    UnsafeSandboxOperationError,
)


class FakeSandboxFiles:
    def __init__(self, content_by_path: dict[str, str | bytes]):
        self._content_by_path = content_by_path

    def read(self, path: str):
        return self._content_by_path[path]


class FakeSandbox:
    def __init__(self, content_by_path: dict[str, str | bytes]):
        self.files = FakeSandboxFiles(content_by_path)


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

    def test_secure_read_text_file_still_works_without_unsafe_opt_in(self) -> None:
        secure_adapter = E2BSandboxAdapter()
        secure_adapter._sandbox = FakeSandbox({"/tmp/proof.txt": "PROVA L3"})

        result = secure_adapter._read_text_result("/tmp/proof.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "PROVA L3")
        self.assertIsNotNone(result.hash_sha256)


if __name__ == "__main__":
    unittest.main()
