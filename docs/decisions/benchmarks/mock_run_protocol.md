# Protocolo de Benchmark: Mock-First Gate (Fase 0)

## 1. Objetivo Executivo
Validar a integridade mecânica da FSM, dos Contratos Core e do Ledger através de execuções determinísticas simuladas. **Este teste prova o esqueleto, não a segurança do adaptador de sandbox.**

## 2. Proibições Estritas (RedLines)
- **NO LLM:** Uso exclusivo de intents pré-definidas (Mocks).
- **NO API:** Sem chamadas externas ou dependências de rede.
- **NO VENDOR:** Uso do adaptador de portabilidade provado no B4.
- **NO INVENT:** Proibida qualquer alteração conceitual na arquitetura durante o gate.

## 3. Matriz de Cenários e Expectativa de Ledger

| ID | Cenário | Eventos Mínimos no Ledger | Veredito de Sucesso (Físico) |
| :--- | :--- | :--- | :--- |
| **S1** | **Caminho Feliz** | `INTENT_PROPOSED`, `EXECUTION_FINISHED`, `SYSTEM_STATE` | `rev-parse HEAD` atualizado; Diff vazio vs Ref Final. |
| **S2** | **Proposta Inválida** | `INTENT_PROPOSED`, `EXECUTION_FINISHED` (Malformed) | `git status` limpo; HEAD inalterado; Sem mutação. |
| **S3** | **Falha + Rollback** | `INTENT_PROPOSED`, `EXECUTION_FINISHED`, `ROLLBACK_TRIGGERED`, `SYSTEM_STATE` | `git status` limpo; `rev-parse HEAD` == Baseline; Sem arquivos residuais. |
| **S4** | **Timeout Material** | `INTENT_PROPOSED`, `EXECUTION_FINISHED`, `ROLLBACK_TRIGGERED`, `SYSTEM_STATE` | `git status` limpo; HEAD == Baseline; Reversão de mutação parcial provada. |
| **S5** | **Violação Seg.** | `INTENT_PROPOSED`, `SECURITY_VIOLATION_DETECTED`, `EXECUTION_FINISHED` | **HALT**; Se mutação parcial: Rollback comprovado; Se limpo: ERROR imediato. |

## 4. Invariantes de Passagem e Critérios de Restauração

O sistema só é considerado "Aprovado na Fase 0" se, após cada cenário de falha (S2, S3, S4, S5), o repositório atender rigorosamente:
1. **Status Limpo:** `git status --porcelain` retorna vazio.
2. **HEAD íntegro:** `git rev-parse HEAD` coincide com a baseline de teste capturada no `SNAPSHOT_PENDING`.
3. **Zero Resíduos:** Nenhum arquivo não rastreado (untracked) ou diretório temporário criado pelo cenário permanece no workspace.
4. **Diff Vazio:** `git diff HEAD` não apresenta alterações materiais em relação à baseline.

## 5. Regra de Segurança para S5 (Violação Estrutural)
No cenário de **Segurança (S5)**:
- Se houver detecção prematura (sem efeito material): Terminação em `ERROR` imediato preservando o log.
- Se houver indício de efeito material parcial antes do trigger: A FSM é obrigada a passar por `ROLLBACK_PENDING` para garantir a integridade física antes de atingir o estado de Halt terminal.

## 6. Limites de Validação
- O benchmark valida a **Orquestração** (Cérebro).
- O isolamento forte do adaptador de sandbox permanece um item aberto para a Fase 1.
