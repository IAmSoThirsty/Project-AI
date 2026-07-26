@echo off
setlocal
cd /d "%~dp0"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\owner\Stop-ProjectAI.ps1"
if errorlevel 1 pause
