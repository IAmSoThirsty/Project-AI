# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_mfa_auth.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_mfa_auth.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Tests for Multi-Factor Authentication module
"""

import unittest
import time
import base64
import threading
from datetime import datetime, timedelta

from thirstys_waterfall.security.mfa_auth import (
    MFAAuthenticator,
    AuthContext,
    AuthMethod,
    AuthLevel,
    RiskLevel,
    BiometricType,
    TOTPProvider,
    FIDO2Provider,
    PasskeyProvider,
    CertificateProvider,
    BiometricProvider,
    generate_totp_secret,
)

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID


class TestMFAAuthenticator(unittest.TestCase):
    """Test MFAAuthenticator core functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mfa = MFAAuthenticator()
        self.user_id = "test_user_123"
        self.session_id = "test_session_abc"

    def test_initialization(self):
        """Test MFA authenticator initialization"""
        self.assertIsInstance(self.mfa, MFAAuthenticator)
        self.assertIn(AuthMethod.TOTP, self.mfa.providers)
        self.assertIn(AuthMethod.FIDO2, self.mfa.providers)
        self.assertIn(AuthMethod.PASSKEY, self.mfa.providers)
        self.assertIn(AuthMethod.CERTIFICATE, self.mfa.providers)
        self.assertIn(AuthMethod.BIOMETRIC, self.mfa.providers)

    def test_create_auth_context(self):
        """Test authentication context creation"""
        context = self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        self.assertEqual(context.user_id, self.user_id)
        self.assertEqual(context.session_id, self.session_id)
        self.assertEqual(context.auth_level, AuthLevel.NONE)
        self.assertIsInstance(context.risk_level, RiskLevel)
        self.assertEqual(len(context.authenticated_methods), 0)

    def test_session_validation(self):
        """Test session validation"""
        self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        # Session should be valid initially
        valid, ctx = self.mfa.validate_session(self.session_id)
        self.assertTrue(valid)
        self.assertIsNotNone(ctx)

    def test_session_invalidation(self):
        """Test session invalidation"""
        self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        # Invalidate session
        success = self.mfa.invalidate_session(self.session_id)
        self.assertTrue(success)

        # Session should now be invalid
        valid, _ = self.mfa.validate_session(self.session_id)
        self.assertFalse(valid)

    def test_risk_level_update(self):
        """Test risk level updates"""
        context = self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        initial_risk = context.risk_level
        self.mfa.update_risk_level(context, RiskLevel.EXTREME)

        self.assertEqual(context.risk_level, RiskLevel.EXTREME)
        self.assertNotEqual(initial_risk, context.risk_level)

    def test_get_session_info(self):
        """Test session info retrieval"""
        self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        info = self.mfa.get_session_info(self.session_id)

        self.assertIsNotNone(info)
        self.assertEqual(info["user_id"], self.user_id)
        self.assertIn("auth_level", info)
        self.assertIn("risk_level", info)
        self.assertIn("expires_at", info)

    def test_audit_log(self):
        """Test audit logging"""
        self.mfa.create_auth_context(
            user_id=self.user_id,
            session_id=self.session_id,
            ip_address="192.168.1.100",
            user_agent="Test Browser",
        )

        audit_log = self.mfa.get_audit_log(limit=10)

        self.assertIsInstance(audit_log, list)
        self.assertGreater(len(audit_log), 0)
        self.assertIn("timestamp", audit_log[0])
        self.assertIn("event", audit_log[0])


class TestTOTPProvider(unittest.TestCase):
    """Test TOTP authentication provider"""

    def setUp(self):
        """Set up test fixtures"""
        self.provider = TOTPProvider()
        self.user_id = "totp_test_user"

    def test_enrollment(self):
        """Test TOTP enrollment"""
        success, enrollment_data = self.provider.enroll(self.user_id)

        self.assertTrue(success)
        self.assertIsNotNone(enrollment_data)
        self.assertIn("secret", enrollment_data)
        self.assertIn("provisioning_uri", enrollment_data)
        self.assertIn("algorithm", enrollment_data)
        self.assertEqual(enrollment_data["digits"], 6)

    def test_totp_generation(self):
        """Test TOTP token generation"""
        secret = generate_totp_secret()
        success, enrollment_data = self.provider.enroll(self.user_id, secret)

        self.assertTrue(success)

        # Generate token
        config = self.provider._secrets[self.user_id]
        counter = int(time.time()) // config.period
        token = self.provider._generate_totp(config, counter)

        self.assertEqual(len(token), 6)
        self.assertTrue(token.isdigit())

    def test_totp_authentication(self):
        """Test TOTP authentication"""
        secret = generate_totp_secret()
        self.provider.enroll(self.user_id, secret)

        # Create auth context
        from thirstys_waterfall.security.mfa_auth import AuthContext

        context = AuthContext(
            user_id=self.user_id,
            session_id="totp_session",
            ip_address="127.0.0.1",
            user_agent="Test",
        )

        # Generate valid token
        config = self.provider._secrets[self.user_id]
        counter = int(time.time()) // config.period
        valid_token = self.provider._generate_totp(config, counter)

        # Should authenticate successfully
        result = self.provider.authenticate(valid_token, context)
        self.assertTrue(result)

        # Same token should fail (replay protection)
        result = self.provider.authenticate(valid_token, context)
        self.assertFalse(result)

    def test_totp_revocation(self):
        """Test TOTP revocation"""
        self.provider.enroll(self.user_id)

        success = self.provider.revoke(self.user_id)
        self.assertTrue(success)

        # Should not be able to authenticate after revocation
        self.assertNotIn(self.user_id, self.provider._secrets)


class TestFIDO2Provider(unittest.TestCase):
    """Test FIDO2/WebAuthn provider"""

    def setUp(self):
        """Set up test fixtures"""
        self.provider = FIDO2Provider()
        self.user_id = "fido2_test_user"

    def test_enrollment(self):
        """Test FIDO2 credential enrollment"""
        credential_data = {
            "credential_id": base64.b64encode(b"test_credential_id").decode(),
            "public_key": base64.b64encode(b"test_public_key_data").decode(),
            "aaguid": base64.b64encode(b"test_aaguid_data").decode(),
        }

        success = self.provider.enroll(self.user_id, credential_data)
        self.assertTrue(success)
        self.assertIn(self.user_id, self.provider._credentials)

    def test_challenge_generation(self):
        """Test challenge generation"""
        challenge = self.provider.generate_challenge(self.user_id)

        self.assertIsInstance(challenge, bytes)
        self.assertEqual(len(challenge), 32)
        self.assertIn(self.user_id, self.provider._challenges)

    def test_credential_revocation(self):
        """Test credential revocation"""
        credential_data = {
            "credential_id": base64.b64encode(b"test_credential_id").decode(),
            "public_key": base64.b64encode(b"test_public_key_data").decode(),
            "aaguid": base64.b64encode(b"test_aaguid_data").decode(),
        }

        self.provider.enroll(self.user_id, credential_data)

        success = self.provider.revoke(self.user_id, credential_data["credential_id"])
        self.assertTrue(success)


class TestPasskeyProvider(unittest.TestCase):
    """Test Passkey provider"""

    def setUp(self):
        """Set up test fixtures"""
        self.provider = PasskeyProvider()
        self.user_id = "passkey_test_user"

    def test_enrollment(self):
        """Test passkey enrollment"""
        credential_data = {
            "device_name": "Test Device",
            "device_key": b"0" * 32,
        }

        success = self.provider.enroll(self.user_id, credential_data)
        self.assertTrue(success)
        self.assertIn(self.user_id, self.provider._passkeys)

    def test_passkey_revocation(self):
        """Test passkey revocation"""
        credential_data = {
            "device_name": "Test Device",
            "device_key": b"0" * 32,
        }

        self.provider.enroll(self.user_id, credential_data)
        passkey_id = self.provider._passkeys[self.user_id][0].passkey_id

        success = self.provider.revoke(self.user_id, passkey_id)
        self.assertTrue(success)


class TestCertificateProvider(unittest.TestCase):
    """Test X.509 certificate provider"""

    def setUp(self):
        """Set up test fixtures"""
        self.provider = CertificateProvider()
        self.user_id = "cert_test_user"
        self.cert_pem = self._generate_test_certificate()

    def _generate_test_certificate(self):
        """Generate a test certificate"""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Test"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Thirstys Waterfall"),
                x509.NameAttribute(NameOID.COMMON_NAME, "test_user"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now())
            .not_valid_after(datetime.now() + timedelta(days=365))
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        return cert.public_bytes(serialization.Encoding.PEM)

    def test_enrollment(self):
        """Test certificate enrollment"""
        success = self.provider.enroll(self.user_id, self.cert_pem)
        self.assertTrue(success)
        self.assertIn(self.user_id, self.provider._certificates)

    def test_certificate_validation(self):
        """Test certificate validation"""
        cert = x509.load_pem_x509_certificate(self.cert_pem, default_backend())
        valid = self.provider._validate_certificate(cert)
        self.assertTrue(valid)


class TestBiometricProvider(unittest.TestCase):
    """Test biometric authentication provider"""

    def setUp(self):
        """Set up test fixtures"""
        self.provider = BiometricProvider()
        self.user_id = "biometric_test_user"

    def test_enrollment(self):
        """Test biometric enrollment"""
        credential_data = {
            "type": BiometricType.FINGERPRINT.value,
            "template": "test_fingerprint_template_data",
            "quality_score": 0.95,
        }

        success = self.provider.enroll(self.user_id, credential_data)
        self.assertTrue(success)
        self.assertIn(self.user_id, self.provider._templates)

    def test_biometric_revocation(self):
        """Test biometric template revocation"""
        credential_data = {
            "type": BiometricType.FINGERPRINT.value,
            "template": "test_fingerprint_template_data",
            "quality_score": 0.95,
        }

        self.provider.enroll(self.user_id, credential_data)
        template_id = self.provider._templates[self.user_id][0].template_id

        success = self.provider.revoke(self.user_id, template_id)
        self.assertTrue(success)


class TestAuthLevelCalculation(unittest.TestCase):
    """Test authentication level calculation"""

    def setUp(self):
        """Set up test fixtures"""
        self.mfa = MFAAuthenticator()

    def test_no_auth(self):
        """Test no authentication"""
        context = AuthContext(
            user_id="test", session_id="test", ip_address="127.0.0.1", user_agent="Test"
        )

        level = self.mfa._calculate_auth_level(context)
        self.assertEqual(level, AuthLevel.NONE)

    def test_single_factor(self):
        """Test single factor authentication"""
        context = AuthContext(
            user_id="test", session_id="test", ip_address="127.0.0.1", user_agent="Test"
        )
        context.authenticated_methods.add(AuthMethod.PASSWORD)

        level = self.mfa._calculate_auth_level(context)
        self.assertEqual(level, AuthLevel.BASIC)

    def test_two_factor(self):
        """Test two-factor authentication"""
        context = AuthContext(
            user_id="test", session_id="test", ip_address="127.0.0.1", user_agent="Test"
        )
        context.authenticated_methods.add(AuthMethod.PASSWORD)
        context.authenticated_methods.add(AuthMethod.TOTP)

        level = self.mfa._calculate_auth_level(context)
        self.assertEqual(level, AuthLevel.STANDARD)

    def test_hardware_auth(self):
        """Test hardware-based authentication"""
        context = AuthContext(
            user_id="test", session_id="test", ip_address="127.0.0.1", user_agent="Test"
        )
        context.authenticated_methods.add(AuthMethod.PASSWORD)
        context.authenticated_methods.add(AuthMethod.FIDO2)

        level = self.mfa._calculate_auth_level(context)
        self.assertEqual(level, AuthLevel.ELEVATED)

    def test_biometric_auth(self):
        """Test biometric authentication"""
        context = AuthContext(
            user_id="test", session_id="test", ip_address="127.0.0.1", user_agent="Test"
        )
        context.authenticated_methods.add(AuthMethod.PASSWORD)
        context.authenticated_methods.add(AuthMethod.FIDO2)
        context.authenticated_methods.add(AuthMethod.BIOMETRIC)

        level = self.mfa._calculate_auth_level(context)
        self.assertEqual(level, AuthLevel.HIGH)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of MFA operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mfa = MFAAuthenticator()

    def test_concurrent_session_creation(self):
        """Test concurrent session creation"""
        results = []

        def create_session(user_num):
            try:
                context = self.mfa.create_auth_context(
                    user_id=f"user_{user_num}",
                    session_id=f"session_{user_num}",
                    ip_address="127.0.0.1",
                    user_agent="Test",
                )
                results.append(context.session_id)
            except Exception:
                results.append(None)

        threads = [
            threading.Thread(target=create_session, args=(i,)) for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All sessions should be created successfully
        self.assertEqual(len([r for r in results if r is not None]), 20)

    def test_concurrent_enrollment(self):
        """Test concurrent method enrollment"""
        results = []

        def enroll_method(user_num):
            try:
                success, _ = self.mfa.enroll_method(
                    user_id=f"user_{user_num}",
                    method=AuthMethod.TOTP,
                    credential_data=generate_totp_secret(),
                )
                results.append(success)
            except Exception:
                results.append(False)

        threads = [threading.Thread(target=enroll_method, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All enrollments should succeed
        self.assertEqual(sum(results), 20)


class TestRiskEngineIntegration(unittest.TestCase):
    """Test Privacy Risk Engine integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.mfa = MFAAuthenticator()

    def test_risk_callback(self):
        """Test risk engine callback"""

        def mock_risk_callback(context):
            if "suspicious" in context.ip_address:
                return RiskLevel.EXTREME
            return RiskLevel.LOW

        self.mfa.set_risk_engine_callback(mock_risk_callback)

        # Create normal context
        normal_context = self.mfa.create_auth_context(
            user_id="test_user",
            session_id="normal_session",
            ip_address="192.168.1.1",
            user_agent="Test",
        )
        self.assertEqual(normal_context.risk_level, RiskLevel.LOW)

        # Create suspicious context
        suspicious_context = self.mfa.create_auth_context(
            user_id="test_user",
            session_id="suspicious_session",
            ip_address="suspicious_ip",
            user_agent="Test",
        )
        self.assertEqual(suspicious_context.risk_level, RiskLevel.EXTREME)


if __name__ == "__main__":
    unittest.main()
