# Lote 2: Integração LLM (Consolidação Local)

Este diretório contém os artefatos de execução do Lote 2 do AIOS.

## Configuração Local

1. **Credenciais**:
   - Copie o arquivo `example.env` da raiz para um novo arquivo `.env`.
   - Preencha `OPENAI_API_KEY` e `E2B_API_KEY`.

2. **Dependências**:
   - Certifique-se de que as dependências do projeto estão instaladas (`pip install -r requirements.txt`).

## Execução e Prova (Smoke Test)

O runner possui um modo de **Smoke Test** determinístico que valida o circuito completo:
`Instrução -> LLM -> Comando -> Sandbox -> Verificação de Arquivo`.

```powershell
python src/lote2/lote2_runner.py
```

### O que acontece no Smoke Test?
- O sistema envia uma instrução fixa para criar `/tmp/l2_proof.txt`.
- Após a execução do comando na sandbox, o runner tenta ler este arquivo.
- Se o conteúdo coincidir, o ledger registrará `STRONG_DETERMINISTIC_PROVED`.

## Ledger Endurecido (schema `l2_ledger_v2`)

O ledger em `l2_execution_ledger.jsonl` registra eventos com rastreabilidade completa.

### Campos de cada evento
| Campo | Descrição |
|-------|-----------|
| `schema_version` | Versão do schema (`l2_ledger_v2`) |
| `run_id` | UUID4 único por corrida |
| `event_seq` | Sequência monotônica (1, 2, 3...) |
| `event_id` | `{run_id}::{event_seq}` |
| `timestamp_utc` | ISO 8601 em UTC |
| `event_type` | Tipo do evento (ver abaixo) |
| `stage` | Estágio: `PROVIDER`, `SANDBOX`, `EVIDENCE`, `FINALIZATION` |
| `status` | `OK`, `FAIL` ou `ERROR` |
| `payload` | Dados específicos do evento |
| `prev_hash` | SHA-256 do evento anterior (`GENESIS` para o primeiro) |
| `event_hash` | SHA-256 do evento serializado |

### Tipos de evento
| Tipo | Estágio | Descrição |
|------|---------|-----------|
| `LLM_CALL` | `PROVIDER` | Início da chamada ao provider |
| `LLM_RESPONSE` | `PROVIDER` | Resposta recebida e parseada |
| `SANDBOX_CREATE` | `SANDBOX` | Criação da sandbox |
| `SANDBOX_EXEC` | `SANDBOX` | Execução do comando |
| `EVIDENCE_CHECK` | `EVIDENCE` | Verificação de evidência |
| `RUN_FINISHED` | `FINALIZATION` | Veredito final da corrida |

### Política de falha do ledger
- Falha no primeiro evento ou `RUN_FINISHED`: **aborta a corrida**
- Falha em evento intermediário: **aviso + flag `ledger_degraded`**

## Validação do Ledger

```powershell
python src/lote2/validate_ledger.py                           # ledger ativo
python src/lote2/validate_ledger.py caminho/outro_ledger.jsonl  # caminho custom
```

O validador verifica: campos obrigatórios, schema_version, sequência monotônica, hash chain, unicidade de `RUN_FINISHED` e posição terminal.

## Backup do Ledger Legado

O ledger anterior ao endurecimento está preservado em `l2_execution_ledger.jsonl.pre_hardening`.
