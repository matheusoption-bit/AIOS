# Protocolo de Ataque e Benchmark de Sandbox (Lote 1)

## 1. Testes de Escape de Filesystem (FS-ESCAPE)
| Teste | Comando Mock | Resultado Esperado | Critério de Falha |
| :--- | :--- | :--- | :--- |
| **Read Host SSH** | `cat ~/.ssh/id_rsa` | `File not found` | Leitura de bytes reais do host. |
| **Write Protected** | `touch /etc/malicious` | `Read-only` ou `Denied` | Escrita fora do root virtualizado da sandbox. |
| **Virtualized Root** | `ls /` | Árvore OS legítima da sandbox | Ver arquivos do **Host** (ex: `C:\Users`). |

## 2. Testes de Path Traversal (FS-TRAVERSAL)
| Teste | Comando Mock | Resultado Esperado | Critério de Falha |
| :--- | :--- | :--- | :--- |
| **Relative Escape** | `cat ../../../etc/passwd` | Permanecer no Workspace | Acesso a arquivos acima do root da sandbox. |
| **Symlink Escape** | `ln -s /etc/shadow link; cat link` | Erro ou leitura do `/etc` interno | Resolução de link para o sistema do host. |
| **Canonical Resolution** | Acesso via path absoluto do host | `Not found` | Bypass da virtualização via path real. |

## 3. Testes de Neutralização de Rede (NET-HEX - Tese B)
> [!IMPORTANT]
> **Decisão de Homologação:** Adotada a **Tese B**. O foco da homologação é o **Isolamento de Infraestrutura do Host**. A presença de rede externa não invalida o gate de boundary, desde que o alcance ao orquestrador seja nulo.

| Teste | Comando Mock | Resultado Esperado | Critério de Falha |
| :--- | :--- | :--- | :--- |
| **External Egress** | `curl -I google.com` | `SUCCESS` | N/A (Aceito sob Tese B). |
| **Host Bridge** | `curl 172.17.0.1` | `unreachable` | Sucesso na conexão ao host bridge. |
| **Local Private IP** | `ping 192.168.1.1` | `unreachable` | Comunicação com rede local sensível. |

## 4. Testes de Exfiltração de Segredos (SECRET-ESCAPE)
| Teste | Comando Mock | Resultado Esperado | Critério de Falha |
| :--- | :--- | :--- | :--- |
| **Env Leak** | `printenv` | Apenas envs configuradas | Presença de chaves/tokens do Host ou Runtime. |
| **Docker Socket** | `ls /var/run/docker.sock` | `Not found` | Acesso ao socket (permite controle do host). |
| **Cloud/Git Config** | `ls ~/.aws` or `~/.gitconfig` | `Not found` | Vazamento de credenciais globais do host. |

## 5. Testes de Lifecycle e Escape de Processo (PROC-HALT)
| Teste | Comando Mock | Resultado Esperado | Critério de Falha |
| :--- | :--- | :--- | :--- |
| **Zombie Check** | `sleep 9999 &` | Processo morto após `destroy()` | Processo continua rodando no host. |
| **PID Visibility** | `ps aux` | Vê apenas processos da sandbox | Lista processos do Orquestrador ou do Host. |

## 6. Adaptabilidade e Observações de Host
- **Targeting:** Se o host for Windows, os alvos de `FS-ESCAPE` e `SECRET-ESCAPE` devem ser adaptados (ex: `%USERPROFILE%\.ssh` em vez de `~/.ssh`).
- **Limitação de Ambiente:** A falha em executar um adaptador por ausência de ferramenta no host (ex: Docker ausente) deve ser registrada como **Limitação do Equipamento de Teste**, não como descarte da arquitetura.
- **Allowlist de Env:** Variavéis como `PATH`, `LANG` ou injetadas pelo orquestrador são aceitáveis. Qualquer outra ("SENSITIVE_API_KEY") é falha crítica.

## 7. Critérios de Avaliação e Gate Binário

### A. Gate Binário de Segurança (FAIL Instantâneo)
O candidato é **reprovado automaticamente** se falhar em qualquer um destes:
- Leitura ou Escrita real no FS do Host fora do root virtual.
- Qualquer escape via Symlink ou Path Traversal.
- Resolução de DNS ou Reachability de rede externa/local.
- Processo sobrevivendo ao comando `destroy()` (Cisão de lifecycle).
- Acesso a Sockets sensíveis ou Credenciais do Host via File/Env.

### B. Score Comparativo (Para Candidatos Aprovados no Gate A)
- **Latência:** Compatibilidade com o feedback-loop iterativo (Desenvolvimento interativo).
- **Ergonomia:** Qualidade da integração com a `SandboxInterface`.
- **Independência:** Risco de Vendor Lock-in (Local vs Cloud).
