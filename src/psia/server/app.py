"""
PSIA HTTP gateway — exposes the 7-stage pipeline as a REST API.

Endpoints:
  POST /run     — run a raw intent dict through all 7 stages
  GET  /health  — bootstrap health check
  GET  /chain   — canonical log chain validity + length

Port: 8002 (distinct from Triumvirate at 8001)

Start with:
    uvicorn psia.server.app:app --host 0.0.0.0 --port 8002
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    class IntentPayload(BaseModel):
        actor: str
        action: str
        target: str
        context: dict[str, Any] = {}
        origin: str = "unknown"

    def create_app(triumvirate_url: str = "http://localhost:8001") -> "FastAPI":
        from ..core import Pipeline
        from ..bootstrap.init import bootstrap_pipeline

        pipeline = Pipeline(triumvirate_url=triumvirate_url)

        app = FastAPI(
            title="PSIA Gateway",
            description="7-stage Plane Separation / Isolation Architecture pipeline",
            version="1.0.0",
        )
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.post("/run")
        async def run_pipeline(intent: IntentPayload):
            result = pipeline.run(intent.dict())
            return result.summary()

        @app.get("/health")
        async def health():
            return bootstrap_pipeline(triumvirate_url=triumvirate_url)

        @app.get("/chain")
        async def chain_status():
            valid = pipeline._canon_log.verify_chain()
            length = len(pipeline._canon_log)
            return {"chain_valid": valid, "entries": length}

        return app

    # Module-level app instance for uvicorn
    app = create_app()

except ImportError:
    # FastAPI not installed — provide a stub that explains the situation
    def create_app(**_):
        raise ImportError(
            "FastAPI is required to run the PSIA HTTP gateway. "
            "Install with: pip install fastapi uvicorn"
        )
    app = None  # type: ignore
