"""
PKI Backend Integrations

Integrations with external PKI systems like HashiCorp Vault and cert-manager.
"""

import os
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class PKIBackend(ABC):
    """Abstract base class for PKI backends"""
    
    @abstractmethod
    def issue_certificate(
        self,
        common_name: str,
        ttl: str = "8760h",
        **kwargs,
    ) -> Dict[str, str]:
        """Issue a new certificate"""
        pass
    
    @abstractmethod
    def revoke_certificate(self, serial_number: str) -> bool:
        """Revoke a certificate"""
        pass


class VaultPKI(PKIBackend):
    """
    HashiCorp Vault PKI integration
    
    Provides certificate management using Vault's PKI secrets engine.
    """
    
    def __init__(
        self,
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
        pki_path: str = "pki",
        role_name: str = "temporal-service",
    ):
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.pki_path = pki_path
        self.role_name = role_name
        
        if not self.vault_token:
            raise ValueError("Vault token not provided")
        
        self.headers = {
            "X-Vault-Token": self.vault_token,
            "Content-Type": "application/json",
        }
    
    def issue_certificate(
        self,
        common_name: str,
        ttl: str = "8760h",
        alt_names: Optional[str] = None,
        ip_sans: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Issue certificate from Vault PKI
        
        Args:
            common_name: Certificate CN
            ttl: Time to live (e.g., "8760h", "365d")
            alt_names: Comma-separated DNS SANs
            ip_sans: Comma-separated IP SANs
        
        Returns:
            Dict with certificate, private_key, ca_chain
        """
        url = f"{self.vault_addr}/v1/{self.pki_path}/issue/{self.role_name}"
        
        data = {
            "common_name": common_name,
            "ttl": ttl,
        }
        
        if alt_names:
            data["alt_names"] = alt_names
        if ip_sans:
            data["ip_sans"] = ip_sans
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            cert_data = result["data"]
            
            logger.info(f"Issued certificate from Vault for: {common_name}")
            
            return {
                "certificate": cert_data["certificate"],
                "private_key": cert_data["private_key"],
                "ca_chain": "\n".join(cert_data.get("ca_chain", [])),
                "serial_number": cert_data["serial_number"],
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to issue certificate from Vault: {e}")
            raise
    
    def revoke_certificate(self, serial_number: str) -> bool:
        """Revoke certificate in Vault"""
        url = f"{self.vault_addr}/v1/{self.pki_path}/revoke"
        
        data = {"serial_number": serial_number}
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Revoked certificate: {serial_number}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to revoke certificate: {e}")
            return False
    
    def read_ca_certificate(self) -> str:
        """Read CA certificate from Vault"""
        url = f"{self.vault_addr}/v1/{self.pki_path}/ca/pem"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to read CA certificate: {e}")
            raise


class CertManagerBackend(PKIBackend):
    """
    Cert-manager integration for Kubernetes
    
    Generates Kubernetes Certificate resources for cert-manager to process.
    """
    
    def __init__(
        self,
        namespace: str = "temporal",
        issuer_name: str = "temporal-ca-issuer",
        issuer_kind: str = "ClusterIssuer",
    ):
        self.namespace = namespace
        self.issuer_name = issuer_name
        self.issuer_kind = issuer_kind
    
    def generate_certificate_manifest(
        self,
        name: str,
        common_name: str,
        dns_names: Optional[list] = None,
        duration: str = "8760h",
        renew_before: str = "720h",
    ) -> Dict[str, Any]:
        """
        Generate cert-manager Certificate manifest
        
        Args:
            name: Certificate resource name
            common_name: Certificate CN
            dns_names: List of DNS SANs
            duration: Certificate duration
            renew_before: Renewal threshold
        
        Returns:
            Kubernetes Certificate manifest
        """
        manifest = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
            },
            "spec": {
                "secretName": f"{name}-tls",
                "duration": duration,
                "renewBefore": renew_before,
                "subject": {
                    "organizations": ["Temporal Technologies"],
                },
                "commonName": common_name,
                "isCA": False,
                "privateKey": {
                    "algorithm": "RSA",
                    "encoding": "PKCS8",
                    "size": 2048,
                },
                "usages": [
                    "server auth",
                    "client auth",
                    "digital signature",
                    "key encipherment",
                ],
                "issuerRef": {
                    "name": self.issuer_name,
                    "kind": self.issuer_kind,
                    "group": "cert-manager.io",
                },
            },
        }
        
        if dns_names:
            manifest["spec"]["dnsNames"] = dns_names
        
        return manifest
    
    def issue_certificate(
        self,
        common_name: str,
        ttl: str = "8760h",
        **kwargs,
    ) -> Dict[str, str]:
        """Generate certificate manifest (does not issue directly)"""
        manifest = self.generate_certificate_manifest(
            name=common_name.replace(".", "-"),
            common_name=common_name,
            duration=ttl,
            **kwargs,
        )
        
        logger.info(f"Generated cert-manager manifest for: {common_name}")
        
        return {
            "manifest": str(manifest),
            "note": "Apply this manifest to Kubernetes to issue the certificate",
        }
    
    def revoke_certificate(self, serial_number: str) -> bool:
        """Certificate revocation handled by deleting K8s resource"""
        logger.warning("Use kubectl delete to revoke cert-manager certificates")
        return False
