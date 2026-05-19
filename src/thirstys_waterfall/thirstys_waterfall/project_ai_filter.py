"""Project-AI inbound filter adapter for Thirstys Waterfall.

This module is intentionally side-effect light. The full Waterfall orchestrator
starts VPN, storage, browser, and firewall subsystems; Project-AI only needs an
edge verdict before requests enter the invariant engine. The adapter therefore
uses Waterfall's URL/content security primitives directly and returns the
duck-typed contract expected by ``app.core.waterfall_filter``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .browser.content_blocker import ContentBlocker
from .privacy.anti_phishing import AntiPhishingEngine

logger = logging.getLogger(__name__)


@dataclass
class ProjectAIWaterfallResult:
    allowed: bool
    context: dict[str, Any]
    reason: str | None = None


class ProjectAIWaterfallAdapter:
    """Reusable Waterfall policy adapter for Project-AI request contexts."""

    def __init__(self) -> None:
        self._content_blocker = ContentBlocker(
            block_trackers=True,
            block_popups=True,
            block_redirects=True,
            block_ads=True,
        )
        self._anti_phishing = AntiPhishingEngine({"anti_phishing": True})
        self._content_blocker.start()
        self._anti_phishing.start()

    def filter(self, context: dict[str, Any]) -> ProjectAIWaterfallResult:
        checked_context = dict(context)
        url = self._extract_first(
            checked_context,
            "url",
            "uri",
            "target_url",
            "href",
            "endpoint",
        )
        content = self._extract_first(
            checked_context,
            "content",
            "body",
            "html",
            "payload_text",
            default="",
        )

        if url and self._content_blocker.should_block(str(url)):
            return self._deny(checked_context, "waterfall-content-blocker")

        if url and self._anti_phishing.is_phishing(str(url), str(content or "")):
            return self._deny(checked_context, "waterfall-anti-phishing")

        if content and not self._content_blocker.should_allow_content(
            str(content),
            str(checked_context.get("content_type", "text/plain")),
        ):
            return self._deny(checked_context, "waterfall-content-policy")

        checked_context["waterfall"] = {
            "engine": "thirstys_waterfall",
            "allowed": True,
            "content_blocker": self._content_blocker.get_statistics(),
            "anti_phishing": self._anti_phishing.get_statistics(),
        }
        return ProjectAIWaterfallResult(allowed=True, context=checked_context)

    @staticmethod
    def _extract_first(
        context: dict[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        for key in keys:
            value = context.get(key)
            if value:
                return value

        payload = context.get("payload")
        if isinstance(payload, dict):
            for key in keys:
                value = payload.get(key)
                if value:
                    return value

        request = context.get("request")
        if isinstance(request, dict):
            for key in keys:
                value = request.get(key)
                if value:
                    return value

        return default

    @staticmethod
    def _deny(context: dict[str, Any], reason: str) -> ProjectAIWaterfallResult:
        logger.warning("Thirstys Waterfall denied inbound context: %s", reason)
        context["waterfall"] = {
            "engine": "thirstys_waterfall",
            "allowed": False,
            "reason": reason,
        }
        return ProjectAIWaterfallResult(
            allowed=False,
            context=context,
            reason=reason,
        )


_adapter = ProjectAIWaterfallAdapter()


def filter(context: dict[str, Any]) -> ProjectAIWaterfallResult:
    """Filter a Project-AI inbound context through Thirstys Waterfall."""
    return _adapter.filter(context)


__all__ = ["ProjectAIWaterfallAdapter", "ProjectAIWaterfallResult", "filter"]
