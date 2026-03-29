@echo off
REM Thirstys Waterfall - Windows Installation Script
REM Run with: install.bat

echo =================================
echo Thirstys Waterfall Installer
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected

REM Check if pip is installed
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed
    echo Please reinstall Python with pip
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install package
echo.
echo Installing Thirstys Waterfall...
if exist setup.py (
    echo Installing from local source...
    python -m pip install -e .
) else if exist pyproject.toml (
    echo Installing from local source...
    python -m pip install -e .
) else (
    echo Installing from PyPI...
    python -m pip install thirstys-waterfall
)

if %errorlevel% neq 0 (
    echo Error: Installation failed
    pause
    exit /b 1
)

REM Platform-specific information
echo.
echo For full VPN and firewall functionality, you may need:
echo   - WireGuard for Windows: https://www.wireguard.com/install/
echo   - OpenVPN for Windows: https://openvpn.net/community-downloads/
echo   - Windows Firewall is built-in
echo.

REM Verify installation
echo Verifying installation...
python -c "from thirstys_waterfall import ThirstysWaterfall; print('Import successful')" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Installation verification failed
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo Usage:
echo   thirstys-waterfall --help    # Show help
echo   thirstys-waterfall --status  # Show status
echo.
echo Python API:
echo   from thirstys_waterfall import ThirstysWaterfall
echo   waterfall = ThirstysWaterfall()
echo   waterfall.start()
echo.
echo Next steps:
echo   1. Copy .env.example to .env and configure
echo   2. Review examples\ directory for usage examples
echo   3. Read the documentation in README.md
echo.
pause
