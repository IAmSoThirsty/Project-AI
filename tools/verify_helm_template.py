from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from typing import Any, cast

import yaml

REQUIRED_TOP_LEVEL_FIELDS = ("apiVersion", "kind", "metadata")
EXPECTED_PROJECT_IMAGE_COMPONENTS = {
    "api",
    "arbiter-rlp",
    "atlas",
    "docs-portal",
    "genesis",
    "operator-console",
    "proof-portal",
    "swr",
}
SHA256_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


class HelmTemplateVerificationError(ValueError):
    """Raised when rendered Helm output is not a valid offline manifest set."""


def _document_name(document: dict[str, Any], index: int) -> str:
    metadata = document.get("metadata")
    if isinstance(metadata, dict):
        name = metadata.get("name")
        if isinstance(name, str) and name.strip():
            return name
    return f"document #{index}"


def _container_images(document: dict[str, Any]) -> tuple[str, ...]:
    kind = document.get("kind")
    spec = document.get("spec")
    if not isinstance(spec, dict):
        return ()
    pod_spec: object | None = None
    if kind in {"Deployment", "DaemonSet", "StatefulSet", "Job"}:
        template = spec.get("template")
        if isinstance(template, dict):
            pod_spec = template.get("spec")
    elif kind == "CronJob":
        job_template = spec.get("jobTemplate")
        if isinstance(job_template, dict):
            job_spec = job_template.get("spec")
            if isinstance(job_spec, dict):
                template = job_spec.get("template")
                if isinstance(template, dict):
                    pod_spec = template.get("spec")
    if not isinstance(pod_spec, dict):
        return ()
    images: list[str] = []
    for field in ("initContainers", "containers"):
        containers = pod_spec.get(field, ())
        if not isinstance(containers, list):
            continue
        for container in containers:
            if isinstance(container, dict) and isinstance(container.get("image"), str):
                images.append(cast(str, container["image"]))
    return tuple(images)


def verify_documents(
    documents: Iterable[Any],
    *,
    expected_namespace: str | None = None,
) -> int:
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
        namespace = metadata.get("namespace")
        if (
            expected_namespace is not None
            and namespace is not None
            and namespace != expected_namespace
        ):
            raise HelmTemplateVerificationError(
                f"{metadata_name} namespace mismatch: "
                f"expected={expected_namespace!r} actual={namespace!r}"
            )
    if count == 0:
        raise HelmTemplateVerificationError("no Kubernetes manifests were rendered")
    return count


def verify_project_images(
    documents: Iterable[Any],
    *,
    registry: str,
    owner: str,
    tag: str,
) -> None:
    expected = {
        f"{registry}/{owner}/project-ai-{component}:{tag}"
        for component in EXPECTED_PROJECT_IMAGE_COMPONENTS
    }
    actual: set[str] = set()
    for raw_document in documents:
        if isinstance(raw_document, dict):
            for image in _container_images(cast("dict[str, Any]", raw_document)):
                if "project-ai-" in image:
                    actual.add(image)
    if actual != expected:
        raise HelmTemplateVerificationError(
            f"Project-AI image set mismatch: expected={sorted(expected)} actual={sorted(actual)}"
        )


def verify_project_image_digests(
    documents: Iterable[Any],
    *,
    registry: str,
    owner: str,
) -> None:
    prefix = f"{registry}/{owner}/project-ai-"
    components: set[str] = set()
    invalid: list[str] = []
    for raw_document in documents:
        if not isinstance(raw_document, dict):
            continue
        for image in _container_images(cast("dict[str, Any]", raw_document)):
            if not image.startswith(prefix):
                continue
            name_and_digest = image.removeprefix(prefix).split("@", maxsplit=1)
            if len(name_and_digest) != 2 or SHA256_DIGEST.fullmatch(name_and_digest[1]) is None:
                invalid.append(image)
                continue
            components.add(name_and_digest[0])
    if invalid or components != EXPECTED_PROJECT_IMAGE_COMPONENTS:
        raise HelmTemplateVerificationError(
            "Project-AI digest image set mismatch: "
            f"expected_components={sorted(EXPECTED_PROJECT_IMAGE_COMPONENTS)} "
            f"actual_components={sorted(components)} invalid={sorted(invalid)}"
        )


def verify_text(
    rendered: str,
    *,
    expected_namespace: str | None = None,
    project_image: tuple[str, str, str] | None = None,
    project_digest_owner: tuple[str, str] | None = None,
) -> int:
    documents = tuple(yaml.safe_load_all(rendered))
    count = verify_documents(documents, expected_namespace=expected_namespace)
    if project_image is not None:
        registry, owner, tag = project_image
        verify_project_images(documents, registry=registry, owner=owner, tag=tag)
    if project_digest_owner is not None:
        registry, owner = project_digest_owner
        verify_project_image_digests(documents, registry=registry, owner=owner)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-namespace")
    parser.add_argument("--project-image-registry")
    parser.add_argument("--project-image-owner")
    parser.add_argument("--project-image-tag")
    parser.add_argument("--require-project-image-digests", action="store_true")
    arguments = parser.parse_args()
    image_arguments = (
        arguments.project_image_registry,
        arguments.project_image_owner,
        arguments.project_image_tag,
    )
    if arguments.project_image_tag and not all(image_arguments):
        parser.error("all three --project-image-* arguments are required for tag verification")
    if arguments.require_project_image_digests and not all(image_arguments[:2]):
        parser.error("--project-image-registry and --project-image-owner are required for digests")
    if arguments.require_project_image_digests and arguments.project_image_tag:
        parser.error("tag and digest image verification modes are mutually exclusive")
    project_image = cast(
        "tuple[str, str, str] | None", image_arguments if all(image_arguments) else None
    )
    project_digest_owner = cast(
        "tuple[str, str] | None",
        image_arguments[:2] if arguments.require_project_image_digests else None,
    )
    try:
        count = verify_text(
            sys.stdin.read(),
            expected_namespace=arguments.expected_namespace,
            project_image=project_image,
            project_digest_owner=project_digest_owner,
        )
    except (HelmTemplateVerificationError, yaml.YAMLError) as error:
        print(f"helm template verification failed: {error}", file=sys.stderr)
        return 1
    print(f"helm template verification passed: {count} manifest(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
