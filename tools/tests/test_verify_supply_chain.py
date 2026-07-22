"""Tests for the independent supply-chain verifier.

Fixtures are the real manifest shapes captured from ghcr.io on 2026-07-20, not
invented ones. The subject-digest binding test is the load-bearing case: a
signature that is valid but bound to a different image is the failure mode that
signature checking exists to catch.

No test here touches the network. The live registry check is exercised by
``uv run python tools/verify_supply_chain.py`` and recorded in the evidence
bundle; unit tests must stay hermetic.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).parents[1] / "verify_supply_chain.py"
SPEC = importlib.util.spec_from_file_location("verify_supply_chain", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

POLICY_PATH = Path(__file__).parents[1] / "supply_chain_policy.json"

API_DIGEST = "sha256:e878d233dd09535aa5b6356612eb0ecfd169bb98ebf751264284eec44276e502"
REFERRER_DIGEST = "sha256:15538d22aacecda9a2a24bffa8ccaecb934822ca0ba35716140052c3b4df5618"
BUNDLE_TYPE = "application/vnd.dev.sigstore.bundle.v0.3+json"


@pytest.fixture  # type: ignore[untyped-decorator]
def policy() -> dict[str, Any]:
    loaded: dict[str, Any] = MODULE.load_policy(POLICY_PATH)
    return loaded


def _fallback_index() -> dict[str, Any]:
    """The referrers fallback tag index, exactly as ghcr.io serves it.

    Note ``artifactType`` here is the referrer's *config* media type, not the
    sigstore bundle type. ghcr.io populates it that way, so filtering on the index
    would reject a perfectly valid signature.
    """
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "size": 876,
                "digest": REFERRER_DIGEST,
                "artifactType": "application/vnd.oci.empty.v1+json",
            }
        ],
    }


def _referrer_manifest(subject_digest: str = API_DIGEST) -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {"mediaType": "application/vnd.oci.empty.v1+json", "size": 2},
        "layers": [{"mediaType": BUNDLE_TYPE, "size": 11627}],
        "annotations": {
            "dev.sigstore.bundle.content": "dsse-envelope",
            "dev.sigstore.bundle.predicateType": "https://sigstore.dev/cosign/sign/v1",
        },
        "subject": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "size": 856,
            "digest": subject_digest,
        },
        "artifactType": BUNDLE_TYPE,
    }


def _fetchers(
    index: dict[str, Any],
    referrer: dict[str, Any] | None,
    *,
    legacy_status: int = 404,
) -> tuple[Any, Any, Any]:
    def fetch_json(url: str, token: str | None, accept: str | None) -> Any:
        if url.endswith(REFERRER_DIGEST):
            if referrer is None:
                raise MODULE.SupplyChainVerificationError("referrer missing")
            return referrer
        return index

    def fetch_status(url: str, token: str | None, accept: str | None) -> int:
        return legacy_status

    def token_factory(registry: str, repository: str) -> str:
        return "test-token"

    return fetch_json, fetch_status, token_factory


def _layout(**kwargs: Any) -> dict[str, Any]:
    policy = MODULE.load_policy(POLICY_PATH)
    index = kwargs.pop("index", _fallback_index())
    referrer = kwargs.pop("referrer", _referrer_manifest())
    legacy_status = kwargs.pop("legacy_status", 404)
    fetch_json, fetch_status, token_factory = _fetchers(
        index, referrer, legacy_status=legacy_status
    )
    record: dict[str, Any] = MODULE.verify_signature_layout(
        policy,
        kwargs.pop("component", "api"),
        kwargs.pop("digest", API_DIGEST),
        fetch_json=fetch_json,
        fetch_status=fetch_status,
        token_factory=token_factory,
    )
    return record


# --------------------------------------------------------------------------------
# Policy
# --------------------------------------------------------------------------------


def test_policy_loads_and_declares_eight_images(policy: dict[str, Any]) -> None:
    assert len(policy["image_components"]) == 8
    assert policy["cosign"]["major"] == 3
    assert "@sha256:" in policy["cosign"]["verifier_image"]


def test_policy_rejects_unanchored_identity_regexp(tmp_path: Path) -> None:
    document = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    document["identity"]["approved_release_identity_regexp"] = (
        "^https://github[.]com/IAmSoThirsty/Project-AI/[.]github/workflows/publish[.]yaml@.*$"
    )
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(MODULE.SupplyChainVerificationError, match="anchor the git ref"):
        MODULE.load_policy(path)


# --------------------------------------------------------------------------------
# Layer B: registry layout
# --------------------------------------------------------------------------------


def test_layout_accepts_real_ghcr_shape() -> None:
    record = _layout()
    assert record["subject_digest_bound"] is True
    assert record["artifact_type"] == BUNDLE_TYPE
    assert record["legacy_sig_tag_present"] is False


def test_layout_rejects_subject_digest_mismatch() -> None:
    """A signature bound to a different image must never be accepted."""
    other = "sha256:" + "b" * 64
    with pytest.raises(MODULE.SupplyChainVerificationError, match="does not cover this image"):
        _layout(referrer=_referrer_manifest(subject_digest=other))


def test_layout_rejects_missing_subject() -> None:
    referrer = _referrer_manifest()
    del referrer["subject"]
    with pytest.raises(MODULE.SupplyChainVerificationError, match="not bound to any image"):
        _layout(referrer=referrer)


def test_layout_rejects_wrong_artifact_type() -> None:
    referrer = _referrer_manifest()
    referrer["artifactType"] = "application/vnd.oci.empty.v1+json"
    with pytest.raises(MODULE.SupplyChainVerificationError, match="no referrer manifest"):
        _layout(referrer=referrer)


def test_layout_rejects_missing_bundle_layer() -> None:
    referrer = _referrer_manifest()
    referrer["layers"] = [{"mediaType": "application/octet-stream", "size": 1}]
    with pytest.raises(MODULE.SupplyChainVerificationError, match=r"no .* layer"):
        _layout(referrer=referrer)


def test_layout_rejects_wrong_bundle_predicate_type() -> None:
    referrer = _referrer_manifest()
    referrer["annotations"]["dev.sigstore.bundle.predicateType"] = "https://example.invalid/x"
    with pytest.raises(MODULE.SupplyChainVerificationError, match="predicateType"):
        _layout(referrer=referrer)


def test_layout_rejects_unexpected_legacy_sig_tag() -> None:
    """A legacy .sig tag means the signing format drifted from the declared policy."""
    with pytest.raises(
        MODULE.SupplyChainVerificationError, match=r"legacy .* unexpectedly present"
    ):
        _layout(legacy_status=200)


def test_layout_rejects_empty_referrers_index() -> None:
    with pytest.raises(MODULE.SupplyChainVerificationError, match="no signature referrer"):
        _layout(index={"schemaVersion": 2, "manifests": []})


# --------------------------------------------------------------------------------
# Layer A: cosign
# --------------------------------------------------------------------------------


def _completed(
    returncode: int, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["cosign"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def test_cosign_accepts_verified_output(policy: dict[str, Any]) -> None:
    stdout = (
        f'[{{"critical":{{"image":{{"docker-manifest-digest":"{API_DIGEST}"}}}}}}]\n'
        "The code-signing certificate was verified using trusted certificate authority certificates"
    )
    record = MODULE.verify_signature_cosign(
        policy, "api", API_DIGEST, identity_regexp="^x$", runner=lambda cmd: _completed(0, stdout)
    )
    assert record["result"] == "verified"
    assert record["digest"] == API_DIGEST


def test_cosign_rejects_nonzero_exit(policy: dict[str, Any]) -> None:
    with pytest.raises(MODULE.SupplyChainVerificationError, match="signature verification failed"):
        MODULE.verify_signature_cosign(
            policy,
            "api",
            API_DIGEST,
            identity_regexp="^x$",
            runner=lambda cmd: _completed(1, "", "no matching signatures"),
        )


def test_cosign_rejects_zero_exit_without_certificate_confirmation(policy: dict[str, Any]) -> None:
    """A zero exit code is not evidence. This is the exact 2026-07-20 failure mode."""
    with pytest.raises(
        MODULE.SupplyChainVerificationError, match="did not report certificate verification"
    ):
        MODULE.verify_signature_cosign(
            policy,
            "api",
            API_DIGEST,
            identity_regexp="^x$",
            runner=lambda cmd: _completed(0, "looks fine to me"),
        )


def test_cosign_rejects_output_not_bound_to_expected_digest(policy: dict[str, Any]) -> None:
    stdout = (
        '[{"critical":{"image":{"docker-manifest-digest":"sha256:' + "c" * 64 + '"}}}]\n'
        "The code-signing certificate was verified using trusted certificate authority certificates"
    )
    with pytest.raises(MODULE.SupplyChainVerificationError, match="does not bind"):
        MODULE.verify_signature_cosign(
            policy,
            "api",
            API_DIGEST,
            identity_regexp="^x$",
            runner=lambda cmd: _completed(0, stdout),
        )


def test_missing_docker_is_blocked_not_passed(policy: dict[str, Any]) -> None:
    """ "We could not look" must never be reported as "we looked and it was fine"."""

    def runner(command: Any) -> subprocess.CompletedProcess[str]:
        raise MODULE.SupplyChainBlockedError("docker is not available")

    with pytest.raises(MODULE.SupplyChainBlockedError):
        MODULE.verify_signature_cosign(
            policy, "api", API_DIGEST, identity_regexp="^x$", runner=runner
        )


def test_attestation_absence_is_a_failure(policy: dict[str, Any]) -> None:
    with pytest.raises(
        MODULE.SupplyChainVerificationError, match="no verifiable spdxjson attestation"
    ):
        MODULE.verify_attestation_cosign(
            policy,
            "api",
            API_DIGEST,
            "spdxjson",
            identity_regexp="^x$",
            runner=lambda cmd: _completed(
                1, "", "none of the attestations matched the predicate type"
            ),
        )


# --------------------------------------------------------------------------------
# Identity resolution and coverage
# --------------------------------------------------------------------------------


def test_default_identity_is_the_approved_release_pattern(policy: dict[str, Any]) -> None:
    regexp = MODULE.resolve_identity_regexp(policy, allow_branch_provenance=False)
    assert regexp == policy["identity"]["approved_release_identity_regexp"]
    assert "@.*$" not in regexp


def test_branch_provenance_requires_explicit_opt_in(policy: dict[str, Any]) -> None:
    """The current eight digests were built from an unmerged agent branch."""
    approved = MODULE.resolve_identity_regexp(policy, allow_branch_provenance=False)
    allowed = MODULE.resolve_identity_regexp(policy, allow_branch_provenance=True)
    assert approved != allowed
    # re.escape() escapes the hyphens, so match on unescaped path segments only.
    assert "refs/heads/agent/production" in allowed
    assert "agent/production" not in approved
    assert "tags/v" in approved and "heads/main" in approved


def test_incomplete_digest_set_is_rejected(policy: dict[str, Any]) -> None:
    with pytest.raises(
        MODULE.SupplyChainVerificationError, match="does not cover the declared images"
    ):
        MODULE.verify_all_images(policy, {"api": API_DIGEST}, layers=())


def test_image_reference_rejects_non_digest(policy: dict[str, Any]) -> None:
    with pytest.raises(MODULE.SupplyChainVerificationError, match="invalid digest"):
        MODULE.image_reference(policy, "api", "latest")
