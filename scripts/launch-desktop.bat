@echo off
REM Project-AI Desktop Application Launcher
REM This script launches the Project-AI dashboard application
REM Create a shortcut to this file on your desktop for easy access

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11+ or add it to your PATH
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create it
if not exist "%SCRIPT_DIR%.venv" (
    echo Creating Python virtual environment...
    python -m venv "%SCRIPT_DIR%.venv"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies if needed
pip install -q -r "%SCRIPT_DIR%requirements.txt" 2>nul

REM Launch the application
echo Launching Project-AI Dashboard...
python "%SCRIPT_DIR%src\app\main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Please check that all dependencies are installed
    echo.
    pause
)

endlocal
