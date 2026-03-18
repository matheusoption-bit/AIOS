# Transição da Fase 0 para a Fase 1 — Lote 1

## 1. Veredito Executivo
A Fase 0 (Fundação) é formalmente encerrada como **APROVADA COM RESSALVAS**. O sistema sucessor possui agora um esqueleto mecânico e lógico funcional, orquestrado por uma FSM determinística e auditado por um Ledger imutável. No entanto, o isolamento real entre runtime e host permanece como uma lacuna de segurança que deve ser sanada antes de qualquer expansão de features.

## 2. O Que a Fase 0 Provou
- **FSM:** Máquina de estados determinística com tratamento explícito de erros e rollback.
- **Contratos:** Ontologia de `Intent` e `ExecutionResult` com tipagem rígida (Pydantic v2).
- **Ledger Mínimo:** Log de eventos append-only com encadeamento de hashes SHA-256.
- **Rollback:** Mecanismo atômico de reversão de estado físico baseado em Git.
- **Dual-Truth:** Modelo funcional onde Git é o código e Ledger é a execução.
- **Benchmark Mock-First:** Sucesso em 5 cenários críticos de fluxo lógico.
- **Abstração da Sandbox:** A `SandboxInterface` provou ser capaz de orquestrar múltiplos adaptadores sem vazamento de vendor.

## 3. O Que a Fase 0 Não Provou
- **Isolamento Forte Real:** O adaptador `Subprocess` não oferece barreira de segurança contra escapes.
- **Boundary Robusta Host/Runtime:** Superfície de ataque entre host e processos da sandbox não explorada.
- **Hardening de Rede:** Mecanismos físicos de bloqueio de I/O de rede não implementados.
- **Política Final de Comando/Mount:** Regras restritivas de execução e visibilidade de arquivos ainda são permissivas.
- **Superfície de Escape:** Capacidade de contenção real sob ataque ou código malicioso.

## 4. Decisão de Fechamento da Fase 0
- **Status Final:** Encerrada.
- **Justificativa:** O esqueleto lógico está pronto para suportar a carga operacional. A infraestrutura de orquestração é estável.
- **Ressalva Crítica:** A segurança da Sandbox é a última barreira de fundação pendente.
- **Autorização Formal:** Fica autorizada a abertura da Fase 1, limitada estritamente ao **Lote 1: Isolamento de Sandbox**.

## 5. Missão do Lote 1 da Fase 1
> "Materializar uma boundary de segurança real e isolamento forte entre o runtime e o host, provando a eficácia da contenção física antes de conectar o sistema à inteligência do LLM."

## 6. Definição Operacional de Isolamento Forte
Para o Sistema Sucessor, isolamento forte significa:
1. **Contenção de Processo:** Processos da sandbox não podem listar, sinalizar ou interagir com processos do host ou de outras sandboxes.
2. **Virtualização de Filesystem:** A sandbox vê apenas o workspace materializado; o acesso ao `/etc`, `/proc` do host ou volumes sensíveis é fisicamente impossível.
3. **Network Jail:** Ausência total de stacks de rede ou bloqueio via kernel (ex: namespaces) que impeça exfiltração de dados ou chamadas externas não autorizadas.
4. **Resiliência a Escape:** Garantia de que privilégios elevados dentro da sandbox não se traduzam em privilégios no host.

## 7. Candidatos de Sandbox para o Lote 1 (Famílias de Abordagem)

| Abordagem | Exemplos | Vantagens | Riscos | Merece exp? |
| :--- | :--- | :--- | :--- | :--- |
| **Container Hardened** | Docker (gVisor/Sysbox) | Próximo ao dev local, baixo custo. | Escapes conhecidos no kernel compartilhado. | Sim |
| **Sandbox Managed Cloud** | E2B, Modal, AWS Lambda | Isolamento de VM por design, zero infra. | Latência de rede e dependência de SaaS. | Sim |
| **MicroVM Local** | Firecracker, Kata Containers | Isolamento de hardware, alta segurança. | Complexidade de setup em Windows/Dev. | Sim (Não descartar cedo) |

> [!IMPORTANT]
> **Nota de Planejamento:** A Etapa 1 (Threat Model e Especificação) não deve descartar a abordagem de MicroVM Local prematuramente por mera conveniência de setup. O descarte ou aceitação deve ser derivado estritamente da matriz de capacidades e do custo operacional real.

## 8. Critérios de Decisão do Lote 1
- **Segurança (Peso 40%):** Capacidade real de contenção e histórico de vulnerabilidades.
- **Ergonomia (Peso 20%):** Facilidade de integração com a `SandboxInterface` Python.
- **Latência (Peso 20%):** Compatibilidade com o feedback-loop de desenvolvimento iterativo (Sem meta arbitrária).
- **Independência (Peso 20%):** Gerenciamento do risco de vendor lock-in e suporte a dev local.

## 9. Experimento Mínimo Comparativo do Lote 1
### Hipótese
"Abordagens de isolamento por MicroVM ou Managed VM oferecem contenção de rede e filesystem superior a Containers sem degradar a ergonomia do loop de desenvolvimento."

- **Cenários:** Tentativa de exfiltração de dados (rede) e leitura de arquivos sensíveis do host.
- **Medição:** Latência comparativa entre operações atômicas (create/exec/destroy).
- **Resultado Esperado:** Definição clara do trade-off entre segurança e velocidade para escolha de adaptadores de Dev vs Produção.

## 10. Backlog Reordenado do Lote 1 da Fase 1

### Etapa 1 — Threat Model e Especificação
- [ ] **F1-L1-T1:** Elaboração do Threat Model de Boundary (Definição de Escapes e Ameaças)
- [ ] **F1-L1-T2:** Matriz de Capacidades Obrigatórias e Protocolo de Ataque/Benchmark
- [ ] **F1-L1-T3:** Especificação de Capabilities Mínimas da Sandbox Forte (Draft Técnico)

### Etapa 2 — Implementação e Prova
- [ ] **F1-L1-T4:** Implementação dos Adaptadores Candidatos (Docker vs Managed Cloud)
- [ ] **F1-L1-T5:** Execução do Protocolo de Benchmark Comparativo
- [ ] **F1-L1-T6:** Arbitragem Final (Default de Desenvolvimento vs Default de Segurança-Alvo)

## 11. O Que Não Entra no Lote 1 da Fase 1
- Integração com LLMs Reais ou APIs.
- Planejamento de Multi-agentes ou UI.
- Otimizações de performance prematuras fora do escopo de isolamento.

## 12. Gate de Saída do Lote 1 da Fase 1
Decisão fundamentada sobre os adaptadores que serão usados na Fase 1, com prova de que a abordagem de produção contém ataques de rede, filesystem e escalada de privilégio conforme o protocolo definido na Etapa 1.

## 13. Caminho Mínimo de Transição da Fase 0 para o Lote 1 da Fase 1
1. **Fechamento:** Registro deste artefato em `TRANSICAO_FASE_0_PARA_FASE_1_LOTE_1.md`.
2. **Abertura:** Atualização do backlog operacional para o Lote 1.
3. **Preparação:** Escolha das versões/vendors dos candidatos (Docker/E2B).
4. **Checkpoint:** Revisão do experimento de ataque pelo Security Boundary Architect.

## 14. Recomendação Final
Priorizar a **contenção física** sobre a **flexibilidade funcional**. A Fase 1 só deve avançar para inteligência quando o "aquário" estiver provadamente estanque.

## 15. Instrução do Fundador em Uma Frase
> "Não construa uma inteligência poderosa sobre uma fundação que não consegue segurar um processo rebelde."
