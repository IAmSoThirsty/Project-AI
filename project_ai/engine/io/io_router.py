"""
IO Router
=========

Handles IO channels and routes input/output to and from PACE.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import PACEEngine


class IORouter:
    """
    Handles IO channels and routes input/output to and from PACE.
    """

    def __init__(self, engine: "PACEEngine"):
        self.engine = engine

    def receive_input(self, channel: str, payload: dict) -> dict:
        """
        Receive input from a channel and route to engine.

        Args:
            channel: Channel identifier (cli, api, gui, h323, etc.)
            payload: Input payload

        Returns:
            Response from engine
        """
        return self.engine.handle_input(channel, payload)

    def send_output(self, channel: str, data: dict) -> None:
        """
        Send output to a channel.

        Args:
            channel: Destination channel
            data: Output data
        """
        # Placeholder: integrate with H.323, APIs, etc.
        print(f"[IO:{channel}] {data}")


__all__ = ["IORouter"]
