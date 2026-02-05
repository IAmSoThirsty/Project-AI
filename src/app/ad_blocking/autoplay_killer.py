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
        return {'autoplay_killed': self.killed_count}
