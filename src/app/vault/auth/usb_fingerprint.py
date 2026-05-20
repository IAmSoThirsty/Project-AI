"""
USB device fingerprinting for clone-resistance checks.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class USBDeviceFingerprint:
    """Generates and verifies a content-addressable fingerprint of a USB path."""

    def __init__(self, usb_path: str) -> None:
        self.usb_path = Path(usb_path)

    def generate(self) -> dict[str, object]:
        path_str = str(self.usb_path.resolve()) if self.usb_path.exists() else str(self.usb_path)
        return {
            "path": path_str,
            "path_hash": hashlib.sha256(path_str.encode()).hexdigest(),
            "exists": self.usb_path.exists(),
        }

    def verify(self, fingerprint: dict[str, object]) -> bool:
        expected = self.generate()
        return fingerprint.get("path_hash") == expected.get("path_hash")
