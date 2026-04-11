"""
Token Validator

Validates capability tokens in different contexts (HTTP, gRPC, etc.)
"""

from typing import Optional, Dict, Any
import logging
from .token_manager import Token, CapabilityTokenManager

logger = logging.getLogger(__name__)


class TokenValidator:
    """
    Validates tokens in various contexts
    
    Supports validation for HTTP requests, gRPC calls, and custom contexts.
    """
    
    def __init__(self, token_manager: CapabilityTokenManager):
        self.token_manager = token_manager
    
    def validate_http_request(
        self,
        token: Token,
        required_scopes: list,
        request_headers: Dict[str, str],
        request_ip: str,
        resource_path: str,
    ) -> bool:
        """
        Validate token for HTTP request
        
        Args:
            token: Token to validate
            required_scopes: Required scopes for endpoint
            request_headers: HTTP headers
            request_ip: Client IP address
            resource_path: Resource being accessed
        
        Returns:
            True if token is valid for this request
        """
        # Extract service from headers
        source_service = request_headers.get("X-Service-Name")
        
        return self.token_manager.validate_token(
            token=token,
            required_scopes=required_scopes,
            source_ip=request_ip,
            source_service=source_service,
            resource=resource_path,
        )
    
    def validate_grpc_call(
        self,
        token: Token,
        required_scopes: list,
        metadata: Dict[str, str],
        peer_address: str,
        method_name: str,
    ) -> bool:
        """
        Validate token for gRPC call
        
        Args:
            token: Token to validate
            required_scopes: Required scopes for method
            metadata: gRPC metadata
            peer_address: Peer IP address
            method_name: gRPC method being called
        
        Returns:
            True if token is valid for this call
        """
        # Extract IP from peer address (format: "ipv4:1.2.3.4:port")
        source_ip = peer_address.split(":")[1] if ":" in peer_address else peer_address
        source_service = metadata.get("x-service-name")
        
        return self.token_manager.validate_token(
            token=token,
            required_scopes=required_scopes,
            source_ip=source_ip,
            source_service=source_service,
            resource=method_name,
        )
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """
        Extract token from Authorization header
        
        Supports formats:
        - Bearer <token>
        - Capability <token>
        
        Args:
            authorization_header: Authorization header value
        
        Returns:
            Token string or None
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split(" ", 1)
        if len(parts) != 2:
            return None
        
        scheme, token = parts
        if scheme.lower() in ("bearer", "capability"):
            return token
        
        return None
    
    def validate_token_string(
        self,
        token_string: str,
        required_scopes: Optional[list] = None,
        **context
    ) -> bool:
        """
        Validate token from string representation
        
        Args:
            token_string: Token ID or serialized token
            required_scopes: Required scopes
            **context: Additional validation context
        
        Returns:
            True if valid
        """
        # Get token from storage
        token = self.token_manager.get_token(token_string)
        if not token:
            logger.warning(f"Token not found: {token_string}")
            return False
        
        return self.token_manager.validate_token(
            token=token,
            required_scopes=required_scopes,
            source_ip=context.get("source_ip"),
            source_service=context.get("source_service"),
            resource=context.get("resource"),
        )
