from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "scripts" / "owner" / "Export-ProjectAIOfflineBundle.ps1"
VALIDATOR = ROOT / "scripts" / "owner" / "Test-OfflineRelease.ps1"


def project_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def test_offline_exporter_carries_release_legal_and_version_material() -> None:
    exporter = EXPORTER.read_text(encoding="utf-8")
    for required in (
        '"LICENSE"',
        '"NOTICE"',
        '"THIRD_PARTY_NOTICES.md"',
        '"RELEASE.json"',
        '"project-ai-p1-v$version-windows-amd64.zip"',
        "product_version = $version",
        "source_tree_clean = $sourceTreeClean",
    ):
        assert required in exporter

    version = project_version()
    notes = ROOT / "docs" / "deployment" / f"RELEASE_NOTES_v{version}.md"
    assert notes.is_file()
    assert f"Project-AI v{version}" in notes.read_text(encoding="utf-8")


def test_release_export_requires_clean_source_and_emits_all_sidecars() -> None:
    exporter = EXPORTER.read_text(encoding="utf-8")
    assert "if (-not $sourceTreeClean -and -not $AllowDirtySource)" in exporter
    assert "Ensure-OwnerLocalEnvironment" in exporter
    assert "Assert-OwnerCredentialContinuity" in exporter
    assert "Initialize-OwnerSecretStore | Out-Null" in exporter
    assert "Write-OwnerRuntimeSecrets | Out-Null" in exporter
    assert '"$resolvedOutput.sha256"' in exporter
    assert '"$resolvedOutput.sig"' in exporter
    assert '"$resolvedOutput.pub"' in exporter
    assert "Remove-Item -LiteralPath $publishedPath -Force" in exporter
    assert "Write-Sha256Sidecar" in exporter
    assert "Write-SshSignatureSidecar" in exporter
    assert '"$ArchivePath.sha256"' in exporter
    assert '"$ArchivePath.sig"' in exporter
    assert '"$ArchivePath.pub"' in exporter
    assert "project-ai-offline-release" in exporter


def test_release_validator_checks_external_and_internal_integrity() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    for required in (
        "Get-FileHash -Algorithm SHA256",
        "Test-SshFileSignature",
        "offline-bundle-manifest.json",
        "RELEASE.json",
        "source_tree_clean",
        "The release manifest contains an unsafe path",
        "The release archive has a hash mismatch",
    ):
        assert required in validator


def test_owner_evidence_receipts_do_not_collide_within_one_second() -> None:
    common = (ROOT / "scripts" / "owner" / "_owner-common.ps1").read_text(encoding="utf-8")
    negative = (ROOT / "scripts" / "owner" / "Test-OwnerRecoveryNegativePaths.ps1").read_text(
        encoding="utf-8"
    )
    assert "yyyyMMddTHHmmssfffZ" in common
    assert "Distinct restore failures did not retain distinct evidence receipts" in negative


def test_destructive_restore_repairs_non_root_api_volume_ownership() -> None:
    script = (ROOT / "scripts" / "owner" / "Restore-ProjectAI.ps1").read_text(encoding="utf-8")

    assert "docker cp" in script
    assert "--no-deps --user 0 --cap-add CHOWN" in script
    assert "chown -R 10001:10001 /data" in script
    assert "Could not repair restored audit and SWR state ownership" in script


def test_windows_runtime_secrets_are_docker_readable_outside_private_profile() -> None:
    secret_store = (ROOT / "scripts" / "owner" / "Secret-Store.ps1").read_text(encoding="utf-8")
    common = (ROOT / "scripts" / "owner" / "_owner-common.ps1").read_text(encoding="utf-8")
    compose = (ROOT / "compose.secrets.yaml").read_text(encoding="utf-8")

    assert "CommonApplicationData" in secret_store
    assert r'"Project-AI\owner-runtime\$($identity.Value)"' in secret_store
    assert "Set-OwnerDockerRuntimeAcl" in secret_store
    assert '"docker-users"' in secret_store
    assert '$dockerGrant = "*$($dockerUsers.Value):R"' in secret_store
    assert "$env:PROJECT_AI_RUNTIME_SECRET_ROOT = $resolvedRuntime" in secret_store
    assert "$env:PROJECT_AI_RUNTIME_SECRET_ROOT = Get-OwnerRuntimeRoot" in common
    assert compose.count("${PROJECT_AI_RUNTIME_SECRET_ROOT:-.owner-state/runtime}") == 5


def test_web_proxy_matches_the_browser_gateway_path_contract() -> None:
    api = (ROOT / "apps" / "web" / "shared" / "src" / "api.ts").read_text(encoding="utf-8")
    nginx = (ROOT / "docker" / "nginx.conf").read_text(encoding="utf-8")

    assert '?? "/api"' in api
    assert 'requestJson<BootstrapStatus>("/api/v1/auth/bootstrap-status")' in api
    assert "proxy_pass http://api:8000/;" in nginx
    for relative in (
        "apps/web/operator-console/vite.config.ts",
        "apps/web/proof-portal/vite.config.ts",
        "apps/web/docs-portal/vite.config.ts",
    ):
        config = (ROOT / relative).read_text(encoding="utf-8")
        assert 'replace(/^\\/api/, "")' in config


def test_release_profile_is_consistent_across_active_documents() -> None:
    version = project_version()
    expected = f"v{version}"
    for relative in (
        "README.md",
        "OWNER_QUICKSTART.md",
        "docs/deployment/DEPLOYMENT_MODEL.md",
        "docs/deployment/OFFLINE_FIRST_READINESS.md",
        f"docs/deployment/RELEASE_NOTES_{expected}.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert expected in text
        assert re.search(r"Offline[- ]First Local", text, re.IGNORECASE)


def test_owner_cockpit_requirement_index_remains_well_formed() -> None:
    requirements_path = ROOT / "docs" / "standards" / "owner-cockpit" / "REQUIREMENTS.json"
    requirements = json.loads(requirements_path.read_text(encoding="utf-8"))
    rows = requirements["requirements"]
    assert len(rows) == 144
    assert len({row["id"] for row in rows}) == 144
