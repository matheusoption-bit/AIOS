# Fundação de Contratos e Regras (Fase 0 - Bloco 2) - REVISADO

## 1. Tipatagem Core (Morfologia de Dados)

### Intent (Intenção do LLM)
Representa a proposta bruta gerada pelo modelo de linguagem.
- `id`: UUID
- `kind`: **Enum[PATCH, SHELL, GIT]** (Discriminador explícito do payload)
- `purpose`: String (Justificativa semântica)
- `payload`: **Union[FilePatch, ShellCommand, GitOperation]** (União discriminada por `kind`)
- `metadata`: **IntentMetadata** (Schema restrito e normativo)

**IntentMetadata Schema:**
- `model_name`: String (Ex: `gpt-4o`, `claude-3.5-sonnet`)
- `completion_id`: String (Referência ao provider)
- `prompt_tokens`: Integer
- `completion_tokens`: Integer
- `stop_reason`: String
- `sampling_params`: Dict (Ex: temperature)

### ExecutionResult (Veredito do Runtime)
O resultado determinístico da tentativa de aplicar uma Intent.
- `intent_id`: UUID
- `status`: Enum[SUCCESS, FAILURE, ERROR]
- `output`: String (Stdout/Stderr ou Diff resultante)
- `termination_reason`: TerminationReason (Mapeamento rígido com `status`)
- `git_ref`: String (Hash do commit/ref reprodutível associada)

**Mapeamento Semântico Status ↔ Reason:**
- `SUCCESS` ↔ `COMPLETED`
- `FAILURE` ↔ `MAX_CYCLES_REACHED`, `TIMEOUT`, `MALFORMED_PROPOSAL`
- `ERROR` ↔ `SECURITY_VIOLATION`, `UNRECOVERABLE_ERROR`

### LedgerEntry (Registro de Auditoria)
A entrada imutável no log de eventos.
- `index`: Integer (Sequence)
- `event_type`: Enum[INTENT_PROPOSED, EXECUTION_FINISHED, SYSTEM_STATE]
- `intent_id`: UUID (Obrigatório para referenciar origem)
- **`payload`: Union[Intent, ExecutionResult, SystemStatus]** (Tipagem estrita por `event_type`)
- `prev_hash`: String (Hash da entrada anterior)
- `entry_hash`: String (Hash calculado da entrada atual)
- `git_ref`: String (Referência Git associada a este estado)
- `timestamp`: ISO8601

## 2. Execution Budget (Contrato Explícito)

```python
class ExecutionBudget(BaseModel):
    max_cycles: int
    cycle_timeout_seconds: float
    total_timeout_seconds: float
    max_mutation_size_bytes: int
```

## 3. TerminationReason (Enums)
- `COMPLETED`: Objetivo atingido e verificado.
- `MAX_CYCLES_REACHED`: Esgotamento de tentativas.
- `TIMEOUT`: Esgotamento de tempo total ou de ciclo.
- `MALFORMED_PROPOSAL`: Schema da Intent inválido ou recusado.
- `SECURITY_VIOLATION`: Tentativa de bypass de sandbox ou acesso negado.
- `UNRECOVERABLE_ERROR`: Falha catastrófica de infra (ex: disk full).

## 4. Pendências de Arrasto (Status: OPEN)

| ID | Item | Descrição |
| :--- | :--- | :--- |
| **A1** | Memo de Arbitragem Stack | Formalização técnica da escolha Python/Pydantic vs TS/Zod. |
| **A2** | Spec Canônica Dual-Truth | Definição rigorosa da sincronia State-Repo sem micro-commits fixos. |
| **A3** | Matriz de Rollback Git | Tabela de cenários de falha física (dirty states, concurrent writes) e resposta. |
| **A4** | Regras do Event Log | Especificação canônica de cálculo de hash e serialização do ledger. |
