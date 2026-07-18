"""
cerberus.security — Enterprise security modules (Cerberus Guard Bot port).

Ported from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/security/``:

- input_validation — attack-vector detection + sanitization
- rbac — role-based access control
- rate_limiter — token-bucket / sliding-window rate limiting
- threat_detector — signature + behavioral threat detection
- audit_logger — HMAC-signed tamper-evident audit logging
- auth — PBKDF2 password hashing, policy, sessions, lockout
- monitoring — alerts, metric anomaly detection, Prometheus export
- encryption — Fernet encryption at rest with key rotation
  (requires ``cryptography``, declared)
- sandbox — restricted-execution helpers (see its honest-scope docstring:
  guard rails and subprocess/container isolation, not a governance boundary)

``encryption`` and ``sandbox`` were previously documented as deferred; the
C1 reconciliation wave (``docs/operations/CERBERUS_RECONCILIATION_MATRIX.md``)
completed both ports from the standalone guard-bot repo.
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
from cerberus.security.modules.encryption import (
    EncryptionKey,
    EncryptionManager,
    KeyManager,
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
from cerberus.security.modules.sandbox import (
    AgentSandbox,
    ContainerSandbox,
    PluginSandbox,
    SandboxConfig,
    SandboxViolation,
)
from cerberus.security.modules.threat_detector import (
    ThreatCategory,
    ThreatDetectionResult,
    ThreatDetector,
    ThreatLevel,
)

__all__ = [
    "AgentSandbox",
    "Alert",
    "AlertManager",
    "AlertSeverity",
    "AttackType",
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "AuditSeverity",
    "AuthManager",
    "ContainerSandbox",
    "EncryptionKey",
    "EncryptionManager",
    "InputValidator",
    "KeyManager",
    "PasswordHasher",
    "PasswordPolicy",
    "Permission",
    "PermissionDenied",
    "PluginSandbox",
    "RBACManager",
    "RateLimitConfig",
    "RateLimitExceeded",
    "RateLimiter",
    "Role",
    "SandboxConfig",
    "SandboxViolation",
    "SecurityMonitor",
    "Session",
    "ThreatCategory",
    "ThreatDetectionResult",
    "ThreatDetector",
    "ThreatLevel",
    "ValidationResult",
    "rate_limit",
]
