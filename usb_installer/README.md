<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `usb_installer/` — USB Deployment

> **Scripts and assets for creating bootable/portable USB installations of Project-AI.**

## Contents

| File | Purpose |
|---|---|
| `autorun_launcher.sh` | Auto-run launcher script for USB boot |

## USB Creation Scripts

Located in `scripts/`:

- `create_installation_usb.ps1` — Full installation USB
- `create_portable_usb.ps1` — Portable (no-install) USB
- `create_universal_usb.ps1` — Universal USB (multi-platform)

## Usage

```powershell
# Create a portable USB on drive E:
powershell scripts/create_portable_usb.ps1 -Drive E:
```

See `docs/PORTABLE_APP_GUIDE.md` for detailed instructions.
