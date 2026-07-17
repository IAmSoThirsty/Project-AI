"""Domain models for human accounts and sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class AccountRole(StrEnum):
    OWNER = "owner"
    ADMINISTRATOR = "administrator"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"
    VIEWER = "viewer"


@dataclass(frozen=True)
class Account:
    id: str
    username: str
    display_name: str
    password_hash: str
    role: AccountRole
    status: str
    actor_id: str | None
    failed_attempts: int
    locked_until: datetime | None
    created_at: datetime
    password_changed_at: datetime
    mfa_secret_ciphertext: str | None
    mfa_enabled: bool
    mfa_last_counter: int | None
    must_change_password: bool


@dataclass(frozen=True)
class StoredSession:
    id: str
    account_id: str
    token_hash: str
    csrf_hash: str
    created_at: datetime
    last_seen_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    user_agent: str
    client_host: str
    revoked_at: datetime | None
    mfa_verified_at: datetime | None


@dataclass(frozen=True)
class SessionBundle:
    account: Account
    session: StoredSession
    token: str
    csrf_token: str


@dataclass(frozen=True)
class SecurityEvent:
    id: int
    event_type: str
    account_id: str | None
    occurred_at: datetime
    source: str
    detail: str


@dataclass(frozen=True)
class BootstrapResult:
    bundle: SessionBundle
    recovery_codes: tuple[str, ...]


@dataclass(frozen=True)
class MfaEnrollment:
    secret: str
    provisioning_uri: str


@dataclass(frozen=True)
class ManagedAccountResult:
    account: Account
    recovery_codes: tuple[str, ...]
