from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from tools.verify_node_dependencies import AuditPolicyError, validate_report

NOW = datetime(2026, 7, 27, tzinfo=UTC)


def _policy() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "audit_level": "moderate",
        "exceptions": [
            {
                "advisory": "GHSA-example",
                "package": "react-router",
                "version": "7.18.1",
                "severity": "high",
                "paths": ["app>react-router-dom>react-router"],
                "source_roots": ["app/src"],
                "forbidden_source_terms": ["unstable_RSC"],
                "expires_utc": "2026-08-31T00:00:00Z",
                "rationale": "Test exception.",
            }
        ],
    }


def _report() -> dict[str, Any]:
    return {
        "advisories": {
            "1": {
                "github_advisory_id": "GHSA-example",
                "module_name": "react-router",
                "severity": "high",
                "findings": [
                    {
                        "version": "7.18.1",
                        "paths": ["app>react-router-dom>react-router"],
                    }
                ],
            }
        }
    }


def _root(tmp_path: Path, content: str = "createBrowserRouter([])") -> Path:
    source = tmp_path / "app" / "src"
    source.mkdir(parents=True)
    (source / "app.tsx").write_text(content, encoding="utf-8")
    return tmp_path


def test_exact_unexpired_source_bounded_exception_passes(tmp_path: Path) -> None:
    validate_report(_report(), _policy(), root=_root(tmp_path), now=NOW)


def test_unknown_advisory_fails_closed(tmp_path: Path) -> None:
    report = _report()
    report["advisories"]["1"]["github_advisory_id"] = "GHSA-unknown"
    with pytest.raises(AuditPolicyError, match="unapproved vulnerability"):
        validate_report(report, _policy(), root=_root(tmp_path), now=NOW)


@pytest.mark.parametrize("field,value", [("module_name", "other"), ("severity", "critical")])
def test_advisory_metadata_drift_fails_closed(tmp_path: Path, field: str, value: str) -> None:
    report = _report()
    report["advisories"]["1"][field] = value
    with pytest.raises(AuditPolicyError, match="drift"):
        validate_report(report, _policy(), root=_root(tmp_path), now=NOW)


def test_version_or_path_drift_fails_closed(tmp_path: Path) -> None:
    report = _report()
    report["advisories"]["1"]["findings"][0]["version"] = "7.18.2"
    with pytest.raises(AuditPolicyError, match="version drift"):
        validate_report(report, _policy(), root=_root(tmp_path), now=NOW)


def test_forbidden_source_use_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AuditPolicyError, match="exception boundary violated"):
        validate_report(
            _report(),
            _policy(),
            root=_root(tmp_path, "unstable_RSC()"),
            now=NOW,
        )


def test_expired_exception_fails_closed(tmp_path: Path) -> None:
    policy = _policy()
    policy["exceptions"][0]["expires_utc"] = "2026-07-26T00:00:00Z"
    with pytest.raises(AuditPolicyError, match="expired"):
        validate_report(_report(), policy, root=_root(tmp_path), now=NOW)


def test_stale_exception_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AuditPolicyError, match="stale exception"):
        validate_report({"advisories": {}}, _policy(), root=_root(tmp_path), now=NOW)
