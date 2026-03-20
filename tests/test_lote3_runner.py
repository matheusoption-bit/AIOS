import json
import hashlib
import sys
import tempfile
import unittest
import warnings
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
from src.lote2.ledger import L2Ledger
from src.lote2.validate_ledger import validate_ledger
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
        read_success: bool = True,
        read_error: str | None = None,
        read_override: str | None = None,
    ) -> None:
        self.create_success = create_success
        self.copy_success = copy_success
        self.read_success = read_success
        self.read_error = read_error
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
        if not self.read_success:
            return ReadFileResult(success=False, error=self.read_error or "read failed")

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


def _load_ledger_events(ledger_path: Path) -> list[dict]:
    with ledger_path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class Lote3RunnerTests(unittest.TestCase):
    def _run_with_real_ledger(self, adapter: FakeAdapter, intent: WriteFileIntent) -> tuple[list[dict], bool]:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "lote3_runner_ledger.jsonl"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ledger = L2Ledger(ledger_path=ledger_path)

            runner = Lote3Runner(adapter=adapter, client=FakeClient(intent), ledger=ledger)
            runner.run("fixture")

            events = _load_ledger_events(ledger_path)
            ledger_is_valid = validate_ledger(ledger_path)

        return events, ledger_is_valid

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

    def test_real_ledger_successful_run_validates_generated_ledger(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="PROVA L3",
            explanation="fixture",
        )

        events, ledger_is_valid = self._run_with_real_ledger(FakeAdapter(), intent)

        self.assertTrue(ledger_is_valid)
        self.assertEqual(events[-1]["event_type"], "RUN_FINISHED")
        self.assertEqual(events[-1]["payload"]["final_outcome"], "SUCCESS")
        self.assertEqual(events[-1]["payload"]["evidence_level"], "STRONG_DETERMINISTIC_PROVED")

    def test_real_ledger_evidence_divergence_closes_with_supported_schema(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="PROVA L3",
            explanation="fixture",
        )

        events, ledger_is_valid = self._run_with_real_ledger(
            FakeAdapter(read_override="PROVA DIVERGENTE"),
            intent,
        )

        evidence_event = next(event for event in events if event["event_type"] == "EVIDENCE_CHECK")
        self.assertEqual(evidence_event["status"], "FAIL")
        self.assertEqual(evidence_event["payload"]["evidence_level"], "PROOF_FAILED")
        self.assertEqual(events[-1]["event_type"], "RUN_FINISHED")
        self.assertEqual(events[-1]["payload"]["final_outcome"], "EVIDENCE_FAILURE")
        self.assertEqual(events[-1]["payload"]["evidence_level"], "PROOF_FAILED")
        self.assertTrue(ledger_is_valid)

    def test_real_ledger_missing_evidence_closes_with_supported_schema(self) -> None:
        intent = WriteFileIntent(
            operation="WRITE_FILE_TEXT",
            target_path="/tmp/aios_workspace/outputs/proof.txt",
            content="PROVA L3",
            explanation="fixture",
        )

        events, ledger_is_valid = self._run_with_real_ledger(
            FakeAdapter(read_success=False, read_error="read failed"),
            intent,
        )

        evidence_event = next(event for event in events if event["event_type"] == "EVIDENCE_CHECK")
        self.assertEqual(evidence_event["status"], "FAIL")
        self.assertEqual(evidence_event["payload"]["evidence_level"], "PROOF_MISSING")
        self.assertEqual(events[-1]["event_type"], "RUN_FINISHED")
        self.assertEqual(events[-1]["payload"]["final_outcome"], "EVIDENCE_FAILURE")
        self.assertEqual(events[-1]["payload"]["evidence_level"], "PROOF_MISSING")
        self.assertTrue(ledger_is_valid)


if __name__ == "__main__":
    unittest.main()
