# Engenharia de Fluxo: Máquina de Estados (FSM) - Fase 0 (REVISADA)

## 1. Topologia de Estados

### Estados Transientes (Não-Absorventes)
- `IDLE`: Repouso. Aguardando nova `Intent`.
- `INTENT_VALIDATION`: Auditoria de schema e budget da proposta.
- `SNAPSHOT_PENDING`: Preparação da baseline reprodutível (Git).
- `EXECUTION_PENDING`: Mutação em progresso no ambiente isolado.
- `VERIFICATION_PENDING`: Auditoria pós-mutação (testes/checks).
- `ROLLBACK_PENDING`: Reversão atômica do estado físico em caso de falha.

### Estados Terminais (Absorventes)
- `SUCCESS`: Execução concluída e verificada. Produz **referência Git reprodutível** no Ledger.
- `FAILURE`: Encerramento controlado (Rollback OK ou sem efeito material).
- `ERROR`: Falha não controlada, rollback impossível ou violação estrutural.

## 2. Tabela de Transições Determinísticas

| Estado Atual | Evento | Próximo Estado | Observação |
| :--- | :--- | :--- | :--- |
| `IDLE` | `RECEIVE_INTENT` | `INTENT_VALIDATION` | Início do ciclo. |
| `INTENT_VALIDATION` | `VALID` | `SNAPSHOT_PENDING` | Registro de proposta no Ledger. |
| `INTENT_VALIDATION` | `INVALID` | `FAILURE` | Motivo: `MALFORMED_PROPOSAL`. |
| `INTENT_VALIDATION` | `BUDGET_EXCEEDED` | `FAILURE` | Motivo: `MAX_CYCLES/TIMEOUT`. |
| `SNAPSHOT_PENDING` | `READY` | `EXECUTION_PENDING` | Captura de `git_ref` inicial. |
| `SNAPSHOT_PENDING` | `SNAPSHOT_FAIL` | `ERROR` | Falha de infra-estrutura. |
| `EXECUTION_PENDING` | `FINISH` | `VERIFICATION_PENDING` | Captura de Output/Logs. |
| `EXECUTION_PENDING` | `TIMEOUT_EXCEEDED` | `ROLLBACK_PENDING` ou `FAILURE` | [1] |
| `EXECUTION_PENDING` | `SECURITY_TRIGGER` | `ERROR` | Violação estrutural detectada. |
| `VERIFICATION_PENDING` | `CHECK_OK` | `SUCCESS` | Produz Ref Git Final + Ledger Hash. |
| `VERIFICATION_PENDING` | `CHECK_FAIL` | `ROLLBACK_PENDING` | Gatilho de reversão. |
| `ROLLBACK_PENDING` | `ROLLBACK_OK` | `FAILURE` | Estado limpo após erro lógico. |
| `ROLLBACK_PENDING` | `ROLLBACK_FAIL` | `ERROR` | **HALT CRÍTICO** (Inconsistência). |

**Notas Normativas de Transição:**
[1] Se houver efeito material parcial detectado no repositório, a transição para `TIMEOUT_EXCEEDED` DEVE passar obrigatoriamente por `ROLLBACK_PENDING`. Se não houver efeito material ainda, pode transitar diretamente para `FAILURE`.

## 3. Invariantes de Fundação

### Invariante de Reversibilidade
Nenhuma execução pode encerrar em `SUCCESS` ou retornar ao estado `IDLE` sem que o runtime aponte deterministicamente:
1. O estado inicial do repositório (Git Ref inicial).
2. O estado final referenciado (Git Ref final no Ledger).
3. Em caso de falha, a confirmação de que o estado restaurado coincide com a baseline.

### Invariante de Auditoria
Toda transição com efeito relevante no runtime deve produzir registro auditável. Transições com efeito material no repositório devem ser registradas no Ledger imediatamente **antes** (intenção) e **depois** (evidência da mutação), garantindo a rastreabilidade forense completa.

## 4. Garantia de Terminação
A FSM é obrigada a transitar para um estado terminal se qualquer métrica do `ExecutionBudget` (definido no B2) for violada. O estado `ROLLBACK_PENDING` é o guardião final da integridade antes da declaração de `FAILURE`.
