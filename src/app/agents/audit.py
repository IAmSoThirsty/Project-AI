"""Explainability & Audit agent: record explainability outputs and audit events."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditAgent:
    """Record explainability outputs and audit events to persona_dir files."""

    def __init__(self, persona_dir: Optional[str] = None) -> None:
        self.persona_dir = persona_dir
        if self.persona_dir:
            os.makedirs(self.persona_dir, exist_ok=True)

    def record_explainability(
        self, which: str, explain: List[Dict[str, Any]], meta: Dict[str, Any] = None
    ) -> bool:
        try:
            path = os.path.join(self.persona_dir or ".", "explainability_audit.log")
            entry = {
                "timestamp": datetime.now().isoformat(),
                "model": which,
                "explain": explain,
                "meta": meta or {},
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            return True
        except Exception:
            return False

    def record_event(self, name: str, details: Dict[str, Any]) -> bool:
        try:
            path = os.path.join(self.persona_dir or ".", "event_audit.log")
            entry = {
                "timestamp": datetime.now().isoformat(),
                "event": name,
                "details": details,
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            return True
        except Exception:
            return False
