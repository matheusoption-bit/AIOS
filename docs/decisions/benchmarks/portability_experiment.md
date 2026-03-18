import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

# --- Tipos Estruturados (conforme B2) ---
class SandboxCreateResult:
    def __init__(self, id, success, materialized_ref):
        self.id = id
        self.success = success
        self.materialized_ref = materialized_ref

class ExecutionResult:
    def __init__(self, status, output):
        self.status = status
        self.output = output

# --- Interface Canônica (conforme B4-T10) ---
class ISandbox(ABC):
    @abstractmethod
    def create(self, baseline_ref: str) -> SandboxCreateResult: pass
    @abstractmethod
    def run_command(self, command: str, timeout_seconds: float) -> ExecutionResult: pass
    @abstractmethod
    def destroy(self) -> bool: pass

# --- Candidato 1: Subprocess (Real) ---
class LocalSubprocessSandbox(ISandbox):
    def create(self, baseline_ref: str):
        print(f"[Subprocess] Criando sandbox na ref: {baseline_ref}")
        return SandboxCreateResult(str(uuid.uuid4()), True, baseline_ref)
    
    def run_command(self, command, timeout_seconds):
        import subprocess
        print(f"[Subprocess] Executando: {command}")
        # Simulação de execução real
        return ExecutionResult("SUCCESS", f"Output of {command}")
        
    def destroy(self):
        print("[Subprocess] Destruindo recursos locais.")
        return True

# --- Candidato 2: Mock (Simulação) ---
class InProcMockSandbox(ISandbox):
    def create(self, baseline_ref: str):
        print(f"[Mock] Inicializando mock in-memory na ref: {baseline_ref}")
        return SandboxCreateResult("mock-id", True, baseline_ref)
    
    def run_command(self, command, timeout_seconds):
        print(f"[Mock] Simulando: {command}")
        return ExecutionResult("SUCCESS", "Mocked output")
        
    def destroy(self):
        print("[Mock] Limpando memória.")
        return True

# --- Prova de Portabilidade ---
def run_benchmark(sandbox: ISandbox):
    result = sandbox.create("HEAD")
    if result.success:
        sandbox.run_command("ls -la", 5.0)
        sandbox.destroy()

print("--- Teste de Adaptador 1 ---")
run_benchmark(LocalSubprocessSandbox())
print("\n--- Teste de Adaptador 2 ---")
run_benchmark(InProcMockSandbox())
