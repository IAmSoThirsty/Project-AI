@echo off
REM Project-AI Desktop Application Setup
REM This script sets up Project-AI as a desktop application with shortcuts
REM Run as Administrator for full functionality

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Project-AI Desktop Application Setup
echo ========================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src"

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: This script should be run as Administrator for full functionality
    echo Some features (like Start Menu shortcuts) may not work without admin rights
    echo.
    echo Continuing with limited functionality...
    echo.
)

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python is installed and available.
echo.

REM Create virtual environment if it doesn't exist
if not exist "%SCRIPT_DIR%.venv" (
    echo Creating Python virtual environment...
    python -m venv "%SCRIPT_DIR%.venv"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing dependencies from requirements.txt...
if exist "%SCRIPT_DIR%requirements.txt" (
    pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo WARNING: Some dependencies may not have installed correctly
    )
) else (
    echo WARNING: requirements.txt not found
)

echo.
echo ========================================
echo   Installation Complete
echo ========================================
echo.
echo You can now launch Project-AI using:
echo   1. Double-click: launch-desktop.bat
echo   2. Desktop shortcut (if created)
echo   3. Start Menu (if created)
echo.
echo To create desktop and Start Menu shortcuts, run:
echo   python install-shortcuts.py
echo.
echo To start the application now, press any key...
echo.
pause

REM Launch the application
set "PYTHONPATH=%SCRIPT_DIR%src"
python "%SCRIPT_DIR%src\app\main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Please check that all dependencies are installed
    echo.
    pause
)

endlocal
