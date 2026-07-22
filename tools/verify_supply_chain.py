#!/usr/bin/env python3
"""Independently verify container image signatures and attestations against the registry.

This verifier exists because the 2026-07-20 external audit reported "no signatures found"
for all eight image digests while the publish workflow reported success. Both observations
were locally correct: the workflow verified its own output with the same cosign binary that
produced it, and the auditor verified with cosign 2.6.0, which cannot read the cosign 3.x
bundle format the workflow actually writes.

Two independent verification layers are therefore implemented, and both must pass:

Layer A (``--layer cosign``) runs cosign from an OCI image pinned by digest -- a different
distribution channel from the ``sigstore/cosign-installer`` GitHub-release tarball used by
the signer. It asserts cryptographic validity, certificate identity, and OIDC issuer.

Layer B (``--layer registry``) speaks the plain OCI distribution API and asserts the storage
layout directly, sharing no code with cosign. If cosign changes its default storage format
again, Layer B breaks loudly instead of moving silently with it.

Every check is performed against an immutable digest. Tags are never verified: a tag is a
mutable pointer and can resolve to a manifest other than the one that was signed.

Absence of network access or Docker is reported as BLOCKED and exits non-zero. It is never
reported as a pass.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "tools" / "supply_chain_policy.json"

SHA256_DIGEST = re.compile(r"\Asha256:[0-9a-f]{64}\Z")
_TOKEN_URL = "https://{registry}/token?scope=repository:{repository}:pull&service={registry}"
_MANIFEST_ACCEPT = ", ".join(
    (
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    )
)

Runner = Callable[[Sequence[str]], "subprocess.CompletedProcess[str]"]


class SupplyChainVerificationError(ValueError):
    """Raised when registry supply-chain evidence does not satisfy the declared policy."""


class SupplyChainBlockedError(SupplyChainVerificationError):
    """Raised when a check could not be executed at all.

    Kept distinct from a verification failure so that "we could not look" is never
    reported, recorded, or mistaken as "we looked and it was fine".
    """


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SupplyChainVerificationError(message)


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    """Load and structurally validate the supply-chain policy document."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:  # pragma: no cover - filesystem failure
        raise SupplyChainBlockedError(f"cannot read supply-chain policy {path}: {error}") from error
    try:
        policy = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SupplyChainVerificationError(
            f"supply-chain policy is not valid JSON: {error}"
        ) from error
    _require(isinstance(policy, dict), "supply-chain policy must be a JSON object")
    for key in ("registry", "owner", "image_components", "cosign", "signature", "identity"):
        _require(key in policy, f"supply-chain policy missing {key}")
    components = policy["image_components"]
    _require(
        isinstance(components, list)
        and len(components) == 8
        and all(isinstance(c, str) for c in components),
        "supply-chain policy must declare exactly eight image components",
    )
    identity = policy["identity"]
    approved = identity.get("approved_release_identity_regexp")
    if not isinstance(approved, str) or not (approved.startswith("^") and approved.endswith("$")):
        raise SupplyChainVerificationError(
            "approved_release_identity_regexp must be fully anchored"
        )
    _require(
        "@.*$" not in approved and "@[.]*$" not in approved,
        "approved_release_identity_regexp must anchor the git ref; "
        "a trailing '@.*$' accepts any branch",
    )
    return cast(dict[str, Any], policy)


def image_reference(policy: dict[str, Any], component: str, digest: str) -> str:
    """Build an immutable, digest-pinned image reference."""
    _require(SHA256_DIGEST.match(digest) is not None, f"invalid digest for {component}: {digest}")
    return f"{policy['registry']}/{policy['owner']}/project-ai-{component}@{digest}"


# --------------------------------------------------------------------------------------
# Layer B: plain OCI distribution API. No cosign, no Docker.
# --------------------------------------------------------------------------------------


def _http_json(url: str, token: str | None = None, accept: str | None = None) -> Any:
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    if accept:
        request.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise SupplyChainVerificationError(
            f"registry returned HTTP {error.code} for {url}"
        ) from error
    except urllib.error.URLError as error:
        raise SupplyChainBlockedError(f"cannot reach registry {url}: {error.reason}") from error


def _http_status(url: str, token: str | None = None, accept: str | None = None) -> int:
    request = urllib.request.Request(url, method="GET")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    if accept:
        request.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status)
    except urllib.error.HTTPError as error:
        return int(error.code)
    except urllib.error.URLError as error:
        raise SupplyChainBlockedError(f"cannot reach registry {url}: {error.reason}") from error


def anonymous_pull_token(registry: str, repository: str) -> str:
    """Obtain an anonymous pull token.

    Anonymous tokens are used deliberately: they prove the evidence is retrievable
    without privileged credentials, which is what "independently retrievable" means.
    """
    payload = _http_json(_TOKEN_URL.format(registry=registry, repository=repository))
    token = payload.get("token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token:
        raise SupplyChainBlockedError(f"no anonymous pull token issued for {repository}")
    return token


def verify_signature_layout(
    policy: dict[str, Any],
    component: str,
    digest: str,
    *,
    fetch_json: Callable[[str, str | None, str | None], Any] = _http_json,
    fetch_status: Callable[[str, str | None, str | None], int] = _http_status,
    token_factory: Callable[[str, str], str] = anonymous_pull_token,
) -> dict[str, Any]:
    """Assert the signature storage layout directly, without cosign.

    Checks, in order: the legacy ``.sig`` tag is absent exactly as the policy declares;
    the referrers fallback tag exists; it advertises the sigstore bundle artifact type;
    and -- the check that actually matters -- the referring manifest's ``subject.digest``
    equals the digest under test, so a signature cannot be borrowed from another image.
    """
    registry = policy["registry"]
    signature = policy["signature"]
    repository = f"{policy['owner']}/project-ai-{component}"
    digest_hex = digest.split(":", 1)[1]
    fallback_tag = signature["fallback_tag_pattern"].format(digest_hex=digest_hex)
    token = token_factory(registry, repository)
    base = f"https://{registry}/v2/{repository}"

    if signature.get("legacy_sig_tag_expected_absent"):
        status = fetch_status(f"{base}/manifests/{fallback_tag}.sig", token, _MANIFEST_ACCEPT)
        _require(
            status == 404,
            f"{component}: legacy {fallback_tag}.sig tag unexpectedly present (HTTP {status}); "
            "the declared cosign v3 bundle format does not write it, so its presence means "
            "the signing format drifted from policy",
        )

    index = fetch_json(f"{base}/manifests/{fallback_tag}", token, _MANIFEST_ACCEPT)
    _require(
        isinstance(index, dict),
        f"{component}: referrers fallback tag {fallback_tag} is not a manifest",
    )
    manifests = index.get("manifests")
    _require(
        isinstance(manifests, list) and len(manifests) > 0,
        f"{component}: no signature referrer found at {fallback_tag}",
    )

    expected_type = signature["artifact_type"]

    # The index entry's artifactType is NOT authoritative. ghcr.io populates it from the
    # referrer's *config* mediaType (application/vnd.oci.empty.v1+json for a sigstore
    # bundle), not from the referrer manifest's own artifactType field. Filtering on the
    # index would therefore reject a perfectly valid signature. Fetch each referrer and
    # read its real artifactType.
    referrer_digest: str | None = None
    manifest: dict[str, Any] | None = None
    seen_types: list[Any] = []
    for entry in manifests:
        if not isinstance(entry, dict):
            continue
        candidate_digest = entry.get("digest")
        if not isinstance(candidate_digest, str) or SHA256_DIGEST.match(candidate_digest) is None:
            continue
        candidate = fetch_json(f"{base}/manifests/{candidate_digest}", token, _MANIFEST_ACCEPT)
        if not isinstance(candidate, dict):
            continue
        seen_types.append(candidate.get("artifactType"))
        if candidate.get("artifactType") == expected_type:
            referrer_digest = candidate_digest
            manifest = candidate
            break

    _require(
        manifest is not None and referrer_digest is not None,
        f"{component}: no referrer manifest with artifactType {expected_type} at {fallback_tag}; "
        f"found {seen_types}",
    )
    assert manifest is not None and referrer_digest is not None  # narrowed by _require
    layers = manifest.get("layers")
    _require(
        isinstance(layers, list)
        and any(
            isinstance(layer, dict) and layer.get("mediaType") == signature["bundle_media_type"]
            for layer in layers
        ),
        f"{component}: signature manifest has no {signature['bundle_media_type']} layer",
    )
    annotations = manifest.get("annotations")
    if not isinstance(annotations, dict):
        raise SupplyChainVerificationError(f"{component}: signature manifest has no annotations")
    predicate_type = annotations.get("dev.sigstore.bundle.predicateType")
    _require(
        predicate_type == signature["bundle_predicate_type"],
        f"{component}: bundle predicateType is {predicate_type!r}, "
        f"expected {signature['bundle_predicate_type']!r}",
    )

    subject = manifest.get("subject")
    if not isinstance(subject, dict):
        raise SupplyChainVerificationError(
            f"{component}: signature manifest has no subject -- it is not bound to any image"
        )
    subject_digest = subject.get("digest")
    _require(
        subject_digest == digest,
        f"{component}: signature subject digest {subject_digest!r} does not match the image digest {digest!r}; "
        "the signature does not cover this image",
    )

    return {
        "component": component,
        "digest": digest,
        "fallback_tag": fallback_tag,
        "artifact_type": expected_type,
        "referrer_digest": referrer_digest,
        "subject_digest_bound": True,
        "legacy_sig_tag_present": False,
    }


# --------------------------------------------------------------------------------------
# Layer A: pinned cosign container.
# --------------------------------------------------------------------------------------


def _default_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command), capture_output=True, text=True, timeout=300, check=False
        )
    except FileNotFoundError as error:
        raise SupplyChainBlockedError(f"docker is not available: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise SupplyChainBlockedError(f"cosign verification timed out: {error}") from error


def _cosign_command(policy: dict[str, Any], args: Sequence[str]) -> list[str]:
    return ["docker", "run", "--rm", policy["cosign"]["verifier_image"], *args]


def verify_signature_cosign(
    policy: dict[str, Any],
    component: str,
    digest: str,
    *,
    identity_regexp: str,
    runner: Runner = _default_runner,
) -> dict[str, Any]:
    """Verify the signature cryptographically using the digest-pinned cosign image."""
    reference = image_reference(policy, component, digest)
    identity = policy["identity"]
    result = runner(
        _cosign_command(
            policy,
            (
                "verify",
                "--certificate-identity-regexp",
                identity_regexp,
                "--certificate-oidc-issuer",
                identity["oidc_issuer"],
                reference,
            ),
        )
    )
    combined = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        raise SupplyChainVerificationError(
            f"{component}: cosign signature verification failed: {combined.strip().splitlines()[0] if combined.strip() else 'no output'}"
        )
    _require(
        "code-signing certificate was verified" in combined,
        f"{component}: cosign exited 0 but did not report certificate verification; "
        "refusing to treat a zero exit code as evidence",
    )
    _require(
        digest in result.stdout,
        f"{component}: cosign output does not bind the verified signature to {digest}",
    )
    return {
        "component": component,
        "digest": digest,
        "reference": reference,
        "verifier": f"cosign {policy['cosign']['verifier_image_version']} ({policy['cosign']['verifier_image']})",
        "identity_regexp": identity_regexp,
        "oidc_issuer": identity["oidc_issuer"],
        "method": "cosign verify --certificate-identity-regexp (digest-pinned)",
        "result": "verified",
    }


def verify_attestation_cosign(
    policy: dict[str, Any],
    component: str,
    digest: str,
    predicate_type: str,
    *,
    identity_regexp: str,
    runner: Runner = _default_runner,
) -> dict[str, Any]:
    """Verify a cosign attestation of the given predicate type."""
    reference = image_reference(policy, component, digest)
    identity = policy["identity"]
    result = runner(
        _cosign_command(
            policy,
            (
                "verify-attestation",
                "--type",
                predicate_type,
                "--certificate-identity-regexp",
                identity_regexp,
                "--certificate-oidc-issuer",
                identity["oidc_issuer"],
                reference,
            ),
        )
    )
    combined = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0 or "code-signing certificate was verified" not in combined:
        first = combined.strip().splitlines()[0] if combined.strip() else "no output"
        raise SupplyChainVerificationError(
            f"{component}: no verifiable {predicate_type} attestation for {digest}: {first}"
        )
    return {
        "component": component,
        "digest": digest,
        "predicate_type": predicate_type,
        "verifier": f"cosign {policy['cosign']['verifier_image_version']}",
        "method": "cosign verify-attestation (digest-pinned)",
        "result": "verified",
    }


# --------------------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------------------


def resolve_identity_regexp(policy: dict[str, Any], *, allow_branch_provenance: bool) -> str:
    """Return the certificate identity regexp to enforce.

    Defaults to the approved release identity (release tags and ``main`` only). The
    current eight candidate digests were built from an unmerged agent branch and do NOT
    satisfy it; verifying them therefore requires an explicit opt-in that is recorded in
    the emitted evidence.
    """
    identity = policy["identity"]
    if not allow_branch_provenance:
        return str(identity["approved_release_identity_regexp"])
    actual = policy.get("current_candidate", {}).get("actual_identity")
    _require(
        isinstance(actual, str) and actual.startswith("https://github.com/"),
        "policy declares no current_candidate.actual_identity to allow",
    )
    return "^" + re.escape(str(actual)) + "$"


def verify_all_images(
    policy: dict[str, Any],
    digests: dict[str, str],
    *,
    layers: Sequence[str] = ("registry", "cosign"),
    require_attestations: bool = False,
    allow_branch_provenance: bool = False,
    runner: Runner = _default_runner,
) -> dict[str, Any]:
    """Verify every declared image component. Fails closed on the first bad image."""
    expected = set(policy["image_components"])
    provided = set(digests)
    _require(
        provided == expected,
        f"digest set does not cover the declared images; missing={sorted(expected - provided)} "
        f"unexpected={sorted(provided - expected)}",
    )

    identity_regexp = resolve_identity_regexp(
        policy, allow_branch_provenance=allow_branch_provenance
    )
    signature_records: list[dict[str, Any]] = []
    layout_records: list[dict[str, Any]] = []
    attestation_records: list[dict[str, Any]] = []

    for component in sorted(expected):
        digest = digests[component]
        if "registry" in layers:
            layout_records.append(verify_signature_layout(policy, component, digest))
        if "cosign" in layers:
            signature_records.append(
                verify_signature_cosign(
                    policy, component, digest, identity_regexp=identity_regexp, runner=runner
                )
            )
        if require_attestations:
            for predicate_type in policy["attestation"]["predicate_types"].values():
                attestation_records.append(
                    verify_attestation_cosign(
                        policy,
                        component,
                        digest,
                        predicate_type,
                        identity_regexp=identity_regexp,
                        runner=runner,
                    )
                )

    return {
        "policy_version": policy["policy_version"],
        "layers": list(layers),
        "allow_branch_provenance": allow_branch_provenance,
        "identity_regexp": identity_regexp,
        "meets_approved_release_identity": not allow_branch_provenance,
        "images_verified": len(expected),
        "signature_layout": layout_records,
        "signature_verifications": signature_records,
        "sbom_attestations": attestation_records,
    }


def _load_digests(path: Path) -> dict[str, str]:
    """Load the eight digests from the successor evidence record.

    Accepts the mapping either at the top level or nested under ``evidence``, which is
    where ``REMOTE_SUCCESSOR_EVIDENCE.json`` keeps it.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise SupplyChainBlockedError(f"cannot read digest source {path}: {error}") from error
    digests = payload.get("image_digests")
    if not isinstance(digests, dict):
        evidence = payload.get("evidence")
        if isinstance(evidence, dict):
            digests = evidence.get("image_digests")
    _require(isinstance(digests, dict), f"{path} has no image_digests mapping")
    return {str(k): str(v) for k, v in digests.items()}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--digests",
        type=Path,
        default=ROOT / "docs" / "operations" / "cab" / "REMOTE_SUCCESSOR_EVIDENCE.json",
        help="JSON file containing an image_digests mapping",
    )
    parser.add_argument(
        "--layer",
        action="append",
        choices=("registry", "cosign"),
        help="verification layer to run (default: both)",
    )
    parser.add_argument("--require-attestations", action="store_true")
    parser.add_argument(
        "--allow-branch-provenance",
        action="store_true",
        help="accept signatures issued to a non-release git ref (recorded in the output)",
    )
    parser.add_argument("--json", action="store_true", help="emit the evidence record as JSON")
    args = parser.parse_args(argv)

    try:
        policy = load_policy(args.policy)
        digests = _load_digests(args.digests)
        report = verify_all_images(
            policy,
            digests,
            layers=tuple(args.layer) if args.layer else ("registry", "cosign"),
            require_attestations=args.require_attestations,
            allow_branch_provenance=args.allow_branch_provenance,
        )
    except SupplyChainBlockedError as error:
        print(f"BLOCKED: supply-chain verification could not execute: {error}", file=sys.stderr)
        return 2
    except SupplyChainVerificationError as error:
        print(f"FAIL: supply-chain verification failed: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for record in report["signature_layout"]:
            print(f"PASS layout    {record['component']:<17} {record['digest']} (subject-bound)")
        for record in report["signature_verifications"]:
            print(f"PASS signature {record['component']:<17} {record['digest']}")
        for record in report["sbom_attestations"]:
            print(f"PASS attest    {record['component']:<17} {record['predicate_type']}")
        print(f"verified {report['images_verified']} images")
        if report["allow_branch_provenance"]:
            print(
                "WARNING: --allow-branch-provenance was used; these signatures do NOT meet the "
                "approved release identity and are not release provenance",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
