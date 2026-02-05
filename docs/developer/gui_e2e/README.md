# GUI E2E Automation Proposal

This document outlines a pragmatic approach to adding E2E GUI automation for the PyQt6-based Leather Book application.

Constraints:

- GUI automation for PyQt apps on CI requires either headless X server (Linux) or virtual display (Xvfb) on Ubuntu runners, or use of Windows runners with virtual desktop.
- Tests must not rely on heavy GPU resources; use software rendering options where possible.

Options:

1. Use `pytest-qt` for unit/integration with Qt event loop control. Best for widget-level tests.
1. Use `sikuli`/`pyautogui` or `guietta` for pixel-based flows (less robust, not recommended).
1. Use `pytest-qt` + `xvfb` on GitHub Actions for headless automation of common flows.

Recommended stack:

- `pytest-qt` (for Qt test fixtures and event loop control)
- `xvfb` on Linux GitHub Actions runners (via `Xvfb` service)
- `pytest` with `--maxfail=1` and `-q` for CI runs

Sample CI step snippet:

```yaml
- name: Run GUI E2E (Xvfb)
  run: |
    sudo apt-get update && sudo apt-get install -y xvfb
    export DISPLAY=:99
    Xvfb :99 -screen 0 1920x1080x24 &
    pytest tests/gui_e2e -q
```

Minimum test to start with:

- Launch the main window
- Verify login dialog appears
- Simulate login via test inputs
- Verify dashboard navigation occurs

Caveats:

- Avoid image generation or heavy ML models in E2E tests.
- Use mocked services for network or cloud dependencies.

This document proposes starting with `pytest-qt` and a small set of deterministic GUI tests. Implementation can be incremental: start with `tests/gui_e2e/test_launch_and_login.py` using `pytest-qt` fixtures.
