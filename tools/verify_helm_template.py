from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import Any, cast

import yaml

REQUIRED_TOP_LEVEL_FIELDS = ("apiVersion", "kind", "metadata")


class HelmTemplateVerificationError(ValueError):
    """Raised when rendered Helm output is not a valid offline manifest set."""


def _document_name(document: dict[str, Any], index: int) -> str:
    metadata = document.get("metadata")
    if isinstance(metadata, dict):
        name = metadata.get("name")
        if isinstance(name, str) and name.strip():
            return name
    return f"document #{index}"


def verify_documents(documents: Iterable[Any]) -> int:
    count = 0
    for index, raw_document in enumerate(documents, start=1):
        if raw_document is None:
            continue
        if not isinstance(raw_document, dict):
            raise HelmTemplateVerificationError(
                f"document #{index} must be a mapping, got {type(raw_document).__name__}"
            )
        document = cast("dict[str, Any]", raw_document)
        count += 1
        missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in document]
        if missing:
            document_name = _document_name(document, index)
            raise HelmTemplateVerificationError(
                f"{document_name} missing required field(s): {', '.join(missing)}"
            )
        metadata = document["metadata"]
        if not isinstance(metadata, dict):
            document_name = _document_name(document, index)
            raise HelmTemplateVerificationError(f"{document_name} metadata must be a mapping")
        metadata_name = metadata.get("name")
        if not isinstance(metadata_name, str) or not metadata_name.strip():
            raise HelmTemplateVerificationError(
                f"document #{index} metadata.name must be non-empty"
            )
    if count == 0:
        raise HelmTemplateVerificationError("no Kubernetes manifests were rendered")
    return count


def verify_text(rendered: str) -> int:
    return verify_documents(yaml.safe_load_all(rendered))


def main() -> int:
    try:
        count = verify_text(sys.stdin.read())
    except (HelmTemplateVerificationError, yaml.YAMLError) as error:
        print(f"helm template verification failed: {error}", file=sys.stderr)
        return 1
    print(f"helm template verification passed: {count} manifest(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
