# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

"""
PSIA Cryptographic Primitives.

Production-grade Ed25519 signing/verification and RFC 3161 timestamp
authority for the Project-AI Sovereign Immune Architecture.

Modules:
    ed25519_provider  — Key generation, signing, verification via PyCA cryptography
    rfc3161_provider  — Local RFC 3161-compliant Timestamp Authority
"""

from psia.crypto.ed25519_provider import Ed25519KeyPair, Ed25519Provider, KeyStore

__all__ = [
    "Ed25519KeyPair",
    "Ed25519Provider",
    "KeyStore",
]
