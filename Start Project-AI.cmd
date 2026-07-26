@echo off
setlocal
cd /d "%~dp0"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\owner\Start-ProjectAI.ps1" -Offline
if errorlevel 1 pause
