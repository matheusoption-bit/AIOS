import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ci.check_disallowed_calls import ViolationCollector


class CIGuardrailTests(unittest.TestCase):
    def _collect_messages(self, relative_path: str, source: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(source), encoding="utf-8")
            collector = ViolationCollector(path)
            collector.visit(__import__("ast").parse(path.read_text(encoding="utf-8"), filename=str(path)))
            return [message for _, message in collector.violations]

    def test_detects_os_popen(self) -> None:
        messages = self._collect_messages(
            "src/example.py",
            """
            import os
            os.popen("id")
            """,
        )
        self.assertTrue(any("os.popen" in message for message in messages))

    def test_detects_exec_builtin(self) -> None:
        messages = self._collect_messages(
            "tests/example_test.py",
            """
            exec("print('boom')")
            """,
        )
        self.assertTrue(any("builtin 'exec'" in message for message in messages))

    def test_detects_dynamic_import_bypass(self) -> None:
        messages = self._collect_messages(
            "src/example.py",
            """
            getattr(__import__("os"), "system")("id")
            """,
        )
        self.assertTrue(any("dynamic getattr import" in message for message in messages))

    def test_detects_direct_copy_in_call(self) -> None:
        messages = self._collect_messages(
            "src/example.py",
            """
            adapter.copy_in("host.txt", "/tmp/aios_workspace/outputs/proof.txt")
            """,
        )
        self.assertTrue(any("copy_in" in message for message in messages))

    def test_write_text_file_is_not_classified_as_admin_call(self) -> None:
        messages = self._collect_messages(
            "src/example.py",
            """
            sandbox.write_text_file("/tmp/aios_workspace/outputs/proof.txt", "ok")
            """,
        )

        self.assertFalse(any("write_text_file" in message for message in messages), messages)
