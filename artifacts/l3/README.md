# Lote 3: Structured Mutation Boundary v1

Este diretório contém a primeira iteração do Lote 3, que elimina a dependência aberta de *shell commands* entre o Provedor LLM e a Sandbox, substituindo-a por transações declarativas de mutação estritamente validadas.

## 1. Objetivo Fundamental
O novo fluxo do Lote 3 elimina o uso de shell arbitrário na interface com o LLM, substituindo por mutações seguras controladas via runtime. O preexistente Lote 2, no entanto, segue intocado como baseline anterior de I/O de shell livre e ledger endurecido.

## 2. Escopo Mínimo Implementado

- **Operação Suportada:** Apenas `WRITE_FILE_TEXT`. Outras operações (`READ`, `DELETE`, `MKDIR`) estão ausentes propositalmente nesta v1.
- **Path Enforcement determinístico:** Arquivos só podem ser gravados matematicamente dentro do diretório `/tmp/aios_workspace/`. Tentativas em `../` provaram ser rejeitadas como `PathViolationError`.
- **Ausência de Shell Arbitrário:** O LLM não manda mais script bash; apenas `target_path` e `content` purificados. O runner empilha as peças via recurso isolado `adapter.copy_in`, removendo o `run_command` da superfície de interação direta.
- **Continuidade de Taxonomia:** Em lugar de inventar um pseudo-ledger do zero, a taxonomia existente no `L2Ledger` foi minimamente sub-rostrada (com suporte a `"POLICY_CHECK"`e `"SANDBOX_MUTATION"`) aproveitando Hashes, Segregação, ID's, Evidências e Degradação segura.

## 3. Topologia Arquitetural Adicionada
```text
(Runner L3)
  ├── 1. Extrai Intenção Declarativa do LLM `WriteFileIntent`.
  ├── 2. Valida Destino via `path_policy` (PurePosixPath strict check vs `/tmp/aios_workspace/`).
  ├── 3. Caso Path Inseguro -> Lança `SECURITY_VIOLATION` -> Fail-Closed.
  ├── 4. Caso Seguro -> Faz I/O direto com o arquivo na E2B através de `copy_in`.
  └── 5. Confirma Evidência Lendo na E2B se o conteúdo bate exatamente.
```

## 4. Execução Padrão Realidade
Foi construído em `src/lote3/lote3_runner.py` dois ensaios obrigatórios nativos. Basta possuir credenciais ativadas em ambiente:
```bash
python src/lote3/lote3_runner.py
```
Esse comando aciona implicitamente o *Modo Lícito* gerando sucesso forte, e logo depois emenda o ensaio de *Modo Ilícito* provocando path traversal deliberado na sandbox, emitindo veredicto Fail-Close por conta de invasão fora do path reservado. 
Ambos registram provas limpas encadeadas pelo hashing contínuo na trilha de auditoria comum do Lote 2 `artifacts/l2/l2_execution_ledger.jsonl`.
