"""Mutation tests for the publish-workflow and supply-chain policy gates.

Before 2026-07-20 ``verify_publish_workflow`` was five substring checks, none of
them signing-related: every cosign step could have been deleted and the gate would
still have passed. The external audit made that concrete -- the workflow reported
success while producing no independently retrievable attestation at all.

Each test below removes exactly one control from the REAL workflow and asserts the
gate notices. If any of these ever starts passing, the gate has lost its teeth.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

MODULE_PATH = Path(__file__).parents[1] / "verify_pre_deployment.py"
SPEC = importlib.util.spec_from_file_location("verify_pre_deployment", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

REPO_ROOT = Path(__file__).parents[2]
PUBLISH_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "publish.yaml"
POLICY_FILE = REPO_ROOT / "tools" / "supply_chain_policy.json"

WILDCARD_IDENTITY = "publish[.]yaml@.*$"
ANCHORED_IDENTITY = "publish[.]yaml@${{ github.ref }}$"


def _real_workflow_text() -> str:
    return PUBLISH_WORKFLOW.read_text(encoding="utf-8")


def _workflow_root(tmp_path: Path, text: str) -> Path:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "publish.yaml").write_text(text, encoding="utf-8")
    return tmp_path


def _mutated_document(mutate: Any) -> str:
    document = yaml.safe_load(_real_workflow_text())
    mutate(document)
    dumped: str = yaml.safe_dump(document, sort_keys=False)
    return dumped


# ---------------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------------


def test_gate_passes_on_the_real_workflow() -> None:
    assert MODULE.verify_publish_workflow(REPO_ROOT) > 5


# ---------------------------------------------------------------------------------
# Signing and attestation production
# ---------------------------------------------------------------------------------


def test_rejects_removed_signing_step(tmp_path: Path) -> None:
    text = _real_workflow_text().replace("sign_and_attest_image.sh", "echo-nothing.sh")
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="must sign and attest"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


def test_rejects_removed_sbom_generation(tmp_path: Path) -> None:
    text = _real_workflow_text().replace("anchore/sbom-action", "anchore/noop-action")
    assert "sbom-action" not in text, "mutation did not remove the SBOM step"
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="must generate an SBOM"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


def test_rejects_missing_id_token_permission(tmp_path: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        del document["jobs"]["build-api"]["permissions"]["id-token"]

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="id-token"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, _mutated_document(mutate)))


def test_rejects_signing_a_tag_instead_of_a_digest(tmp_path: Path) -> None:
    text = _real_workflow_text().replace(
        "steps.build.outputs.digest", "needs.image-metadata.outputs.version"
    )
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="immutable build digest"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


# ---------------------------------------------------------------------------------
# Format pinning and identity anchoring
# ---------------------------------------------------------------------------------


def test_rejects_unpinned_cosign_release(tmp_path: Path) -> None:
    """An unpinned cosign-installer silently follows the latest cosign major.

    That is the root cause of the 2026-07-20 discrepancy: the v2 -> v3 default
    change moved signatures to the referrers format with no repository change.
    """
    text = _real_workflow_text().replace("cosign-release:", "cosign-unpinned:")
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="cosign-release"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


def test_rejects_wildcard_certificate_identity(tmp_path: Path) -> None:
    """A trailing '@.*$' accepts a signature issued to any git ref.

    The workflow used exactly that until 2026-07-20, which is why images built
    from an unmerged agent branch passed its own verification.
    """
    text = _real_workflow_text().replace(ANCHORED_IDENTITY, WILDCARD_IDENTITY)
    assert WILDCARD_IDENTITY in text, "mutation did not apply"
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="anchor the git ref"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


# ---------------------------------------------------------------------------------
# Verification integrity
# ---------------------------------------------------------------------------------


def test_rejects_reintroduced_fake_sbom_job(tmp_path: Path) -> None:
    """The deleted publish-sbom job was named 'Generate and attach SBOMs' and only
    ran echo statements."""

    def mutate(document: dict[str, Any]) -> None:
        document["jobs"]["publish-sbom"] = {
            "name": "Generate and attach SBOMs",
            "runs-on": "ubuntu-latest",
            "if": "always()",
            "steps": [{"run": 'echo "images built with provenance and SBOM attestations"'}],
        }

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="publish-sbom"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, _mutated_document(mutate)))


def test_rejects_conditional_verify_job(tmp_path: Path) -> None:
    """'if: always()' let verify-images report success when every build job failed."""

    def mutate(document: dict[str, Any]) -> None:
        document["jobs"]["verify-images"]["if"] = "always()"

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="must not be conditional"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, _mutated_document(mutate)))


def test_rejects_missing_attestation_verification(tmp_path: Path) -> None:
    text = _real_workflow_text().replace("cosign verify-attestation", "cosign verify")
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="must verify attestations"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


def test_rejects_missing_independent_verifier(tmp_path: Path) -> None:
    """Verifying cosign's output with cosign alone cannot detect a format change."""
    text = _real_workflow_text().replace("verify_supply_chain.py", "verify_nothing.py")
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="independent verifier"):
        MODULE.verify_publish_workflow(_workflow_root(tmp_path, text))


# ---------------------------------------------------------------------------------
# Supply-chain policy gate
# ---------------------------------------------------------------------------------


def test_policy_gate_passes_on_repository() -> None:
    assert MODULE.verify_supply_chain_policy(REPO_ROOT) == 8


def _policy_root(tmp_path: Path, policy: dict[str, Any]) -> Path:
    target = tmp_path / "tools"
    target.mkdir(parents=True, exist_ok=True)
    (target / "supply_chain_policy.json").write_text(json.dumps(policy), encoding="utf-8")
    return tmp_path


def test_policy_gate_rejects_unpinned_verifier_image(tmp_path: Path) -> None:
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    policy["cosign"]["verifier_image"] = "ghcr.io/sigstore/cosign/cosign:v3.1.2"
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="pinned by digest"):
        MODULE.verify_supply_chain_policy(_policy_root(tmp_path, policy))


def test_policy_gate_rejects_wildcard_identity(tmp_path: Path) -> None:
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    policy["identity"]["approved_release_identity_regexp"] = "^https://github[.]com/x@.*$"
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="anchor the git ref"):
        MODULE.verify_supply_chain_policy(_policy_root(tmp_path, policy))


def test_policy_gate_rejects_buildkit_attestations_as_sufficient(tmp_path: Path) -> None:
    """BuildKit in-toto layers are real but no standard verifier reads them."""
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    policy["attestation"]["buildkit_attestations_are_not_sufficient"] = False
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="BuildKit"):
        MODULE.verify_supply_chain_policy(_policy_root(tmp_path, policy))
