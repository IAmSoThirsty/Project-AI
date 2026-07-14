"""TAAR classification engine.

Escalation order: OPEN < CONTROLLED < RESTRICTED < SECRET < PHANTOM < BLACK.
Classification escalates only. It never downgrades automatically —
downgrade requires human declassification, which TAAR does not implement.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from taar.models import CLASSIFICATION_RANK, ClassificationLevel, EvidenceBundle

if TYPE_CHECKING:
    from taar.registry import Registry

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "private_key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    ),
    ("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "jwt_like_token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}\b"),
    ),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}\b")),
    (
        "credential_url",
        re.compile(
            r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^:/\s]+:[^@\s]+@"
        ),
    ),
    (
        "env_secret",
        re.compile(r"(?im)^\s*[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD)\s*=\s*\S{8,}"),
    ),
    (
        "redacted_marker",
        re.compile(r"«redacted:"),
    ),
]

PLACEHOLDER_MARKERS = (
    "changeme",
    "example",
    "dummy",
    "fake",
    "test-token",
    "placeholder",
    "your-",
    "xxxx",
    "<",
    "redacted",
)

_ORDER = sorted(CLASSIFICATION_RANK, key=CLASSIFICATION_RANK.__getitem__)


def rank(level: ClassificationLevel) -> int:
    return CLASSIFICATION_RANK[level]


def escalate(current: ClassificationLevel, candidate: ClassificationLevel) -> ClassificationLevel:
    """Return the higher-ranked classification. Never downgrades."""
    return candidate if rank(candidate) > rank(current) else current


def is_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def find_secret_matches(text: str) -> list[tuple[str, str]]:
    """Return (pattern_name, matched_value) pairs found in text."""
    matches: list[tuple[str, str]] = []
    for name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            matches.append((name, match.group(0)))
    return matches


def redact(value: str) -> str:
    """Redact a secret-like value, keeping at most the first and last 4 chars.

    Already-redacted markers («redacted:VALUE») are unwrapped first so the
    inner value is redacted normally.
    """
    marker = _REDACTED_MARKER.match(value.strip())
    if marker is not None:
        value = marker.group(1)
    stripped = value.strip()
    if len(stripped) <= 12:
        return "***"
    return f"{stripped[:4]}...{stripped[-4:]}"


_REDACTED_MARKER = re.compile(r"^«redacted:(.*)»$")


def classify_finding(message: str, default: ClassificationLevel) -> ClassificationLevel:
    if find_secret_matches(message):
        return escalate(default, ClassificationLevel.SECRET)
    return default


def classify_evidence(bundle: EvidenceBundle) -> ClassificationLevel:
    level = bundle.classification
    for finding in bundle.findings:
        level = classify_finding(finding.message, level)
    return level


def classify_artifact(path: Path, has_run_record: bool) -> ClassificationLevel:
    """An artifact without a producing run record is PHANTOM."""
    if not has_run_record:
        return ClassificationLevel.PHANTOM
    return ClassificationLevel.OPEN


def may_feed_writer(level: ClassificationLevel, registry: Registry) -> bool:
    """Whether evidence at this classification may feed a writer.

    BLACK and PHANTOM never feed writers. Other levels follow the
    classifications registry. SECRET is handled by the executor's
    declared-secret-writer exception (a writer whose task classification
    default is SECRET and whose output is redacted may consume SECRET
    evidence — this is the sanitized secret-report path)."""
    if level in (ClassificationLevel.BLACK, ClassificationLevel.PHANTOM):
        return False
    meta = registry.classifications_by_level.get(level.value, {})
    return bool(meta.get("may_feed_writer", False))


def requires_redaction(level: ClassificationLevel, registry: Registry) -> bool:
    meta = registry.classifications_by_level.get(level.value, {})
    return bool(meta.get("redaction_required", level == ClassificationLevel.SECRET))


def requires_quarantine(level: ClassificationLevel, registry: Registry) -> bool:
    meta = registry.classifications_by_level.get(level.value, {})
    default = level in (ClassificationLevel.PHANTOM, ClassificationLevel.BLACK)
    return bool(meta.get("quarantine_required", default))
