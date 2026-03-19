from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal


POLICY_MODE = os.getenv("AIOS_L3_POLICY_MODE", "shadow").strip().lower() or "shadow"
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
    def should_block(self) -> bool:
        return self.action == "blocked_enforcing"


def _normalize_mode(mode: str | None = None) -> str:
    candidate = (mode or POLICY_MODE).strip().lower()
    return candidate if candidate in {"shadow", "enforce"} else "shadow"


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

    if any(finding.severity == "block" for finding in findings):
        action: Literal["passed", "warning", "blocked_enforcing"] = "blocked_enforcing"
    elif findings:
        action = "warning"
    else:
        action = "passed"

    return PolicyGuardResult(
        mode=normalized_mode,
        action=action,
        findings=tuple(findings),
    )
