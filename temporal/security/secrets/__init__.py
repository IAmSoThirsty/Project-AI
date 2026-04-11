"""
Secrets Management

Integration with HashiCorp Vault and Sealed Secrets for secure credential storage.
"""

from .vault_integration import SecretsManager, VaultSecretEngine
from .sealed_secrets import SealedSecretsManager

__all__ = [
    "SecretsManager",
    "VaultSecretEngine",
    "SealedSecretsManager",
]
