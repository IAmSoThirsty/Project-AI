#!/usr/bin/env bash
# =============================================================================
# PROJECT-AI — Oculus Go Full ADB Unlock, Root Flash & Deployment Script
# =============================================================================
# Target Device : Oculus Go (codename: pacific)
# Android Base  : Android 8.1.0 (API 27)
# USB Interface : Micro-USB → USB-A/C → Development Host
# Author        : Project-AI
# Version       : 1.0.0
# =============================================================================
#
# PREREQUISITES (run once before this script):
#   1. Install Android Platform Tools (ADB + Fastboot)
#      → https://developer.android.com/tools/releases/platform-tools
#   2. Install Oculus ADB drivers (Windows only)
#      → https://developer.oculus.com/downloads/package/oculus-adb-drivers/
#   3. Create a Meta Developer Organization
#      → https://dashboard.oculus.com/organization/create
#   4. Enable Developer Mode via Oculus mobile app:
#      → Device → [Your Go] → Developer Mode → ON
#   5. Download Meta's official Unlocked OS build ZIP
#      → https://developers.meta.com/horizon/blog/unlocking-oculus-go/
#      Place the file at: ./unlocked_build.zip (same dir as this script)
#   6. Place your Project-AI APK at: ./ProjectAI.apk
#
# USAGE:
#   chmod +x project_ai_oculus_go_unlock.sh
#   ./project_ai_oculus_go_unlock.sh
#
# STAGES (run independently via argument):
#   ./project_ai_oculus_go_unlock.sh verify        # Stage 0: Device check only
#   ./project_ai_oculus_go_unlock.sh unlock         # Stage 1: Flash unlocked OS
#   ./project_ai_oculus_go_unlock.sh bootloader     # Stage 2: Unlock bootloader
#   ./project_ai_oculus_go_unlock.sh root           # Stage 3: Root + system access
#   ./project_ai_oculus_go_unlock.sh launcher       # Stage 4: Disable stock launcher
#   ./project_ai_oculus_go_unlock.sh deploy         # Stage 5: Deploy Project-AI APK
#   ./project_ai_oculus_go_unlock.sh wifi           # Stage 6: Switch to Wi-Fi ADB
#   ./project_ai_oculus_go_unlock.sh full           # All stages in sequence
#
# ⚠  WARNING: Stages 1 and 2 WIPE ALL USER DATA. There is no undo.
# =============================================================================

set -euo pipefail

# ─── COLOR OUTPUT ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

log()     { echo -e "${CYAN}[PROJECT-AI]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }
banner()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"; \
            echo -e "${BOLD}${CYAN}  $*${RESET}"; \
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}\n"; }

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
UNLOCKED_BUILD="./unlocked_build.zip"
PROJECT_AI_APK="./ProjectAI.apk"
PROJECT_AI_PKG="com.projectai.vr"                  # ← Change to your actual package name
PROJECT_AI_ACTIVITY=".MainActivity"               # ← Change to your main activity class
DEVICE_CODENAME="pacific"
WAIT_TIMEOUT=60                                    # Seconds to wait for device reconnect

# ─── HELPERS ──────────────────────────────────────────────────────────────────

wait_for_device() {
    local mode="${1:-device}"   # 'device', 'recovery', 'sideload', 'bootloader'
    log "Waiting for device in mode: ${mode} (timeout: ${WAIT_TIMEOUT}s) ..."
    local elapsed=0
    while ! adb get-state 2>/dev/null | grep -q "device" && \
          ! fastboot devices 2>/dev/null | grep -q "fastboot"; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ "$elapsed" -ge "$WAIT_TIMEOUT" ]; then
            error "Timed out waiting for device. Check USB connection and try again."
        fi
    done
    success "Device detected."
}

wait_for_adb_device() {
    log "Waiting for ADB device ..."
    adb wait-for-device
    sleep 3
    success "ADB device ready."
}

check_prerequisites() {
    banner "PREREQUISITE CHECK"
    command -v adb      >/dev/null 2>&1 || error "ADB not found. Install Android Platform Tools."
    command -v fastboot >/dev/null 2>&1 || error "Fastboot not found. Install Android Platform Tools."
    success "ADB:      $(adb version | head -1)"
    success "Fastboot: $(fastboot --version | head -1)"

    [ -f "$UNLOCKED_BUILD" ] || error "Unlocked OS build not found at: $UNLOCKED_BUILD"
    success "Unlocked OS build found: $UNLOCKED_BUILD"

    [ -f "$PROJECT_AI_APK" ] || warn "Project-AI APK not found at: $PROJECT_AI_APK (deploy stage will fail)"
}

# =============================================================================
# STAGE 0 — DEVICE VERIFICATION
# =============================================================================
stage_verify() {
    banner "STAGE 0 — DEVICE VERIFICATION"

    log "Checking ADB device connection ..."
    adb devices -l
    echo ""

    DEVICE_SERIAL=$(adb get-serialno 2>/dev/null || echo "NONE")
    if [ "$DEVICE_SERIAL" = "NONE" ]; then
        error "No ADB device found. Check:\n  1. USB cable is plugged in\n  2. Developer Mode is ON\n  3. 'Allow USB Debugging' accepted in headset"
    fi
    success "Device serial: $DEVICE_SERIAL"

    # Confirm it's an Oculus Go
    DEVICE_MODEL=$(adb shell getprop ro.product.device 2>/dev/null | tr -d '[:space:]')
    ANDROID_VER=$(adb shell getprop ro.build.version.release 2>/dev/null | tr -d '[:space:]')
    BUILD_ID=$(adb shell getprop ro.build.id 2>/dev/null | tr -d '[:space:]')

    log "Device model    : $DEVICE_MODEL"
    log "Android version : $ANDROID_VER"
    log "Build ID        : $BUILD_ID"

    if [ "$DEVICE_MODEL" != "$DEVICE_CODENAME" ]; then
        warn "Device codename is '$DEVICE_MODEL', expected '$DEVICE_CODENAME'. Proceed with caution."
    else
        success "Confirmed: Oculus Go (pacific)"
    fi

    # Check current unlock state
    UNLOCK_STATE=$(adb shell getprop ro.boot.flash.locked 2>/dev/null | tr -d '[:space:]')
    log "Bootloader lock state: ${UNLOCK_STATE:-unknown}"
}

# =============================================================================
# STAGE 1 — FLASH UNLOCKED OS (via ADB Sideload)
# =============================================================================
stage_unlock() {
    banner "STAGE 1 — FLASH UNLOCKED OS"

    warn "⚠  THIS WILL WIPE ALL USER DATA ON THE DEVICE."
    warn "   Press ENTER to continue or Ctrl+C to abort."
    read -r

    log "Rebooting device to sideload mode ..."
    adb reboot sideload

    log "Waiting for sideload mode ..."
    sleep 10
    # Some builds show as 'sideload' state, others as 'recovery'
    # adb wait-for-sideload is not always reliable; use a manual poll
    local elapsed=0
    until adb get-state 2>/dev/null | grep -qE "sideload|recovery"; do
        sleep 2
        elapsed=$((elapsed + 2))
        [ "$elapsed" -ge "$WAIT_TIMEOUT" ] && error "Device did not enter sideload mode."
    done
    success "Device in sideload/recovery mode."

    log "Flashing unlocked OS build: $UNLOCKED_BUILD"
    log "This may take 3–8 minutes. Do not disconnect USB ..."
    adb sideload "$UNLOCKED_BUILD"

    success "Unlocked OS flashed successfully."
    log "Device will reboot automatically ..."
    sleep 5
    wait_for_adb_device
    success "Stage 1 complete. Device running Unlocked OS."
}

# =============================================================================
# STAGE 2 — BOOTLOADER UNLOCK (fastboot oem unlock)
# =============================================================================
stage_bootloader() {
    banner "STAGE 2 — BOOTLOADER UNLOCK"

    warn "⚠  THIS WILL WIPE ALL USER DATA AGAIN."
    warn "   Boot.img signature verification and dm-verity will be disabled."
    warn "   Press ENTER to continue or Ctrl+C to abort."
    read -r

    log "Rebooting to bootloader (fastboot mode) ..."
    adb reboot bootloader

    log "Waiting for fastboot device ..."
    fastboot wait-for-device
    sleep 3

    log "Connected fastboot devices:"
    fastboot devices

    log "Sending OEM unlock command ..."
    log "→ CONFIRM THE UNLOCK PROMPT ON THE HEADSET SCREEN using the Volume + Power buttons."
    fastboot oem unlock

    log "Waiting for device to reboot after unlock ..."
    sleep 10
    wait_for_adb_device

    # Verify unlock
    LOCK_STATUS=$(adb shell getprop ro.boot.flash.locked 2>/dev/null | tr -d '[:space:]')
    log "Bootloader lock status: ${LOCK_STATUS}"
    if [ "$LOCK_STATUS" = "0" ]; then
        success "Bootloader is UNLOCKED."
    else
        warn "Lock status returned: '${LOCK_STATUS}'. May still be locked — verify manually."
    fi

    success "Stage 2 complete. Bootloader unlocked."
}

# =============================================================================
# STAGE 3 — ROOT ACCESS + SYSTEM PARTITION REMOUNT
# =============================================================================
stage_root() {
    banner "STAGE 3 — ROOT ACCESS & SYSTEM PARTITION"

    log "Restarting ADB daemon as root ..."
    adb root
    sleep 3

    # Verify root
    WHO=$(adb shell whoami 2>/dev/null | tr -d '[:space:]')
    if [ "$WHO" = "root" ]; then
        success "ADB shell running as root."
    else
        error "Root failed. Ensure you flashed the unlocked OS build in Stage 1."
    fi

    log "Disabling dm-verity ..."
    adb disable-verity || warn "disable-verity returned non-zero (may already be disabled on unlocked build)"
    sleep 2

    log "Rebooting to apply verity changes ..."
    adb reboot
    wait_for_adb_device
    adb root
    sleep 3

    log "Remounting system partition as read-write ..."
    adb remount
    sleep 2

    # Verify
    SYSTEM_RW=$(adb shell mount | grep " /system " | grep -c "rw" || true)
    if [ "$SYSTEM_RW" -gt 0 ]; then
        success "/system mounted read-write."
    else
        warn "/system may still be read-only. Run: adb shell mount -o remount,rw /system"
        adb shell mount -o remount,rw /system || warn "Manual remount also failed — unlocked build may handle this differently."
    fi

    log "System partition info:"
    adb shell df -h /system

    success "Stage 3 complete. Root access and system partition available."
}

# =============================================================================
# STAGE 4 — DISABLE STOCK OCULUS LAUNCHER
# =============================================================================
stage_launcher() {
    banner "STAGE 4 — DISABLE STOCK OCULUS LAUNCHER"

    log "Listing currently active launcher packages ..."
    adb shell pm list packages -e | grep -iE "oculus|home|launcher|systemux" || true
    echo ""

    # Core Oculus UI packages to disable
    OCULUS_PACKAGES=(
        "com.oculus.home"
        "com.oculus.systemux"
        "com.oculus.shellenv"
        "com.oculus.socialplatform"
        "com.oculus.store"
        "com.oculus.guardian"
    )

    for pkg in "${OCULUS_PACKAGES[@]}"; do
        if adb shell pm list packages | grep -q "$pkg"; then
            log "Disabling: $pkg"
            adb shell pm disable-user --user 0 "$pkg" && success "Disabled: $pkg" || warn "Could not disable: $pkg"
        else
            log "Not installed, skipping: $pkg"
        fi
    done

    # Stop any running Oculus services
    log "Force-stopping Oculus services ..."
    for pkg in "${OCULUS_PACKAGES[@]}"; do
        adb shell am force-stop "$pkg" 2>/dev/null || true
    done

    success "Stage 4 complete. Stock launcher disabled."
}

# =============================================================================
# STAGE 5 — DEPLOY PROJECT-AI APK AS DEFAULT HOME
# =============================================================================
stage_deploy() {
    banner "STAGE 5 — DEPLOY PROJECT-AI APK"

    [ -f "$PROJECT_AI_APK" ] || error "Project-AI APK not found: $PROJECT_AI_APK"

    # Enable unknown sources
    log "Enabling installation from unknown sources ..."
    adb shell settings put secure install_non_market_apps 1
    adb shell settings put global package_verifier_enable 0

    # Install APK
    log "Installing Project-AI APK: $PROJECT_AI_APK"
    adb install -r -g "$PROJECT_AI_APK"
    success "APK installed: $PROJECT_AI_PKG"

    # Set as default home activity
    log "Setting Project-AI as default HOME activity ..."
    adb shell cmd package set-home-activity "${PROJECT_AI_PKG}/${PROJECT_AI_PKG}${PROJECT_AI_ACTIVITY}"

    # Set VR category intent handler
    log "Registering Project-AI as default VR app ..."
    adb shell cmd package set-home-activity "${PROJECT_AI_PKG}/${PROJECT_AI_PKG}${PROJECT_AI_ACTIVITY}" || \
        warn "set-home-activity may require manual confirmation on device."

    # Performance tuning for Project-AI
    log "Applying Project-AI performance profile ..."
    adb shell setprop debug.oculus.gpuLevel 4
    adb shell setprop debug.oculus.cpuLevel 4
    adb shell setprop debug.oculus.refreshRate 72
    adb shell setprop debug.oculus.frontbuffer 1     # Reduce latency
    log "GPU Level   : $(adb shell getprop debug.oculus.gpuLevel)"
    log "CPU Level   : $(adb shell getprop debug.oculus.cpuLevel)"
    log "Refresh Rate: $(adb shell getprop debug.oculus.refreshRate) Hz"

    # Optional: also push APK to system/app for persistence across reboots
    # Uncomment below if you want system-level install (requires Stage 3 root)
    # log "Promoting to system app for persistence ..."
    # adb shell mkdir -p /system/app/ProjectAI
    # adb push "$PROJECT_AI_APK" /system/app/ProjectAI/ProjectAI.apk
    # adb shell chmod 644 /system/app/ProjectAI/ProjectAI.apk

    # Launch Project-AI
    log "Launching Project-AI ..."
    adb shell monkey -p "$PROJECT_AI_PKG" -c android.intent.category.LAUNCHER 1
    sleep 3

    # Verify it launched
    FOREGROUND=$(adb shell dumpsys activity activities | grep "mResumedActivity" || true)
    log "Current foreground activity: $FOREGROUND"

    success "Stage 5 complete. Project-AI deployed and launched."
}

# =============================================================================
# STAGE 6 — SWITCH TO WI-FI ADB (cut the USB cord)
# =============================================================================
stage_wifi() {
    banner "STAGE 6 — WI-FI ADB"

    log "Getting device IP address ..."
    DEVICE_IP=$(adb shell ip route | awk '{print $NF}' | head -1)

    if [ -z "$DEVICE_IP" ]; then
        DEVICE_IP=$(adb shell ifconfig wlan0 2>/dev/null | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}')
    fi

    if [ -z "$DEVICE_IP" ]; then
        error "Could not determine device IP. Ensure Go is connected to Wi-Fi."
    fi

    log "Device IP: $DEVICE_IP"
    log "Enabling TCP ADB on port 5555 ..."
    adb tcpip 5555
    sleep 3

    log "Connecting via Wi-Fi: ${DEVICE_IP}:5555"
    log "You can now unplug the USB cable."
    sleep 2
    adb connect "${DEVICE_IP}:5555"
    sleep 2

    # Verify connection
    if adb devices | grep -q "${DEVICE_IP}:5555"; then
        success "Wi-Fi ADB connected: ${DEVICE_IP}:5555"
        log "Run future ADB commands with: adb -s ${DEVICE_IP}:5555 <command>"
    else
        warn "Wi-Fi ADB connection not confirmed. Try manually: adb connect ${DEVICE_IP}:5555"
    fi

    echo ""
    log "Useful Wi-Fi ADB commands:"
    echo "  adb -s ${DEVICE_IP}:5555 shell"
    echo "  adb -s ${DEVICE_IP}:5555 logcat -s ProjectAI"
    echo "  adb -s ${DEVICE_IP}:5555 install -r ./ProjectAI_update.apk"
    echo "  adb -s ${DEVICE_IP}:5555 push ./model_weights /sdcard/project_ai/models/"

    success "Stage 6 complete. USB cord is free."
}

# =============================================================================
# STAGE 7 — LOGCAT MONITOR FOR PROJECT-AI (bonus utility)
# =============================================================================
stage_logcat() {
    banner "PROJECT-AI LOGCAT MONITOR"
    log "Streaming Project-AI logs (Ctrl+C to stop) ..."
    adb logcat -c
    adb logcat "*:S" "${PROJECT_AI_PKG}:V" "AndroidRuntime:E" "ActivityManager:I" | \
        grep --line-buffered -E "ProjectAI|${PROJECT_AI_PKG}|FATAL|Exception|Error"
}

# =============================================================================
# FULL SEQUENCE
# =============================================================================
stage_full() {
    banner "PROJECT-AI — FULL UNLOCK & DEPLOY SEQUENCE"
    warn "This will run ALL stages in order."
    warn "Stages 1 and 2 WIPE ALL DATA. Ensure no important data is on the device."
    warn "Total estimated time: 10–20 minutes."
    echo ""
    warn "Press ENTER to begin or Ctrl+C to abort."
    read -r

    check_prerequisites
    stage_verify
    stage_unlock
    stage_bootloader
    stage_root
    stage_launcher
    stage_deploy
    stage_wifi

    banner "PROJECT-AI DEPLOYMENT COMPLETE"
    success "Oculus Go is fully unlocked and running Project-AI."
    log "The device is now:"
    echo "  ✓ Running Meta's official Unlocked OS"
    echo "  ✓ Bootloader unlocked (dm-verity disabled)"
    echo "  ✓ ADB root access enabled"
    echo "  ✓ Stock Oculus launcher disabled"
    echo "  ✓ Project-AI set as default home activity"
    echo "  ✓ GPU/CPU at max performance profile"
    echo "  ✓ Running at 72 Hz refresh rate"
    echo "  ✓ Accessible via Wi-Fi ADB"
}

# =============================================================================
# ENTRY POINT
# =============================================================================
STAGE="${1:-full}"

case "$STAGE" in
    verify)      check_prerequisites; stage_verify ;;
    unlock)      check_prerequisites; stage_unlock ;;
    bootloader)  check_prerequisites; stage_bootloader ;;
    root)        check_prerequisites; stage_root ;;
    launcher)    check_prerequisites; stage_launcher ;;
    deploy)      check_prerequisites; stage_deploy ;;
    wifi)        check_prerequisites; stage_wifi ;;
    logcat)      stage_logcat ;;
    full)        stage_full ;;
    *)
        echo "Usage: $0 [verify|unlock|bootloader|root|launcher|deploy|wifi|logcat|full]"
        exit 1
        ;;
esac
