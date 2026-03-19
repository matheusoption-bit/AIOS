"""
Validador de integridade do Ledger Endurecido do Lote 2 do AIOS.

Verifica por corrida (run_id):
- campos obrigatórios presentes
- schema_version esperado
- sequência monotônica de event_seq
- event_id coerente com run_id::event_seq
- hash chain (prev_hash do evento N == event_hash do evento N-1)
- exatamente um RUN_FINISHED por corrida
- RUN_FINISHED como último evento da corrida

Uso:
    python src/lote2/validate_ledger.py [caminho_opcional.jsonl]
"""

import sys
import os
import json
import hashlib
import hmac
from pathlib import Path
from collections import defaultdict

# Adiciona a raiz do projeto ao sys.path para imports relativos funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.lote2.ledger import (
    SCHEMA_VERSION,
    LEGACY_SCHEMA_VERSIONS,
    LEDGER_HMAC_ENV_VAR,
    DEV_FALLBACK_HMAC_KEY,
    VALID_EVENT_TYPES,
    VALID_STAGES,
    VALID_STATUSES,
    VALID_FINAL_OUTCOMES,
    VALID_EVIDENCE_LEVELS,
    VALID_INTEGRITY_MODES,
)

EXPECTED_SCHEMA_VERSION = SCHEMA_VERSION
SUPPORTED_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION, *LEGACY_SCHEMA_VERSIONS})

REQUIRED_FIELDS = frozenset({
    "schema_version", "run_id", "event_seq", "event_id",
    "timestamp_utc", "event_type", "stage", "status",
    "payload", "prev_hash", "event_hash",
})


def compute_hash(event: dict) -> str:
    """Recalcula o hash do evento (sem o campo event_hash)."""
    event_copy = {k: v for k, v in event.items() if k != "event_hash"}
    canonical = json.dumps(event_copy, sort_keys=True, ensure_ascii=False)
    integrity_mode = event_copy.get("integrity_mode")
    if integrity_mode is None and event_copy.get("schema_version") in LEGACY_SCHEMA_VERSIONS:
        integrity_mode = "LEGACY_SHA256"

    if integrity_mode == "LEGACY_SHA256":
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    hmac_key = os.getenv(LEDGER_HMAC_ENV_VAR, DEV_FALLBACK_HMAC_KEY).encode("utf-8")
    return hmac.new(hmac_key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def validate_ledger(ledger_path: Path) -> bool:
    """
    Valida o ledger JSONL. Retorna True se todas as corridas são válidas.
    """
    if not ledger_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {ledger_path}")
        return False

    # Leitura e parse
    events = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                events.append((line_num, event))
            except json.JSONDecodeError as e:
                print(f"[ERRO] Linha {line_num}: JSON inválido — {e}")
                return False

    if not events:
        print("[AVISO] Ledger vazio.")
        return True

    # Agrupar por run_id
    runs = defaultdict(list)
    for line_num, event in events:
        run_id = event.get("run_id", "__DESCONHECIDO__")
        runs[run_id].append((line_num, event))

    total_runs = len(runs)
    valid_runs = 0
    failed_runs = 0

    for run_id, run_events in runs.items():
        print(f"\n{'='*60}")
        print(f"  Corrida: {run_id}")
        print(f"  Eventos: {len(run_events)}")
        print(f"{'='*60}")

        run_ok = True
        errors = []

        # Verificação 1: campos obrigatórios e schema_version
        for line_num, event in run_events:
            missing = REQUIRED_FIELDS - set(event.keys())
            if missing:
                errors.append(f"  Linha {line_num}: campos ausentes — {missing}")
                run_ok = False

            sv = event.get("schema_version")
            if sv not in SUPPORTED_SCHEMA_VERSIONS:
                errors.append(
                    f"  Linha {line_num}: schema_version '{sv}' não suportado (esperado um de {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
                )
                run_ok = False

            integrity_mode = event.get("integrity_mode")
            if sv == EXPECTED_SCHEMA_VERSION:
                if integrity_mode not in VALID_INTEGRITY_MODES - {"LEGACY_SHA256"}:
                    errors.append(
                        f"  Linha {line_num}: integrity_mode '{integrity_mode}' inválido para schema '{EXPECTED_SCHEMA_VERSION}'"
                    )
                    run_ok = False

            ev_type = event.get("event_type")
            if ev_type and ev_type not in VALID_EVENT_TYPES:
                errors.append(f"  Linha {line_num}: event_type inválido '{ev_type}'")
                run_ok = False

            stage = event.get("stage")
            if stage and stage not in VALID_STAGES:
                errors.append(f"  Linha {line_num}: stage inválido '{stage}'")
                run_ok = False

            status = event.get("status")
            if status and status not in VALID_STATUSES:
                errors.append(f"  Linha {line_num}: status inválido '{status}'")
                run_ok = False

            if ev_type == "RUN_FINISHED":
                payload = event.get("payload", {})
                outcome = payload.get("final_outcome")
                if outcome and outcome not in VALID_FINAL_OUTCOMES:
                     errors.append(f"  Linha {line_num}: final_outcome inválido '{outcome}'")
                     run_ok = False
                
                # Consistência: se outcome é success/partial, status deve ser OK. Se não, FAIL.
                expected_status = "OK" if outcome in ("SUCCESS", "PARTIAL_SUCCESS") else "FAIL"
                if status != expected_status:
                    errors.append(f"  Linha {line_num}: status '{status}' inconsistente com outcome '{outcome}' (esperado '{expected_status}')")
                    run_ok = False

                evidence_level = payload.get("evidence_level")
                if evidence_level and evidence_level not in VALID_EVIDENCE_LEVELS:
                    errors.append(f"  Linha {line_num}: evidence_level inválido '{evidence_level}'")
                    run_ok = False

                if sv == EXPECTED_SCHEMA_VERSION and payload.get("intent_phase") != "CLOSE":
                    errors.append(f"  Linha {line_num}: RUN_FINISHED deve registrar intent_phase='CLOSE'")
                    run_ok = False

            if ev_type == "LLM_CALL" and sv == EXPECTED_SCHEMA_VERSION:
                payload = event.get("payload", {})
                if payload.get("intent_phase") != "OPEN":
                    errors.append(f"  Linha {line_num}: LLM_CALL deve registrar intent_phase='OPEN'")
                    run_ok = False


        # Verificação 2: sequência monotônica de event_seq
        seqs = [event.get("event_seq") for _, event in run_events]
        expected_seqs = list(range(1, len(run_events) + 1))
        if seqs != expected_seqs:
            errors.append(f"  Sequência event_seq incorreta: {seqs} (esperado: {expected_seqs})")
            run_ok = False

        # Verificação 3: event_id coerente
        for line_num, event in run_events:
            expected_id = f"{run_id}::{event.get('event_seq')}"
            actual_id = event.get("event_id")
            if actual_id != expected_id:
                errors.append(f"  Linha {line_num}: event_id '{actual_id}' != esperado '{expected_id}'")
                run_ok = False

        # Verificação 4: hash chain
        for i, (line_num, event) in enumerate(run_events):
            # Verificar event_hash
            recalculated = compute_hash(event)
            if recalculated != event.get("event_hash"):
                errors.append(
                    f"  Linha {line_num}: event_hash inválido "
                    f"(registrado: {event.get('event_hash', 'AUSENTE')[:16]}..., "
                    f"calculado: {recalculated[:16]}...)"
                )
                run_ok = False

            # Verificar prev_hash
            if i == 0:
                if event.get("prev_hash") != "GENESIS":
                    errors.append(f"  Linha {line_num}: primeiro evento deve ter prev_hash='GENESIS'")
                    run_ok = False
            else:
                prev_event = run_events[i - 1][1]
                if event.get("prev_hash") != prev_event.get("event_hash"):
                    errors.append(
                        f"  Linha {line_num}: prev_hash não corresponde ao event_hash do evento anterior"
                    )
                    run_ok = False

        # Verificação 5: exatamente um RUN_FINISHED
        finished_events = [(ln, ev) for ln, ev in run_events if ev.get("event_type") == "RUN_FINISHED"]
        if len(finished_events) == 0:
            errors.append("  Nenhum evento RUN_FINISHED encontrado")
            run_ok = False
        elif len(finished_events) > 1:
            errors.append(f"  Múltiplos RUN_FINISHED encontrados ({len(finished_events)})")
            run_ok = False

        # Verificação 6: RUN_FINISHED deve ser o último evento
        if finished_events:
            last_line = run_events[-1][0]
            finished_line = finished_events[-1][0]
            if finished_line != last_line:
                errors.append(
                    f"  RUN_FINISHED (linha {finished_line}) não é o último evento (linha {last_line})"
                )
                run_ok = False

        # Resultado da corrida
        if run_ok:
            print("  ✓ VÁLIDA")
            valid_runs += 1
        else:
            print("  ✗ INVÁLIDA")
            for err in errors:
                print(err)
            failed_runs += 1

    # Resumo final
    print(f"\n{'='*60}")
    print(f"  RESUMO DO LEDGER")
    print(f"{'='*60}")
    print(f"  Arquivo:          {ledger_path}")
    print(f"  Total de corridas: {total_runs}")
    print(f"  Válidas:           {valid_runs}")
    print(f"  Inválidas:         {failed_runs}")
    print(f"  Veredito:          {'OK' if failed_runs == 0 else 'FALHA'}")
    print(f"{'='*60}\n")

    return failed_runs == 0


if __name__ == "__main__":
    # Caminho padrão: ledger ativo do Lote 2
    default_path = Path("artifacts/l2/l2_execution_ledger.jsonl")

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = default_path

    print(f"[Validador L2] Validando: {target}")
    ok = validate_ledger(target)
    sys.exit(0 if ok else 1)
