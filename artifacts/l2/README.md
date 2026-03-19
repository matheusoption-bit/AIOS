# Lote 2: Integração LLM (Consolidação Local)

Este diretório contém os artefatos de execução do Lote 2 Mínimo do AIOS.

## Configuração Local

1. **Credenciais**:
   - Copie o arquivo `example.env` da raiz para um novo arquivo `.env`.
   - Preencha `OPENAI_API_KEY` e `E2B_API_KEY`.

2. **Dependências**:
   - Certifique-se de que as dependências do projeto estão instaladas (`pip install -r requirements.txt`).

## Execução e Prova (Smoke Test)

O runner possui um modo de **Smoke Test** determinístico que valida o circuito completo:
`Instrução -> LLM -> Comando -> Sandbox -> Verificação de Arquivo`.

Para executar:
```powershell
python src/lote2/lote2_runner.py
```

### O que acontece no Smoke Test?
- O sistema envia uma instrução fixa para criar `/tmp/l2_proof.txt`.
- Após a execução do comando na sandbox, o runner tenta ler este arquivo.
- Se o conteúdo coincidir, o log registrará `STRONG_DETERMINISTIC_PROVED`.

## Auditoria
Consulte `l2_execution_ledger.jsonl` para ver a trilha técnica de cada execução, incluindo timestamps em UTC e níveis de evidência.
