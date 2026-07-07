from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from canonical.state import CanonicalState


class CanonicalStoreError(RuntimeError):
    pass


class FileCanonicalStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, state: CanonicalState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(f"{self.path.name}.tmp")
        payload = json.dumps(
            state.to_record(),
            indent=2,
            sort_keys=True,
        )
        temp_path.write_text(f"{payload}\n", encoding="utf-8")
        temp_path.replace(self.path)

    def load(self) -> CanonicalState:
        if not self.path.exists():
            raise CanonicalStoreError(f"canonical state file not found: {self.path}")
        try:
            record: Any = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise CanonicalStoreError(f"canonical state load failed: {exc}") from exc
        if not isinstance(record, dict):
            raise CanonicalStoreError("canonical state file must contain a JSON object")
        try:
            return CanonicalState.from_record(record)
        except Exception as exc:
            raise CanonicalStoreError(f"canonical state decode failed: {exc}") from exc
