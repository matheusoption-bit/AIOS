import unittest

from infra.sandbox.adapter import (
    E2BSandboxAdapter,
    E2BSecureWorkspaceSandbox,
    E2BUnsafeAdminSandboxAdapter,
    MutationSpec,
    UnsafeSandboxOperationError,
)


class FakeSandboxFiles:
    def __init__(self, content_by_path: dict[str, str | bytes]):
        self._content_by_path = content_by_path

    def read(self, path: str):
        return self._content_by_path[path]

    def write(self, path: str, content: bytes) -> None:
        self._content_by_path[path] = content


class FakeSandbox:
    def __init__(self, content_by_path: dict[str, str | bytes]):
        self.files = FakeSandboxFiles(content_by_path)


class AdapterHardeningTests(unittest.TestCase):
    def test_default_adapter_blocks_unsafe_primitives(self) -> None:
        adapter = E2BSandboxAdapter()

        with self.assertRaises(UnsafeSandboxOperationError):
            adapter.copy_in("host.txt", "/tmp/aios_workspace/outputs/host.txt")

        with self.assertRaises(UnsafeSandboxOperationError):
            adapter.run_command("echo hello", 1.0)

        with self.assertRaises(UnsafeSandboxOperationError):
            adapter.apply_mutation(MutationSpec(script="echo hello"))

        with self.assertRaises(UnsafeSandboxOperationError):
            adapter.list_files("/tmp")

        with self.assertRaises(UnsafeSandboxOperationError):
            adapter.read_file("/tmp/proof.txt")

    def test_explicit_admin_adapter_keeps_legacy_behavior(self) -> None:
        with self.assertWarns(RuntimeWarning):
            adapter = E2BUnsafeAdminSandboxAdapter()

        result = adapter.run_command("echo hello", 1.0)
        self.assertEqual(result.status, "ERROR")
        self.assertEqual(result.stderr, "Sandbox not created")

    def test_secure_read_text_file_still_works_without_unsafe_opt_in(self) -> None:
        secure_adapter = E2BSandboxAdapter()
        secure_adapter._sandbox = FakeSandbox({"/tmp/proof.txt": "PROVA L3"})

        result = secure_adapter.read_text_file("/tmp/proof.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "PROVA L3")
        self.assertIsNotNone(result.hash_sha256)

    def test_raw_adapter_write_text_file_keeps_generic_behavior(self) -> None:
        adapter = E2BSandboxAdapter()
        sandbox = FakeSandbox({})
        adapter._sandbox = sandbox

        result = adapter.write_text_file("/tmp/escape.txt", "PROVA L3")

        self.assertTrue(result.success)
        self.assertEqual(sandbox.files._content_by_path["/tmp/escape.txt"], b"PROVA L3")

    def test_secure_workspace_write_text_file_rejects_destination_outside_safe_workspace(self) -> None:
        adapter = E2BSandboxAdapter()
        adapter._sandbox = FakeSandbox({})
        secure_sandbox = E2BSecureWorkspaceSandbox(adapter=adapter)

        result = secure_sandbox.write_text_file("/tmp/escape.txt", "PROVA L3")

        self.assertFalse(result.success)
        self.assertIn("workspace seguro", result.error_message or "")

    def test_secure_workspace_write_text_file_accepts_safe_workspace_destination(self) -> None:
        adapter = E2BSandboxAdapter()
        sandbox = FakeSandbox({})
        adapter._sandbox = sandbox
        secure_sandbox = E2BSecureWorkspaceSandbox(adapter=adapter)

        result = secure_sandbox.write_text_file("proofs/output.txt", "PROVA L3")

        self.assertTrue(result.success)
        self.assertEqual(
            sandbox.files._content_by_path["/tmp/aios_workspace/outputs/proofs/output.txt"],
            b"PROVA L3",
        )

    def test_secure_workspace_read_text_file_rejects_path_outside_safe_workspace(self) -> None:
        adapter = E2BSandboxAdapter()
        adapter._sandbox = FakeSandbox({"/tmp/escape.txt": "ESCAPE"})
        secure_sandbox = E2BSecureWorkspaceSandbox(adapter=adapter)

        result = secure_sandbox.read_text_file("/tmp/escape.txt")

        self.assertFalse(result.success)
        self.assertIn("workspace seguro", result.error or "")

    def test_secure_workspace_read_text_file_accepts_safe_workspace_path(self) -> None:
        adapter = E2BSandboxAdapter()
        adapter._sandbox = FakeSandbox({
            "/tmp/aios_workspace/outputs/proofs/input.txt": "PROVA L3",
        })
        secure_sandbox = E2BSecureWorkspaceSandbox(adapter=adapter)

        result = secure_sandbox.read_text_file("proofs/input.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "PROVA L3")
        self.assertIsNotNone(result.hash_sha256)


if __name__ == "__main__":
    unittest.main()
