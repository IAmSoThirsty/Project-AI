# Stage 14.5 Desktop Acceptance

**Status:** ACCEPTED FOR DEVELOPMENT

## Required Evidence

- [x] Six read-only operator panels: status, replay, audit, capability, governance, settings.
- [x] API tokens remain in memory and are not persisted.
- [x] Capability claims are explicitly `UNVERIFIED` without issuer authority.
- [x] Capability token input is cleared immediately after inspection.
- [x] No direct governance, capability authority, Arbiter, RLP, or execution imports.
- [x] Ruff passes for the desktop application.
- [x] Strict MyPy passes for 48 workspace source files.
- [x] Desktop tests: `13 passed`; branch coverage: `91.98%`.
- [x] Full Python regression gate: `113 passed`.
- [x] Wheel and source distribution build at `0.0.0.dev0`.
- [x] PyQt6 offscreen source launch exits 0.
- [x] Unsigned `PyInstaller --onedir` development artifact builds.
- [x] Packaged offscreen executable launch exits 0.

## Development Artifact

- Path: `build/stage14_5/dist/Project-AI-Desktop` (ignored local output)
- Files: `187`
- Bytes: `97,170,241`
- Executable SHA-256: `943cc622f177c0a006c8db9bce519966b74c9beffc6d8155c8542ada7e3280a9`
- Signature/installer: none; this is an unsigned development artifact only

PyInstaller reported only expected conditional modules for non-Windows
platforms (`pwd`, `grp`, `posix`, `fcntl`, `termios`, and related imports).
The packaged Windows application launched successfully without those modules.
