#!/usr/bin/env python3
"""Verify pre-deployment evidence, docs, and development runtime manifests."""

from __future__ import annotations

import importlib
import sys
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
}
REQUIRED_FILES = (
    ".env.example",
    "README.md",
    "CHANGELOG.md",
    "compose.yaml",
    ".github/workflows/ci.yaml",
    "helm/project-ai/values.yaml",
    "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md",
    "docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md",
    "docs/operations/CONTINUITY_MAP.md",
    "docs/internal/STAGE_19_5_SESSION_LEDGER.md",
    "docs/internal/STAGE_19_5J2_9_ACCEPTANCE.md",
    "docs/internal/STAGE_19_5_PRE_DEPLOYMENT_ACCEPTANCE.md",
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
    return 7


def verify_ci_workflow(root: Path = ROOT) -> int:
    workflow = _yaml(root, ".github/workflows/ci.yaml")
    jobs = _as_mapping(workflow.get("jobs"), "CI jobs")
    job_names = set(jobs)
    _require(
        job_names == EXPECTED_CI_JOBS,
        f"CI jobs mismatch: expected={sorted(EXPECTED_CI_JOBS)} actual={sorted(job_names)}",
    )
    return len(jobs)


def verify_docs(root: Path = ROOT) -> int:
    checklist = _read(root, "docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md")
    runbook = _read(root, "docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md")
    readme = _read(root, "README.md")
    changelog = _read(root, "CHANGELOG.md")
    combined = "\n".join((checklist, runbook, readme, changelog))
    normalized = " ".join(combined.split())

    for variable in REQUIRED_DOC_ENV_VARS:
        _require(variable in combined, f"documentation missing environment variable {variable}")
    for required_text in (
        "uv run python tools/verify_pre_deployment.py",
        "docker compose up -d --build --wait --wait-timeout 240",
        "python tools/verify_compose_health.py",
        "helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py",
        "No version tag, GitHub Release, package publication, image publication, or deployment",
        "28362260186",
    ):
        _require(
            required_text in combined or required_text in normalized,
            f"documentation missing required text: {required_text}",
        )
    return 4


def verify_all(root: Path = ROOT) -> tuple[str, ...]:
    checks = (
        ("required files", verify_required_files),
        ("environment example", verify_env_example),
        ("compose manifest", verify_compose),
        ("helm values", verify_helm_values),
        ("CI workflow", verify_ci_workflow),
        ("pre-deployment docs", verify_docs),
    )
    results: list[str] = []
    for label, check in checks:
        count = check(root)
        results.append(f"{label}: {count} check(s) passed")
    return tuple(results)


def main() -> int:
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
