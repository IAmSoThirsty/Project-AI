# H.323 Secure Coding & Extension Development Guidelines

Version 1.0 — Developer Standards for Custom H.323 Extensions

## 1. Purpose

Defines secure development practices for custom H.323 extensions, plugins, or integrations to ensure they do not compromise the security posture of the H.323 deployment.

---

## 2. Secure Coding Requirements

### 2.1 Input Validation

**Validate All H.225/H.245 Fields**:
```python
def validate_h225_setup(setup_msg):

    # Validate source address

    if not validate_h323_id(setup_msg.source_address):
        raise SecurityError("Invalid source H.323 ID")

    # Validate destination address

    if not validate_e164(setup_msg.dest_address):
        raise SecurityError("Invalid E.164 number")

    # Validate call ID format

    if not validate_call_id(setup_msg.call_id):
        raise SecurityError("Invalid call ID")

    # Validate no SQL injection in aliases

    if contains_sql_injection(setup_msg.alias):
        raise SecurityError("SQL injection detected in alias")
```

**Field Length Limits**:
```python
MAX_H323_ID_LENGTH = 128
MAX_E164_LENGTH = 15
MAX_CALL_ID_LENGTH = 64

def validate_field_length(field, max_length, field_name):
    if len(field) > max_length:
        raise SecurityError(f"{field_name} exceeds max length {max_length}")
```

### 2.2 H.235 Enforcement

**Always Enforce H.235 Profiles**:
```python
def setup_call(endpoint, destination):

    # Validate endpoint certificate

    if not validate_certificate(endpoint.certificate):
        raise SecurityError("Endpoint certificate invalid")

    # Require H.235.3 for H.225

    if not endpoint.supports_h235_3():
        raise SecurityError("H.235.3 not supported")

    # Require SRTP for media

    if not endpoint.supports_srtp():
        raise SecurityError("SRTP not supported")

    # Proceed with secure call setup

    call = initiate_secure_call(endpoint, destination)
    return call
```

**Never Bypass Security**:
```python

# WRONG: Allowing insecure fallback

def setup_call_insecure(endpoint, destination):
    try:
        return setup_secure_call(endpoint, destination)
    except SecurityError:
        return setup_cleartext_call(endpoint, destination)  # NEVER DO THIS

# CORRECT: Fail closed on security errors

def setup_call_secure(endpoint, destination):
    try:
        return setup_secure_call(endpoint, destination)
    except SecurityError as e:
        log_security_event("call_setup_failed", endpoint.id, str(e))
        raise  # Propagate error, do not fallback
```

### 2.3 PKI Integration

**Use Enterprise PKI**:
```python
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def validate_certificate(cert_pem):

    # Load certificate

    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

    # Check issuer (must be Voice/Video CA)

    if cert.issuer.rfc4514_string() != "CN=Voice-Video-CA,O=Example Corp":
        return False

    # Check SAN

    san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
    if not san_ext:
        return False

    # Check expiration

    if cert.not_valid_after < datetime.utcnow():
        return False

    # Check revocation status

    if is_revoked(cert):
        return False

    return True
```

**CRL/OCSP Checking**:
```python
import requests

def check_ocsp(cert):
    ocsp_url = get_ocsp_url_from_cert(cert)
    ocsp_request = build_ocsp_request(cert)

    response = requests.post(ocsp_url, data=ocsp_request, timeout=5)

    if response.status_code != 200:
        raise SecurityError("OCSP server unreachable")

    ocsp_response = parse_ocsp_response(response.content)

    if ocsp_response.status == "revoked":
        raise SecurityError("Certificate revoked")

    return ocsp_response.status == "good"
```

### 2.4 Secure Transport

**Always Use TLS/IPsec**:
```python
import ssl

def connect_to_gatekeeper(gk_address):
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM')

    # Load client certificate for mutual TLS

    context.load_cert_chain('endpoint.pem', 'endpoint-key.pem')

    # Load CA bundle

    context.load_verify_locations('ca-bundle.pem')

    # Connect

    conn = context.wrap_socket(socket.socket(), server_hostname=gk_address)
    conn.connect((gk_address, 1720))

    return conn
```

### 2.5 Avoid Custom Crypto

**Use Standard Libraries**:
```python

# WRONG: Custom SRTP implementation

def custom_srtp_encrypt(plaintext, key):

    # ... custom encryption logic ...

    pass  # NEVER DO THIS

# CORRECT: Use standard library

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def srtp_encrypt(plaintext, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, encryptor.tag
```

### 2.6 Input Sanitization

**Sanitize All User Inputs**:
```python
import re

def sanitize_h323_id(h323_id):

    # Allow only alphanumeric, dash, underscore

    if not re.match(r'^[a-zA-Z0-9_-]+$', h323_id):
        raise SecurityError("Invalid characters in H.323 ID")
    return h323_id

def sanitize_e164(e164):

    # Allow only digits and leading +

    if not re.match(r'^\+?[0-9]+$', e164):
        raise SecurityError("Invalid E.164 format")
    return e164
```

**Prevent SQL Injection**:
```python

# WRONG: String concatenation

def get_endpoint_by_id(h323_id):
    query = f"SELECT * FROM endpoints WHERE h323_id = '{h323_id}'"
    return db.execute(query)  # SQL INJECTION RISK

# CORRECT: Parameterized query

def get_endpoint_by_id(h323_id):
    query = "SELECT * FROM endpoints WHERE h323_id = ?"
    return db.execute(query, (h323_id,))
```

---

## 3. Extension Development Rules

### 3.1 Must Not Weaken H.235

**Prohibited Actions**:

- Disabling H.235.2/3/4/6
- Allowing RTP fallback
- Bypassing certificate validation
- Accepting expired certificates
- Accepting revoked certificates
- Downgrading cipher suites

**Correct Pattern**:
```python
class H323Extension:
    def before_call_setup(self, call):

        # Extension can add functionality

        # but MUST NOT weaken security

        # Validate security posture

        if not call.h235_enabled():
            raise SecurityError("H.235 not enabled")

        if not call.srtp_enabled():
            raise SecurityError("SRTP not enabled")

        # Extension logic here

        self.log_call_attempt(call)
```

### 3.2 Must Not Bypass Gatekeeper

**Prohibited Actions**:

- Direct endpoint-to-endpoint signaling without GK knowledge
- Accepting calls without ARQ/ACF
- Bypassing admission control

**Correct Pattern**:
```python
def initiate_call(source_ep, dest_ep):

    # MUST go through Gatekeeper

    arq = build_admission_request(source_ep, dest_ep)
    acf = send_to_gatekeeper(arq)

    if not acf.admitted:
        raise CallRejected(acf.reason)

    # Proceed with call setup

    setup = build_h225_setup(source_ep, dest_ep)
    send_setup(setup)
```

### 3.3 Must Not Expose SRTP Keys

**Prohibited Actions**:

- Logging SRTP keys
- Transmitting keys in cleartext
- Storing keys on disk unencrypted

**Correct Pattern**:
```python
class SRTPSession:
    def __init__(self, master_key):

        # Store key in protected memory

        self._master_key = self._protect_key(master_key)

    def _protect_key(self, key):

        # Use OS-level key protection (e.g., mlock on Linux)

        protected = mlock(key)
        return protected

    def __del__(self):

        # Zero out key on destruction

        self._master_key = b'\x00' * len(self._master_key)
```

### 3.4 Must Log All Security Events

**Required Logging**:
```python
import logging
import json

def log_security_event(event_type, component_id, outcome, details=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_category": "SECURITY",
        "event_type": event_type,
        "component_id": component_id,
        "outcome": outcome,
        "severity": "ERROR" if outcome == "FAILURE" else "INFO"
    }

    if details:
        entry["details"] = details

    logging.info(json.dumps(entry))

# Usage

log_security_event("h235_token_validation", "ep-101", "FAILURE",
                  {"reason": "invalid_signature"})
```

---

## 4. Testing Requirements

### 4.1 Unit Tests for Signaling

```python
import unittest

class TestH225Signaling(unittest.TestCase):
    def test_setup_with_valid_h235(self):
        setup = build_h225_setup(source="ep-101", dest="+14085551234")
        setup.h235_token = generate_valid_token()

        result = validate_h225_setup(setup)
        self.assertTrue(result)

    def test_setup_with_invalid_h235(self):
        setup = build_h225_setup(source="ep-101", dest="+14085551234")
        setup.h235_token = None

        with self.assertRaises(SecurityError):
            validate_h225_setup(setup)

    def test_setup_with_expired_cert(self):
        setup = build_h225_setup(source="ep-101", dest="+14085551234")
        setup.certificate = load_expired_cert()

        with self.assertRaises(SecurityError):
            validate_h225_setup(setup)
```

### 4.2 SRTP Negotiation Tests

```python
class TestSRTPNegotiation(unittest.TestCase):
    def test_srtp_mandatory(self):
        olc = build_open_logical_channel()
        olc.srtp_enabled = True

        result = negotiate_media(olc)
        self.assertTrue(result.srtp_active)

    def test_srtp_fallback_denied(self):
        olc = build_open_logical_channel()
        olc.srtp_enabled = False

        with self.assertRaises(SecurityError):
            negotiate_media(olc)
```

### 4.3 PKI Validation Tests

```python
class TestPKIValidation(unittest.TestCase):
    def test_valid_certificate(self):
        cert = load_test_cert("valid.pem")
        self.assertTrue(validate_certificate(cert))

    def test_expired_certificate(self):
        cert = load_test_cert("expired.pem")
        self.assertFalse(validate_certificate(cert))

    def test_revoked_certificate(self):
        cert = load_test_cert("revoked.pem")
        with self.assertRaises(SecurityError):
            validate_certificate(cert)

    def test_untrusted_issuer(self):
        cert = load_test_cert("untrusted-issuer.pem")
        self.assertFalse(validate_certificate(cert))
```

### 4.4 Fuzz Testing for H.225/H.245

```python
from boofuzz import *

def fuzz_h225_setup():
    session = Session(target=Target(connection=TCPSocketConnection("gk.example.com", 1720)))

    s_initialize("H225_SETUP")

    # Fuzz source address

    s_string("ep-101", name="source", fuzzable=True)

    # Fuzz destination address

    s_string("+14085551234", name="dest", fuzzable=True)

    # Fuzz call ID

    s_string("abc123", name="call_id", fuzzable=True, max_len=1024)

    session.connect(s_get("H225_SETUP"))
    session.fuzz()

# Run fuzzer

fuzz_h225_setup()
```

---

## 5. Code Review Checklist

### 5.1 Security Review

- [ ] All H.225/H.245 fields validated
- [ ] H.235 profiles enforced
- [ ] PKI validation correct
- [ ] TLS/IPsec used for transport
- [ ] No custom cryptography
- [ ] All inputs sanitized
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities (if web UI)
- [ ] SRTP keys not exposed
- [ ] Security events logged

### 5.2 Functional Review

- [ ] Extension does not bypass GK
- [ ] Extension does not weaken security
- [ ] Extension handles errors gracefully
- [ ] Extension logs appropriately
- [ ] Extension tested (unit + integration)

### 5.3 Performance Review

- [ ] No performance regression
- [ ] Memory leaks checked
- [ ] CPU usage acceptable
- [ ] Network usage acceptable

---

## 6. Deployment Checklist

### 6.1 Pre-Deployment

- [ ] Code reviewed
- [ ] All tests pass (unit, integration, security, fuzz)
- [ ] Security scan pass (no critical/high vulnerabilities)
- [ ] Documentation complete
- [ ] Change request approved

### 6.2 Deployment

- [ ] Deploy to test environment
- [ ] Validate functionality
- [ ] Validate security posture (H.235, SRTP)
- [ ] Deploy to production (gradual rollout)
- [ ] Monitor for issues (24-48 hours)

### 6.3 Post-Deployment

- [ ] Validate logs flowing to SIEM
- [ ] Validate security alerts working
- [ ] Performance metrics acceptable
- [ ] No user complaints

---

## 7. Completion Criteria

Extension development is considered compliant when:

- All secure coding requirements met
- H.235 enforcement validated
- PKI integration correct
- All tests pass (unit, integration, security, fuzz)
- Code reviewed and approved
- Deployed without security incidents
- Logging and monitoring operational
