from __future__ import annotations

import json
from pathlib import Path

import pytest

from security import ChimeraSecurity, classify, start_audit_relay


@pytest.mark.parametrize(
    ("path", "body", "ua", "minimum", "tag", "outcome"),
    [
        ("/", b"", b"Mozilla/5.0", 0, None, "ALLOW"),
        ("/.env", b"", b"curl/8", 30, "env_probe", "ESCALATE"),
        ("/wp-login.php", b"", b"sqlmap/1.7", 60, "sqli_tool", "DENY"),
        ("/?id=1' OR '1'='1", b"", b"Mozilla/5.0", 40, "sqli", "ESCALATE"),
        ("/admin", b"../../etc/passwd", b"x", 50, "traversal", "ESCALATE"),
        ("/shell?cmd=cat", b"", b"x", 70, "rce", "DENY"),
        ("/api", b"", b"masscan/1.3", 40, "scanner", "ESCALATE"),
    ],
)
def test_classifier_truth_table(
    path: str,
    body: bytes,
    ua: bytes,
    minimum: int,
    tag: str | None,
    outcome: str,
) -> None:
    detection = classify(path, body, ua, {"x-test": "value"})
    assert detection.score >= minimum
    assert detection.outcome == outcome
    if tag is not None:
        assert tag in detection.tags


def test_chimera_requires_strong_secret() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        ChimeraSecurity(b"short")


def test_canary_register_scan_rotate_and_audit(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    service = ChimeraSecurity(b"x" * 32, start_audit_relay(audit_path))
    first = service.register_canary("aws/key")
    hits = service.scan(f"leak={first}", context="request-body")

    assert hits[0].label == "aws/key"
    assert first not in audit_path.read_text(encoding="utf-8")

    second = service.rotate_canary("aws/key")
    assert second != first
    assert service.scan(first, context="retired") == ()
    assert service.scan(second.encode(), context="active")[0].label == "aws/key"


def test_canary_rejects_empty_normalized_label() -> None:
    service = ChimeraSecurity(b"x" * 32)
    with pytest.raises(ValueError, match="must not be empty"):
        service.register_canary("")


def test_inspection_relays_canonical_verdict(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    service = ChimeraSecurity(b"x" * 32, start_audit_relay(audit_path))

    result = service.inspect(action_id="action-1", path="/.env")
    record = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])

    assert result.outcome == "ESCALATE"
    assert record["event"] == "chimera.verdict"
    assert record["verdict"] == "ESCALATE"
