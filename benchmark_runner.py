
import hashlib
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Modelos de Contrato (Bloco 2) ---

class Intent:
    def __init__(self, kind: str, payload: Any, metadata: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.kind = kind
        self.payload = payload
        self.metadata = metadata

class ExecutionResult:
    def __init__(self, intent_id: str, status: str, termination_reason: str, git_ref: str, output: str = ""):
        self.intent_id = intent_id
        self.status = status
        self.termination_reason = termination_reason
        self.git_ref = git_ref
        self.output = output

class LedgerEntry:
    def __init__(self, index: int, event_type: str, intent_id: str, payload: Any, prev_hash: str, git_ref: str):
        self.index = index
        self.event_type = event_type
        self.intent_id = intent_id
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.payload = payload
        self.prev_hash = prev_hash
        self.git_ref = git_ref
        self.entry_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        content = f"{self.index}{self.intent_id}{json.dumps(self.payload, sort_keys=True)}{self.prev_hash}{self.git_ref}"
        return hashlib.sha256(content.encode()).hexdigest()

# --- Orquestrador FSM (Bloco 3) ---

class MockFSM:
    def __init__(self):
        self.state = "IDLE"
        self.ledger = []
        self.current_git_ref = "base-commit-000"
        self.last_hash = "0" * 64
        self.material_effect = False
        self.current_intent = None

    def log_event(self, event_type: str, payload: Any):
        intent_id = self.current_intent.id if self.current_intent else "SYSTEM"
        entry = LedgerEntry(
            len(self.ledger),
            event_type,
            intent_id,
            payload,
            self.last_hash,
            self.current_git_ref
        )
        self.ledger.append(entry)
        self.last_hash = entry.entry_hash
        print(f"[LEDGER] {event_type} registered. Hash: {self.last_hash[:8]}")

    def run_scenario(self, scenario_id: str, intent_data: Dict[str, Any], behavior: Dict[str, Any]):
        print(f"\n--- Iniciando Cenário {scenario_id} ---")
        self.state = "IDLE"
        self.material_effect = False
        
        # 1. RECEIVE_INTENT -> INTENT_VALIDATION
        self.state = "INTENT_VALIDATION"
        self.current_intent = Intent(intent_data['kind'], intent_data['payload'], {})
        
        if behavior.get('malformed_proposal'):
            self.log_event("INTENT_PROPOSED", intent_data)
            self.state = "FAILURE"
            self.log_event("EXECUTION_FINISHED", {"status": "FAILURE", "reason": "MALFORMED_PROPOSAL"})
            return "PASS"

        if behavior.get('budget_exceeded'):
             self.log_event("INTENT_PROPOSED", intent_data)
             self.state = "FAILURE"
             self.log_event("EXECUTION_FINISHED", {"status": "FAILURE", "reason": "MAX_CYCLES_REACHED"})
             return "PASS"

        self.log_event("INTENT_PROPOSED", intent_data)
        
        # 2. VALID -> SNAPSHOT_PENDING
        self.state = "SNAPSHOT_PENDING"
        self.log_event("SYSTEM_STATE", {"step": "SNAPSHOT_READY", "baseline": self.current_git_ref})
        
        # 3. READY -> EXECUTION_PENDING
        self.state = "EXECUTION_PENDING"
        if behavior.get('material_effect'):
            self.material_effect = True
            print("[EXEC] Mutação física aplicada.")

        if behavior.get('security_violation'):
            print("[SECURITY] Violação detectada!")
            self.log_event("SECURITY_VIOLATION_DETECTED", {"trigger": "Unauthorized OS write"})
            if self.material_effect:
                self.state = "ROLLBACK_PENDING"
                self.handle_rollback()
            self.state = "ERROR"
            self.log_event("EXECUTION_FINISHED", {"status": "ERROR", "reason": "SECURITY_VIOLATION"})
            return "PASS"

        if behavior.get('timeout'):
            print("[TIMEOUT] Tempo esgotado.")
            if self.material_effect:
                self.state = "ROLLBACK_PENDING"
                self.handle_rollback()
            self.state = "FAILURE"
            self.log_event("EXECUTION_FINISHED", {"status": "FAILURE", "reason": "TIMEOUT"})
            return "PASS"

        # 4. FINISH -> VERIFICATION_PENDING
        self.state = "VERIFICATION_PENDING"
        if behavior.get('check_fail'):
            print("[CHECK] Verificação falhou.")
            self.state = "ROLLBACK_PENDING"
            self.handle_rollback()
            self.state = "FAILURE"
            self.log_event("EXECUTION_FINISHED", {"status": "FAILURE", "reason": "VERIFICATION_FAILED"})
            return "PASS"

        # 5. CHECK_OK -> SUCCESS
        self.state = "SUCCESS"
        self.current_git_ref = f"commit-{uuid.uuid4().hex[:8]}"
        self.log_event("EXECUTION_FINISHED", {"status": "SUCCESS", "reason": "COMPLETED", "git_ref": self.current_git_ref})
        self.log_event("SYSTEM_STATE", {"git_ref": self.current_git_ref})
        return "PASS"

    def handle_rollback(self):
        print(f"[ROLLBACK] Restaurando para baseline: {self.current_git_ref}")
        self.material_effect = False
        self.log_event("ROLLBACK_TRIGGERED", {"baseline": self.current_git_ref})
        print("[ROLLBACK] Restauração física concluída (Git Reset --hard).")

# --- Execução dos 5 Cenários ---

fsm = MockFSM()

# S1: Caminho Feliz
fsm.run_scenario("S1", {"kind": "PATCH", "payload": "diff ..."}, {})

# S2: Proposta Inválida
fsm.run_scenario("S2", {"kind": "UNKNOWN", "payload": {}}, {"malformed_proposal": True})

# S3: Falha + Rollback
fsm.run_scenario("S3", {"kind": "SHELL", "payload": "rm -rf /"}, {"material_effect": True, "check_fail": True})

# S4: Timeout Material
fsm.run_scenario("S4", {"kind": "PATCH", "payload": "large diff"}, {"material_effect": True, "timeout": True})

# S5: Violação Seg. (com efeito material parcial)
fsm.run_scenario("S5", {"kind": "SHELL", "payload": "eval code"}, {"material_effect": True, "security_violation": True})

# --- Verificação de Integridade ---
print("\n--- Verificação de Integridade do Ledger ---")
intact = True
for i in range(1, len(fsm.ledger)):
    if fsm.ledger[i].prev_hash != fsm.ledger[i-1].entry_hash:
        print(f"ERRO: Quebra na cadeia no índice {i}!")
        intact = False
if intact:
    print("Sucesso: Hash Chain de 256 bits 100% íntegra.")

# --- Persistência Final do Mock Ledger ---
with open("benchmark_ledger.jsonl", "w") as f:
    for entry in fsm.ledger:
        f.write(json.dumps(entry.__dict__) + "\n")
print(f"Ledger final persistido com {len(fsm.ledger)} entradas.")
