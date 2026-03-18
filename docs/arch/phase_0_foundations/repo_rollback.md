# Especificação: Rollback do Repositório (Fase 0)

## 1. Definição de Escopo
O Rollback do Repositório foca na **persistência física do código** (Truth A), sendo independente do isolamento de execução da Sandbox.

## 2. Mecanismo Canônico: Git-Based Reset
Para a Fase 0, a integridade é mantida via referências Git.

### Operação de Baseline (Pre-Mutation)
Antes de qualquer envio para `EXECUTION_PENDING`:
1. O runtime captura o `git_rev` atual (ex: SHA do commit).
2. Se o repositório estiver "sujo" (dirty), a FSM deve transitar para `ERROR`.

### Operação de Restauração (Rollback)
Disparada no estado `ROLLBACK_PENDING` por um `CHECK_FAIL`:
1. `git reset --hard <baseline_rev>`
2. `git clean -fd` (Limpeza de arquivos não rastreados).

## 3. Invariante de Restauração
Nenhum rollback é considerado `ROLLBACK_OK` se um `git status --porcelain` retornar qualquer saída após a operação. Falha na limpeza física força a transição imediata para `ERROR` (Halt do Sistema).

## 4. Limites de Fase 0
- Não há suporte para "Merge/Rebase" automático em caso de conflitos externos.
- O sistema assume exclusividade de escrita no diretório alvo durante o ciclo da FSM.
