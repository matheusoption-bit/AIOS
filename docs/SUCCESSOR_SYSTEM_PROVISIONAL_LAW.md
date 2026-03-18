# Lei Provisória do Sistema Sucessor

> **Conselho Final de Arbitragem:** Principal Software Architect · Runtime Reliability Judge · Deterministic Systems Architect · Security Boundary Judge · Systems Governance Editor · Technical Decision Arbiter · Architecture Consistency Auditor · Red-Team Integrator · Normative Systems Drafting Lead
>
> **Método:** Arbitragem dos oito documentos-fonte (Perplexity.md, GPT.md, Grok.md, Gemini.md/RULE, V1 MAX, V2 BLIND, RED_TEAM_V3_BLIND, DECISION_DOCKET). Cada tema recebe uma única formulação canônica. Contradições são resolvidas com justificativa explícita. Nenhuma ambiguidade é preservada por elegância ou diplomacia.
>
> **Data de promulgação:** 2026-03-17

---

## 1. Veredito Executivo

### O que foi consolidado

O corpus de oito documentos demonstra convergência real e irrefutável em seis axiomas estruturais:

1. O LLM é coprocessador de proposta — sem autoridade de efeito direto.
2. A unidade central é um ciclo de execução com estado finito e budget explícito.
3. Toda mutação de arquivo usa escrita atômica (arquivo temporário + rename).
4. Schema estrito na fronteira LLM → runtime é obrigatório antes de qualquer efeito.
5. Nenhuma escrita no filesystem do host fora de sandbox isolado.
6. Um registro append-only de transições de execução é necessário desde o Dia 1.

Esses seis axiomas são **Lei Provisória imediata**. Não requerem mais prova. Não requerem mais debate.

### O que foi reconciliado

Cinco contradições materiais foram identificadas entre os documentos e resolvidas por arbitragem neste documento:

1. **Ledger único vs. dual-truth** — Resolvido em favor de dual-truth (Git + event log).
2. **SQLite vs. JSONL no Dia 1** — Resolvido: JSONL com hash simples no Dia 1; SQLite na Fase 3.
3. **HMAC no Dia 1 vs. Fase 3** — Resolvido: hash SHA-256 simples no Dia 1; HMAC na Fase 3.
4. **Git Branch como snapshot unificado** — Resolvido: dois mecanismos distintos para dois problemas distintos.
5. **Multi-agent como "múltiplas chamadas LLM"** — Resolvido: a proibição correta é agentes com autoridade autônoma de efeito, não múltiplas chamadas LLM por ciclo.

### O que continua aberto

Três decisões permanecem formalmente abertas e exigem experimento antes de freeze:

1. **Stack/linguagem do núcleo** (TypeScript+Zod vs. Python+Pydantic).
2. **Fornecedor de sandbox** (E2B vs. alternativas — a propriedade está congelada, o vendor não).
3. **Portabilidade literal do código DELTA** (cross-language boundary não quantificado).

### Situação do projeto

**O projeto pode entrar na Fase 0** após conclusão dos experimentos obrigatórios (máximo 8 horas de trabalho técnico).

**O projeto pode preparar a Fase 1** após o mock test do ciclo completo passar sem LLM real.

---

## 2. Contradições Encontradas e Resolvidas

| Contradição | Onde apareceu | Por que é relevante | Decisão de arbitragem | O que foi descartado |
|---|---|---|---|---|
| Ledger como única fonte da verdade (single-truth) vs. Git+EventLog (dual-truth) | V1: single-truth c/ conf. 95. V2: dual-truth c/ conf. 65. RED_TEAM: dual-truth c/ conf. 82. DOCKET: dual-truth c/ conf. 82 | Impacta toda a arquitetura de storage, snapshot e schema de eventos | **Dual-truth canônico:** Git é a verdade do código; event log é a verdade das execuções. Os dois se comunicam por referência (entries referenciam commit hashes). | Single-truth absoluto. Git já é append-only, content-addressed e criptograficamente íntegro para estado de código. Redundar com ledger é overengineering demonstrável. |
| SQLite WAL como storage do Dia 1 vs. JSONL simples | V1 MAX: SQLite+HMAC JSONL. V2: SQLite c/ conf. 88. RED_TEAM: rebaixa para 65, defende JSONL para Fase 1-2. DOCKET: "SQLite WAL + schema". Gemini.md (RULE): cita SQLite em múltiplas partes | Volume de eventos em Fase 0-2 é baixo; JSONL scan linear < 10ms para < 10.000 entradas | **JSONL append-only no Dia 1.** 5 campos mínimos + hash SHA-256 simples. SQLite entra apenas quando uma query real exigir indexação que scan linear não serve. | SQLite WAL como requisito do Dia 1. Adiciona zero benefício quando o volume não justifica. |
| HMAC chaining no Dia 1 vs. Fase 3 | V1: Dia 1 c/ conf. 85. V2: parcialmente reaberto. RED_TEAM: conf. 45, defende Fase 3. DOCKET: conf. 55 (HMAC Dia 1) | HMAC exige gerenciamento de chaves. Nenhum documento especificou o modelo de ameaça que HMAC defende antes da Fase 3. | **HMAC na Fase 3. Hash SHA-256 simples (prev_id + conteúdo) no Dia 1.** Tamper-detectable suficiente para Fases 1-2. | HMAC como requisito do Dia 1. Sem modelo de ameaça formalizado, HMAC é overhead operacional sem benefício de correção. |
| Git Branch como mecanismo unificado de snapshot | V1: Git Branch c/ conf. 80. V2 e RED_TEAM: conflação identificada. DOCKET: "separação dual-mecanismo" c/ conf. 82 | Sandbox filesystem e repositório persistente são dois problemas distintos com mecanismos distintos | **Dois mecanismos distintos:** (a) Sandbox efêmero por ciclo — filesystem descartado por design; (b) Git commit pré-patch antes de toda aplicação persistente + git reset para rollback. | Git Branch como mecanismo único unificado. Container efêmero já fornece snapshot de sandbox por design. |
| "Multi-agent" como sinônimo de múltiplas chamadas LLM | V1, V2 e análises iniciais: proibição ampla. RED_TEAM: clarificou distinção. DOCKET: incorporou distinção | Proibição mal formulada pode impedir arquiteturas legítimas (planejamento + patch em dois LLM calls) | **Proibição canônica: agentes com autoridade autônoma de efeito (side-effects independentes).** Múltiplas chamadas LLM por ciclo (ex: planejamento + geração de patch) são permitidas e podem ser necessárias. | Proibição genérica de "múltiplas chamadas LLM". Aider usa múltiplos calls e não é "multi-agent" no sentido perigoso. |
| Confiança inflada no TypeScript+Zod como stack | V1: TypeScript c/ conf. 70 (tratado como pré-decidido). V2: conf. 55. RED_TEAM: conf. 35-40. DOCKET: não congela | Justificativa declarada é familiaridade com o legado — exatamente o sistema declarado arquiteturalmente letal. Primitives mais valiosas (DELTA) estão em Python | **Stack permanece formalmente aberta.** Experimento de 3 horas decide. Nenhum default TypeScript é assumido. | TypeScript como default implícito herdado do ORACLE-OS. |
| E2B como vendor com conf. 90 vs. interface abstrata | V1: E2B c/ conf. 90. V2 e RED_TEAM: vendor lock-in sem análise de custo (50ms-300ms cold start; custo por execução) | Escolha herdada do projeto legado sem análise técnica independente | **Propriedade congelada (microVM isolation); vendor formalmente aberto.** SandboxInterface com dois adaptadores decide. | E2B como binding arquitetural. A propriedade (isolamento kernel-level) está congelada; a implementação não. |

---

## 3. Decisões Canônicas Provisórias

| Tema | Formulação canônica | Classificação | Default provisório | Reavaliação necessária? |
|---|---|---|---|---|
| 1. Tese fundadora | FSM zero-based. LLM é coprocessador de proposta sem autoridade de efeito. | LEI PROVISÓRIA | FSM + LLM como proponente | Não |
| 2. Fonte da verdade | Dual-truth: Git para estado do código; event log para histórico de execuções. Comunicação por referência (hashes de commit). | LEI PROVISÓRIA | Dual-truth | Não |
| 3. Ledger do Dia 1 | JSONL append-only com 5 campos + hash SHA-256 simples. HMAC na Fase 3. SQLite quando query real exigir. | LEI PROVISÓRIA | JSONL + hash simples | Não (schema de 5 campos a formalizar na Fase 0) |
| 4. Snapshot / rollback | Dois mecanismos: (a) container efêmero por ciclo; (b) git commit pré-patch + git reset para repositório persistente. | LEI PROVISÓRIA | Container efêmero + git commit | Sim (medir latência de git reset antes de freeze) |
| 5. Modelo de mutação | Write-atomic: arquivo temp → rename atômico → verificação pós-escrita. Sem mutação parcial. | LEI PROVISÓRIA | Write-atomic total | Não |
| 6. Security boundary | Propriedade: isolamento kernel-level ou hypervisor-level. Vendor: aberto até experimento. SandboxInterface abstrata com ≥2 adaptadores. | LEI PROVISÓRIA (propriedade) / HIPÓTESE ABERTA (vendor) | SandboxInterface + adaptador Docker local | Sim (benchmarkar 2 vendors) |
| 7. Stack / linguagem | Linguagem única sem runtime híbrido. Ferramenta a decidir por experimento. `any` proibido em qualquer boundary. | OBRIGAÇÃO DE PROVA | Nenhum default — experimento decide | Sim (experimento stack-comparison de 3h) |
| 8. Contratos mínimos | Parse before effect. Schema estrito versionado em toda boundary LLM→runtime. `any` proibido. | LEI PROVISÓRIA (princípio) / HIPÓTESE ABERTA (ferramenta) | Ferramenta depende da stack | Não (princípio); sim (ferramenta depende do experimento 7) |
| 9. Budgets / retries / terminação | TerminationReason como tipo de primeira classe. Budget explícito por ciclo. FSM com estados absorventes. Sem while-true. | LEI PROVISÓRIA | Max iterations fixo + TerminationReason | Nunca |
| 10. Benchmark inicial | Pipeline completo (Intent→Parse→Validate→Snapshot→Apply→Verify→LedgerEntry) com LLM mockado em repositório toy. | LEI PROVISÓRIA | Mock-first benchmark | Não |
| 11. Sequência pré-Fase 1 | Tipos → FSM → Mock test → SandboxInterface → LLM real | LEI PROVISÓRIA | Sequência obrigatória ordenada | Não |
| 12. Proibido no começo | Lista negra com enforcement via CI: escrita no host, while-true, schema `any`, auto-modificação, agentes com efeito autônomo, LLM calls dentro de transições FSM, RAG/memória vetorial, decomposição de tarefas antes de 1 ciclo estável | LEI PROVISÓRIA | CI gate ativo | Após Fase 3 e loop auditável |

---

## 4. O Que Agora É Lei Provisória

Os seguintes itens passam a valer como referência oficial provisória do projeto. Não devem ser reabertos sem motivo técnico forte e justificativa falsificável:

1. **O LLM é coprocessador de proposta.** Jamais árbitro de efeito. Sua autoridade termina na saída estruturada tipada. Toda mutação é decidida pelo runtime determinístico.

2. **A unidade central é uma Execução de Intent governada por FSM.** Começa com intent normalizado. Termina em estado absorvente com TerminationReason explícito. É completamente rastreável via event log.

3. **Dual-truth é a arquitetura de verdade.** Git é a verdade do código. Event log é a verdade das execuções. Nenhum dos dois subsume o outro.

4. **Write-atomic é o único modelo de mutação.** Arquivo temporário → rename atômico (O_RENAME/POSIX) → verificação pós-escrita. Nenhuma mutação parcial tolerada.

5. **Schema enforcement na fronteira é axiomático.** Todo payload atravessando a boundary LLM→runtime é validado antes de qualquer efeito. Rejeição imediata em erro de schema. `any` é proibido.

6. **Budget explícito e TerminationReason são tipos de primeira classe.** Nenhum ciclo sem budget. Nenhuma transição FSM sem TerminationReason definido no mapa de estados. While-true é proibido arquiteturalmente.

7. **Event log append-only desde o Dia 1.** 5 campos mínimos: `id`, `ts`, `type`, `payload_hash` (SHA-256), `prev_id`. Hash simples (sha256 de prev_id + conteúdo) para tamper-detection. Sem HMAC antes da Fase 3.

8. **Snapshot antes de toda mutação persistente.** Git commit pré-patch no repositório persistente. Rollback = git reset --hard para hash conhecido. Container efêmero por ciclo para isola o filesystem de execução.

9. **Mock-first obrigatório.** O pipeline completo deve funcionar com LLM mockado (patch hardcoded) antes de qualquer chave de API LLM ser usada. Se não funcionar sem LLM, a fundação tem um buraco.

10. **Isolamento de execução é não-negociável (propriedade).** Todo código gerado por LLM executa em ambiente com separação de kernel do host. A propriedade está congelada; o vendor está aberto.

11. **Lista negra com enforcement via CI.** Não é governança documental. É gate técnico que falha no pipeline antes do merge.

12. **Sequência de Fase 0 é obrigatória e ordenada.** Tipos de primeira classe → FSM formalizada → Mock test → SandboxInterface → LLM real. Inversão de sequência garante refatoração massiva.

---

## 5. O Que Ainda Não É Lei

### Hipóteses Abertas

- **Dual-truth como implementação:** A propriedade dual-truth está congelada. O esquema exato de como o event log referencia os commit hashes do Git ainda é uma hipótese a formalizar na Fase 0.
- **Modelo de verdade para cenários de replay complexos:** Confirmação empírica de que `git checkout <hash>` resolve todos os cenários de reconstituição de estado sem necessidade de event log para estado de código.

### Obrigações de Prova

- **Stack/linguagem do núcleo:** TypeScript+Zod vs. Python+Pydantic. Experimento de 3 horas. Três critérios objetivos. Nenhum default antes do experimento.
- **Fornecedor de sandbox:** Latência e custo de dois adaptadores de SandboxInterface. Mínimo: Docker local + um provider cloud. Decisão baseada em dados medidos.
- **Portabilidade literal das primitives DELTA:** Custo em dias de engenharia para portar `audit.py` e `keyring.py` vs. reimplementar os padrões do zero na linguagem alvo. Decide se porta ou reimplementa.
- **Latência de git reset para repositório representativo:** < 2 segundos para repo de tamanho representativo (500 arquivos, 50MB). Medido em cronômetro.

### Escolhas Provisórias (não são lei, mas são o default de trabalho até o experimento)

- JSONL como storage do event log no Dia 1 (pode mudar para SQLite se query real exigir).
- Adaptador Docker local como implementação padrão de SandboxInterface durante desenvolvimento.
- 5 campos mínimos do LedgerEntry como schema operacional até formalização na Fase 0.

### Itens Adiados Deliberadamente

- HMAC chaining → Fase 3.
- SQLite como storage do event log → quando query real exigir indexação.
- Schema detalhado dos eventos além dos 5 campos mínimos → Fase 0 finalization.
- API pública do runtime (HTTP, CLI, SDK) → pós-loop mínimo funcional.
- Política de retenção do event log → pós-primeiro evento real.
- Decomposição de tarefas multi-step → métricas de Fase 2+ justificam.
- Multi-agent com autoridade de efeito → pós-loop auditável (Fase 3+).
- RAG / memória vetorial / indexação semântica → Fase 5+.

---

## 6. Revisão Tema por Tema

---

### Tema 1 — Tese Fundadora

**Estado atual do debate:** Consolidado. Convergência de 100% dos documentos (8/8).

**Formulação canônica provisória:** O sistema sucessor é uma Máquina de Estados Finita zero-based. O LLM é um coprocessador heurístico que produz propostas tipadas (structured output). O runtime determinístico é o único árbitro de efeitos no filesystem. Toda proposta do LLM passa por validação de schema antes de qualquer transição de estado com efeito físico.

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** FSM com estados absorventes, LLM propondo, runtime decidindo.

**O que foi rejeitado:** Qualquer arquitetura que coloque o LLM como tomador de decisão de efeito. LangGraph como runtime core. "Agente OS" com múltiplos papéis autônomos antes do loop mínimo auditável.

**Justificativa de arbitragem:** Convergência de 8/8 documentos. Evidência externa independente (Aider, SWE-agent, Devin architecture, padrão Hybrid Deterministic-Agentic). Nenhuma alternativa tecnicamente defensável.

**Risco se errado:** Muito alto. Herdar arquitetura probabilística como base causa contaminação sistêmica irrecuperável.

**Trigger de reavaliação:** Evidência empírica publicada de sistema LLM-first com confiabilidade de produção superior a sistemas FSM-first para o mesmo domínio de mutação de código em repositórios reais.

---

### Tema 2 — Fonte da Verdade do Sistema

**Estado atual do debate:** Contradição resolvida. V1 (single-truth conf. 95) contradito por V2 (dual-truth conf. 65) e RED_TEAM (dual-truth conf. 82). DOCKET converge em dual-truth.

**Formulação canônica provisória:** Dual-truth explícita e separada. (a) **Verdade do código:** repositório Git — append-only, content-addressed, criptograficamente íntegro por hash de commit. (b) **Verdade das execuções:** event log append-only — registra decisões, intenções, saídas de validação e eventos de rollback. Os dois sistemas comunicam exclusivamente por referência: entradas do event log referenciam hashes de commit Git. Git não substitui o event log; o event log não reconstrói o estado do código.

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** Git para código. JSONL append-only para execuções. Referência cruzada por commit hash.

**O que foi rejeitado:** Single-truth absoluto (ledger tenta reconstruir estado do código). O único cenário que single-truth resolve e dual-truth não resolve — reconstituição de estado de código a partir de log de eventos — é computacionalmente mais caro do que `git checkout <hash>` e não foi identificado como necessário por nenhum dos documentos.

**Justificativa de arbitragem:** Git é um sistema de event sourcing para código. `git log` é o event log. Commit hash é o ledger entry content-addressed. GitOps (Argo CD, Flux) é produção em escala do modelo dual-truth. Construir um segundo sistema para subsumer o que Git já provê é overengineering demonstrável.

**Risco se errado:** Alto. Single-truth implementado como ledger único exige infraestrutura adicional custosa para algo que Git já resolve.

**Trigger de reavaliação:** Identificação de um cenário concreto de replay ou auditoria que `git checkout <hash>` não resolve e que o event log, por si só, resolve.

---

### Tema 3 — Ledger do Dia 1

**Estado atual do debate:** Contraditório (V1: SQLite+HMAC no Dia 1. RED_TEAM: JSONL simples suficiente para Fase 1-2. DOCKET: SQLite WAL como default mas HMAC adiado).

**Formulação canônica provisória:**

- **Storage do Dia 1:** JSONL append-only por execução. Sem SQLite antes de uma query real exigir indexação.
- **Integridade do Dia 1:** Hash SHA-256 simples de `(prev_id + conteúdo do evento)` em cada entrada. Tamper-detectable sem gerenciamento de chaves.
- **HMAC:** Fase 3. Só entra quando o sistema estiver em produção com múltiplos usuários e o modelo de ameaça de adulteração interna for especificado.
- **SQLite:** Entra quando uma query demonstrável contra o event log exigir indexação que scan linear JSONL não serve eficientemente.
- **Schema mínimo do evento (5 campos obrigatórios):** `id` (UUID), `ts` (ISO-8601), `type` (enum), `payload_hash` (SHA-256 do payload), `prev_id` (UUID do evento anterior na execução).

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** JSONL + hash SHA-256 simples + 5 campos + `snapshot_ref` (hash do git commit associado).

**O que foi rejeitado:** HMAC como requisito do Dia 1. SQLite como requisito do Dia 1. Nenhum documento especificou o modelo de ameaça que requer HMAC antes de produção multi-usuário. Volume de eventos em Fases 0-2 é baixo; JSONL scan < 1ms para < 10.000 entradas.

**Justificativa de arbitragem:** Máxima de engenharia: complexidade só entra quando a necessidade é demonstrada. HMAC exige keyring, rotação, recuperação. SQLite exige setup de schema, WAL mode, migrations. Nenhum dos dois é necessário para o loop mínimo funcional.

**Risco se errado:** Médio. Adotar HMAC prematuramente adiciona overhead evitável. Migrar de JSONL para SQLite é < 1 dia de trabalho quando necessário.

**Trigger de reavaliação:** Fase 3 (HMAC). Quando uma query específica exigir SQLite (SQLite).

---

### Tema 4 — Snapshot / Rollback do Dia 1

**Estado atual do debate:** Contradição resolvida. V1 conflacionou sandbox filesystem com repositório persistente. RED_TEAM separou os dois. DOCKET formalizou a separação.

**Formulação canônica provisória:**

- **Snapshot de sandbox** (filesystem durante execução): Container efêmero por ciclo de execução. O filesystem do container é descartado por design ao fim de cada ciclo. Nenhuma lógica adicional de snapshot necessária.
- **Snapshot de repositório** (persistência entre ciclos): `git commit` com referência `pre-patch-<execution-id>` antes de toda aplicação de patch ao branch persistente. Rollback = `git reset --hard <hash>`. Evento `ROLLBACK_TRIGGERED` registrado no event log com referência ao commit hash de pré-patch.

**Classificação:** LEI PROVISÓRIA (separação dos dois mecanismos). OBRIGAÇÃO DE PROVA (latência do git reset medida antes de freeze definitivo).

**Default operacional provisório:** Container Docker efêmero + git commit pré-patch.

**O que foi rejeitado:** Git Branch por execução como mecanismo unificado. COW antes de experimento que comprove vantagem de latência.

**Justificativa de arbitragem:** Dois problemas distintos requerem dois mecanismos distintos. Container efêmero já provê snapshot de sandbox gratuitamente. Git commit já provê snapshot de repositório com zero infraestrutura adicional e rollback em uma linha de comando.

**Risco se errado:** Alto. Rollback incorreto é a segunda causa de falha mais grave depois da ausência de sandbox.

**Trigger de reavaliação:** Latência de `git reset` > 2 segundos para repositório representativo → avaliar COW ou alternativa.

---

### Tema 5 — Modelo de Mutação

**Estado atual do debate:** Sólido. Convergência 8/8 documentos.

**Formulação canônica provisória:** Write-atomic obrigatório. Sequência: (1) validação de schema do patch, (2) criação de ponto de restauração (git commit pré-patch), (3) escrita em arquivo temporário no sandbox, (4) rename atômico (syscall O_RENAME/POSIX), (5) verificação pós-escrita antes de registrar `PATCH_APPLIED`. Para patches em partes de arquivo: reescrita total do arquivo preferível a string-search replacement. Nenhuma mutação parcial tolerada.

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** Arquivo temp → rename atômico → verificação → ledger entry.

**O que foi rejeitado:** Diff-patching via string-search (degeneração silenciosa em patches múltiplos). Mutação direta sem arquivo temporário.

**Justificativa de arbitragem:** Padrão POSIX consolidado. Sem alternativa tecnicamente defensável para garantir que nenhum arquivo fique em estado parcialmente escrito.

**Risco se errado:** Alto. Mutação não-atômica pode deixar arquivos corrompidos mid-write com perda de dados irreversível.

**Trigger de reavaliação:** Arquivos de código > 100MB (improvável para source code normal).

---

### Tema 6 — Boundary de Segurança / Sandbox

**Estado atual do debate:** Sólido (propriedade). Contraditório resolvido (vendor).

**Formulação canônica provisória:**

- **Propriedade (congelada):** Toda execução de código gerado por LLM ocorre em ambiente com isolamento kernel-level ou hypervisor-level. Sem acesso ao filesystem do host fora do workspace designado. Sem acesso de rede exceto a endpoints explicitamente autorizados. Terminação após timeout configurável. Esta propriedade é não-negociável e não depende de vendor.
- **Interface (congelada):** `SandboxInterface` com métodos `create(spec)`, `exec(handle, cmd)`, `copy_in(handle, path, content)`, `copy_out(handle, path)`, `destroy(handle)`. A arquitetura se vincula à interface, não à implementação.
- **Vendor (aberto):** Decidido após experimento de benchmark com ≥ 2 adaptadores. Adaptador Docker local é o default para desenvolvimento. Adaptador cloud é obrigação de prova.

**Classificação:** LEI PROVISÓRIA (propriedade + interface). OBRIGAÇÃO DE PROVA (vendor/implementação).

**Default operacional provisório:** Docker local para desenvolvimento. Vendor cloud a definir por benchmark antes da Fase 1.

**O que foi rejeitado:** E2B como binding arquitetural sem análise de latência e custo. Binding pre-experimento a qualquer vendor específico.

**Justificativa de arbitragem:** A propriedade de isolamento (kernel-level) é não-negociável e independe de vendor. O vendor E2B foi herdado do projeto legado sem análise de custo (50ms-300ms cold start; custo por sandbox-segundo em produção). A decisão de vendor é operacional, não arquitetural, e requer dados medidos.

**Risco se errado:** Muito alto (sem isolamento). Médio (vendor errado → vendor lock-in ou latência incompatível com throughput).

**Trigger de reavaliação:** Mudança de pricing do fornecedor escolhido ou deterioração de SLA.

---

### Tema 7 — Stack / Linguagem do Núcleo

**Estado atual do debate:** Formalmente aberto. V1 tratava TypeScript como pré-decidido (conf. 70) com justificativa de familiaridade com o legado. RED_TEAM reduz para conf. 35-40. DOCKET formaliza como PROVE BEFORE FREEZE.

**Formulação canônica provisória:** A linguagem do núcleo é decidida por experimento de 3 horas antes da Fase 0. Nenhum default TypeScript é assumido. Nenhum default Python é assumido. O princípio está congelado: linguagem única no runtime core, schema enforcement estrito, `any` proibido em qualquer boundary. A ferramenta específica (Zod vs. Pydantic) depende da linguagem escolhida.

**Classificação:** OBRIGAÇÃO DE PROVA

**Default operacional provisório:** Nenhum. Experimento decide.

**O que foi rejeitado:** TypeScript como herança implícita do ORACLE-OS (justificativa: "familiaridade" com o sistema declarado arquiteturalmente letal é a pior justificativa possível). Python sem experimento comparativo.

**Justificativa de arbitragem:** A única justificativa para TypeScript nos documentos é familiaridade com o legado. Isso não é uma justificativa técnica — é um viés de continuidade com o sistema que este projeto declara abandonar. Python tem vantagem técnica demonstrável no ecossistema LLM (instructor, pydantic-ai, outlines, litellm). As primitives mais valiosas (DELTA_v102) estão em Python. O custo do experimento é 3 horas. O custo de escolher errado e descobrir na Fase 3 é semanas de refatoração.

**Risco se errado:** Médio. Friction acumulada por linguagem errada = refatoração cara em Fase 3+. Não fatal, mas evitável.

**Trigger de reavaliação:** Resultado do experimento stack-comparison. Irreversível após Fase 0.

---

### Tema 8 — Contratos Mínimos

**Estado atual do debate:** Sólido (princípio). Dependente (ferramenta).

**Formulação canônica provisória:** Parse before effect. Todo payload que atravessa a fronteira LLM→runtime é validado contra schema versionado com tipos estritos antes de qualquer efeito. Rejeição imediata e registro de `VALIDATION_FAILED` no event log em caso de falha de schema. `any`, `unknown` e campos opcionais não-tipados são proibidos em boundaries críticas. A ferramenta específica (Zod vs. Pydantic) depende da decisão de stack.

**Classificação:** LEI PROVISÓRIA (princípio). HIPÓTESE ABERTA (ferramenta — depende do experimento de stack).

**Default operacional provisório:** Princípio ativo desde o Dia 1. Ferramenta decidida pelo experimento do Tema 7.

**O que foi rejeitado:** Parsing tolerante a lixo. Schema frouxo. Validação pós-efeito. Campos `any` em qualquer boundary que aceita output do LLM.

**Justificativa de arbitragem:** Convergência de 8/8 documentos. Validado pelo padrão Schema-First Contract Enforcement da indústria. Sem schema enforcement estrito, o LLM pode injetar payloads malformados diretamente no motor de mutação.

**Risco se errado:** Alto. Classes inteiras de erros lógicos tornam-se indetectáveis na boundary.

**Trigger de reavaliação:** Nunca (princípio). Após experimento de stack (ferramenta).

---

### Tema 9 — Budgets / Retries / Termination Policy

**Estado atual do debate:** Sólido. Convergência 8/8 documentos.

**Formulação canônica provisória:** `TerminationReason` é um tipo de primeira classe com valores enumerados: `SUCCESS`, `FAILED_SAFE`, `POLICY_BLOCK`, `BUDGET_EXHAUSTED`, `UNVERIFIABLE`. Nenhum ciclo de execução sem budget explícito de: iterações máximas, chamadas LLM máximas, e timeout total. A FSM só aceita transições válidas. Estado absorvente é obrigatório. Sem estados sem saída. Cada tentativa de retry é um `LedgerEntry` registrado.

**Classificação:** LEI PROVISÓRIA. Axiomático.

**Default operacional provisório:** Max iterations fixo. TerminationReason registrado em todo encerramento de ciclo.

**O que foi rejeitado:** While-true architecture. Loops heurísticos sem budget. Terminação implícita sem razão registrada.

**Justificativa de arbitragem:** Anti-padrão while-true é universalmente documentado em literatura de workflow (Temporal.io, AgentOps). Sistemas sem termination policy explícita esgotam recursos de forma não recuperável.

**Risco se errado:** Muito alto. Loop infinito = colapso operacional do sistema.

**Trigger de reavaliação:** Nunca. Princípio axiomático.

---

### Tema 10 — Benchmark Inicial do Loop Mínimo

**Estado atual do debate:** Sólido. Convergência de alta intensidade nos documentos.

**Formulação canônica provisória:** Critério de sucesso da Fase 1: o pipeline completo `Intent → Parse → Validate → Snapshot → Apply → Verify → LedgerEntry` executa com sucesso em repositório toy simples usando LLM **mockado** (patch hardcoded). Inclui: (a) rollback simulado com verificação de integridade pós-rollback; (b) evento `ROLLBACK_TRIGGERED` no ledger; (c) ciclo com sucesso com `PATCH_APPLIED` e `LedgerEntry` verificável; (d) latência do ciclo completo documentada. Se o pipeline não funciona sem LLM, a fundação tem um buraco estrutural.

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** Mock com patch hardcoded. Sem LLM real até o mock passar.

**O que foi rejeitado:** Benchmark que exige LLM real para validar a arquitetura. Benchmark mais complexo que esconde falhas na fundação.

**Justificativa de arbitragem:** Alta convergência interna. Evidência externa (Aider, SWE-bench). Mock-first é separação de concerns aplicada à arquitetura. A fundação deve ser testável independentemente do componente probabilístico.

**Risco se errado:** Alto. Benchmark que exige LLM esconde falhas estruturais descobertas apenas em produção.

**Trigger de reavaliação:** Nunca para a Fase 1. Benchmarks mais ricos entram em Fase 2+.

---

### Tema 11 — Gate de Entrada da Fase 0

Ver Seção 8.

---

### Tema 12 — Gate de Liberação da Fase 1

Ver Seção 9.

---

### Tema 13 — Programa Mínimo de Experimentos

Ver Seção 10.

---

### Tema 14 — O Que Está Proibido no Começo

**Estado atual do debate:** Sólido (lista). Contradição resolvida (definição de "multi-agent").

**Formulação canônica provisória:** Lista negra com enforcement via CI gate (falha o pipeline antes do merge):

| # | Proibição | Severidade |
|---|---|---|
| 1 | Qualquer escrita no filesystem do host fora do sandbox | 10 |
| 2 | Qualquer ciclo de execução sem `TerminationReason` explícito | 10 |
| 3 | Qualquer schema `any` ou `unknown` em boundary que aceita output do LLM | 9 |
| 4 | Qualquer auto-modificação do código do runtime durante operação | 9 |
| 5 | Agentes com autoridade de efeito autônomo e independente (≠ múltiplas chamadas LLM por ciclo) | 8 |
| 6 | Chamadas LLM dentro de transições da FSM (LLM calls são activities, não transitions) | 8 |
| 7 | RAG, memória vetorial, indexação semântica | FORBIDDEN EARLY |
| 8 | Decomposição de tarefas antes de 1 ciclo completo ser estável e auditável | FORBIDDEN EARLY |
| 9 | Integração com LLM real antes do mock test passar | FORBIDDEN EARLY |

**Esclarecimento canônico:** "Multi-agent" na proibição #5 refere-se a agentes com autoridade autônoma de efeito (side-effects independentes), **não** a múltiplas chamadas LLM por ciclo. Um ciclo com chamada de planejamento + chamada de geração de patch **não é** "multi-agent" no sentido proibido.

**Classificação:** LEI PROVISÓRIA

**Default operacional provisório:** CI gate implementado antes da Fase 0.

**Justificativa de arbitragem:** Lista negra sem enforcement via CI é governança cosmética — a anti-lição central de bautt-sigma-up. O enforcement deve ser técnico, não documental.

**Risco se errado:** Muito alto. Cada item desta lista foi derivado de uma falha catastrófica documentada em sistemas reais.

**Trigger de reavaliação:** Após Fase 3 e loop auditável estável.

---

## 7. Decisões que Exigem Experimento Antes de Freeze

| Tema | Hipótese em disputa | Experimento mínimo | Critério de sucesso | Critério de falha | Quando executar |
|---|---|---|---|---|---|
| Stack / linguagem | Python+Pydantic é tecnicamente superior a TypeScript+Zod para este runtime | Implementar `LedgerEntry` schema validation + structured LLM output parsing nas duas stacks | Uma stack vence em ≥ 2 de 3 critérios objetivos (LOC, LLM ecosystem maturity, portabilidade primitives DELTA) | Nenhuma vantagem clara → Python por portabilidade de primitives | Antes da Fase 0 (máx. 3h) |
| Sandbox vendor | SandboxInterface com 2 adaptadores pode ser implementada em 1 dia, eliminando vendor lock-in | Definir SandboxInterface; implementar adaptador Docker local + adaptador cloud; benchmarkar create+exec+destroy | Ambos funcionando; diferença de latência medida e documentada; decisão de vendor baseada em dados | Apenas 1 adaptador (lock-in implícito); latência incompatível com throughput mínimo | Antes da Fase 1 (máx. 1 dia) |
| Latência git reset (snapshot repositório) | `git reset --hard <hash>` em < 2 segundos para repositório representativo | Medir latência de git reset para repo de 500 arquivos / 50MB | Rollback < 2s; zero corrupção detectável após rollback | Latência > 2s → avaliar alternativas (COW, outro mecanismo) | Antes da Fase 1 (máx. 2h) |
| JSONL vs. SQLite | JSONL scan linear é suficiente para todas as queries necessárias em Fase 0-2 | Enumerar todas as queries que o sistema precisará executar contra o event log nas Fases 0-2; avaliar se scan linear < 10ms as serve | Todas as queries em Fase 0-2 servidas por scan linear < 10ms | Alguma query requer ordenação ou filtragem que SQLite otimiza materialmente | Antes da Fase 1 |
| Portabilidade das primitives DELTA | Portar `audit.py` e lógica de atomic write custa < 2 dias de engenharia na linguagem alvo | Estimar LOC + testes de correção para portar as primitives na linguagem alvo | Port < 2 dias sem testes de correção adicionais | Port > 3 dias ou introduz domain pollution → reimplementar padrão do zero | Antes da Fase 0 finalization |

---

## 8. Gate Canônico de Entrada da Fase 0

Nenhum código de produção antes desta lista estar completa. A ordem é obrigatória:

**Experimentos obrigatórios (pré-Fase 0):**
- [ ] Experimento stack-comparison concluído e decisão documentada
- [ ] Estimativa de portabilidade das primitives DELTA concluída
- [ ] Modelo de ameaça formalizado (documento de 1 página: quais ameaças o sistema defende no Dia 1)

**Artefatos obrigatórios (pré-início da implementação da Fase 0):**
- [ ] Decisão de stack (linguagem + ferramenta de schema) documentada e irrevogável para a Fase 0
- [ ] Tipos de primeira classe formalizados: `Intent`, `LedgerEntry`, `FileChange`, `TerminationReason`, `PolicyViolation`, `SnapshotReference`, `RetryBudget`, `ExecutionResult`
- [ ] FSM formalizada: diagrama de estados e transições com pré-condições explícitas
- [ ] `SandboxInterface` definida (não necessariamente implementada com 2 adaptadores)
- [ ] Schema mínimo do LedgerEntry definido (5 campos obrigatórios documentados)
- [ ] Lista negra de proibições implementada como CI gate (não apenas documentada)

**O que pode continuar em aberto durante a Fase 0:**
- Vendor/implementação específica de sandbox
- Schema detalhado dos eventos além dos 5 campos mínimos
- HMAC chaining (adiado para Fase 3)
- Mecanismo exato de snapshot de código (a definir com base na decisão de sandbox)
- API pública do runtime

**Proibido entrar na Fase 0:**
- Multi-agent com autoridade de efeito
- RAG, memória vetorial
- Self-evolution ou auto-modificação do runtime
- Integração com LLM real antes do mock test passar
- Qualquer módulo que não seja: tipos, FSM, schema validation, estrutura de projeto, CI gates

---

## 9. Gate Canônico de Liberação da Fase 1

Para a Fase 1 começar, os seguintes critérios devem ser **provados, não declarados**:

**Prova do mock loop (gate principal):**
- [ ] Pipeline completo `Intent → Parse → Validate → Snapshot → Apply → Verify → LedgerEntry` executa com LLM **mockado** (patch hardcoded) em repositório toy simples
- [ ] Latência do ciclo completo (sem LLM real) documentada e considerada aceitável

**Prova de rollback:**
- [ ] Após falha simulada de verificação pós-patch: sistema retorna exatamente ao estado pré-patch via `git reset --hard <hash>`
- [ ] Zero corrupção detectável após rollback
- [ ] Evento `ROLLBACK_TRIGGERED` presente no event log com referência ao snapshot de pré-patch

**Prova de termination discipline:**
- [ ] FSM entra em estado absorvente dentro do budget em todos os cenários de teste
- [ ] Nenhum ciclo sem `TerminationReason` explícito registrado no log
- [ ] Tentativa artificial de loop infinito é interceptada e encerra em `BUDGET_EXHAUSTED`

**Prova de schema boundary:**
- [ ] Payload inválido é rejeitado antes de qualquer efeito
- [ ] Rejeição registrada como `VALIDATION_FAILED` no event log
- [ ] Nenhum payload não-validado atingiu o motor de mutação nos testes

**Prova de safe mutation path:**
- [ ] Todos os arquivos mutados usaram padrão temp-file + rename atômico
- [ ] Verificação pós-write confirma integridade do arquivo antes de `PATCH_APPLIED`

**Prova de dual-truth:**
- [ ] Git commit hash de pré-patch referenciado em toda entrada de ledger que envolve mutação
- [ ] Estado do repositório recuperável via `git checkout <hash>` sem dependência do event log para estado de código

**Prova de sandbox benchmark:**
- [ ] Experimento sandbox-abstraction concluído com 2 adaptadores e latência documentada
- [ ] Decisão de vendor documentada antes de qualquer código de Fase 1 ser escrito

---

## 10. Programa Canônico Mínimo de Experimentos

Cinco experimentos. Cada um fecha uma dúvida crítica. Duração máxima indicada:

**Experimento 1 — stack-comparison (3h)**
- Objetivo: Decidir linguagem do core com critérios técnicos, não familiارidade com legado.
- Artefato: Dois snippets de `LedgerEntry` schema validation + structured LLM output parsing. Tabela comparativa: LOC, LLM ecosystem maturity, portabilidade primitives DELTA.
- Decide: Linguagem do núcleo — irreversível após Fase 0.

**Experimento 2 — delta-portability (2h)**
- Objetivo: Quantificar custo de portabilidade das primitives DELTA.
- Artefato: Estimativa de LOC e testes de correção para portar `audit.py` e lógica de atomic write na linguagem alvo.
- Decide: Portar código vs. reimplementar padrões do zero.

**Experimento 3 — sandbox-abstraction (1 dia)**
- Objetivo: Definir SandboxInterface e benchmarkar 2 implementações.
- Artefato: SandboxInterface definida. 2 adaptadores funcionando. Tabela de latência (create+exec+destroy) por adaptador.
- Decide: Vendor padrão de sandbox. Confirma que a interface é suficientemente abstrata.

**Experimento 4 — snapshot-model (2h)**
- Objetivo: Medir latência de git reset e confirmar separação sandbox/repositório.
- Artefato: Medição de latência de `git reset --hard` para repo representativo. Confirmação de zero corrupção após rollback.
- Decide: Mecanismo de snapshot de repositório. Valida (ou invalida) git commit como mecanismo standard.

**Experimento 5 — mutation-path / mock-first benchmark (1 dia)**
- Objetivo: Executar o ciclo completo com mock LLM. Gate para Phase 1.
- Artefato: Script executável com ciclo completo (1) intent hardcoded → (2) patch mockado → (3) schema validation → (4) git commit pré-patch → (5) write-atomic → (6) verificação → (7) LedgerEntry → (8) rollback simulado.
- Decide: Confirma que a fundação é correta antes de integrar LLM real. **Este é o gate absoluto para a Fase 1.**

---

## 11. Caminho Canônico Até o Início da Construção

**Passo 1 — Experimentos de stack e portabilidade (5h)**
- Objetivo: Fechar a linguagem do core e quantificar portabilidade do DELTA.
- Artefato esperado: Decisão de linguagem documentada + estimativa de portabilidade.
- O que destrava: Definição dos tipos de primeira classe na linguagem certa.
- O que ainda não destrava: Implementação da Fase 0.

**Passo 2 — Modelo de ameaça (2h)**
- Objetivo: Documento de 1 página especificando quais ameaças o sistema defende no Dia 1.
- Artefato esperado: Documento de ameaça formal.
- O que destrava: Decisão definitiva de hash simples vs. HMAC no Dia 1 (confirmada em hash simples se ameaça principal é hallucination LLM ou bug honesto).
- O que ainda não destrava: Vendor de sandbox.

**Passo 3 — Tipos de primeira classe e FSM (6h)**
- Objetivo: Formalizar `Intent`, `LedgerEntry`, `FileChange`, `TerminationReason`, `PolicyViolation`, `SnapshotReference`, `RetryBudget`, `ExecutionResult`. Diagrama de estados da FSM com transições e pré-condições.
- Artefato esperado: Arquivo de tipos + diagrama de FSM.
- O que destrava: Gate de entrada da Fase 0.
- O que ainda não destrava: Integração com LLM real.

**Passo 4 — CI gates e SandboxInterface (4h)**
- Objetivo: Script de CI gate para lista negra de proibições. Definição formal de `SandboxInterface`.
- Artefato esperado: CI gate ativo + interface definida.
- O que destrava: Início da implementação da Fase 0.
- O que ainda não destrava: Fase 1.

**→ ENTRADA NA FASE 0** (após Passos 1-4)

**Passo 5 — Implementação da Fase 0: pacote core-model (1 semana)**
- Objetivo: Tipos de primeira classe com invariantes e testes unitários in-memory. Schema do event log. Hash chain simples.
- Artefato esperado: Pacote `core-model` com 100% de cobertura de tipos via mocks.
- O que destrava: Experimento mutation-path.
- O que ainda não destrava: Fase 1 com LLM real.

**Passo 6 — Experimento sandbox-abstraction (1 dia)**
- Objetivo: SandboxInterface + 2 adaptadores + benchmark de latência + decisão de vendor.
- Artefato esperado: Dois adaptadores funcionando. Tabela de latência. Decisão de vendor documentada.
- O que destrava: Integração do sandbox no ciclo completo.
- O que ainda não destrava: LLM real.

**Passo 7 — Experimento snapshot-model (2h)**
- Objetivo: Medir latência de git reset. Confirmar separação sandbox/repositório.
- Artefato esperado: Medição de latência. Confirmação de zero corrupção.
- O que destrava: Gate de Fase 1 (prova de rollback).
- O que ainda não destrava: LLM real.

**Passo 8 — Experimento mutation-path / mock-first benchmark (1 dia)**
- Objetivo: Ciclo completo com LLM mockado incluindo rollback.
- Artefato esperado: Script executável + log estruturado de todo o ciclo + evidência de rollback limpo.
- O que destrava: **Gate absoluto para a Fase 1.**
- O que ainda não destrava: Complexidade adicional.

**→ LIBERAÇÃO DA FASE 1** (após Passo 8 com mock test passando)

**Passo 9 — Integração do LLM real (Fase 1)**
- Objetivo: Um modelo, uma chamada de planejamento + patch, schema estrito, budget explícito.
- Artefato esperado: Ciclo completo com LLM real em repositório toy.
- O que destrava: Iteração sobre qualidade dos outputs.
- O que ainda não destrava: Decomposição de tarefas, multi-agent, RAG.

---

## 12. Glossário Normativo de Classificações

**Lei Provisória**
Uma decisão suficientemente fundamentada por convergência de evidências (internas e externas) para ser tratada como referência operacional do projeto. Não deve ser reaberta sem motivo técnico forte e justificativa falsificável. Pode ser revisada se a evidência mudar materialmente. Não é dogma permanente — é o melhor estado atual do conhecimento.

**Hipótese Aberta**
Uma questão que não foi suficientemente provada para ser congelada. Está identificada, tem formulações candidatas em competição, mas requer experimento ou decisão formal antes de virar Lei Provisória. Trabalhar como se fosse lei antes de ser provada é um erro de processo.

**Obrigação de Prova**
Uma decisão que deve ser fechada por experimento mensurável antes de um gate específico. Tem critério de sucesso e critério de falha definidos. Bloqueia o avanço para o próximo gate até ser executada. Não é opcional.

**Adiado Deliberadamente**
Um tema que foi avaliado, reconhecido como relevante no longo prazo, e conscientemente excluído do escopo atual porque introduziria complexidade antes de sua necessidade ser demonstrada. Não é "esquecido" — é postergado com justificativa. Reabertura requer evidência de que a fase atual o torna necessário.

**Proibido no Começo**
Um padrão ou componente que está ativamente proibido de entrar no projeto antes de um gate específico, com enforcement técnico (CI gate), não apenas documental. A proibição tem severidade graduada. Violação bloqueia o merge.

**Default Operacional Provisório**
A implementação de trabalho atual para uma decisão que ainda não foi congelada. Pode ser alterado pelo resultado de um experimento sem causar refatoração significativa. É o que o time usa enquanto a Obrigação de Prova não foi executada.

**Trigger de Reavaliação**
A condição específica e mensurável que, se ocorrer, justifica reabrir uma Lei Provisória ou um Default Operacional. Sem trigger explícito, a reavaliação é arbitrária e cria instabilidade de governança. O trigger define quando a lei pode mudar, não por capricho ou preferência pessoal.

---

## 13. O Que Deve Parar de Acontecer Agora

Os seguintes comportamentos devem parar **imediatamente**:

1. **Produzir novos documentos fundadores sem obrigações de prova.** Este documento é o último manifesto permitido. O próximo artefato deve ser código ou resultado de experimento.

2. **Manter dois defaults concorrentes para o mesmo tema.** Cada tema tem exatamente uma formulação canônica. Documentos que apresentem alternativas sem decidir entre elas são hipóteses, não especificações.

3. **Chamar de "freeze" o que ainda é hipótese.** O V1 congelou TypeScript (conf. 70), E2B (conf. 90) e single-truth (conf. 95) sem evidência empírica. Confiança declarada sem experimento não é confiança real.

4. **Congelar vendor em vez de propriedade arquitetural.** A propriedade de isolamento está congelada. O vendor não está. A confusão entre os dois cria vendor lock-in arquitectural desnecessário.

5. **Conflacionar sandbox de execução com snapshot de repositório.** São dois problemas com dois mecanismos distintos. Tratá-los como um só produz designs incorretos e decisões de snapshot erradas.

6. **Usar "multi-agent" como sinônimo de "múltiplas chamadas LLM".** A proibição correta é: agentes com autoridade autônoma de efeito. Múltiplas chamadas LLM por ciclo são permitidas.

7. **Iniciar código de Fase 1 sem que o mock loop passe.** O loop deve funcionar com patch hardcoded antes de qualquer chave de API LLM ser usada.

8. **Sofisticar o ledger antes de validar o ciclo mínimo.** HMAC chaining, SQLite WAL, CQRS são Fase 3. O Dia 1 do ledger é um arquivo JSONL append-only com 5 campos e hash SHA-256 simples.

9. **Tratar documentos anteriores (V1, V2) como especificações técnicas.** O V1 é orientação filosófica correta e especificação técnica prematura. O V2 melhora o V1 mas herda parte de seus vieses. Esta lei provisória é o documento normativo vigente.

10. **Adiar o experimento stack-comparison por mais de 3 horas.** É 3 horas de trabalho que economiza semanas de refatoração. Adiar mais é procrastinação com custo crescente.

11. **Usar linguagem épica em documentos de decisão técnica.** Toda decisão deve ter critério de falsificação explícito. Sem falsificação, é manifesto, não especificação. Termos como "obliteração conceitual" e "disciplina militarizada" têm poder retórico e zero utilidade de governança.

12. **Fazer média entre os documentos anteriores.** O objetivo não é média — é arbitragem. Esta lei arbitrou. Onde os documentos divergiam, este Conselho decidiu.

---

## 14. Recomendação Final

### O que fazer — ordem obrigatória

**AGORA (próximas 8 horas):**
Execute os experimentos stack-comparison (3h) e delta-portability (2h). Escreva o modelo de ameaça (2h). Decida linguagem antes de qualquer outra ação. Não entre na Fase 0 em linguagem errada.

**ESTA SEMANA:**
Complete os Passos 1-4 do Caminho Canônico. Chegue em estado "Ready to start Phase 0". Formalize tipos, FSM, CI gates e SandboxInterface.

**FASE 0 (próxima semana):**
Implemente `core-model` com tipos e invariantes. JSONL event log simples. Hash chain SHA-256. Sem LLM real, sem chamadas API externas, sem sandbox (apenas interface definida).

**GATE PARA FASE 1:**
Mock test do ciclo completo (experimento mutation-path) deve passar. Se não passa, a fundação tem um buraco — descubra antes de integrar o LLM.

### O que não fazer

- Não começar a Fase 0 em TypeScript antes de executar o experimento stack-comparison.
- Não tratar nenhuma das decisões abertas como fechadas.
- Não construir HMAC antes de especificar o modelo de ameaça.
- Não construir RAG, memória vetorial ou decomposição de tarefas antes da Fase 3.
- Não usar o V1 como especificação técnica — usá-lo apenas como orientação filosófica.
- Não produzir outro documento fundador sem que o próximo artefato seja código executável.

### O que preservar dos documentos anteriores

- A tese FSM zero-based — correta e bem fundamentada.
- A lista de proibições iniciais — ampliada e formalizada neste documento.
- Os tipos de primeira classe nomeados — corretamente identificados.
- A sequência de fases — corretamente ordenada.
- O conceito de budget explícito e TerminationReason — axiomático.
- O mock-first benchmark — adicionado pelo V2 e confirmado pelo RED_TEAM.
- A distinção propriedade vs. vendor — adicionada pelo V2 e aprofundada pelo RED_TEAM.

---

## 15. Instrução Final do Fundador em Uma Frase

**Execute os experimentos antes de escrever a primeira linha de código de produção: a stack correta é escolhida em 3 horas de comparação técnica, o rollback é válido apenas quando medido em cronômetro, e o sistema só pode ser chamado de determinístico depois que o mock loop executar sem LLM e o pipeline completo de mutação, rollback e ledger funcionar com patch hardcoded em repositório toy — qualquer declaração de determinismo antes dessa prova é manifesto, não engenharia.**
