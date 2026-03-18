# AIOS — Documento Mestre de Continuidade

Contexto consolidado para retomar o trabalho em uma nova conversa sem perder decisões, estado atual e guardrails.

Atualizado em 18/03/2026

## 0. Convenção fixa deste documento

- Este arquivo é a referência canônica de continuidade do AIOS.
- Nome padrão fixo: `docs/AIOS_CONTINUIDADE_MESTRE.md`.
- Regra padrão: atualizar este arquivo in-place, em vez de criar novas variantes paralelas com nomes diferentes.
- Só criar cópia histórica quando houver uma virada real de estado ou fase; nesse caso, arquivar a versão anterior em `docs/archive/continuidade/AIOS_CONTINUIDADE_YYYY-MM-DD.md` antes da atualização.
- Toda atualização deve preservar quatro coisas com clareza:
  - estado atual
  - o que foi provado
  - o que continua aberto
  - próximo passo saudável
- Este documento deve permanecer executivo, disciplinado e orientado à retomada. Ele não substitui os documentos canônicos de lei, plano ou especificação detalhada.

## 1. Retrato executivo

| Tema | Status atual |
|---|---|
| Fase 0 | Encerrada como aprovada com ressalvas; mock-first gate passou e o esqueleto do sistema foi provado. |
| Lote 1 / 1B da Fase 1 | Homologado. A boundary E2B foi alinhada ao modelo canônico de egress com `default deny`, e a evidência final foi regenerada. |
| Sandbox de segurança-alvo | E2B é o candidato homologado atual para a boundary de segurança-alvo; `SubprocessSandbox` continua descartado para uso seguro. |
| Lote 2 (integração com LLM) | Deixa de estar bloqueado por pendência de boundary. O próximo movimento saudável é planejar sua abertura com escopo estreito, não abrir expansão caótica. |
| DELTA / SIGMA | Continuam como fonte futura de primitives específicas; não devem poluir o desenvolvimento agora. |
| Próximo foco saudável | Consolidar a nova linha de base pós-L1B e abrir o planejamento disciplinado do Lote 2, mantendo o AIOS limpo e sem reabrir arquitetura sem motivo forte. |

## 2. O que foi decidido ao longo da conversa

- O AIOS não deve ser uma reconstrução do Oracle-OS. A tese correta é construção do sucessor a partir do zero, usando aprendizados e primitives úteis, sem colocar o Oracle no centro.
- A arquitetura foi consolidada em torno de um runtime determinístico ao redor de um componente probabilístico.
- Foram adotados como pilares: FSM explícita, dual-truth (Git = código; ledger = execução), rollback obrigatório, schema boundary estrito, budget/termination explícitos e mock-first como gate de fundação.
- O projeto passou por várias etapas documentais: blueprints, red team, decision docket, lei provisória e plano canônico da Fase 0.
- Depois disso, a conversa migrou para backlog real, execução controlada por blocos/lotes e checkpoints humanos entre etapas.
- A policy de egress do AIOS foi fechada em favor do modelo canônico: `default deny + allowlist explícita`, e não `controlled cloud egress`.

## 3. Estado consolidado da Fase 0

- Fase 0 foi tratada como fundação estrutural, não como produto.
- Objetivo da Fase 0: provar o esqueleto do runtime antes de qualquer integração com LLM real.
- Decisões aceitas na Fase 0: Python 3.10+ / Pydantic v2 como default operacional provisório; dual-truth; rollback Git-based como baseline provisória; SandboxInterface como contrato; benchmark mock-first como gate oficial.
- FSM mínima foi refinada até incluir `ROLLBACK_PENDING`, budget/timeout explícitos e estados terminais semanticamente definidos.
- O benchmark mock-first passou nos cenários críticos: caminho feliz, proposta malformada, falha com rollback, timeout com efeito material e violação estrutural.
- Conclusão correta da Fase 0: aprovada com ressalvas. O cérebro do sistema funciona e destravou a validação séria da boundary na Fase 1.

## 4. O que foi provado

- FSM determinística com rollback explícito e terminação clara.
- Contratos core suficientemente rígidos para fundação: `Intent`, `ExecutionResult`, `LedgerEntry`, budgets e razões de terminação.
- Event log mínimo com encadeamento por hash como trilha auditável inicial.
- Rollback e restauração como propriedades reais do fluxo de execução.
- Dual-truth operacional: o estado do código é governado por Git; o estado da execução é governado pelo ledger.
- A `SandboxInterface` consegue abstrair múltiplos adaptadores sem vazar semântica de vendor.
- O benchmark mock-first demonstrou que o runtime sabe falhar sem corromper o repositório nem perder rastreabilidade.
- A boundary E2B agora demonstra:
  - isolamento do host
  - bloqueio de acesso ao host bridge
  - não vazamento de segredo do orquestrador
  - bloqueio de saída externa arbitrária
  - ciclo de vida e mutação estruturada funcionando

## 5. O que foi fechado no Lote 1B

- `SubprocessSandbox` foi descartado como candidato de segurança-alvo. Ele pode servir no máximo para desenvolvimento local básico, nunca para execução segura de código derivado de LLM.
- O E2B foi mantido como candidato principal e passou pela homologação final do Lote 1B.
- A divergência entre a Lei Provisória e a antiga leitura do harness foi resolvida em favor da Lei Provisória.
- O mecanismo de enforcement de egress foi confirmado no SDK E2B (`allow_internet_access=False`) e aplicado explicitamente no código.
- O harness foi corrigido para tratar bloqueio de saída externa arbitrária como `PASS` normativo.
- As evidências foram regeneradas após o patch e todos os testes relevantes passaram.

## 6. Boundary de sandbox — formulação final do estado atual

- A boundary de sandbox do AIOS está homologada para o escopo atual do Lote 1B.
- A formulação correta agora não é mais "a jaula contra o host parece boa, mas a saída ainda está em aberto".
- A formulação correta agora é: a boundary E2B está alinhada ao critério canônico atual do AIOS para o lote homologado, com `default deny` explícito e evidência empírica regenerada.
- Isso não significa congelamento eterno da solução de vendor; significa apenas que, para o escopo atual, a proof obligation da boundary foi cumprida.

## 7. Contratos e componentes que continuam importantes

- `SandboxInterface` canônica: `create`, `destroy`, `copy_in`, `apply_mutation`, `run_command`, `list_files`, `read_file`, com retornos estruturados.
- FSM v1.1: estados transientes `IDLE`, `INTENT_VALIDATION`, `SNAPSHOT_PENDING`, `EXECUTION_PENDING`, `VERIFICATION_PENDING`, `ROLLBACK_PENDING`; estados terminais `SUCCESS`, `FAILURE`, `ERROR`.
- `ExecutionBudget` como contrato explícito.
- `LedgerEntry` / event log como base de auditoria.
- `MutationSpec` como forma neutra de representar mutações sem congelar cedo demais um único mecanismo.
- `E2BSandboxAdapter` segue sendo peça importante da boundary e agora incorpora enforcement explícito de egress no código.

## 8. Estado atual do workspace

- O workspace foi reorganizado para melhorar continuidade e disciplina desde o início.
- Estrutura atual relevante:
  - `docs/` para documentos canônicos e continuidade
  - `sandbox/` para adaptador e harness
  - `artifacts/l1b/` para evidências da homologação do Lote 1B
  - `requirements.txt` na raiz com dependências principais do experimento
- Caminhos importantes no estado atual:
  - `docs/SUCCESSOR_SYSTEM_PROVISIONAL_LAW.md`
  - `docs/PLANO_CANONICO_EXECUCAO_FASE_0_FINAL.md`
  - `sandbox/e2b_adapter_v0.py`
  - `sandbox/sandbox_harness_v1.py`
  - `artifacts/l1b/l1b_audit_brute_logs.json`
  - `artifacts/l1b/l1b_final_evidence.json`
- `pydantic`, `python-dotenv` e `e2b` estão disponíveis tanto no `venv` quanto no Python global do ambiente atual.

## 9. Reanálise dos repositórios externos (somente código como verdade)

- Repositórios com valor direto para o sucessor: `DELTA_v102`, `delta_protocol`, `delta_v102_the_registrar` e `bautt-sigma-up`.
- Repositório com valor indireto como disciplina de dados: `construction-data-pipeline`.
- Repositório que não deve servir de base mental do core do AIOS: `notepress-saas`.
- Conclusão mais importante dessa leitura: o sucessor não deve nascer "a partir do DELTA" como bloco inteiro. Ele deve, no máximo, extrair primitives implementadas de integridade, política, rastreabilidade e proveniência quando o timing for certo.
- A leitura mais útil continua sendo: "o sucessor precisa mais dos dentes do DELTA e dos ossos de composição do SIGMA do que dos repositórios inteiros".

## 10. Decisão sobre DELTA-Lite

- A ideia de DELTA-Lite foi considerada estrategicamente boa, mas o timing foi julgado inadequado para entrar como frente formal de desenvolvimento neste momento.
- Decisão mantida: não puxar DELTA-Lite agora para o Antigravity e não poluir o AIOS com governança pesada antes do sistema respirar sozinho.
- Foi aceito apenas manter a ideia em parking lot técnico, com possíveis primitives futuras: envelope canônico de execução, policy decision explícita, redaction/classificação de segredos, proveniência por hash e perfis operacionais de política.
- Regra de timing: só reabrir DELTA-Lite quando duas condições forem verdadeiras:
  - boundary homologada sem ressalva operacional impeditiva
  - primeiro fluxo com LLM real funcionando de ponta a ponta

## 11. Guardrails fortes para a próxima conversa

- Não reabrir a arquitetura inteira.
- Não tratar inferência lógica como substituto de prova empírica.
- Não transformar a abertura do Lote 2 em expansão caótica.
- Não puxar DELTA-Lite agora como frente ativa.
- Manter o framing por famílias de abordagem, não por marcas isoladas, quando falar de sandbox.
- Separar sempre o que é default de desenvolvimento do que é segurança-alvo/produção.
- Sempre distinguir: o que foi provado, o que foi apenas decidido, o que está pendente e o que continua proibido.
- Preservar disciplina de escopo: um próximo passo principal por vez.

## 12. Próximo estado recomendado ao retomar

- O fechamento do Lote 1B não é mais o trabalho principal; ele já está consolidado.
- O movimento correto agora é um planejamento disciplinado de abertura do Lote 2, ainda com escopo estreito.
- Esse planejamento deve partir do estado atual já homologado da boundary, sem reabrir a discussão de egress que acabou de ser fechada.
- O primeiro passo saudável não é implementar integração ampla com LLM de uma vez; é definir o recorte mínimo do Lote 2 que respeita a arquitetura já estabilizada.
- Se for preciso pedir algo ao Antigravity no começo da próxima conversa, o ideal é um prompt curto e cirúrgico voltado a:
  - resumir o estado pós-L1B
  - identificar o menor recorte válido do Lote 2
  - propor o próximo passo prático sem abrir frentes paralelas

## 13. Resumo em uma frase

O AIOS já provou que o cérebro funciona e já homologou a jaula mínima necessária; a continuidade saudável agora depende de abrir o próximo lote com disciplina, sem dispersão e sem reabrir o que acabou de ser fechado.

## 14. Instruções para uso deste documento na próxima conversa

- Use este arquivo como contexto-base.
- Peça continuidade a partir do estado atual do AIOS, sem reabrir fases antigas.
- Se necessário, copie e cole os itens das seções 5, 6, 10, 11 e 12, porque elas concentram o que acabou de ser fechado, o que deve ser evitado e o que fazer a seguir.
- Caso o objetivo da nova conversa seja operacional, não volte para o fechamento do Lote 1B a menos que apareça uma nova evidência concreta de regressão.
- Caso o objetivo da nova conversa seja avanço de produto, comece pelo planejamento estreito do Lote 2 e não por DELTA-Lite, novos blueprints ou revisões fundacionais.
