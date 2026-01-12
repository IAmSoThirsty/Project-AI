@echo off
REM Setup a Qt Designer development virtual environment (Windows)
REM - Creates/activates venv at repo root: venv-designer
REM - Installs tools from requirements-designer.txt (tools/ then repo root)
REM - Falls back to PyQt6 (+pyqt6-tools) or PySide6 and attempts to launch Qt Designer

SETLOCAL
SET SCRIPT_DIR=%~dp0
REM project root is parent of tools\
SET REPO_ROOT=%SCRIPT_DIR%..\
SET VENV_DIR=%REPO_ROOT%venv-designer
SET LOG_FILE=%SCRIPT_DIR%setup_designer_env.log

echo Using repository root: %REPO_ROOT%

REM Ensure python is available
where python >nul 2>&1
IF ERRORLEVEL 1 (
  echo Python not found in PATH. Install Python 3.8+ or add it to PATH and re-run.
  pause
  exit /b 1
)

echo Creating virtual environment at %VENV_DIR% (if it doesn't exist)...
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
  python -m venv "%VENV_DIR%"
  IF ERRORLEVEL 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

CALL "%VENV_DIR%\Scripts\activate.bat"
IF ERRORLEVEL 1 (
  echo Failed to activate virtual environment.
  pause
  exit /b 1
)

echo Upgrading pip, setuptools and wheel (logging to %LOG_FILE%)...
python -m pip install --upgrade pip setuptools wheel > "%LOG_FILE%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo Failed upgrading pip. See %LOG_FILE% for details.
)

REM Install designer-specific requirements if present, otherwise fall back to PyQt6 + pyqt6-tools
SET "DESIGNER_BACKEND=pyqt"
IF EXIST "%SCRIPT_DIR%requirements-designer.txt" (
  echo Installing packages from %SCRIPT_DIR%requirements-designer.txt (logging to %LOG_FILE%)...
  pip install -r "%SCRIPT_DIR%requirements-designer.txt" > "%LOG_FILE%" 2>&1
  IF %ERRORLEVEL% NEQ 0 (
    echo Installation from %SCRIPT_DIR%requirements-designer.txt failed. See %LOG_FILE%.
  )
  GOTO :after_installs
)
IF EXIST "%REPO_ROOT%requirements-designer.txt" (
  echo Installing packages from %REPO_ROOT%requirements-designer.txt (logging to %LOG_FILE%)...
  pip install -r "%REPO_ROOT%requirements-designer.txt" > "%LOG_FILE%" 2>&1
  IF %ERRORLEVEL% NEQ 0 (
    echo Installation from %REPO_ROOT%requirements-designer.txt failed. See %LOG_FILE%.
  )
  GOTO :after_installs
)

echo No requirements-designer.txt found. Attempting to install PyQt6 + pyqt6-tools (logging to %LOG_FILE%)...
pip install pyqt6 pyqt6-tools > "%LOG_FILE%" 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO :try_pyside
GOTO :after_installs

:try_pyside
echo PyQt6 installation failed. Attempting to install PySide6 as a fallback (logging to %LOG_FILE%)...
pip install pyside6 > "%LOG_FILE%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo PySide6 installation also failed. See %LOG_FILE% for details.
  echo You may need to install Qt Designer manually and add it to PATH.
  GOTO :install_failed
)
SET "DESIGNER_BACKEND=pyside"

:after_installs

REM Try to locate and run Qt Designer for the selected backend
IF "%DESIGNER_BACKEND%"=="pyqt" (
  IF EXIST "%VENV_DIR%\Scripts\designer.exe" (
    echo Launching Qt Designer (PyQt) ...
    start "" "%VENV_DIR%\Scripts\designer.exe"
    GOTO :eof
  )
  IF EXIST "%VENV_DIR%\Lib\site-packages\pyqt6_tools\Qt\bin\designer.exe" (
    echo Launching Qt Designer from pyqt6_tools package...
    start "" "%VENV_DIR%\Lib\site-packages\pyqt6_tools\Qt\bin\designer.exe"
    GOTO :eof
  )
  IF EXIST "%VENV_DIR%\Scripts\pyqt6-tools.exe" (
    echo Launching pyqt6-tools...
    start "" "%VENV_DIR%\Scripts\pyqt6-tools.exe"
    GOTO :eof
  )
)

IF "%DESIGNER_BACKEND%"=="pyside" (
  IF EXIST "%VENV_DIR%\Scripts\pyside6-designer.exe" (
    echo Launching Qt Designer (PySide6) ...
    start "" "%VENV_DIR%\Scripts\pyside6-designer.exe"
    GOTO :eof
  )
  IF EXIST "%VENV_DIR%\Lib\site-packages\PySide6\Qt\bin\designer.exe" (
    echo Launching Qt Designer from PySide6 package...
    start "" "%VENV_DIR%\Lib\site-packages\PySide6\Qt\bin\designer.exe"
    GOTO :eof
  )
)

REM Try common executable names on PATH as a last resort
where designer >nul 2>&1
IF NOT ERRORLEVEL 1 (
  echo Launching Designer from PATH...
  start "" "designer"
  GOTO :eof
)
where pyside6-designer >nul 2>&1
IF NOT ERRORLEVEL 1 (
  echo Launching pyside6-designer from PATH...
  start "" "pyside6-designer"
  GOTO :eof
)
where pyqt6-tools >nul 2>&1
IF NOT ERRORLEVEL 1 (
  echo Launching pyqt6-tools from PATH...
  start "" "pyqt6-tools"
  GOTO :eof
)

:install_failed
echo Installation failed. See %LOG_FILE% for details.
echo To launch Designer manually:
echo 1) Activate the venv: call "%VENV_DIR%\Scripts\activate.bat"
echo 2) Run: "%%VENV_DIR%%\Scripts\designer.exe" if present or use an external Qt Designer installation.
echo Alternatively install Qt (https://www.qt.io/download) and add the Qt bin folder to PATH.

pause
