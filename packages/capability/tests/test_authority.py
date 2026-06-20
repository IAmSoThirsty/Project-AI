from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from capability import (
    CapabilityAuthority,
    ExpiredCapabilityError,
    InvalidCapabilityError,
    ReplayedCapabilityError,
    RevokedCapabilityError,
    ScopeMismatchError,
)
from kernel import TrustedClock


class MutableTime:
    def __init__(self) -> None:
        self.value = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value


def authority(time: MutableTime | None = None) -> CapabilityAuthority:
    return CapabilityAuthority(
        b"s" * 32,
        issuer="project-ai",
        clock=TrustedClock(time) if time is not None else None,
        token_id_factory=lambda: "token-1",
    )


def issue(service: CapabilityAuthority) -> str:
    return service.issue(
        subject="operator",
        operation="write",
        resource="record:1",
        ttl=timedelta(minutes=5),
    )


def test_issue_verify_and_consume_exact_scope() -> None:
    service = authority()
    token = issue(service)
    claims = service.verify(
        token,
        subject="operator",
        operation="write",
        resource="record:1",
    )
    assert claims.token_id == "token-1"
    service.consume(token, subject="operator", operation="write", resource="record:1")
    with pytest.raises(ReplayedCapabilityError):
        service.consume(token, subject="operator", operation="write", resource="record:1")


@pytest.mark.parametrize(
    ("subject", "operation", "resource"),
    [
        ("other", "write", "record:1"),
        ("operator", "delete", "record:1"),
        ("operator", "write", "record:2"),
    ],
)
def test_scope_mismatch_denies(subject: str, operation: str, resource: str) -> None:
    service = authority()
    with pytest.raises(ScopeMismatchError):
        service.verify(issue(service), subject=subject, operation=operation, resource=resource)


def test_expiry_revocation_and_signature_tamper_deny() -> None:
    time = MutableTime()
    service = authority(time)
    token = issue(service)
    time.value += timedelta(minutes=5)
    with pytest.raises(ExpiredCapabilityError):
        service.verify(token, subject="operator", operation="write", resource="record:1")

    live = authority()
    live_token = issue(live)
    live.revoke("token-1")
    with pytest.raises(RevokedCapabilityError):
        live.verify(live_token, subject="operator", operation="write", resource="record:1")
    payload, signature = live_token.split(".")
    tampered = ("A" if payload[0] != "A" else "B") + payload[1:] + "." + signature
    with pytest.raises(InvalidCapabilityError, match="signature"):
        authority().verify(
            tampered,
            subject="operator",
            operation="write",
            resource="record:1",
        )


@pytest.mark.parametrize("token", ["", "one.two.three", "one.***"])
def test_malformed_token_denies(token: str) -> None:
    with pytest.raises(InvalidCapabilityError):
        authority().verify(token, subject="operator", operation="write", resource="record:1")


def test_issuance_and_configuration_validation() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        CapabilityAuthority(b"short", issuer="x")
    with pytest.raises(ValueError, match="issuer"):
        CapabilityAuthority(b"s" * 32, issuer="")
    with pytest.raises(ValueError, match="max_ttl"):
        CapabilityAuthority(b"s" * 32, issuer="x", max_ttl=timedelta(0))
    service = authority()
    with pytest.raises(ValueError, match="subject"):
        service.issue(subject="", operation="write", resource="x", ttl=timedelta(seconds=1))
    with pytest.raises(ValueError, match="ttl"):
        service.issue(subject="x", operation="write", resource="x", ttl=timedelta(hours=2))
    with pytest.raises(ValueError, match="token_id"):
        service.revoke("")
    empty_id = CapabilityAuthority(
        b"s" * 32,
        issuer="x",
        token_id_factory=lambda: "",
    )
    with pytest.raises(ValueError, match="token_id_factory"):
        empty_id.issue(subject="x", operation="read", resource="x", ttl=timedelta(seconds=1))
