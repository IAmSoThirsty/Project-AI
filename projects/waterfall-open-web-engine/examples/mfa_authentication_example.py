# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / mfa_authentication_example.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / mfa_authentication_example.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
Multi-Factor Authentication (MFA) Example
Demonstrates comprehensive usage of the MFA authentication module
"""

import logging
import time
from thirstys_waterfall.security import (
    MFAAuthenticator,
    AuthMethod,
    AuthLevel,
    RiskLevel,
    BiometricType,
)
from thirstys_waterfall.security.mfa_auth import generate_totp_secret

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def example_basic_authentication():
    """Example 1: Basic authentication flow"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Authentication Flow")
    print("=" * 60)

    # Initialize MFA authenticator
    mfa = MFAAuthenticator()

    # Create authentication context for user session
    context = mfa.create_auth_context(
        user_id="alice@example.com",
        session_id="session_12345",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    )

    print(f"✓ Session created for {context.user_id}")
    print(f"  - Risk level: {context.risk_level.name}")
    print(f"  - Auth level: {context.auth_level.name}")

    return mfa, context


def example_totp_enrollment_and_auth(mfa, user_id):
    """Example 2: TOTP enrollment and authentication"""
    print("\n" + "=" * 60)
    print("Example 2: TOTP Enrollment and Authentication")
    print("=" * 60)

    # Enroll TOTP for user
    secret = generate_totp_secret()
    success, enrollment_data = mfa.enroll_method(
        user_id=user_id, method=AuthMethod.TOTP, credential_data=secret
    )

    if success:
        print(f"✓ TOTP enrolled for {user_id}")
        print(f"  - Secret (base32): {enrollment_data['secret']}")
        print(f"  - Algorithm: {enrollment_data['algorithm']}")
        print(f"  - Digits: {enrollment_data['digits']}")
        print(f"  - Period: {enrollment_data['period']} seconds")
        print(f"  - Provisioning URI: {enrollment_data['provisioning_uri'][:60]}...")

        # Simulate authentication
        # In production, user would provide this from authenticator app
        totp_provider = mfa.providers[AuthMethod.TOTP]
        config = totp_provider._secrets[user_id]
        counter = int(time.time()) // config.period
        valid_token = totp_provider._generate_totp(config, counter)

        print(f"\n  Generated TOTP token: {valid_token}")

        # Create auth context for authentication
        context = mfa.create_auth_context(
            user_id=user_id,
            session_id=f"totp_session_{int(time.time())}",
            ip_address="192.168.1.100",
            user_agent="Test",
        )

        # Authenticate with TOTP
        success, error = mfa.authenticate(
            context=context, method=AuthMethod.TOTP, credential=valid_token
        )

        if success:
            print("✓ TOTP authentication successful")
            print(f"  - Auth level: {context.auth_level.name}")
            print(f"  - Methods: {[m.value for m in context.authenticated_methods]}")
        else:
            print(f"✗ TOTP authentication failed: {error}")


def example_fido2_enrollment(mfa, user_id):
    """Example 3: FIDO2/WebAuthn enrollment"""
    print("\n" + "=" * 60)
    print("Example 3: FIDO2/WebAuthn Enrollment")
    print("=" * 60)

    import base64

    # Simulate FIDO2 credential data (in production, this comes from WebAuthn API)
    credential_data = {
        "credential_id": base64.b64encode(b"fido2_credential_id_12345").decode(),
        "public_key": base64.b64encode(b"fido2_public_key_data_12345").decode(),
        "aaguid": base64.b64encode(b"authenticator_guid").decode(),
    }

    success = mfa.enroll_method(
        user_id=user_id, method=AuthMethod.FIDO2, credential_data=credential_data
    )[0]

    if success:
        print(f"✓ FIDO2 credential enrolled for {user_id}")
        print(f"  - Credential ID: {credential_data['credential_id'][:40]}...")
        print("  - Hardware security key registered")


def example_passkey_enrollment(mfa, user_id):
    """Example 4: Passkey enrollment"""
    print("\n" + "=" * 60)
    print("Example 4: Passkey Enrollment")
    print("=" * 60)

    passkey_data = {
        "device_name": "MacBook Pro",
        "device_key": b"0" * 32,  # In production, derive from device
    }

    success = mfa.enroll_method(
        user_id=user_id, method=AuthMethod.PASSKEY, credential_data=passkey_data
    )[0]

    if success:
        print(f"✓ Passkey enrolled for {user_id}")
        print(f"  - Device: {passkey_data['device_name']}")
        print("  - Passwordless authentication enabled")


def example_biometric_enrollment(mfa, user_id):
    """Example 5: Biometric enrollment"""
    print("\n" + "=" * 60)
    print("Example 5: Biometric Enrollment")
    print("=" * 60)

    # Enroll fingerprint
    biometric_data = {
        "type": BiometricType.FINGERPRINT.value,
        "template": "simulated_fingerprint_template_data_unique_to_user",
        "quality_score": 0.95,
    }

    success = mfa.enroll_method(
        user_id=user_id, method=AuthMethod.BIOMETRIC, credential_data=biometric_data
    )[0]

    if success:
        print(f"✓ Biometric enrolled for {user_id}")
        print(f"  - Type: {biometric_data['type']}")
        print(f"  - Quality: {biometric_data['quality_score']*100:.1f}%")
        print("  - Security: Only hashed template stored (no raw data)")


def example_risk_based_escalation(mfa):
    """Example 6: Risk-based authentication escalation"""
    print("\n" + "=" * 60)
    print("Example 6: Risk-Based Authentication Escalation")
    print("=" * 60)

    # Configure risk assessment
    def assess_risk(context):
        """Custom risk assessment logic"""
        risk_score = 0

        # Check IP reputation
        suspicious_ips = ["1.2.3.4", "5.6.7.8"]
        if context.ip_address in suspicious_ips:
            risk_score += 3

        # Check device fingerprint
        if not context.device_fingerprint:
            risk_score += 2

        # Check for first-time session
        if len(context.previous_sessions) == 0:
            risk_score += 1

        # Map to risk level
        if risk_score >= 4:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    mfa.set_risk_engine_callback(assess_risk)
    print("✓ Risk engine configured")

    # Test with normal user
    normal_context = mfa.create_auth_context(
        user_id="normal_user@example.com",
        session_id="normal_session",
        ip_address="192.168.1.50",
        user_agent="Chrome",
        device_fingerprint="known_device_abc123",
    )

    print("\n  Normal user session:")
    print(f"    - Risk level: {normal_context.risk_level.name}")

    # Test with suspicious user
    suspicious_context = mfa.create_auth_context(
        user_id="suspicious_user@example.com",
        session_id="suspicious_session",
        ip_address="1.2.3.4",  # Suspicious IP
        user_agent="Unknown",
    )

    print("\n  Suspicious user session:")
    print(f"    - Risk level: {suspicious_context.risk_level.name}")
    print(f"    - Risk factors: {suspicious_context.risk_factors}")

    # Check authentication requirements
    escalation_required, missing_methods = mfa.require_escalation(
        context=suspicious_context, target_level=AuthLevel.HIGH
    )

    if escalation_required:
        print("\n  ⚠ Additional authentication required:")
        for method in missing_methods:
            print(f"      - {method.value}")


def example_session_management(mfa):
    """Example 7: Session management"""
    print("\n" + "=" * 60)
    print("Example 7: Session Management")
    print("=" * 60)

    # Create multiple sessions
    sessions = []
    for i in range(3):
        context = mfa.create_auth_context(
            user_id=f"user{i}@example.com",
            session_id=f"session_{i}",
            ip_address=f"192.168.1.{100+i}",
            user_agent="Chrome",
        )
        sessions.append(context.session_id)

    print(f"✓ Created {len(sessions)} sessions")

    # Validate sessions
    print("\n  Session validation:")
    for session_id in sessions:
        valid, ctx = mfa.validate_session(session_id)
        if valid:
            info = mfa.get_session_info(session_id)
            print(f"    ✓ {session_id}: {info['user_id']} - {info['auth_level']}")

    # Invalidate a session
    invalidated_session = sessions[0]
    success = mfa.invalidate_session(invalidated_session)
    if success:
        print(f"\n  ✓ Session {invalidated_session} invalidated")

    # Verify invalidation
    valid, _ = mfa.validate_session(invalidated_session)
    print(f"    - Session now valid: {valid}")


def example_audit_logging(mfa):
    """Example 8: Audit logging"""
    print("\n" + "=" * 60)
    print("Example 8: Audit Logging")
    print("=" * 60)

    # Get recent audit events
    audit_log = mfa.get_audit_log(limit=10)

    print(f"✓ Retrieved {len(audit_log)} audit events\n")

    # Display recent events
    for i, entry in enumerate(audit_log[-5:], 1):
        print(f"  Event {i}:")
        print(f"    - Type: {entry['event']}")
        print(
            f"    - Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))}"
        )
        if entry["context"]:
            print(f"    - User: {entry['context']['user_id']}")
            print(f"    - Risk: {entry['context']['risk_level']}")
        if entry["metadata"]:
            print(f"    - Metadata: {entry['metadata']}")
        print()


def example_method_revocation(mfa, user_id):
    """Example 9: Method revocation"""
    print("\n" + "=" * 60)
    print("Example 9: Authentication Method Revocation")
    print("=" * 60)

    # List current methods (simulated)
    print(f"  Current methods for {user_id}:")
    print("    - TOTP (enrolled)")
    print("    - FIDO2 (enrolled)")
    print("    - Passkey (enrolled)")

    # Revoke TOTP
    success = mfa.revoke_method(
        user_id=user_id, method=AuthMethod.TOTP, credential_id="totp_secret"
    )

    if success:
        print(f"\n  ✓ TOTP method revoked for {user_id}")
        print("    - User must re-enroll to use TOTP")


def example_multi_factor_flow(mfa, user_id):
    """Example 10: Complete multi-factor authentication flow"""
    print("\n" + "=" * 60)
    print("Example 10: Complete Multi-Factor Authentication Flow")
    print("=" * 60)

    # Create session
    context = mfa.create_auth_context(
        user_id=user_id,
        session_id=f"mfa_flow_session_{int(time.time())}",
        ip_address="192.168.1.200",
        user_agent="Chrome/120.0",
    )

    print("✓ Session created")
    print(f"  - Initial auth level: {context.auth_level.name}")
    print(f"  - Initial risk level: {context.risk_level.name}")

    # Step 1: Password (simulated - not implemented in this module)
    print("\n  Step 1: Password authentication")
    context.authenticated_methods.add(AuthMethod.PASSWORD)
    context.auth_level = mfa._calculate_auth_level(context)
    print("    ✓ Password accepted")
    print(f"    - Auth level: {context.auth_level.name}")

    # Step 2: TOTP (we enrolled this earlier)
    print("\n  Step 2: TOTP authentication")
    totp_provider = mfa.providers[AuthMethod.TOTP]
    if user_id in totp_provider._secrets:
        config = totp_provider._secrets[user_id]
        counter = int(time.time()) // config.period
        token = totp_provider._generate_totp(config, counter)

        success, error = mfa.authenticate(context, AuthMethod.TOTP, token)
        if success:
            print("    ✓ TOTP verified")
            print(f"    - Auth level: {context.auth_level.name}")

    # Check if we need escalation for high-security operation
    print("\n  Checking requirements for HIGH security operation:")
    escalation_required, missing_methods = mfa.require_escalation(
        context=context, target_level=AuthLevel.HIGH
    )

    if escalation_required:
        print("    ⚠ Additional authentication required:")
        for method in missing_methods:
            print(f"        - {method.value}")
    else:
        print("    ✓ Current authentication sufficient")
        print(f"    - Auth level: {context.auth_level.name}")


def main():
    """Run all examples"""
    print("\n")
    print("=" * 60)
    print(" Multi-Factor Authentication (MFA) Examples")
    print("=" * 60)

    # Example 1: Basic authentication
    mfa, context = example_basic_authentication()
    user_id = context.user_id

    # Example 2: TOTP
    example_totp_enrollment_and_auth(mfa, user_id)

    # Example 3: FIDO2
    example_fido2_enrollment(mfa, user_id)

    # Example 4: Passkey
    example_passkey_enrollment(mfa, user_id)

    # Example 5: Biometric
    example_biometric_enrollment(mfa, user_id)

    # Example 6: Risk-based escalation
    example_risk_based_escalation(mfa)

    # Example 7: Session management
    example_session_management(mfa)

    # Example 8: Audit logging
    example_audit_logging(mfa)

    # Example 9: Method revocation
    example_method_revocation(mfa, user_id)

    # Example 10: Complete multi-factor flow
    example_multi_factor_flow(mfa, user_id)

    print("\n" + "=" * 60)
    print(" All examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
