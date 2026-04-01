#!/usr/bin/env python3
"""Repair malformed TOML description fields under `integrations/`.

This utility was recovered from scratch and promoted into the canonical
maintenance surface so the generated integration manifests can be repaired
repeatably.
"""

from __future__ import annotations

import re
from pathlib import Path

DESCRIPTION_PATTERN = re.compile(
    r"(description\s*=\s*)(.*?)(?=\n\s*[a-zA-Z-]+(?:\s*=| \[\w+\])|\n\s*\[|$)",
    re.DOTALL,
)


def fix_toml(file_path: Path) -> bool:
    content = file_path.read_text(encoding="utf-8")

    def replacer(match: re.Match[str]) -> str:
        prefix = match.group(1)
        value = match.group(2).strip()

        while value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        while value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        value = value.strip('"').strip("'")
        value = value.replace('"""', '"')
        return f'{prefix}"""{value}"""'

    new_content = DESCRIPTION_PATTERN.sub(replacer, content)
    if new_content == content:
        return False

    file_path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {file_path}")
    return True


def main() -> None:
    for path in Path("integrations").rglob("pyproject.toml"):
        fix_toml(path)


if __name__ == "__main__":
    main()
