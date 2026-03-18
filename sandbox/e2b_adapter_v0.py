
import os
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from e2b import Sandbox
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --- Classes de Resultado Estruturado (Alinhamento Canônico) ---

class SandboxCreateResult(BaseModel):
    sandbox_id: Optional[str] = None
    success: bool
    status_code: int
    materialized_ref: str # Mapeado para o Template ID no E2B
    error: Optional[str] = None

class SandboxDestroyResult(BaseModel):
    success: bool
    exit_status: str # 'KILLED', 'EXPIRED', 'CLEANUP_FAILED'
    error_message: Optional[str] = None

class SandboxOpResult(BaseModel):
    success: bool
    error_message: Optional[str] = None
    bytes_written: Optional[int] = None

class ExecutionResult(BaseModel):
    status: str # 'SUCCESS', 'FAILURE', 'ERROR'
    stdout: str
    stderr: str
    exit_code: int
    command: Optional[str] = None

class ListFilesResult(BaseModel):
    success: bool
    files: List[str]
    error: Optional[str] = None

class ReadFileResult(BaseModel):
    success: bool
    content: Optional[str] = None
    hash_sha256: Optional[str] = None
    error: Optional[str] = None

class MutationSpec(BaseModel):
    type: str = "SHELL_SCRIPT"
    script: str
    description: Optional[str] = None

# --- Interface ISandbox (CONTRATO CANÔNICO FASE 1) ---

class ISandbox(ABC):
    @abstractmethod
    def create(self, baseline_ref: str) -> SandboxCreateResult: pass
    
    @abstractmethod
    def destroy(self) -> SandboxDestroyResult: pass
    
    @abstractmethod
    def copy_in(self, source_path: str, dest_path: str) -> SandboxOpResult: pass
    
    @abstractmethod
    def apply_mutation(self, mutation: MutationSpec) -> ExecutionResult: pass
    
    @abstractmethod
    def run_command(self, command: str, timeout_seconds: float) -> ExecutionResult: pass
    
    @abstractmethod
    def list_files(self, path: str) -> ListFilesResult: pass
    
    @abstractmethod
    def read_file(self, path: str) -> ReadFileResult: pass

# --- Implementação Adaptador E2B Homologado ---

class E2BSandboxAdapter(ISandbox):
    def __init__(self, api_key: str = None):
        self._api_key = api_key or os.getenv("E2B_API_KEY")
        self._sandbox: Optional[Sandbox] = None

    def create(self, baseline_ref: str) -> SandboxCreateResult:
        """
        Mapeia baseline_ref (semântica do runtime) para template_id (E2B).
        Na Fase 1, 'base' mapeia para o template padrão 'base'.
        """
        try:
            template_id = baseline_ref if baseline_ref != "base" else "base"
            # O enforcement de egress fica explícito no código para manter a
            # boundary auditável e aderente ao modelo canônico de default deny.
            self._sandbox = Sandbox.create(
                template=template_id,
                allow_internet_access=False,
            )
            return SandboxCreateResult(
                sandbox_id=self._sandbox.sandbox_id,
                success=True,
                status_code=201,
                materialized_ref=template_id
            )
        except Exception as e:
            return SandboxCreateResult(
                success=False,
                status_code=500,
                materialized_ref=baseline_ref,
                error=str(e)
            )

    def destroy(self) -> SandboxDestroyResult:
        if not self._sandbox:
            return SandboxDestroyResult(success=True, exit_status="NONE")
        
        try:
            self._sandbox.kill()
            self._sandbox = None
            return SandboxDestroyResult(success=True, exit_status="KILLED")
        except Exception as e:
            return SandboxDestroyResult(success=False, exit_status="CLEANUP_FAILED", error_message=str(e))

    def run_command(self, command: str, timeout_seconds: float) -> ExecutionResult:
        if not self._sandbox:
            return ExecutionResult(status="ERROR", stdout="", stderr="Sandbox not created", exit_code=-1)
        
        try:
            # E2B SDK v2: sandbox.commands.run()
            proc = self._sandbox.commands.run(command, timeout=timeout_seconds)
            return ExecutionResult(
                status="SUCCESS" if proc.exit_code == 0 else "FAILURE",
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.exit_code,
                command=command
            )
        except Exception as e:
            return ExecutionResult(status="ERROR", stdout="", stderr=str(e), exit_code=-2, command=command)

    def apply_mutation(self, mutation: MutationSpec) -> ExecutionResult:
        """
        Implementação inicial de mutação via shell script (patch/sed/etc).
        """
        print(f"[E2B] Aplicando mutação: {mutation.description or 'Sem descrição'}")
        return self.run_command(mutation.script, 30.0)

    def copy_in(self, source_path: str, dest_path: str) -> SandboxOpResult:
        if not self._sandbox:
            return SandboxOpResult(success=False, error_message="Sandbox not created")
        
        try:
            with open(source_path, "rb") as f:
                content = f.read()
                self._sandbox.files.write(dest_path, content)
                return SandboxOpResult(success=True, bytes_written=len(content))
        except Exception as e:
            return SandboxOpResult(success=False, error_message=str(e))

    def list_files(self, path: str) -> ListFilesResult:
        if not self._sandbox:
            return ListFilesResult(success=False, files=[], error="Sandbox not created")
        
        try:
            entries = self._sandbox.files.list(path)
            return ListFilesResult(success=True, files=[e.name for e in entries])
        except Exception as e:
            return ListFilesResult(success=False, files=[], error=str(e))

    def read_file(self, path: str) -> ReadFileResult:
        if not self._sandbox:
            return ReadFileResult(success=False, error="Sandbox not created")
        
        try:
            content = self._sandbox.files.read(path)
            if isinstance(content, bytes):
                text_content = content.decode('utf-8')
                raw_bytes = content
            else:
                text_content = content
                raw_bytes = content.encode('utf-8')
            
            h = hashlib.sha256(raw_bytes).hexdigest()
            return ReadFileResult(success=True, content=text_content, hash_sha256=h)
        except Exception as e:
            return ReadFileResult(success=False, error=str(e))
