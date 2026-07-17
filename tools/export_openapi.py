"""Export the canonical development gateway OpenAPI schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_ai_api import create_app


def export_openapi(output: Path) -> None:
    """Write a stable, source-controlled OpenAPI snapshot."""
    schema = create_app(dois=()).openapi()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/api/openapi-baseline.json"),
        help="Schema output path",
    )
    args = parser.parse_args()
    export_openapi(args.output)


if __name__ == "__main__":
    main()
