import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para imports relativos funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from infra.sandbox.adapter import E2BSandboxAdapter
from src.lote2.provider_client import OpenAIClient
from src.lote2.response_schema import LLMResponse

# Configuração Determinística de Integridade (Smoke Test)
SMOKE_TEST_INSTRUCTION = "Crie o arquivo /tmp/l2_proof.txt com o conteúdo 'SUCESSO_L2_DETERMINISTICO'"
SMOKE_TEST_ARTIFACT = "/tmp/l2_proof.txt"
SMOKE_TEST_EXPECTED_CONTENT = "SUCESSO_L2_DETERMINISTICO"

class Lote2Runner:
    """
    Runner de integração do Lote 2: O circuito fechado funcional do AIOS.
    """
    def __init__(self):
        self.adapter = E2BSandboxAdapter()
        self.client = OpenAIClient()
        self.artifact_path = Path("artifacts/l2/l2_execution_ledger.jsonl")
        self.artifact_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_data: dict):
        """
        Registra evento no ledger mínimo do Lote 2 (JSONL).
        """
        event_data["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with open(self.artifact_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + "\n")

    def run(self, user_instruction: str, is_smoke_test: bool = False):
        print(f"\n[AIOS L2] {'MODO SMOKE TEST' if is_smoke_test else 'Execução Regular'}")
        print(f"[AIOS L2] Instrução: '{user_instruction}'")
        
        # 1. Chamada ao Provider (FORA da Sandbox)
        try:
            raw_response, parsed_response = self.client.get_completion(user_instruction)
            
            self.log_event({
                "type": "LLM_DECISION",
                "instruction": user_instruction,
                "is_smoke_test": is_smoke_test,
                "raw_response": raw_response,
                "command": parsed_response.command
            })
            
        except Exception as e:
            print(f"[ERRO] Falha no Provider: {str(e)}")
            self.log_event({"type": "FAILURE", "reason": "LLM_CALL_FAILED", "error": str(e)})
            return

        # 2. Execução na Sandbox (DEFAULT DENY ativado por padrão)
        print(f"[AIOS L2] Criando Sandbox E2B...")
        create_res = self.adapter.create("base")
        if not create_res.success:
            print(f"[ERRO] Falha ao criar sandbox: {create_res.error}")
            self.log_event({"type": "FAILURE", "reason": "SANDBOX_CREATE_FAILED", "error": create_res.error})
            return

        try:
            print(f"[AIOS L2] Executando comando: {parsed_response.command}")
            exec_res = self.adapter.run_command(parsed_response.command, timeout_seconds=30.0)
            
            # 3. Coleta de Evidência Determinística (Se for smoke test ou sugerido)
            evidence = None
            if is_smoke_test:
                print(f"[AIOS L2] Verificando evidência determinística em {SMOKE_TEST_ARTIFACT}...")
                read_res = self.adapter.read_file(SMOKE_TEST_ARTIFACT)
                if read_res.success and SMOKE_TEST_EXPECTED_CONTENT in (read_res.content or ""):
                    evidence = "STRONG_DETERMINISTIC_PROVED"
                    print("[AIOS L2] EVIDÊNCIA FORTE CONFIRMADA.")
                else:
                    evidence = "EVIDENCE_NOT_FOUND"
                    print("[AVISO] Comando executou mas evidência não foi encontrada.")

            self.log_event({
                "type": "SANDBOX_EXECUTION",
                "command": parsed_response.command,
                "exit_code": exec_res.exit_code,
                "status": exec_res.status,
                "evidence_level": evidence or "INDIRECT",
                "stdout": exec_res.stdout,
                "stderr": exec_res.stderr
            })
            
            print(f"[AIOS L2] Fluxo concluído. Status Sandbox: {exec_res.status}")
            
        except Exception as e:
            msg = f"Erro na execução da sandbox: {str(e)}"
            print(f"[ERRO] {msg}")
            self.log_event({"type": "FAILURE", "reason": "SANDBOX_RUNTIME_ERROR", "error": str(e)})
        finally:
            self.adapter.destroy()

        print("[AIOS L2] Ciclo finalizado. Ledger atualizado em artifacts/l2/")

if __name__ == "__main__":
    runner = Lote2Runner()
    
    # Check for credentials
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_e2b = bool(os.getenv("E2B_API_KEY"))

    if has_openai and has_e2b:
        # Se houver chaves, roda o Smoke Test por padrão para garantir integridade
        runner.run(SMOKE_TEST_INSTRUCTION, is_smoke_test=True)
    else:
        print("\n" + "!"*60)
        print("  AVISO: CREDENCIAIS AUSENTES (OPENAI_API_KEY ou E2B_API_KEY)")
        print("  O Runner está pronto para execução real, mas exige chaves no .env")
        print("!"*60 + "\n")
        
        # Teste de carga a seco (somente schema) pode ser feito via testes unitários.
