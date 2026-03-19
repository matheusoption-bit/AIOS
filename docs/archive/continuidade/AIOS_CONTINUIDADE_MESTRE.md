# AIOS — Documento Mestre de Continuidade

Contexto consolidado para retomar o trabalho em uma nova conversa sem perder decisões, estado atual, guardrails e forma correta de operação.

Atualizado em 19/03/2026

## 0. Convenção fixa deste documento

- Este arquivo é a referência canônica de continuidade do AIOS.
- Nome padrão fixo: `docs/AIOS_CONTINUIDADE_MESTRE.md`.
- Regra padrão: atualizar este arquivo in-place, em vez de criar novas variantes paralelas com nomes diferentes.
- Só criar cópia histórica quando houver uma virada real de estado ou fase; nesse caso, arquivar a versão anterior em `docs/archive/continuidade/AIOS_CONTINUIDADE_YYYY-MM-DD.md` antes da atualização.
- Toda atualização deve preservar com clareza:
  - estado atual
  - o que foi provado
  - o que continua aberto
  - próximo passo saudável
  - o que NÃO deve ser feito agora
- Este documento deve permanecer executivo, disciplinado e orientado à retomada. Ele não substitui os documentos canônicos de lei, plano ou especificação detalhada.

## 1. Retrato executivo

| Tema | Status atual |
|---|---|
| Fase 0 | Encerrada como aprovada com ressalvas; mock-first gate passou e o esqueleto do sistema foi provado. |
| Lote 1 / 1B da Fase 1 | Homologado. A boundary E2B foi alinhada ao modelo canônico de egress com `default deny`, com evidência empírica regenerada. |
| Sandbox de segurança-alvo | E2B é o candidato homologado atual para a boundary de segurança-alvo; `SubprocessSandbox` continua descartado para uso seguro. |
| Lote 2 (integração com LLM) | Fechado na `main`. Já houve prova ponta a ponta com credenciais reais, homologação E2E, endurecimento do ledger e tratamento mínimo de failure modes/rollback. |
| Ledger do Lote 2 | Endurecido com `run_id`, `event_seq`, `event_id`, `schema_version`, hash chain SHA-256, `RUN_FINISHED` inequívoco, validador multi-run e política fail-closed proporcional. |
| Failure modes do Lote 2 | Tratados no escopo mínimo proporcional: provider, timeout, sandbox create, sandbox exec, evidência não encontrada, cleanup/destroy e falhas críticas do ledger. |
| DELTA / SIGMA | Continuam como fonte futura de primitives específicas; não devem poluir o desenvolvimento agora. |
| Documento estratégico-curatorial | Existe e foi preservado em `docs/strategy/`; é referência estratégica secundária, não backlog automático nem motor de execução. |
| Próximo foco saudável | Abrir uma branch nova e planejar o Lote 3 mínimo com escopo estreito, sem reabrir arquitetura e sem expansão caótica. |

## 2. O que foi decidido ao longo do processo

- O AIOS não deve ser uma reconstrução do Oracle-OS. A tese correta é construção do sucessor a partir do zero, usando aprendizados e primitives úteis, sem colocar o Oracle no centro.
- A arquitetura foi consolidada em torno de um runtime determinístico ao redor de um componente probabilístico.
- Foram adotados como pilares: FSM explícita, dual-truth (Git = código; ledger = execução), rollback obrigatório, schema boundary estrito, budget/termination explícitos e mock-first como gate de fundação.
- O projeto passou por blueprints, red team, decision docket, lei provisória e plano canônico da Fase 0.
- Depois disso, a conversa migrou para backlog real, execução controlada por blocos/lotes e checkpoints humanos entre etapas.
- A policy de egress do AIOS foi fechada em favor do modelo canônico: `default deny + allowlist explícita`, e não `controlled cloud egress`.
- O documento estratégico-curatorial deve permanecer em espera ativa: útil para visão e filtragem de hipóteses, mas sem autorização automática de implementação.
- Regra de maturidade mantida: fase/lote homologado -> endurecimento proporcional -> só então nova expansão, salvo evidência forte em contrário.
- Regra de branches adotada para blocos relevantes: fechar bloco na `main`, abrir branch nova para o próximo bloco, revisar antes de qualquer novo merge.

## 3. Estado consolidado da Fase 0

- Fase 0 foi tratada como fundação estrutural, não como produto.
- Objetivo da Fase 0: provar o esqueleto do runtime antes de qualquer integração com LLM real.
- Decisões aceitas na Fase 0: Python 3.10+ / Pydantic v2 como default operacional provisório; dual-truth; rollback Git-based como baseline provisória; `SandboxInterface` como contrato; benchmark mock-first como gate oficial.
- FSM mínima foi refinada até incluir `ROLLBACK_PENDING`, budget/timeout explícitos e estados terminais semanticamente definidos.
- O benchmark mock-first passou nos cenários críticos: caminho feliz, proposta malformada, falha com rollback, timeout com efeito material e violação estrutural.
- Conclusão correta da Fase 0: aprovada com ressalvas. O cérebro do sistema funciona e destravou a validação séria da boundary na Fase 1.

## 4. O que foi provado

### Fundação e boundary

- FSM determinística com rollback explícito e terminação clara.
- Contratos core suficientemente rígidos para fundação: `Intent`, `ExecutionResult`, `LedgerEntry`, budgets e razões de terminação.
- Event log mínimo com encadeamento por hash como trilha auditável inicial.
- Rollback e restauração como propriedades reais do fluxo de execução.
- Dual-truth operacional: o estado do código é governado por Git; o estado da execução é governado pelo ledger.
- A `SandboxInterface` abstrai múltiplos adaptadores sem vazar semântica de vendor.
- O benchmark mock-first demonstrou que o runtime sabe falhar sem corromper o repositório nem perder rastreabilidade.
- A boundary E2B demonstrou:
  - isolamento do host
  - bloqueio de acesso ao host bridge
  - não vazamento de segredo do orquestrador
  - bloqueio de saída externa arbitrária
  - ciclo de vida e mutação estruturada funcionando

### Lote 2

- Primeiro slice funcional do Lote 2 implementado.
- Chamada real ao provider fora da sandbox funcionando.
- Resposta JSON estruturada validada.
- Execução real na sandbox E2B funcionando.
- Evidência forte via smoke test determinístico confirmada.
- Homologação ponta a ponta com credenciais reais concluída.
- Ledger do Lote 2 endurecido e validado com:
  - `run_id`
  - `event_seq`
  - `event_id`
  - `schema_version`
  - `prev_hash`
  - `event_hash`
  - `RUN_FINISHED` terminal inequívoco
  - validação multi-run
  - enumeração de tipos/estágios/status/outcomes
- Failure modes mínimos tratados no runner para:
  - erro genérico de provider
  - timeout de provider
  - JSON/schema inválido
  - falha de criação da sandbox
  - falha de execução na sandbox
  - evidência não encontrada
  - cleanup/destroy com resultado registrado
  - falha crítica do ledger

## 5. O que foi fechado no Lote 1B

- `SubprocessSandbox` foi descartado como candidato de segurança-alvo. Pode servir no máximo para desenvolvimento local básico, nunca para execução segura de código derivado de LLM.
- O E2B foi mantido como candidato principal e passou pela homologação final do Lote 1B.
- A divergência entre leituras antigas e a Lei Provisória foi resolvida em favor da Lei Provisória.
- O enforcement de egress foi confirmado no SDK E2B (`allow_internet_access=False`) e aplicado explicitamente no código.
- O harness foi corrigido para tratar bloqueio de saída externa arbitrária como `PASS` normativo.
- As evidências foram regeneradas após o patch e todos os testes relevantes passaram.

## 6. Lote 2 — formulação final do estado atual

- O Lote 2 está encerrado como bloco de integração mínima bem-sucedida e endurecida.
- Formulação correta:
  - o AIOS já provou chamada real ao provider
  - já provou execução real na sandbox
  - já provou evidência forte
  - já endureceu o ledger mínimo
  - já tratou failure modes e rollback mínimo proporcionais
- Isso NÃO significa que o runtime final está pronto ou completo.
- Significa que a proof obligation do Lote 2, no escopo mínimo definido, foi cumprida.
- O commit de fechamento do Lote 2 já está publicado na `main`: `57f1e8237142448670afd9569fa9c176ba810ca7`.

## 7. Contratos e componentes que continuam importantes

- `SandboxInterface` canônica: `create`, `destroy`, `copy_in`, `apply_mutation`, `run_command`, `list_files`, `read_file`, com retornos estruturados.
- FSM v1.1: estados transientes `IDLE`, `INTENT_VALIDATION`, `SNAPSHOT_PENDING`, `EXECUTION_PENDING`, `VERIFICATION_PENDING`, `ROLLBACK_PENDING`; estados terminais `SUCCESS`, `FAILURE`, `ERROR`.
- `ExecutionBudget` como contrato explícito.
- `LedgerEntry` / event log como base de auditoria.
- `MutationSpec` como forma neutra de representar mutações sem congelar cedo demais um único mecanismo.
- `E2BSandboxAdapter` como peça da boundary.
- `L2Ledger` como trilha endurecida mínima do Lote 2.
- `validate_ledger.py` como validador multi-run do ledger endurecido do Lote 2.

## 8. Estado atual do repositório

Estrutura relevante no estado atual:

- `docs/` para documentos canônicos e continuidade
- `docs/strategy/` para documentos estratégicos-curatoriais
- `artifacts/l1b/` para evidências da homologação do Lote 1B
- `artifacts/l2/` para ledger, revisão local e documentação do Lote 2
- `src/lote2/` para implementação real do slice mínimo, ledger e validador
- `requirements.txt` na raiz com dependências principais do experimento

Caminhos importantes:

- `docs/AIOS_CONTINUIDADE_MESTRE.md`
- `docs/SUCCESSOR_SYSTEM_PROVISIONAL_LAW.md`
- `docs/PLANO_CANONICO_EXECUCAO_FASE_0_FINAL.md`
- `docs/planning/status/task_tracking.md`
- `docs/strategy/AIOS_V8_Guia_Estrategico_Curado_Consolidado.md`
- `src/lote2/response_schema.py`
- `src/lote2/provider_client.py`
- `src/lote2/lote2_runner.py`
- `src/lote2/ledger.py`
- `src/lote2/validate_ledger.py`
- `artifacts/l2/l2_execution_ledger.jsonl`
- `artifacts/l2/l2_execution_ledger.jsonl.pre_hardening`

## 9. Decisão sobre DELTA-Lite e documento estratégico

- A ideia de DELTA-Lite continua estrategicamente boa, mas o timing permanece inadequado para virar frente ativa agora.
- Condições mínimas que já foram alcançadas:
  - boundary homologada sem ressalva impeditiva
  - primeiro fluxo com LLM real funcionando de ponta a ponta
- Mesmo assim, a decisão operacional continua:
  - não puxar DELTA-Lite como frente formal agora
  - não poluir o AIOS com governança pesada antes do próximo recorte mínimo do produto
- O documento estratégico-curatorial em `docs/strategy/` foi preservado.
- Regra de uso:
  - não é backlog
  - não é roadmap vinculante
  - não reabre arquitetura sozinho
  - não supera o repositório
  - não supera evidência
  - serve para filtrar hipóteses, prompts e possíveis futuros incrementos
- O sistema deve seguir a lógica: usar o documento estratégico como mapa de futuro, não como ordem de marcha.

## 10. Guardrails fortes para a próxima conversa

- Não reabrir a arquitetura inteira.
- Não tratar inferência lógica como substituto de prova empírica.
- Não transformar a abertura do Lote 3 em expansão caótica.
- Não puxar DELTA-Lite agora como frente ativa.
- Manter o framing por famílias de abordagem, não por marcas isoladas, quando falar de sandbox.
- Separar sempre o que é default de desenvolvimento do que é segurança-alvo/produção.
- Distinguir sempre: o que foi provado, o que foi implementado, o que foi apenas planejado, o que é hipótese, o que está revogado.
- Preservar disciplina de escopo: um próximo passo principal por vez.
- Não misturar brainstorm estratégico com backlog executável.
- Não deixar documento estratégico bonito sequestrar a execução.
- Fechou bloco relevante -> `main`; próximo bloco relevante -> branch nova; revisão antes de merge.
- Priorizar prompts econômicos:
  - prompt curto para devolutiva de plano
  - prompt médio para endurecimento/implementação relevante
  - prompt completo só para mudança arquitetural, auditoria pesada ou virada crítica de fase
- Política de uso de modelos:
  - Gemini 3 Flash para tarefas leves, ajustes, revisões e refinamentos
  - Gemini 3.1 Pro como cavalo de batalha principal
  - Claude / GPT OSS / premium apenas quando o risco técnico justificar
- Formato padrão de prompts para ferramentas externas:
  - título
  - modelo sugerido
  - plano B
  - caixa de prompt só com conteúdo copiável

## 11. Próximo estado recomendado ao retomar

- O fechamento do Lote 2 já está consolidado e publicado na `main`.
- O movimento correto agora é abrir uma branch nova e planejar o Lote 3 mínimo.
- Esse planejamento deve:
  - partir do que o Lote 2 já provou
  - definir o que o Lote 3 NÃO deve ser agora
  - propor 2 ou 3 recortes mínimos possíveis
  - escolher 1 recorte recomendado
  - manter o AIOS fora de multi-agent, memória longa ampla, planner geral e observabilidade pesada nesta etapa
- O primeiro passo saudável da próxima conversa não é implementar Lote 3 de uma vez.
- O primeiro passo saudável é:
  - revisar o estado atual
  - confirmar o fechamento do Lote 2
  - abrir branch nova
  - definir o recorte mínimo do Lote 3

## 12. Forma correta de operar nas próximas conversas

- Tratar a conversa nova como continuação direta desta.
- Usar este documento como contexto-base.
- Considerar o repositório como fonte principal de verdade.
- Quando receber artefatos do Antigravity:
  - ler tudo
  - identificar o que foi realmente feito
  - localizar lacunas, inconsistências e oportunidades
  - propor o próximo prompt imediatamente
- Quando receber plano de implementação:
  - dar parecer objetivo
  - listar ajustes cirúrgicos
  - gerar prompt curto para atualização do plano, salvo se o risco exigir algo mais completo
- Quando fechar uma fase ou bloco:
  - decidir se já vai para `main`
  - só depois abrir branch nova para o próximo bloco

## 13. Resumo em uma frase

O AIOS já provou o cérebro, já homologou a jaula mínima, já integrou LLM real com evidência forte e já endureceu o Lote 2; a continuidade saudável agora depende de abrir o Lote 3 mínimo com disciplina, em branch nova, sem dispersão e sem transformar visão estratégica em execução prematura.

## 14. Instruções de uso deste documento na próxima conversa

- Use este arquivo como contexto-base.
- Peça continuidade a partir do estado atual do AIOS, sem reabrir fases antigas.
- Se necessário, destaque especialmente as seções 1, 6, 9, 10 e 11.
- Se o objetivo da nova conversa for operacional:
  - não volte para o fechamento do Lote 1B nem do Lote 2
  - comece pelo planejamento estreito do Lote 3
- Se o objetivo da nova conversa for revisão estratégica:
  - mantenha o documento em `docs/strategy/` como referência secundária
  - não misture brainstorm com backlog
- Se for preciso pedir algo ao Antigravity no começo da próxima conversa, o ideal é um prompt curto e cirúrgico voltado a:
  - resumir o estado pós-Lote 2
  - abrir branch nova
  - identificar o menor recorte válido do Lote 3
  - propor o próximo passo prático sem abrir frentes paralelas
