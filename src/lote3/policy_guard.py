from __future__ import annotations

import os
import re
import warnings
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal


POLICY_MODE = os.getenv("AIOS_L3_POLICY_MODE", "shadow")
_INVALID_MODE_WARNING_EMITTED = False
ALLOWED_FILE_SUFFIXES = frozenset({".txt", ".md", ".json", ".yaml", ".yml", ".log"})
SUSPICIOUS_CONTENT_PATTERNS = {
    "SUSPICIOUS_SHEBANG": re.compile(r"^#!", re.MULTILINE),
    "SUSPICIOUS_NETWORK_TOOL": re.compile(r"\b(curl|wget|Invoke-WebRequest)\b", re.IGNORECASE),
    "SUSPICIOUS_DYNAMIC_EXEC": re.compile(r"\b(eval|exec|compile)\b", re.IGNORECASE),
    "SUSPICIOUS_IMPORT": re.compile(r"\b(__import__|importlib\.import_module|subprocess|os\.popen)\b"),
    "SUSPICIOUS_BASE64": re.compile(r"\b(base64|frombase64string)\b", re.IGNORECASE),
}


@dataclass(frozen=True)
class PolicyFinding:
    rule_id: str
    severity: Literal["warning", "block"]
    message: str


@dataclass(frozen=True)
class PolicyGuardResult:
    mode: str
    action: Literal["passed", "warning", "blocked_enforcing"]
    findings: tuple[PolicyFinding, ...]

    @property
    def has_blockable_findings(self) -> bool:
        return any(finding.severity == "block" for finding in self.findings)

    @property
    def should_block(self) -> bool:
        return self.mode == "enforce" and self.has_blockable_findings


def _normalize_mode(mode: str | None = None) -> str:
    global _INVALID_MODE_WARNING_EMITTED

    raw_mode = POLICY_MODE if mode is None else mode
    candidate = (raw_mode or "").strip().lower()
    if candidate in {"shadow", "enforce"}:
        return candidate

    if not _INVALID_MODE_WARNING_EMITTED:
        warnings.warn(
            f"policy mode inválido '{raw_mode}'; degradando para 'shadow'.",
            RuntimeWarning,
            stacklevel=2,
        )
        _INVALID_MODE_WARNING_EMITTED = True
    return "shadow"


def evaluate_write_intent(safe_path: str, content: str, mode: str | None = None) -> PolicyGuardResult:
    normalized_mode = _normalize_mode(mode)
    findings: list[PolicyFinding] = []

    suffix = PurePosixPath(safe_path).suffix.lower()
    if suffix not in ALLOWED_FILE_SUFFIXES:
        findings.append(
            PolicyFinding(
                rule_id="DISALLOWED_FILE_SUFFIX",
                severity="block",
                message=(
                    f"Extensão '{suffix or '[sem extensao]'}' não faz parte da allowlist "
                    f"segura: {sorted(ALLOWED_FILE_SUFFIXES)}."
                ),
            )
        )

    for rule_id, pattern in SUSPICIOUS_CONTENT_PATTERNS.items():
        if pattern.search(content):
            findings.append(
                PolicyFinding(
                    rule_id=rule_id,
                    severity="warning",
                    message=f"Conteúdo correspondeu à regra de observação '{rule_id}'.",
                )
            )

    has_blockable_findings = any(finding.severity == "block" for finding in findings)

    if not findings:
        action: Literal["passed", "warning", "blocked_enforcing"] = "passed"
    elif normalized_mode == "enforce" and has_blockable_findings:
        action = "blocked_enforcing"
    else:
        action = "warning"

    return PolicyGuardResult(
        mode=normalized_mode,
        action=action,
        findings=tuple(findings),
    )
