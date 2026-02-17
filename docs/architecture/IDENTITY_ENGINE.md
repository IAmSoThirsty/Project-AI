# Identity Engine Specification

**Version:** 1.0 **Last Updated:** 2026-01-23 **Status:** Specification

______________________________________________________________________

## Overview

The Identity Engine is responsible for managing user identities, authentication, authorization, and session management within the PACE system. It provides a secure foundation for all user interactions.

## Core Responsibilities

1. **Authentication**: Verify user credentials and issue tokens
1. **Authorization**: Validate user permissions for actions
1. **Session Management**: Track active user sessions
1. **Identity Storage**: Persist user identity data
1. **Token Management**: Issue, validate, and revoke tokens

## Architecture

```
┌─────────────────────────────────────────┐
│         Identity Manager                 │
├─────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐        │
│  │  Auth      │  │  Session   │        │
│  │  Provider  │  │  Manager   │        │
│  └────────────┘  └────────────┘        │
│                                         │
│  ┌────────────┐  ┌────────────┐        │
│  │   Token    │  │  Identity  │        │
│  │  Manager   │  │   Store    │        │
│  └────────────┘  └────────────┘        │
└─────────────────────────────────────────┘
```

## Authentication Flow

### Password-Based Authentication

```

1. User submits credentials (username, password)

   ↓

2. Identity Manager validates credentials

   ↓

3. Auth Provider verifies password hash

   ↓

4. If valid:
   - Load user identity from Identity Store
   - Create session via Session Manager
   - Generate token via Token Manager
   - Return identity + token

   ↓

5. If invalid:
   - Log failed attempt
   - Increment failure counter
   - Apply rate limiting
   - Return authentication error

```

### Token-Based Authentication

```

1. User submits request with token

   ↓

2. Identity Manager extracts token

   ↓

3. Token Manager validates token:
   - Check signature
   - Check expiration
   - Check revocation status

   ↓

4. If valid:
   - Load identity from token claims
   - Verify session still active
   - Return identity

   ↓

5. If invalid:
   - Log attempt
   - Return authentication error

```

## Implementation Details

### IdentityManager Class

```python
class IdentityManager:
    """
    Manages user identity, authentication, and authorization.

    This is the main entry point for all identity operations in the PACE system.
    It coordinates authentication providers, session management, and token issuance.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Identity Manager.

        Args:
            config: Configuration containing:

                - auth_provider: Authentication provider type ("local", "oauth", "ldap")
                - session_timeout: Session timeout in seconds (default: 3600)
                - token_lifetime: Token lifetime in seconds (default: 3600)
                - storage_backend: Identity storage backend ("json", "db")
                - data_dir: Directory for persistent storage

        """
        self.config = config
        self.auth_provider = self._create_auth_provider()
        self.session_manager = SessionManager(config)
        self.token_manager = TokenManager(config)
        self.identity_store = IdentityStore(config)

    def authenticate(self, credentials: Credentials) -> Identity:
        """
        Authenticate a user with provided credentials.

        Supports multiple authentication methods:

        - Password-based (username + password)
        - Token-based (JWT token)
        - OAuth (OAuth token)

        Args:
            credentials: User credentials

        Returns:
            Identity: Authenticated user identity

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit exceeded
        """

        # Rate limiting check

        if self._is_rate_limited(credentials.username):
            raise RateLimitError("Too many authentication attempts")

        # Delegate to auth provider

        try:
            identity = self.auth_provider.authenticate(credentials)
            self._reset_failure_count(credentials.username)
            return identity
        except AuthenticationError:
            self._increment_failure_count(credentials.username)
            raise

    def verify_token(self, token: str) -> bool:
        """
        Verify an authentication token.

        Args:
            token: JWT token to verify

        Returns:
            bool: True if token is valid and not expired
        """
        return self.token_manager.verify(token)

    def get_identity(self, user_id: str) -> Optional[Identity]:
        """
        Retrieve identity by user ID.

        Args:
            user_id: Unique user identifier

        Returns:
            Identity if found, None otherwise
        """
        return self.identity_store.get(user_id)

    def create_session(self, identity: Identity) -> Session:
        """
        Create a new session for an authenticated identity.

        Args:
            identity: Authenticated user identity

        Returns:
            Session: New session with token
        """
        session = self.session_manager.create(identity)
        token = self.token_manager.issue(identity, session.session_id)
        session.token = token
        return session

    def end_session(self, session_id: str) -> None:
        """
        End a user session.

        Args:
            session_id: Session identifier to terminate
        """
        self.session_manager.end(session_id)
        self.token_manager.revoke_by_session(session_id)

    def register_user(self, username: str, password: str, roles: List[str] = None) -> Identity:
        """
        Register a new user.

        Args:
            username: Unique username
            password: User password (will be hashed)
            roles: Optional list of roles

        Returns:
            Identity: Newly created identity

        Raises:
            IdentityError: If username already exists
        """
        if self.identity_store.exists(username):
            raise IdentityError(f"Username '{username}' already exists")

        # Create identity

        identity = Identity(
            user_id=self._generate_user_id(),
            username=username,
            roles=roles or ["user"],
            permissions=self._get_default_permissions(roles or ["user"]),
            metadata={}
        )

        # Store hashed password

        password_hash = self._hash_password(password)
        self.identity_store.store(identity, password_hash)

        return identity

    def update_password(self, user_id: str, old_password: str, new_password: str) -> None:
        """
        Update user password.

        Args:
            user_id: User identifier
            old_password: Current password for verification
            new_password: New password to set

        Raises:
            AuthenticationError: If old password is incorrect
        """

        # Verify old password

        identity = self.get_identity(user_id)
        if not identity:
            raise IdentityError(f"User '{user_id}' not found")

        credentials = Credentials(username=identity.username, password=old_password)
        if not self.auth_provider.verify_password(credentials):
            raise AuthenticationError("Current password is incorrect")

        # Update to new password

        password_hash = self._hash_password(new_password)
        self.identity_store.update_password(user_id, password_hash)

        # Invalidate all existing sessions

        self.session_manager.end_all_for_user(user_id)
```

## Session Management

### Session Lifecycle

```

1. Create: User authenticates successfully
2. Active: User makes requests with valid token
3. Refresh: Token refreshed before expiration
4. Expire: Session exceeds timeout or user logs out
5. Cleanup: Expired sessions removed periodically

```

### SessionManager Class

```python
class SessionManager:
    """
    Manages user sessions.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize session manager.

        Args:
            config: Configuration with session_timeout
        """
        self.config = config
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = config.get("session_timeout", 3600)

    def create(self, identity: Identity) -> Session:
        """Create a new session for an identity."""
        session_id = self._generate_session_id()
        session = Session(
            session_id=session_id,
            identity=identity,
            token="",  # Set by IdentityManager
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.session_timeout)
        )
        self.sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and session.expires_at > datetime.now():
            return session
        return None

    def end(self, session_id: str) -> None:
        """End a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def end_all_for_user(self, user_id: str) -> None:
        """End all sessions for a user."""
        to_remove = [
            sid for sid, session in self.sessions.items()
            if session.identity.user_id == user_id
        ]
        for sid in to_remove:
            del self.sessions[sid]

    def cleanup_expired(self) -> None:
        """Remove expired sessions."""
        now = datetime.now()
        to_remove = [
            sid for sid, session in self.sessions.items()
            if session.expires_at <= now
        ]
        for sid in to_remove:
            del self.sessions[sid]
```

## Token Management

### Token Format (JWT)

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "username": "john_doe",
    "roles": ["user", "admin"],
    "session_id": "session_123",
    "iat": 1706025600,
    "exp": 1706029200
  },
  "signature": "..."
}
```

### TokenManager Class

```python
class TokenManager:
    """
    Manages authentication tokens (JWT).
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize token manager.

        Args:
            config: Configuration with:

                - secret_key: Secret key for JWT signing
                - token_lifetime: Token lifetime in seconds

        """
        self.config = config
        self.secret_key = config.get("secret_key", self._generate_secret())
        self.token_lifetime = config.get("token_lifetime", 3600)
        self.revoked_tokens: Set[str] = set()

    def issue(self, identity: Identity, session_id: str) -> str:
        """
        Issue a new JWT token.

        Args:
            identity: User identity
            session_id: Associated session ID

        Returns:
            str: JWT token
        """
        payload = {
            "sub": identity.user_id,
            "username": identity.username,
            "roles": identity.roles,
            "session_id": session_id,
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(seconds=self.token_lifetime)).timestamp()
        }

        # In real implementation, use a proper JWT library

        token = self._encode_jwt(payload)
        return token

    def verify(self, token: str) -> bool:
        """
        Verify a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            bool: True if valid and not expired
        """
        if token in self.revoked_tokens:
            return False

        try:
            payload = self._decode_jwt(token)
            exp = payload.get("exp", 0)
            return datetime.now().timestamp() < exp
        except Exception:
            return False

    def revoke(self, token: str) -> None:
        """Revoke a token."""
        self.revoked_tokens.add(token)

    def revoke_by_session(self, session_id: str) -> None:
        """Revoke all tokens for a session."""

        # In real implementation, maintain token->session mapping

        pass
```

## Security Considerations

### Password Security

- Passwords hashed using bcrypt or Argon2
- Minimum password strength requirements enforced
- Password history maintained (prevent reuse)

### Token Security

- Tokens signed with strong secret key
- Short token lifetime (1 hour default)
- Token refresh mechanism for long sessions
- Token revocation support

### Rate Limiting

- Failed authentication attempts limited
- Progressive backoff on repeated failures
- IP-based rate limiting

### Session Security

- Session IDs cryptographically random
- Session timeout enforced
- Concurrent session limits
- Session hijacking prevention

## Configuration

```yaml
identity:
  auth_provider: "local"  # local, oauth, ldap
  session_timeout: 3600  # seconds
  token_lifetime: 3600  # seconds
  password_policy:
    min_length: 8
    require_uppercase: true
    require_lowercase: true
    require_digits: true
    require_special: true
  rate_limiting:
    max_attempts: 5
    lockout_duration: 300  # seconds
  storage:
    backend: "json"  # json, postgresql, mongodb
    data_dir: "./data/identity"
```

## Integration with Policy Engine

The Identity Engine works closely with the Policy Engine:

1. **Authentication Policies**: Policy engine validates authentication attempts
1. **Authorization Policies**: Policy engine checks user permissions for actions
1. **Session Policies**: Policy engine enforces session limits and timeout rules

## Monitoring and Logging

### Metrics

- Authentication success/failure rates
- Active session count
- Token issuance rate
- Failed authentication attempts by user/IP

### Logging

- All authentication attempts (success and failure)
- Session creation and termination
- Token issuance and revocation
- Password changes
- Rate limit violations

### Audit Trail

- User login/logout events
- Permission changes
- Failed access attempts
- Account lockouts

## See Also

- [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) - Identity Manager interface
- [PACE_ARCHITECTURE.md](PACE_ARCHITECTURE.md) - Overall architecture
- [CAPABILITY_MODEL.md](CAPABILITY_MODEL.md) - Capability authorization
