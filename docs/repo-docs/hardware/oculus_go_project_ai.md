# Oculus Go — Full Technical Reference & Project-AI VR Integration Guide

---

## SECTION 1: FULL HARDWARE SPECIFICATIONS

| Component | Specification |
|---|---|
| **Chipset** | Qualcomm Snapdragon 821 (MSM8996 Pro) |
| **CPU** | Quad-core Kryo (2x 2.35 GHz + 2x 1.6 GHz) |
| **GPU** | Adreno 530 |
| **RAM** | 3 GB LPDDR4 |
| **Storage** | 32 GB or 64 GB (no microSD) |
| **Display** | 5.5" Fast-switch LCD, single panel |
| **Resolution** | 2560 × 1440 (1280 × 1440 per eye), 538 PPI |
| **Refresh Rate** | 60 Hz (default) or 72 Hz (developer selectable) |
| **Lenses** | Fresnel, fixed IPD 63.5 mm |
| **Field of View** | ~101 degrees |
| **Pixel Density** | 12.67 pixels per degree |
| **Tracking** | 3-Degrees of Freedom (3DOF) — rotational only, no positional |
| **Audio** | Integrated spatial audio speakers + 3.5mm jack + microphone |
| **Connectivity** | USB Micro-B (USB 2.0), Wi-Fi 802.11 a/b/g/n/ac (2.4/5 GHz), Bluetooth 4.1 |
| **Battery** | Built-in Li-Ion; 1.5–2 hrs gaming, 2–2.5 hrs video |
| **Charge Time** | ~3 hrs via 10W (5V 2A) adapter |
| **Dimensions** | 190mm × 105mm × 115mm |
| **Weight** | 468g |
| **OS (stock)** | Android-based Oculus OS (discontinued — last update ~2020) |
| **Controller** | Wireless, 3DOF laser-pointer style |
| **Special Rendering** | Fixed Foveated Rendering (FFR), Dynamic Clock Throttling, Vulkan support |
| **MSRP** | $199 (32 GB) / $249 (64 GB) — discontinued |

> **Note**: No positional (6DOF) tracking. No inside-out cameras. Rotational head tracking only.

---

## SECTION 2: WIPE, RESET & BOOTLOADER UNLOCK PROCEDURES

### 2A — Standard Factory Reset (Software Wipe)

**Via headset (hardware method):**
```
1. Power OFF the headset
2. Hold Power + Volume (-) simultaneously until boot screen appears
3. Navigate with Volume buttons to "Factory Reset"
4. Press Power to select → navigate to "Yes" → confirm
```

**Via Oculus app (phone method):**
```
Settings → Devices → [Select headset] → Advanced Settings → Factory Reset → Reset
```
This wipes all apps, user data, and account links. **Does not alter the OS or bootloader.**

---

### 2B — Full OS Unlock + Bootloader Flash (Deep Wipe for Project-AI)

Meta/Oculus officially released an **Unlocked OS Build** (announced by John Carmack, Oct 2021). This is the key to full reprogramming.

**What it does:**
- Disables boot.img signature verification
- Disables dm-verity kernel enforcement
- Enables `fastboot flash` and `adb root`
- Allows replacement of `boot.img` AND `system.img`
- **COMPLETELY wipes all user data and apps**
- No OTA updates possible after unlock

**Prerequisites:**
- Windows PC (Linux also works)
- [Oculus ADB Drivers](https://developer.oculus.com/downloads/package/oculus-adb-drivers/)
- ADB + Fastboot (Android Platform Tools)
- `unlocked_build.zip` — download from [Meta Developer Unlock Page](https://developers.meta.com/horizon/blog/unlocking-oculus-go/)
- Developer Mode enabled on headset (via Meta/Oculus mobile app)
- Meta developer organization account (create at dashboard.oculus.com)

---

### 2C — Step-by-Step: Full Unlock + Wipe Sequence

```bash
# STEP 1 — Enable Developer Mode
# On phone: Oculus app → Device → Developer Mode → Toggle ON
# (Requires a Meta developer org: dashboard.oculus.com/organization/create)

# STEP 2 — Connect via USB, verify ADB sees device
adb devices
# Accept the "Allow USB Debugging" prompt inside headset

# STEP 3 — Enter ADB Sideload Mode
adb reboot sideload
# OR: hold Volume Up on boot → select "Sideload" in bootloader menu

# STEP 4 — Flash the Unlocked OS build
adb sideload unlocked_build.zip
# Wait for full completion and automatic reboot (~700 MB, takes several minutes)

# STEP 5 — Reboot to Bootloader
adb reboot bootloader
# OR: hold Volume Up from powered off state

# STEP 6 — Unlock Bootloader (THIS ERASES EVERYTHING)
fastboot oem unlock
# Confirm on headset screen
# Device now fully unlocked

# STEP 7 — Verify unlock and root
adb root
adb shell
# You now have root shell access

# STEP 8 — Flash custom boot/system image
fastboot flash boot your_custom_boot.img
fastboot flash system your_custom_system.img
fastboot reboot
```

**To re-lock (restores signature checking, wipes data again):**
```bash
fastboot oem lock
```

---

## SECTION 3: ADB COMMAND INTERFACE — PROJECT-AI TERMINAL REFERENCE

Once developer mode + ADB is active, this is your full command interface:

```bash
# Device connection
adb devices                          # List connected devices
adb shell                            # Open shell on device
adb root                             # Restart adbd with root (unlocked only)

# App management
adb install myapp.apk                # Install APK
adb uninstall com.package.name       # Remove app
adb shell pm list packages -3        # List sideloaded packages
adb shell pm disable-user com.oculus.home   # Disable stock launcher

# Launch apps directly
adb shell monkey -p com.your.app 1   # Launch app by package name
adb shell am force-stop com.your.app # Force stop app

# File system
adb push localfile /sdcard/path      # Push file to device
adb pull /sdcard/path localfile      # Pull file from device

# System settings
adb shell settings put secure install_non_market_apps 1  # Enable unknown sources

# Unlock firmware-specific
adb shell getprop ro.build.version.release  # Check Android version
adb shell getprop ro.product.device         # Confirm device = "pacific"

# Performance
adb shell setprop debug.oculus.gpuLevel 4   # Max GPU performance level
adb shell setprop debug.oculus.cpuLevel 4   # Max CPU performance level

# Framerate
adb shell setprop debug.oculus.refreshRate 72   # Force 72Hz mode
```

---

## SECTION 4: CUSTOM SOFTWARE / VR INTERFACE — PROJECT-AI BUILD OPTIONS

### Option A — Unity + Meta XR SDK (Recommended for fastest deployment)

**Stack:**
- Unity 2022 LTS or Unity 6
- Meta XR All-in-One SDK (from Unity Asset Store or [developers.meta.com](https://developers.meta.com/horizon/downloads/))
- Android Build Support module
- JDK 11 + Android SDK API Level 25+ (Oculus Go targets API 25)

**Build target settings for Oculus Go:**
```
Platform: Android
Architecture: ARM64 (or ARMv7 for legacy)
Minimum API Level: Android 7.1 (API 25)
Target API Level: API 26
XR Plugin: Oculus XR Plugin OR legacy Oculus SDK
Stereo Rendering: Single Pass (Multiview for performance)
```

**Output:** `.apk` → deploy via `adb install project_ai.apk`

---

### Option B — Native C++ with OpenXR (Maximum control for Project-AI)

**Stack:**
- Android NDK r21+
- OpenXR SDK (Meta Mobile OpenXR loader — v19+ official support)
- Vulkan 1.0 (preferred renderer for Go's Adreno 530)
- CMake build system

**Key APIs:**
```cpp
// OpenXR initialization (mobile)
xrCreateInstance(...)
xrGetSystem(...)
xrCreateSession(...)
xrCreateSwapchain(...)  // VR stereo rendering

// Oculus VrAPI (legacy, deprecated Aug 2022 — use OpenXR instead)
vrapi_EnterVrMode(...)
vrapi_SubmitFrame2(...)
```

**Deploy:**
```bash
adb install project_ai_native.apk
adb shell monkey -p com.projectai.vr 1
```

---

### Option C — Custom Launcher / Replace Stock OS UI

With the unlocked firmware, you can **replace the entire Oculus home screen launcher**:

```bash
# Disable default Oculus launcher
adb shell pm disable-user com.oculus.home
adb shell pm disable-user com.oculus.systemux

# Set your APK as the default home activity
adb shell cmd package set-home-activity com.projectai.launcher/.MainActivity

# Or push your launcher as a system app (root required)
adb root
adb remount  # Remount system partition as R/W
adb push ProjectAI_Launcher.apk /system/app/ProjectAILauncher/ProjectAI_Launcher.apk
adb shell chmod 644 /system/app/ProjectAILauncher/ProjectAI_Launcher.apk
adb reboot
```

**Community reference:** [woroko's Go App Launcher](https://github.com/woroko) provides an open-source custom launcher already built for unlocked Go firmware (Jan 2025 release).

---

### Option D — WebXR via Custom Browser (Python/Node.js friendly for Project-AI)

Since Go runs Android, you can push a custom browser (Chromium-based) and serve WebXR apps from a local server or Project-AI backend:

```bash
# Push custom Chromium APK with WebXR support
adb install chromium_webxr.apk

# Point to your Project-AI local WebXR server
# Run on connected machine: python -m http.server 8080
# Access from Go's browser: http://YOUR_PC_IP:8080/project_ai_vr.html
```
**WebXR stack:** A-Frame, Three.js, or Babylon.js — all work with 3DOF Go controller input.

---

## SECTION 5: PROJECT-AI VR INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────┐
│         PROJECT-AI BACKEND          │
│  (Python / Node.js / FastAPI)       │
│  Running on PC / Cloud              │
└──────────────┬──────────────────────┘
               │ WebSocket / REST API
               │ (Wi-Fi — same network)
               ▼
┌─────────────────────────────────────┐
│         OCULUS GO (UNLOCKED)        │
│  Custom APK or WebXR frontend       │
│  Receives AI commands / renders VR  │
│  Sends: head orientation (3DOF)     │
│  Receives: scene data, AI responses │
└─────────────────────────────────────┘
               │
               │ USB (ADB for deploy/debug)
               │ Micro-USB → PC
               ▼
┌─────────────────────────────────────┐
│           DEVELOPMENT PC            │
│  ADB command terminal               │
│  Unity / Android Studio / VS Code   │
│  fastboot flash pipeline            │
└─────────────────────────────────────┘
```

**Controller input mapping for Project-AI:**
- Touchpad → Navigation / menu selection
- Trigger → Primary action / AI interaction trigger
- Back button → Return / cancel
- Head orientation → 3DOF Euler angles via `VrApi` or `OpenXR` → feed to AI spatial reasoning module

---

## SECTION 6: IMPORTANT LIMITATIONS & WORKAROUNDS

| Limitation | Impact on Project-AI | Workaround |
|---|---|---|
| 3DOF only (no positional tracking) | No room-scale movement | Use fixed-position AI command interface UI |
| USB 2.0 only | Slow file transfer (~40 MB/s max) | Use Wi-Fi ADB: `adb connect <IP>:5555` |
| No Google Play Services | Some Android libs unavailable | Bundle all dependencies in APK |
| Discontinued Meta support | No new SDK updates | Use unlocked OS + OpenXR 1.0 |
| ~60 MB free system partition | Limited system app installs | Extend via Magisk + custom recovery (TWRP in progress) |
| No 6DOF cameras | Can't do hand tracking | Controller-only UI or Bluetooth gamepad |
| Battery: 1.5–2 hrs | Session limits | USB passthrough power (limited support) |

---

## SECTION 7: TOOLS & DOWNLOAD LINKS

| Tool | Purpose | Link |
|---|---|---|
| Oculus ADB Drivers | USB connection on Windows | developer.oculus.com/downloads/package/oculus-adb-drivers/ |
| Unlocked OS Build | Bootloader unlock + root | developers.meta.com/horizon/blog/unlocking-oculus-go/ |
| Meta XR SDK | VR development SDK | developers.meta.com/horizon/downloads/ |
| SideQuest | GUI sideload tool | sidequestvr.com |
| Platform Tools (ADB/Fastboot) | Core ADB commands | developer.android.com/tools/releases/platform-tools |
| Go App Launcher | Custom launcher post-unlock | github.com/woroko |
| postmarketOS port | Linux on Go (WIP) | wiki.postmarketos.org/wiki/Oculus_Go_(oculus-pacific) |
| OpenXR SDK | Cross-platform VR API | khronos.org/openxr |

---

*Generated for Project-AI — Oculus Go VR Integration Research*
*April 2026*
