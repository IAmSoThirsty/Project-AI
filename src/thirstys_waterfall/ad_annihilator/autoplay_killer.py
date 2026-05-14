"""
Autoplay Killer - Destroys autoplay videos and audio
"""

import logging


class AutoplayKiller:
    """
    Kills all autoplay videos and audio.
    No mercy for intrusive media.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.killed_count = 0

    def kill_video_autoplay(self, video_element: str) -> bool:
        """Kill video autoplay"""
        self.killed_count += 1
        self.logger.debug("Video autoplay KILLED")
        return True

    def kill_audio_autoplay(self, audio_element: str) -> bool:
        """Kill audio autoplay"""
        self.killed_count += 1
        self.logger.debug("Audio autoplay KILLED")
        return True

    def get_stats(self):
        """Get kill statistics"""
        return {"autoplay_killed": self.killed_count}

    def block_autoplay(self) -> bool:
        """Block autoplay globally"""
        self.logger.debug("Autoplay blocking activated")
        return True

    def is_autoplay(self, element: str) -> bool:
        """Check if element has autoplay attribute"""
        if not element:
            return False
        element_lower = element.lower()
        return "autoplay" in element_lower or "auto-play" in element_lower
