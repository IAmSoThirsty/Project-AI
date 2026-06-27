from __future__ import annotations

import importlib.util
from pathlib import Path

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
