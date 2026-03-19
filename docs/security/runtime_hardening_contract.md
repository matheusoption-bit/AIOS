# Runtime Hardening Contract

Este documento registra os controles operacionais e de código que endurecem o AIOS sem transformar a segurança em policy teatral.

## Regras operacionais

- `main` deve exigir branch protection com PR obrigatório e status checks do CI Gate.
- Push direto em `main` deve permanecer bloqueado.
- O workflow de integração da sandbox deve continuar fora do gate rápido de PR.

## Regras de runtime

- O Lote 3 é o caminho oficial de execução segura.
- O Lote 2 só pode rodar em modo legado explícito com `AIOS_ENABLE_LEGACY_LOTE2=1`.
- Ledger bruto não pode ser usado como contexto de prompting; apenas resumos determinísticos derivados dele.
- Falha de ledger antes de pontos críticos deve encerrar a corrida em fail-closed.

## Regras de auditoria

- Sucesso operacional e sucesso com prova não são sinônimos.
- O ledger deve registrar abertura da intenção antes da ação e fechamento ao final da corrida.
- A trilha de auditoria usa HMAC quando `AIOS_LEDGER_HMAC_KEY` está configurada; sem isso, o modo de fallback é explicitamente marcado como não ideal.
