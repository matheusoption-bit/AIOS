from __future__ import annotations

from pathlib import Path


class RawLedgerPromptingError(ValueError):
    """Levantada quando algum componente tenta usar ledger bruto como prompt."""


def assert_not_raw_ledger_source(source: str) -> None:
    normalized = source.replace("\\", "/").lower()
    if normalized.endswith(".jsonl") or "artifacts/l2/l2_execution_ledger" in normalized:
        raise RawLedgerPromptingError(
            "Ledger bruto nao pode ser usado como contexto de prompting. "
            "Use um resumo deterministico separado."
        )


def build_deterministic_prompt_context(summary: str, source_label: str = "deterministic_summary") -> dict[str, str]:
    assert_not_raw_ledger_source(source_label)
    return {
        "source": source_label,
        "summary": summary.strip(),
    }
