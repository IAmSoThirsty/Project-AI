# Thirstys Waterfall Integration

Thirstys Waterfall is vendored into Project-AI at `src/thirstys_waterfall`.
It is available in two modes:

1. Edge filtering through `app.core.waterfall_filter`.
2. Full active privacy/security orchestration through `thirstys_waterfall`.

The edge filter is side-effect-light and loads by default through:

```text
WATERFALL_MODULE=thirstys_waterfall.project_ai_filter
```

It uses Waterfall content blocking and anti-phishing primitives before requests
enter Project-AI governance.

## Active Controls

Full Waterfall startup can activate host/network controls such as firewall, VPN,
browser, storage, and kill-switch subsystems. These controls are real and are
intended for owned systems and authorized penetration testing.

To start full active controls, use one of:

```powershell
$env:THIRSTYS_WATERFALL_ENABLE_ACTIVE_CONTROLS = "1"
thirstys-waterfall --start
```

or:

```powershell
thirstys-waterfall --enable-active-controls --start
```

or set this in a Waterfall config file:

```json
{
  "project_ai": {
    "allow_active_controls": true
  }
}
```

## Destructive Responses

DOS Trap response paths can wipe in-memory secret stores, sanitize files, or shut
down a host when explicitly configured. These responses are separate from normal
active controls and require a second activation:

```powershell
$env:THIRSTYS_WATERFALL_ENABLE_DESTRUCTIVE_RESPONSES = "1"
```

or:

```powershell
thirstys-waterfall --enable-active-controls --enable-destructive-responses --start
```

or:

```json
{
  "project_ai": {
    "allow_active_controls": true,
    "allow_destructive_responses": true
  }
}
```

This keeps Cerberus and authorized security tests real while preventing accidental
host mutation from imports, unit tests, or status commands.
