@echo off
REM Enhanced Cognitive IDE Launcher for Windows
REM Starts all required services

echo ======================================
echo Enhanced Cognitive IDE Launcher
echo ======================================
echo.

REM Check if node is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [31m❌ Node.js is not installed[0m
    echo Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

REM Check if python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [31m❌ Python 3 is not installed[0m
    echo Please install Python 3.10+ from https://python.org
    exit /b 1
)

echo [32m✅ Prerequisites check passed[0m
echo.

REM Start collaboration server
echo [33m🚀 Starting collaboration server...[0m
start /B node collaboration-server.js
timeout /t 2 /nobreak >nul
echo [32m✅ Collaboration server started[0m

REM Start API server
echo [33m🚀 Starting API server...[0m
start /B python api_server.py
timeout /t 2 /nobreak >nul
echo [32m✅ API server started[0m

REM Start development server
echo [33m🚀 Starting development server...[0m
start /B npm run dev
timeout /t 3 /nobreak >nul
echo [32m✅ Development server started[0m

echo.
echo ======================================
echo [32m✨ Enhanced Cognitive IDE is running![0m
echo ======================================
echo.
echo Services:
echo   - Vite Dev Server:    http://localhost:5173
echo   - API Server:         http://localhost:8000
echo   - Collaboration:      ws://localhost:8080
echo.
echo Press Ctrl+C to stop all services
echo.

pause
