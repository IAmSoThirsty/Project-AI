@echo off
:: =============================================================================
:: PROJECT-AI — Oculus Go Full ADB Unlock & Deploy Script (Windows)
:: =============================================================================
:: Target Device : Oculus Go (codename: pacific)
:: Host OS       : Windows 11 Pro
:: Author        : Project-AI
:: =============================================================================
::
:: USAGE:
::   Run as Administrator
::   project_ai_oculus_go_unlock.bat [stage]
::   Stages: verify | unlock | bootloader | root | launcher | deploy | wifi | full
::
:: =============================================================================

setlocal enabledelayedexpansion

:: ─── CONFIGURATION ───────────────────────────────────────────────────────────
set UNLOCKED_BUILD=unlocked_build.zip
set PROJECT_AI_APK=ProjectAI.apk
set PROJECT_AI_PKG=com.projectai.vr
set PROJECT_AI_ACTIVITY=.MainActivity

set STAGE=%1
if "%STAGE%"=="" set STAGE=full

:: ─── COLOR (via PowerShell) ──────────────────────────────────────────────────
:: We use powershell for colored output on Windows
set "LOG=powershell -command Write-Host"

goto :main

:log
    powershell -command "Write-Host '[PROJECT-AI] %~1' -ForegroundColor Cyan"
    goto :eof

:success
    powershell -command "Write-Host '[OK] %~1' -ForegroundColor Green"
    goto :eof

:warn
    powershell -command "Write-Host '[WARN] %~1' -ForegroundColor Yellow"
    goto :eof

:error
    powershell -command "Write-Host '[ERROR] %~1' -ForegroundColor Red"
    pause
    exit /b 1

:banner
    powershell -command "Write-Host '══════════════════════════════════════' -ForegroundColor Cyan"
    powershell -command "Write-Host '  %~1' -ForegroundColor Cyan"
    powershell -command "Write-Host '══════════════════════════════════════' -ForegroundColor Cyan"
    goto :eof

:: =============================================================================
:stage_verify
    call :banner "STAGE 0 — DEVICE VERIFICATION"
    call :log "Checking ADB connection..."
    adb devices -l
    if errorlevel 1 call :error "ADB not found. Install Platform Tools."

    for /f "skip=1 tokens=1" %%i in ('adb devices') do (
        if not "%%i"=="" set SERIAL=%%i
    )

    for /f %%i in ('adb shell getprop ro.product.device') do set MODEL=%%i
    for /f %%i in ('adb shell getprop ro.build.version.release') do set ANDROID=%%i
    for /f %%i in ('adb shell getprop ro.build.id') do set BUILDID=%%i

    call :log "Device model    : %MODEL%"
    call :log "Android version : %ANDROID%"
    call :log "Build ID        : %BUILDID%"

    if "%MODEL%"=="pacific" (
        call :success "Confirmed: Oculus Go"
    ) else (
        call :warn "Device codename '%MODEL%' - expected 'pacific'. Proceed carefully."
    )
    goto :eof

:: =============================================================================
:stage_unlock
    call :banner "STAGE 1 — FLASH UNLOCKED OS"
    call :warn "THIS WILL WIPE ALL DATA. Press any key to continue or close window to abort."
    pause

    if not exist "%UNLOCKED_BUILD%" call :error "Unlocked build not found: %UNLOCKED_BUILD%"

    call :log "Rebooting to sideload mode..."
    adb reboot sideload

    call :log "Waiting 15 seconds for sideload mode..."
    timeout /t 15 /nobreak

    call :log "Flashing unlocked OS (this takes 3-8 minutes)..."
    adb sideload "%UNLOCKED_BUILD%"

    call :success "Unlocked OS flashed."
    call :log "Waiting for device reboot..."
    timeout /t 15 /nobreak
    adb wait-for-device
    call :success "Stage 1 complete."
    goto :eof

:: =============================================================================
:stage_bootloader
    call :banner "STAGE 2 — BOOTLOADER UNLOCK"
    call :warn "THIS WILL WIPE ALL DATA AGAIN. Press any key to continue."
    pause

    call :log "Rebooting to fastboot mode..."
    adb reboot bootloader
    timeout /t 8 /nobreak

    call :log "Connected fastboot devices:"
    fastboot devices

    call :log "Sending OEM unlock..."
    call :warn "CONFIRM the unlock prompt ON THE HEADSET using Volume + Power buttons."
    fastboot oem unlock

    call :log "Waiting for reboot..."
    timeout /t 15 /nobreak
    adb wait-for-device

    for /f %%i in ('adb shell getprop ro.boot.flash.locked') do set LOCKSTATE=%%i
    call :log "Bootloader lock state: %LOCKSTATE%"
    if "%LOCKSTATE%"=="0" (
        call :success "Bootloader UNLOCKED."
    ) else (
        call :warn "Lock state unclear. Verify on device."
    )
    call :success "Stage 2 complete."
    goto :eof

:: =============================================================================
:stage_root
    call :banner "STAGE 3 — ROOT ACCESS"

    call :log "Restarting ADB as root..."
    adb root
    timeout /t 5 /nobreak

    for /f %%i in ('adb shell whoami') do set WHO=%%i
    if "%WHO%"=="root" (
        call :success "Running as root."
    ) else (
        call :error "Root failed. Flash unlocked OS first."
    )

    call :log "Disabling dm-verity..."
    adb disable-verity

    call :log "Rebooting to apply changes..."
    adb reboot
    adb wait-for-device
    adb root
    timeout /t 5 /nobreak

    call :log "Remounting /system as RW..."
    adb remount

    call :success "Stage 3 complete. Root active."
    goto :eof

:: =============================================================================
:stage_launcher
    call :banner "STAGE 4 — DISABLE STOCK LAUNCHER"

    call :log "Disabling Oculus UI packages..."

    for %%p in (
        com.oculus.home
        com.oculus.systemux
        com.oculus.shellenv
        com.oculus.socialplatform
        com.oculus.store
        com.oculus.guardian
    ) do (
        call :log "Disabling: %%p"
        adb shell pm disable-user --user 0 %%p 2>nul || call :warn "Could not disable %%p"
        adb shell am force-stop %%p 2>nul
    )

    call :success "Stage 4 complete. Stock launcher disabled."
    goto :eof

:: =============================================================================
:stage_deploy
    call :banner "STAGE 5 — DEPLOY PROJECT-AI"

    if not exist "%PROJECT_AI_APK%" call :error "APK not found: %PROJECT_AI_APK%"

    call :log "Enabling unknown sources..."
    adb shell settings put secure install_non_market_apps 1
    adb shell settings put global package_verifier_enable 0

    call :log "Installing Project-AI APK..."
    adb install -r -g "%PROJECT_AI_APK%"
    call :success "APK installed: %PROJECT_AI_PKG%"

    call :log "Setting as default home activity..."
    adb shell cmd package set-home-activity %PROJECT_AI_PKG%/%PROJECT_AI_PKG%%PROJECT_AI_ACTIVITY%

    call :log "Applying performance profile..."
    adb shell setprop debug.oculus.gpuLevel 4
    adb shell setprop debug.oculus.cpuLevel 4
    adb shell setprop debug.oculus.refreshRate 72
    adb shell setprop debug.oculus.frontbuffer 1

    call :log "Launching Project-AI..."
    adb shell monkey -p %PROJECT_AI_PKG% -c android.intent.category.LAUNCHER 1

    call :success "Stage 5 complete. Project-AI deployed."
    goto :eof

:: =============================================================================
:stage_wifi
    call :banner "STAGE 6 — WI-FI ADB"

    for /f "tokens=*" %%i in ('adb shell ip route ^| findstr /r "src"') do (
        for %%j in (%%i) do set DEVICE_IP=%%j
    )

    if "%DEVICE_IP%"=="" (
        call :warn "Could not auto-detect IP. Check: adb shell ip route"
    ) else (
        call :log "Device IP: %DEVICE_IP%"
    )

    call :log "Enabling TCP/IP on port 5555..."
    adb tcpip 5555
    timeout /t 3 /nobreak

    call :log "You can now unplug USB."
    if not "%DEVICE_IP%"=="" (
        adb connect %DEVICE_IP%:5555
        call :success "Wi-Fi ADB: %DEVICE_IP%:5555"
    )

    call :success "Stage 6 complete."
    goto :eof

:: =============================================================================
:stage_full
    call :banner "PROJECT-AI — FULL SEQUENCE"
    call :warn "All stages will run. Stages 1 and 2 WIPE ALL DATA."
    call :warn "Press any key to begin or close window to abort."
    pause

    call :stage_verify
    call :stage_unlock
    call :stage_bootloader
    call :stage_root
    call :stage_launcher
    call :stage_deploy
    call :stage_wifi

    call :banner "PROJECT-AI DEPLOYMENT COMPLETE"
    call :success "Oculus Go unlocked and running Project-AI."
    goto :eof

:: =============================================================================
:main
    if "%STAGE%"=="verify"      goto :stage_verify
    if "%STAGE%"=="unlock"      goto :stage_unlock
    if "%STAGE%"=="bootloader"  goto :stage_bootloader
    if "%STAGE%"=="root"        goto :stage_root
    if "%STAGE%"=="launcher"    goto :stage_launcher
    if "%STAGE%"=="deploy"      goto :stage_deploy
    if "%STAGE%"=="wifi"        goto :stage_wifi
    if "%STAGE%"=="full"        goto :stage_full

    echo Usage: project_ai_oculus_go_unlock.bat [verify^|unlock^|bootloader^|root^|launcher^|deploy^|wifi^|full]
    exit /b 1
