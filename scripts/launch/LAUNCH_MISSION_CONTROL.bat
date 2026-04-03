@echo off
:: Project-AI Mission Control Launch Script
:: Starts all systems for production deployment

title PROJECT-AI MISSION CONTROL
color 0A
cls

echo ========================================
echo   PROJECT-AI MISSION CONTROL
echo   LAUNCH SEQUENCE INITIATED
echo ========================================
echo.

:: Check if already running
tasklist /FI "WINDOWTITLE eq PROJECT-AI Backend*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [WARNING] Backend already running!
    echo Press Ctrl+C to abort, or
    pause
)

echo [T-4] Starting Project-AI Backend...
echo.
start "PROJECT-AI Backend" cmd /k "python start_api.py"
timeout /t 3 /nobreak >nul

echo [T-3] Waiting for backend initialization...
timeout /t 5 /nobreak >nul

echo [T-2] Starting Legion API...
echo.
start "Legion API" cmd /k "python integrations\openclaw\legion_api.py"
timeout /t 3 /nobreak >nul

echo [T-1] Opening Legion Interface...
timeout /t 3 /nobreak >nul
start http://localhost:8002

echo.
echo ========================================
echo   LAUNCH SUCCESSFUL!
echo ========================================
echo.
echo   Backend API:  http://localhost:8001
echo   Legion API:   http://localhost:8002
echo   API Docs:     http://localhost:8001/docs
echo.
echo   Save Points:  Auto-saving every 15 minutes
echo   Governance:   Triumvirate active
echo.
echo ========================================
echo.
echo Press any key to open Mission Control Dashboard...
pause >nul

start http://localhost:8001/docs

echo.
echo Mission Control Dashboard opened!
echo.
echo To stop all services:
echo   1. Close both command windows
echo   2. Or press Ctrl+C in each window
echo.
pause
