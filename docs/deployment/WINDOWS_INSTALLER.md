# Windows Installer

A standalone Windows installer for `apps/desktop`, distributed as a single bootstrapper
executable (`Project-AI-Desktop-Setup.exe`) that a user can download and run without cloning
the repo or running any other Project-AI service first.

## Status

- **Unsigned.** No code-signing certificate is configured anywhere in this repo. Windows
  SmartScreen will flag the installer and the two executables it contains as unrecognized.
  See [Signing](#signing) below for what happens once a certificate is configured, and for
  why this is a deliberate, disclosed state rather than an oversight.
- **Auto-update: out of scope.** Installing a new version means downloading and running a
  new installer; there is no in-app update check.
- **No EULA dialog, no first-run wizard, no license-acceptance UI.** Deliberately not built —
  none of the confirmed requirements for this work asked for it.

## What gets installed

The bootstrapper chains two MSI packages under a single Add/Remove Programs entry
("Project-AI Desktop"):

- `Desktop.msi` → `%ProgramFiles%\Project-AI\Desktop\Project-AI-Desktop.exe` (or a caller-supplied
  install path — see [Installing to a custom path](#installing-to-a-custom-path))
- `Api.msi` → `%ProgramFiles%\Project-AI\Api\project-ai-api-server.exe`

Both MSIs set `ARPSYSTEMCOMPONENT=1` on themselves and the bootstrapper's `MsiPackage`
elements set `Visible="no"`, so only the bundle shows in Programs & Features — verified
empirically by `tools/smoke_windows_installer.ps1`, which checks the `SystemComponent`
registry value on each product key after a real install rather than trusting the WiX
schema's stated defaults alone.

## How the bundled backend works

The desktop app (`apps/desktop`) talks to the `packages/api` FastAPI gateway over HTTP, same
as always. What changes when installed:

1. On startup, `api_supervisor.py` health-probes `http://127.0.0.1:8000/health/live`. If
   something is already answering there (e.g. a developer's `docker compose up api`), the app
   uses it and never spawns anything.
2. If nothing answers, and only when running from the frozen/installed build (never from
   `uv run` source or CI's offscreen smoke job), it launches the sibling
   `..\Api\project-ai-api-server.exe` as a child process.
3. That child process (`packages/api/src/project_ai_api/server.py`) binds its own listening
   socket on an OS-assigned port and writes the resolved port to a `--port-file` before it
   starts serving — the only process that ever binds the socket is the one that reports the
   port, so there is no window for a second process to race for the same port. The supervisor
   waits on that file rather than pre-selecting a port.
4. A per-user loopback token is generated once and persisted under
   `%LOCALAPPDATA%\Project-AI-Desktop\config\local-api.token`, then passed to the child via
   `PROJECT_AI_API_TOKEN`. The gateway's `require_auth` dependency
   (`packages/api/src/project_ai_api/app.py`) does a real constant-time comparison against
   this token for every protected route — this is an enforced credential, not decoration.
5. The audit evidence file lives at
   `%LOCALAPPDATA%\Project-AI-Desktop\data\chimera-audit.jsonl` and is **not** deleted on
   uninstall (uninstall only removes the Program Files install root).
6. When the desktop app quits, it terminates only the process it spawned itself — never a
   pre-existing gateway it found already running.

Known limitation: the reuse-or-spawn decision is a single health probe at startup with no
re-check. Two near-simultaneous launches of the desktop app could each fail to see the other's
not-yet-ready spawn and both start their own api child process (each on its own OS-assigned
port, so they won't collide with each other, but two would briefly run). Accepted for this
phase — this is a single-user desktop tool.

## Installing to a custom path

The bundle exposes an overridable `InstallFolder` variable, forwarded into both MSIs'
`INSTALLFOLDER`/`APIINSTALLFOLDER` properties:

```
Project-AI-Desktop-Setup.exe /quiet InstallFolder="D:\Custom\Path"
```

`tools/smoke_windows_installer.ps1` asserts this forwarding actually works (files exist under
the requested path after a silent install) rather than trusting that the property was
authored correctly.

## Silent install / uninstall

```
Project-AI-Desktop-Setup.exe /quiet /log install.log
Project-AI-Desktop-Setup.exe /quiet /uninstall /log uninstall.log
```

## System requirements

- Windows 10 or later, x64.
- The Qt6 DLLs shipped by the `PyQt6` wheel are self-contained in the PyInstaller onedir
  output; no separate Qt install is required. Whether a system-wide Visual C++ runtime is
  additionally required has not been verified against a machine that never had one installed —
  treat this as **Not verified** rather than assuming it works everywhere.

## Signing

`tools/sign_windows_artifact.ps1` reads `CODESIGN_CERT_PATH` / `CODESIGN_CERT_PASSWORD` from
the environment. If unset (true today, everywhere), every call is a no-op that prints
`"unsigned: no signing certificate configured"` and exits 0 — the build does not fail, it
produces an honestly-unsigned artifact. Once a certificate is configured, `signtool` runs
against, in order: both onedir executables (before MSI packaging), both MSI packages, and
finally the Burn bootstrapper.

## WiX Toolset licensing (Open Source Maintenance Fee)

The installer is built with WiX Toolset v7 (`dotnet tool install --global wix`). Its source
remains free under its own LICENSE, but per the current terms at
<https://docs.firegiant.com/wix/osmf/>: organizations generating more than $10,000 in annual
revenue are required to sponsor the `wixtoolset` GitHub organization to satisfy the Open
Source Maintenance Fee (introduced in WiX v6; CLI-level EULA acceptance enforcement added in
v7). Accepting the EULA (`-acceptEula wix7` / `wix eula accept wix7`) is free and does not by
itself verify or require payment — it is a separate, honor-system compliance obligation tied
to revenue.

Project-AI is pre-alpha (`0.0.0.dev0`) with no revenue, so the free-use terms apply today.
**If this project starts generating revenue, re-check the threshold at the URL above before
continuing to build with WiX.**

## Where the source lives

- `installer/windows/Desktop.wxs`, `Api.wxs`, `Bundle.wxs` — WiX sources.
- `tools/build_windows_installer.ps1` — builds both PyInstaller onedir bundles, both MSIs, and
  the Burn bootstrapper, signing each artifact (no-op today) as it's produced.
- `tools/sign_windows_artifact.ps1` — the shared, no-op-safe signing helper.
- `tools/smoke_windows_installer.ps1` — silent install → verify → silent uninstall → verify,
  shared by `tools/acceptance_gate.ps1`'s `Build-And-Smoke-Installer` step and the
  `windows-installer` CI job so the two paths cannot drift.
- `packages/api/src/project_ai_api/server.py` — the frozen-friendly standalone api entrypoint.
- `apps/desktop/src/project_ai_desktop/api_supervisor.py`, `credentials.py`, `local_paths.py`
  — the desktop-side process supervisor and per-user state.
