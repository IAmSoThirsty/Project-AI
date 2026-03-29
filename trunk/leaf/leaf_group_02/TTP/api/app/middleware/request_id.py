# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / request_id.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / request_id.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Request ID middleware for request tracing.
"""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state
        request.state.request_id = request_id

        # Call next middleware/endpoint
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
