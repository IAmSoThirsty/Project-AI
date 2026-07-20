"""Bounded Prometheus metrics for the Project-AI API gateway."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import FastAPI, Request, Response
from kernel.version import PROJECT_AI_VERSION
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

HTTP_REQUESTS = Counter(
    "project_ai_http_requests",
    "Project-AI API HTTP requests.",
    ("method", "route", "status_code"),
)
HTTP_DURATION = Histogram(
    "project_ai_http_request_duration_seconds",
    "Project-AI API request duration in seconds.",
    ("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
BUILD_INFO = Gauge(
    "project_ai_build_info",
    "Immutable Project-AI release metadata.",
    ("version",),
)
BUILD_INFO.labels(version=PROJECT_AI_VERSION).set(1)


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else "unmatched"


def install_metrics(application: FastAPI) -> None:
    """Install a public scrape endpoint and low-cardinality HTTP instrumentation."""

    @application.middleware("http")
    async def observe_http(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            route = _route_path(request)
            HTTP_REQUESTS.labels(
                method=request.method,
                route=route,
                status_code=str(status_code),
            ).inc()
            HTTP_DURATION.labels(method=request.method, route=route).observe(
                perf_counter() - started
            )

    @application.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=generate_latest(),
            headers={"Content-Type": CONTENT_TYPE_LATEST},
        )
