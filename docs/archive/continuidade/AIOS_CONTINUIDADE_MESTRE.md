# AIOS — Documento Mestre de Continuidade

Contexto consolidado para retomar o trabalho em uma nova conversa sem perder decisões, estado atual, guardrails e forma correta de operação.

Atualizado em 19/03/2026

## 0. Convenção fixa deste documento

- Este arquivo é a referência de continuidade usada para retomar o AIOS com contexto operacional.
- Regra padrão: atualizar este documento in-place com o estado real do repositório e da branch ativa, sem criar variantes paralelas desnecessárias.
- Toda atualização deve preservar com clareza:
  - estado atual
  - o que foi provado
  - o que foi implementado
  - o que continua aberto
  - próximo passo saudável
  - o que NÃO deve ser feito agora
- Este documento é executivo e orientado à retomada. Ele não substitui especificações detalhadas, leis provisórias nem documentos estratégicos.

## 1. Retrato executivo

| Tema | Status atual |
|---|---|
| Fase 0 | Encerrada como aprovada com ressalvas; mock-first gate passou e o esqueleto do sistema foi provado. |
| Lote 1 / 1B da Fase 1 | Homologado. A boundary E2B foi alinhada ao modelo canônico de egress com `default deny`, com evidência empírica regenerada. |
| Sandbox de segurança-alvo | E2B continua como boundary homologada; `SubprocessSandbox` permanece descartado para execução segura. |
| Lote 2 | Continua existente como legado, mas agora deve ficar desativado por padrão. Só pode rodar com override explícito `AIOS_ENABLE_LEGACY_LOTE2=1`. |
| Lote 3 | Endurecido como caminho seguro padrão na branch `ci-gate-lote3`, com write boundary estreita, policy guard leve e testes offline passando. |
| Ledger | Evoluiu para um estado mais forte: sanitização, `integrity_mode`, `evidence_level`, HMAC e validação compatível com legado. |
| CI Gate | Endurecido e operacional na branch `ci-gate-lote3`: scanner ampliado, higiene de artefatos, lockfile com hashes e suíte offline. |
| Supply chain | `requirements.lock` gerado; workflows passam a instalar com `--require-hashes`; actions pinadas por SHA. |
| Prompting / memória | Regra formalizada: ledger bruto não entra em contexto de prompting; histórico futuro deve passar por resumo determinístico separado. |
| Estado de merge | Hardening implementado localmente e validado; ainda depende de commit/push/PR/merge e de configuração manual de branch protection no GitHub. |
| Próximo foco saudável | Fechar o PR da branch `ci-gate-lote3`, configurar branch protection e só então avançar para defesa em profundidade e próximos recortes do runtime. |

## 2. O que foi decidido ao longo do processo

- O AIOS não deve ser uma reconstrução do Oracle-OS. A tese correta é construção do sucessor a partir do zero, usando aprendizados e primitives úteis, sem colocar o Oracle no centro.
- A arquitetura foi consolidada em torno de um runtime determinístico ao redor de um componente probabilístico.
- Foram adotados como pilares: FSM explícita, dual-truth, rollback obrigatório, schema boundary estrito, budget/termination explícitos e mock-first como gate de fundação.
- A policy de egress do AIOS foi fechada em favor do modelo canônico: `default deny + allowlist explícita`.
- O documento estratégico-curatorial deve permanecer como referência secundária, nunca como backlog automático.
- Regra de maturidade mantida: fase/lote homologado -> endurecimento proporcional -> só então nova expansão.
- Segurança deve ser inteligente:
  - bloquear fortemente o que é estruturalmente perigoso
  - colocar em `shadow mode` o que ainda precisa de telemetria
  - evitar policies vagas e heurísticas infladas
- Regra formal nova:
  - ledger bruto não pode ser usado como memória ou contexto do modelo
  - qualquer memória futura deve ser derivada de resumo determinístico separado
- Regra operacional nova:
  - o Lote 3 passa a ser o caminho seguro padrão
  - o Lote 2 fica restrito a modo legado explícito
- Regra de governança agora explícita:
  - `main` deve operar com branch protection, PR obrigatório e status checks do CI Gate

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

- Chamada real ao provider fora da sandbox funcionando.
- Resposta JSON estruturada validada.
- Execução real na sandbox E2B funcionando.
- Evidência forte via smoke test determinístico confirmada.
- Homologação ponta a ponta com credenciais reais concluída.
- Ledger do Lote 2 foi endurecido progressivamente e agora suporta:
  - `run_id`
  - `event_seq`
  - `event_id`
  - `schema_version`
  - `prev_hash`
  - `event_hash`
  - `RUN_FINISHED` terminal inequívoco
  - `integrity_mode`
  - `evidence_level`
  - sanitização de payload
  - validação multi-run
  - compatibilidade controlada com formato legado

### Hardening pós-Lote 2 / Lote 3 seguro

- O Lote 3 foi endurecido para operar com write boundary estreita em `/tmp/aios_workspace/outputs`.
- `target_path` agora é validado contra subárvore fixa, não contra o workspace amplo.
- `content` passou a ter limite formal de tamanho.
- O schema do Lote 3 foi endurecido com `extra="forbid"`.
- Um `policy guard` leve foi introduzido em `shadow mode` para registrar payloads suspeitos sem bloquear prematuramente casos legítimos.
- O runner do Lote 3 agora separa melhor intenção, política, mutação e evidência.
- O ledger agora registra melhor a diferença entre sucesso simples e sucesso com prova.
- O sistema passou a falhar fechado quando o ledger degrada antes de checkpoints críticos.
- A regra "ledger bruto não é prompt" foi materializada no código como guardrail explícito.

### CI / governança técnica

- O scanner do CI agora cobre `src/`, `infra/`, `tests/` e `scripts/`.
- Regressões óbvias de shell e chamadas perigosas adicionais passaram a ser verificadas.
- O CI Gate agora verifica também higiene de artefatos e suíte offline de testes.
- O pipeline passou a instalar dependências via lockfile com hashes.
- Foi preparada uma suíte separada de integração da sandbox, fora do gate rápido de PR.

## 5. O que foi fechado no Lote 1B

- `SubprocessSandbox` foi descartado como candidato de segurança-alvo. Pode servir no máximo para desenvolvimento local básico, nunca para execução segura de código derivado de LLM.
- O E2B foi mantido como candidato principal e passou pela homologação final do Lote 1B.
- A divergência entre leituras antigas e a Lei Provisória foi resolvida em favor da Lei Provisória.
- O enforcement de egress foi confirmado no SDK E2B (`allow_internet_access=False`) e aplicado explicitamente no código.
- O harness foi corrigido para tratar bloqueio de saída externa arbitrária como `PASS` normativo.
- As evidências foram regeneradas após o patch e todos os testes relevantes passaram.

## 6. Formulação correta do estado atual

- O Lote 2 não deve mais ser tratado como caminho operacional padrão.
- O Lote 2 continua existindo como legado controlado para compatibilidade e diagnóstico histórico.
- O Lote 3 passa a ser a referência oficial de execução segura no estado atual do projeto.
- O hardening mais recente foi implementado na branch `ci-gate-lote3`.
- Esse hardening já passou na validação local, mas ainda não deve ser tratado como plenamente consolidado até:
  - commit e push da branch
  - abertura e revisão do PR
  - merge em `main`
  - ativação manual da branch protection e dos status checks obrigatórios
- Formulação correta:
  - a foundation do sistema está provada
  - a boundary segura mínima está provada
  - a integração real com provider está provada
  - o runtime foi endurecido além do mínimo inicial
  - a governança de CI foi fortalecida
  - ainda resta fechar o circuito operacional no GitHub

## 7. Contratos e componentes que continuam importantes

- `SandboxInterface` canônica como contrato-base.
- `E2BSandboxAdapter` como boundary completa.
- Fachada segura da sandbox para o runtime seguro, reduzindo exposição casual de métodos poderosos.
- `L2Ledger` como trilha auditável com suporte a HMAC e validação compatível com legado.
- `validate_ledger.py` como validador multi-run e multi-esquema.
- `WriteFileIntent` como boundary estruturada do Lote 3.
- `validate_safe_path()` como política de contenção de path do Lote 3.
- `policy_guard.py` como camada leve de observação e futuro enforcement gradual.
- `prompt_context.py` como guardrail explícito contra uso de ledger bruto em prompting.
- `scripts/ci/check_disallowed_calls.py` e `scripts/ci/check_tracked_artifacts.py` como guardrails oficiais do repositório.

## 8. Estado atual do repositório

Estrutura relevante no estado atual:

- `docs/` para documentos canônicos, contratos e continuidade
- `docs/archive/continuidade/` para histórico de continuidade
- `docs/security/` para contrato operacional de hardening
- `docs/strategy/` para documentos estratégicos-curatoriais
- `artifacts/l1b/` para evidências da homologação do Lote 1B
- `artifacts/l2/` para documentação e materiais do Lote 2
- `src/lote2/` para legado controlado, ledger e validador
- `src/lote3/` para o caminho seguro atual
- `src/common/` para guardrails compartilhados de prompting
- `infra/sandbox/` para a boundary E2B e harness
- `scripts/ci/` para os gates de segurança do repositório
- `tests/` para suíte offline
- `tests/integration/` para checks mais pesados e reais da sandbox
- `requirements.txt` e `requirements.lock` na raiz

Caminhos importantes:

- `docs/archive/continuidade/AIOS_CONTINUIDADE_MESTRE.md`
- `docs/security/runtime_hardening_contract.md`
- `docs/SUCCESSOR_SYSTEM_PROVISIONAL_LAW.md`
- `docs/PLANO_CANONICO_EXECUCAO_FASE_0_FINAL.md`
- `docs/planning/status/task_tracking.md`
- `docs/strategy/AIOS_V8_Guia_Estrategico_Curado_Consolidado.md`
- `src/lote2/lote2_runner.py`
- `src/lote2/ledger.py`
- `src/lote2/validate_ledger.py`
- `src/lote3/lote3_runner.py`
- `src/lote3/path_policy.py`
- `src/lote3/policy_guard.py`
- `src/lote3/response_schema.py`
- `src/common/prompt_context.py`
- `infra/sandbox/adapter.py`
- `scripts/ci/check_disallowed_calls.py`
- `.github/workflows/ci-gate.yml`
- `.github/workflows/sandbox-integration.yml`

## 9. Decisão sobre DELTA-Lite e documento estratégico

- A ideia de DELTA-Lite continua estrategicamente boa, mas o timing permanece inadequado para virar frente ativa agora.
- O AIOS já avançou além do ponto em que fazia sentido usar estratégia como substituto de execução.
- O documento estratégico-curatorial em `docs/strategy/` foi preservado.
- Regra de uso:
  - não é backlog
  - não é roadmap vinculante
  - não reabre arquitetura sozinho
  - não supera o repositório
  - não supera evidência
  - serve para filtrar hipóteses, prompts e futuros incrementos
- O sistema deve seguir a lógica: usar o documento estratégico como mapa de futuro, não como ordem de marcha.

## 10. Guardrails fortes para a próxima conversa

- Não reabrir a arquitetura inteira.
- Não tratar inferência lógica como substituto de prova empírica.
- Não confundir branch validada localmente com proteção operacional já fechada.
- Não reativar o Lote 2 como padrão.
- Não usar ledger bruto como contexto de prompting.
- Não transformar `shadow mode` em bloqueio prematuro sem telemetria.
- Não puxar DELTA-Lite agora como frente ativa.
- Não misturar brainstorm estratégico com backlog executável.
- Distinguir sempre:
  - o que foi provado
  - o que foi implementado
  - o que foi validado só localmente
  - o que já foi merged
  - o que ainda depende de configuração externa
- Preservar disciplina de escopo: um próximo passo principal por vez.
- Fechou bloco relevante -> `main`; próximo bloco relevante -> branch nova; revisão antes de merge.

## 11. Próximo estado recomendado ao retomar

- O hardening da branch `ci-gate-lote3` deve ser tratado como o bloco prioritário de fechamento.
- O movimento correto ao retomar é:
  - revisar rapidamente a branch e a descrição do PR
  - commitar o estado validado localmente
  - push da branch
  - abrir e revisar o PR
  - configurar branch protection e status checks obrigatórios na `main`
  - opcionalmente rodar o workflow de integração da sandbox com segredo real
- Só depois disso o próximo passo saudável é abrir uma nova branch para defesa em profundidade e expansão incremental.
- O primeiro passo da próxima conversa não deve ser "inventar um novo lote".
- O primeiro passo saudável é verificar:
  - se o PR foi merged
  - se a branch protection ficou ativa
  - se o CI Gate virou contrato real da `main`

## 12. Forma correta de operar nas próximas conversas

- Tratar a conversa nova como continuação direta desta.
- Usar este documento como contexto-base.
- Considerar o repositório como fonte principal de verdade.
- Considerar que:
  - `main` só estará efetivamente blindada depois da configuração no GitHub
  - a branch atual já contém a implementação principal do hardening
  - a suíte offline já passou localmente
- Quando receber artefatos ou pareceres externos:
  - ler tudo
  - separar achado confirmado de extrapolação
  - reconciliar com o estado real do código
  - transformar isso em próximo passo concreto
- Quando receber novo plano de segurança:
  - avaliar por camadas
  - bloquear o que é estruturalmente perigoso
  - deixar em observação o que ainda precisa de telemetria
- Quando fechar um bloco:
  - decidir se já vai para `main`
  - só depois abrir branch nova para o próximo bloco

## 13. Resumo em uma frase

O AIOS já provou a fundação, homologou a boundary E2B, integrou provider real, endureceu ledger/runtime/CI e colocou o Lote 3 como caminho seguro padrão; a continuidade saudável agora depende de fechar o PR de hardening, ativar a governança real no GitHub e só então seguir para defesa em profundidade sem dispersão.

## 14. Instruções de uso deste documento na próxima conversa

- Use este arquivo como contexto-base.
- Se a conversa nova for operacional, comece perguntando pelo estado da branch `ci-gate-lote3` e do PR correspondente.
- Destaque especialmente as seções 1, 6, 10 e 11.
- Se o objetivo for segurança:
  - verificar primeiro merge, branch protection e status checks
  - só depois discutir novos endurecimentos
- Se o objetivo for expansão do runtime:
  - manter o Lote 3 como baseline segura
  - não reabrir Lote 2 como padrão
  - não introduzir memória longa ampla nem multi-agent agora
- Se for preciso pedir algo ao Antigravity ou outra IA no começo da próxima conversa, o ideal é um prompt curto e cirúrgico voltado a:
  - verificar se o hardening da `ci-gate-lote3` já está merged
  - checar se a branch protection está ativa
  - resumir o estado pós-hardening do runtime
  - propor o próximo passo prático sem abrir frentes paralelas
