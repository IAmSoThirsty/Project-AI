"""Knowledge Curator agent

Conservatively deduplicates, annotates and tags continuous learning reports.
Provides a small API used by CouncilHub and other agents.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class KnowledgeCurator(KernelRoutedAgent):
    def __init__(self, data_dir: str = "data", kernel: CognitionKernel | None = None) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.data_dir = data_dir
        self.curated_path = os.path.join(self.data_dir, "continuous_learning", "curated.json")
        os.makedirs(os.path.dirname(self.curated_path), exist_ok=True)
        self.curated: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.curated_path):
            try:
                with open(self.curated_path, encoding="utf-8") as f:
                    self.curated = json.load(f)
            except Exception:
                logger.exception("Failed to load curated knowledge")

    def _save(self) -> None:
        try:
            with open(self.curated_path, "w", encoding="utf-8") as f:
                json.dump(self.curated, f, indent=2)
        except Exception:
            logger.exception("Failed to save curated knowledge")

    def curate(self, reports: list[dict[str, Any]]) -> dict[str, Any]:
        """Curate incoming reports: dedupe and annotate.

        Returns a summary of actions taken.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_curate,
            reports,
            operation_name="curate_reports",
            risk_level="low",
            metadata={"report_count": len(reports)},
        )

    def _do_curate(self, reports: list[dict[str, Any]]) -> dict[str, Any]:
        """Internal implementation of report curation."""
        added = 0
        for r in reports:
            content = json.dumps(r, sort_keys=True)
            h = hashlib.sha256(content.encode()).hexdigest()
            if any(entry.get("fingerprint") == h for entry in self.curated):
                continue
            entry = {
                "fingerprint": h,
                "topic": r.get("topic"),
                "summary": r.get("neutral_summary"),
                "raw": r,
            }
            self.curated.append(entry)
            added += 1
        if added:
            self._save()
        return {"added": added, "total": len(self.curated)}

    def get_topics(self) -> list[str]:
        return list({c.get("topic") for c in self.curated if c.get("topic")})

    def receive_message(self, from_id: str, message: str) -> None:
        logger.info("KnowledgeCurator received message from %s", from_id)
