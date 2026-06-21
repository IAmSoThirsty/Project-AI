"""Read the authoritative DOI evidence without duplicating the registry."""

from __future__ import annotations

import re
from pathlib import Path

from project_ai_api.models import DoiRecord

_CATALOG_ROW = re.compile(
    r"^\| \[\[(?P<title>[^\]]+)\]\] \| "
    r"(?P<url>https://doi\.org/(?P<doi>[^ |]+)) \| (?P<domain>[^ |]+) \|$"
)


def load_doi_registry(path: Path) -> tuple[DoiRecord, ...]:
    """Load only the non-duplicated complete catalog section."""
    records: list[DoiRecord] = []
    in_catalog = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Complete Catalog":
            in_catalog = True
            continue
        if line == "## Named Catalog":
            break
        if not in_catalog:
            continue
        match = _CATALOG_ROW.fullmatch(line)
        if match is None:
            continue
        records.append(DoiRecord(**match.groupdict()))
    if not records:
        raise ValueError(f"No DOI records found in {path}")
    return tuple(records)
