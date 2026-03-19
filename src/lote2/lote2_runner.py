import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para imports relativos funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.lote2.response_schema import LLMResponse
from src.lote2.ledger import L2Ledger, LedgerWriteError
from pydantic import ValidationError

# Configuração Determinística de Integridade (Smoke Test)
SMOKE_TEST_INSTRUCTION = "Crie o arquivo /tmp/l2_proof.txt com o conteúdo 'SUCESSO_L2_DETERMINISTICO'"
SMOKE_TEST_ARTIFACT = "/tmp/l2_proof.txt"
SMOKE_TEST_EXPECTED_CONTENT = "SUCESSO_L2_DETERMINISTICO"
LEGACY_MODE_ENV_VAR = "AIOS_ENABLE_LEGACY_LOTE2"

class Lote2Runner:
    """
    Runner de integração do Lote 2: O circuito fechado funcional do AIOS.
    Agora com ledger endurecido (hash chain, run_id, eventos granulares).
    """
    def __init__(self, adapter=None, client=None, ledger=None):
        if adapter is None:
            from infra.sandbox.adapter import E2BUnsafeAdminSandboxAdapter

            adapter = E2BUnsafeAdminSandboxAdapter()
        if client is None:
            from src.lote2.provider_client import OpenAIClient

            client = OpenAIClient()

        self.adapter = adapter
        self.client = client
        self.ledger = ledger or L2Ledger()

    def _ensure_legacy_mode_allowed(self, user_instruction: str, is_smoke_test: bool) -> None:
        if os.getenv(LEGACY_MODE_ENV_VAR) != "1":
            self.ledger.emit("POLICY_CHECK", "RUNTIME", "FAIL", {
                "policy_action": "blocked_enforcing",
                "reason": "LEGACY_LOTE2_DISABLED",
                "instruction": user_instruction,
                "is_smoke_test": is_smoke_test,
            })
            self.ledger.emit_run_finished(
                final_outcome="SECURITY_VIOLATION",
                evidence_level="NONE",
                summary=(
                    "Lote 2 bloqueado por padrão. Defina AIOS_ENABLE_LEGACY_LOTE2=1 "
                    "apenas para execuções legadas controladas."
                ),
                intent_phase="CLOSE",
            )
            raise RuntimeError(
                "Lote 2 está desativado por padrão. Defina AIOS_ENABLE_LEGACY_LOTE2=1 "
                "para habilitar o modo legado explicitamente."
            )

        warning = (
            "[AIOS L2] AVISO CRITICO: modo legado habilitado. "
            "Este caminho mantém shell arbitrário e existe apenas para compatibilidade controlada."
        )
        print(warning)
        self.ledger.emit("POLICY_CHECK", "RUNTIME", "OK", {
            "policy_action": "legacy_mode_warning",
            "reason": "LEGACY_LOTE2_ENABLED",
            "instruction": user_instruction,
            "is_smoke_test": is_smoke_test,
        })
        self.ledger.ensure_not_degraded("legacy_mode_warning")

    def run(self, user_instruction: str, is_smoke_test: bool = False):
        self._ensure_legacy_mode_allowed(user_instruction, is_smoke_test)
        print(f"\n[AIOS L2] {'MODO SMOKE TEST' if is_smoke_test else 'Execução Regular'}")
        print(f"[AIOS L2] Instrução: '{user_instruction}'")
        print(f"[AIOS L2] Run ID: {self.ledger.run_id}")

        evidence_level = "NONE"
        final_outcome = "SUCCESS"

        # ── 1. Chamada ao Provider (FORA da Sandbox) ──
        try:
            # Evento: início da chamada ao provider
            try:
                self.ledger.emit("LLM_CALL", "PROVIDER", "OK", {
                    "instruction": user_instruction,
                    "is_smoke_test": is_smoke_test,
                    "intent_phase": "OPEN",
                    "intent_kind": "SHELL_COMMAND",
                })
            except LedgerWriteError as e:
                print(f"[ERRO FATAL] {e}")
                return
            self.ledger.ensure_not_degraded("provider_boundary")

            raw_response, parsed_response = self.client.get_completion(user_instruction)

            # Evento: resposta do provider recebida e parseada
            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "OK", {
                "raw_response": raw_response,
                "command": parsed_response.command,
                "explanation": parsed_response.explanation,
            })
            self.ledger.ensure_not_degraded("provider_response")

        except LedgerWriteError as e:
            # LedgerWriteError do LLM_RESPONSE (primeiro evento já escrito, então é intermediário)
            # Continua com degradação — o emit já setou ledger_degraded
            print(f"[AVISO] Ledger degradado no estágio PROVIDER: {e}")
        except ValidationError as e:
            print(f"[ERRO] Resposta do Provider violou o schema: {e}")
            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "FAIL", {
                "error": "JSON_SCHEMA_VIOLATION",
                "details": str(e),
            })
            try:
                self.ledger.emit_run_finished(
                    final_outcome="PROVIDER_FAILURE",
                    summary="Falha na validação do schema da resposta do provider",
                )
            except LedgerWriteError as le:
                print(f"[ERRO FATAL] Não foi possível registrar RUN_FINISHED: {le}")
            return
        except Exception as e:
            timeout_error = None
            try:
                from openai import APITimeoutError

                timeout_error = APITimeoutError
            except ImportError:
                timeout_error = None

            if timeout_error and isinstance(e, timeout_error):
                print(f"[ERRO] Timeout na chamada ao Provider: {e}")
                self.ledger.emit("LLM_RESPONSE", "PROVIDER", "ERROR", {
                    "error": "PROVIDER_TIMEOUT",
                    "details": str(e),
                })
                try:
                    self.ledger.emit_run_finished(
                        final_outcome="PROVIDER_FAILURE",
                        summary="Timeout na chamada ao provider",
                    )
                except LedgerWriteError as le:
                    print(f"[ERRO FATAL] Não foi possível registrar RUN_FINISHED: {le}")
                return

            print(f"[ERRO] Falha generica no Provider: {e}")
            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "FAIL", {
                "error": str(e),
            })
            try:
                self.ledger.emit_run_finished(
                    final_outcome="PROVIDER_FAILURE",
                    summary=f"Falha na chamada ao provider: {e}",
                )
            except LedgerWriteError as le:
                print(f"[ERRO FATAL] Não foi possível registrar RUN_FINISHED: {le}")
            return

        # ── 2. Criação da Sandbox ──
        print("[AIOS L2] Criando Sandbox E2B...")
        create_res = self.adapter.create("base")

        if not create_res.success:
            print(f"[ERRO] Falha ao criar sandbox: {create_res.error}")
            self.ledger.emit("SANDBOX_CREATE", "SANDBOX", "FAIL", {
                "error": create_res.error,
            })
            try:
                self.ledger.emit_run_finished(
                    final_outcome="SANDBOX_FAILURE",
                    summary=f"Falha ao criar sandbox: {create_res.error}",
                )
            except LedgerWriteError as le:
                print(f"[ERRO FATAL] Não foi possível registrar RUN_FINISHED: {le}")
            return

        self.ledger.emit("SANDBOX_CREATE", "SANDBOX", "OK", {
            "sandbox_id": create_res.sandbox_id,
        })
        self.ledger.ensure_not_degraded("sandbox_create")

        # ── 3. Execução na Sandbox ──
        try:
            print(f"[AIOS L2] Executando comando: {parsed_response.command}")
            exec_res = self.adapter.run_command(parsed_response.command, timeout_seconds=30.0)

            self.ledger.emit("SANDBOX_EXEC", "SANDBOX", "OK" if exec_res.exit_code == 0 else "FAIL", {
                "command": parsed_response.command,
                "exit_code": exec_res.exit_code,
                "status": exec_res.status,
                "stdout": exec_res.stdout,
                "stderr": exec_res.stderr,
            })

            if exec_res.exit_code != 0:
                final_outcome = "SANDBOX_FAILURE"

            # ── 4. Coleta de Evidência Determinística ──
            if is_smoke_test:
                print(f"[AIOS L2] Verificando evidência determinística em {SMOKE_TEST_ARTIFACT}...")
                read_res = self.adapter.read_file(SMOKE_TEST_ARTIFACT)

                if read_res.success and SMOKE_TEST_EXPECTED_CONTENT in (read_res.content or ""):
                    evidence_level = "STRONG_DETERMINISTIC_PROVED"
                    print("[AIOS L2] EVIDÊNCIA FORTE CONFIRMADA.")
                    self.ledger.emit("EVIDENCE_CHECK", "EVIDENCE", "OK", {
                        "artifact_path": SMOKE_TEST_ARTIFACT,
                        "evidence_level": evidence_level,
                        "content_match": True,
                    })
                else:
                    evidence_level = "PROOF_MISSING"
                    final_outcome = "EVIDENCE_FAILURE"
                    print("[AVISO] Comando executou mas evidência não foi encontrada.")
                    self.ledger.emit("EVIDENCE_CHECK", "EVIDENCE", "FAIL", {
                        "artifact_path": SMOKE_TEST_ARTIFACT,
                        "evidence_level": evidence_level,
                        "content_match": False,
                        "read_success": read_res.success,
                        "read_error": read_res.error,
                    })
            else:
                evidence_level = "INDIRECT"

        except Exception as e:
            msg = f"Erro na execução da sandbox: {e}"
            print(f"[ERRO] {msg}")
            self.ledger.emit("SANDBOX_EXEC", "SANDBOX", "ERROR", {
                "error": str(e),
            })
            final_outcome = "SANDBOX_FAILURE"

        # ── 5. Evento Terminal ──
        destroy_payload = None
        try:
            destroy_res = self.adapter.destroy()
            if not destroy_res.success:
                print(f"[AVISO] Falha ao destruir Sandbox: {destroy_res.error_message}")
            destroy_payload = {
                "success": destroy_res.success,
                "exit_status": destroy_res.exit_status,
                "error": destroy_res.error_message
            }
        except Exception as e:
            print(f"[ERRO] Exceção inesperada no Cleanup da Sandbox: {e}")
            destroy_payload = {
                "success": False,
                "exit_status": "CLEANUP_FAILED",
                "error": str(e)
            }

        try:
            # Injeta campo de destroy_result em SUMMARY/Payload
            extra_summary_info = ""
            if destroy_payload and not destroy_payload['success']:
                extra_summary_info = f" [Aviso: Destroy da Sandbox Falhou: {destroy_payload['error']}]"

            self.ledger.emit_run_finished(
                final_outcome=final_outcome,
                evidence_level=evidence_level,
                summary=f"Corrida finalizada. Outcome: {final_outcome}.{extra_summary_info}",
                intent_phase="CLOSE",
                destroy_result=destroy_payload
            )
        except LedgerWriteError as e:
            print(f"[ERRO FATAL] Não foi possível registrar RUN_FINISHED: {e}")

        print(f"[AIOS L2] Ciclo finalizado. Outcome: {final_outcome}")
        print(f"[AIOS L2] Ledger atualizado em {self.ledger.ledger_path}")
        if self.ledger.ledger_degraded:
            print("[AVISO] Ledger degradado — alguns eventos intermediários podem ter sido perdidos.")

if __name__ == "__main__":
    runner = Lote2Runner()

    # Verificação de credenciais
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_e2b = bool(os.getenv("E2B_API_KEY"))

    if has_openai and has_e2b:
        # Se houver chaves, roda o Smoke Test por padrão para garantir integridade
        try:
            runner.run(SMOKE_TEST_INSTRUCTION, is_smoke_test=True)
        except RuntimeError as e:
            print(f"[ERRO FATAL] {e}")
            sys.exit(1)
    else:
        print("\n" + "!"*60)
        print("  AVISO: CREDENCIAIS AUSENTES (OPENAI_API_KEY ou E2B_API_KEY)")
        print("  O Runner está pronto para execução real, mas exige chaves no .env")
        print("!"*60 + "\n")
