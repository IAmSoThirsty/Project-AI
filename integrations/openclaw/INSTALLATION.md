# OpenClaw Installation Guide

## Prerequisites

- Node.js 22.13.1 or higher
- npm 11.8.0 or higher

## Installation Steps

### 1. Open a NEW PowerShell Window

Close this terminal and open a fresh PowerShell (Admin mode) to ensure Node.js is in PATH.

### 2. Install OpenClaw CLI

```powershell
npm install -g @openclaw-ai/cli
```

### 3. Run Onboarding

```powershell
openclaw onboard --install-daemon
```

### 4. Onboarding Configuration

Follow these prompts:

| Prompt | Recommended Selection |
|--------|----------------------|
| Understanding of risks? | **Yes** |
| Onboarding mode | **Quick Start** |
| Model provider | **Skip for now** (we'll use Legion) |
| Channels (Telegram/Discord) | **No** (configure later) |
| Skills | **No** (configure later) |
| Hooks (logging/automation) | **All three** |
| Complete installation? | **Yes** |

### 5. Start OpenClaw Gateway

```powershell
openclaw install
openclaw gateway status
```

### 6. Configure Legion Integration

After installation completes, update the OpenClaw configuration:

**Location**: `~/.openclaw/config.json` (or similar)

**Add this configuration**:

```json
{
  "agent": {
    "type": "custom",
    "name": "Legion",
    "url": "http://localhost:8001/openclaw/message",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

### 7. Start Services

**Terminal 1** - Start Legion API:

```powershell
cd C:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI
python scripts/start_api.py
```

**Terminal 2** - Start OpenClaw:

```powershell
openclaw dashboard
```

### 8. Test Integration

Visit: `http://127.0.0.1:18789/`

Send a test message - it will flow through:

```
OpenClaw → Legion API (/openclaw/message) → Triumvirate → Response
```

## Troubleshooting

### If `openclaw` command not found

Refresh PATH in PowerShell:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Check Installation

```powershell
openclaw --version
openclaw gateway status
```

### View Logs

```powershell
openclaw logs
```
