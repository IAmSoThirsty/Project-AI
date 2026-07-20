from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).parents[1] / "verify_helm_template.py"
SPEC = importlib.util.spec_from_file_location("verify_helm_template", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_verify_text_accepts_basic_manifest() -> None:
    rendered = """
apiVersion: v1
kind: Service
metadata:
  name: project-ai
"""
    assert MODULE.verify_text(rendered) == 1


def test_verify_text_rejects_missing_metadata_name() -> None:
    rendered = """
apiVersion: apps/v1
kind: Deployment
metadata: {}
"""
    with pytest.raises(MODULE.HelmTemplateVerificationError, match=r"metadata\.name"):
        MODULE.verify_text(rendered)


def test_verify_text_rejects_empty_render() -> None:
    with pytest.raises(MODULE.HelmTemplateVerificationError, match="no Kubernetes"):
        MODULE.verify_text("")


def test_verify_text_rejects_explicit_cross_namespace_resource() -> None:
    rendered = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: wrong-namespace
  namespace: other
"""
    with pytest.raises(MODULE.HelmTemplateVerificationError, match="namespace mismatch"):
        MODULE.verify_text(rendered, expected_namespace="project-ai-prod")


def test_verify_project_images_requires_exact_eight_image_set() -> None:
    documents = []
    for component in sorted(MODULE.EXPECTED_PROJECT_IMAGE_COMPONENTS):
        documents.append(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": component},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": component,
                                    "image": f"ghcr.io/iamsothirsty/project-ai-{component}:v0.0.2",
                                }
                            ]
                        }
                    }
                },
            }
        )

    MODULE.verify_project_images(
        documents,
        registry="ghcr.io",
        owner="iamsothirsty",
        tag="v0.0.2",
    )
    documents.pop()
    with pytest.raises(MODULE.HelmTemplateVerificationError, match="image set mismatch"):
        MODULE.verify_project_images(
            documents,
            registry="ghcr.io",
            owner="iamsothirsty",
            tag="v0.0.2",
        )


def test_verify_project_image_digests_requires_all_components_and_sha256() -> None:
    documents: list[dict[str, Any]] = []
    for component in sorted(MODULE.EXPECTED_PROJECT_IMAGE_COMPONENTS):
        documents.append(
            {
                "kind": "Deployment",
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "image": "ghcr.io/iamsothirsty/project-ai-"
                                    f"{component}@sha256:{'a' * 64}"
                                }
                            ]
                        }
                    }
                },
            }
        )

    MODULE.verify_project_image_digests(
        documents,
        registry="ghcr.io",
        owner="iamsothirsty",
    )
    documents[0]["spec"]["template"]["spec"]["containers"][0]["image"] = (
        "ghcr.io/iamsothirsty/project-ai-api:latest"
    )
    with pytest.raises(MODULE.HelmTemplateVerificationError, match="digest image set mismatch"):
        MODULE.verify_project_image_digests(
            documents,
            registry="ghcr.io",
            owner="iamsothirsty",
        )
