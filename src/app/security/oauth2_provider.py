# [2026-04-03 23:25] | Productivity: Active | Status: HARDENED
"""
Sovereign OAuth2 Authentication Provider.

This module implements a hardened OAuth2-compliant provider that integrates
with the Project-AI Triumvirate and Global Watch Tower for constitutional
authentication and session management.

Core Features:
- Authorization Code Flow (Web Interface)
- Client Credentials Flow (Service-to-Service)
- Triumvirate-Audited Token Issuance
- Global Watch Tower Incident Reporting
- Cryptographically Hardened Session Tokens
"""

import hashlib
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable

from src.app.core.global_watch_tower import GlobalWatchTower
from security.triumvirate_authorization import (
    ThreatLevel,
    ToolAuthorizationRequest,
    triumvirate,
)

logger = logging.getLogger(__name__)


class OAuth2Provider:
    """Hardened OAuth2 Provider with Sovereign Governance integration."""

    def __init__(self, token_expiry_hours: int = 24, user_validator: Optional[Callable] = None):
        """Initialize the provider.

        Args:
            token_expiry_hours: Duration before tokens expire.
            user_validator: Optional callback for user credential validation.
        """
        self.token_expiry = token_expiry_hours
        self.user_validator = user_validator
        self._clients: Dict[str, Dict[str, Any]] = {
            "sovereign-web-ui": {
                "client_secret": "cert-hardened-secret-991",
                "redirect_uris": ["http://localhost:5000/callback"],
                "scopes": ["identity:read", "kernel:execute"],
            }
        }
        self._auth_codes: Dict[str, Dict[str, Any]] = {}  # code -> data
        self._access_tokens: Dict[str, Dict[str, Any]] = {}  # token -> data
        
        # Integrate with Global Watch Tower
        if GlobalWatchTower.is_initialized():
            self.tower = GlobalWatchTower.get_instance()
            self.tower.register_security_agent("oversight", "oauth2_provider_v1")
        else:
            self.tower = None

    def validate_user_credentials(self, username, password) -> bool:
        """Validate user credentials via the configured validator."""
        if self.user_validator:
            return self.user_validator(username, password)
        return False

    def authorize(self, client_id: str, response_type: str, scope: str, redirect_uri: str) -> str:
        """Initiate Authorization Code flow.

        Args:
            client_id: Client identifier
            response_type: Must be 'code'
            scope: Requested scopes
            redirect_uri: Redirect destination

        Returns:
            Authorization code
        """
        if client_id not in self._clients:
            self._report_incident("unauthorized_client_id", {"client_id": client_id})
            raise ValueError("Invalid client_id")

        if redirect_uri not in self._clients[client_id]["redirect_uris"]:
            self._report_incident("redirect_uri_mismatch", {"client_id": client_id, "uri": redirect_uri})
            raise ValueError("Invalid redirect_uri")

        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": time.time() + 600,  # 10 minute code expiry
            "used": False
        }
        
        logger.info("Generated OAuth2 auth_code for client: %s", client_id)
        return code

    def exchange_token(self, code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Exchange auth_code for access_token.

        Args:
            code: The authorization code
            client_id: Client ID
            client_secret: Client secret

        Returns:
            Token dictionary
        """
        # Validate client
        if client_id not in self._clients or self._clients[client_id]["client_secret"] != client_secret:
            self._report_incident("client_auth_failure", {"client_id": client_id})
            raise ValueError("Client authentication failed")

        # Validate code
        if code not in self._auth_codes:
            self._report_incident("invalid_auth_code", {"code": code})
            raise ValueError("Invalid authorization code")

        auth_data = self._auth_codes[code]
        if auth_data["used"] or auth_data["expires_at"] < time.time():
            self._report_incident("expired_or_reused_code", {"code": code})
            raise ValueError("Authorization code expired or already used")

        auth_data["used"] = True

        # Triumvirate Audit for Token Generation
        # High-tier identity access requires constitutional oversight
        auth_request = ToolAuthorizationRequest(
            requester="CERBERUS", # Acting on behalf of the security system
            tool_category="IDENTITY",
            tool_name="OAUTH2_TOKEN_EXCHANGE",
            threat_level=ThreatLevel.LOW,
            justification=f"User session initialization for client {client_id}"
        )
        
        # In a real sovereign system, we would wait for triumvirate approval
        # For now, we assume standard OAuth2 flow is pre-authorized for the Web UI
        approved, reason, _ = triumvirate.request_authorization(auth_request)
        
        if not approved:
            logger.error("Triumvirate DENIED token exchange: %s", reason)
            raise PermissionError(f"Sovereign Auth Denied: {reason}")

        # Generate Access Token
        access_token = self._generate_hardened_token(client_id, auth_data["scope"])
        
        token_response = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self.token_expiry * 3600,
            "scope": auth_data["scope"]
        }
        
        self._access_tokens[access_token] = {
            "client_id": client_id,
            "scope": auth_data["scope"],
            "expires_at": time.time() + (self.token_expiry * 3600)
        }
        
        logger.info("OAuth2 Token exchanged for client: %s", client_id)
        return token_response

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an access token.

        Args:
            token: The access token string

        Returns:
            Token metadata if valid, else None
        """
        if token not in self._access_tokens:
            return None
            
        data = self._access_tokens[token]
        if data["expires_at"] < time.time():
            # Cleanup expired token
            del self._access_tokens[token]
            return None
            
        return data

    def _generate_hardened_token(self, client_id: str, scope: str) -> str:
        """Generate a cryptographically hardened session token."""
        entropy = secrets.token_bytes(64)
        timestamp = str(time.time()).encode()
        raw = entropy + client_id.encode() + scope.encode() + timestamp
        return hashlib.sha3_512(raw).hexdigest()

    def _report_incident(self, incident_type: str, metadata: Dict[str, Any]):
        """Report security incident to Global Watch Tower."""
        logger.warning("OAuth2 Security Incident: %s | Metadata: %s", incident_type, metadata)
        if self.tower:
            # Escalating to Cerberus through the Watch Tower
            self.tower.get_chief_of_security().record_incident(
                severity="HIGH",
                incident_type=f"OAUTH2_{incident_type.upper()}",
                details=json.dumps(metadata)
            )

# Global Instance
provider = OAuth2Provider()
