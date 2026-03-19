"""
Módulo de Ledger Endurecido do Lote 2 do AIOS.

Responsável por:
- Geração de run_id por corrida
- Sequência monotônica de eventos (event_seq)
- Hash chain SHA-256 por corrida
- Política fail-closed proporcional de escrita
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Versão canônica do schema do ledger
SCHEMA_VERSION = "l2_ledger_v2"

# Tipos de evento válidos
VALID_EVENT_TYPES = frozenset({
    "LLM_CALL",
    "LLM_RESPONSE",
    "POLICY_CHECK",
    "SANDBOX_CREATE",
    "SANDBOX_EXEC",
    "SANDBOX_MUTATION",
    "EVIDENCE_CHECK",
    "RUN_FINISHED",
})

# Estágios válidos
VALID_STAGES = frozenset({
    "PROVIDER",
    "RUNTIME",
    "SANDBOX",
    "EVIDENCE",
    "FINALIZATION",
})

# Status válidos
VALID_STATUSES = frozenset({
    "OK",
    "FAIL",
    "ERROR",
})

# Outcomes finais válidos (exclusivos de RUN_FINISHED)
VALID_FINAL_OUTCOMES = frozenset({
    "SUCCESS",
    "PARTIAL_SUCCESS",
    "SECURITY_VIOLATION",
    "PROVIDER_FAILURE",
    "SANDBOX_FAILURE",
    "EVIDENCE_FAILURE",
    "LEDGER_FAILURE",
})


class LedgerWriteError(Exception):
    """Exceção para falha crítica de escrita no ledger."""
    pass


class L2Ledger:
    """
    Ledger endurecido do Lote 2.

    Cada instância representa uma corrida (run) com run_id único,
    sequência monotônica de eventos e hash chain SHA-256.
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or Path("artifacts/l2/l2_execution_ledger.jsonl")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        self.run_id = str(uuid.uuid4())
        self._event_seq = 0
        self._prev_hash = "GENESIS"
        self.ledger_degraded = False
        self._first_event_written = False

    def _compute_hash(self, event: dict) -> str:
        """
        Calcula SHA-256 do evento serializado canonicamente.
        O campo event_hash é excluído do cálculo (ainda não existe no dict neste ponto).
        """
        canonical = json.dumps(event, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _build_event(self, event_type: str, stage: str, status: str,
                     payload: dict) -> dict:
        """Constrói o dicionário de evento com todos os campos obrigatórios."""
        self._event_seq += 1

        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type inválido: {event_type}")
        if stage not in VALID_STAGES:
            raise ValueError(f"stage inválido: {stage}")
        if status not in VALID_STATUSES:
            raise ValueError(f"status inválido: {status}")

        event = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "event_seq": self._event_seq,
            "event_id": f"{self.run_id}::{self._event_seq}",
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": event_type,
            "stage": stage,
            "status": status,
            "payload": payload,
            "prev_hash": self._prev_hash,
        }

        event_hash = self._compute_hash(event)
        event["event_hash"] = event_hash

        return event

    def _write_event(self, event: dict) -> None:
        """Escreve o evento no JSONL. Lança IOError em caso de falha."""
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _is_critical_point(self, event_type: str) -> bool:
        """Determina se este ponto de escrita é crítico (aborta em falha)."""
        if event_type == "RUN_FINISHED":
            return True
        if not self._first_event_written:
            return True
        return False

    def emit(self, event_type: str, stage: str, status: str,
             payload: dict) -> Optional[dict]:
        """
        Emite um evento no ledger.

        Retorna:
            dict: o evento estruturado escrito, se bem-sucedido
            None: se falha intermediária (ledger degradado)

        Lança:
            LedgerWriteError: se falha em ponto crítico (primeiro evento)
        """
        event = self._build_event(event_type, stage, status, payload)
        is_critical = self._is_critical_point(event_type)

        try:
            self._write_event(event)
            self._prev_hash = event["event_hash"]
            self._first_event_written = True
            return event
        except Exception as e:
            if is_critical:
                raise LedgerWriteError(
                    f"Falha crítica ao escrever evento '{event_type}' no ledger: {e}"
                ) from e
            else:
                self.ledger_degraded = True
                print(
                    f"[LEDGER AVISO] Falha ao escrever evento '{event_type}' "
                    f"(event_seq={event['event_seq']}). Ledger degradado. Erro: {e}"
                )
                # Atualiza prev_hash mesmo sem escrita, para manter consistência
                # interna do sequencing (o hash chain ficará quebrado no arquivo,
                # mas o validador detectará isso)
                self._prev_hash = event["event_hash"]
                return None

    def emit_run_finished(self, final_outcome: str,
                          evidence_level: str = "NONE",
                          summary: str = "",
                          **extra_payload) -> dict:
        """
        Emite o evento terminal RUN_FINISHED.

        Lança LedgerWriteError se a escrita falhar (ponto crítico).
        """
        if final_outcome not in VALID_FINAL_OUTCOMES:
            raise ValueError(f"final_outcome inválido: {final_outcome}")

        payload = {
            "final_outcome": final_outcome,
            "evidence_level": evidence_level,
            "summary": summary,
        }
        
        if extra_payload:
            payload.update(extra_payload)

        if self.ledger_degraded:
            payload["ledger_degraded"] = True

        status = "OK" if final_outcome in ("SUCCESS", "PARTIAL_SUCCESS") else "FAIL"

        event = self._build_event("RUN_FINISHED", "FINALIZATION", status, payload)

        try:
            self._write_event(event)
            self._prev_hash = event["event_hash"]
            return event
        except Exception as e:
            raise LedgerWriteError(
                f"Falha crítica ao escrever RUN_FINISHED no ledger: {e}"
            ) from e
