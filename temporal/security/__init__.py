"""
Zero-Trust Security Framework for Temporal Cloud

This module provides comprehensive security controls including:
- mTLS for inter-service communication
- Capability-based authorization
- Network segmentation
- Secrets management
- Immutable audit logging
"""

from .mtls.cert_manager import CertificateManager, MTLSConfig
from .capability_tokens.token_manager import CapabilityTokenManager, Token
from .network_policies.policy_manager import NetworkPolicyManager
from .secrets.vault_integration import SecretsManager
from .audit.audit_logger import AuditLogger, SecurityEvent

__all__ = [
    "CertificateManager",
    "MTLSConfig",
    "CapabilityTokenManager",
    "Token",
    "NetworkPolicyManager",
    "SecretsManager",
    "AuditLogger",
    "SecurityEvent",
]

__version__ = "1.0.0"
