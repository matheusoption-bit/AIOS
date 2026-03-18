# Formalização: Event Log Mínimo (Ledger Fase 0)

## 1. Princípios do Ledger
- **Append-Only:** Escrita serializada em formato JSONL (JSON lines).
- **Auditabilidade Forense:** Cada entrada permite reconstruir o "porquê" (Intent) e o "resultado" (Git Ref).
- **Integridade Mecânica:** Chain de hashes SHA-256 por entrada.

## 2. Estrutura da Entrada (`LedgerEntry`)

```json
{
  "index": 101,
  "event_type": "EXECUTION_FINISHED",
  "intent_id": "uuid-v4",
  "timestamp": "2026-03-17T21:50:00Z",
  "payload": {
      "status": "SUCCESS",
      "termination_reason": "COMPLETED",
      "git_ref": "sha-final-do-commit",
      "output_summary": "Patch applied successfully"
  },
  "prev_hash": "sha256-anterior",
  "entry_hash": "sha256(index + intent_id + payload + prev_hash)"
}
```

## 3. Política de Integridade (Sem HMAC)
Na Fase 0, a integridade é garantida pela **sequência de hashes**:
1. Se `current.prev_hash != previous.entry_hash`, o log está violado.
2. A verificação de integridade deve ocorrer no `IDLE` (Warm-up) e no `Gate Final` de Fase 0.

## 4. Limites de Fase 0
- **Sem HMAC/Keyring:** A segurança contra adulteração local é secundária à auditabilidade lógica.
- **Persistência Simples:** Arquivo `ledger.jsonl` no host.
- **Sem Rotação de Log:** Gerenciamento manual por enquanto.
