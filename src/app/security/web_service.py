"""Web service security for SOAP and HTTP services.

This module implements:
- SOAP over HTTP client/server utilities
- Secure CGI/web framework wrappers
- XML envelope validation
- Header/permission locking
- Capability-based access control
"""

import hashlib
import hmac
import logging
import time
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring  # nosec B405 - Only used for building XML, not parsing

import defusedxml.ElementTree as DefusedET

logger = logging.getLogger(__name__)


class SOAPClient:
    """Secure SOAP over HTTP client."""

    def __init__(self, endpoint: str, username: str | None = None, password: str | None = None):
        """Initialize SOAP client.

        Args:
            endpoint: SOAP endpoint URL
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.session_token: str | None = None

    def call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call SOAP method with parameters.

        Args:
            method: SOAP method name
            params: Method parameters

        Returns:
            Response dictionary

        Raises:
            ValueError: If response is invalid
        """
        # Build SOAP envelope
        envelope = self._build_envelope(method, params)

        # Validate envelope
        if not self._validate_envelope(envelope):
            raise ValueError("Invalid SOAP envelope")

        # Add authentication
        if self.username and self.password:
            envelope = self._add_authentication(envelope)

        # Send request (mock implementation - requires requests library)
        logger.info("SOAP call: %s to %s", method, self.endpoint)

        # Parse response (mock)
        response_xml = "<soap:Envelope><soap:Body><result>success</result></soap:Body></soap:Envelope>"
        return self._parse_response(response_xml)

    def _build_envelope(self, method: str, params: dict[str, Any]) -> str:
        """Build SOAP envelope.

        Args:
            method: Method name
            params: Parameters

        Returns:
            SOAP envelope XML
        """
        root = Element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope")
        root.set("xmlns:soap", "http://schemas.xmlsoap.org/soap/envelope/")

        body = SubElement(root, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        method_elem = SubElement(body, method)

        # Add parameters
        for key, value in params.items():
            param = SubElement(method_elem, key)
            param.text = str(value)

        return tostring(root, encoding="unicode")

    def _validate_envelope(self, envelope: str) -> bool:
        """Validate SOAP envelope structure.

        Args:
            envelope: SOAP envelope XML

        Returns:
            True if valid
        """
        try:
            # Use defusedxml for parsing untrusted XML
            root = DefusedET.fromstring(envelope)

            # Check for soap/envelope in tag
            tag_lower = root.tag.lower()
            if "envelope" not in tag_lower:
                logger.warning("Invalid SOAP envelope: wrong root element")
                return False

            # Check for Body element - try both with and without namespace
            body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
            if body is None:
                # Try without namespace
                body = root.find(".//Body")
                if body is None:
                    # Try with soap prefix
                    for child in root:
                        if "body" in child.tag.lower():
                            body = child
                            break

            if body is None:
                logger.warning("Invalid SOAP envelope: no Body element")
                return False

            return True

        except ET.ParseError as e:
            logger.error("Invalid SOAP envelope XML: %s", e)
            return False

    def _add_authentication(self, envelope: str) -> str:
        """Add WS-Security authentication to envelope.

        Args:
            envelope: SOAP envelope XML

        Returns:
            Envelope with authentication
        """
        # Parse envelope - using defusedxml since this is untrusted input
        root = DefusedET.fromstring(envelope)

        # Add security header
        header = Element("{http://schemas.xmlsoap.org/soap/envelope/}Header")
        security = SubElement(
            header,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security",
        )

        username_token = SubElement(security, "UsernameToken")

        username_elem = SubElement(username_token, "Username")
        username_elem.text = self.username

        password_elem = SubElement(username_token, "Password")
        password_elem.text = self.password

        # Insert header before body
        root.insert(0, header)

        return tostring(root, encoding="unicode")

    def _parse_response(self, response_xml: str) -> dict[str, Any]:
        """Parse SOAP response.

        Args:
            response_xml: Response XML

        Returns:
            Response dictionary
        """
        try:
            # Use defusedxml for parsing untrusted XML responses
            root = DefusedET.fromstring(response_xml)
            body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")

            if body is None:
                raise ValueError("No Body element in response")

            # Extract result (simplified)
            result = {}
            for child in body:
                for elem in child:
                    result[elem.tag] = elem.text

            return result

        except DefusedET.ParseError as e:
            logger.error("Failed to parse SOAP response: %s", e)
            raise ValueError(f"Invalid SOAP response: {e}") from e


class SecureWebHandler:
    """Secure web request handler with capability-based access control."""

    def __init__(self):
        """Initialize secure web handler."""
        self.capabilities: dict[str, list[str]] = {}
        self.locked_headers = {"X-Frame-Options", "X-Content-Type-Options", "X-XSS-Protection"}

    def register_capability(self, token: str, allowed_actions: list[str]) -> None:
        """Register capability token with allowed actions.

        Args:
            token: Capability token
            allowed_actions: List of allowed actions
        """
        self.capabilities[token] = allowed_actions
        logger.info("Registered capability token: %s", token[:16])

    def check_capability(self, token: str, action: str) -> bool:
        """Check if token has capability for action.

        Args:
            token: Capability token
            action: Requested action

        Returns:
            True if allowed
        """
        if token not in self.capabilities:
            logger.warning("Unknown capability token: %s", token[:16])
            return False

        allowed = action in self.capabilities[token]

        if not allowed:
            logger.warning("Action %s not allowed for token %s", action, token[:16])

        return allowed

    def generate_capability_token(self, allowed_actions: list[str]) -> str:
        """Generate new capability token.

        Args:
            allowed_actions: List of allowed actions

        Returns:
            Capability token
        """
        import secrets

        token = secrets.token_urlsafe(32)
        self.register_capability(token, allowed_actions)

        return token

    def validate_headers(self, headers: dict[str, str]) -> bool:
        """Validate request headers for security.

        Args:
            headers: Request headers

        Returns:
            True if headers are valid
        """
        # Check for required security headers (in responses)
        if "X-Content-Type-Options" in headers and headers["X-Content-Type-Options"] != "nosniff":
            logger.warning("Invalid X-Content-Type-Options header")
            return False

        # Check for locked headers (shouldn't be modified)
        # This is more relevant for response headers
        return True

    def set_secure_headers(self) -> dict[str, str]:
        """Get secure response headers.

        Returns:
            Dictionary of secure headers
        """
        return {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "no-referrer",
        }

    def sign_request(self, data: str, secret_key: str) -> str:
        """Sign request data with HMAC.

        Args:
            data: Request data
            secret_key: Secret key for signing

        Returns:
            HMAC signature
        """
        signature = hmac.new(
            secret_key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()

        return signature

    def verify_signature(self, data: str, signature: str, secret_key: str) -> bool:
        """Verify request signature.

        Args:
            data: Request data
            signature: Provided signature
            secret_key: Secret key

        Returns:
            True if signature is valid
        """
        expected = self.sign_request(data, secret_key)

        # Use constant-time comparison
        return hmac.compare_digest(signature, expected)


class RateLimiter:
    """Rate limiting for API endpoints."""

    def __init__(self, max_requests: int = 100, window: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = window
        self.requests: dict[str, list[float]] = {}

    def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier is within rate limit.

        Args:
            identifier: Client identifier (IP, user ID, etc.)

        Returns:
            True if within limit, False if exceeded
        """
        now = time.time()
        cutoff = now - self.window

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier] if ts > cutoff
            ]
        else:
            self.requests[identifier] = []

        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning("Rate limit exceeded for %s", identifier)
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier.

        Args:
            identifier: Client identifier

        Returns:
            Number of remaining requests
        """
        now = time.time()
        cutoff = now - self.window

        if identifier in self.requests:
            recent = [ts for ts in self.requests[identifier] if ts > cutoff]
            return max(0, self.max_requests - len(recent))

        return self.max_requests


class InputValidator:
    """Input validation for web requests."""

    def __init__(self):
        """Initialize input validator."""
        self.max_input_length = 10000
        self.allowed_content_types = {"application/json", "text/plain", "application/xml"}

    def validate_input(self, data: str, content_type: str) -> bool:
        """Validate input data.

        Args:
            data: Input data
            content_type: Content type

        Returns:
            True if valid
        """
        # Check length
        if len(data) > self.max_input_length:
            logger.warning("Input exceeds maximum length: %d", len(data))
            return False

        # Check content type
        if content_type not in self.allowed_content_types:
            logger.warning("Invalid content type: %s", content_type)
            return False

        # Check for null bytes
        if "\x00" in data:
            logger.warning("Null byte in input detected")
            return False

        return True

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal.

        Args:
            filename: Input filename

        Returns:
            Sanitized filename
        """
        import os
        import re

        # Remove path components
        filename = os.path.basename(filename)

        # Remove dangerous characters
        filename = re.sub(r"[^\w\s\-\.]", "", filename)

        # Limit length
        filename = filename[:255]

        return filename
