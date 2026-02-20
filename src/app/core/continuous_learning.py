"""Continuous learning engine that tracks incoming facts and generates structured reports."""

from __future__ import annotations

import datetime
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LearningReport:
    """A structured report generated after absorbing new knowledge."""

    topic: str
    timestamp: str
    facts: list[str]
    usage_ideas: list[str]
    neutral_summary: str
    pros_cons: dict[str, list[str]]
    metadata: dict[str, Any]


class ContinuousLearningEngine:
    """Engine responsible for continuously absorbing new information."""

    DATA_FILE = "reports.json"

    def __init__(self, data_dir: str = "data") -> None:
        """Initialize storage and load previous insights."""
        self.data_dir = data_dir
        self.engine_dir = os.path.join(data_dir, "continuous_learning")
        os.makedirs(self.engine_dir, exist_ok=True)
        self._storage_file = os.path.join(self.engine_dir, self.DATA_FILE)
        self.reports: list[LearningReport] = []
        self._load_reports()

    def absorb_information(
        self,
        topic: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> LearningReport:
        """Absorb text and emit a detailed report."""
        metadata = metadata or {}
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        facts = self._extract_facts(content)
        usage = self._generate_usage(topic, content)
        pros_cons = self._evaluate_pros_cons(content)
        neutral = self._compose_neutral(topic, facts, pros_cons)

        report = LearningReport(
            topic=topic,
            timestamp=timestamp,
            facts=facts,
            usage_ideas=usage,
            neutral_summary=neutral,
            pros_cons=pros_cons,
            metadata=metadata,
        )
        self.reports.append(report)
        self._save_reports()
        return report

    def _load_reports(self) -> None:
        """Load past reports from disk."""
        if not os.path.exists(self._storage_file):
            return
        try:
            with open(self._storage_file, encoding="utf-8") as handle:
                data = json.load(handle)
                for entry in data:
                    self.reports.append(LearningReport(**entry))
        except Exception as error:  # pragma: no cover - defensive
            logger.error("Failed to load continuous learning reports: %s", error)

    def _save_reports(self) -> None:
        """Serialize reports to disk."""
        try:
            with open(self._storage_file, "w", encoding="utf-8") as handle:
                json.dump([asdict(report) for report in self.reports], handle, indent=2)
        except Exception as error:  # pragma: no cover - defensive
            logger.error("Failed to save continuous learning reports: %s", error)

    def _extract_facts(self, content: str) -> list[str]:
        """Find up to three meaningful facts in the text."""
        candidates = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content) if len(s.strip()) >= 20]
        if not candidates:
            return [content.strip()]
        return candidates[:3]

    def _generate_usage(self, topic: str, content: str) -> list[str]:
        """Suggest how the new knowledge might be put to work."""
        ideas = [
            f"Brief the team on {topic} with the verified facts so they stay aligned.",
            f"Create a small experiment around {topic} that tests one of the recorded facts.",
        ]
        if "application" in content.lower():
            ideas.append(f"Leverage the application-focused details to improve how {topic} connects to daily practice.")
        return ideas

    def _evaluate_pros_cons(self, content: str) -> dict[str, list[str]]:
        """Detect whether the content outlines a controversy and mirror both perspectives."""
        normalized = content.lower()
        controversy_markers = [
            "controversy",
            "debate",
            "pro",
            "con",
            "opposition",
            "split",
        ]
        pros_cons = {"pros": [], "cons": []}
        if any(marker in normalized for marker in controversy_markers):
            pros_cons["pros"].append("Summarizes the benefits or arguments that advocates are promoting.")
            pros_cons["cons"].append("Remembers the counterpoints that keep the debate grounded and neutral.")
        return pros_cons

    def _compose_neutral(self, topic: str, facts: list[str], pros_cons: dict[str, list[str]]) -> str:
        """Compose a neutral perspective that accompanies the recorded facts."""
        base = f"Continuous learning update for {topic}: {len(facts)} fact(s) recorded."
        if pros_cons.get("pros") or pros_cons.get("cons"):
            base += " Neutral perspective weighs the pros and cons before suggesting action."
        else:
            base += " The perspective remains centered on the documented facts."
        return base
