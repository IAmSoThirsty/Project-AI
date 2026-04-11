"""
Certificate Manager for mTLS

Handles certificate lifecycle management including generation, rotation,
and validation for mutual TLS authentication.
"""

import os
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


@dataclass
class Certificate:
    """Represents an X.509 certificate"""
    subject: str
    serial_number: int
    not_valid_before: datetime
    not_valid_after: datetime
    public_key_pem: str
    certificate_pem: str
    private_key_pem: Optional[str] = None
    is_ca: bool = False
    fingerprint: str = ""
    
    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = self._calculate_fingerprint()
    
    def _calculate_fingerprint(self) -> str:
        """Calculate SHA256 fingerprint of certificate"""
        cert_bytes = self.certificate_pem.encode('utf-8')
        return hashlib.sha256(cert_bytes).hexdigest()
    
    def is_valid(self) -> bool:
        """Check if certificate is currently valid"""
        now = datetime.utcnow()
        return self.not_valid_before <= now <= self.not_valid_after
    
    def days_until_expiry(self) -> int:
        """Calculate days until certificate expires"""
        delta = self.not_valid_after - datetime.utcnow()
        return max(0, delta.days)


@dataclass
class MTLSConfig:
    """Configuration for mTLS setup"""
    ca_cert_path: str
    cert_path: str
    key_path: str
    verify_client: bool = True
    verify_server: bool = True
    min_tls_version: str = "1.3"
    cipher_suites: List[str] = field(default_factory=lambda: [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
    ])
    cert_rotation_days: int = 30
    key_size: int = 4096


class CertificateManager:
    """
    Manages certificate lifecycle for mTLS
    
    Features:
    - Certificate generation with strong cryptography
    - Automatic rotation before expiry
    - CA certificate management
    - Integration with Vault PKI and cert-manager
    """
    
    def __init__(
        self,
        ca_cert_path: Optional[str] = None,
        ca_key_path: Optional[str] = None,
        storage_backend: str = "filesystem",
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
    ):
        self.ca_cert_path = ca_cert_path
        self.ca_key_path = ca_key_path
        self.storage_backend = storage_backend
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        
        self._ca_cert: Optional[x509.Certificate] = None
        self._ca_key: Optional[rsa.RSAPrivateKey] = None
        
        if ca_cert_path and ca_key_path:
            self._load_ca()
    
    def _load_ca(self):
        """Load CA certificate and private key"""
        try:
            with open(self.ca_cert_path, "rb") as f:
                self._ca_cert = x509.load_pem_x509_certificate(
                    f.read(), default_backend()
                )
            
            with open(self.ca_key_path, "rb") as f:
                self._ca_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            
            logger.info(f"Loaded CA certificate: {self._ca_cert.subject}")
        except Exception as e:
            logger.error(f"Failed to load CA: {e}")
            raise
    
    def create_ca(
        self,
        common_name: str = "Temporal Cloud Root CA",
        organization: str = "Temporal Technologies",
        validity_days: int = 3650,
    ) -> Certificate:
        """
        Create a new Certificate Authority
        
        Args:
            common_name: CA common name
            organization: Organization name
            validity_days: Certificate validity period
        
        Returns:
            Certificate object with CA cert and private key
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend(),
        )
        
        # Create subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build certificate
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )
        
        self._ca_cert = cert
        self._ca_key = private_key
        
        # Serialize certificate and key
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')
        
        pub_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')
        
        logger.info(f"Created CA certificate: {common_name}")
        
        return Certificate(
            subject=common_name,
            serial_number=cert.serial_number,
            not_valid_before=cert.not_valid_before,
            not_valid_after=cert.not_valid_after,
            public_key_pem=pub_key_pem,
            certificate_pem=cert_pem,
            private_key_pem=key_pem,
            is_ca=True,
        )
    
    def issue_certificate(
        self,
        common_name: str,
        organization: str = "Temporal Technologies",
        dns_names: Optional[List[str]] = None,
        ip_addresses: Optional[List[str]] = None,
        validity_days: int = 365,
    ) -> Certificate:
        """
        Issue a new certificate signed by the CA
        
        Args:
            common_name: Certificate common name (service name)
            organization: Organization name
            dns_names: List of DNS SANs
            ip_addresses: List of IP SANs
            validity_days: Certificate validity period
        
        Returns:
            Certificate object with cert and private key
        """
        if not self._ca_cert or not self._ca_key:
            raise ValueError("CA certificate not loaded. Call create_ca() first.")
        
        # Generate private key for service
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        
        # Create subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build SAN extension
        san_list = []
        if dns_names:
            san_list.extend([x509.DNSName(name) for name in dns_names])
        if ip_addresses:
            from ipaddress import ip_address
            san_list.extend([x509.IPAddress(ip_address(ip)) for ip in ip_addresses])
        
        # Build certificate
        cert_builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self._ca_cert.subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                ]),
                critical=True,
            )
        )
        
        if san_list:
            cert_builder = cert_builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )
        
        cert = cert_builder.sign(self._ca_key, hashes.SHA256(), default_backend())
        
        # Serialize certificate and key
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')
        
        pub_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')
        
        logger.info(f"Issued certificate for: {common_name}")
        
        return Certificate(
            subject=common_name,
            serial_number=cert.serial_number,
            not_valid_before=cert.not_valid_before,
            not_valid_after=cert.not_valid_after,
            public_key_pem=pub_key_pem,
            certificate_pem=cert_pem,
            private_key_pem=key_pem,
            is_ca=False,
        )
    
    def save_certificate(
        self,
        cert: Certificate,
        cert_path: str,
        key_path: Optional[str] = None,
    ):
        """Save certificate and optionally private key to files"""
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        
        with open(cert_path, "w") as f:
            f.write(cert.certificate_pem)
        
        if key_path and cert.private_key_pem:
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, "w") as f:
                f.write(cert.private_key_pem)
            # Secure the private key file
            os.chmod(key_path, 0o600)
        
        logger.info(f"Saved certificate to {cert_path}")
    
    def verify_certificate(self, cert_pem: str) -> bool:
        """Verify certificate against CA"""
        if not self._ca_cert:
            raise ValueError("CA certificate not loaded")
        
        try:
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode('utf-8'), default_backend()
            )
            
            # Verify signature
            public_key = self._ca_cert.public_key()
            public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                cert.signature_algorithm_parameters,
            )
            
            # Verify validity period
            now = datetime.utcnow()
            if not (cert.not_valid_before <= now <= cert.not_valid_after):
                logger.warning(f"Certificate expired or not yet valid")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Certificate verification failed: {e}")
            return False
    
    def rotate_certificate(
        self,
        old_cert: Certificate,
        validity_days: int = 365,
    ) -> Certificate:
        """
        Rotate an existing certificate
        
        Args:
            old_cert: Certificate to rotate
            validity_days: New certificate validity period
        
        Returns:
            New Certificate object
        """
        logger.info(f"Rotating certificate for: {old_cert.subject}")
        return self.issue_certificate(
            common_name=old_cert.subject,
            validity_days=validity_days,
        )
    
    def get_certificates_needing_rotation(
        self,
        certificates: List[Certificate],
        rotation_threshold_days: int = 30,
    ) -> List[Certificate]:
        """Get list of certificates that need rotation"""
        return [
            cert for cert in certificates
            if cert.days_until_expiry() <= rotation_threshold_days
        ]
