import hashlib
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infra.sandbox.adapter import (
    ReadFileResult,
    SandboxCreateResult,
    SandboxDestroyResult,
    SandboxOpResult,
)
from src.lote3.lote3_runner import Lote3Runner
from src.lote3.response_schema import WriteFileIntent


class FakeClient:
    def __init__(self, intent: WriteFileIntent) -> None:
        self.intent = intent

    def get_completion(self, instruction: str):
        return (self.intent.model_dump_json(), self.intent)


class FakeAdapter:
    def __init__(
        self,
        *,
        create_success: bool = True,
        copy_success: bool = True,
        read_override: str | None = None,
    ) -> None:
        self.create_success = create_success
        self.copy_success = copy_success
        self.read_override = read_override
        self.files: dict[str, str] = {}
        self.create_calls = 0
        self.copy_calls = 0
        self.destroy_calls = 0

    def create(self, baseline_ref: str) -> SandboxCreateResult:
        self.create_calls += 1
        if not self.create_success:
            return SandboxCreateResult(
                success=False,
                status_code=500,
                materialized_ref=baseline_ref,
                error="create failed",
            )
        return SandboxCreateResult(
            sandbox_id="sandbox-test",
            success=True,
            status_code=201,
            materialized_ref=baseline_ref,
        )

    def write_text_file(self, dest_path: str, content: str) -> SandboxOpResult:
        self.copy_calls += 1
        if not self.copy_success:
            return SandboxOpResult(success=False, error_message="copy failed")

        self.files[dest_path] = content
        return SandboxOpResult(success=True, bytes_written=len(content.encode("utf-8")))

    def read_text_file(self, path: str) -> ReadFileResult:
        content = self.read_override if self.read_override is not None else self.files.get(path, "")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return ReadFileResult(success=True, content=content, hash_sha256=digest)

    def destroy(self) -> SandboxDestroyResult:
        self.destroy_calls += 1
        return SandboxDestroyResult(success=True, exit_status="KILLED")


class FakeLedger:
    def __init__(self) -> None:
        self.run_id = "test-run-id"
        self.ledger_path = Path("memory://ledger")
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


class Lote3RunnerTests(unittest.TestCase):
    def test_successful_mutation_emits_successful_terminal_event(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="PROVA L3",
            explanation="fixture",
        )
        adapter = FakeAdapter()
        ledger = FakeLedger()
        runner = Lote3Runner(adapter=adapter, client=FakeClient(intent), ledger=ledger)

        runner.run("crie o arquivo de prova")

        self.assertEqual(adapter.create_calls, 1)
        self.assertEqual(adapter.copy_calls, 1)
        self.assertEqual(adapter.destroy_calls, 1)
        self.assertTrue(any(event["event_type"] == "POLICY_CHECK" and event["status"] == "OK" for event in ledger.events))
        self.assertTrue(any(event["event_type"] == "SANDBOX_MUTATION" and event["status"] == "OK" for event in ledger.events))
        self.assertTrue(any(event["event_type"] == "EVIDENCE_CHECK" and event["status"] == "OK" for event in ledger.events))
        self.assertEqual(ledger.finished_events[-1]["final_outcome"], "SUCCESS")
        self.assertEqual(ledger.finished_events[-1]["evidence_level"], "STRONG_DETERMINISTIC_PROVED")

    def test_illegal_path_fails_closed_before_sandbox_creation(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="../../../../etc/passwd",
            content="blocked",
            explanation="fixture",
        )
        adapter = FakeAdapter()
        ledger = FakeLedger()
        runner = Lote3Runner(adapter=adapter, client=FakeClient(intent), ledger=ledger)

        runner.run("tente escapar do workspace", expected_fail=True)

        self.assertEqual(adapter.create_calls, 0)
        self.assertTrue(any(event["event_type"] == "POLICY_CHECK" and event["status"] == "FAIL" for event in ledger.events))
        self.assertEqual(ledger.finished_events[-1]["final_outcome"], "SECURITY_VIOLATION")

    def test_copy_failure_is_reported_as_sandbox_failure(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="PROVA L3",
            explanation="fixture",
        )
        adapter = FakeAdapter(copy_success=False)
        ledger = FakeLedger()
        runner = Lote3Runner(adapter=adapter, client=FakeClient(intent), ledger=ledger)

        runner.run("falhe na copia")

        self.assertEqual(adapter.create_calls, 1)
        self.assertEqual(adapter.copy_calls, 1)
        self.assertEqual(adapter.destroy_calls, 1)
        self.assertTrue(any(event["event_type"] == "SANDBOX_MUTATION" and event["status"] == "ERROR" for event in ledger.events))
        self.assertEqual(ledger.finished_events[-1]["final_outcome"], "SANDBOX_FAILURE")

    def test_policy_guard_warnings_do_not_block_shadow_mode(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="#!/bin/bash\necho shadow warning",
            explanation="fixture",
        )
        adapter = FakeAdapter()
        ledger = FakeLedger()
        runner = Lote3Runner(adapter=adapter, client=FakeClient(intent), ledger=ledger)

        runner.run("grave um script para observacao")

        policy_events = [event for event in ledger.events if event["event_type"] == "POLICY_CHECK"]
        self.assertEqual(policy_events[-1]["status"], "OK")
        self.assertEqual(policy_events[-1]["payload"]["policy_action"], "warning")
        self.assertEqual(ledger.finished_events[-1]["final_outcome"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
