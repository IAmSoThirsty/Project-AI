# Project-AI Desktop

PyQt6 operator application for gateway status, canonical replay evidence
checks, verified audit viewing, unverified capability claim inspection,
governance display, and in-memory settings.

The desktop application does not import governance or execution packages.
Capability inspection decodes public claims but cannot authenticate
signatures without issuer authority, and labels that limit in the UI.

The native controls expose assistive-technology names and descriptions for
navigation, status messages, read-only evidence tables, capability inspection,
and connection settings. Keyboard focus follows Qt's native tab and list
navigation behavior. Automated tests verify that metadata without placing token
values in the accessibility tree. The minimum 900 by 620 window has been visually
checked on Windows. Manual NVDA acceptance remains required before release.

## Bundled local api gateway

When installed via the Windows installer (see
[`docs/deployment/WINDOWS_INSTALLER.md`](../../docs/deployment/WINDOWS_INSTALLER.md)),
the app is standalone: on startup it checks whether a gateway is already
reachable at `http://127.0.0.1:8000/health/live`; if not, and only when
running from a frozen/installed build, it spawns the bundled
`project-ai-api-server` process as a child, generates a per-user loopback
token (`credentials.py`), and points the UI at whatever port that process
reports (see `api_supervisor.py`). It never spawns anything when a gateway is
already reachable, and it never spawns anything when running from source
(`uv run`) or in CI's offscreen smoke job.

This is the one credential the desktop persists to disk, under
`%LOCALAPPDATA%\Project-AI-Desktop\config\`. It is distinct from, and does not
affect, the Settings page's user-entered remote gateway token, which remains
in-memory only and is never written anywhere (see
`test_local_loopback_token_is_the_only_persisted_secret` in
`tests/test_desktop.py`).

Signing status: the installer is currently **unsigned** — no code-signing
certificate is configured in this repo. See
[`docs/deployment/WINDOWS_INSTALLER.md`](../../docs/deployment/WINDOWS_INSTALLER.md).
