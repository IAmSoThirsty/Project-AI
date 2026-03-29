# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / timing.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / timing.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Timing middleware for request duration tracking.
"""

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

logger = structlog.get_logger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Track request processing time."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"

        # Log request
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time,
            request_id=getattr(request.state, "request_id", None),
        )

        return response
