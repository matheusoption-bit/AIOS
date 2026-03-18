# Threat Model de Boundary: Sandbox Lote 1 (Fase 1)

## 1. Escopo de Proteção
O objetivo primário é proteger o **Host** e o **Runtime Orchestrator** contra código arbitrário executado na sandbox.

## 2. Vetores de Ataque Sob Escrutínio (Em Escopo)
| Vetor | Descrição | Impacto | Prioridade |
| :--- | :--- | :--- | :--- |
| **Exfiltração de Dados (Network)** | Código na sandbox tentando enviar dados para servidores externos. | Perda de Propriedade Intelectual. | **CRÍTICA** |
| **Escalonamento de Privilégios** | Processo na sandbox tentando obter `root` no host através de vulnerabilidades de kernel. | Comprometimento total do Host. | **ALTA** |
| **Vazamento de Filesystem** | Acesso a diretórios fora do workspace materializado (ex: `C:\`, `/etc`, `~/.ssh`). | Roubo de credenciais/dados. | **ALTA** |
| **Esgotamento de Recursos (DoS)** | Fork-bombs ou loops infinitos de disco/memória. | Indisponibilidade do orquestrador. | **MÉDIA** |
| **Persistência Pós-Destruição** | Processos zumbis ou cronjobs sobrevivendo ao `destroy()`. | Corrupção de execuções futuras. | **MÉDIA** |

## 3. Riscos Temporariamente Aceitáveis (Out of Scope - L1)
- **Side-channel attacks** (Spectre/Meltdown) para leitura de memória cross-sandbox.
- **Ataques de Engenharia Social** através de outputs formatados (ex: links maliciosos no log).
- **Consumo excessivo de CPU legítima** (tratado via budgets, não por contenção física no L1).

## 4. Política de Contenção (Success Criteria)
A sandbox é considerada segura para a Fase 1 se:
1. **Network:** `ping` ou `curl` retornam erro imediato (idealmente o dispositivo de rede nem existe).
2. **Filesystem:** Caminhos absolutos do host não são resolvíveis.
3. **Identity:** O usuário dentro da sandbox não tem mapeamento de permissão para arquivos do host.

## 5. Matriz de Capacidades Obrigatórias
- **Cap-P1 (Process):** Namespaces de PID isolados (sandbox não vê processos do host).
- **Cap-F1 (Filesystem):** Mount points de leitura/escrita restritos e isolados.
- **Cap-N1 (Network):** No-Network por default; Sem acesso a `localhost` do host.
- **Cap-L1 (Lifecycle):** Garantia de limpeza atômica de todos os sub-recursos no `destroy()`.
