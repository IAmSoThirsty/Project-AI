# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Cerberus Security Module

Comprehensive security features for AI/AGI system protection including:
- Input validation and sanitization
- Audit logging with tamper detection
- Rate limiting and egress controls
- Role-Based Access Control (RBAC)
- Encryption at rest
- Agent/plugin sandboxing
- Threat detection
- Monitoring and alerting
"""

from .modules.audit_logger import AuditEvent, AuditLogger
from .modules.auth import AuthManager, PasswordHasher
from .modules.encryption import EncryptionManager, KeyManager
from .modules.input_validation import InputValidator, ValidationResult
from .modules.monitoring import AlertManager, SecurityMonitor
from .modules.rate_limiter import RateLimiter, rate_limit
from .modules.rbac import Permission, RBACManager, Role
from .modules.sandbox import AgentSandbox, PluginSandbox
from .modules.threat_detector import ThreatDetector, ThreatLevel

__all__ = [
    "InputValidator",
    "ValidationResult",
    "AuditLogger",
    "AuditEvent",
    "RateLimiter",
    "rate_limit",
    "RBACManager",
    "Role",
    "Permission",
    "EncryptionManager",
    "KeyManager",
    "AuthManager",
    "PasswordHasher",
    "ThreatDetector",
    "ThreatLevel",
    "SecurityMonitor",
    "AlertManager",
    "AgentSandbox",
    "PluginSandbox",
]
