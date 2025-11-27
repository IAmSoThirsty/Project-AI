"""Privacy Guardian agent: PII detection and redaction helpers."""

import re
from typing import Dict, List


class PrivacyGuardian:
    """Detect and redact simple PII patterns from text.

    NOTE: This is a best-effort placeholder and not a substitute for
    production-grade PII detection libraries.
    """

    EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_RE = re.compile(r"\b\+?\d[\d\s\-]{7,}\b")

    def __init__(self) -> None:
        pass

    def find_pii(self, text: str) -> List[Dict[str, str]]:
        findings = []
        for m in self.EMAIL_RE.finditer(text or ""):
            findings.append({"type": "email", "match": m.group(0)})
        for m in self.PHONE_RE.finditer(text or ""):
            findings.append({"type": "phone", "match": m.group(0)})
        return findings

    def redact(self, text: str) -> str:
        t = self.EMAIL_RE.sub("[REDACTED_EMAIL]", text or "")
        t = self.PHONE_RE.sub("[REDACTED_PHONE]", t)
        return t
