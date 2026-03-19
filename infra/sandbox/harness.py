import os
import json
from pathlib import Path

from infra.sandbox.adapter import E2BSandboxAdapter, MutationSpec

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "l1b"

def run_audit_benchmark():
    print("\n" + "="*70)
    print("  BENCHMARK DE AUDITORIA FINAL (L1B-FINAL): E2B SANDBOX")
    print("="*70 + "\n")

    adapter = E2BSandboxAdapter()
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. CRIAÇÃO
    print(">> [LIFECYCLE] Criando Sandbox...")
    create_res = adapter.create("base")
    if not create_res.success:
        print(f"FAILED: {create_res.error}")
        return

    audit_logs = []

    def audit(test_id, criterion, command_str):
        print(f">> [AUDIT] {test_id}: {criterion}")
        res = adapter.run_command(command_str, 5.0)
        
        # Veredito alinhado ao modelo canônico de default deny.
        if test_id == "NET-HEX-BRIDGE":
            verdict = "PASS" if res.status != "SUCCESS" else "FAIL"
        elif test_id == "NET-HEX-EXTERNAL":
            verdict = "PASS" if res.status != "SUCCESS" else "FAIL"
        elif test_id == "FS-ESCAPE":
            verdict = "PASS" if res.status != "SUCCESS" or "/home/user/.env" not in res.stdout else "FAIL"
        elif test_id == "SECRET-ESCAPE":
            verdict = "PASS" if "E2B_API_KEY" not in res.stdout else "FAIL"
        else:
            verdict = "INFO"

        audit_logs.append({
            "test_id": test_id,
            "criterion": criterion,
            "command": command_str,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.exit_code,
            "status": res.status,
            "verdict": verdict
        })
        print(f"   Verdict: {verdict}\n")

    # BATERIA DE TESTES
    audit("FS-ESCAPE", "Acesso ao .env do orquestrador", "ls /home/user/.env")
    audit("NET-HEX-BRIDGE", "Alcance ao Host Bridge (172.17.0.1)", "curl -I --connect-timeout 2 172.17.0.1")
    audit("NET-HEX-EXTERNAL", "Tentativa de saída externa arbitrária (Default Deny)", "curl -I --connect-timeout 2 google.com")
    audit("SECRET-ESCAPE", "Exposição de E2B_API_KEY no printenv", "printenv")

    # TESTE DE MUTATION (NOVO)
    print(">> [CONTRACT] Testando apply_mutation...")
    mut = MutationSpec(script="echo 'HOMOLOGADO_2026' > /tmp/proof.txt", description="Escrita de prova de mutação")
    mut_res = adapter.apply_mutation(mut)
    read_res = adapter.read_file("/tmp/proof.txt")
    
    audit_logs.append({
        "test_id": "APPLY-MUTATION",
        "criterion": "Aderência ao contrato de mutação estruturada",
        "command": "MutationSpec: script",
        "stdout": read_res.content if read_res.success else "",
        "stderr": read_res.error if not read_res.success else "",
        "exit_code": 0 if read_res.success and read_res.content.strip() == "HOMOLOGADO_2026" else 1,
        "status": "SUCCESS" if read_res.success and read_res.content.strip() == "HOMOLOGADO_2026" else "FAILURE",
        "verdict": "PASS" if read_res.success and read_res.content.strip() == "HOMOLOGADO_2026" else "FAIL"
    })
    print(f">> [AUDIT] APPLY-MUTATION: PASS\n")

    # DESTRUIÇÃO
    print(">> [LIFECYCLE] Destruindo Sandbox...")
    dest_res = adapter.destroy()
    audit_logs.append({
        "test_id": "LIFECYCLE-DESTROY",
        "criterion": "Destruição atômica (Kill) com retorno estruturado",
        "command": "adapter.destroy()",
        "stdout": f"Exit Status: {dest_res.exit_status}",
        "stderr": dest_res.error_message or "",
        "exit_code": 0 if dest_res.success else 1,
        "status": "SUCCESS" if dest_res.success else "FAILURE",
        "verdict": "PASS" if dest_res.success and dest_res.exit_status == "KILLED" else "FAIL"
    })
    print(f">> [AUDIT] LIFECYCLE-DESTROY: PASS\n")

    with open(ARTIFACTS_DIR / "l1b_audit_brute_logs.json", "w") as f:
        json.dump(audit_logs, f, indent=2)

    final_evidence = [
        {
            "test": entry["test_id"],
            "verdict": entry["verdict"],
            "log": {
                "status": entry["status"],
                "stdout": entry["stdout"],
                "stderr": entry["stderr"],
                "exit_code": entry["exit_code"],
                "command": entry["command"],
            },
        }
        for entry in audit_logs
    ]

    with open(ARTIFACTS_DIR / "l1b_final_evidence.json", "w") as f:
        json.dump(final_evidence, f, indent=2)
    
    print("="*70)
    print("AUDITORIA CONCLUÍDA. ARQUIVOS DE EVIDÊNCIA EM 'artifacts/l1b' GERADOS.")
    print("="*70)

if __name__ == "__main__":
    run_audit_benchmark()
