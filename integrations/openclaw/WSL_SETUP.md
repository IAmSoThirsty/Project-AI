# WSL + OpenClaw + Legion Setup Guide

## Part 1: WSL Installation (In Progress)

**Status:** Installing WSL with Ubuntu...

WSL is being installed in the background. This will take a few minutes.

After installation completes, you'll need to:

1. **Restart your computer**
2. **Open Ubuntu** from the Start menu
3. **Create a username and password** when prompted

## Part 2: Install OpenClaw in WSL

Once WSL is running, open the Ubuntu terminal and run:

```bash

# Update package manager

sudo apt update

# Install OpenClaw

curl -fsSL https://openclaw.ai/install.sh | bash
```

Follow the onboarding prompts:

- **Onboarding mode**: Quick Start
- **Model provider**: Skip for now
- **Channels**: No
- **Skills**: No
- **Hooks**: All three recommended

## Part 3: Configure OpenClaw to Use Legion

After OpenClaw installation, configure it to connect to your Windows Legion API:

### Find WSL IP Address

```bash

# In WSL terminal

ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1
```

### Configure OpenClaw

Edit OpenClaw config (location will be shown during installation):

```json
{
  "agent": {
    "type": "custom",
    "name": "Legion",
    "url": "http://<WINDOWS_IP>:8001/openclaw/message"
  }
}
```

Replace `<WINDOWS_IP>` with your Windows machine IP (usually `172.x.x.1` in WSL).

## Part 4: Test Legion API (Standalone)

While WSL is installing, test the Legion API independently:

### Start Legion API (Windows PowerShell)

```powershell
cd C:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI
python scripts/start_api.py
```

### Run Test Suite (New PowerShell Window)

```powershell
cd C:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI
python integrations/openclaw/test_standalone_api.py
```

This will test all OpenClaw endpoints:

- Health check
- Capabilities list
- Message processing
- Status metrics

## Part 5: Connect Everything

Once both WSL and Legion API are running:

**Terminal 1 (Windows)**: Legion API

```powershell
python scripts/start_api.py
```

**Terminal 2 (WSL/Ubuntu)**: OpenClaw

```bash
openclaw gateway status
openclaw dashboard
```

**Browser**: Open `http://127.0.0.1:18789/`

Messages will flow: **OpenClaw (WSL) → Legion API (Windows) → Triumvirate → Response**

## Troubleshooting

### WSL Can't Reach Windows

Find your Windows IP from WSL:

```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

### Legion API Not Accessible

Allow firewall access:

```powershell
New-NetFirewallRule -DisplayName "Legion API" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

### Check OpenClaw Logs

```bash
openclaw logs
```
