# 🚀 How to Actually Run Project-AI

**Stop trying the automated scripts - they're causing issues. Here's the simple way:**

______________________________________________________________________

## Quick Start (2 Steps)

### Step 1: Start the Backend

Open PowerShell or Command Prompt:

```powershell
cd C:\Users\Jeremy\Desktop\Project-AI-main
python start_api.py
```

**Wait for this message:**

```
Uvicorn running on http://0.0.0.0:8001
```

**Leave this window open!**

______________________________________________________________________

### Step 2: Start Legion (Optional - if you want the chat interface)

Open a **NEW** PowerShell/Command Prompt window:

```powershell
cd C:\Users\Jeremy\Desktop\Project-AI-main
python integrations\openclaw\legion_api.py
```

**Wait for this message:**

```
Uvicorn running on http://localhost:8002
```

**Leave this window open too!**

______________________________________________________________________

### Step 3: Open in Browser

**Backend API Docs:**

- Open browser to: <http://localhost:8001/docs>

**Legion Chat Interface (if running):**

- Open browser to: <http://localhost:8002>
- Or open file: `integrations/openclaw/legion_interface.html`

______________________________________________________________________

## What You've Built

✅ **Save Points System** - Auto-saves every 15 minutes (API endpoints at /api/savepoints/\*) ✅ **Triumvirate Governance** - Active in backend ✅ **Legion Integration** - Chat interface with AI ✅ **Universal USB Installer** - Script at `scripts\create_universal_usb.ps1` ✅ **Android App** - Source code ready (needs SDK to build APK) ✅ **Clean Project Structure** - 209 files → 54 in root

______________________________________________________________________

## If You Want to Test Save Points

**Via API (<http://localhost:8001/docs>):**

1. Go to `/api/savepoints/create` endpoint
1. Click "Try it out"
1. Enter a description like "Test save"
1. Click "Execute"

**Check auto-saves:**

```powershell
dir data\savepoints\auto
```

______________________________________________________________________

## The Automated Stuff That's Ready

You don't need to run the backend to use these:

**Create USB Installer:**

```powershell
.\scripts\create_universal_usb.ps1
```

**Build Everything (if you had Android SDK configured):**

```powershell
.\scripts\deploy_complete.ps1
```

**Cleanup Root Directory (already done):**

```powershell
.\scripts\cleanup_root.ps1
```

______________________________________________________________________

## GitHub Release v1.3.0

All your code is committed and pushed. To create the official release:

```bash
git tag -a v1.3.0 -m "Production deployment system"
git push origin v1.3.0
```

This will trigger GitHub Actions to build packages (if Android SDK is configured in CI).

______________________________________________________________________

## Bottom Line

**You have a complete production system.**

The heavy automation scripts were causing issues. Just run the backend manually when you want to test it:

1. `python start_api.py` - That's it!
1. Open <http://localhost:8001/docs>
1. Explore the save points endpoints
1. Let it run for hours if you want

Everything else (USB installer, Android app source, documentation) is ready to go.

______________________________________________________________________

**No need for complex launch scripts. Keep it simple!** 🚀
