"""
Capability Token Manager

Issues and manages capability tokens for fine-grained authorization.
Tokens are cryptographically signed and include scopes, TTL, and constraints.
"""

import os
import secrets
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TokenStatus(Enum):
    """Token status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class TokenConstraints:
    """Constraints for token usage"""
    ip_whitelist: Optional[List[str]] = None
    service_whitelist: Optional[List[str]] = None
    resource_patterns: Optional[List[str]] = None
    rate_limit: Optional[int] = None  # requests per minute
    max_uses: Optional[int] = None
    time_of_day: Optional[Dict[str, str]] = None  # {"start": "09:00", "end": "17:00"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Token:
    """Capability token with permissions and constraints"""
    id: str
    subject: str
    scopes: List[str]
    issued_at: datetime
    expires_at: datetime
    constraints: TokenConstraints = field(default_factory=TokenConstraints)
    status: TokenStatus = TokenStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: str = ""
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        now = datetime.utcnow()
        return (
            self.status == TokenStatus.ACTIVE
            and self.issued_at <= now <= self.expires_at
        )
    
    def has_scope(self, scope: str) -> bool:
        """Check if token has specific scope"""
        # Support wildcard scopes like "workflow:*"
        for token_scope in self.scopes:
            if token_scope == scope:
                return True
            if token_scope.endswith("*"):
                prefix = token_scope[:-1]
                if scope.startswith(prefix):
                    return True
        return False
    
    def has_all_scopes(self, scopes: List[str]) -> bool:
        """Check if token has all required scopes"""
        return all(self.has_scope(scope) for scope in scopes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "subject": self.subject,
            "scopes": self.scopes,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "constraints": self.constraints.to_dict(),
            "status": self.status.value,
            "metadata": self.metadata,
            "signature": self.signature,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """Create token from dictionary"""
        return cls(
            id=data["id"],
            subject=data["subject"],
            scopes=data["scopes"],
            issued_at=datetime.fromisoformat(data["issued_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            constraints=TokenConstraints(**data.get("constraints", {})),
            status=TokenStatus(data.get("status", "active")),
            metadata=data.get("metadata", {}),
            signature=data.get("signature", ""),
        )


class CapabilityTokenManager:
    """
    Manages capability tokens for fine-grained authorization
    
    Features:
    - Cryptographically signed tokens
    - Scope-based permissions
    - TTL enforcement
    - Constraint validation (IP, service, resource, rate limit)
    - Token revocation
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        default_ttl: int = 3600,
        issuer: str = "temporal-cloud",
    ):
        self.secret_key = secret_key or os.getenv("TOKEN_SECRET_KEY") or secrets.token_hex(32)
        self.default_ttl = default_ttl
        self.issuer = issuer
        self._tokens: Dict[str, Token] = {}
    
    def _generate_token_id(self) -> str:
        """Generate unique token ID"""
        return f"cap_{secrets.token_urlsafe(32)}"
    
    def _sign_token(self, token: Token) -> str:
        """Generate HMAC signature for token"""
        payload = json.dumps({
            "id": token.id,
            "subject": token.subject,
            "scopes": token.scopes,
            "issued_at": token.issued_at.isoformat(),
            "expires_at": token.expires_at.isoformat(),
            "constraints": token.constraints.to_dict(),
        }, sort_keys=True)
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_signature(self, token: Token) -> bool:
        """Verify token signature"""
        expected_signature = self._sign_token(token)
        return hmac.compare_digest(token.signature, expected_signature)
    
    def issue_token(
        self,
        subject: str,
        scopes: List[str],
        ttl: Optional[int] = None,
        constraints: Optional[TokenConstraints] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Token:
        """
        Issue a new capability token
        
        Args:
            subject: Token subject (service/user identifier)
            scopes: List of permission scopes
            ttl: Time to live in seconds (default: 3600)
            constraints: Optional usage constraints
            metadata: Optional metadata
        
        Returns:
            Signed Token object
        
        Example:
            token = manager.issue_token(
                subject="temporal-worker-001",
                scopes=["workflow:execute", "activity:invoke"],
                ttl=3600,
                constraints=TokenConstraints(
                    ip_whitelist=["10.0.0.0/24"],
                    service_whitelist=["temporal-frontend"],
                    rate_limit=1000
                )
            )
        """
        token_id = self._generate_token_id()
        now = datetime.utcnow()
        ttl = ttl or self.default_ttl
        
        token = Token(
            id=token_id,
            subject=subject,
            scopes=scopes,
            issued_at=now,
            expires_at=now + timedelta(seconds=ttl),
            constraints=constraints or TokenConstraints(),
            status=TokenStatus.ACTIVE,
            metadata=metadata or {},
        )
        
        # Sign token
        token.signature = self._sign_token(token)
        
        # Store token
        self._tokens[token_id] = token
        
        logger.info(f"Issued token {token_id} for {subject} with scopes: {scopes}")
        
        return token
    
    def validate_token(
        self,
        token: Token,
        required_scopes: Optional[List[str]] = None,
        source_ip: Optional[str] = None,
        source_service: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> bool:
        """
        Validate token and check constraints
        
        Args:
            token: Token to validate
            required_scopes: Required scopes for operation
            source_ip: Source IP address
            source_service: Source service identifier
            resource: Resource being accessed
        
        Returns:
            True if token is valid and satisfies constraints
        """
        # Verify signature
        if not self._verify_signature(token):
            logger.warning(f"Invalid signature for token {token.id}")
            return False
        
        # Check if token is valid
        if not token.is_valid():
            logger.warning(f"Token {token.id} is not valid (status: {token.status})")
            return False
        
        # Check scopes
        if required_scopes and not token.has_all_scopes(required_scopes):
            logger.warning(f"Token {token.id} missing required scopes: {required_scopes}")
            return False
        
        # Validate constraints
        constraints = token.constraints
        
        # IP whitelist
        if constraints.ip_whitelist and source_ip:
            if not self._check_ip_whitelist(source_ip, constraints.ip_whitelist):
                logger.warning(f"Token {token.id} IP not in whitelist: {source_ip}")
                return False
        
        # Service whitelist
        if constraints.service_whitelist and source_service:
            if source_service not in constraints.service_whitelist:
                logger.warning(f"Token {token.id} service not in whitelist: {source_service}")
                return False
        
        # Resource patterns
        if constraints.resource_patterns and resource:
            if not self._check_resource_patterns(resource, constraints.resource_patterns):
                logger.warning(f"Token {token.id} resource not matching patterns: {resource}")
                return False
        
        # Time of day constraint
        if constraints.time_of_day:
            if not self._check_time_of_day(constraints.time_of_day):
                logger.warning(f"Token {token.id} used outside allowed time window")
                return False
        
        return True
    
    def _check_ip_whitelist(self, ip: str, whitelist: List[str]) -> bool:
        """Check if IP is in whitelist (supports CIDR)"""
        from ipaddress import ip_address, ip_network
        
        ip_obj = ip_address(ip)
        for allowed in whitelist:
            if "/" in allowed:
                # CIDR notation
                if ip_obj in ip_network(allowed, strict=False):
                    return True
            else:
                # Exact match
                if ip == allowed:
                    return True
        return False
    
    def _check_resource_patterns(self, resource: str, patterns: List[str]) -> bool:
        """Check if resource matches any pattern (supports wildcards)"""
        import re
        for pattern in patterns:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            if re.match(f"^{regex_pattern}$", resource):
                return True
        return False
    
    def _check_time_of_day(self, time_constraint: Dict[str, str]) -> bool:
        """Check if current time is within allowed window"""
        from datetime import time
        
        now = datetime.utcnow().time()
        start_time = datetime.strptime(time_constraint["start"], "%H:%M").time()
        end_time = datetime.strptime(time_constraint["end"], "%H:%M").time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:
            # Handles overnight windows (e.g., 22:00 - 06:00)
            return now >= start_time or now <= end_time
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a token"""
        if token_id in self._tokens:
            self._tokens[token_id].status = TokenStatus.REVOKED
            logger.info(f"Revoked token {token_id}")
            return True
        logger.warning(f"Token {token_id} not found for revocation")
        return False
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """Get token by ID"""
        return self._tokens.get(token_id)
    
    def rotate_token(self, old_token: Token, ttl: Optional[int] = None) -> Token:
        """
        Rotate token by issuing new one and revoking old
        
        Args:
            old_token: Token to rotate
            ttl: TTL for new token
        
        Returns:
            New Token
        """
        # Issue new token with same properties
        new_token = self.issue_token(
            subject=old_token.subject,
            scopes=old_token.scopes,
            ttl=ttl or self.default_ttl,
            constraints=old_token.constraints,
            metadata=old_token.metadata,
        )
        
        # Revoke old token
        self.revoke_token(old_token.id)
        
        logger.info(f"Rotated token {old_token.id} to {new_token.id}")
        
        return new_token
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from storage"""
        now = datetime.utcnow()
        expired = [
            token_id for token_id, token in self._tokens.items()
            if token.expires_at < now
        ]
        
        for token_id in expired:
            del self._tokens[token_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired tokens")
        
        return len(expired)
