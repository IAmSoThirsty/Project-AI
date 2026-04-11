"""
Sealed Secrets Integration

Integration with Bitnami Sealed Secrets for encrypted Kubernetes secrets.
"""

import os
import subprocess
import json
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SealedSecretsManager:
    """
    Manages Sealed Secrets for Kubernetes
    
    Sealed Secrets allows you to encrypt Kubernetes secrets and store them
    in version control. Only the cluster can decrypt them.
    
    Features:
    - Encrypt secrets using cluster's public key
    - Generate sealed secret manifests
    - Support for namespaced and cluster-wide scopes
    """
    
    def __init__(
        self,
        controller_name: str = "sealed-secrets-controller",
        controller_namespace: str = "kube-system",
        kubeseal_binary: str = "kubeseal",
    ):
        self.controller_name = controller_name
        self.controller_namespace = controller_namespace
        self.kubeseal_binary = kubeseal_binary
        
        # Check if kubeseal is available
        self._verify_kubeseal()
    
    def _verify_kubeseal(self):
        """Verify kubeseal binary is available"""
        try:
            subprocess.run(
                [self.kubeseal_binary, "--version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(
                f"kubeseal binary not found. Install from: "
                f"https://github.com/bitnami-labs/sealed-secrets/releases"
            )
    
    def create_secret_manifest(
        self,
        name: str,
        namespace: str,
        data: Dict[str, str],
        secret_type: str = "Opaque",
    ) -> Dict[str, Any]:
        """
        Create Kubernetes Secret manifest
        
        Args:
            name: Secret name
            namespace: Namespace
            data: Secret data (key-value pairs)
            secret_type: Secret type
        
        Returns:
            Secret manifest dictionary
        """
        import base64
        
        # Base64 encode all values
        encoded_data = {
            key: base64.b64encode(value.encode('utf-8')).decode('utf-8')
            for key, value in data.items()
        }
        
        manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": namespace,
            },
            "type": secret_type,
            "data": encoded_data,
        }
        
        return manifest
    
    def seal_secret(
        self,
        secret_manifest: Dict[str, Any],
        scope: str = "strict",
        output_format: str = "yaml",
    ) -> str:
        """
        Seal a secret using kubeseal
        
        Args:
            secret_manifest: Kubernetes Secret manifest
            scope: Sealing scope (strict, namespace-wide, cluster-wide)
            output_format: Output format (yaml or json)
        
        Returns:
            Sealed secret manifest as string
        """
        # Convert manifest to YAML
        secret_yaml = yaml.dump(secret_manifest)
        
        # Run kubeseal
        cmd = [
            self.kubeseal_binary,
            "--format", output_format,
            "--scope", scope,
            "--controller-name", self.controller_name,
            "--controller-namespace", self.controller_namespace,
        ]
        
        try:
            result = subprocess.run(
                cmd,
                input=secret_yaml.encode('utf-8'),
                capture_output=True,
                check=True,
            )
            
            sealed_secret = result.stdout.decode('utf-8')
            logger.info(f"Sealed secret {secret_manifest['metadata']['name']}")
            
            return sealed_secret
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to seal secret: {e.stderr.decode('utf-8')}")
            raise
    
    def create_sealed_secret(
        self,
        name: str,
        namespace: str,
        data: Dict[str, str],
        scope: str = "strict",
        output_file: Optional[str] = None,
    ) -> str:
        """
        Create and seal a secret in one step
        
        Args:
            name: Secret name
            namespace: Namespace
            data: Secret data
            scope: Sealing scope
            output_file: Optional file to write sealed secret
        
        Returns:
            Sealed secret YAML
        """
        # Create secret manifest
        secret_manifest = self.create_secret_manifest(name, namespace, data)
        
        # Seal it
        sealed_secret = self.seal_secret(secret_manifest, scope=scope)
        
        # Optionally write to file
        if output_file:
            with open(output_file, "w") as f:
                f.write(sealed_secret)
            logger.info(f"Wrote sealed secret to {output_file}")
        
        return sealed_secret
    
    def fetch_certificate(self) -> str:
        """
        Fetch the sealing certificate from the controller
        
        Returns:
            Public certificate PEM
        """
        cmd = [
            self.kubeseal_binary,
            "--fetch-cert",
            "--controller-name", self.controller_name,
            "--controller-namespace", self.controller_namespace,
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            cert = result.stdout.decode('utf-8')
            logger.info("Fetched sealing certificate")
            return cert
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch certificate: {e.stderr.decode('utf-8')}")
            raise
    
    def rotate_secret(
        self,
        name: str,
        namespace: str,
        new_data: Dict[str, str],
    ) -> str:
        """
        Rotate a sealed secret by creating a new one
        
        Args:
            name: Secret name
            namespace: Namespace
            new_data: New secret data
        
        Returns:
            New sealed secret YAML
        """
        logger.info(f"Rotating sealed secret {name} in {namespace}")
        return self.create_sealed_secret(name, namespace, new_data)


def create_temporal_sealed_secrets(
    manager: SealedSecretsManager,
    namespace: str = "temporal",
) -> Dict[str, str]:
    """
    Create sealed secrets for Temporal services
    
    Args:
        manager: SealedSecretsManager instance
        namespace: Kubernetes namespace
    
    Returns:
        Dict of secret names to sealed secret YAML
    """
    sealed_secrets = {}
    
    # Database credentials
    db_secret = manager.create_sealed_secret(
        name="temporal-database-credentials",
        namespace=namespace,
        data={
            "username": "temporal",
            "password": "CHANGEME_SECURE_PASSWORD",
            "host": "temporal-postgresql",
            "port": "5432",
        },
    )
    sealed_secrets["temporal-database-credentials"] = db_secret
    
    # mTLS certificates (example - in practice, use cert-manager)
    mtls_secret = manager.create_sealed_secret(
        name="temporal-mtls-certs",
        namespace=namespace,
        data={
            "ca.crt": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
            "tls.crt": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
            "tls.key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
        },
    )
    sealed_secrets["temporal-mtls-certs"] = mtls_secret
    
    # API keys
    api_secret = manager.create_sealed_secret(
        name="temporal-api-keys",
        namespace=namespace,
        data={
            "frontend-api-key": "CHANGEME_API_KEY",
            "admin-api-key": "CHANGEME_ADMIN_KEY",
        },
    )
    sealed_secrets["temporal-api-keys"] = api_secret
    
    logger.info(f"Created {len(sealed_secrets)} sealed secrets for Temporal")
    
    return sealed_secrets
