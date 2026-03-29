<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / security-training.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / security-training.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Comprehensive Security Training Materials

## Table of Contents
1. [Learning Objectives](#learning-objectives)
2. [Authentication & Identity Management](#authentication--identity-management)
3. [Authorization & Access Control](#authorization--access-control)
4. [Input Validation & Data Integrity](#input-validation--data-integrity)
5. [Encryption & Cryptography](#encryption--cryptography)
6. [Guardians Security Framework](#guardians-security-framework)
7. [Incident Response Planning](#incident-response-planning)
8. [Assessment & Exercises](#assessment--exercises)

---

## Learning Objectives

By completing this training, participants will be able to:

- **Understand core security principles** and how they apply to Cerberus
- **Implement authentication mechanisms** using Cerberus authentication modules
- **Design authorization models** with role-based and attribute-based access control
- **Validate and sanitize input** to prevent injection attacks
- **Apply encryption and cryptographic practices** correctly
- **Deploy and manage Cerberus Guardians** for security enforcement
- **Respond to security incidents** following established procedures
- **Recognize security vulnerabilities** in code reviews and assessments

---

## Authentication & Identity Management

### 1.1 Authentication Fundamentals

Authentication is the process of verifying that a user is who they claim to be. The three main authentication factors are:

**Knowledge Factor (Something You Know)**
- Passwords
- PIN codes
- Security questions
- Passphrase

**Possession Factor (Something You Have)**
- Hardware tokens
- Smart cards
- Mobile devices
- Authentication apps (TOTP)

**Inherence Factor (Something You Are)**
- Fingerprints
- Facial recognition
- Iris scanning
- Behavioral biometrics

### 1.2 Multi-Factor Authentication (MFA)

Multi-Factor Authentication requires multiple independent verification methods to establish identity.

**Cerberus MFA Implementation:**

```python
from cerberus.security import AuthenticationManager, MFAProvider
from cerberus.guardians import MFAGuardian

class SecureAuthenticationFlow:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.mfa_provider = MFAProvider()
        self.mfa_guardian = MFAGuardian()
    
    def authenticate_user(self, username, password, mfa_token):
        """
        Authenticate user with password and MFA token.
        """
        try:
            # Step 1: Verify password
            if not self.auth_manager.verify_password(username, password):
                self.mfa_guardian.log_failed_attempt(username, "password_mismatch")
                raise AuthenticationError("Invalid credentials")
            
            # Step 2: Verify MFA token
            if not self.mfa_provider.verify_token(username, mfa_token):
                self.mfa_guardian.log_failed_attempt(username, "mfa_token_invalid")
                raise AuthenticationError("Invalid MFA token")
            
            # Step 3: Check for anomalous behavior
            if self.mfa_guardian.detect_anomaly(username):
                self.mfa_guardian.trigger_additional_verification(username)
            
            # Step 4: Log successful authentication
            session_token = self.auth_manager.create_session(username)
            self.mfa_guardian.log_successful_authentication(username)
            
            return session_token
            
        except Exception as e:
            self.mfa_guardian.log_security_event("auth_failure", str(e))
            raise
    
    def setup_mfa_for_user(self, username, delivery_method):
        """
        Set up MFA for a new user.
        delivery_method: 'sms', 'email', 'totp'
        """
        # Generate secret
        secret = self.mfa_provider.generate_secret()
        
        # Store in secure vault
        self.mfa_provider.store_secret(username, secret)
        
        # Send initial codes
        if delivery_method == 'sms':
            self.mfa_provider.send_sms_token(username)
        elif delivery_method == 'email':
            self.mfa_provider.send_email_token(username)
        elif delivery_method == 'totp':
            qr_code = self.mfa_provider.generate_totp_qr(username, secret)
            return qr_code
        
        # Log MFA setup
        self.mfa_guardian.log_mfa_setup(username, delivery_method)
```

### 1.3 Password Management

**Best Practices:**

- **Minimum length**: 12-16 characters
- **Complexity requirements**: Mix of uppercase, lowercase, numbers, special characters
- **Password storage**: Never store plain text passwords; use bcrypt, scrypt, or Argon2
- **Password expiration**: 90-180 days for sensitive accounts
- **History**: Prevent reuse of last 5-12 passwords
- **Account lockout**: Lock after 5-10 failed attempts for 15-30 minutes

**Cerberus Password Management:**

```python
from cerberus.security import PasswordManager, PasswordPolicy
from cerberus.guardians import PasswordGuardian

class PasswordManagementSystem:
    def __init__(self):
        self.password_manager = PasswordManager()
        self.password_policy = PasswordPolicy()
        self.password_guardian = PasswordGuardian()
    
    def validate_password_strength(self, password):
        """
        Validate password against security policy.
        """
        checks = {
            'length': len(password) >= 16,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'numbers': any(c.isdigit() for c in password),
            'special_chars': any(c in '!@#$%^&*' for c in password),
            'no_username': 'admin' not in password.lower(),
            'no_dict_words': self.password_policy.check_dictionary(password)
        }
        
        if not all(checks.values()):
            failed_checks = [k for k, v in checks.items() if not v]
            raise PasswordPolicyViolation(f"Failed checks: {failed_checks}")
        
        return True
    
    def set_password(self, username, new_password):
        """
        Set password with policy validation and guardian tracking.
        """
        # Validate against policy
        self.validate_password_strength(new_password)
        
        # Check password history
        if self.password_manager.is_password_reused(username, new_password):
            self.password_guardian.log_policy_violation(
                username, 
                "password_reuse_attempt"
            )
            raise PasswordPolicyViolation("Password previously used")
        
        # Hash password with strong algorithm
        password_hash = self.password_manager.hash_password(
            new_password,
            algorithm='argon2',
            time_cost=2,
            memory_cost=65536
        )
        
        # Store in secure vault
        self.password_manager.store_password(username, password_hash)
        
        # Log password change
        self.password_guardian.log_password_change(username)
    
    def handle_failed_login_attempt(self, username):
        """
        Track and respond to failed login attempts.
        """
        attempts = self.password_guardian.increment_failed_attempts(username)
        
        if attempts == 3:
            self.password_guardian.send_alert(
                username,
                "Multiple failed login attempts detected"
            )
        elif attempts == 5:
            self.password_guardian.lock_account(username)
            self.password_guardian.notify_security_team(
                username,
                "Account locked after 5 failed attempts"
            )
            raise AccountLockedException(
                "Account locked. Contact support to unlock."
            )
```

### 1.4 Session Management

Sessions must be properly managed to prevent hijacking and fixation attacks.

**Session Security Properties:**

- **Secure token generation**: Use cryptographically secure random number generators
- **HTTPS only**: All session communications must use HTTPS/TLS
- **HttpOnly cookies**: Prevent JavaScript access to session tokens
- **Secure flag**: Ensure cookies only sent over HTTPS
- **SameSite attribute**: Prevent CSRF attacks (SameSite=Strict or Lax)
- **Session timeout**: 15-30 minutes of inactivity
- **Absolute timeout**: 8 hours maximum session duration
- **Token rotation**: Regenerate token on privilege escalation

---

## Authorization & Access Control

### 2.1 Access Control Models

**Role-Based Access Control (RBAC)**

RBAC uses predefined roles to control access to resources.

```python
from cerberus.security import RoleManager, AccessControl
from cerberus.guardians import AccessGuardian

class RBACImplementation:
    def __init__(self):
        self.role_manager = RoleManager()
        self.access_control = AccessControl()
        self.access_guardian = AccessGuardian()
    
    def define_roles(self):
        """
        Define organizational roles with associated permissions.
        """
        roles = {
            'viewer': {
                'permissions': ['read:reports', 'read:documents'],
                'description': 'Can view reports and documents only'
            },
            'analyst': {
                'permissions': [
                    'read:reports', 
                    'create:reports',
                    'update:reports',
                    'read:documents'
                ],
                'description': 'Can create and modify reports'
            },
            'admin': {
                'permissions': [
                    'read:*',
                    'create:*',
                    'update:*',
                    'delete:*',
                    'manage:users',
                    'manage:roles'
                ],
                'description': 'Full system access'
            }
        }
        
        for role_name, role_config in roles.items():
            self.role_manager.create_role(
                role_name,
                role_config['permissions'],
                role_config['description']
            )
            self.access_guardian.log_role_creation(role_name, role_config)
    
    def assign_role_to_user(self, username, role_name):
        """
        Assign a role to a user with audit logging.
        """
        if not self.role_manager.role_exists(role_name):
            raise RoleNotFound(f"Role '{role_name}' does not exist")
        
        self.role_manager.assign_role(username, role_name)
        self.access_guardian.log_role_assignment(username, role_name)
    
    def check_permission(self, username, resource, action):
        """
        Check if user has permission for action on resource.
        """
        roles = self.role_manager.get_user_roles(username)
        
        for role in roles:
            permissions = self.role_manager.get_role_permissions(role)
            
            # Check exact permission
            if f"{action}:{resource}" in permissions:
                self.access_guardian.log_access_grant(
                    username, 
                    resource, 
                    action
                )
                return True
            
            # Check wildcard permission
            if f"{action}:*" in permissions:
                self.access_guardian.log_access_grant(
                    username, 
                    resource, 
                    action
                )
                return True
        
        self.access_guardian.log_access_denial(
            username, 
            resource, 
            action
        )
        raise AccessDenied(
            f"User '{username}' lacks permission for {action} on {resource}"
        )
```

**Attribute-Based Access Control (ABAC)**

ABAC uses attributes (user, resource, environment) for fine-grained control.

```python
from cerberus.security import AttributeEvaluator, PolicyEngine
from cerberus.guardians import ABACGuardian

class ABACImplementation:
    def __init__(self):
        self.attribute_evaluator = AttributeEvaluator()
        self.policy_engine = PolicyEngine()
        self.abac_guardian = ABACGuardian()
    
    def define_policy(self, policy_name, rules):
        """
        Define ABAC policy with attribute rules.
        """
        policy = {
            'name': policy_name,
            'rules': rules,
            'created_at': datetime.now()
        }
        
        self.policy_engine.store_policy(policy)
        self.abac_guardian.log_policy_creation(policy_name)
    
    def evaluate_access(self, subject, resource, action, context):
        """
        Evaluate access based on attributes.
        
        Example context:
        {
            'subject': {'role': 'analyst', 'department': 'finance', 'clearance': 'secret'},
            'resource': {'type': 'report', 'classification': 'confidential', 'owner': 'finance'},
            'action': 'read',
            'environment': {'time': '14:30', 'location': 'office', 'ip': '192.168.1.100'}
        }
        """
        policies = self.policy_engine.get_applicable_policies(
            resource['type'],
            action
        )
        
        for policy in policies:
            if self.attribute_evaluator.evaluate_rules(
                policy['rules'],
                context
            ):
                self.abac_guardian.log_access_grant(
                    subject, 
                    resource, 
                    action,
                    context
                )
                return True
        
        self.abac_guardian.log_access_denial(
            subject, 
            resource, 
            action,
            context
        )
        raise AccessDenied("Access denied based on attribute policies")
```

### 2.2 Principle of Least Privilege (PoLP)

Users should have minimum necessary permissions to perform their job.

**Implementation Guidelines:**

1. **Start with zero permissions**: Deny all by default
2. **Grant specific permissions**: Only what's needed
3. **Regular reviews**: Quarterly access reviews
4. **Temporary elevation**: Use break-glass procedures
5. **Separation of duties**: Prevent any single person from making critical changes

**Cerberus PoLP Enforcement:**

```python
from cerberus.security import PrivilegeManager
from cerberus.guardians import PrivilegeGuardian

class PrincipleOfLeastPrivilege:
    def __init__(self):
        self.privilege_manager = PrivilegeManager()
        self.privilege_guardian = PrivilegeGuardian()
    
    def audit_user_permissions(self, username):
        """
        Audit and report on user permissions.
        """
        current_permissions = self.privilege_manager.get_user_permissions(username)
        job_required_permissions = self.privilege_manager.get_role_permissions(
            self.privilege_manager.get_user_role(username)
        )
        
        excessive_permissions = set(current_permissions) - set(job_required_permissions)
        
        if excessive_permissions:
            self.privilege_guardian.flag_excessive_permissions(
                username,
                excessive_permissions
            )
            
            # Request removal approval
            self.privilege_guardian.create_permission_review_task(
                username,
                excessive_permissions
            )
        
        return {
            'username': username,
            'current_permissions': current_permissions,
            'required_permissions': job_required_permissions,
            'excessive_permissions': list(excessive_permissions)
        }
    
    def temporary_privilege_elevation(self, username, required_permission, reason, duration_minutes):
        """
        Temporarily elevate privileges with extensive logging.
        """
        if not self.privilege_guardian.requires_approval(required_permission):
            raise PermissionError("Cannot elevate this permission")
        
        # Log the request
        request_id = self.privilege_guardian.log_elevation_request(
            username,
            required_permission,
            reason
        )
        
        # Get approval (in real system, would get manager approval)
        if not self.privilege_guardian.get_approval(request_id):
            raise AccessDenied("Privilege elevation denied")
        
        # Grant temporary permission
        expiration = datetime.now() + timedelta(minutes=duration_minutes)
        token = self.privilege_manager.grant_temporary_permission(
            username,
            required_permission,
            expiration
        )
        
        # Log the grant
        self.privilege_guardian.log_elevation_granted(
            username,
            required_permission,
            expiration
        )
        
        return token
```

---

## Input Validation & Data Integrity

### 3.1 Input Validation Principles

Input validation prevents injection attacks, malformed data, and buffer overflows.

**Validation Strategy:**

1. **Whitelist over blacklist**: Define what IS valid
2. **Validate at boundaries**: Check at entry points
3. **Reject invalid data**: Don't try to fix malformed input
4. **Encode output**: Escape data for safe display
5. **Validate type and format**: Ensure correct data types

**Cerberus Input Validation:**

```python
from cerberus.security import InputValidator, ValidationRules, DataSanitizer
from cerberus.guardians import InputGuardian

class SecureInputHandling:
    def __init__(self):
        self.input_validator = InputValidator()
        self.validation_rules = ValidationRules()
        self.data_sanitizer = DataSanitizer()
        self.input_guardian = InputGuardian()
    
    def define_validation_rules(self):
        """
        Define validation rules for common input types.
        """
        self.validation_rules.add_rule('email', {
            'type': 'string',
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'max_length': 254
        })
        
        self.validation_rules.add_rule('username', {
            'type': 'string',
            'pattern': r'^[a-zA-Z0-9_-]{3,32}$',
            'blacklist': ['admin', 'root', 'system']
        })
        
        self.validation_rules.add_rule('password', {
            'type': 'string',
            'min_length': 12,
            'max_length': 128,
            'requires_mixed_case': True,
            'requires_numbers': True,
            'requires_special_chars': True
        })
        
        self.validation_rules.add_rule('phone', {
            'type': 'string',
            'pattern': r'^\+?1?\d{9,15}$'
        })
        
        self.validation_rules.add_rule('file_upload', {
            'type': 'file',
            'allowed_extensions': ['.pdf', '.doc', '.docx', '.xls'],
            'max_size': 10485760,  # 10MB
            'scan_for_malware': True
        })
    
    def validate_user_input(self, input_data, rule_name):
        """
        Validate user input against defined rules.
        """
        try:
            rule = self.validation_rules.get_rule(rule_name)
            
            if not rule:
                raise ValidationError(f"No rule defined for '{rule_name}'")
            
            # Type check
            if not self.input_validator.check_type(input_data, rule['type']):
                self.input_guardian.log_validation_failure(
                    rule_name,
                    "type_mismatch",
                    input_data
                )
                raise ValidationError(f"Invalid type for {rule_name}")
            
            # Pattern check
            if 'pattern' in rule:
                if not self.input_validator.match_pattern(input_data, rule['pattern']):
                    self.input_guardian.log_validation_failure(
                        rule_name,
                        "pattern_mismatch",
                        input_data
                    )
                    raise ValidationError(f"Invalid format for {rule_name}")
            
            # Length check
            if 'min_length' in rule:
                if len(input_data) < rule['min_length']:
                    raise ValidationError(
                        f"Input too short (min: {rule['min_length']})"
                    )
            
            if 'max_length' in rule:
                if len(input_data) > rule['max_length']:
                    raise ValidationError(
                        f"Input too long (max: {rule['max_length']})"
                    )
            
            # Blacklist check
            if 'blacklist' in rule:
                if input_data.lower() in rule['blacklist']:
                    self.input_guardian.log_validation_failure(
                        rule_name,
                        "blacklist_match",
                        input_data
                    )
                    raise ValidationError(f"'{input_data}' is not allowed")
            
            self.input_guardian.log_validation_success(rule_name)
            return True
            
        except ValidationError as e:
            self.input_guardian.log_security_event("validation_error", str(e))
            raise
    
    def sanitize_output(self, data, context='html'):
        """
        Sanitize data for safe output in specific context.
        """
        if context == 'html':
            return self.data_sanitizer.html_escape(data)
        elif context == 'sql':
            return self.data_sanitizer.sql_escape(data)
        elif context == 'url':
            return self.data_sanitizer.url_encode(data)
        elif context == 'javascript':
            return self.data_sanitizer.javascript_escape(data)
        else:
            raise ValueError(f"Unknown context: {context}")
```

### 3.2 Common Injection Attacks

**SQL Injection**

Attackers inject SQL code to manipulate database queries.

```python
# VULNERABLE CODE - DO NOT USE
def vulnerable_user_lookup(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# SECURE CODE - USE THIS
def secure_user_lookup(user_id):
    # Parameterized query prevents injection
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
```

**Command Injection**

Attackers inject shell commands into system calls.

```python
# VULNERABLE CODE - DO NOT USE
import subprocess
def vulnerable_file_processing(filename):
    subprocess.run(f"process_file {filename}", shell=True)

# SECURE CODE - USE THIS
def secure_file_processing(filename):
    # Use list form to avoid shell interpretation
    subprocess.run(['process_file', filename], shell=False)
```

**Cross-Site Scripting (XSS)**

Attackers inject JavaScript code into web pages.

```html
<!-- VULNERABLE - DO NOT USE -->
<div><%= user_comment %></div>

<!-- SECURE - USE THIS -->
<div><%= escapeHtml(user_comment) %></div>
```

---

## Encryption & Cryptography

### 4.1 Encryption Fundamentals

**Symmetric Encryption**

Same key encrypts and decrypts data.

```python
from cerberus.security import EncryptionManager, CryptoAlgorithms
from cerberus.guardians import CryptoGuardian

class SymmetricEncryption:
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.crypto_algorithms = CryptoAlgorithms()
        self.crypto_guardian = CryptoGuardian()
    
    def encrypt_data(self, plaintext, key):
        """
        Encrypt data using AES-256-GCM.
        """
        # Generate random IV
        iv = self.encryption_manager.generate_iv(16)
        
        # Encrypt with AES-256-GCM
        ciphertext, auth_tag = self.encryption_manager.encrypt(
            plaintext=plaintext,
            key=key,
            iv=iv,
            algorithm='AES-256-GCM'
        )
        
        # Log encryption operation
        self.crypto_guardian.log_encryption_operation(
            algorithm='AES-256-GCM',
            data_size=len(plaintext)
        )
        
        # Return IV + ciphertext + auth_tag
        return {
            'iv': iv,
            'ciphertext': ciphertext,
            'auth_tag': auth_tag
        }
    
    def decrypt_data(self, encrypted_data, key):
        """
        Decrypt data using AES-256-GCM.
        """
        try:
            plaintext = self.encryption_manager.decrypt(
                ciphertext=encrypted_data['ciphertext'],
                key=key,
                iv=encrypted_data['iv'],
                auth_tag=encrypted_data['auth_tag'],
                algorithm='AES-256-GCM'
            )
            
            self.crypto_guardian.log_decryption_operation(
                algorithm='AES-256-GCM',
                success=True
            )
            
            return plaintext
            
        except Exception as e:
            self.crypto_guardian.log_decryption_operation(
                algorithm='AES-256-GCM',
                success=False,
                error=str(e)
            )
            raise
```

**Asymmetric Encryption**

Different keys for encryption (public) and decryption (private).

```python
from cerberus.security import RSAManager, KeyPair

class AsymmetricEncryption:
    def __init__(self):
        self.rsa_manager = RSAManager()
        self.crypto_guardian = CryptoGuardian()
    
    def generate_key_pair(self, key_size=2048):
        """
        Generate RSA key pair.
        """
        public_key, private_key = self.rsa_manager.generate_keypair(key_size)
        
        self.crypto_guardian.log_key_generation(
            algorithm='RSA',
            key_size=key_size
        )
        
        return public_key, private_key
    
    def encrypt_with_public_key(self, plaintext, public_key):
        """
        Encrypt with public key (only recipient's private key can decrypt).
        """
        ciphertext = self.rsa_manager.encrypt(
            plaintext,
            public_key,
            padding='OAEP'
        )
        
        return ciphertext
    
    def decrypt_with_private_key(self, ciphertext, private_key):
        """
        Decrypt with private key.
        """
        plaintext = self.rsa_manager.decrypt(
            ciphertext,
            private_key,
            padding='OAEP'
        )
        
        return plaintext
```

### 4.2 Key Management

```python
from cerberus.security import KeyVault, KeyRotationManager
from cerberus.guardians import KeyGuardian

class SecureKeyManagement:
    def __init__(self):
        self.key_vault = KeyVault()
        self.key_rotation = KeyRotationManager()
        self.key_guardian = KeyGuardian()
    
    def store_encryption_key(self, key_id, key_material, key_type):
        """
        Store encryption key in secure vault with audit logging.
        """
        # Verify key strength
        if len(key_material) < 32:  # Minimum 256 bits
            raise KeyError("Key material insufficient (minimum 256 bits)")
        
        # Store in HSM or secure vault
        self.key_vault.store_key(
            key_id=key_id,
            key_material=key_material,
            key_type=key_type,
            metadata={
                'created_at': datetime.now(),
                'rotation_interval': 90,  # days
                'algorithm': 'AES-256'
            }
        )
        
        self.key_guardian.log_key_storage(key_id, key_type)
    
    def rotate_encryption_keys(self):
        """
        Rotate encryption keys according to policy.
        """
        keys_to_rotate = self.key_vault.get_keys_requiring_rotation()
        
        for old_key_id in keys_to_rotate:
            # Generate new key
            new_key = self.key_vault.generate_key(key_type='AES-256')
            new_key_id = f"{old_key_id}_v2"
            
            # Store new key
            self.key_vault.store_key(new_key_id, new_key, 'AES-256')
            
            # Re-encrypt data with new key
            data_encrypted_with_old_key = self.key_vault.find_data(old_key_id)
            
            for data_item in data_encrypted_with_old_key:
                plaintext = self.decrypt_data(data_item, old_key_id)
                re_encrypted = self.encrypt_data(plaintext, new_key_id)
                self.key_vault.update_data(data_item['id'], re_encrypted, new_key_id)
            
            # Mark old key as rotated
            self.key_vault.mark_key_rotated(old_key_id)
            self.key_guardian.log_key_rotation(old_key_id, new_key_id)
```

---

## Guardians Security Framework

### 5.1 Guardian Architecture

Cerberus Guardians are modular security components that enforce policies and monitor security:

**Guardian Types:**

1. **AuthenticationGuardian**: Manages authentication policies and anomaly detection
2. **AccessGuardian**: Enforces authorization and logs access events
3. **InputGuardian**: Validates and sanitizes input
4. **CryptoGuardian**: Monitors cryptographic operations
5. **IncidentGuardian**: Detects and responds to security incidents
6. **ComplianceGuardian**: Ensures regulatory compliance

### 5.2 Guardian Implementation Example

```python
from cerberus.guardians import BaseGuardian, GuardianRegistry
from datetime import datetime, timedelta

class CustomSecurityGuardian(BaseGuardian):
    def __init__(self, name):
        super().__init__(name)
        self.policies = {}
        self.events = []
        self.alerts = []
    
    def register_policy(self, policy_name, policy_rule, severity='medium'):
        """
        Register a security policy.
        """
        self.policies[policy_name] = {
            'rule': policy_rule,
            'severity': severity,
            'created_at': datetime.now()
        }
    
    def evaluate_policy(self, policy_name, context):
        """
        Evaluate if policy is violated in given context.
        """
        if policy_name not in self.policies:
            raise PolicyNotFound(f"Policy '{policy_name}' not registered")
        
        policy = self.policies[policy_name]
        
        try:
            is_violated = not policy['rule'](context)
            
            if is_violated:
                self.raise_alert(
                    policy_name,
                    context,
                    policy['severity']
                )
            
            return not is_violated
            
        except Exception as e:
            self.log_event('policy_evaluation_error', {
                'policy': policy_name,
                'error': str(e)
            })
            raise
    
    def raise_alert(self, policy_name, context, severity):
        """
        Raise security alert when policy violated.
        """
        alert = {
            'timestamp': datetime.now(),
            'policy': policy_name,
            'context': context,
            'severity': severity,
            'status': 'open'
        }
        
        self.alerts.append(alert)
        self.log_event('security_alert', alert)
        
        # Take automated action based on severity
        if severity == 'critical':
            self.escalate_to_security_team(alert)
        elif severity == 'high':
            self.notify_managers(alert)
    
    def escalate_to_security_team(self, alert):
        """
        Escalate critical alert to security team.
        """
        # In production, would integrate with incident management
        print(f"CRITICAL ALERT: {alert['policy']}")
        print(f"Context: {alert['context']}")
    
    def log_event(self, event_type, event_data):
        """
        Log security event with timestamp.
        """
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'data': event_data
        }
        
        self.events.append(event)
    
    def get_events(self, filters=None):
        """
        Retrieve logged events with optional filtering.
        """
        events = self.events
        
        if filters:
            if 'start_time' in filters:
                events = [e for e in events 
                         if e['timestamp'] >= filters['start_time']]
            
            if 'end_time' in filters:
                events = [e for e in events 
                         if e['timestamp'] <= filters['end_time']]
            
            if 'event_type' in filters:
                events = [e for e in events 
                         if e['type'] == filters['event_type']]
        
        return events
```

---

## Incident Response Planning

### 6.1 Incident Response Framework

**Phases:**

1. **Preparation**: Tools, processes, team training
2. **Detection & Analysis**: Identify and assess incident
3. **Containment**: Stop spread, preserve evidence
4. **Eradication**: Remove attacker access and malware
5. **Recovery**: Restore systems to normal operation
6. **Post-Incident**: Learn and improve

### 6.2 Incident Response Procedures

```python
from cerberus.security import IncidentManager, ThreatAnalyzer
from cerberus.guardians import IncidentGuardian

class IncidentResponseProcedure:
    def __init__(self):
        self.incident_manager = IncidentManager()
        self.threat_analyzer = ThreatAnalyzer()
        self.incident_guardian = IncidentGuardian()
        self.incident_log = []
    
    def detect_security_incident(self, detection_source, alert_details):
        """
        Detect and classify security incident.
        """
        # Create incident record
        incident = {
            'incident_id': self.incident_manager.generate_incident_id(),
            'detection_source': detection_source,
            'detected_at': datetime.now(),
            'status': 'detected',
            'severity': 'unknown',
            'events': [alert_details]
        }
        
        # Analyze threat
        analysis = self.threat_analyzer.analyze(alert_details)
        
        # Classify severity
        incident['severity'] = self.classify_severity(analysis)
        
        # Log detection
        self.incident_guardian.log_incident_detection(incident)
        self.incident_log.append(incident)
        
        # Notify incident response team
        if incident['severity'] in ['high', 'critical']:
            self.incident_guardian.activate_incident_response_team(incident)
        
        return incident
    
    def classify_severity(self, analysis):
        """
        Classify incident severity based on analysis.
        """
        severity_factors = {
            'has_data_exfiltration': 'critical',
            'has_ransomware': 'critical',
            'has_malware': 'high',
            'has_unauthorized_access': 'high',
            'has_failed_access_attempts': 'medium',
            'has_suspicious_activity': 'medium'
        }
        
        max_severity_level = {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}
        max_level = 0
        max_severity = 'low'
        
        for factor, severity in severity_factors.items():
            if analysis.get(factor):
                level = max_severity_level[severity]
                if level > max_level:
                    max_level = level
                    max_severity = severity
        
        return max_severity
    
    def contain_incident(self, incident_id):
        """
        Contain incident to prevent further damage.
        """
        incident = self.incident_manager.get_incident(incident_id)
        
        # Step 1: Isolate affected systems
        affected_systems = self.identify_affected_systems(incident)
        
        for system in affected_systems:
            self.incident_guardian.isolate_system(system)
        
        incident['status'] = 'contained'
        incident['contained_at'] = datetime.now()
        incident['isolation_actions'] = affected_systems
        
        # Step 2: Preserve evidence
        self.preserve_evidence(incident)
        
        # Step 3: Notify stakeholders
        self.incident_guardian.notify_stakeholders(
            incident,
            "Incident contained - investigation ongoing"
        )
        
        self.incident_log.append(incident)
    
    def preserve_evidence(self, incident):
        """
        Preserve forensic evidence from incident.
        """
        evidence_collection = {
            'incident_id': incident['incident_id'],
            'collected_at': datetime.now(),
            'evidence_items': []
        }
        
        # Collect logs
        logs = self.incident_manager.collect_system_logs(incident)
        evidence_collection['evidence_items'].append({
            'type': 'system_logs',
            'data': logs,
            'hash': self.incident_guardian.compute_hash(logs)
        })
        
        # Collect memory dumps
        memory_dumps = self.incident_manager.collect_memory_dumps(incident)
        evidence_collection['evidence_items'].append({
            'type': 'memory_dumps',
            'data': memory_dumps,
            'hash': self.incident_guardian.compute_hash(memory_dumps)
        })
        
        # Store evidence in secure vault
        self.incident_guardian.store_evidence(evidence_collection)
    
    def generate_incident_report(self, incident_id):
        """
        Generate comprehensive incident report.
        """
        incident = self.incident_manager.get_incident(incident_id)
        
        report = {
            'incident_id': incident['incident_id'],
            'executive_summary': self.generate_executive_summary(incident),
            'timeline': self.generate_timeline(incident),
            'affected_systems': self.identify_affected_systems(incident),
            'root_cause': self.analyze_root_cause(incident),
            'recommendations': self.generate_recommendations(incident),
            'generated_at': datetime.now()
        }
        
        return report
    
    def generate_executive_summary(self, incident):
        """
        Generate executive summary of incident.
        """
        return f"""
        Incident ID: {incident['incident_id']}
        Detection Time: {incident['detected_at']}
        Severity: {incident['severity']}
        Status: {incident['status']}
        
        Summary: Security incident detected involving {incident['detection_source']}.
        Systems affected and contained. Investigation ongoing.
        """
    
    def generate_timeline(self, incident):
        """
        Generate chronological timeline of incident.
        """
        timeline = []
        
        for event in incident['events']:
            timeline.append({
                'timestamp': event.get('timestamp', incident['detected_at']),
                'event': event.get('description', 'Event recorded'),
                'severity': event.get('severity', 'medium')
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline
    
    def generate_recommendations(self, incident):
        """
        Generate recommendations to prevent similar incidents.
        """
        recommendations = [
            "Review and strengthen access controls",
            "Implement additional monitoring",
            "Update security policies",
            "Conduct security awareness training",
            "Patch vulnerable systems",
            "Review and improve detection capabilities"
        ]
        
        if incident['severity'] == 'critical':
            recommendations.extend([
                "Conduct full security audit",
                "Review third-party access",
                "Consider incident response drill"
            ])
        
        return recommendations
```

---

## Assessment & Exercises

### 7.1 Knowledge Assessment Quiz

**Question 1: Multi-Factor Authentication**

Q: Which of the following represents two factors of authentication?
- A) Password and security question
- B) Password and biometric fingerprint
- C) Username and password
- D) Email and password

**Answer: B** - Password (knowledge factor) and biometric fingerprint (inherence factor) are different authentication factors.

**Question 2: Principle of Least Privilege**

Q: What does the Principle of Least Privilege require?

A) All users should have full system access
B) Users should have minimum necessary permissions for their job
C) Administrators should enforce strict access controls
D) Permissions should be reviewed quarterly

**Answer: B** - PoLP requires granting minimum necessary permissions.

**Question 3: Input Validation**

Q: What is the best approach to input validation?

A) Accept all input and try to fix malformed data
B) Use a blacklist of dangerous inputs
C) Use a whitelist of valid input patterns
D) Trust user input by default

**Answer: C** - Whitelist valid patterns, reject everything else.

### 7.2 Hands-On Exercises

**Exercise 1: Implement Secure Authentication**

```
Task: Implement a secure authentication system with:
- Password validation policy (minimum 12 characters, mixed case, numbers, special chars)
- Rate limiting (5 failed attempts = lock for 30 minutes)
- MFA requirement for sensitive operations
- Session timeout after 30 minutes of inactivity

Deliverables:
1. Code implementing authentication
2. Unit tests covering all scenarios
3. Documentation of security properties
```

**Exercise 2: Access Control Review**

```
Task: Review and audit user permissions in a sample system:
- Identify users with excessive permissions
- Document which permissions are actually used
- Propose permission reductions
- Identify separation of duty violations

Deliverables:
1. Audit report with findings
2. Permission reduction recommendations
3. Risk assessment for current permissions
```

**Exercise 3: Secure Input Validation**

```
Task: Create input validation module for a web application:
- Validate email addresses
- Validate usernames
- Validate file uploads
- Prevent common injection attacks

Deliverables:
1. Validation code with unit tests
2. Documentation of validation rules
3. Examples of attacks prevented
```

### 7.3 Assessment Criteria

| Criteria | Proficient | Competent | Developing |
|----------|-----------|-----------|-----------|
| **Authentication Knowledge** | Can explain all three authentication factors and implement MFA | Can explain 2+ factors and basic MFA | Can explain 1-2 factors |
| **Authorization Design** | Can design RBAC and ABAC systems | Can design RBAC systems with PoLP | Understands basic role concepts |
| **Input Validation** | Can identify and prevent multiple injection types | Can identify and prevent common injections | Aware of injection risks |
| **Cryptography** | Can implement encryption with proper key management | Can implement basic encryption | Understands encryption concepts |
| **Incident Response** | Can lead incident response following procedures | Can execute incident response procedures | Understands IR phases |

---

## Summary

This comprehensive security training covers:

✅ **Authentication & Identity**: Factors, MFA, password management, session security
✅ **Authorization & Access Control**: RBAC, ABAC, Principle of Least Privilege
✅ **Input Validation**: Validation strategies, injection attack prevention
✅ **Encryption & Cryptography**: Symmetric/asymmetric encryption, key management
✅ **Guardians Framework**: Security enforcement and monitoring
✅ **Incident Response**: Detection, containment, recovery, reporting
✅ **Practical Exercises**: Hands-on implementation and assessment

**Next Steps:**
1. Complete all exercises
2. Pass knowledge assessment
3. Participate in incident response drills
4. Maintain certification with annual refresher training

---

**Document Version**: 1.0
**Last Updated**: 2024
**Training Duration**: 8-10 hours
**Certification Valid For**: 1 year
