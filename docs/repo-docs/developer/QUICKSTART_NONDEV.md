---
type: quickstart
tags: [p1-developer, non-developer-guide, beginner-friendly, desktop-app, end-user, simple-setup]
created: 2026-04-20
last_verified: 2026-04-20
status: current
related_systems: [desktop-app, setup-scripts, python-installation, windows-installation]
stakeholders: [non-developers, end-users, new-users]
audience: beginner
prerequisites: [windows-10-11-or-macos, python-3.12]
estimated_time: 10 minutes
review_cycle: monthly
---
# Quick Start (Non-developer)

This guide helps non-technical users get started with Project-AI (Desktop) quickly.

Prerequisites:

- Windows 10/11 or recent macOS
- Python 3.12 installed (use Microsoft Store or official installer)

Steps:

1. Download the repository ZIP or clone it using GitHub Desktop.
1. Double-click `launch-desktop.bat` (Windows) or run `python -m src.app.main` (macOS if Python installed)
1. On first run, create an admin account when prompted.
1. Configure preferences via the Persona panel.
1. To update the app, download the latest ZIP or use the provided update mechanism in the app.

If anything goes wrong:

- Check `logs/` for `app.log` and share with the maintainer.
- For privacy, all data is stored locally under `data/`.

Support:

- Create an issue on GitHub with `bug` label and include `logs/app.log` and `data/` export if comfortable.
