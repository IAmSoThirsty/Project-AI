"""
SovereignToolVault — storage-only vault enforcing execution/storage separation.

The vault holds tool binaries and returns their raw bytes on authenticated read.
It never executes, invokes, or launches tools.
"""

from __future__ import annotations

from pathlib import Path


class SovereignToolVault:
    """Authenticated read-only tool storage.  Never executes stored content."""

    def __init__(self, vault_path: str, usb_path: str) -> None:
        self.vault_path = Path(vault_path)
        self.usb_path = Path(usb_path)
        self.is_mounted: bool = False
        self._mount_point: Path | None = None

    def read_tool_to_buffer(self, tool_name: str) -> bytes:
        """Return raw bytes of *tool_name* from the mounted vault."""
        if not self.is_mounted:
            raise PermissionError("Vault is not mounted — authenticate first")
        mount = self._mount_point or self.vault_path
        tool_path = mount / tool_name
        if not tool_path.exists():
            raise ValueError(f"Tool not found in vault: {tool_name}")
        return tool_path.read_bytes()
