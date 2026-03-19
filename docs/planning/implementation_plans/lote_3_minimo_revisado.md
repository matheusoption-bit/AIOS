# Planejamento do Lote 3 Mínimo — Revisado

## 1. Veredito sobre a proposta anterior
A proposta "Sentinela v1" deve ser **descartada como recorte principal**. 
Impor um Policy Guard (baseado em análise estática/regex) sobre uma entrada que permite shell arbitrário é combater o sintoma, não a doença. Tentar prever todas as variações maliciosas de bash é um problema insolúvel e arquiteturalmente ingênuo. A primeira linha de defesa não é filtrar o shell genérico, é **eliminar o shell genérico da API do modelo**.

## 2. Problema estrutural principal do estágio atual
A análise do código (`src/lote2/response_schema.py` e `src/lote2/lote2_runner.py`) revela a maior fragilidade arquitetural do AIOS hoje: **o tamanho do contrato entre o LLM e a Sandbox**. 
Atualmente, o LLM devolve um campo estruturado `command: str`, que o runner executa cegamente via `adapter.run_command`.
Um comando shell é uma porta de entrada semanticamente infinita. Ele subverte o controle tipado. Enquanto a interface for "me dê um comando bash", qualquer esforço de contenção será apenas heurística. O sistema precisa passar de "execução arbitrária" para "mutação determinística".

## 3. Opções reais de Lote 3 mínimo
**Opção A: Structured Mutation Boundary v1**
Uma interface estrita onde o LLM não devolve mais bash, e sim uma intenção declarativa de mutação (ex: Operação `WRITE_FILE_TEXT` com `path` e `content`). O runner valida o destino contra um workspace isolado e executa a escrita de forma parametrizada.

**Opção B: Shell Controladores (Wrappers)**
O LLM continua emitindo comandos, mas restritos a um binário/script wrapper pré-instalado na E2B, que faz a validação interna de path e payload antes de agir na file system.

**Opção C: Sentinela sobre Shell (Proposta Legada)**
Manter o contrato aberto (bash) e tentar interpor um analisador de strings/regex antes da execução na sandbox.

## 4. Recorte recomendado
**Opção A: Structured Mutation Boundary v1**

**Justificativa Forte:**
É o menor e mais seguro incremento real acima do Lote 2 porque **substitui uma superfície de ataque infinita (shell) por uma superfície perfeitamente previsível (objeto tipado)**. Ao invés do Orquestrador ser um passador de bash, ele vira um compilador de intenções seguras. 
Ao suportar apenas **uma** mutação (`WRITE_FILE_TEXT`) contida em um diretório absoluto (`/tmp/aios_workspace/`), resolve-se determinística e estruturalmente o problema de path traversal. Aproveita exatamente a fundação já provada (Lote 2 Provider + Lote 2 Sandbox + Hash Chain Ledger), apenas alterando o "tipo do payload" que viaja entre eles, elevando instantaneamente a segurança do runtime sem precisar inventar o Sentinela ainda.

## 5. Plano de Implementação Enxuto

**Arquivos prováveis:**
- `src/lote3/response_schema.py` [Cópia/Novo]: Criar schema pydantic declarativo (ex: `MutationIntent` ou `WriteFileIntent` em vez de `command: str`).
- `src/lote3/lote3_runner.py` [Evolução L2]: Substituir `adapter.run_command` por um fluxo que recebe a mutação estruturada, valida o path strict contra `/tmp/aios_workspace/` (rejeitando `..` e aberturas relativas) e então chama uma função segura da sandbox para gravar o arquivo.
- `src/lote3/ledger.py` [Evolução L2]: Adaptar o evento `SANDBOX_EXEC` para algo como `SANDBOX_MUTATION`, logando `path` e status do IO em vez de stdout/stderr genéricos.

**Mudanças principais:**
1. Orquestrador passa a exigir payload de mutação, não de shell.
2. Defesa contra Path Traversal diretamente no runner (em Python), abortando a corrida se o LLM tentar escrever fora do workspace permitido.
3. Evidência passa a ser lida do prórpio destino gravado (via `adapter.read_file()`).

**Verificações esperadas:**
- Model output com path lícito (`/tmp/aios_workspace/teste.txt`) -> Escrita sucedida e provada.
- Model output com path ilícito (`/etc/passwd` ou `../root`) -> Orquestrador detecta, emite fail-closed, registra recusa no ledger e encerra, provando a blindagem.

**Riscos de escopo:**
- Tentar suportar `READ`, `DELETE`, `MKDIR` de uma vez. O Lote 3 mínimo deve ter **apenas a capacidade de WRITE** para provar a boundary.

## 6. Branch de Trabalho
`feat/lote-3-planning-revisado`

## 7. Estado para Revisão
**Pronto para arbitragem do Fundador.** O erro inercial do planejamento estratégico anterior foi contido pela leitura explícita do código, apontando para um aperto de contrato (mutação estruturada) no lugar de uma muleta heurística (Sentinela shell). Nenhuma linha de implementação começará antes do veredito humano.
