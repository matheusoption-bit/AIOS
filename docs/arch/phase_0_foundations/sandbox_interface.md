# Especificação: SandboxInterface (Fase 0) - REVISADA

## 1. Propriedades Congeladas (Leis de Fundação)
- **Vendor-Agnostic:** Independente de Docker, E2B ou MicroVMs.
- **Efemeridade:** Ambiente sem persistência própria (Snapshot -> Mutação -> Descarte).
- **Runtime Soberano:** O runtime controla o ciclo de vida absoluto.
- **Comunicação Blindada:** Sem rede externa e sem writable mounts diretos do host.
- **Isolamento de Primitives:** Runtime inacessível de dentro da Sandbox.
- **Observabilidade:** Toda mutação material deve ser mediada e registrada pelo runtime.

## 2. Interface Abstrata (`ISandbox`)

```python
class ISandbox(ABC):
    # --- Lifecycle ---
    @abstractmethod
    def create(self, baseline_ref: str) -> SandboxCreateResult:
        """Inicializa o ambiente. Deve confirmar a materialização da baseline."""
        pass

    @abstractmethod
    def destroy(self) -> SandboxDestroyResult:
        """Elimina recursos. Deve reportar falhas de limpeza ou timeouts."""
        pass

    # --- Input / Mutation ---
    @abstractmethod
    def copy_in(self, source: Path, destination: Path) -> SandboxOpResult:
        """Staging de arquivos/artefatos para dentro da sandbox."""
        pass

    @abstractmethod
    def apply_mutation(self, mutation: MutationSpec) -> ExecutionResult:
        """Aplica alteração material (Patch, Script, etc) via especificação neutra."""
        pass

    # --- Execution ---
    @abstractmethod
    def run_command(self, command: str, timeout_seconds: float) -> ExecutionResult:
        """Executa comando shell e captura saída/evidência."""
        pass

    # --- Inspection / Evidence Collection ---
    @abstractmethod
    def list_files(self, path: str) -> ListFilesResult:
        """Lista arquivos para auditoria de estrutura."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> ReadFileResult:
        """Coleta conteúdo/evidência de arquivos específicos pós-mutação."""
        pass
```

## 3. Resultados Estruturados (Contratos de Erro)
- `SandboxCreateResult`: `id`, `success`, `status_code`, `materialized_ref`.
- `SandboxOpResult`: `success`, `error_message`, `bytes_written`.
- `ReadFileResult`: `success`, `content`, `hash_sha256`, `error`.

## 4. O Que Permanece Aberto
- A forma final do `MutationSpec` (começará aceitando `FilePatch`).
- A implementação obrigatória de `read_file` vs `collect_diff` na primeira versão.
- A tipagem exata dos novos resultados estruturados (`SandboxDestroyResult`).
