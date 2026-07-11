"""
cerberus.security — Enterprise security modules (Cerberus Guard Bot port).

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/security/``,
stdlib-only subset (no new workspace dependencies):

- input_validation — attack-vector detection + sanitization
- rbac — role-based access control
- rate_limiter — token-bucket / sliding-window rate limiting
- threat_detector — signature + behavioral threat detection
- audit_logger — HMAC-signed tamper-evident audit logging
- auth — PBKDF2 password hashing, policy, sessions, lockout
- monitoring — alerts, metric anomaly detection, Prometheus export

Deferred (not ported): ``encryption`` (needs the ``cryptography`` package as a
declared dependency) and ``sandbox`` (Unix-only ``resource`` limits plus
arbitrary-code ``exec``; out of scope for the canonical governance surface).
"""

from cerberus.security.modules.audit_logger import (
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
)
from cerberus.security.modules.auth import (
    AuthManager,
    PasswordHasher,
    PasswordPolicy,
    Session,
)
from cerberus.security.modules.input_validation import (
    AttackType,
    InputValidator,
    ValidationResult,
)
from cerberus.security.modules.monitoring import (
    Alert,
    AlertManager,
    AlertSeverity,
    SecurityMonitor,
)
from cerberus.security.modules.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitExceeded,
    rate_limit,
)
from cerberus.security.modules.rbac import (
    Permission,
    PermissionDenied,
    RBACManager,
    Role,
)
from cerberus.security.modules.threat_detector import (
    ThreatCategory,
    ThreatDetectionResult,
    ThreatDetector,
    ThreatLevel,
)

__all__ = [
    "Alert",
    "AlertManager",
    "AlertSeverity",
    "AttackType",
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "AuditSeverity",
    "AuthManager",
    "InputValidator",
    "PasswordHasher",
    "PasswordPolicy",
    "Permission",
    "PermissionDenied",
    "RBACManager",
    "RateLimitConfig",
    "RateLimitExceeded",
    "RateLimiter",
    "Role",
    "SecurityMonitor",
    "Session",
    "ThreatCategory",
    "ThreatDetectionResult",
    "ThreatDetector",
    "ThreatLevel",
    "ValidationResult",
    "rate_limit",
]
