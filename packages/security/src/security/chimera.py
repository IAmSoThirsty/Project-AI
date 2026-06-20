"""Reusable Chimera request classification and canary detection."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, Literal

from security.bridge import AppendOnlyAuditRelay, receive_canary_hit, receive_verdict

type Outcome = Literal["ALLOW", "DENY", "ESCALATE"]


@dataclass(frozen=True)
class Detection:
    score: int
    tags: tuple[str, ...]
    outcome: Outcome


@dataclass(frozen=True)
class CanaryHit:
    label: str
    token_sha256: str


@dataclass(frozen=True)
class _Rule:
    tag: str
    weight: int
    pattern: re.Pattern[bytes]


_RULES: Final = (
    _Rule("env_probe", 30, re.compile(rb"(?:^|/)\.env(?:$|[/?\r\n])", re.IGNORECASE)),
    _Rule("wp_probe", 20, re.compile(rb"wp-(?:login|admin)", re.IGNORECASE)),
    _Rule("sqli", 40, re.compile(rb"(?:\bunion\s+select\b|'\s*or\s*'?[01]'?\s*=)", re.IGNORECASE)),
    _Rule("traversal", 50, re.compile(rb"(?:\.\./|\.\.\\|/etc/passwd|/etc/shadow)", re.IGNORECASE)),
    _Rule(
        "rce", 70, re.compile(rb"(?:[?&](?:cmd|exec)=|\b(?:curl|wget)\s+https?://)", re.IGNORECASE)
    ),
    _Rule("sqli_tool", 60, re.compile(rb"\bsqlmap(?:/|\b)", re.IGNORECASE)),
    _Rule("scanner", 40, re.compile(rb"\b(?:masscan|nmap|nikto)(?:/|\b)", re.IGNORECASE)),
)


def classify(
    path: str,
    body: bytes = b"",
    ua: bytes = b"",
    headers: Mapping[str, str] | None = None,
) -> Detection:
    header_bytes = b"\n".join(
        f"{name}:{value}".encode("utf-8", "replace")
        for name, value in sorted((headers or {}).items())
    )
    subject = b"\n".join((path.encode("utf-8", "replace"), body, ua, header_bytes))
    tags = tuple(rule.tag for rule in _RULES if rule.pattern.search(subject))
    score = min(100, sum(rule.weight for rule in _RULES if rule.tag in tags))
    outcome: Outcome = "DENY" if score >= 60 else "ESCALATE" if score >= 15 else "ALLOW"
    return Detection(score=score, tags=tags, outcome=outcome)


class ChimeraSecurity:
    """Classify requests and track canaries without exposing raw tokens to audit."""

    def __init__(self, secret: bytes, relay: AppendOnlyAuditRelay | None = None) -> None:
        if len(secret) < 32:
            raise ValueError("Chimera secret must contain at least 32 bytes")
        self._secret = secret
        self._relay = relay
        self._canaries: dict[str, str] = {}
        self._lock = threading.Lock()

    def register_canary(self, label: str) -> str:
        safe_label = re.sub(r"[^a-zA-Z0-9_-]", "_", label)
        if not safe_label:
            raise ValueError("Canary label must not be empty")
        nonce = secrets.token_bytes(18)
        signature = hmac.new(self._secret, safe_label.encode() + nonce, hashlib.sha256).hexdigest()[
            :24
        ]
        token = f"CHIMERA-CANARY-{safe_label}-{signature}"
        with self._lock:
            self._canaries[token] = label
        return token

    def rotate_canary(self, label: str) -> str:
        with self._lock:
            retired = [token for token, current in self._canaries.items() if current == label]
            for token in retired:
                del self._canaries[token]
        return self.register_canary(label)

    def scan(self, content: bytes | str, *, context: str) -> tuple[CanaryHit, ...]:
        payload = content.encode("utf-8", "replace") if isinstance(content, str) else content
        with self._lock:
            matches = tuple(
                (token, label)
                for token, label in self._canaries.items()
                if token.encode() in payload
            )
        hits = tuple(
            CanaryHit(label=label, token_sha256=hashlib.sha256(token.encode()).hexdigest())
            for token, label in matches
        )
        if self._relay is not None:
            for token, _label in matches:
                receive_canary_hit(self._relay, canary_value=token, context=context)
        return hits

    def inspect(
        self,
        *,
        action_id: str,
        path: str,
        body: bytes = b"",
        ua: bytes = b"",
        headers: Mapping[str, str] | None = None,
    ) -> Detection:
        detection = classify(path, body, ua, headers)
        if self._relay is not None:
            receive_verdict(
                self._relay,
                action_id=action_id,
                verdict=detection.outcome,
                source="chimera",
            )
        return detection
