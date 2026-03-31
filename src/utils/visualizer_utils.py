# [2026-03-05 17:55] | Productivity: Active
import logging

logger = logging.getLogger(__name__)


class VisualizerUtils:
    """
    Sovereign diagnostic visualizer.
    Provides non-critical visual feedback for system states.
    """

    HTTP_CAT_BASE = "https://http.cat/"

    @staticmethod
    def get_error_visual(status_code: int) -> str:
        """
        Returns a URL to a status-appropriate diagnostic visual.
        Modeled after the 'HttpCat' pattern for playful but informative diagnostics.
        """
        # Only activated in 'Chaos' or 'Debug' profiles
        return f"{VisualizerUtils.HTTP_CAT_BASE}{status_code}.jpg"

    @staticmethod
    def log_visual_diagnostic(status_code: int, message: str):
        """Logs a message with a companion visual diagnostic link."""
        visual_url = VisualizerUtils.get_error_visual(status_code)
        logger.info(f"DIAGNOSTIC [{status_code}]: {message} | Visual: {visual_url}")
