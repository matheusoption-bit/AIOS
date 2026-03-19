import sys
import os
import tempfile
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para imports relativos funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.sandbox.adapter import E2BSandboxAdapter
from src.lote3.provider_client import OpenAIClient
from src.lote3.path_policy import validate_safe_path, PathViolationError
from src.lote2.ledger import L2Ledger, LedgerWriteError
from pydantic import ValidationError
from openai import APITimeoutError

class Lote3Runner:
    """
    Runner de integração do Lote 3: Structured Mutation Boundary.
    O Orquestrador não é mais um passador cego de bash. Ele compila intents estruturados.
    """
    def __init__(self):
        self.adapter = E2BSandboxAdapter()
        self.client = OpenAIClient()
        self.ledger = L2Ledger() # Reaproveitando Ledger endurecido do Lote 2

    def run(self, user_instruction: str, expected_fail: bool = False):
        print(f"\n[AIOS L3] {'MODO SMOKE TEST (Ilícito esperado)' if expected_fail else 'Execução Regular/Lícita'}")
        print(f"[AIOS L3] Instrução: '{user_instruction}'")
        print(f"[AIOS L3] Run ID: {self.ledger.run_id}")

        evidence_level = "NONE"
        final_outcome = "SUCCESS"

        # ── 1. Chamada ao Provider (FORA da Sandbox) ──
        try:
            self.ledger.emit("LLM_CALL", "PROVIDER", "OK", {
                "instruction": user_instruction,
                "expected_fail": expected_fail,
                "lote": "LOTE_3_STRUCTURED_MUTATION"
            })
            
            raw_response, parsed_intent = self.client.get_completion(user_instruction)

            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "OK", {
                "operation": parsed_intent.operation,
                "target_path": parsed_intent.target_path,
                "content_size": len(parsed_intent.content),
                "explanation": parsed_intent.explanation,
            })

        except ValidationError as e:
            print(f"[ERRO] Resposta do Provider violou o schema estrito de mutação: {e}")
            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "FAIL", {"error": "JSON_SCHEMA_VIOLATION"})
            self._force_finish("PROVIDER_FAILURE", "Schema de mutação violado.")
            return
        except Exception as e:
            print(f"[ERRO] Falha no Provider: {e}")
            self.ledger.emit("LLM_RESPONSE", "PROVIDER", "FAIL", {"error": str(e)})
            self._force_finish("PROVIDER_FAILURE", str(e))
            return

        # ── 2. Path Policy Enforcement (Runtime Boundary Guard) ──
        print(f"[AIOS L3] Validando intenção de mutação: {parsed_intent.target_path}")
        try:
            safe_path = validate_safe_path(parsed_intent.target_path)
            print(f"[AIOS L3] Caminho validado com sucesso: {safe_path}")
            
            # Novo evento usando a taxonomia base do L2 (aproveitando flexibilidade do payload)
            self.ledger.emit("POLICY_CHECK", "RUNTIME", "OK", {
                "requested_path": parsed_intent.target_path,
                "resolved_path": safe_path
            })
        except PathViolationError as e:
            msg = f"Mutação interceptada pelo Policy Guard: {e}"
            print(f"[BLOQUEIO DE SEGURANÇA] {msg}")
            self.ledger.emit("POLICY_CHECK", "RUNTIME", "FAIL", {"error": str(e)})
            self._force_finish("SECURITY_VIOLATION", msg)
            return

        # ── 3. Criação da Sandbox ──
        print("[AIOS L3] Criando Sandbox E2B...")
        create_res = self.adapter.create("base")

        if not create_res.success:
            print(f"[ERRO] Falha ao criar sandbox: {create_res.error}")
            self.ledger.emit("SANDBOX_CREATE", "SANDBOX", "FAIL", {"error": create_res.error})
            self._force_finish("SANDBOX_FAILURE", create_res.error)
            return

        self.ledger.emit("SANDBOX_CREATE", "SANDBOX", "OK", {"sandbox_id": create_res.sandbox_id})

        # ── 4. Setup do Workspace Base e Mutação Estruturada ──
        try:
            # Garante que o diretório exista (usando run_command unicamente como infra setup cego, não a partir do LLM)
            self.adapter.run_command("mkdir -p /tmp/aios_workspace", timeout_seconds=10.0)

            # Para respeitar a interface ISandbox do Lote 1/2 sem alterá-la, usamos copy_in
            print(f"[AIOS L3] Aplicando mutação '{parsed_intent.operation}' em '{safe_path}'...")
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(parsed_intent.content)
                tmp_file_path = tmp_file.name

            # Copia para dentro da sandbox (I/O seguro)
            copy_res = self.adapter.copy_in(tmp_file_path, safe_path)
            os.remove(tmp_file_path)

            if not copy_res.success:
                 raise RuntimeError(f"Falha no copy_in: {copy_res.error_message}")

            self.ledger.emit("SANDBOX_MUTATION", "SANDBOX", "OK", {
                "operation": parsed_intent.operation,
                "target_path": safe_path,
                "bytes_written": copy_res.bytes_written
            })

            # ── 5. Coleta de Evidência Determinística ──
            print(f"[AIOS L3] Verificando evidência lendo {safe_path}...")
            read_res = self.adapter.read_file(safe_path)

            if read_res.success and read_res.content == parsed_intent.content:
                evidence_level = "STRONG_DETERMINISTIC_PROVED"
                print("[AIOS L3] EVIDÊNCIA FORTE CONFIRMADA: Conteúdo gravado coincide perfeitamente.")
                self.ledger.emit("EVIDENCE_CHECK", "EVIDENCE", "OK", {
                    "artifact_path": safe_path,
                    "evidence_level": evidence_level,
                    "content_match": True,
                })
            else:
                evidence_level = "EVIDENCE_FAILURE"
                final_outcome = "SANDBOX_FAILURE"
                print("[AVISO] Comando executou mas evidência de conteúdo falhou.")
                self.ledger.emit("EVIDENCE_CHECK", "EVIDENCE", "FAIL", {
                    "artifact_path": safe_path,
                    "evidence_level": evidence_level,
                    "content_match": False,
                })

        except Exception as e:
            msg = f"Erro na operação de mutação da sandbox: {e}"
            print(f"[ERRO] {msg}")
            self.ledger.emit("SANDBOX_MUTATION", "SANDBOX", "ERROR", {"error": str(e)})
            final_outcome = "SANDBOX_FAILURE"

        # ── 6. Evento Terminal ──
        destroy_payload = None
        try:
            destroy_res = self.adapter.destroy()
            destroy_payload = {
                "success": destroy_res.success,
                "exit_status": destroy_res.exit_status,
                "error": destroy_res.error_message
            }
        except Exception as e:
            destroy_payload = {"success": False, "exit_status": "CLEANUP_FAILED", "error": str(e)}

        self._force_finish(final_outcome, f"Ciclo finalizado. Outcome: {final_outcome}", evidence_level, destroy_payload)
        print(f"[AIOS L3] Ciclo finalizado. Outcome: {final_outcome}")
        print(f"[AIOS L3] Ledger atualizado em {self.ledger.ledger_path}")

    def _force_finish(self, outcome: str, summary: str, evidence: str = "NONE", destroy_payload: dict = None):
        try:
            self.ledger.emit_run_finished(
                final_outcome=outcome,
                evidence_level=evidence,
                summary=summary,
                destroy_result=destroy_payload
            )
        except LedgerWriteError:
            pass

if __name__ == "__main__":
    runner = Lote3Runner()

    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_e2b = bool(os.getenv("E2B_API_KEY"))

    if not (has_openai and has_e2b):
         print("AVISO: CREDENCIAIS AUSENTES no .env")
         sys.exit(1)

    print("\n--- TESTE LÍCITO (Escrita Permitida) ---")
    runner.run("Crie um arquivo chamado 'lote3_sucesso.txt' com o texto 'PROVA L3'")

    print("\n\n--- TESTE ILÍCITO (Path Traversal / Escape) ---")
    runner.run("Crie um arquivo chamado '../../../../etc/passwd_fake' com o texto 'hacked'", expected_fail=True)
