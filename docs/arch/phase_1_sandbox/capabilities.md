## 1. Isolamento de FS (Core Property)
- **Isolation Level:** Virtualizado ou Chrooted (A sandbox deve possuir seu próprio root `/` independente do host).
- **Traversal Protection:** Bloqueio nativo de escapes via `..` ou resoluções de paths absolutos do host.
- **Mounts:** Apenas o diretório de workspace deve ser montado como `RW`. Todos os outros diretórios de runtime necessários devem ser `RO`.
- **Symlink Protection:** Seguimento de symlinks que apontem para fora do boundary virtualizado deve ser bloqueado.

## 2. Network (Core Property - Tese B)
- **Política Mandatória:** **Isolamento de Host + Egress Controlado**.
- **Isolamento de Host:** Bloqueio absoluto de alcance a `localhost` do orquestrador, redes de bridge (ex: `172.17.0.1`) e IPs privados da rede local da infraestrutura.
- **Egress (Saída):** Em ambientes Cloud/Managed (E2B), a saída para a internet é permitida por padrão para viabilizar ferramentas, mas deve ser tratada como canal de exfiltração monitorado no Lote 2.
- **DNS:** Resolução externa permitida em Tese B.

## 3. Privilégios (Core Property)
- **User:** O código deve rodar como um usuário sem privilégios (`non-root`).
- **Capabilities:** Remoção de `CAP_SYS_ADMIN`, `CAP_NET_RAW`, etc. do container/processo.

## 4. Observabilidade e Controle
- **Logs:** Captura obrigatória de `stdout` e `stderr` sem bypass.
- **Kill Switch:** O `destroy()` deve invocar um `SIGKILL` garantido em toda a árvore de processos descendente.

## 5. Itens em Aberto (Post-Etapa 1)
- Persistência de volumes entre sandboxes (inicialmente proibido).
- Compartilhamento de GPU (inicialmente proibido).
