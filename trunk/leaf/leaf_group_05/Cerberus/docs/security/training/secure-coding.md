<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / secure-coding.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / secure-coding.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Secure Coding Practices Guide

## Table of Contents
1. [Learning Objectives](#learning-objectives)
2. [OWASP Top 10](#owasp-top-10)
3. [Vulnerability Prevention](#vulnerability-prevention)
4. [Secure Code Patterns](#secure-code-patterns)
5. [Code Review Checklist](#code-review-checklist)
6. [Cerberus Security Modules](#cerberus-security-modules)
7. [Common Mistakes](#common-mistakes)
8. [Best Practices](#best-practices)

---

## Learning Objectives

By completing this secure coding guide, developers will be able to:

- **Understand OWASP Top 10** web application vulnerabilities
- **Prevent injection attacks** (SQL, command, LDAP)
- **Implement proper authentication and authorization**
- **Handle sensitive data securely** (encryption, hashing)
- **Validate and sanitize input** properly
- **Use Cerberus security modules** in code
- **Perform security code reviews** effectively
- **Write tests for security** properties
- **Identify and remediate** common vulnerabilities

---

## OWASP Top 10

The OWASP Top 10 lists the most critical web application security risks:

### A01:2021 Broken Access Control

Unauthorized users can access protected resources or functions.

**Vulnerable Example:**

```python
# VULNERABLE - No access control check
def view_user_profile(user_id):
    # Directly return user data without checking authorization
    user = User.query.get(user_id)
    return user.profile_data
```

**Secure Example:**

```python
# SECURE - Check authorization before accessing
from cerberus.security import AccessController
from cerberus.guardians import AccessGuardian

def view_user_profile(user_id, current_user):
    access_controller = AccessController()
    access_guardian = AccessGuardian()
    
    # Check if current user can view this profile
    if not access_controller.can_user_view_profile(current_user, user_id):
        access_guardian.log_unauthorized_access_attempt(
            current_user,
            user_id
        )
        raise AuthorizationError("Access denied")
    
    user = User.query.get(user_id)
    access_guardian.log_profile_access(current_user, user_id)
    return user.profile_data
```

### A02:2021 Cryptographic Failures

Sensitive data exposed due to weak or missing encryption.

**Vulnerable Example:**

```python
# VULNERABLE - Storing sensitive data in plaintext
def save_credit_card(card_number, cvv):
    db.execute(
        "INSERT INTO credit_cards (number, cvv) VALUES (?, ?)",
        (card_number, cvv)
    )
```

**Secure Example:**

```python
# SECURE - Encrypt sensitive data
from cerberus.security import EncryptionManager, EncryptionVault

def save_credit_card(card_number, cvv):
    encryption_manager = EncryptionManager()
    vault = EncryptionVault()
    
    # Hash card number for later lookup
    card_hash = encryption_manager.hash_pii(card_number)
    
    # Encrypt full card number for storage
    encrypted_card = encryption_manager.encrypt_aes_256(card_number)
    encrypted_cvv = encryption_manager.encrypt_aes_256(cvv)
    
    # Store in secure vault
    vault.store({
        'card_hash': card_hash,
        'card_number': encrypted_card,
        'cvv': encrypted_cvv,
        'created_at': datetime.now()
    })
```

### A03:2021 Injection

Untrusted input interpreted as code (SQL, command, LDAP injection).

**SQL Injection Vulnerable:**

```python
# VULNERABLE - String concatenation allows injection
def find_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Attack: username = "' OR '1'='1"
# Resulting query: SELECT * FROM users WHERE username = '' OR '1'='1'
# Returns ALL users!
```

**SQL Injection Secure:**

```python
# SECURE - Parameterized query prevents injection
def find_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
    
# Parameterized: Treats username as data, not code
```

**Command Injection Vulnerable:**

```python
# VULNERABLE - Shell=True allows command injection
def process_file(filename):
    subprocess.run(f"process_file {filename}", shell=True)

# Attack: filename = "data.txt; rm -rf /"
# Executes: process_file data.txt; rm -rf /
```

**Command Injection Secure:**

```python
# SECURE - Pass arguments as list to prevent shell interpretation
def process_file(filename):
    subprocess.run(['process_file', filename], shell=False)
    
# Arguments passed directly to process, no shell interpretation
```

### A04:2021 Insecure Design

Missing security controls during design phase.

**Insecure Design Pattern:**

```python
# No rate limiting on login attempts
# No account lockout
# No MFA option
# No incident detection
def login(username, password):
    if verify_password(username, password):
        return create_session(username)
    else:
        raise LoginError("Invalid credentials")
```

**Secure Design Pattern:**

```python
from cerberus.security import RateLimiter, MFAProvider
from cerberus.guardians import AuthenticationGuardian

def login(username, password, mfa_token):
    rate_limiter = RateLimiter()
    mfa_provider = MFAProvider()
    auth_guardian = AuthenticationGuardian()
    
    # Rate limiting
    if rate_limiter.is_rate_limited(username):
        auth_guardian.log_rate_limit_exceeded(username)
        raise RateLimitError("Too many attempts - try again later")
    
    # Verify password
    if not verify_password(username, password):
        rate_limiter.record_failed_attempt(username)
        auth_guardian.log_failed_login(username, "password_mismatch")
        raise LoginError("Invalid credentials")
    
    # Verify MFA
    if not mfa_provider.verify_token(username, mfa_token):
        auth_guardian.log_failed_login(username, "mfa_failure")
        raise LoginError("Invalid MFA token")
    
    # Check for anomalous login
    if auth_guardian.is_anomalous_login(username):
        auth_guardian.trigger_additional_verification(username)
    
    # Create session
    session = create_session(username)
    auth_guardian.log_successful_login(username)
    
    return session
```

### A05:2021 Broken Authentication

Weak authentication mechanisms allow attackers to gain unauthorized access.

**Secure Authentication Implementation:**

```python
from cerberus.security import PasswordManager, PasswordValidator
from cerberus.security import SessionManager, TokenGenerator
from cerberus.guardians import AuthenticationGuardian

class SecureAuthenticationSystem:
    def __init__(self):
        self.password_manager = PasswordManager()
        self.password_validator = PasswordValidator()
        self.session_manager = SessionManager()
        self.token_generator = TokenGenerator()
        self.auth_guardian = AuthenticationGuardian()
    
    def register_user(self, username, password, email):
        """
        Register new user with secure password handling.
        """
        # Validate password strength
        validation_result = self.password_validator.validate(password)
        if not validation_result['is_valid']:
            raise PasswordPolicyError(validation_result['errors'])
        
        # Check for duplicate username
        if self.password_manager.user_exists(username):
            raise DuplicateUserError(f"Username '{username}' already taken")
        
        # Hash password with Argon2
        password_hash = self.password_manager.hash_password(
            password,
            algorithm='argon2',
            time_cost=2,
            memory_cost=65536
        )
        
        # Store user
        user = self.password_manager.create_user(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        self.auth_guardian.log_user_registration(username)
        return user
    
    def authenticate_user(self, username, password):
        """
        Authenticate user and return secure session.
        """
        # Look up user
        user = self.password_manager.get_user(username)
        if not user:
            # Generic error - don't reveal if user exists
            self.auth_guardian.log_failed_login(username, "user_not_found")
            raise AuthenticationError("Invalid username or password")
        
        # Verify password
        if not self.password_manager.verify_password(password, user['password_hash']):
            self.auth_guardian.log_failed_login(username, "password_mismatch")
            raise AuthenticationError("Invalid username or password")
        
        # Create secure session token
        session_token = self.token_generator.generate_secure_token()
        session_expiry = datetime.now() + timedelta(hours=8)
        
        # Store session
        session = self.session_manager.create_session(
            user_id=user['id'],
            token=session_token,
            expiry=session_expiry,
            secure=True,
            httponly=True,
            samesite='Strict'
        )
        
        self.auth_guardian.log_successful_login(username)
        return session_token
```

### A06:2021 Sensitive Data Exposure

Sensitive data exposed during transmission or storage.

**Data Classification and Protection:**

```python
from cerberus.security import DataClassifier, DLP
from cerberus.guardians import DataGuardian

class DataProtectionStrategy:
    def __init__(self):
        self.data_classifier = DataClassifier()
        self.dlp = DLP()
        self.data_guardian = DataGuardian()
    
    def classify_and_protect_data(self, data):
        """
        Classify data and apply appropriate protection.
        """
        # Classify data sensitivity
        classification = self.data_classifier.classify(data)
        
        if classification == 'restricted':
            # Apply strongest protection
            return self.protect_restricted_data(data)
        elif classification == 'confidential':
            # Apply medium protection
            return self.protect_confidential_data(data)
        elif classification == 'internal':
            # Apply basic protection
            return self.protect_internal_data(data)
        else:
            return data
    
    def protect_restricted_data(self, data):
        """
        Protect restricted data (PII, healthcare, financial).
        """
        # Encryption in transit: TLS 1.2+
        # Encryption at rest: AES-256
        # Access control: Role-based
        # Logging: Comprehensive audit trail
        
        return {
            'encryption': 'AES-256-GCM',
            'access_control': 'restricted',
            'audit_logging': 'comprehensive',
            'data_retention': '7_years',
            'anonymization': True
        }
    
    def prevent_data_exposure_in_logs(self, log_message):
        """
        Prevent sensitive data from being logged.
        """
        # Patterns for sensitive data
        sensitive_patterns = {
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'password': r'password\s*=\s*[^\s]+',
            'api_key': r'api[_-]?key\s*=\s*[^\s]+',
            'token': r'token\s*=\s*[^\s]+'
        }
        
        sanitized_message = log_message
        
        for data_type, pattern in sensitive_patterns.items():
            import re
            sanitized_message = re.sub(
                pattern,
                f'[REDACTED_{data_type.upper()}]',
                sanitized_message,
                flags=re.IGNORECASE
            )
        
        self.data_guardian.log_message(sanitized_message)
        return sanitized_message
```

### A07:2021 Identification and Authentication Failures

Weaknesses in authentication and session management.

**Secure Session Management:**

```python
from cerberus.security import SessionManager
from cerberus.guardians import SessionGuardian

class SecureSessionManagement:
    def __init__(self):
        self.session_manager = SessionManager()
        self.session_guardian = SessionGuardian()
    
    def create_secure_session(self, user_id):
        """
        Create secure session with all recommended properties.
        """
        # Generate cryptographically secure token
        token = os.urandom(32).hex()
        
        # Create session with security properties
        session = {
            'token': token,
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=8),
            'last_activity': datetime.now(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'secure': True,
            'httponly': True,
            'samesite': 'Strict'
        }
        
        self.session_manager.store_session(token, session)
        self.session_guardian.log_session_creation(user_id, session)
        
        return token
    
    def validate_session(self, token):
        """
        Validate session and detect hijacking.
        """
        session = self.session_manager.get_session(token)
        
        if not session:
            self.session_guardian.log_invalid_session(token)
            raise SessionError("Invalid session")
        
        # Check expiration
        if session['expires_at'] < datetime.now():
            self.session_manager.delete_session(token)
            self.session_guardian.log_expired_session(token)
            raise SessionError("Session expired")
        
        # Check for session hijacking indicators
        if not self.is_same_client(session):
            self.session_guardian.log_session_hijacking_attempt(
                token,
                session
            )
            self.session_manager.delete_session(token)
            raise SessionError("Session hijacked")
        
        # Update last activity
        session['last_activity'] = datetime.now()
        self.session_manager.update_session(token, session)
        
        return session
    
    def is_same_client(self, session):
        """
        Detect if session is from same client (IP, User-Agent).
        """
        # Check IP address (with tolerance for dynamic IPs)
        current_ip = request.remote_addr
        if not self.session_guardian.is_ip_in_range(
            current_ip,
            session['ip_address']
        ):
            return False
        
        # Check User-Agent
        current_user_agent = request.headers.get('User-Agent')
        if current_user_agent != session['user_agent']:
            return False
        
        return True
    
    def regenerate_session_token(self, old_token):
        """
        Regenerate session token to prevent fixation attacks.
        """
        # Get existing session
        session = self.session_manager.get_session(old_token)
        
        # Generate new token
        new_token = os.urandom(32).hex()
        
        # Copy session data
        session['token'] = new_token
        
        # Store new session
        self.session_manager.store_session(new_token, session)
        
        # Delete old session
        self.session_manager.delete_session(old_token)
        
        self.session_guardian.log_session_token_regeneration(old_token, new_token)
        
        return new_token
```

### A08:2021 Software and Data Integrity Failures

Using untrusted software or data without verification.

**Secure Dependency Management:**

```python
from cerberus.security import DependencyVerifier, IntegrityChecker
from cerberus.guardians import IntegrityGuardian

class SecureDependencyManagement:
    def __init__(self):
        self.dependency_verifier = DependencyVerifier()
        self.integrity_checker = IntegrityChecker()
        self.integrity_guardian = IntegrityGuardian()
    
    def verify_package_integrity(self, package_name, version):
        """
        Verify package integrity before using.
        """
        # Check package signature
        signature_valid = self.dependency_verifier.verify_signature(
            package_name,
            version
        )
        
        if not signature_valid:
            self.integrity_guardian.log_signature_verification_failure(
                package_name,
                version
            )
            raise IntegrityError(f"Invalid signature for {package_name}")
        
        # Check against known vulnerabilities
        vulnerabilities = self.dependency_verifier.check_vulnerabilities(
            package_name,
            version
        )
        
        if vulnerabilities:
            self.integrity_guardian.log_vulnerable_package(
                package_name,
                version,
                vulnerabilities
            )
            raise VulnerabilityError(
                f"{package_name} has known vulnerabilities: {vulnerabilities}"
            )
        
        # Verify checksum
        checksum_valid = self.integrity_checker.verify_checksum(
            package_name,
            version
        )
        
        if not checksum_valid:
            self.integrity_guardian.log_checksum_mismatch(
                package_name,
                version
            )
            raise IntegrityError(f"Checksum mismatch for {package_name}")
        
        self.integrity_guardian.log_package_verified(package_name, version)
        return True
```

### A09:2021 Logging and Monitoring Failures

Insufficient logging and monitoring of security events.

**Comprehensive Security Logging:**

```python
from cerberus.security import SecurityLogger, LogAnalyzer
from cerberus.guardians import LoggingGuardian

class ComprehensiveSecurityLogging:
    def __init__(self):
        self.security_logger = SecurityLogger()
        self.log_analyzer = LogAnalyzer()
        self.logging_guardian = LoggingGuardian()
    
    def setup_security_logging(self):
        """
        Set up comprehensive security event logging.
        """
        security_events_to_log = [
            # Authentication events
            'successful_login',
            'failed_login',
            'account_lockout',
            'password_change',
            'mfa_setup',
            
            # Authorization events
            'access_granted',
            'access_denied',
            'privilege_escalation',
            'role_change',
            
            # Data events
            'data_access',
            'data_modification',
            'data_deletion',
            'data_export',
            
            # Administrative events
            'admin_action',
            'configuration_change',
            'security_policy_change',
            
            # Security events
            'vulnerability_detected',
            'malware_detected',
            'intrusion_detected',
            'policy_violation'
        ]
        
        for event_type in security_events_to_log:
            self.security_logger.register_event_type(event_type)
    
    def log_security_event(self, event_type, event_data):
        """
        Log security event with comprehensive details.
        """
        log_entry = {
            'timestamp': datetime.now(),
            'event_type': event_type,
            'user_id': event_data.get('user_id'),
            'ip_address': event_data.get('ip_address'),
            'user_agent': event_data.get('user_agent'),
            'resource': event_data.get('resource'),
            'action': event_data.get('action'),
            'result': event_data.get('result'),
            'additional_data': event_data.get('additional_data'),
            'severity': self.determine_severity(event_type)
        }
        
        # Store in secure log
        self.security_logger.log_event(log_entry)
        
        # Analyze for suspicious patterns
        self.log_analyzer.analyze_event(log_entry)
        
        # Alert if critical
        if log_entry['severity'] == 'critical':
            self.logging_guardian.alert_security_team(log_entry)
    
    def detect_security_anomalies(self):
        """
        Analyze logs for security anomalies.
        """
        anomalies = self.log_analyzer.detect_anomalies()
        
        for anomaly in anomalies:
            self.logging_guardian.log_anomaly_detected(anomaly)
            
            if anomaly['severity'] == 'high':
                self.logging_guardian.escalate_to_security_team(anomaly)
```

### A10:2021 Server-Side Request Forgery (SSRF)

Server makes requests to unintended locations.

**SSRF Vulnerable:**

```python
# VULNERABLE - No validation of URL
def fetch_content_from_url(url):
    response = requests.get(url)
    return response.content

# Attack: fetch_content_from_url("http://169.254.169.254/latest/meta-data/")
# Accesses AWS metadata service, leaks credentials!
```

**SSRF Secure:**

```python
# SECURE - Whitelist and validate URLs
from cerberus.security import URLValidator, SSRFProtection
from cerberus.guardians import NetworkGuardian

def fetch_content_from_url(url):
    url_validator = URLValidator()
    ssrf_protection = SSRFProtection()
    network_guardian = NetworkGuardian()
    
    # Parse and validate URL
    try:
        parsed_url = url_validator.parse_url(url)
    except ValueError:
        network_guardian.log_ssrf_attempt(url, "invalid_url")
        raise ValueError("Invalid URL")
    
    # Check against whitelist
    if not url_validator.is_whitelisted_domain(parsed_url.hostname):
        network_guardian.log_ssrf_attempt(url, "domain_not_whitelisted")
        raise ValueError("Domain not whitelisted")
    
    # Verify not internal IP
    if ssrf_protection.is_internal_ip(parsed_url.hostname):
        network_guardian.log_ssrf_attempt(url, "internal_ip_blocked")
        raise ValueError("Cannot access internal IP addresses")
    
    # Verify port is allowed
    if not ssrf_protection.is_allowed_port(parsed_url.port):
        network_guardian.log_ssrf_attempt(url, "port_not_allowed")
        raise ValueError("Port not allowed")
    
    # Fetch with timeout
    try:
        response = requests.get(url, timeout=5)
        network_guardian.log_url_fetch(url, response.status_code)
        return response.content
    except Exception as e:
        network_guardian.log_url_fetch_error(url, str(e))
        raise
```

---

## Vulnerability Prevention

### Input Validation Framework

```python
from cerberus.security import InputValidator, ValidationRules
from cerberus.guardians import InputGuardian

class RobustInputValidation:
    def __init__(self):
        self.input_validator = InputValidator()
        self.validation_rules = ValidationRules()
        self.input_guardian = InputGuardian()
    
    def validate_email(self, email):
        """Validate email address."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not self.input_validator.match_pattern(email, pattern):
            self.input_guardian.log_validation_failure('email', email)
            raise ValueError("Invalid email format")
        return email
    
    def validate_integer(self, value, min_value=None, max_value=None):
        """Validate integer within range."""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            self.input_guardian.log_validation_failure('integer', value)
            raise ValueError("Not a valid integer")
        
        if min_value is not None and int_value < min_value:
            raise ValueError(f"Value below minimum {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValueError(f"Value above maximum {max_value}")
        
        return int_value
    
    def validate_filename(self, filename):
        """Validate filename to prevent directory traversal."""
        import os
        
        # Reject path traversal attempts
        if '..' in filename or filename.startswith('/'):
            self.input_guardian.log_validation_failure('filename', filename)
            raise ValueError("Invalid filename")
        
        # Get basename only (no directory)
        filename = os.path.basename(filename)
        
        # Whitelist allowed extensions
        allowed_extensions = ['.pdf', '.txt', '.doc', '.docx', '.xls']
        _, ext = os.path.splitext(filename)
        
        if ext.lower() not in allowed_extensions:
            self.input_guardian.log_validation_failure('filename', filename)
            raise ValueError(f"File type not allowed: {ext}")
        
        return filename
```

### Output Encoding

```python
from cerberus.security import OutputEncoder

class SecureOutputHandling:
    def __init__(self):
        self.output_encoder = OutputEncoder()
    
    def render_html_safe(self, content):
        """Encode content for safe HTML rendering."""
        return self.output_encoder.html_escape(content)
    
    def render_javascript_safe(self, data):
        """Encode content for JavaScript context."""
        return self.output_encoder.javascript_escape(data)
    
    def render_url_safe(self, url_param):
        """Encode content for URL context."""
        return self.output_encoder.url_encode(url_param)
```

---

## Secure Code Patterns

### Secure Error Handling

```python
# INSECURE - Leaks internal details
def get_user(user_id):
    try:
        user = db.query(User).filter(User.id == user_id).one()
        return user
    except SQLAlchemy.exc.NoResultFound as e:
        raise Exception(f"SQL Error: {e}")  # Leaks DB structure

# SECURE - Generic error message
def get_user(user_id):
    try:
        user = db.query(User).filter(User.id == user_id).one()
        return user
    except Exception:
        logger.error(f"Error retrieving user {user_id}", exc_info=True)
        raise GenericError("User not found")  # Generic message
```

### Secure Exception Handling

```python
from cerberus.security import ErrorHandler

class SecureErrorHandling:
    def __init__(self):
        self.error_handler = ErrorHandler()
    
    def handle_security_error(self, error, context):
        """
        Handle security errors appropriately.
        """
        # Log detailed error internally
        self.error_handler.log_error_details(error, context)
        
        # Return generic error to user
        if isinstance(error, AuthenticationError):
            return {"error": "Authentication failed"}
        elif isinstance(error, AuthorizationError):
            return {"error": "Access denied"}
        elif isinstance(error, ValidationError):
            return {"error": "Invalid input"}
        else:
            return {"error": "An error occurred"}
```

---

## Code Review Checklist

### Security Code Review Template

```python
# Code Review Security Checklist

class SecurityCodeReviewChecklist:
    checklist = {
        "Authentication & Authorization": [
            "All public endpoints require authentication",
            "Authorization checks present before data access",
            "Session tokens generated securely",
            "Session timeout implemented",
            "Privilege escalation prevented",
            "API key rotation enforced"
        ],
        
        "Input Validation": [
            "All user inputs validated",
            "Whitelist approach used (not blacklist)",
            "File uploads validated",
            "File paths prevented from directory traversal",
            "SQL injection prevention (parameterized queries)",
            "Command injection prevention",
            "XSS prevention (output encoding)"
        ],
        
        "Cryptography": [
            "Sensitive data encrypted at rest",
            "HTTPS/TLS enforced for transit",
            "Passwords hashed with strong algorithm (Argon2)",
            "Random number generation is cryptographic",
            "Encryption keys stored securely",
            "Old encryption keys rotated regularly"
        ],
        
        "Error Handling": [
            "Errors logged with details",
            "Generic errors returned to users",
            "Stack traces not exposed",
            "Sensitive data not in error messages",
            "Exception handling is specific"
        ],
        
        "Data Protection": [
            "Sensitive data identified and classified",
            "PII encrypted or hashed",
            "Credit card data encrypted",
            "Data minimization applied",
            "Retention policies enforced",
            "Backup data encrypted"
        ],
        
        "Logging & Monitoring": [
            "Authentication attempts logged",
            "Authorization failures logged",
            "Data access logged",
            "Admin actions logged",
            "Logs protected from tampering",
            "Log retention policy defined"
        ],
        
        "Dependencies": [
            "All dependencies documented",
            "No known vulnerabilities",
            "Dependencies kept current",
            "Supply chain verified",
            "Third-party code reviewed"
        ],
        
        "Configuration": [
            "No hardcoded secrets",
            "Configuration externalized",
            "Debug mode disabled in production",
            "Security headers set",
            "CORS properly configured"
        ]
    }
    
    def conduct_security_review(self, code):
        """
        Conduct comprehensive security code review.
        """
        findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for category, checks in self.checklist.items():
            for check in checks:
                result = self.evaluate_check(code, check)
                if result['passed'] is False:
                    findings[result['severity']].append({
                        'category': category,
                        'check': check,
                        'recommendation': result['recommendation']
                    })
        
        return findings
```

---

## Cerberus Security Modules

### Using Cerberus Security Modules

```python
# Import Cerberus security modules
from cerberus.security import (
    AuthenticationManager,
    AuthorizationManager,
    EncryptionManager,
    InputValidator,
    AuditLogger
)
from cerberus.guardians import (
    SecurityGuardian,
    AccessGuardian,
    InputGuardian,
    EncryptionGuardian
)

class CerberusSecurityIntegration:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.authz_manager = AuthorizationManager()
        self.encryption_manager = EncryptionManager()
        self.input_validator = InputValidator()
        self.audit_logger = AuditLogger()
        
        self.security_guardian = SecurityGuardian()
        self.access_guardian = AccessGuardian()
        self.input_guardian = InputGuardian()
        self.encryption_guardian = EncryptionGuardian()
    
    def secure_user_operation(self, user_id, operation, data):
        """
        Perform operation with Cerberus security controls.
        """
        # Step 1: Authenticate user
        if not self.auth_manager.is_authenticated():
            self.security_guardian.log_unauthenticated_access_attempt()
            raise AuthenticationError("User not authenticated")
        
        # Step 2: Validate input
        try:
            validated_data = self.input_validator.validate(data)
        except ValidationError as e:
            self.input_guardian.log_validation_failure(data, str(e))
            raise
        
        # Step 3: Check authorization
        if not self.authz_manager.can_perform_operation(user_id, operation):
            self.access_guardian.log_unauthorized_operation(
                user_id,
                operation
            )
            raise AuthorizationError("User not authorized for this operation")
        
        # Step 4: Encrypt sensitive data if needed
        if self.input_guardian.is_sensitive_data(validated_data):
            encrypted_data = self.encryption_manager.encrypt(
                validated_data
            )
            self.encryption_guardian.log_encryption_operation(
                operation,
                len(validated_data)
            )
        else:
            encrypted_data = validated_data
        
        # Step 5: Perform operation
        result = self.perform_operation(operation, encrypted_data)
        
        # Step 6: Audit log
        self.audit_logger.log_operation(
            user_id=user_id,
            operation=operation,
            result='success',
            timestamp=datetime.now()
        )
        
        return result
```

---

## Common Mistakes

### Mistake 1: Trusting User Input

```python
# WRONG
user_id = request.args.get('id')  # String from user
data = db.query(User).filter(User.id == user_id).all()

# RIGHT
user_id = request.args.get('id')
try:
    user_id = int(user_id)  # Validate type
except ValueError:
    raise ValidationError("Invalid user ID")

data = db.query(User).filter(User.id == user_id).all()
```

### Mistake 2: Insufficient Logging

```python
# WRONG - No logging
def delete_user(user_id):
    User.query.filter(User.id == user_id).delete()

# RIGHT - Comprehensive logging
def delete_user(user_id, current_user):
    user = User.query.get(user_id)
    
    audit_logger.log({
        'action': 'user_deletion',
        'deleted_user_id': user_id,
        'deleted_by': current_user,
        'timestamp': datetime.now(),
        'user_details': user.to_dict()
    })
    
    User.query.filter(User.id == user_id).delete()
```

### Mistake 3: Weak Cryptography

```python
# WRONG - Weak hashing
import hashlib
password_hash = hashlib.md5(password).hexdigest()

# RIGHT - Strong hashing
from cerberus.security import PasswordHasher
password_hash = PasswordHasher.hash(password, algorithm='argon2')
```

---

## Best Practices

### Defense in Depth

```python
class DefenseInDepthExample:
    """
    Implement multiple security layers.
    """
    
    def secure_api_endpoint(self, request):
        # Layer 1: HTTPS/TLS
        if not request.is_secure:
            return 403, "HTTPS required"
        
        # Layer 2: API Rate Limiting
        if self.rate_limiter.is_rate_limited(request.remote_addr):
            return 429, "Rate limit exceeded"
        
        # Layer 3: Authentication
        if not self.auth_manager.is_authenticated():
            return 401, "Authentication required"
        
        # Layer 4: Authorization
        if not self.authz_manager.can_access_resource():
            return 403, "Access denied"
        
        # Layer 5: Input Validation
        try:
            data = self.input_validator.validate(request.data)
        except ValidationError:
            return 400, "Invalid input"
        
        # Layer 6: Business Logic Validation
        if not self.business_logic.is_valid(data):
            return 422, "Business rule violated"
        
        # Layer 7: Audit Logging
        self.audit_logger.log_request(request)
        
        # Process request
        result = self.process_request(data)
        
        return 200, result
```

### Secure by Default

```python
class SecurityDefaults:
    """
    Defaults should be secure.
    """
    
    DEFAULT_CONFIG = {
        'ssl_enabled': True,  # Not False
        'debug_mode': False,  # Not True
        'require_auth': True,  # Not False
        'require_https': True,  # Not False
        'log_sensitive_data': False,  # Not True
        'allow_cors': False,  # Not True
        'password_min_length': 12,  # Not 6
        'session_timeout': 30,  # minutes, not hours
        'encryption_algorithm': 'AES-256-GCM',
        'password_hash_algorithm': 'argon2'
    }
```

---

## Summary

This secure coding guide covered:

✅ **OWASP Top 10**: All 10 most critical vulnerabilities
✅ **Prevention Patterns**: Concrete examples of vulnerable vs. secure code
✅ **Input Validation**: Robust data validation strategies
✅ **Output Encoding**: Safe data rendering in different contexts
✅ **Cryptography**: Proper encryption and key management
✅ **Error Handling**: Secure error messages and logging
✅ **Code Review Checklist**: Systematic security review template
✅ **Cerberus Modules**: Integration with security framework
✅ **Common Mistakes**: Avoid pitfalls
✅ **Best Practices**: Defense in depth and secure defaults

**Key Principles:**

1. **Trust nothing** - Validate all inputs
2. **Defense in depth** - Multiple security layers
3. **Secure by default** - Conservative defaults
4. **Fail securely** - Errors don't leak information
5. **Log everything** - Audit trail for investigation
6. **Keep current** - Update dependencies and patches
7. **Review regularly** - Security code reviews
8. **Test security** - Unit tests for security properties

---

**Document Version**: 1.0
**Last Updated**: 2024
**Framework**: Cerberus Security
**Language**: Python
**Training Duration**: 6-8 hours
