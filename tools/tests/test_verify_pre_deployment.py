from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).parents[1] / "verify_pre_deployment.py"
SPEC = importlib.util.spec_from_file_location("verify_pre_deployment", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_candidate_manifest(tmp_path: Path) -> str:
    manifest = (
        tmp_path / "packages" / "thirstys-standard-v3q" / "thirstys-standard-v3q.manifest.yaml"
    )
    manifest.parent.mkdir(parents=True)
    content = b"fixture-manifest"
    manifest.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


_IMAGE_NAMES = (
    "api",
    "docs-portal",
    "proof-portal",
    "operator-console",
    "swr",
    "atlas",
    "arbiter-rlp",
    "genesis",
)


def _complete_verified_evidence(manifest_sha: str) -> dict[str, Any]:
    """A fully-verified successor evidence document the gate accepts.

    Baseline for negative tests: each poisons exactly one field to prove a
    specific fabrication cannot pass the strict ``status: verified`` branch.
    """
    digest = "sha256:" + "a" * 64
    return {
        "schema_version": "1.0",
        "candidate_version": "0.0.3",
        "candidate_commit": "c" * 40,
        "candidate_manifest_sha256": manifest_sha,
        "status": "verified",
        "review_only": False,
        "required": {
            field: True
            for field in (
                "owner_key_rotation_verified",
                "exact_manifest_ratification_verified",
                "external_proof_custody_verified",
                "commit_pushed",
                "successor_ci_green",
                "image_signatures_verified",
                "release_provenance_verified",
                "sbom_attestations_verified",
                "production_overlay_verified",
                "remote_backup_verified",
                "monitoring_crds_verified",
                "dependabot_disposition_verified",
                "target_environment_approved",
                "rollback_rehearsal_verified",
            )
        },
        "evidence": {
            "owner_key_rotation_record": "rotation.json",
            "exact_manifest_ratification_record": "ratification.json",
            "proof_custody_record": "proof-custody.json",
            "remote_commit_sha": "c" * 40,
            "remote_ci_runs": ["run-1"],
            "image_digests": {name: digest for name in _IMAGE_NAMES},
            "signature_verifications": [
                {
                    "image": name,
                    "digest": digest,
                    "verifier": "cosign v3.1.2",
                    "method": "cosign verify (digest-pinned)",
                    "result": "verified",
                }
                for name in _IMAGE_NAMES
            ],
            "sbom_attestations": [
                {
                    "image": name,
                    "digest": digest,
                    "predicate_type": "spdxjson",
                    "verifier": "cosign v3.1.2",
                    "method": "cosign verify-attestation (digest-pinned)",
                    "result": "verified",
                }
                for name in _IMAGE_NAMES
            ],
            "production_overlay_record": "overlay.json",
            "remote_backup_record": "backup.json",
            "monitoring_crds_record": "crds.json",
            "dependabot_disposition_record": "dependabot.json",
            "target_environment_record": "target.json",
            "rollback_rehearsal_record": "rollback.json",
        },
    }


def _write_evidence(tmp_path: Path, evidence: dict[str, Any]) -> Path:
    path = tmp_path / "docs" / "operations" / "cab" / "REMOTE_SUCCESSOR_EVIDENCE.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(evidence), encoding="utf-8")
    return path


def test_current_repo_pre_deployment_gate_reports_owner_key_blocker() -> None:
    owner_key_present = (
        MODULE.ROOT / "packages" / "thirstys-standard-v3q" / "owner-private.json"
    ).exists()
    with pytest.raises(MODULE.PreDeploymentVerificationError) as error:
        MODULE.verify_all(MODULE.ROOT)
    if owner_key_present:
        assert "must be absent from the checkout" in str(error.value)
    else:
        assert "remote successor evidence is not verified" in str(error.value)


def test_pre_deployment_report_lists_all_current_blockers() -> None:
    report = MODULE.collect_pre_deployment_report(MODULE.ROOT)

    owner_key_present = (
        MODULE.ROOT / "packages" / "thirstys-standard-v3q" / "owner-private.json"
    ).exists()
    if owner_key_present:
        assert any(
            result.startswith("FAIL Docker secret exclusions:")
            and "owner-controlled signing material" in result
            for result in report
        )
    assert any(
        result.startswith("FAIL remote successor evidence:")
        and "not verified" in result
        and "owner_key_rotation_verified" in result
        and "rollback_rehearsal_verified" in result
        for result in report
    )
    assert any(result.startswith("PASS document scope boundaries:") for result in report)


def test_required_files_include_current_successor_cab_pack() -> None:
    assert (
        "docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md"
        in MODULE.REQUIRED_FILES
    )
    assert "docs/operations/cab/OPTIONAL_SERVICE_USAGE.json" in MODULE.REQUIRED_FILES
    assert "docs/operations/cab/OPTIONAL_SERVICE_USAGE.md" in MODULE.REQUIRED_FILES


def test_optional_service_boundaries_pass_repository() -> None:
    assert MODULE.verify_optional_service_boundaries(MODULE.ROOT) == 14


def test_optional_service_boundary_rejects_core_dependency(tmp_path: Path) -> None:
    source = tmp_path / "fallback.md"
    source.write_text("local source", encoding="utf-8")
    services = []
    for service_id in sorted(MODULE.EXPECTED_OPTIONAL_SERVICES):
        services.append(
            {
                "id": service_id,
                "purpose": "fixture",
                "classification": "operator_tool",
                "required_for_core": service_id == "vercel",
                "required_for_governance": False,
                "replaceable": True,
                "canonical_local_source": "fallback.md",
                "outage_behavior": "continue_locally",
                "activation": "explicit_operator_action",
            }
        )
    manifest = tmp_path / "docs" / "operations" / "cab" / "OPTIONAL_SERVICE_USAGE.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "policy": "optional_replaceable",
                "canonical_authority": "local_repo",
                "services": services,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="core dependency"):
        MODULE.verify_optional_service_boundaries(tmp_path)


def test_current_reference_documents_have_deployment_boundaries() -> None:
    assert MODULE.verify_document_scope_boundaries(MODULE.ROOT) == 56


def test_reference_document_without_boundary_is_rejected(tmp_path: Path) -> None:
    for relative_path in MODULE.DOCUMENT_SCOPE_BOUNDARY_FILES:
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("reference text", encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="deployment boundary"):
        MODULE.verify_document_scope_boundaries(tmp_path)


def test_env_example_rejects_real_token(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.example"
    env_file.write_text(
        "\n".join(
            (
                "PROJECT_AI_API_TOKEN=real-token",
                "PROJECT_AI_API_URL=http://127.0.0.1:8000",
                "PROJECT_AI_DESKTOP_SMOKE=1",
                "QT_QPA_PLATFORM=offscreen",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="real API token"):
        MODULE.verify_env_example(tmp_path)


def test_docker_secret_exclusions_require_owner_key_path(tmp_path: Path) -> None:
    (tmp_path / ".dockerignore").write_text(".git\n", encoding="utf-8")

    with pytest.raises(
        MODULE.PreDeploymentVerificationError,
        match="owner-controlled signing material",
    ):
        MODULE.verify_docker_secret_exclusions(tmp_path)


def test_docker_secret_exclusions_accept_owner_key_path(tmp_path: Path) -> None:
    (tmp_path / ".dockerignore").write_text(
        "packages/thirstys-standard-v3q/owner-private.json\n",
        encoding="utf-8",
    )

    assert MODULE.verify_docker_secret_exclusions(tmp_path) == 2


def test_docker_secret_exclusions_reject_present_owner_key(tmp_path: Path) -> None:
    owner_key = tmp_path / "packages" / "thirstys-standard-v3q" / "owner-private.json"
    owner_key.parent.mkdir(parents=True)
    owner_key.write_text("redacted-test-fixture", encoding="utf-8")
    (tmp_path / ".dockerignore").write_text(
        "packages/thirstys-standard-v3q/owner-private.json\n",
        encoding="utf-8",
    )

    with pytest.raises(
        MODULE.PreDeploymentVerificationError,
        match="must be absent from the checkout",
    ):
        MODULE.verify_docker_secret_exclusions(tmp_path)


def test_owner_key_rotation_tool_has_repository_safety_guards() -> None:
    assert MODULE.verify_owner_key_rotation_tool(MODULE.ROOT) == 8


def test_remote_successor_evidence_fails_closed_until_verified(tmp_path: Path) -> None:
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = {
        "schema_version": "1.0",
        "candidate_version": "0.0.3",
        "candidate_commit": "a" * 40,
        "candidate_manifest_sha256": manifest_sha,
        "status": "missing",
        "review_only": True,
        "required": {
            "owner_key_rotation_verified": False,
            "exact_manifest_ratification_verified": False,
            "external_proof_custody_verified": False,
            "commit_pushed": False,
            "successor_ci_green": False,
            "image_signatures_verified": False,
            "release_provenance_verified": False,
            "sbom_attestations_verified": False,
            "production_overlay_verified": False,
            "remote_backup_verified": False,
            "monitoring_crds_verified": False,
            "dependabot_disposition_verified": False,
            "target_environment_approved": False,
            "rollback_rehearsal_verified": False,
        },
        "evidence": {
            "owner_key_rotation_record": None,
            "exact_manifest_ratification_record": None,
            "proof_custody_record": None,
            "remote_commit_sha": None,
            "remote_ci_runs": [],
            "image_digests": {},
            "signature_verifications": [],
            "sbom_attestations": [],
            "production_overlay_record": None,
            "remote_backup_record": None,
            "monitoring_crds_record": None,
            "dependabot_disposition_record": None,
            "target_environment_record": None,
            "rollback_rehearsal_record": None,
        },
    }
    path = tmp_path / "docs" / "operations" / "cab" / "REMOTE_SUCCESSOR_EVIDENCE.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(evidence), encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="not verified"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_remote_successor_evidence_verified_requires_external_records(tmp_path: Path) -> None:
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = {
        "schema_version": "1.0",
        "candidate_version": "0.0.3",
        "candidate_commit": "b" * 40,
        "candidate_manifest_sha256": manifest_sha,
        "status": "verified",
        "review_only": False,
        "required": {
            "owner_key_rotation_verified": True,
            "exact_manifest_ratification_verified": True,
            "external_proof_custody_verified": True,
            "commit_pushed": True,
            "successor_ci_green": True,
            "image_signatures_verified": True,
            "release_provenance_verified": True,
            "sbom_attestations_verified": True,
            "production_overlay_verified": True,
            "remote_backup_verified": True,
            "monitoring_crds_verified": True,
            "dependabot_disposition_verified": True,
            "target_environment_approved": True,
            "rollback_rehearsal_verified": True,
        },
        "evidence": {
            "owner_key_rotation_record": "rotation.json",
            "exact_manifest_ratification_record": "ratification.json",
            "proof_custody_record": "proof-custody.json",
            "remote_commit_sha": "b" * 40,
            "remote_ci_runs": ["run-1"],
            "image_digests": {},
            "signature_verifications": ["sig-1"],
            "sbom_attestations": ["att-1"],
            "production_overlay_record": "overlay.json",
            "remote_backup_record": "backup.json",
            "monitoring_crds_record": "crds.json",
            "dependabot_disposition_record": "dependabot.json",
            "target_environment_record": "target.json",
            "rollback_rehearsal_record": "rollback.json",
        },
    }
    path = tmp_path / "docs" / "operations" / "cab" / "REMOTE_SUCCESSOR_EVIDENCE.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(evidence), encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="cover all images"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_remote_successor_evidence_accepts_complete_external_records(tmp_path: Path) -> None:
    manifest_sha = _write_candidate_manifest(tmp_path)
    image_names = (
        "api",
        "docs-portal",
        "proof-portal",
        "operator-console",
        "swr",
        "atlas",
        "arbiter-rlp",
        "genesis",
    )
    evidence = {
        "schema_version": "1.0",
        "candidate_version": "0.0.3",
        "candidate_commit": "c" * 40,
        "candidate_manifest_sha256": manifest_sha,
        "status": "verified",
        "review_only": False,
        "required": {
            field: True
            for field in (
                "owner_key_rotation_verified",
                "exact_manifest_ratification_verified",
                "external_proof_custody_verified",
                "commit_pushed",
                "successor_ci_green",
                "image_signatures_verified",
                "release_provenance_verified",
                "sbom_attestations_verified",
                "production_overlay_verified",
                "remote_backup_verified",
                "monitoring_crds_verified",
                "dependabot_disposition_verified",
                "target_environment_approved",
                "rollback_rehearsal_verified",
            )
        },
        "evidence": {
            "owner_key_rotation_record": "rotation.json",
            "exact_manifest_ratification_record": "ratification.json",
            "proof_custody_record": "proof-custody.json",
            "remote_commit_sha": "c" * 40,
            "remote_ci_runs": ["run-1"],
            "image_digests": {name: "sha256:" + "a" * 64 for name in image_names},
            # Structured records. The previous fixture used the placeholders
            # ["sig-1"] / ["att-1"], which mirrored a real weakness: the gate only
            # checked that these lists were non-empty, so the production record
            # containing "cosign v2.6.0 no signatures found" satisfied the
            # "signatures verified" requirement.
            "signature_verifications": [
                {
                    "image": name,
                    "digest": "sha256:" + "a" * 64,
                    "verifier": "cosign v3.1.2",
                    "method": "cosign verify (digest-pinned)",
                    "result": "verified",
                }
                for name in image_names
            ],
            "sbom_attestations": [
                {
                    "image": name,
                    "digest": "sha256:" + "a" * 64,
                    "predicate_type": "spdxjson",
                    "verifier": "cosign v3.1.2",
                    "method": "cosign verify-attestation (digest-pinned)",
                    "result": "verified",
                }
                for name in image_names
            ],
            "production_overlay_record": "overlay.json",
            "remote_backup_record": "backup.json",
            "monitoring_crds_record": "crds.json",
            "dependabot_disposition_record": "dependabot.json",
            "target_environment_record": "target.json",
            "rollback_rehearsal_record": "rollback.json",
        },
    }
    path = tmp_path / "docs" / "operations" / "cab" / "REMOTE_SUCCESSOR_EVIDENCE.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(evidence), encoding="utf-8")

    # 4 base + 14 required booleans + 14 evidence fields. The required set grew by
    # one on 2026-07-20 with release_provenance_verified: a cryptographically valid
    # signature issued to an unmerged agent branch is not release provenance.
    assert MODULE.verify_remote_successor_evidence(tmp_path) == 32


def test_remote_successor_evidence_baseline_builder_is_accepted(tmp_path: Path) -> None:
    # Guards the negative tests below: they are only meaningful if the un-poisoned
    # baseline actually passes.
    manifest_sha = _write_candidate_manifest(tmp_path)
    _write_evidence(tmp_path, _complete_verified_evidence(manifest_sha))
    assert MODULE.verify_remote_successor_evidence(tmp_path) == 32


def test_remote_successor_evidence_rejects_cosign_v2_signature_record(tmp_path: Path) -> None:
    # The exact 2026-07-20 weakness: a record produced by cosign 2.x -- which cannot
    # read the v3 bundle format -- must never satisfy the signatures-verified gate,
    # even when it claims a "verified" result.
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = _complete_verified_evidence(manifest_sha)
    evidence["evidence"]["signature_verifications"][0]["verifier"] = "cosign v2.6.0"
    _write_evidence(tmp_path, evidence)
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="cosign >= 3"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_remote_successor_evidence_rejects_unverified_signature_result(tmp_path: Path) -> None:
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = _complete_verified_evidence(manifest_sha)
    evidence["evidence"]["signature_verifications"][0]["result"] = "failed"
    _write_evidence(tmp_path, evidence)
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="verified result"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_remote_successor_evidence_rejects_signature_digest_mismatch(tmp_path: Path) -> None:
    # A signature record bound to a different digest than the recorded image digest.
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = _complete_verified_evidence(manifest_sha)
    evidence["evidence"]["signature_verifications"][0]["digest"] = "sha256:" + "b" * 64
    _write_evidence(tmp_path, evidence)
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="recorded image digest"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_remote_successor_evidence_rejects_empty_attestations_when_verified(tmp_path: Path) -> None:
    # A verified document that carries no attestation records must not pass.
    manifest_sha = _write_candidate_manifest(tmp_path)
    evidence = _complete_verified_evidence(manifest_sha)
    evidence["evidence"]["sbom_attestations"] = []
    _write_evidence(tmp_path, evidence)
    with pytest.raises(MODULE.PreDeploymentVerificationError, match="missing external records"):
        MODULE.verify_remote_successor_evidence(tmp_path)


def test_collect_blockers_itemizes_every_condition_separately() -> None:
    blockers = MODULE.collect_blockers(MODULE.ROOT)
    conditions = {b["condition"] for b in blockers}
    categories = {b["category"] for b in blockers}
    # Distinct mandatory prerequisites must each appear as their own entry, not be
    # collapsed under a single "remote evidence" line.
    for expected in (
        "release_provenance_verified",
        "sbom_attestations_verified",
        "owner_key_rotation_verified",
        "external_proof_custody_verified",
        "rollback_rehearsal_verified",
        "monitoring_crds_verified",
        "production_ingress_host",
        "production_remote_backup",
    ):
        assert expected in conditions
    # Each blocker names its category and an actionable minimum fix.
    assert {"owner", "external-supply-chain", "production"} <= categories
    for blocker in blockers:
        assert blocker["category"] and len(blocker["minimum_fix"]) > 20
    # Substantially more than the three machine-checked gates.
    assert len(blockers) >= 10


def test_v3q_authority_boundary_passes_repository() -> None:
    assert MODULE.verify_v3q_authority_boundary(MODULE.ROOT) == 6


def test_waterfall_integration_boundary_passes_repository() -> None:
    assert MODULE.verify_waterfall_integration(MODULE.ROOT) == 7


def test_production_values_reject_placeholder_host(tmp_path: Path) -> None:
    (tmp_path / "helm").mkdir()
    (tmp_path / "helm" / "values.prod.yaml").write_text(
        "ingress:\n"
        "  hosts:\n"
        "    - host: project-ai.example.com\n"
        "  tls:\n"
        "    - hosts: [project-ai.example.com]\n",
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="placeholder host"):
        MODULE.verify_production_values(tmp_path)


def test_production_values_accept_owner_overlay_host(tmp_path: Path) -> None:
    (tmp_path / "helm").mkdir()
    (tmp_path / "helm" / "values.prod.yaml").write_text(
        "ingress:\n"
        "  hosts:\n"
        "    - host: project-ai.prod.example.org\n"
        "  tls:\n"
        "    - hosts: [project-ai.prod.example.org]\n",
        encoding="utf-8",
    )

    assert MODULE.verify_production_values(tmp_path) == 3


def test_production_values_reject_disabled_remote_backup(tmp_path: Path) -> None:
    (tmp_path / "helm").mkdir()
    (tmp_path / "helm" / "values.prod.yaml").write_text(
        "ingress:\n"
        "  hosts:\n"
        "    - host: app.example.org\n"
        "  tls:\n"
        "    - hosts: [app.example.org]\n"
        "backup:\n"
        "  remote:\n"
        "    enabled: false\n"
        "    destination: ''\n"
        "    secretName: ''\n",
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="remote backup"):
        MODULE.verify_production_backup(tmp_path)


def test_production_backup_accepts_configured_target(tmp_path: Path) -> None:
    (tmp_path / "helm").mkdir()
    (tmp_path / "helm" / "values.prod.yaml").write_text(
        "backup:\n"
        "  remote:\n"
        "    enabled: true\n"
        "    destination: s3:project-ai-backups\n"
        "    secretName: project-ai-backup-config\n",
        encoding="utf-8",
    )

    assert MODULE.verify_production_backup(tmp_path) == 3


def test_release_version_rejects_package_drift(tmp_path: Path) -> None:
    (tmp_path / "packages" / "example").mkdir(parents=True)
    (tmp_path / "apps" / "web" / "portal").mkdir(parents=True)
    (tmp_path / "apps" / "android" / "app").mkdir(parents=True)
    (tmp_path / "helm" / "project-ai").mkdir(parents=True)
    (tmp_path / "docs" / "api").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "root"\nversion = "1.2.3"\n', encoding="utf-8"
    )
    (tmp_path / "packages" / "example" / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "1.2.2"\n', encoding="utf-8"
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="version does not match"):
        MODULE.verify_release_version(tmp_path)


def test_web_runtime_requires_tmp_pid(tmp_path: Path) -> None:
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker" / "web.Dockerfile").write_text(
        "COPY docker/nginx-main.conf /etc/nginx/nginx.conf\nUSER 10001:10001\n",
        encoding="utf-8",
    )
    (tmp_path / "docker" / "nginx-main.conf").write_text(
        "error_log /dev/stderr;\naccess_log /dev/stdout;\n",
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match=r"pid /tmp/nginx\.pid"):
        MODULE.verify_web_runtime(tmp_path)


def test_ci_workflow_requires_expected_jobs(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yaml").write_text("jobs:\n  python: {}\n", encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="CI jobs mismatch"):
        MODULE.verify_ci_workflow(tmp_path)


def test_repository_ci_workflow_exactly_matches_expected_jobs() -> None:
    assert MODULE.verify_ci_workflow(MODULE.ROOT) == len(MODULE.EXPECTED_CI_JOBS)


def test_ci_workflow_rejects_unexpected_job(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    jobs = "\n".join(f"  {name}: {{}}" for name in sorted(MODULE.EXPECTED_CI_JOBS))
    (workflow_dir / "ci.yaml").write_text(
        f"jobs:\n{jobs}\n  unauthorized-extra: {{}}\n",
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="CI jobs mismatch"):
        MODULE.verify_ci_workflow(tmp_path)


def test_local_test_evidence_rejects_document_count_drift(tmp_path: Path) -> None:
    evidence_path = tmp_path / "docs" / "operations" / "cab" / "LOCAL_VERIFICATION_EVIDENCE.json"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "recorded_at": "2026-07-21T00:00:00Z",
                "scope": "dirty-working-tree",
                "branch": "verification",
                "head": "a" * 40,
                "command": "uv run pytest -q",
                "status": "passed",
                "results": {
                    "passed": 10,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 1,
                    "xfailed": 0,
                    "xpassed": 0,
                    "deselected": 0,
                    "flaky": 0,
                    "retried": 0,
                    "mocked": "not-measured",
                },
                "coverage": {
                    "command": "uv run python tools/run_ci_coverage.py --batches 8",
                    "status": "passed",
                    "branch_percent": 87.48,
                    "threshold_percent": 80,
                    "requested_batches": 8,
                    "executed_batches": 11,
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text(
        "Full pytest: 10 passed, 1 skipped",
        encoding="utf-8",
    )
    checklist = tmp_path / "docs" / "deployment" / "PRE_DEPLOYMENT_CHECKLIST.md"
    checklist.parent.mkdir(parents=True)
    checklist.write_text(
        "Full pytest: 9 passed, 1 skipped",
        encoding="utf-8",
    )

    with pytest.raises(
        MODULE.PreDeploymentVerificationError,
        match="does not match structured local test evidence",
    ):
        MODULE.verify_local_test_evidence(tmp_path)


def test_local_test_evidence_rejects_coverage_drift(tmp_path: Path) -> None:
    relative_paths = (
        "AGENTS.md",
        "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md",
        "docs/operations/cab/LOCAL_VERIFICATION_EVIDENCE.json",
    )
    for relative_path in relative_paths:
        source = MODULE.ROOT / relative_path
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    checklist = tmp_path / "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md"
    checklist.write_text(
        checklist.read_text(encoding="utf-8").replace(
            "Batched branch coverage: 87.48%, threshold 80%.",
            "Batched branch coverage: 99.99%, threshold 80%.",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        MODULE.PreDeploymentVerificationError,
        match="does not match structured local coverage evidence",
    ):
        MODULE.verify_local_test_evidence(tmp_path)


def test_security_workflow_requires_codeql_and_checkov(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "security.yaml").write_text("jobs:\n  codeql: {}\n", encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="security jobs mismatch"):
        MODULE.verify_security_workflow(tmp_path)


def test_vulnerability_workflow_requires_lock_derived_third_party_audit(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "vulnscan.yaml").write_text(
        "jobs:\n  python:\n    steps:\n      - run: pip-audit --skip-editable\n",
        encoding="utf-8",
    )

    with pytest.raises(
        MODULE.PreDeploymentVerificationError,
        match="locked third-party audit control",
    ):
        MODULE.verify_vulnerability_workflow(tmp_path)


def test_workflow_action_pinning_passes_repository() -> None:
    assert MODULE.verify_workflow_action_pinning(MODULE.ROOT) > 0


def test_workflow_action_pinning_rejects_tag_reference(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yaml").write_text(
        "jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="full SHA"):
        MODULE.verify_workflow_action_pinning(tmp_path)


def test_publish_workflow_requires_immutable_overlay(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "publish.yaml").write_text("name: Publish\n", encoding="utf-8")

    with pytest.raises(MODULE.PreDeploymentVerificationError, match="release tag"):
        MODULE.verify_publish_workflow(tmp_path)
