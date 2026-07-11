"""Signed, exact-scope capability issuance, verification, revocation, and consumption."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import cast

from kernel import TrustedClock


class CapabilityError(RuntimeError):
    pass


class InvalidCapabilityError(CapabilityError):
    pass


class ExpiredCapabilityError(CapabilityError):
    pass


class ScopeMismatchError(CapabilityError):
    pass


class RevokedCapabilityError(CapabilityError):
    pass


class ReplayedCapabilityError(CapabilityError):
    pass


@dataclass(frozen=True)
class CapabilityClaims:
    token_id: str
    issuer: str
    subject: str
    operation: str
    resource: str
    issued_at: int
    expires_at: int


def _encode(content: bytes) -> str:
    return base64.urlsafe_b64encode(content).rstrip(b"=").decode("ascii")


def _decode(content: str) -> bytes:
    padding = "=" * (-len(content) % 4)
    try:
        return base64.b64decode(content + padding, altchars=b"-_", validate=True)
    except (ValueError, TypeError) as error:
        raise InvalidCapabilityError("invalid capability encoding") from error


class CapabilityAuthority:
    def __init__(
        self,
        secret: bytes,
        *,
        issuer: str,
        clock: TrustedClock | None = None,
        max_ttl: timedelta = timedelta(hours=1),
        token_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if len(secret) < 32:
            raise ValueError("capability secret must contain at least 32 bytes")
        if not issuer.strip():
            raise ValueError("issuer must not be empty")
        if max_ttl <= timedelta(0):
            raise ValueError("max_ttl must be positive")
        self._secret = secret
        self._issuer = issuer
        self._clock = clock or TrustedClock()
        self._max_ttl = max_ttl
        self._token_id_factory = token_id_factory or (lambda: secrets.token_hex(16))
        self._revoked: set[str] = set()
        self._consumed: dict[str, int] = {}
        self._lock = threading.Lock()

    def issue(
        self,
        *,
        subject: str,
        operation: str,
        resource: str,
        ttl: timedelta,
    ) -> str:
        for name, value in (("subject", subject), ("operation", operation), ("resource", resource)):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if ttl <= timedelta(0) or ttl > self._max_ttl:
            raise ValueError("ttl must be positive and no greater than max_ttl")
        issued_at = int(self._clock.now().timestamp())
        token_id = self._token_id_factory()
        if not token_id.strip():
            raise ValueError("token_id_factory returned an empty token ID")
        claims = {
            "expires_at": issued_at + int(ttl.total_seconds()),
            "issued_at": issued_at,
            "issuer": self._issuer,
            "operation": operation,
            "resource": resource,
            "subject": subject,
            "token_id": token_id,
            "version": 1,
        }
        payload = _encode(
            json.dumps(claims, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
        )
        signature = _encode(
            hmac.new(self._secret, payload.encode("ascii"), hashlib.sha256).digest()
        )
        return f"{payload}.{signature}"

    def verify(
        self,
        token: str,
        *,
        subject: str,
        operation: str,
        resource: str,
    ) -> CapabilityClaims:
        claims = self._authenticate(token)
        now = int(self._clock.now().timestamp())
        if now >= claims.expires_at:
            raise ExpiredCapabilityError("capability has expired")
        if (claims.subject, claims.operation, claims.resource) != (subject, operation, resource):
            raise ScopeMismatchError("capability scope does not match action")
        with self._lock:
            if claims.token_id in self._revoked:
                raise RevokedCapabilityError("capability has been revoked")
        return claims

    def consume(
        self,
        token: str,
        *,
        subject: str,
        operation: str,
        resource: str,
    ) -> CapabilityClaims:
        claims = self.verify(
            token,
            subject=subject,
            operation=operation,
            resource=resource,
        )
        with self._lock:
            if claims.token_id in self._consumed:
                raise ReplayedCapabilityError("capability has already been consumed")
            self._consumed[claims.token_id] = claims.expires_at
        return claims

    def revoke(self, token_id: str) -> None:
        if not token_id.strip():
            raise ValueError("token_id must not be empty")
        with self._lock:
            self._revoked.add(token_id)

    def sweep_expired(self) -> int:
        """Remove expired entries from the consumed set and return the count removed."""
        now = int(self._clock.now().timestamp())
        with self._lock:
            expired = [tid for tid, exp in self._consumed.items() if now >= exp]
            for tid in expired:
                del self._consumed[tid]
            return len(expired)

    def _authenticate(self, token: str) -> CapabilityClaims:
        parts = token.split(".")
        if len(parts) != 2:
            raise InvalidCapabilityError("capability must contain payload and signature")
        payload, signature_text = parts
        provided = _decode(signature_text)
        expected = hmac.new(self._secret, payload.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(provided, expected):
            raise InvalidCapabilityError("capability signature mismatch")
        try:
            raw = cast(object, json.loads(_decode(payload)))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise InvalidCapabilityError("capability payload is not valid JSON") from error
        return self._claims(raw)

    def _claims(self, raw: object) -> CapabilityClaims:
        if not isinstance(raw, dict) or set(raw) != {
            "expires_at",
            "issued_at",
            "issuer",
            "operation",
            "resource",
            "subject",
            "token_id",
            "version",
        }:
            raise InvalidCapabilityError("capability claims schema mismatch")
        values = cast(dict[str, object], raw)
        if type(values["version"]) is not int or values["version"] != 1:
            raise InvalidCapabilityError("capability version or issuer mismatch")
        token_id = self._string_claim(values, "token_id")
        issuer = self._string_claim(values, "issuer")
        subject = self._string_claim(values, "subject")
        operation = self._string_claim(values, "operation")
        resource = self._string_claim(values, "resource")
        if issuer != self._issuer:
            raise InvalidCapabilityError("capability version or issuer mismatch")
        issued_at = values["issued_at"]
        expires_at = values["expires_at"]
        if type(issued_at) is not int or type(expires_at) is not int:
            raise InvalidCapabilityError("capability time claim is invalid")
        if expires_at <= issued_at:
            raise InvalidCapabilityError("capability expiry must follow issuance")
        return CapabilityClaims(
            token_id=token_id,
            issuer=issuer,
            subject=subject,
            operation=operation,
            resource=resource,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    @staticmethod
    def _string_claim(values: dict[str, object], name: str) -> str:
        value = values[name]
        if not isinstance(value, str) or not value:
            raise InvalidCapabilityError("capability string claim is invalid")
        return value
