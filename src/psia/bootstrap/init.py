"""
PSIA bootstrap — initialise the pipeline and verify all 7 stages are operational.

Run this at service startup to confirm the pipeline is healthy before
accepting production traffic.
"""

from __future__ import annotations

import logging

log = logging.getLogger("psia.bootstrap")


def bootstrap_pipeline(triumvirate_url: str = "http://localhost:8001") -> dict:
    """
    Initialise the PSIA pipeline and run a self-test through all 7 stages.

    Returns a health report dict:
        {
          "healthy": bool,
          "stages_operational": int,    # 0–7
          "anchor_available": bool,     # Ed25519 key loaded
          "chain_valid": bool,          # canonical log hash chain intact
          "errors": list[str],
        }
    """
    from ..core import Pipeline

    errors: list[str] = []
    anchor_available = False
    chain_valid = False
    stages_operational = 0

    try:
        pipeline = Pipeline(triumvirate_url=triumvirate_url)
        anchor_available = pipeline._anchor.available
        chain_valid = pipeline._canon_log.verify_chain()

        # Smoke test with a benign read intent
        result = pipeline.run({
            "actor": "system",
            "action": "read",
            "target": "psia.bootstrap.healthcheck",
            "context": {"bootstrap": True},
            "origin": "internal",
        })
        stages_operational = len([s for s in result.trace.stages if s.passed])
        if not result.passed:
            errors.append(f"bootstrap smoke test failed: {result.error}")

    except Exception as exc:
        errors.append(f"pipeline init failed: {exc}")

    healthy = len(errors) == 0 and stages_operational == 7
    report = {
        "healthy": healthy,
        "stages_operational": stages_operational,
        "anchor_available": anchor_available,
        "chain_valid": chain_valid,
        "errors": errors,
    }

    if healthy:
        log.info("PSIA bootstrap: all 7 stages operational")
    else:
        log.warning("PSIA bootstrap: health check failed — %s", errors)

    return report
