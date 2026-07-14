"""Loopback-only credential for the desktop-spawned local api process.

This is architecturally distinct from the Settings page's user-entered remote
gateway token (``main_window.py``'s ``api_token_input``), which stays
in-memory only and is never written to disk. This module persists a
*different* secret: one the desktop app generates itself, never displays,
and uses solely to authenticate to a child process it spawned on
``127.0.0.1``. It is protected only by the OS-default per-user ACLs on
``%LOCALAPPDATA%`` — proportionate for a loopback-only secret, not a
substitute for real access control.
"""

from __future__ import annotations

import secrets

from project_ai_desktop.local_paths import LocalPaths

TOKEN_FILE_NAME = "local-api.token"
_TOKEN_BYTES = 32


def load_or_create_token(paths: LocalPaths) -> str:
    """Return the persisted local-api token, generating one if absent or unreadable."""
    paths.ensure()
    token_path = paths.config_dir / TOKEN_FILE_NAME
    try:
        existing = token_path.read_text(encoding="utf-8").strip()
    except OSError:
        existing = ""
    if existing:
        return existing
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    token_path.write_text(token, encoding="utf-8")
    return token
