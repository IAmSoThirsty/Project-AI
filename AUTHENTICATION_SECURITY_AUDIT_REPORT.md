---
type: report
report_type: audit
report_date: 2026-02-08T15:00:00Z
project_phase: security-audit
completion_percentage: 100
tags:
  - status/needs-attention
  - security/authentication
  - audit/critical-gaps
  - risk/high
area: authentication-authorization
stakeholders:
  - security-team
  - backend-team
  - devops-team
supersedes: []
related_reports:
  - SECURITY_VULNERABILITY_ASSESSMENT_REPORT.md
  - ACCOUNT_LOCKOUT_IMPLEMENTATION_REPORT.md
next_report: ACCOUNT_LOCKOUT_IMPLEMENTATION_REPORT.md
impact:
  - Critical security gaps identified
  - Dual authentication systems documented
  - High risk flagged for production
  - Missing account lockout mechanism
verification_method: security-code-review
risk_level: high
critical_gaps: multiple
---

# Project-AI Authentication & Authorization Security Audit

**Audit Date:** 2026-02-08
**Scope:** Core authentication/authorization modules
**Auditor:** GitHub Copilot CLI
**Status:** ⚠️ NEEDS ATTENTION - Multiple critical gaps identified

---

## Executive Summary

Project-AI implements **dual authentication systems** with strong cryptographic foundations but exhibits **critical security gaps** in session management, password policies, timing attack protection, and account recovery. The system lacks comprehensive authorization (RBAC is partially implemented but not enforced), has no account lockout in the primary auth system, and is vulnerable to timing attacks in password verification.

**Risk Level:** 🔴 **HIGH** - Production deployment without remediation poses security risks.

---

## 1. Authentication Security Assessment

### 1.1 Password Hashing (UserManager)

**Location:** `src/app/core/user_manager.py`

#### ✅ Strengths

1. **Strong Hashing Algorithms**
   - Uses `passlib` with dual-scheme support: `pbkdf2_sha256` (preferred) + `bcrypt` (fallback)
   - Automatic migration from plaintext passwords (lines 69-89)
   - Legacy hash migration on authentication
   - 100,000 PBKDF2 iterations (industry standard)

2. **Proper Implementation**
   ```python
   pwd_context = CryptContext(
       schemes=["pbkdf2_sha256", "bcrypt"],
       deprecated="auto",
   )
   ```
   - Uses `passlib.context` for algorithm agility
   - Proper salt generation (automatic in passlib)
   - Hash verification via `pwd_context.verify()` (line 128)

3. **Secure Defaults**
   - Password hash stored separately from user data
   - `get_user_data()` sanitizes output by removing `password_hash` (line 170)

#### ⚠️ Weaknesses

1. **NO Password Policy Enforcement** 🔴 **CRITICAL**
   - `create_user()` accepts **ANY** password without validation
   - No minimum length requirement
   - No complexity requirements (uppercase, lowercase, digits, special chars)
   - **Evidence:** Line 142-163 - no validation before hashing

2. **NO Account Lockout Mechanism** 🔴 **CRITICAL**
   - `authenticate()` allows unlimited login attempts (line 119-134)
   - No failed attempt tracking
   - No temporary account locking
   - Vulnerable to brute-force attacks

3. **Timing Attack Vulnerability** 🔴 **CRITICAL**
   - Password verification returns immediately for non-existent users (line 122-123)
   - Different execution paths for user existence vs. wrong password
   - Allows username enumeration via response timing
   - **Recommendation:** Use constant-time comparison for user lookup

4. **NO Rate Limiting on Authentication** 🔴 **CRITICAL**
   - No integration with rate limiting systems
   - Can be exploited for credential stuffing attacks

5. **Weak Fallback on Hashing Failure**
   - Silent fallback to weaker PBKDF2 if bcrypt fails (line 104-112)
   - No warning to administrators
   - Migration may skip users if hashing fails (returns `False`, line 112)

### 1.2 Master Password System (CommandOverride)

**Location:** `src/app/core/command_override.py`

#### ✅ Strengths

1. **Strong Hashing with Migration**
   - Modern bcrypt/PBKDF2 hashing (lines 125-136)
   - Automatic migration from legacy SHA-256 hashes (lines 184-205)
   - 100,000 PBKDF2 iterations
   - Proper salt generation (`os.urandom(16)`)

2. **Comprehensive Audit Logging**
   - All authentication attempts logged (lines 104-117)
   - Success/failure tracking
   - Timestamp + action + details
   - Immutable append-only log

3. **Emergency Lockdown**
   - `emergency_lockdown()` revokes auth and restores all protections (lines 284-295)
   - Good fail-safe mechanism

#### ⚠️ Weaknesses

1. **Timing Attack Vulnerability** 🔴 **CRITICAL**
   - SHA-256 comparison in legacy migration (line 186)
   - Should use `secrets.compare_digest()` for constant-time comparison
   - PBKDF2 verification uses string equality (line 157)
   - **Evidence:**
     ```python
     if hashlib.sha256(password.encode("utf-8")).hexdigest() == legacy_hash:
     ```

2. **NO Password Policy Enforcement**
   - `set_master_password()` accepts any password (line 166-175)
   - No complexity requirements
   - No strength validation

3. **NO Account Lockout**
   - Unlimited authentication attempts allowed
   - Only session expiry (auth_timestamp tracking, but no timeout enforcement visible)

4. **Session Management Issues**
   - `auth_timestamp` recorded but no session timeout enforcement
   - No session invalidation on password change
   - `logout()` clears auth but doesn't invalidate active session tokens

### 1.3 Advanced Authentication (Hydra-50 Security)

**Location:** `src/app/core/hydra_50_security.py`

#### ✅ Strengths (Production-Grade)

1. **Comprehensive Password Policy** 🎯 **BEST PRACTICE**
   ```python
   # Line 165-185
   - Minimum 8 characters
   - Uppercase + lowercase required
   - Digit required
   - Special character required (!@#$%^&*()_+-=[]{}|;:,.<>?)
   ```

2. **Account Lockout Protection** 🎯 **BEST PRACTICE**
   ```python
   # Lines 303-321
   - Tracks failed login attempts
   - Locks account after 5 failed attempts
   - 15-minute lockout period (900 seconds)
   - Resets counter on successful login
   ```

3. **Robust Session Management**
   - Session expiration (configurable, default 60 minutes)
   - CSRF token generation (`secrets.token_urlsafe(32)`)
   - IP address + User-Agent tracking
   - Automatic session cleanup on expiry

4. **RBAC Implementation**
   - Role hierarchy: VIEWER → OPERATOR → ADMIN → SUPER_ADMIN
   - Permission-based access control (READ, WRITE, EXECUTE, DELETE, ADMIN)
   - `check_permission()` method (line 326-328)

5. **Input Validation**
   - SQL injection detection (lines 188-194)
   - XSS detection (lines 197-203)
   - Username/email validation (regex patterns)

6. **API Key Management**
   - Key hashing (not stored in plaintext)
   - Expiration support
   - Usage tracking

#### ⚠️ Weaknesses

1. **NOT INTEGRATED** 🔴 **CRITICAL**
   - This module exists but is **not used** by the main application
   - `UserManager` (primary auth) lacks these features
   - Hydra-50 appears to be a standalone security framework
   - **Evidence:** No imports of `Hydra50Security` in `main.py` or GUI modules

2. **User Data Storage**
   - Users stored in plaintext JSON (lines 330-365)
   - Should encrypt sensitive fields at rest
   - No database integration (SQLite/PostgreSQL would be more robust)

---

## 2. Authorization Gaps

### 2.1 Role-Based Access Control (RBAC)

#### Current State

1. **Partial Implementation**
   - `UserManager` stores `role` field (line 160)
   - Default role: `"user"` for all new accounts
   - `update_user()` allows role modification (line 197-216)

2. **NO ENFORCEMENT** 🔴 **CRITICAL**
   - No permission checks in application code
   - No access control middleware
   - GUI doesn't check user roles before enabling features
   - **Evidence:** `LeatherBookInterface` initializes without role validation (line 39-86)

3. **Hydra-50 RBAC Exists But Unused**
   - Full RBAC system in `hydra_50_security.py` (lines 47-64)
   - Permission hierarchy defined
   - `check_permission()` method available
   - **Not integrated** with UserManager or application logic

### 2.2 Privilege Escalation Risks

1. **Unrestricted User Updates**
   - Any authenticated user can call `update_user()` to change their own role
   - No authorization check before role modification
   - **Vulnerability:** Privilege escalation from `user` → `admin`

2. **Command Override System**
   - Master password grants **ALL** privileges
   - No granular permissions
   - Binary auth: authenticated = full control

### 2.3 Missing Authorization Controls

1. **No resource-level permissions**
2. **No action-based authorization**
3. **No attribute-based access control (ABAC)**
4. **No permission inheritance or delegation**

---

## 3. Password Policy Adequacy

### 3.1 Current Policies

| System | Min Length | Complexity | Lockout | Expiration | Reset |
|--------|-----------|-----------|---------|-----------|-------|
| UserManager | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| CommandOverride | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| Hydra-50 | ✅ 8 chars | ✅ Full | ✅ 5 attempts | ❌ None | ❌ None |
| Dashboard Utils | ✅ 8 chars | ⚠️ Partial | ❌ None | ❌ None | ❌ None |

**Dashboard Utils Policy** (used in GUI, `dashboard_utils.py` lines 171-179):
```python
- Minimum 8 characters
- Uppercase letter required
- Digit required
- NO lowercase check
- NO special character check
```

### 3.2 Recommendations (NIST 800-63B Compliance)

1. **Minimum Length:** 12 characters (current: none or 8)
2. **Complexity:** Require 3 of 4 categories (upper, lower, digit, special)
3. **Blacklist:** Common passwords (e.g., "password123", "admin")
4. **Password History:** Prevent reuse of last 5 passwords
5. **Expiration:** 90-day rotation for privileged accounts
6. **Strength Meter:** Provide real-time feedback during creation

### 3.3 CRITICAL: No Password Reset Flow

**Missing Functionality:**
- No `forgot_password()` method
- No password reset tokens
- No email verification for password changes
- No security questions or recovery codes

**Risk:** Account lockout = permanent data loss

---

## 4. Session Security Evaluation

### 4.1 Desktop Application

**Session Management:**
- `LeatherBookInterface.backend_token` stores token (line 42)
- No session timeout enforcement
- No token refresh mechanism
- No secure storage (plaintext in memory)

**Vulnerabilities:**
1. **Indefinite Sessions**
   - Token never expires in desktop app
   - No inactivity timeout
   - User logout only clears `current_user` (UserManager line 134)

2. **No Token Validation**
   - Backend token never validated after creation
   - No signature verification
   - No tampering protection

3. **No Session Binding**
   - Token not bound to IP address
   - Token not bound to device fingerprint
   - Allows token theft and replay

### 4.2 Web Backend

**Location:** `web/backend/app.py`

#### ⚠️ CRITICAL ISSUES

1. **Plaintext Password Storage** 🔴 **CRITICAL**
   ```python
   # Lines 20-23
   _USERS: dict[str, dict[str, str]] = {
       "admin": {"password": "open-sesame", "role": "superuser"},
       "guest": {"password": "letmein", "role": "viewer"},
   }
   ```
   - Passwords stored in plaintext in memory
   - Hardcoded credentials
   - **FOR TESTING ONLY** - must not be used in production

2. **Weak Token Generation**
   ```python
   # Line 62
   token = f"token-{username}"
   ```
   - Predictable tokens (NOT cryptographically random)
   - No signature or HMAC
   - Trivial to forge

3. **No Token Expiration**
   - Tokens never expire
   - Stored indefinitely in `_TOKENS` dict (line 24)
   - No cleanup mechanism

4. **No Session Binding**
   - Token not bound to IP or User-Agent
   - Allows token theft and reuse

5. **Missing Security Headers**
   - No `X-Content-Type-Options`
   - No `X-Frame-Options`
   - No `Content-Security-Policy`
   - No HTTPS enforcement

### 4.3 Hydra-50 Session Management (Unused)

**Proper Implementation:**
```python
# Lines 442-481
- Cryptographically secure session IDs (secrets.token_urlsafe(32))
- Configurable timeout (default 60 minutes)
- Automatic expiry cleanup
- CSRF token generation
- IP + User-Agent binding
```

**Status:** Not integrated with application

---

## 5. Account Lockout Mechanisms

### 5.1 Current State

| System | Lockout Implemented | Threshold | Duration | Unlock Method |
|--------|-------------------|-----------|----------|---------------|
| UserManager | ❌ None | N/A | N/A | N/A |
| CommandOverride | ❌ None | N/A | N/A | N/A |
| Hydra-50 | ✅ Yes | 5 attempts | 15 min | Automatic |

### 5.2 Hydra-50 Lockout Logic

```python
# Lines 316-321
if user.failed_login_attempts >= 5:
    user.locked_until = time.time() + 900  # 15 minutes
```

**Features:**
- Counter increments on failed login
- Resets to 0 on successful login
- Time-based unlock (no admin intervention needed)
- Logged to audit trail

**Missing:**
- No progressive delays (exponential backoff)
- No CAPTCHA after N attempts
- No alert to user or admin
- No IP-based lockout (only account-based)

---

## 6. Password Reset Flows

### ❌ CRITICAL GAP: No Password Reset Mechanism

**Missing Components:**
1. **Forgot Password Flow**
   - No password reset request endpoint
   - No email verification
   - No reset token generation

2. **Reset Token Management**
   - No token expiration
   - No one-time use enforcement
   - No secure token storage

3. **Email Integration**
   - No SMTP configuration for password resets
   - Emergency alert system exists but not used for auth

4. **Security Questions**
   - No fallback authentication method
   - No recovery codes

**Current Workarounds:**
- Admin must manually call `UserManager.set_password(username, new_password)`
- No self-service password reset

**Recommendation:** Implement full password reset flow with:
- Time-limited reset tokens (15-minute expiry)
- Email verification
- Rate limiting on reset requests
- Audit logging

---

## 7. Authentication Logging & Audit Trails

### 7.1 Current Logging

#### UserManager
**Coverage:** ❌ **NONE**
- No logging on `authenticate()` success/failure
- No login attempt tracking
- No suspicious activity detection

#### CommandOverride
**Coverage:** ✅ **EXCELLENT**
- All auth attempts logged (lines 104-117)
- Action + details + timestamp + status
- Append-only audit file (`command_override_audit.log`)
- `get_audit_log(lines=50)` retrieves recent entries

**Example Log Entry:**
```
[2026-02-08T12:34:56] SUCCESS: AUTHENTICATE | Details: Authentication successful
```

#### Hydra-50
**Coverage:** ✅ **GOOD**
- Logs user creation, authentication, lockouts
- Uses Python `logging` module
- Configurable log levels

### 7.2 Missing Logging

1. **Login Events**
   - No logging of successful logins in UserManager
   - No failed login tracking
   - No session creation logging

2. **Account Changes**
   - No audit trail for role changes
   - No logging of password changes
   - No tracking of user metadata updates

3. **Anomaly Detection**
   - No detection of unusual login locations
   - No alerts on multiple failed attempts
   - No tracking of concurrent sessions

### 7.3 Recommendations

1. **Centralized Audit System**
   - Implement `AuthAuditLogger` class
   - Structured logging (JSON format)
   - Integrate with SIEM tools

2. **Logged Events**
   - Login success/failure
   - Password changes
   - Role changes
   - Session creation/expiry
   - Account lockouts

3. **Tamper Protection**
   - Cryptographic signing of log entries
   - Write-once storage (append-only)
   - Periodic integrity checks

---

## 8. Timing Attack Vulnerabilities

### 8.1 Identified Vulnerabilities

#### UserManager.authenticate()
```python
# Lines 122-123 - VULNERABLE
user = self.users.get(username)
if not user:
    return False  # IMMEDIATE RETURN - timing leak
```

**Attack Vector:**
1. Attacker sends login request with known-invalid username
2. Response is instant (no password hash verification)
3. Attacker sends login request with valid username + wrong password
4. Response is delayed (bcrypt verification ~100ms)
5. **Result:** Attacker can enumerate valid usernames

**Fix:**
```python
def authenticate(self, username, password):
    # Always verify password even if user doesn't exist
    user = self.users.get(username)
    
    # Use dummy hash for non-existent users
    if not user:
        # Burn same CPU time as real verification
        pwd_context.verify(password, "$2b$12$dummy_hash_placeholder")
        return False
    
    # Verify actual password
    password_hash = user.get("password_hash")
    if not password_hash:
        pwd_context.verify(password, "$2b$12$dummy_hash_placeholder")
        return False
        
    try:
        if pwd_context.verify(password, password_hash):
            self.current_user = username
            return True
    except Exception:
        return False
    return False
```

#### CommandOverride.authenticate()
```python
# Line 186 - VULNERABLE (legacy migration)
if hashlib.sha256(password.encode("utf-8")).hexdigest() == legacy_hash:
```

**Fix:** Use `secrets.compare_digest()`
```python
import secrets
if secrets.compare_digest(
    hashlib.sha256(password.encode("utf-8")).hexdigest(),
    legacy_hash
):
```

#### CommandOverride PBKDF2 Verification
```python
# Line 157 - VULNERABLE
return base64.b64encode(dk).decode() == stored_dk
```

**Fix:**
```python
import secrets
return secrets.compare_digest(
    base64.b64encode(dk).decode(),
    stored_dk
)
```

### 8.2 Impact

- **Username Enumeration:** Attackers can identify valid accounts
- **Credential Stuffing:** Targeted attacks on known accounts
- **Information Disclosure:** Leaks system architecture details

---

## 9. Critical Recommendations

### 9.1 IMMEDIATE (P0 - Critical)

1. **Fix Timing Attacks** 🔴
   - Add dummy hash verification in `UserManager.authenticate()`
   - Use `secrets.compare_digest()` in all hash comparisons
   - Ensure constant-time execution paths
   - **Files:** `user_manager.py`, `command_override.py`

2. **Implement Password Policies** 🔴
   - Add validation in `UserManager.create_user()` and `set_password()`
   - Enforce Hydra-50 policy (8 chars, uppercase, lowercase, digit, special)
   - Reject common passwords (use `passlib.pwd.strength()`)
   - **Files:** `user_manager.py`

3. **Add Account Lockout to UserManager** 🔴
   - Track failed login attempts (store in user dict)
   - Lock account for 15 minutes after 5 failed attempts
   - Log lockout events
   - **Files:** `user_manager.py`

4. **Replace Web Backend Auth** 🔴
   - Remove hardcoded plaintext passwords
   - Integrate with `UserManager` or Hydra-50
   - Use cryptographically secure tokens (JWT or `secrets.token_urlsafe()`)
   - Add token expiration (1-hour default)
   - **Files:** `web/backend/app.py`

5. **Implement Authentication Logging** 🔴
   - Log all login attempts (success + failure)
   - Include timestamp, username, IP, User-Agent
   - Create `AuthAuditLogger` class
   - **Files:** `user_manager.py`, new `auth_audit.py`

### 9.2 HIGH PRIORITY (P1)

6. **Integrate Hydra-50 Security** 🟠
   - Replace `UserManager` with `Hydra50Security.AuthenticationManager`
   - Migrate existing users to Hydra-50 format
   - Update GUI to use Hydra-50 session management
   - **Effort:** 2-3 days
   - **Benefit:** Gains RBAC, lockout, strong policies, SQL injection protection

7. **Implement RBAC Enforcement** 🟠
   - Add `@require_permission` decorator
   - Check user role before privileged operations
   - Restrict `update_user()` role changes to admins only
   - **Files:** `user_manager.py`, GUI modules

8. **Add Session Security** 🟠
   - Implement session timeout (30-minute inactivity)
   - Add session refresh mechanism
   - Bind sessions to IP + User-Agent
   - Invalidate sessions on password change
   - **Files:** `leather_book_interface.py`, `user_manager.py`

9. **Implement Password Reset Flow** 🟠
   - Generate secure reset tokens (`secrets.token_urlsafe(32)`)
   - 15-minute token expiration
   - Email integration (use existing `EmergencyAlert` SMTP config)
   - One-time use enforcement
   - **Files:** New `password_reset.py`, `user_manager.py`

10. **Add Rate Limiting to Auth Endpoints** 🟠
    - Use existing `RateLimiter` from `hydra_50_security.py`
    - Limit login attempts: 10/minute per IP
    - Limit password reset requests: 3/hour per account
    - **Files:** `user_manager.py`, `web/backend/app.py`

### 9.3 MEDIUM PRIORITY (P2)

11. **Enhance Password Policies**
    - Increase minimum to 12 characters
    - Add password history (prevent reuse of last 5)
    - Implement password strength meter (zxcvbn library)
    - Add password expiration (90 days for admins)

12. **Add Multi-Factor Authentication (MFA)**
    - TOTP (Time-based One-Time Password) via `pyotp`
    - Backup codes (10 one-time codes)
    - Optional SMS/email verification
    - **Note:** Hydra-50 has partial MFA in `mfa_auth.py` (not reviewed in detail)

13. **Improve Session Management**
    - Implement secure session storage (encrypted cookies)
    - Add "Remember Me" functionality (30-day tokens)
    - Concurrent session limits (max 3 active sessions)
    - Session revocation UI

14. **Add Security Headers**
    - `Strict-Transport-Security` (HSTS)
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `Content-Security-Policy`
    - **Files:** `web/backend/app.py`

15. **Encrypt User Data at Rest**
    - Encrypt sensitive fields in `users.json` (using Fernet)
    - Rotate encryption keys
    - Use database instead of JSON (SQLite/PostgreSQL)

---

## 10. Testing Recommendations

### 10.1 Security Test Coverage

**Current Tests:**
- `test_user_manager.py` - Basic auth tests (11 tests)
- `test_user_manager_extended.py` - Extended tests (20+ tests)
- `test_command_override_extended.py` - Override tests (12 tests)

**Missing Tests:**
1. Timing attack resistance tests
2. Account lockout validation
3. Password policy enforcement tests
4. RBAC permission tests
5. Session timeout tests
6. Token expiration tests
7. Password reset flow tests

### 10.2 Recommended Test Suite

```python
# test_auth_security.py

def test_timing_attack_resistance():
    """Verify constant-time execution for invalid vs. valid usernames"""
    # Measure time for non-existent user
    # Measure time for valid user + wrong password
    # Assert times are within 10ms of each other

def test_account_lockout():
    """Verify account locks after 5 failed attempts"""
    # Attempt login 5 times with wrong password
    # Assert 6th attempt returns "Account locked"
    # Wait 15 minutes (use time.sleep or mock time)
    # Assert login succeeds

def test_password_policy_enforcement():
    """Verify password policy is enforced"""
    # Try weak passwords (too short, no uppercase, etc.)
    # Assert all are rejected
    # Try strong password
    # Assert accepted

def test_rbac_permission_checks():
    """Verify role-based access control"""
    # Create user with 'viewer' role
    # Attempt privileged operation
    # Assert denied
    # Create user with 'admin' role
    # Assert allowed

def test_session_expiration():
    """Verify sessions expire after timeout"""
    # Create session
    # Mock time advance by 31 minutes
    # Attempt to use session
    # Assert rejected as expired
```

### 10.3 Penetration Testing

**Recommended Tests:**
1. **Brute Force Attack Simulation**
   - 1,000 login attempts in 1 minute
   - Verify account lockout triggers

2. **Credential Stuffing**
   - Test with known leaked credentials
   - Verify rate limiting prevents mass attempts

3. **Session Hijacking**
   - Capture session token
   - Attempt to use from different IP
   - Verify session binding prevents reuse

4. **Privilege Escalation**
   - Create user with 'viewer' role
   - Attempt to call `update_user(role='admin')`
   - Verify operation is denied

---

## 11. Compliance Gaps

### 11.1 OWASP Top 10 (2021)

| Vulnerability | Status | Details |
|--------------|--------|---------|
| A01: Broken Access Control | 🔴 **FAIL** | No RBAC enforcement |
| A02: Cryptographic Failures | ⚠️ **PARTIAL** | Web backend uses plaintext passwords |
| A03: Injection | ⚠️ **PARTIAL** | Hydra-50 has SQL/XSS detection but not used |
| A04: Insecure Design | 🔴 **FAIL** | No password reset, no session expiry |
| A05: Security Misconfiguration | ⚠️ **PARTIAL** | Missing security headers |
| A07: Identification/Auth Failures | 🔴 **FAIL** | No lockout, timing attacks, weak sessions |

### 11.2 NIST 800-63B (Digital Identity Guidelines)

| Requirement | Status | Details |
|------------|--------|---------|
| Minimum 8-character passwords | ⚠️ **PARTIAL** | Hydra-50 compliant, UserManager not |
| No composition rules | 🔴 **FAIL** | Should allow passphrases |
| Password breach checking | ❌ **NOT IMPLEMENTED** | No HaveIBeenPwned integration |
| Rate limiting on auth | ❌ **NOT IMPLEMENTED** | No rate limits on UserManager |
| MFA for sensitive operations | ❌ **NOT IMPLEMENTED** | No MFA |

### 11.3 CIS Controls (v8)

| Control | Status | Implementation |
|---------|--------|---------------|
| 6.3: Require MFA | ❌ **MISSING** | No MFA |
| 6.4: Require Strong Passwords | ⚠️ **PARTIAL** | Hydra-50 only |
| 6.5: Rotate Passwords | ❌ **MISSING** | No expiration |
| 8.3: Audit Logging | ⚠️ **PARTIAL** | CommandOverride only |
| 8.5: Centralized Log Collection | ❌ **MISSING** | No centralization |

---

## 12. Detailed Code Fixes

### Fix 1: Timing Attack Resistance (UserManager)

**File:** `src/app/core/user_manager.py`

```python
# Replace lines 119-134
def authenticate(self, username, password):
    """Authenticate a user using stored bcrypt password hash.
    
    Uses constant-time execution to prevent username enumeration.
    """
    import secrets
    
    user = self.users.get(username)
    
    # Always verify password even if user doesn't exist (constant-time)
    if not user:
        # Burn CPU time equivalent to real bcrypt verification
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux3N8u7YmeXa"
        try:
            pwd_context.verify(password, dummy_hash)
        except Exception:
            pass
        return False
    
    password_hash = user.get("password_hash")
    if not password_hash:
        # No hash stored - burn time anyway
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux3N8u7YmeXa"
        try:
            pwd_context.verify(password, dummy_hash)
        except Exception:
            pass
        return False
    
    try:
        if pwd_context.verify(password, password_hash):
            self.current_user = username
            return True
    except Exception:
        return False
    
    return False
```

### Fix 2: Password Policy Validation

**File:** `src/app/core/user_manager.py`

```python
# Add after line 26 (after pwd_context definition)
def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements.
    
    Requirements (aligned with Hydra-50):
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    # Optional: Check against common passwords
    common_passwords = ["password", "123456", "password123", "admin", "letmein"]
    if password.lower() in common_passwords:
        return False, "Password is too common and easily guessable"
    
    return True, "Password is strong"


# Update create_user() - replace lines 135-163
def create_user(
    self,
    username,
    password,
    persona: str = "friendly",
    preferences=None,
):
    """Create a new user with a hashed password.
    
    Returns True if created, False if user already exists or password invalid.
    """
    if preferences is None:
        preferences = {
            "language": "en",
            "style": "casual",
        }
    
    if username in self.users:
        return False
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        logger.warning(f"User creation failed for {username}: {error_msg}")
        return False
    
    pw_hash = pwd_context.hash(password)
    self.users[username] = {
        "password_hash": pw_hash,
        "persona": persona,
        "preferences": preferences,
        "location_active": False,
        "approved": True,
        "role": "user",
        "failed_login_attempts": 0,  # Add for lockout tracking
        "locked_until": None,         # Add for lockout tracking
    }
    self.save_users()
    logger.info(f"User created: {username}")
    return True


# Update set_password() - add validation
def set_password(self, username, new_password):
    """Set a new password for an existing user (hashes it).
    
    Returns:
        (success, error_message)
    """
    if username not in self.users:
        return False, "User not found"
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return False, error_msg
    
    self.users[username]["password_hash"] = pwd_context.hash(new_password)
    self.users[username].pop("password", None)  # Remove plaintext if exists
    self.save_users()
    
    logger.info(f"Password changed for user: {username}")
    return True, "Password updated successfully"
```

### Fix 3: Account Lockout

**File:** `src/app/core/user_manager.py`

```python
# Update authenticate() to add lockout logic
def authenticate(self, username, password):
    """Authenticate a user using stored bcrypt password hash.
    
    Implements account lockout after 5 failed attempts (15-minute lockout).
    Uses constant-time execution to prevent username enumeration.
    """
    import secrets
    import time
    
    user = self.users.get(username)
    
    # Always verify password even if user doesn't exist (constant-time)
    if not user:
        # Burn CPU time equivalent to real bcrypt verification
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux3N8u7YmeXa"
        try:
            pwd_context.verify(password, dummy_hash)
        except Exception:
            pass
        return False
    
    # Check if account is locked
    locked_until = user.get("locked_until")
    if locked_until and time.time() < locked_until:
        logger.warning(f"Login attempt for locked account: {username}")
        # Still burn time for constant-time execution
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux3N8u7YmeXa"
        try:
            pwd_context.verify(password, dummy_hash)
        except Exception:
            pass
        return False
    
    password_hash = user.get("password_hash")
    if not password_hash:
        # No hash stored - burn time anyway
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux3N8u7YmeXa"
        try:
            pwd_context.verify(password, dummy_hash)
        except Exception:
            pass
        return False
    
    try:
        if pwd_context.verify(password, password_hash):
            # Success - reset failed attempt counter
            user["failed_login_attempts"] = 0
            user["locked_until"] = None
            self.current_user = username
            self.save_users()
            logger.info(f"User authenticated: {username}")
            return True
        else:
            # Failed authentication - increment counter
            user["failed_login_attempts"] = user.get("failed_login_attempts", 0) + 1
            
            # Lock account after 5 failed attempts
            if user["failed_login_attempts"] >= 5:
                user["locked_until"] = time.time() + 900  # 15 minutes
                logger.warning(f"Account locked due to failed login attempts: {username}")
            
            self.save_users()
            return False
    except Exception as e:
        logger.error(f"Authentication error for {username}: {e}")
        return False
    
    return False
```

### Fix 4: Timing Attack in CommandOverride

**File:** `src/app/core/command_override.py`

```python
# Add import at top
import secrets

# Replace line 186 (in authenticate method)
# OLD:
# if hashlib.sha256(password.encode("utf-8")).hexdigest() == legacy_hash:

# NEW:
if secrets.compare_digest(
    hashlib.sha256(password.encode("utf-8")).hexdigest(),
    legacy_hash
):

# Replace line 157 (in _verify_bcrypt_or_pbkdf2 method)
# OLD:
# return base64.b64encode(dk).decode() == stored_dk

# NEW:
return secrets.compare_digest(
    base64.b64encode(dk).decode(),
    stored_dk
)
```

### Fix 5: Web Backend Security

**File:** `web/backend/app.py`

```python
# Replace entire file with secure implementation

"""Flask backend for Project-AI's lightweight web API."""

from __future__ import annotations

import logging
import secrets
import time
from functools import wraps

try:
    from flask import Flask, jsonify, request
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Flask must be installed to use the Project-AI web backend."
    ) from exc

# Import UserManager for proper authentication
from app.core.user_manager import UserManager

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize UserManager
user_manager = UserManager(users_file="data/web_users.json")

# Session storage (in-memory for demo - use Redis in production)
_SESSIONS: dict[str, dict] = {}

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        if not token or token not in _SESSIONS:
            return jsonify(error="unauthorized", message="Valid token required"), 401
        
        session = _SESSIONS[token]
        
        # Check session expiry
        if time.time() > session["expires_at"]:
            del _SESSIONS[token]
            return jsonify(error="expired", message="Session expired"), 401
        
        # Refresh session on activity
        session["expires_at"] = time.time() + SESSION_TIMEOUT
        
        # Add user to request context
        request.current_user = session["username"]
        
        return f(*args, **kwargs)
    
    return decorated_function


@app.route("/api/status")
def status():
    """Return a simple health snapshot."""
    return jsonify(status="ok", component="web-backend"), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a user and return a session token."""
    payload = request.get_json(silent=True)
    if not payload:
        return (
            jsonify(error="missing-json", message="Request must include JSON body."),
            400,
        )

    username = (payload.get("username") or "").strip()
    password = payload.get("password")
    
    if not username or not password:
        return (
            jsonify(
                error="missing-credentials", message="username and password required"
            ),
            400,
        )

    # Use UserManager for authentication
    if not user_manager.authenticate(username, password):
        return (
            jsonify(
                error="invalid-credentials", message="Username or password incorrect"
            ),
            401,
        )
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Create session
    _SESSIONS[token] = {
        "username": username,
        "created_at": time.time(),
        "expires_at": time.time() + SESSION_TIMEOUT,
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
    }
    
    user_data = user_manager.get_user_data(username)
    
    return (
        jsonify(
            status="ok",
            token=token,
            user={"username": username, "role": user_data.get("role", "user")},
            expires_in=SESSION_TIMEOUT,
        ),
        200,
    )


@app.route("/api/auth/logout", methods=["POST"])
@require_auth
def logout():
    """Logout and invalidate session token."""
    token = request.headers.get("X-Auth-Token")
    if token in _SESSIONS:
        del _SESSIONS[token]
    return jsonify(status="ok", message="Logged out successfully"), 200


@app.route("/api/auth/profile", methods=["GET"])
@require_auth
def profile():
    """Return user profile if a valid token is provided."""
    username = request.current_user
    user_data = user_manager.get_user_data(username)
    
    return jsonify(
        status="ok",
        user={
            "username": username,
            "role": user_data.get("role", "user"),
            "persona": user_data.get("persona", "friendly"),
            "preferences": user_data.get("preferences", {}),
        }
    )


@app.route("/api/debug/force-error")
def force_error():
    """Endpoint intentionally raising an exception to test error handler."""
    raise RuntimeError("forced debug failure")


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    """Return JSON payload for unexpected errors while logging details."""
    logger.exception("Unhandled Flask backend error", exc_info=exc)
    return jsonify(status="error", message=str(exc)), 500


# Add security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 13. Summary Table

| Component | Current State | Risk | Priority | Effort |
|-----------|--------------|------|----------|--------|
| Password Hashing | ✅ Strong (bcrypt/PBKDF2) | ✅ Low | - | - |
| Password Policy | ❌ None (UserManager) | 🔴 High | P0 | 2 hours |
| Account Lockout | ❌ None (UserManager) | 🔴 High | P0 | 2 hours |
| Timing Attacks | ❌ Vulnerable | 🔴 High | P0 | 1 hour |
| Auth Logging | ❌ None (UserManager) | 🔴 High | P0 | 3 hours |
| RBAC Enforcement | ❌ Not enforced | 🔴 High | P1 | 1 day |
| Session Security | ❌ Weak (no timeout) | 🟠 Medium | P1 | 1 day |
| Password Reset | ❌ Missing | 🟠 Medium | P1 | 2 days |
| Rate Limiting | ❌ None | 🟠 Medium | P1 | 4 hours |
| Web Backend | 🔴 Plaintext passwords | 🔴 Critical | P0 | 3 hours |
| MFA | ❌ Missing | 🟡 Low | P2 | 1 week |
| Password Expiration | ❌ Missing | 🟡 Low | P2 | 1 day |

**Total Remediation Effort:** ~2 weeks for P0+P1 fixes

---

## 14. Conclusion

Project-AI has a **solid cryptographic foundation** with strong password hashing (bcrypt/PBKDF2) and a **sophisticated but unused** security framework (Hydra-50). However, the **actively used authentication system** (UserManager) has **critical gaps** that make it vulnerable to:

1. **Brute-force attacks** (no lockout, no rate limiting)
2. **Username enumeration** (timing attacks)
3. **Weak passwords** (no policy enforcement)
4. **Session hijacking** (no expiry, no binding)
5. **Privilege escalation** (no RBAC enforcement)

**Recommendation:** **BLOCK PRODUCTION DEPLOYMENT** until P0 fixes are implemented. The web backend is particularly concerning with plaintext passwords and predictable tokens.

**Positive Note:** The Hydra-50 security module demonstrates production-grade design. **Integrating it** as the primary auth system would resolve most issues instantly.

---

## 15. Next Steps

### Immediate Actions (This Week)

1. ✅ **Apply all P0 fixes** (timing attacks, password policy, lockout, web backend)
2. ✅ **Add authentication logging** to UserManager
3. ✅ **Run security test suite** (create tests from section 10.2)
4. ✅ **Document new password policy** in user-facing docs

### Short-Term (Next 2 Weeks)

5. ✅ **Integrate Hydra-50** as primary auth system
6. ✅ **Implement password reset flow**
7. ✅ **Add RBAC enforcement** in GUI
8. ✅ **Add rate limiting** to auth endpoints

### Long-Term (Next Month)

9. ✅ **Implement MFA** (TOTP)
10. ✅ **Add password expiration** for admins
11. ✅ **Migrate to database** (SQLite → PostgreSQL)
12. ✅ **Penetration testing** by external auditor

---

**Report Generated:** 2026-02-08  
**Status:** 🔴 **CRITICAL GAPS IDENTIFIED** - Remediation required before production use  
**Next Review:** After P0/P1 fixes implemented

