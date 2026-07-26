@echo off
setlocal
cd /d "%~dp0"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\owner\Install-ProjectAIOffline.ps1"
if errorlevel 1 pause
