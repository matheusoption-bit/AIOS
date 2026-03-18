# Plano Canônico de Execução da Fase 0 — Versão Final

## 1. Veredito Executivo

A Fase 0 não é uma etapa de construção funcional; é uma etapa de **fundação estrutural e materialização de restrições**. O objetivo é declarar incontestavelmente os *Schemas* de dados imutáveis, provar a topologia da Máquina de Estados Finita (FSM) via testes locais (*mocks* agressivos), definir as trilhas de auditoria (Registro *Append-Only*) e isolar mecanicamente as interfaces de contenção de efeitos de I/O, antes da introdução de qualquer execução real originada por modelos de linguagem probabilísticos. 

Se, ao final da Fase 0, a fronteira e o isolamento não forem capazes de deter deterministicamente comandos nocivos submetidos por uma fonte simulada, o plano de transição para a Fase 1 estará vetado.

## 2. O Que Foi Preservado do Plano Original

- **Objetivo Central da Fase 0:** Estabelecer a barreira matemática que isola inferência (LLM) de mutação nativa de operações.
- **Abordagem Mock-First:** Testar exaustivamente falhas sistêmicas na orquestração com injeção falsa antes de depender da resposta gerada estocasticamente pelo modelo de IA.
- **Gate de Saída Rigoroso:** Obrigatoriedade de testes de unidade ponta a ponta que passem limpos na barreira sem quebrar, com compilação livre de *bypass* de tipos.
- **Anti-escopo Declarado:** Proibição de ferramentas externas prematuras, abstrações cognitivas (LangGraph) e adoção de agentes duplos na largada.

## 3. O Que Foi Corrigido na Revisão Final

| Ponto Corrigido | Problema no Plano Anterior | Correção Aplicada | Por Que Melhora o Plano |
| :--- | :--- | :--- | :--- |
| **Vendor de Sandbox Implícito** | O texto citava implicitamente E2B e containers instanciados como solução mandatória e rápida. | Alterado para focar na *interface abstrata e na propriedade de isolamento térmico*. E2B e Docker MicroVM viram *candidatos*, não *defaults*. | Evita lock-in indevido numa fase de validação basal, priorizando o desenho da fronteira. |
| **Experimento de Stack Limitado** | Reduzia o conflito TypeScript vs Python à simples velocidade de Parsing (Zod vs Pydantic). | O experimento foi largamente expandido para abarcar latência, segurança estrutural de Tipos, Maturidade das Ferramentas da Linguagem (ecossistema LLM) e Reuso do motor atual (DELTA).  | Protege contra escolhas de plataforma orientadas a *benchmark* em detrimento da ergonomia contínua de software. |
| **Mistura de Snapshot e Sandbox** | Aglutinava Sandbox Executivo (Isolamento de CPU/RAM/Host) com Snapshotting de Disco (Branch Git vs COW). | Separação explícita de subcamadas: O Isolamento previne injeção sistêmica no SO host; o Mecanismo de Reversão estoca as intenções puras manipuladas do arquivo antes do diff. | Torna a falha independente; Se o Snapshot falha, o SO não está comprometido. |
| **Ambiguidade de Latência/Tempos Falsos** | Suposições arbitrárias ("Teste de 1 hora", "latência cravada de 0.05 segundos"). | Substituídos por critérios de verificação e métricas baseadas em faixas plausíveis ou qualidades. | Elimina premissas utópicas inalcançáveis antes da materialização empírica em hardware. |
| **Excesso Retórico Normativo** | Uso hiperbólico de "Tolerância Matemática 100%", "Botão vermelho", "Engenheiro-Chefe burla regras". | Adaptação para jargão de Software Engineering sóbrio (Enforcement Estrito Interdisciplinar, Fail-Fast Padrão, Contraste Rigoroso de Continuidade). | Traz profissionalismo executivo, reduz a postura punitiva artificial, facilitando entendimento de equipes. |

## 4. Ajustes de Formulação Normativa

- O termo *“barreira matemática inquebrável”* foi suavizado e tornado verificável: *"Enforcement estrito de tipos estáticos em tempo de interpretação e compilação"*.
- Foram *desvendorizadas* proposições de Sandbox; o foco muda de E2B para *MicroVM-isolation compliance*.
- Foram desambiguados os *imports* proibidos; eles tornam-se "Inibidores de *Syscall* Nativas" implementados via regras abertas na AST pelo módulo de CI.
- Removidas métricas absolutas irreais, orientando latência ou precisão a *ordens de grandeza razoáveis aplicáveis a fluxos atômicos locais (ex.: sub-segundo overhead, sub-milissegundo para schema validation).*

## 5. Objetivo Oficial da Fase 0

Projetar e validar exaustivamente a topologia determinística imutável do Runtime (Schemas de Comunicação, Auditoria Ledger-Event e Protocolos FSM) via Mocks, sem a introdução de chamadas a modelos fundacionais (LLM). Isso garante o desenvolvimento do mecanismo limitador, isolador e atômico (FSM, Snapshot, Sandbox e Ledger) independente da variação da criatividade generativa.

## 6. Estrutura da Fase 0

A fase é desenhada estrategicamente em 4 pilares:
1. **Decisão Basal de Stack:** Avaliar Python + Pydantic v2 VS TypeScript + Zod.
2. **Definição dos Tipos Fundamentais:** Congelamento total da ontologia do sistema.
3. **Isolamento de Operações Externas (Limites e Contenções):** Interfaceamento dos provedores de Execução, Log de Operações e Volatilidade FS.
4. **Ciclo Verificador (Mock-Run):** Provar a engrenagem (FSM) de fim-a-fim puramente com estruturas simuladas programadas.

## 7. Plano de Execução Sequencial

1. **Kick-off do Experimento de Stack:** Medir rigidez de parsing documental, adequações aos toolings da linguagem corrente, custo logístico de integração e velocidade. Tomar a decisão executiva final do runtime principal. (Resultados na seção 9).
2. **Linter de Base System Boundary:** Institucionalizar via CI/CD que *sub-shells* não encapsulados (e equivalentes de SO aberto) encerrem o build com erro fatal de violação.
3. **Escrita Ininterrupta dos Schemas Finais:** Definir os artefatos `Intent`, `Log_Event`, e `Termination_Proof` nas classes literais orientadas a falha, bloqueando extensões dinâmicas soltas (No `any` or `object` types na camada basal de recepção).
4. **Sintaxe da Máquina de Estados:** Construir a gramática procedimental local (*Loop de Roteamento Estrito*). Todo o FSM recebe Input Validado e termina em estados absolutos.
5. **Assinatura das Interfaces Reversivas (Interfaces):** Construir as abstrações de `ISandbox_Environment`, `ISystem_Snapshot` e `IAppendOnly_Ledger`.
6. **Bateria Pura de Stress de Mocks:** Escapar propositalmente lixos, arrays infindáveis, nulos nas interfaces para depurar a tolerância da barreira e afirmar que a gravação do Log de Rejeição funciona adequadamente antes da introdução da máquina real.

## 8. Artefatos Obrigatórios da Fase 0

| Arquivo/Artefato | Condição de Operacionalidade | Responsabilidade Prática |
| :--- | :--- | :--- |
| `types/core` | Obrigatório / Tipagem Estrita | A única fonte da verdade para contratos DTO transportáveis do FSM. |
| `fsm/engine` | Obrigatório / Pureza de I-O | Controlar unicamente a mecânica processual sem embutir bibliotecas geradoras. |
| `interfaces/boundaries` | Obrigatório / DI Pattern | Desacoplar Snapshot, Sandbox e Ledger de provedores diretos, travando *Vendor Lock-In*. |
| `mocks/adversarial` | Obrigatório / Teste Funcional | Fornecer baterias de testes tóxicos programados de intenções. |
| Regras de Compilação Estrita (`eslint`, `mypy`) | Obrigatório / Proteção Automática | Falhar processos em pipelines caso programadores incluam atalhos para host/OS no *core* da framework. |

## 9. Programa Mínimo de Experimentos da Fase 0

Todo experimento desta fase serve primariamente para destravar decisões essenciais.

**Experimento 1: Bateria Completa de Avaliação da Stack de Código Principal**
*Critério:* O ecossistema LLM atual e a primitividade de código do pacote legado do repositório DELTA requerem avaliação objetiva e estrita da tipagem real (Python vs TypeScript) além do simples JSON estrito.
- Testar rigidez de Validação: Emular estruturas aninhadas complexas.
- Testar viabilidade de re-implementação (migração de módulos úteis Python-Delta).
- Avaliar maturidade do Tooling LLM associado à linguagem candidata no momento presente. 
*Decisão: Congela de fato a linguagem nativa principal de base.*

**Experimento 2: Prova de Carga Relativa de Instanciação do Snapshot vs Branching**
*Critério:* Mensurar e comparar abordagens (COW vs Git local branching) para uma reversão atômica de árvore nativa perante um repositório super-povoados de dependências (`node_modules` massivo).
- Avaliar o custo de *setup* em ordem de grandeza O(n) visível das vias eleitas.
*Decisão: Estipula a interface exata do `ISystem_Snapshot` que acompanhará o Day-1.*

**Experimento 3: Isolamento Estrito de MicroVM Interface Local**
*Critério:* Instanciar uma prova real de que as bibliotecas padrão não vazarão comandos para fora; testar prototipicamente *Firecracker, Docker isolado*, e a viabilidade do *E2B* para abstração na camada basal. O teste atesta as barreiras e descobre empiricamente qual candidato local tem *overhead* prático compatível com um ciclo O(1) fluído, mas sem que a arquitetura *dependa* dele.

## 10. O Que Não Entra na Fase 0 (Anti-Escopo Executivo)

- Automações de APIs de provedores reais de Large Language Models.
- Conexões de persistência relacional maciças rodando DBs em instâncias contêineres acopladas. (Use armazenamento local assinado leve inicialmente).
- Subrotinas multi-agente, Prompts Dinâmicos estruturados analíticos, ou qualquer tipo de simulação semântica conversacional de inteligência inter-papéis.

## 11. Riscos da Fase 0

- **Fuga do Loop Estacionário:** Injetar LLM antes que os *mocks* provem integridade atômica da falha na barreira de FSM causará falsa sensação de resolução.
- **Micro-Otimização Prematura de Ferramental:** Paralisar semanas tentando escolher entre Pydantic V2 e Zod por milissegundos pontuais ou métricas infladas, ao invés de atestar o ecosistema mais sustentável globalmente para o desenvolvimento do core em um horizonte temporal alongado.
- **Integração Ad-Hoc Impaciente:** Escrever pontes diretas imperativas pro FileSystem sem as portas abstratas (quebrar a obrigatoriedade da porta virtual `ISandbox_Environment`), arruinando testes de sistema local futuros. 

## 12. Gate de Saída da Fase 0

O sistema transita em prontidão da Fase 0 se, e somente se, todos os itens abaixo forem aprovados por auditoria contínua de Integração:
- Decisão de stack de linguagem primária fundamentada perante ecossistema robusto.
- Todos os *Schemas Fundamentais de Comunicação da FSM* definidos de modo exato (tipagem extrema) no núcleo da Base de Código.
- Um ciclo autômato puro `intent -> reject` ou `intent -> done` com logs atômicos gerados, usando inputs sintéticos predeterminados, rodando consistentemente sem requerer IO imprevisível.
- Configuração de Lint/Compiler bloqueando importações imperativas livres e banindo tipos arbitrários `Object`/`Any` no limiar da FSM de contratos. 

## 13. Gate de Entrada da Fase 1

Asseverado o estado "Done" da Saída da F0, a Fase 1 inicia detendo formalmente o ecossistema fechado de dados locais, interfaces puras, FSM estático testado e a prova da trilha gravada de modo irrevisável (*Immutable Execution Core*). Somente agora, abre-se a etapa onde as verdadeiras *cabeças* acopladas de Orquestração Inicial (LLM Copilot único) proverão os Inputs que movimentarão localmente as chaves da FSM.

## 14. Caminho Mínimo Seguro da Lei Provisória até a Fase 1

O Caminho Mínimo consiste num processo restrito orientado, essencialmente de Interfaces-first:
1. Comece pelas diretivas e pelo experimento de Linguagem/Stack. A fundação orienta as construções subseqüentes. 
2. Redija *Contracts* e as assinaturas essenciais de Interface sem corpos atrelados a SDKs fechadas.
3. Elabore a lógica transitiva contínua estática da engine FSM de Mock, amarrando tudo num repositório estático simples.
4. Quando o ciclo fechar em conformidade sem IA atestando seu *output*, formalize a mudança de fase.

## 15. Sugestão de Sequenciamento Temporal da Fase 0

- **Ciclo Um:** Benchmarks e Investigação Tecnológica do Experimento de Stack (Tipagem & Isolamentos primários provisórios avaliativos). Decisão tomada em tempo tático restrito.
- **Ciclo Dois:** Modelagem de Contratos Abstratos Universais Internos e *Interface Boundaries*. Fixação de FSM Local.
- **Ciclo Três:** Bateria de Validação Ponta a Ponta Falsa Intencionalmente Severa.

## 16. O Que Deve Parar Imediatamente para a Fase 0 Funcionar

- Transferências desenfreadas (*Ctrl+C / Ctrl+V*) de bibliotecas do repositório legatário ORACLE-OS na premissa de *“agilizar etapas irrelevantes e ganhar velocidade”*. Reutilize padrões intelectuais (Primitivos isolados verificáveis); despreze todo e qualquer acoplamento estrutural em nível de subsistemas orquestrais ou módulos inter-amarrados da rede antiga.

## 17. Recomendação Final

Execute estritamente segundo as lógicas formais limpas listadas. Remova sentimentos passados perante antigos fluxos operacionais e o fascínio com complexidades generativas. Prove que seu modelo detém o impacto mecânico, assegura a sua imutabilidade contenciosa em diário (Append-only Ledger) localmente, e rejeite toxicidades precoces da borda em testes determinísticos fechados antes de plugar as fontes estocásticas oniscientes de Inteligência externa. O código provê a Lei.

## 18. Instrução do Fundador em Uma Frase

**Tranque as portas da arquitetura construindo contratos impenetráveis, interfaces estritamente desacopladas e ciclos determinísticos testáveis rigorosamente antes de admitir qualquer inferência estocástica livre no ambiente de produção real; a solidez matemática isolada salvará o ecossistema do próprio colapso.**
