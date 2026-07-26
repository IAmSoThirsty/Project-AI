@echo off
setlocal
cd /d "%~dp0"
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\owner\Status-ProjectAI.ps1"
pause
