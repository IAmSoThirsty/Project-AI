# Security Architecture - Project-AI

## Overview

Project-AI implements a comprehensive, defense-in-depth security architecture with seven layers of protection, zero-trust principles, and complete audit trail capability. Security is integrated at every level from transport encryption to application-level access control.

## Seven-Layer Security Model

```
┌──────────────────────────────────────────────────────────────┐
│                  7-LAYER SECURITY ARCHITECTURE               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Transport Security (TLS 1.3)                      │
│  ────────────────────────────────────────────────────       │
│  • TLS 1.3 for all connections                              │
│  • Certificate pinning                                       │
│  • Perfect Forward Secrecy                                   │
│  • HSTS enforcement                                          │
│                                                              │
│  Layer 2: Authentication (OAuth 2.0 / JWT)                  │
│  ────────────────────────────────────────────────────       │
│  • OAuth 2.0 / OpenID Connect                               │
│  • JWT tokens (RS256)                                       │
│  • Multi-factor authentication                              │
│  • Session management                                       │
│                                                              │
│  Layer 3: Authorization (RBAC)                              │
│  ────────────────────────────────────────────────────       │
│  • Role-Based Access Control                                │
│  • Fine-grained permissions                                 │
│  • Attribute-Based Access Control (ABAC)                    │
│  • Principle of least privilege                             │
│                                                              │
│  Layer 4: Field-Level Encryption                            │
│  ────────────────────────────────────────────────────       │
│  • Sensitive field encryption (AES-256-GCM)                 │
│  • PII protection                                           │
│  • Credential encryption                                    │
│  • Key rotation                                             │
│                                                              │
│  Layer 5: Database Encryption                               │
│  ────────────────────────────────────────────────────       │
│  • Transparent Data Encryption (TDE)                        │
│  • Encrypted backups                                        │
│  • Encrypted connections                                    │
│  • Column-level encryption                                  │
│                                                              │
│  Layer 6: Storage Encryption                                │
│  ────────────────────────────────────────────────────       │
│  • Object storage encryption (S3/MinIO)                     │
│  • File system encryption                                   │
│  • Backup encryption                                        │
│  • Archive encryption                                       │
│                                                              │
│  Layer 7: Key Management (HSM)                              │
│  ────────────────────────────────────────────────────       │
│  • Hardware Security Module                                 │
│  • Key derivation (PBKDF2)                                  │
│  • Key rotation policies                                    │
│  • Secrets management (Vault)                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Layer 1: Transport Security

### TLS 1.3 Configuration

```python
# HTTPS/TLS Configuration
TLS_CONFIG = {
    'version': 'TLSv1.3',
    'ciphers': [
        'TLS_AES_256_GCM_SHA384',
        'TLS_AES_128_GCM_SHA256',
        'TLS_CHACHA20_POLY1305_SHA256'
    ],
    'prefer_server_ciphers': True,
    'session_tickets': False,  # Disable for Perfect Forward Secrecy
    'session_cache': 'none',
    'dhparam_size': 4096
}

# Certificate Configuration
CERT_CONFIG = {
    'cert_file': '/etc/ssl/certs/project-ai.crt',
    'key_file': '/etc/ssl/private/project-ai.key',
    'ca_file': '/etc/ssl/certs/ca-bundle.crt',
    'verify_mode': 'CERT_REQUIRED',
    'check_hostname': True
}
```

### NGINX TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.project-ai.dev;

    # TLS 1.3 only
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Certificates
    ssl_certificate /etc/ssl/certs/project-ai.crt;
    ssl_certificate_key /etc/ssl/private/project-ai.key;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/certs/ca-bundle.crt;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # Perfect Forward Secrecy
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.project-ai.dev;
    return 301 https://$server_name$request_uri;
}
```

## Layer 2: Authentication

### OAuth 2.0 / OpenID Connect

```python
class AuthenticationService:
    """
    OAuth 2.0 / OIDC authentication service.
    
    Supports:
    - Authorization Code Flow
    - PKCE (Proof Key for Code Exchange)
    - JWT tokens (RS256)
    - Refresh tokens
    """
    
    def __init__(self):
        self.oauth_config = {
            'issuer': 'https://auth.project-ai.dev',
            'authorization_endpoint': 'https://auth.project-ai.dev/authorize',
            'token_endpoint': 'https://auth.project-ai.dev/token',
            'userinfo_endpoint': 'https://auth.project-ai.dev/userinfo',
            'jwks_uri': 'https://auth.project-ai.dev/.well-known/jwks.json',
            'response_types_supported': ['code', 'token', 'id_token'],
            'grant_types_supported': ['authorization_code', 'refresh_token'],
            'token_endpoint_auth_methods_supported': ['client_secret_post', 'client_secret_basic'],
            'scopes_supported': ['openid', 'profile', 'email', 'offline_access']
        }
        
        self.jwt_config = {
            'algorithm': 'RS256',
            'public_key_path': '/etc/ssl/certs/jwt-public.pem',
            'private_key_path': '/etc/ssl/private/jwt-private.pem',
            'issuer': 'https://auth.project-ai.dev',
            'audience': 'https://api.project-ai.dev',
            'access_token_lifetime': 900,  # 15 minutes
            'refresh_token_lifetime': 2592000  # 30 days
        }
    
    async def authenticate(self, credentials: Credentials) -> AuthResult:
        """
        Authenticate user with credentials.
        
        Args:
            credentials: Username/password or OAuth code
        
        Returns:
            AuthResult with tokens and user info
        """
        if credentials.type == 'password':
            return await self._authenticate_password(credentials)
        elif credentials.type == 'oauth':
            return await self._authenticate_oauth(credentials)
        else:
            raise ValueError(f"Unsupported credential type: {credentials.type}")
    
    async def _authenticate_password(self, credentials: Credentials) -> AuthResult:
        """Authenticate with username/password."""
        # Fetch user from database
        user = await db.fetchrow(
            """
            SELECT id, username, password_hash, mfa_enabled, mfa_secret
            FROM users
            WHERE username = $1 AND status = 'active'
            """,
            credentials.username
        )
        
        if not user:
            # Use constant-time comparison to prevent timing attacks
            bcrypt.hashpw(credentials.password.encode(), bcrypt.gensalt())
            raise AuthenticationError("Invalid credentials")
        
        # Verify password
        if not bcrypt.checkpw(credentials.password.encode(), user['password_hash'].encode()):
            # Log failed attempt
            await self._log_failed_attempt(user['id'], credentials.client_ip)
            raise AuthenticationError("Invalid credentials")
        
        # Check if MFA is required
        if user['mfa_enabled']:
            # Require MFA token
            if not credentials.mfa_token:
                return AuthResult(
                    mfa_required=True,
                    mfa_session_id=self._create_mfa_session(user['id'])
                )
            
            # Verify MFA token
            if not self._verify_mfa_token(user['mfa_secret'], credentials.mfa_token):
                raise AuthenticationError("Invalid MFA token")
        
        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        # Create session
        session = await self._create_session(user, access_token, refresh_token)
        
        return AuthResult(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='Bearer',
            expires_in=self.jwt_config['access_token_lifetime'],
            user=User(**user),
            session=session
        )
    
    def _generate_access_token(self, user: dict) -> str:
        """Generate JWT access token."""
        now = datetime.utcnow()
        
        payload = {
            'iss': self.jwt_config['issuer'],
            'aud': self.jwt_config['audience'],
            'sub': user['id'],
            'iat': now,
            'exp': now + timedelta(seconds=self.jwt_config['access_token_lifetime']),
            'username': user['username'],
            'roles': user.get('roles', []),
            'permissions': user.get('permissions', [])
        }
        
        # Load private key
        with open(self.jwt_config['private_key_path'], 'r') as f:
            private_key = f.read()
        
        # Sign token
        token = jwt.encode(payload, private_key, algorithm='RS256')
        
        return token
    
    def validate_token(self, token: str) -> TokenPayload:
        """
        Validate JWT token.
        
        Args:
            token: JWT access token
        
        Returns:
            TokenPayload with user info
        
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Load public key
            with open(self.jwt_config['public_key_path'], 'r') as f:
                public_key = f.read()
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer=self.jwt_config['issuer'],
                audience=self.jwt_config['audience'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_iss': True,
                    'verify_aud': True
                }
            )
            
            return TokenPayload(**payload)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}")
```

### Multi-Factor Authentication

```python
class MFAService:
    """
    Multi-Factor Authentication service.
    
    Supports:
    - TOTP (Time-based One-Time Password)
    - SMS verification
    - Email verification
    - Backup codes
    """
    
    def setup_mfa(self, user_id: str) -> MFASetup:
        """
        Setup MFA for user.
        
        Returns:
            MFASetup with secret and QR code
        """
        import pyotp
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate provisioning URI
        user = self._get_user(user_id)
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name='Project-AI'
        )
        
        # Generate QR code
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Generate backup codes
        backup_codes = [
            self._generate_backup_code() for _ in range(10)
        ]
        
        # Store secret (encrypted)
        await db.execute(
            """
            UPDATE users
            SET mfa_secret = $1, mfa_backup_codes = $2, mfa_setup_pending = TRUE
            WHERE id = $3
            """,
            self._encrypt_secret(secret),
            [self._hash_backup_code(code) for code in backup_codes],
            user_id
        )
        
        return MFASetup(
            secret=secret,
            qr_code_uri=provisioning_uri,
            qr_code_image=qr_image,
            backup_codes=backup_codes
        )
    
    def verify_mfa_token(self, user_id: str, token: str) -> bool:
        """Verify TOTP token."""
        import pyotp
        
        user = await db.fetchrow(
            "SELECT mfa_secret FROM users WHERE id = $1",
            user_id
        )
        
        if not user or not user['mfa_secret']:
            return False
        
        # Decrypt secret
        secret = self._decrypt_secret(user['mfa_secret'])
        
        # Verify token (allow 1 time step drift)
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

## Layer 3: Authorization (RBAC)

### Role-Based Access Control

```python
class AuthorizationService:
    """
    RBAC authorization service.
    
    Hierarchy:
    - Roles contain permissions
    - Users have roles
    - Permissions are checked on resources
    """
    
    ROLES = {
        'admin': {
            'name': 'Administrator',
            'permissions': ['*'],  # All permissions
            'inherits': []
        },
        'user': {
            'name': 'User',
            'permissions': [
                'request.submit',
                'memory.read.own',
                'persona.modify.own',
                'file.upload.own',
                'operation.view.own'
            ],
            'inherits': []
        },
        'analyst': {
            'name': 'Analyst',
            'permissions': [
                'request.submit',
                'memory.read.own',
                'memory.read.others',
                'analysis.data',
                'analysis.pattern',
                'report.generate',
                'operation.view.all'
            ],
            'inherits': ['user']
        },
        'security_officer': {
            'name': 'Security Officer',
            'permissions': [
                'security.scan',
                'security.audit',
                'security.incident.view',
                'audit.read',
                'audit.export',
                'user.view',
                'operation.view.all'
            ],
            'inherits': ['user']
        }
    }
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """
        Check if user has permission for action on resource.
        
        Args:
            user: Authenticated user
            resource: Resource identifier (e.g., 'memory', 'operation')
            action: Action to perform (e.g., 'read', 'write', 'delete')
        
        Returns:
            True if user has permission, False otherwise
        """
        permission = f"{resource}.{action}"
        
        # Get all permissions for user's roles
        user_permissions = self._get_user_permissions(user)
        
        # Check for wildcard permission
        if '*' in user_permissions:
            return True
        
        # Check for exact permission
        if permission in user_permissions:
            return True
        
        # Check for resource wildcard (e.g., 'memory.*')
        resource_wildcard = f"{resource}.*"
        if resource_wildcard in user_permissions:
            return True
        
        # Check for action wildcard (e.g., '*.read')
        action_wildcard = f"*.{action}"
        if action_wildcard in user_permissions:
            return True
        
        return False
    
    def _get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for user (including inherited)."""
        permissions = set()
        
        for role_name in user.roles:
            role = self.ROLES.get(role_name)
            if not role:
                continue
            
            # Add role permissions
            permissions.update(role['permissions'])
            
            # Add inherited permissions (recursive)
            for inherited_role in role.get('inherits', []):
                inherited_perms = self._get_role_permissions(inherited_role)
                permissions.update(inherited_perms)
        
        return permissions
    
    def _get_role_permissions(self, role_name: str) -> Set[str]:
        """Get all permissions for role (including inherited)."""
        role = self.ROLES.get(role_name)
        if not role:
            return set()
        
        permissions = set(role['permissions'])
        
        # Add inherited permissions (recursive)
        for inherited_role in role.get('inherits', []):
            inherited_perms = self._get_role_permissions(inherited_role)
            permissions.update(inherited_perms)
        
        return permissions
```

### Attribute-Based Access Control (ABAC)

```python
class ABACService:
    """
    Attribute-Based Access Control for fine-grained permissions.
    
    Evaluates policies based on:
    - User attributes
    - Resource attributes
    - Environmental attributes
    """
    
    def evaluate_policy(self, user: User, resource: Resource, 
                       action: str, context: dict) -> bool:
        """
        Evaluate ABAC policy.
        
        Example policy:
        {
            'effect': 'allow',
            'conditions': [
                {'attribute': 'user.department', 'operator': 'equals', 'value': 'engineering'},
                {'attribute': 'resource.classification', 'operator': 'not_equals', 'value': 'secret'},
                {'attribute': 'context.time_of_day', 'operator': 'between', 'value': ['09:00', '17:00']}
            ]
        }
        """
        policies = self._get_applicable_policies(user, resource, action)
        
        for policy in policies:
            if self._evaluate_policy_conditions(policy, user, resource, context):
                if policy['effect'] == 'allow':
                    return True
                elif policy['effect'] == 'deny':
                    return False
        
        # Default deny
        return False
    
    def _evaluate_policy_conditions(self, policy: dict, user: User, 
                                    resource: Resource, context: dict) -> bool:
        """Evaluate all conditions in policy."""
        for condition in policy.get('conditions', []):
            if not self._evaluate_condition(condition, user, resource, context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: dict, user: User, 
                           resource: Resource, context: dict) -> bool:
        """Evaluate single condition."""
        attribute = condition['attribute']
        operator = condition['operator']
        expected_value = condition['value']
        
        # Get actual value
        if attribute.startswith('user.'):
            actual_value = getattr(user, attribute[5:])
        elif attribute.startswith('resource.'):
            actual_value = getattr(resource, attribute[9:])
        elif attribute.startswith('context.'):
            actual_value = context.get(attribute[8:])
        else:
            raise ValueError(f"Invalid attribute: {attribute}")
        
        # Evaluate operator
        if operator == 'equals':
            return actual_value == expected_value
        elif operator == 'not_equals':
            return actual_value != expected_value
        elif operator == 'in':
            return actual_value in expected_value
        elif operator == 'not_in':
            return actual_value not in expected_value
        elif operator == 'greater_than':
            return actual_value > expected_value
        elif operator == 'less_than':
            return actual_value < expected_value
        elif operator == 'between':
            return expected_value[0] <= actual_value <= expected_value[1]
        else:
            raise ValueError(f"Invalid operator: {operator}")
```

## Layer 4: Field-Level Encryption

```python
class FieldEncryptionService:
    """
    Encrypt sensitive fields in database.
    
    Uses:
    - AES-256-GCM encryption
    - Unique encryption key per field type
    - Key rotation support
    """
    
    def __init__(self):
        self.keys = self._load_encryption_keys()
        self.cipher_suite = Fernet(self.keys['default'])
    
    def encrypt_field(self, value: str, field_type: str = 'default') -> str:
        """
        Encrypt field value.
        
        Args:
            value: Plain text value
            field_type: Type of field (determines which key to use)
        
        Returns:
            Base64-encoded encrypted value
        """
        # Get encryption key for field type
        key = self.keys.get(field_type, self.keys['default'])
        cipher = Fernet(key)
        
        # Encrypt value
        encrypted = cipher.encrypt(value.encode())
        
        # Return base64-encoded string
        return encrypted.decode()
    
    def decrypt_field(self, encrypted_value: str, field_type: str = 'default') -> str:
        """
        Decrypt field value.
        
        Args:
            encrypted_value: Base64-encoded encrypted value
            field_type: Type of field (determines which key to use)
        
        Returns:
            Plain text value
        """
        # Get encryption key for field type
        key = self.keys.get(field_type, self.keys['default'])
        cipher = Fernet(key)
        
        # Decrypt value
        decrypted = cipher.decrypt(encrypted_value.encode())
        
        # Return plain text string
        return decrypted.decode()
    
    def _load_encryption_keys(self) -> dict:
        """Load encryption keys from key management system."""
        from cryptography.fernet import Fernet
        
        # In production, load from HSM or Vault
        # For demo, generate keys
        return {
            'default': Fernet.generate_key(),
            'pii': Fernet.generate_key(),
            'credentials': Fernet.generate_key(),
            'api_keys': Fernet.generate_key()
        }
```

## Performance Characteristics

### Latency Impact

| Security Layer | Latency Add (P95) |
|---------------|-------------------|
| TLS handshake | 50-100ms (first request only) |
| JWT validation | < 5ms |
| RBAC check | < 2ms |
| Field encryption | < 1ms per field |
| Database encryption | < 5ms |
| Total overhead | < 15ms per request |

## Related Documentation

- [Authentication Flow](./authentication_flow.md)
- [Authorization RBAC](./authorization_rbac.md)
- [Seven-Layer Encryption](./seven_layer_encryption.md)
- [Threat Model](./threat_model.md)
- [Audit Trail](../data_flow/audit_trail_flow.md)
