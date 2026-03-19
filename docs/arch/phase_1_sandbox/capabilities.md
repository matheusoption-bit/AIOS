## 1. Isolamento de FS (Core Property)
- **Isolation Level:** Virtualizado ou Chrooted (A sandbox deve possuir seu próprio root `/` independente do host).
- **Traversal Protection:** Bloqueio nativo de escapes via `..` ou resoluções de paths absolutos do host.
- **Mounts:** Apenas o diretório de workspace deve ser montado como `RW`. Todos os outros diretórios de runtime necessários devem ser `RO`.
- **Symlink Protection:** Seguimento de symlinks que apontem para fora do boundary virtualizado deve ser bloqueado.

## 2. Network (Core Property - Default Deny)
- **Política Mandatória:** **DEFAULT DENY**.
- **Isolamento de Host:** Bloqueio absoluto de alcance a `localhost` do orquestrador, redes de bridge (ex: `172.17.0.1`) e IPs privados da rede local da infraestrutura.
- **Egress (Saída):** A saída para a internet é **bloqueada por padrão** na Fase 1 para garantir a contenção absoluta. Chamadas a APIs de LLM devem ser mediadas pelo orquestrador fora desta boundary.
- **DNS:** Resolução externa desabilitada ou ineficaz devido ao bloqueio de rede.

## 3. Privilégios (Core Property)
- **User:** O código deve rodar como um usuário sem privilégios (`non-root`).
- **Capabilities:** Remoção de `CAP_SYS_ADMIN`, `CAP_NET_RAW`, etc. do container/processo.

## 4. Observabilidade e Controle
- **Logs:** Captura obrigatória de `stdout` e `stderr` sem bypass.
- **Kill Switch:** O `destroy()` deve invocar um `SIGKILL` garantido em toda a árvore de processos descendente.

## 5. Itens em Aberto (Post-Etapa 1)
- Persistência de volumes entre sandboxes (inicialmente proibido).
- Compartilhamento de GPU (inicialmente proibido).
