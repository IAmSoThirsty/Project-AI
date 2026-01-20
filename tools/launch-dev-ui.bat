@echo off
REM Launch developer UI: activate venv-designer and run the desktop app.
REM Usage: double-click or run in cmd. Optional argument /designer to also launch Qt Designer.
nSET SCRIPT_DIR=%~dp0
SET REPO_ROOT=%SCRIPT_DIR%..\
SET VENV_DIR=%REPO_ROOT%venv-designer
necho Activating venv: %VENV_DIR%
IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
  CALL "%VENV_DIR%\Scripts\activate.bat"
) ELSE (
  echo Virtual environment not found. Creating now...
  python -m venv "%VENV_DIR%"
  CALL "%VENV_DIR%\Scripts\activate.bat"
)
necho Running developer UI (python -m src.app.main)...
start "Project-AI" cmd /k "python -m src.app.main"
nREM Optionally launch Designer if /designer passednSET LAUNCH_DESIGNER=0nfor %%a in (%*) do (
  if /I "%%~a"=="/designer" set LAUNCH_DESIGNER=1
)
IF "%LAUNCH_DESIGNER%"=="1" (
  IF EXIST "%VENV_DIR%\Scripts\pyside6-designer.exe" (
    start "Qt Designer" "%VENV_DIR%\Scripts\pyside6-designer.exe"
  ) ELSE IF EXIST "%VENV_DIR%\Lib\site-packages\PySide6\Qt\bin\designer.exe" (
    start "Qt Designer" "%VENV_DIR%\Lib\site-packages\PySide6\Qt\bin\designer.exe"
  ) ELSE (
    echo Designer executable not found in venv. Ensure pyside6 is installed or pass /designer after installing Qt.
  )
)
necho Launched UI. Close this window or press any key to exit.
pause
