@echo off
title Legion Web Interface
echo ========================================
echo   LEGION WEB INTERFACE LAUNCHER
echo ========================================
echo.
echo   Serving interface on: http://localhost:8003
echo   Connecting to Legion API: http://localhost:8002
echo.

start "" "http://localhost:8003/legion_interface.html"
python -m http.server 8003 --directory integrations/openclaw
