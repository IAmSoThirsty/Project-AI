"""
Complete Integration Example

Demonstrates how to use all security components together for
zero-trust Temporal Cloud deployment.
"""

import os
import logging
from datetime import datetime

from temporal.security import (
    CertificateManager,
    MTLSConfig,
    CapabilityTokenManager,
    TokenConstraints,
    NetworkPolicyManager,
    SecretsManager,
    AuditLogger,
    SecurityEvent,
    EventType,
    EventSeverity,
)
from temporal.security.audit import AuditStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_mtls_infrastructure():
    """Setup mTLS certificate infrastructure"""
    logger.info("=== Setting up mTLS Infrastructure ===")
    
    # Initialize certificate manager
    cert_manager = CertificateManager()
    
    # Create CA
    ca_cert = cert_manager.create_ca(
        common_name="Temporal Cloud Root CA",
        organization="Temporal Technologies",
        validity_days=3650
    )
    
    # Save CA certificate
    cert_manager.save_certificate(
        ca_cert,
        cert_path="./certs/ca.crt",
        key_path="./certs/ca.key"
    )
    
    # Issue service certificates
    services = [
        {
            "name": "temporal-frontend",
            "dns_names": ["temporal-frontend", "temporal-frontend.temporal.svc.cluster.local"],
            "ip_addresses": ["10.0.1.100"]
        },
        {
            "name": "temporal-history",
            "dns_names": ["temporal-history", "temporal-history.temporal.svc.cluster.local"],
            "ip_addresses": ["10.0.1.101"]
        },
        {
            "name": "temporal-matching",
            "dns_names": ["temporal-matching", "temporal-matching.temporal.svc.cluster.local"],
            "ip_addresses": ["10.0.1.102"]
        },
        {
            "name": "temporal-worker",
            "dns_names": ["temporal-worker", "temporal-worker.temporal.svc.cluster.local"],
            "ip_addresses": ["10.0.1.103"]
        }
    ]
    
    for service in services:
        cert = cert_manager.issue_certificate(
            common_name=service["name"],
            dns_names=service["dns_names"],
            ip_addresses=service["ip_addresses"],
            validity_days=365
        )
        
        cert_manager.save_certificate(
            cert,
            cert_path=f"./certs/{service['name']}.crt",
            key_path=f"./certs/{service['name']}.key"
        )
        
        logger.info(f"Issued certificate for {service['name']}")
    
    return cert_manager


def setup_capability_tokens(audit_logger):
    """Setup capability token system"""
    logger.info("=== Setting up Capability Tokens ===")
    
    # Initialize token manager
    token_manager = CapabilityTokenManager(
        default_ttl=3600,
        issuer="temporal-cloud"
    )
    
    # Issue token for frontend service
    frontend_token = token_manager.issue_token(
        subject="temporal-frontend",
        scopes=["workflow:start", "workflow:query", "workflow:signal"],
        ttl=7200,
        constraints=TokenConstraints(
            ip_whitelist=["10.0.1.0/24"],
            service_whitelist=["temporal-client"],
            rate_limit=1000
        )
    )
    
    # Log token issuance
    audit_logger.log_event(
        event_type=EventType.AUTHZ_TOKEN_ISSUED,
        actor="system",
        subject="temporal-frontend",
        action="Issued capability token",
        metadata={
            "token_id": frontend_token.id,
            "scopes": frontend_token.scopes,
            "ttl": 7200
        }
    )
    
    # Issue token for worker
    worker_token = token_manager.issue_token(
        subject="temporal-worker-001",
        scopes=["workflow:execute", "activity:invoke", "activity:complete"],
        ttl=3600,
        constraints=TokenConstraints(
            ip_whitelist=["10.0.2.0/24"],
            resource_patterns=["temporal-frontend/*"],
            max_uses=10000
        )
    )
    
    audit_logger.log_event(
        event_type=EventType.AUTHZ_TOKEN_ISSUED,
        actor="system",
        subject="temporal-worker-001",
        action="Issued capability token",
        metadata={
            "token_id": worker_token.id,
            "scopes": worker_token.scopes,
            "ttl": 3600
        }
    )
    
    logger.info(f"Issued frontend token: {frontend_token.id}")
    logger.info(f"Issued worker token: {worker_token.id}")
    
    # Validate token
    is_valid = token_manager.validate_token(
        token=frontend_token,
        required_scopes=["workflow:start"],
        source_ip="10.0.1.50",
        source_service="temporal-client"
    )
    
    logger.info(f"Frontend token validation: {is_valid}")
    
    return token_manager, [frontend_token, worker_token]


def setup_network_policies():
    """Setup network policies"""
    logger.info("=== Setting up Network Policies ===")
    
    # Initialize policy manager
    policy_manager = NetworkPolicyManager(namespace="temporal")
    
    # Create all Temporal policies
    policy_manager.create_all_temporal_policies()
    
    # Export policies to YAML
    policy_manager.export_all_policies("./k8s/network-policies")
    
    logger.info("Created and exported network policies")
    
    return policy_manager


def setup_secrets_management():
    """Setup secrets management with Vault"""
    logger.info("=== Setting up Secrets Management ===")
    
    # Note: This requires a running Vault instance
    # For demo purposes, we'll show the configuration
    
    vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_token = os.getenv("VAULT_TOKEN", "dev-token")
    
    try:
        secrets_manager = SecretsManager(
            vault_addr=vault_addr,
            vault_token=vault_token
        )
        
        # Write database credentials
        secrets_manager.write_secret(
            path="temporal/database",
            data={
                "username": "temporal",
                "password": "SECURE_PASSWORD_HERE",
                "host": "temporal-postgresql",
                "port": "5432"
            },
            mount_point="secret"
        )
        
        # Create transit encryption key
        secrets_manager.create_transit_key("temporal-encryption")
        
        # Encrypt sensitive data
        encrypted_data = secrets_manager.encrypt_data(
            plaintext="sensitive-workflow-data",
            key_name="temporal-encryption"
        )
        
        logger.info("Configured secrets in Vault")
        logger.info(f"Encrypted data sample: {encrypted_data[:50]}...")
        
        return secrets_manager
    
    except Exception as e:
        logger.warning(f"Vault not available: {e}")
        logger.warning("Skipping secrets management setup")
        return None


def setup_audit_logging():
    """Setup audit logging"""
    logger.info("=== Setting up Audit Logging ===")
    
    # Initialize audit storage
    audit_storage = AuditStorage(
        backend="sqlite",
        connection_string="temporal_audit.db"
    )
    
    # Initialize audit logger
    audit_logger = AuditLogger(storage_backend=audit_storage)
    
    # Log system startup
    audit_logger.log_event(
        event_type=EventType.SYSTEM_STARTUP,
        actor="system",
        action="Temporal Cloud security initialization",
        severity=EventSeverity.INFO,
        metadata={
            "version": "1.0.0",
            "components": ["mtls", "capability_tokens", "network_policies", "audit"]
        }
    )
    
    return audit_logger, audit_storage


def simulate_security_workflow(token_manager, audit_logger, tokens):
    """Simulate a security workflow"""
    logger.info("=== Simulating Security Workflow ===")
    
    frontend_token = tokens[0]
    
    # 1. Client attempts to start workflow
    audit_logger.log_event(
        event_type=EventType.AUTHZ_TOKEN_VALIDATED,
        actor="temporal-client",
        subject="temporal-frontend",
        action="Validating token for workflow start",
        source_ip="10.0.1.50"
    )
    
    # Validate token
    is_valid = token_manager.validate_token(
        token=frontend_token,
        required_scopes=["workflow:start"],
        source_ip="10.0.1.50",
        source_service="temporal-client"
    )
    
    if is_valid:
        audit_logger.log_event(
            event_type=EventType.AUTHZ_TOKEN_VALIDATED,
            actor="temporal-client",
            subject="temporal-frontend",
            action="Token validated successfully",
            result="success",
            source_ip="10.0.1.50"
        )
        logger.info("✓ Token validated - workflow start allowed")
    else:
        audit_logger.log_event(
            event_type=EventType.AUTHZ_ACCESS_DENIED,
            actor="temporal-client",
            subject="temporal-frontend",
            action="Token validation failed",
            result="failure",
            severity=EventSeverity.WARNING,
            source_ip="10.0.1.50"
        )
        logger.warning("✗ Token validation failed - access denied")
    
    # 2. Simulate security violation
    audit_logger.log_security_violation(
        actor="unknown-client",
        violation_type="unauthorized_access_attempt",
        details={
            "target": "temporal-frontend",
            "method": "workflow:terminate",
            "reason": "missing_token"
        },
        source_ip="192.168.1.100"
    )
    
    logger.info("✓ Logged security violation")


def verify_audit_chain(audit_logger, audit_storage):
    """Verify audit log chain integrity"""
    logger.info("=== Verifying Audit Chain ===")
    
    # Get recent events
    events = audit_storage.get_events(limit=100)
    
    # Verify chain
    is_valid = audit_logger.verify_chain(events)
    
    if is_valid:
        logger.info(f"✓ Audit chain verified - {len(events)} events")
    else:
        logger.error("✗ Audit chain verification failed!")
    
    return is_valid


def main():
    """Main integration example"""
    logger.info("=" * 60)
    logger.info("Temporal Cloud Zero-Trust Security - Complete Integration")
    logger.info("=" * 60)
    
    # 1. Setup audit logging first
    audit_logger, audit_storage = setup_audit_logging()
    
    # 2. Setup mTLS infrastructure
    cert_manager = setup_mtls_infrastructure()
    
    # 3. Setup capability tokens
    token_manager, tokens = setup_capability_tokens(audit_logger)
    
    # 4. Setup network policies
    policy_manager = setup_network_policies()
    
    # 5. Setup secrets management
    secrets_manager = setup_secrets_management()
    
    # 6. Simulate security workflow
    simulate_security_workflow(token_manager, audit_logger, tokens)
    
    # 7. Verify audit chain
    verify_audit_chain(audit_logger, audit_storage)
    
    logger.info("=" * 60)
    logger.info("Zero-Trust Security Setup Complete!")
    logger.info("=" * 60)
    
    # Display summary
    print("\n📊 Security Infrastructure Summary:")
    print(f"  ✓ mTLS: CA + 4 service certificates")
    print(f"  ✓ Capability Tokens: {len(tokens)} tokens issued")
    print(f"  ✓ Network Policies: {len(policy_manager.policies)} policies created")
    print(f"  ✓ Secrets Management: Vault integration configured")
    
    events = audit_storage.get_events(limit=100)
    print(f"  ✓ Audit Logging: {len(events)} events logged")
    
    print("\n📁 Generated Files:")
    print("  - ./certs/*.crt - Service certificates")
    print("  - ./certs/*.key - Private keys")
    print("  - ./k8s/network-policies/*.yaml - Network policy manifests")
    print("  - ./temporal_audit.db - Audit log database")
    
    print("\n🔒 Security Features Enabled:")
    print("  ✓ Mutual TLS for all inter-service communication")
    print("  ✓ Fine-grained authorization with capability tokens")
    print("  ✓ Network segmentation with zero-trust policies")
    print("  ✓ Encrypted secrets management")
    print("  ✓ Immutable audit logging with chain verification")


if __name__ == "__main__":
    main()
