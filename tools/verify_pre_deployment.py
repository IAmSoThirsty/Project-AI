#!/usr/bin/env python3
"""Verify pre-deployment evidence, docs, and development runtime manifests."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
yaml = cast(Any, importlib.import_module("yaml"))

EXPECTED_COMPOSE_SERVICES = {
    "api",
    "arbiter-rlp",
    "atlas",
    "docs-portal",
    "genesis",
    "operator-console",
    "postgres",
    "proof-portal",
    "swr",
}
EXPECTED_CI_JOBS = {
    "python",
    "rust",
    "node",
    "android",
    "desktop",
    "compose",
    "kubernetes",
    "sbom",
    "windows-installer",
}
EXPECTED_SECURITY_JOBS = {"codeql", "checkov"}
EXPECTED_OPTIONAL_SERVICES = {
    "academic-writing-toolkit",
    "basic-memory-cloud",
    "browser",
    "chrome",
    "documents",
    "github",
    "linear",
    "neon-postgres",
    "notion",
    "pdf",
    "sites",
    "slack",
    "template-creator",
    "vercel",
}
REQUIRED_ENV_VARS = {
    "PROJECT_AI_API_TOKEN",
    "PROJECT_AI_API_URL",
    "PROJECT_AI_DESKTOP_SMOKE",
    "QT_QPA_PLATFORM",
}
REQUIRED_DOC_ENV_VARS = REQUIRED_ENV_VARS | {
    "PROJECT_AI_AUDIT_PATH",
    "PROJECT_AI_DOI_REGISTRY",
    "PROJECT_AI_SERVICE",
    "VITE_API_BASE_URL",
    "THIRSTYS_V3Q_REQUIRED",
    "THIRSTYS_V3Q_REGISTRY",
    "PROJECT_AI_WATERFALL_ENABLED",
    "PROJECT_AI_WATERFALL_CONFIG",
}
REQUIRED_FILES = (
    ".dockerignore",
    ".env.example",
    "README.md",
    "CHANGELOG.md",
    "compose.yaml",
    "docker/nginx-main.conf",
    ".github/workflows/ci.yaml",
    ".github/workflows/publish.yaml",
    ".github/workflows/security.yaml",
    "helm/project-ai/values.yaml",
    "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md",
    "docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md",
    "docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json",
    "docs/operations/cab/OPTIONAL_SERVICE_USAGE.json",
    "docs/operations/cab/OPTIONAL_SERVICE_USAGE.md",
    "docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md",
    "docs/operations/CONTINUITY_MAP.md",
    "docs/internal/STAGE_19_5_SESSION_LEDGER.md",
    "docs/internal/STAGE_19_5J2_9_ACCEPTANCE.md",
    "docs/internal/STAGE_19_5_PRE_DEPLOYMENT_ACCEPTANCE.md",
)
DOCUMENT_SCOPE_BOUNDARY_FILES = (
    "docs/repo-docs/README.md",
    "docs/repo-docs/00_INDEX.md",
    "docs/repo-docs/architecture/00_ARCHITECTURE_MOC.md",
    "docs/source-docs/README.md",
    "docs/source-docs/agents/README.md",
    "docs/source-docs/core/constitutional/README.md",
    "docs/source-docs/security/README.md",
    "docs/source-docs/supporting/README.md",
    "docs/templates/README.md",
    "docs/vault-recovery/README.md",
    "docs/pre-phase2-hold/README.md",
    "docs/governance/thirstys-standard-v3q-manifest/README.md",
    "packages/_staging/README.md",
    "docs/PRODUCTION_INFRASTRUCTURE_BUILD.md",
    "docs/diagrams/architecture/README.md",
    "docs/architecture/visual-maps/README.md",
    "docs/diagrams/README.md",
    "docs/repo-docs/executive/EXECUTIVE_WHITEPAPER.md",
)


class PreDeploymentVerificationError(ValueError):
    """Raised when pre-deployment evidence is missing or stale."""


def _read(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise PreDeploymentVerificationError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def _yaml(root: Path, relative_path: str) -> dict[str, Any]:
    loaded = yaml.safe_load(_read(root, relative_path))
    if not isinstance(loaded, dict):
        raise PreDeploymentVerificationError(f"{relative_path} must parse as a YAML mapping")
    return cast(dict[str, Any], loaded)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreDeploymentVerificationError(message)


def verify_required_files(root: Path = ROOT) -> int:
    for relative_path in REQUIRED_FILES:
        _read(root, relative_path)
    return len(REQUIRED_FILES)


def verify_env_example(root: Path = ROOT) -> int:
    content = _read(root, ".env.example")
    for variable in REQUIRED_ENV_VARS:
        _require(f"{variable}=" in content, f".env.example missing {variable}")
    for line in content.splitlines():
        if line.startswith("PROJECT_AI_API_TOKEN="):
            token_value = line.partition("=")[2].strip()
            _require(token_value == "", ".env.example must not contain a real API token")
    return len(REQUIRED_ENV_VARS)


def verify_docker_secret_exclusions(root: Path = ROOT) -> int:
    lines = {
        line.strip().replace("\\", "/")
        for line in _read(root, ".dockerignore").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    owner_key = "packages/thirstys-standard-v3q/owner-private.json"
    _require(
        owner_key in lines,
        f".dockerignore must exclude owner-controlled signing material: {owner_key}",
    )
    _require(
        not (root / owner_key).exists(),
        f"owner-controlled signing material must be absent from the checkout: {owner_key}",
    )
    return 2


def verify_owner_key_rotation_tool(root: Path = ROOT) -> int:
    """Ensure rotation tooling cannot reuse or locally store owner private keys."""
    scripts = (
        "packages/thirstys-standard-v3q/tools/create_owner_key.py",
        "docs/governance/thirstys-standard-v3q-manifest/tools/create_owner_key.py",
    )
    required_texts = (
        '"--key-id"',
        "required=True",
        "owner-primary is retired",
        "inside the repository checkout",
    )
    checked = 0
    for relative_path in scripts:
        content = _read(root, relative_path)
        for required_text in required_texts:
            _require(
                required_text in content,
                f"{relative_path} missing owner-key safety guard: {required_text}",
            )
            checked += 1
    return checked


def verify_optional_service_boundaries(root: Path = ROOT) -> int:
    """Require useful service integrations to remain optional and replaceable."""
    relative_path = "docs/operations/cab/OPTIONAL_SERVICE_USAGE.json"
    document = json.loads(_read(root, relative_path))
    _require(document.get("schema_version") == "1.0", "optional service schema mismatch")
    _require(
        document.get("policy") == "optional_replaceable",
        "optional service policy must remain optional_replaceable",
    )
    _require(
        document.get("canonical_authority") == "local_repo",
        "optional services cannot hold canonical authority",
    )
    services = document.get("services")
    _require(isinstance(services, list), "optional service list is missing")
    if not isinstance(services, list):
        raise PreDeploymentVerificationError("optional service list is invalid")
    service_ids: set[str] = set()
    for raw_service in services:
        if not isinstance(raw_service, dict):
            continue
        service_id = raw_service.get("id")
        if isinstance(service_id, str):
            service_ids.add(service_id)
    _require(
        service_ids == EXPECTED_OPTIONAL_SERVICES,
        "optional service inventory mismatch: "
        f"expected={sorted(EXPECTED_OPTIONAL_SERVICES)} actual={sorted(service_ids)}",
    )
    _require(len(services) == len(service_ids), "optional service ids must be unique")
    allowed_outage_behaviors = {
        "continue_locally",
        "queue_or_skip_mirror",
        "use_automated_tests",
        "retain_markdown_source",
        "run_local_gates_and_defer_publication",
        "retain_local_tracking_record",
        "use_another_postgresql_provider",
        "retain_local_cab_record",
        "use_kubernetes_or_local_web_delivery",
        "retain_local_event_and_use_another_route",
        "use_repository_templates",
    }
    for raw_service in services:
        service = _as_mapping(raw_service, "optional service entry")
        service_id = service.get("id")
        _require(
            service.get("required_for_core") is False, f"{service_id} became a core dependency"
        )
        _require(
            service.get("required_for_governance") is False,
            f"{service_id} became a governance dependency",
        )
        _require(service.get("replaceable") is True, f"{service_id} must remain replaceable")
        _require(
            service.get("activation") == "explicit_operator_action",
            f"{service_id} must require explicit operator activation",
        )
        _require(
            service.get("outage_behavior") in allowed_outage_behaviors,
            f"{service_id} has an unsupported outage behavior",
        )
        canonical_source = service.get("canonical_local_source")
        _require(
            isinstance(canonical_source, str) and bool(canonical_source),
            f"{service_id} is missing a canonical local source",
        )
        if not isinstance(canonical_source, str):
            raise PreDeploymentVerificationError(f"{service_id} local source is invalid")
        source_path = Path(canonical_source)
        _require(
            not source_path.is_absolute(), f"{service_id} local source must be repository-relative"
        )
        _require((root / source_path).exists(), f"{service_id} local source does not exist")
    return len(services)


def verify_remote_successor_evidence(root: Path = ROOT) -> int:
    """Require explicit external successor evidence before deployment approval."""
    relative_path = "docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json"
    document = json.loads(_read(root, relative_path))
    _require(document.get("schema_version") == "1.0", "successor evidence schema version mismatch")
    _require(document.get("candidate_version") == "0.0.3", "successor evidence version mismatch")
    candidate_commit = document.get("candidate_commit")
    _require(
        isinstance(candidate_commit, str)
        and re.fullmatch(r"[0-9a-f]{40}", candidate_commit) is not None,
        "successor evidence candidate commit must be a full SHA",
    )
    candidate_manifest_sha = document.get("candidate_manifest_sha256")
    _require(
        isinstance(candidate_manifest_sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", candidate_manifest_sha) is not None,
        "successor evidence candidate manifest hash must be a full SHA-256",
    )
    manifest_path = (
        root / "packages" / "thirstys-standard-v3q" / "thirstys-standard-v3q.manifest.yaml"
    )
    _require(manifest_path.is_file(), "successor evidence candidate manifest is missing")
    actual_manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    _require(
        candidate_manifest_sha == actual_manifest_sha,
        "successor evidence candidate manifest hash mismatch",
    )
    _require(document.get("status") in {"missing", "verified"}, "successor evidence status invalid")
    review_only = document.get("review_only")
    _require(isinstance(review_only, bool), "successor evidence review_only must be boolean")
    required = _as_mapping(document.get("required"), "successor evidence requirements")
    required_fields = (
        "owner_key_rotation_verified",
        "exact_manifest_ratification_verified",
        "external_proof_custody_verified",
        "commit_pushed",
        "successor_ci_green",
        "image_signatures_verified",
        "sbom_attestations_verified",
        "production_overlay_verified",
        "remote_backup_verified",
        "monitoring_crds_verified",
        "dependabot_disposition_verified",
        "target_environment_approved",
        "rollback_rehearsal_verified",
    )
    for field in required_fields:
        _require(
            isinstance(required.get(field), bool),
            f"successor evidence field must be boolean: {field}",
        )
    evidence = _as_mapping(document.get("evidence"), "successor evidence records")
    evidence_fields = (
        "owner_key_rotation_record",
        "exact_manifest_ratification_record",
        "proof_custody_record",
        "remote_commit_sha",
        "remote_ci_runs",
        "image_digests",
        "signature_verifications",
        "sbom_attestations",
        "production_overlay_record",
        "remote_backup_record",
        "monitoring_crds_record",
        "dependabot_disposition_record",
        "target_environment_record",
        "rollback_rehearsal_record",
    )
    for field in evidence_fields:
        _require(field in evidence, f"successor evidence record missing field: {field}")
    _require(
        isinstance(evidence["remote_commit_sha"], (str, type(None))),
        "successor evidence remote commit reference must be string or null",
    )
    _require(
        isinstance(evidence["remote_ci_runs"], list),
        "successor evidence remote CI records must be a list",
    )
    image_digests = _as_mapping(evidence["image_digests"], "successor image digests")
    _require(
        isinstance(evidence["signature_verifications"], list),
        "successor signature records must be a list",
    )
    _require(
        isinstance(evidence["sbom_attestations"], list),
        "successor SBOM attestation records must be a list",
    )
    for field in (
        "owner_key_rotation_record",
        "exact_manifest_ratification_record",
        "proof_custody_record",
        "production_overlay_record",
        "remote_backup_record",
        "monitoring_crds_record",
        "dependabot_disposition_record",
        "target_environment_record",
        "rollback_rehearsal_record",
    ):
        _require(
            isinstance(evidence[field], (str, type(None))),
            f"successor evidence {field} must be string or null",
        )
    if document.get("status") == "verified":
        _require(not review_only, "verified successor evidence cannot remain review-only")
        _require(
            evidence["remote_commit_sha"] == candidate_commit,
            "verified successor evidence commit reference mismatch",
        )
        _require(
            bool(evidence["remote_ci_runs"])
            and bool(evidence["signature_verifications"])
            and bool(evidence["sbom_attestations"])
            and isinstance(evidence["production_overlay_record"], str)
            and isinstance(evidence["remote_backup_record"], str)
            and isinstance(evidence["monitoring_crds_record"], str)
            and isinstance(evidence["dependabot_disposition_record"], str)
            and isinstance(evidence["target_environment_record"], str)
            and isinstance(evidence["rollback_rehearsal_record"], str),
            "verified successor evidence is missing external records",
        )
        expected_images = {
            "api",
            "docs-portal",
            "proof-portal",
            "operator-console",
            "swr",
            "atlas",
            "arbiter-rlp",
            "genesis",
        }
        _require(
            set(image_digests) == expected_images,
            "verified successor evidence must cover all images",
        )
        for name, digest in image_digests.items():
            _require(
                isinstance(digest, str)
                and re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None,
                f"verified successor image digest is invalid: {name}",
            )
    unresolved = [field for field in required_fields if not required[field]]
    _require(
        document.get("status") == "verified" and not unresolved,
        "remote successor evidence is not verified; deployment remains fail-closed; "
        f"unresolved fields: {', '.join(unresolved) or 'status'}",
    )
    return 4 + len(required_fields) + len(evidence_fields)


def verify_v3q_authority_boundary(root: Path = ROOT) -> int:
    """Prove production verifies external proofs and cannot self-authorize."""
    integration = _read(
        root,
        "packages/thirstys-standard-v3q/src/thirstys_standard_runtime/integration.py",
    )
    deployment = _read(
        root,
        "packages/thirstys-standard-v3q/src/thirstys_standard_runtime/deployment.py",
    )
    execution_gate = _read(root, "packages/execution/src/execution/gate.py")
    helm_sources = "\n".join(
        (
            _read(root, "helm/project-ai/templates/api.yaml"),
            _read(root, "helm/project-ai/templates/secrets.yaml"),
            _read(root, "helm/project-ai/values.yaml"),
            _read(root, "helm/values.prod.yaml"),
        )
    )
    _require("_mint_authority_proof" not in integration, "V3Q runtime must not mint authority")
    _require("_mint_approval_proof" not in integration, "V3Q runtime must not mint approval")
    _require("private_key" not in deployment, "V3Q deployment must not load private keys")
    _require(
        "THIRSTYS_V3Q_OWNER_KEY" not in helm_sources,
        "Helm must not mount owner private authority into the online runtime",
    )
    _require(
        '("deny", "require_approval")' in execution_gate,
        "ExecutionGate must block V3Q require_approval decisions",
    )
    production = _yaml(root, "helm/values.prod.yaml")
    production_v3q = _as_mapping(production.get("v3q"), "production Helm v3q values")
    _require(production_v3q.get("required") is True, "production Helm must require V3Q")
    production_api = _as_mapping(production.get("api"), "production Helm api values")
    production_api_env = _as_mapping(production_api.get("env"), "production Helm api env")
    _require(
        production_api_env.get("PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED") == "true",
        "production Helm must require durable machine credentials",
    )
    _require(
        "PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED"
        in _read(root, "helm/project-ai/templates/api.yaml"),
        "Helm API template must branch shared-token mounting on durable credential mode",
    )
    return 6


def verify_waterfall_integration(root: Path = ROOT) -> int:
    """Verify the standalone/rebuild package is wired through the API boundary."""
    api_project = _read(root, "packages/api/pyproject.toml")
    routes = _read(root, "packages/api/src/project_ai_api/waterfall_workflows.py")
    app = _read(root, "packages/api/src/project_ai_api/app.py")
    env = _read(root, ".env.example")
    provenance = _read(root, "packages/thirstys-waterfall/PROVENANCE.md")
    for required_text, label in (
        ("project-ai-thirstys-waterfall", "API Waterfall rebuild dependency"),
        ("project-ai-waterfall-adapter", "API Waterfall adapter dependency"),
        ("/api/v1/modules/waterfall/status", "Waterfall status route"),
        ("/api/v1/modules/waterfall/operations", "Waterfall operation route"),
        ("ExecutionGate", "Waterfall execution gate boundary"),
        ("PROJECT_AI_WATERFALL_ENABLED", "Waterfall activation setting"),
        ("Source repository:", "Waterfall provenance record"),
    ):
        source = api_project + routes + app + env + provenance
        _require(required_text in source, f"missing {label}")
    return 7


def _toml(root: Path, relative_path: str) -> dict[str, Any]:
    return tomllib.loads(_read(root, relative_path))


def verify_release_version(root: Path = ROOT) -> int:
    root_project = _as_mapping(_toml(root, "pyproject.toml").get("project"), "root project")
    expected = root_project.get("version")
    _require(
        isinstance(expected, str) and re.fullmatch(r"\d+\.\d+\.\d+", expected) is not None,
        "root project version must be a release SemVer",
    )

    checked = 1
    pyprojects = sorted((root / "packages").glob("*/pyproject.toml")) + sorted(
        (root / "apps").glob("*/pyproject.toml")
    )
    _require(bool(pyprojects), "no workspace package manifests found")
    for path in pyprojects:
        relative = path.relative_to(root).as_posix()
        project = _as_mapping(_toml(root, relative).get("project"), f"{relative} project")
        _require(
            project.get("version") == expected, f"{relative} version does not match {expected}"
        )
        checked += 1

    cargo_workspace = _as_mapping(_toml(root, "Cargo.toml").get("workspace"), "Cargo workspace")
    cargo_package = _as_mapping(cargo_workspace.get("package"), "Cargo workspace package")
    _require(cargo_package.get("version") == expected, "Cargo workspace version mismatch")
    checked += 1

    chart = _yaml(root, "helm/project-ai/Chart.yaml")
    _require(str(chart.get("version")) == expected, "Helm chart version mismatch")
    _require(str(chart.get("appVersion")) == expected, "Helm appVersion mismatch")
    checked += 1

    package_manifests = [
        root / "package.json",
        *sorted((root / "apps" / "web").glob("*/package.json")),
    ]
    for path in package_manifests:
        relative = path.relative_to(root).as_posix()
        package = json.loads(_read(root, relative))
        _require(
            isinstance(package, dict) and package.get("version") == expected,
            f"{relative} version mismatch",
        )
        checked += 1

    android = _read(root, "apps/android/app/build.gradle.kts")
    _require(f'versionName = "{expected}"' in android, "Android versionName mismatch")
    checked += 1

    openapi = json.loads(_read(root, "docs/api/openapi-baseline.json"))
    _require(
        isinstance(openapi, dict)
        and isinstance(openapi.get("info"), dict)
        and openapi["info"].get("version") == expected,
        "OpenAPI baseline version mismatch",
    )
    checked += 1

    uv_lock = _toml(root, "uv.lock")
    uv_packages = uv_lock.get("package")
    if not isinstance(uv_packages, list):
        raise PreDeploymentVerificationError("uv.lock package list missing")
    editable_versions = {
        package.get("version")
        for package in uv_packages
        if isinstance(package, dict)
        and isinstance(package.get("source"), dict)
        and "editable" in package["source"]
    }
    _require(
        editable_versions == {expected}, f"uv.lock editable versions mismatch: {editable_versions}"
    )
    checked += 1
    return checked


def verify_web_runtime(root: Path = ROOT) -> int:
    dockerfile = _read(root, "docker/web.Dockerfile")
    nginx = _read(root, "docker/nginx-main.conf")
    required_dockerfile_text = (
        "COPY docker/nginx-main.conf /etc/nginx/nginx.conf",
        "USER 10001:10001",
    )
    required_nginx_text = (
        "error_log /dev/stderr",
        "access_log /dev/stdout",
        "pid /tmp/nginx.pid",
        "client_body_temp_path /tmp/client_body",
        "proxy_temp_path /tmp/proxy",
    )
    for required_text in required_dockerfile_text:
        _require(required_text in dockerfile, f"web Dockerfile missing {required_text}")
    for required_text in required_nginx_text:
        _require(required_text in nginx, f"Nginx runtime config missing {required_text}")
    return len(required_dockerfile_text) + len(required_nginx_text)


def _as_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PreDeploymentVerificationError(f"{context} must be a mapping")
    return cast(dict[str, Any], value)


def _security_options(service_name: str, service: dict[str, Any]) -> None:
    _require(service.get("read_only") is True, f"{service_name} must use read_only: true")
    cap_drop = service.get("cap_drop")
    _require(isinstance(cap_drop, list) and "ALL" in cap_drop, f"{service_name} must drop ALL caps")
    security_opt = service.get("security_opt")
    _require(
        isinstance(security_opt, list) and "no-new-privileges:true" in security_opt,
        f"{service_name} must set no-new-privileges",
    )
    _require("healthcheck" in service, f"{service_name} must declare a healthcheck")


def verify_compose(root: Path = ROOT) -> int:
    compose = _yaml(root, "compose.yaml")
    services = _as_mapping(compose.get("services"), "compose services")
    service_names = set(services)
    _require(
        service_names == EXPECTED_COMPOSE_SERVICES,
        f"compose services mismatch: expected={sorted(EXPECTED_COMPOSE_SERVICES)} actual={sorted(service_names)}",
    )
    for service_name, raw_service in services.items():
        _security_options(service_name, _as_mapping(raw_service, f"service {service_name}"))

    api_env = _as_mapping(_as_mapping(services["api"], "api service").get("environment"), "api env")
    for variable in ("PROJECT_AI_API_TOKEN", "PROJECT_AI_AUDIT_PATH", "PROJECT_AI_DOI_REGISTRY"):
        _require(variable in api_env, f"api compose env missing {variable}")

    role_expectations = {
        "swr": "swr",
        "atlas": "atlas",
        "arbiter-rlp": "arbiter-rlp",
    }
    for service_name, expected_role in role_expectations.items():
        env = _as_mapping(
            _as_mapping(services[service_name], service_name).get("environment"), service_name
        )
        _require(env.get("PROJECT_AI_SERVICE") == expected_role, f"{service_name} role mismatch")
    return len(services)


def verify_helm_values(root: Path = ROOT) -> int:
    values = _yaml(root, "helm/project-ai/values.yaml")
    api = _as_mapping(values.get("api"), "helm api values")
    api_env = _as_mapping(api.get("env"), "helm api env")
    _require(api_env.get("PROJECT_AI_API_TOKEN") == "", "helm token default must remain blank")
    for variable in ("PROJECT_AI_AUDIT_PATH", "PROJECT_AI_DOI_REGISTRY"):
        _require(variable in api_env, f"helm api env missing {variable}")
    for section in ("docsPortal", "proofPortal", "swr", "atlas", "arbiterRlp", "genesis"):
        _require(section in values, f"helm values missing {section}")
    v3q = _as_mapping(values.get("v3q"), "helm v3q values")
    _require(v3q.get("required") is False, "development Helm values must leave V3Q dormant")
    return 9


def verify_production_values(root: Path = ROOT) -> int:
    """Reject unapproved placeholder inputs from the production values file."""
    values = _yaml(root, "helm/values.prod.yaml")
    ingress = _as_mapping(values.get("ingress"), "production Helm ingress")
    hosts = ingress.get("hosts")
    _require(
        isinstance(hosts, list) and len(hosts) > 0,
        "production Helm ingress hosts are missing",
    )
    if not isinstance(hosts, list):
        raise PreDeploymentVerificationError("production Helm ingress hosts are invalid")
    for item in hosts:
        host_entry = _as_mapping(item, "production Helm ingress host")
        host = host_entry.get("host")
        _require(
            isinstance(host, str) and bool(host),
            "production Helm ingress host is invalid",
        )
        if not isinstance(host, str):
            raise PreDeploymentVerificationError("production Helm ingress host is invalid")
        _require(
            host != "project-ai.example.com" and not host.endswith(".example.com"),
            "production Helm ingress still uses a placeholder host",
        )
    tls_entries = ingress.get("tls")
    _require(
        isinstance(tls_entries, list) and len(tls_entries) > 0,
        "production Helm TLS entries are missing",
    )
    if not isinstance(tls_entries, list):
        raise PreDeploymentVerificationError("production Helm TLS entries are invalid")
    for item in tls_entries:
        tls_entry = _as_mapping(item, "production Helm TLS entry")
        tls_hosts = tls_entry.get("hosts")
        _require(
            isinstance(tls_hosts, list) and len(tls_hosts) > 0,
            "production Helm TLS hosts are missing",
        )
        if not isinstance(tls_hosts, list):
            raise PreDeploymentVerificationError("production Helm TLS hosts are invalid")
        for host in tls_hosts:
            _require(
                isinstance(host, str)
                and bool(host)
                and host != "project-ai.example.com"
                and not host.endswith(".example.com"),
                "production Helm TLS still uses a placeholder host",
            )
    return 3


def verify_production_backup(root: Path = ROOT) -> int:
    """Require a configured remote backup target before production approval."""
    values = _yaml(root, "helm/values.prod.yaml")
    backup = _as_mapping(values.get("backup"), "production Helm backup")
    remote_backup = _as_mapping(backup.get("remote"), "production Helm remote backup")
    _require(
        remote_backup.get("enabled") is True,
        "production Helm remote backup must be enabled for deployment",
    )
    for field in ("destination", "secretName"):
        value = remote_backup.get(field)
        _require(
            isinstance(value, str) and bool(value),
            f"production Helm remote backup {field} is missing",
        )
    return 3


def verify_ci_workflow(root: Path = ROOT) -> int:
    workflow = _yaml(root, ".github/workflows/ci.yaml")
    jobs = _as_mapping(workflow.get("jobs"), "CI jobs")
    job_names = set(jobs)
    _require(
        job_names == EXPECTED_CI_JOBS,
        f"CI jobs mismatch: expected={sorted(EXPECTED_CI_JOBS)} actual={sorted(job_names)}",
    )
    return len(jobs)


def verify_security_workflow(root: Path = ROOT) -> int:
    workflow = _yaml(root, ".github/workflows/security.yaml")
    jobs = _as_mapping(workflow.get("jobs"), "security jobs")
    job_names = set(jobs)
    _require(
        job_names == EXPECTED_SECURITY_JOBS,
        "security jobs mismatch: "
        f"expected={sorted(EXPECTED_SECURITY_JOBS)} actual={sorted(job_names)}",
    )
    workflow_text = _read(root, ".github/workflows/security.yaml")
    for required_text in ("github/codeql-action/init@", "checkov==3.3.8"):
        _require(required_text in workflow_text, f"security workflow missing {required_text}")
    return len(jobs)


def verify_workflow_action_pinning(root: Path = ROOT) -> int:
    """Require immutable full-SHA references for every remote workflow action."""
    workflow_dir = root / ".github" / "workflows"
    _require(workflow_dir.is_dir(), "missing .github/workflows directory")
    action_pattern = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")
    sha_pattern = re.compile(r"@[0-9a-fA-F]{40}$")
    checked = 0
    for workflow in sorted(workflow_dir.glob("*.y*ml")):
        for line_number, line in enumerate(
            workflow.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = action_pattern.match(line)
            if not match:
                continue
            reference = match.group(1)
            if reference.startswith("./"):
                continue
            checked += 1
            _require(
                sha_pattern.search(reference) is not None,
                f"workflow action must use a full SHA: {workflow.name}:{line_number}: {reference}",
            )
    _require(checked > 0, "no remote workflow actions found")
    return checked


def verify_publish_workflow(root: Path = ROOT) -> int:
    workflow_text = _read(root, ".github/workflows/publish.yaml")
    required_texts = (
        "Verify release tag matches repository version",
        "Generate and verify immutable image overlay",
        "docker buildx imagetools inspect",
        "--require-project-image-digests",
        "image-digests.yaml",
    )
    for required_text in required_texts:
        _require(required_text in workflow_text, f"publish workflow missing {required_text}")
    return len(required_texts)


def verify_docs(root: Path = ROOT) -> int:
    checklist = _read(root, "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md")
    runbook = _read(root, "docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md")
    readme = _read(root, "README.md")
    changelog = _read(root, "CHANGELOG.md")
    operator = _read(root, "docs/operator.md")
    architecture = _read(root, "docs/architecture.md")
    security = _read(root, "docs/security.md")
    helm_deploy = _read(root, "docs/deployment/HELM_DEPLOY.md")
    cab_pack = _read(root, "docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md")
    combined = "\n".join(
        (
            checklist,
            runbook,
            readme,
            changelog,
            operator,
            architecture,
            security,
            helm_deploy,
            cab_pack,
        )
    )
    normalized = " ".join(combined.split())

    for variable in REQUIRED_DOC_ENV_VARS:
        _require(variable in combined, f"documentation missing environment variable {variable}")
    for required_text in (
        "uv run python tools/verify_pre_deployment.py",
        "docker compose up -d --build --wait --wait-timeout 240",
        "python tools/verify_compose_health.py",
        "--require-project-image-digests",
        "Local gates alone are not production approval",
        "Local successor version: `0.0.3`",
        "compose runtime: 9/9 healthy and security settings verified",
        "Nine Compose services",
        "All nine development containers",
        "The chart renders eight application workloads",
        "DEPLOYMENT NOT AUTHORIZED",
        "Owner-controlled `owner-primary` key",
        "PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md",
        "REMOTE_SUCCESSOR_EVIDENCE.json",
        "3412 passed",
        "--report",
        "87.32%",
        "draft-manifest review snapshot",
        "placeholder production ingress",
        "unconfigured remote backup",
    ):
        _require(
            required_text in combined or required_text in normalized,
            f"documentation missing required text: {required_text}",
        )
    return 8


def verify_document_scope_boundaries(root: Path = ROOT) -> int:
    """Keep recovered/reference documents from implying current deployment approval."""
    required_phrase = "deployment approval"
    checked = 0
    relative_paths = list(DOCUMENT_SCOPE_BOUNDARY_FILES)
    report_directory = root / "docs/operations/deployment-reports"
    if report_directory.is_dir():
        relative_paths.extend(
            path.relative_to(root).as_posix()
            for path in sorted(report_directory.glob("*.md"))
            if path.relative_to(root).as_posix() not in relative_paths
        )
    for relative_path in relative_paths:
        content = " ".join(_read(root, relative_path).lower().replace(">", " ").split())
        _require(
            required_phrase in content and "fail-closed" in content,
            f"document lacks current deployment boundary: {relative_path}",
        )
        checked += 1
    return checked


def _pre_deployment_checks() -> tuple[tuple[str, Any], ...]:
    return (
        ("required files", verify_required_files),
        ("environment example", verify_env_example),
        ("Docker secret exclusions", verify_docker_secret_exclusions),
        ("owner-key rotation tooling", verify_owner_key_rotation_tool),
        ("optional service boundaries", verify_optional_service_boundaries),
        ("remote successor evidence", verify_remote_successor_evidence),
        ("V3Q external-authority boundary", verify_v3q_authority_boundary),
        ("Waterfall integration boundary", verify_waterfall_integration),
        ("release version agreement", verify_release_version),
        ("non-root web runtime", verify_web_runtime),
        ("compose manifest", verify_compose),
        ("helm values", verify_helm_values),
        ("production Helm values", verify_production_values),
        ("production backup", verify_production_backup),
        ("CI workflow", verify_ci_workflow),
        ("security workflow", verify_security_workflow),
        ("workflow action pinning", verify_workflow_action_pinning),
        ("publish workflow", verify_publish_workflow),
        ("pre-deployment docs", verify_docs),
        ("document scope boundaries", verify_document_scope_boundaries),
    )


def verify_all(root: Path = ROOT) -> tuple[str, ...]:
    results: list[str] = []
    for label, check in _pre_deployment_checks():
        count = check(root)
        results.append(f"{label}: {count} check(s) passed")
    return tuple(results)


def collect_pre_deployment_report(root: Path = ROOT) -> tuple[str, ...]:
    """Evaluate every gate and return a complete diagnostic report.

    This intentionally does not change the strict fail-fast behavior of
    :func:`verify_all`; it gives operators all currently-known blockers in one
    diagnostic pass without weakening deployment authorization.
    """
    results: list[str] = []
    for label, check in _pre_deployment_checks():
        try:
            count = check(root)
        except Exception as error:
            results.append(f"FAIL {label}: {error}")
        else:
            results.append(f"PASS {label}: {count} check(s) passed")
    return tuple(results)


def main() -> int:
    if "--report" in sys.argv[1:]:
        report = collect_pre_deployment_report(ROOT)
        for result in report:
            print(result)
        failed = any(result.startswith("FAIL ") for result in report)
        if failed:
            print("pre-deployment report found blocking gates", file=sys.stderr)
            return 1
        print("pre-deployment report passed")
        return 0
    try:
        for result in verify_all(ROOT):
            print(result)
    except PreDeploymentVerificationError as error:
        print(f"pre-deployment verification failed: {error}", file=sys.stderr)
        return 1
    print("pre-deployment verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
