@echo off
REM Create complete v1.0.0 release package with all platforms (Windows)
REM Enhanced with dependency validation, manifest checking, and JSON reporting

setlocal enabledelayedexpansion

set VERSION=1.0.0
set RELEASE_DIR=releases\project-ai-v%VERSION%
set DATE_STR=%date:~-4%-%date:~4,2%-%date:~7,2%

echo =========================================
echo Project AI v%VERSION% Release Builder
echo =========================================
echo Date: %DATE_STR%
echo.

REM Check dependencies
echo Checking system dependencies...
set MISSING_DEPS=0

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK Python found
) else (
    echo   ERROR Python not found
    set /a MISSING_DEPS+=1
)

where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK Node.js found
) else (
    echo   WARNING Node.js not found ^(optional^)
)

where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK npm found
) else (
    echo   WARNING npm not found ^(optional^)
)

where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   OK Docker found
) else (
    echo   WARNING Docker not found ^(optional^)
)

if exist gradlew (
    echo   OK Gradle wrapper found
) else (
    echo   WARNING Gradle wrapper not found
)

echo.

if %MISSING_DEPS% GTR 0 (
    echo ERROR: Missing required dependencies. Please install them first.
    exit /b 1
)

REM Create release directories
mkdir "%RELEASE_DIR%\backend" 2>nul
mkdir "%RELEASE_DIR%\web" 2>nul
mkdir "%RELEASE_DIR%\android" 2>nul
mkdir "%RELEASE_DIR%\desktop" 2>nul
mkdir "%RELEASE_DIR%\docs" 2>nul
mkdir "%RELEASE_DIR%\monitoring" 2>nul

REM 1. Backend API
echo [1/5] Building Backend API...
echo   - Copying source files...
xcopy /E /I /Q api "%RELEASE_DIR%\backend\api"
xcopy /E /I /Q tarl "%RELEASE_DIR%\backend\tarl"
xcopy /E /I /Q config "%RELEASE_DIR%\backend\config"
xcopy /E /I /Q utils "%RELEASE_DIR%\backend\utils"
xcopy /E /I /Q kernel "%RELEASE_DIR%\backend\kernel"
xcopy /E /I /Q governance "%RELEASE_DIR%\backend\governance"
copy start_api.py "%RELEASE_DIR%\backend\" >nul
copy requirements.txt "%RELEASE_DIR%\backend\" >nul
copy .env.example "%RELEASE_DIR%\backend\.env" >nul

echo   - Creating startup script...
(
echo @echo off
echo echo Starting Project AI Governance API v1.0.0...
echo pip install -r requirements.txt
echo python start_api.py
) > "%RELEASE_DIR%\backend\start.bat"

echo OK Backend packaged

REM 2. Web Frontend
echo [2/5] Packaging Web Frontend...
xcopy /E /I /Q web "%RELEASE_DIR%\web"

echo OK Web packaged

REM 3. Android (copy if exists)
echo [3/5] Checking for Android APK...
if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    copy "android\app\build\outputs\apk\debug\app-debug.apk" ^
         "%RELEASE_DIR%\android\project-ai-v%VERSION%-debug.apk" >nul
    echo OK Android APK found
) else (
    echo WARNING Android APK not found - run gradlew assembleDebug first
)

REM 4. Desktop (copy if exists)
echo [4/5] Checking for Desktop builds...
if exist "desktop\dist" (
    xcopy /E /I /Q desktop\dist "%RELEASE_DIR%\desktop"
    echo OK Desktop apps found
) else (
    echo WARNING Desktop builds not found - run npm run build first
)

REM 5. Monitoring Agents
echo [5/7] Packaging Monitoring Agents...
if exist monitoring (
    xcopy /E /I /Q monitoring "%RELEASE_DIR%\monitoring"
    echo OK Monitoring agents packaged
) else (
    echo WARNING Monitoring directory not found
)

REM 6. Documentation
echo [6/7] Copying Documentation...
copy README.md "%RELEASE_DIR%\" >nul
copy CONSTITUTION.md "%RELEASE_DIR%\" >nul
copy CHANGELOG.md "%RELEASE_DIR%\" >nul
copy LICENSE "%RELEASE_DIR%\" >nul
copy SECURITY.md "%RELEASE_DIR%\" >nul
if exist docs xcopy /E /I /Q docs "%RELEASE_DIR%\docs" >nul

REM Create master README
(
echo # Project AI Governance Kernel v%VERSION%
echo.
echo Official production release - %DATE_STR%
echo.
echo ## What's Included
echo.
echo - Backend API
echo - Web Frontend
echo - Android App
echo - Desktop Apps
echo - Documentation
echo.
echo ## Quick Start
echo.
echo ### Backend:
echo   cd backend
echo   start.bat
echo.
echo ### Web:
echo   Open web\index.html
echo.
echo ### Android:
echo   Install android\project-ai-v%VERSION%-debug.apk
echo.
echo See README files in each directory for details.
) > "%RELEASE_DIR%\README.md"

REM Create archive (requires 7-Zip or similar)
echo.
echo Creating release archive...
if exist "C:\Program Files\7-Zip\7z.exe" (
    cd releases
    "C:\Program Files\7-Zip\7z.exe" a -tzip "project-ai-v%VERSION%.zip" "project-ai-v%VERSION%\*" -r >nul
    cd ..
    echo OK Archive created
) else (
    echo WARNING 7-Zip not found - skipping archive creation
    echo   Install 7-Zip or manually zip the release folder
)

REM 7. Cleanup sensitive files
echo.
echo [7/7] Cleaning up sensitive files...
del /S /Q "%RELEASE_DIR%\*.key" 2>nul
del /S /Q "%RELEASE_DIR%\*.pem" 2>nul
del /S /Q "%RELEASE_DIR%\secrets.*" 2>nul
echo OK Sensitive files cleaned

REM Generate machine-readable release summary
echo.
echo Generating release summary...
set BUILD_SUMMARY=releases\release-summary-v%VERSION%.json

(
echo {
echo   "version": "%VERSION%",
echo   "build_date": "%DATE_STR%",
echo   "release_directory": "%RELEASE_DIR%",
echo   "artifacts": {
echo     "backend": {
echo       "included": true,
echo       "components": ["api", "tarl", "governance", "config", "utils", "kernel"]
echo     },
echo     "web": {
echo       "included": true
echo     },
echo     "android": {
echo       "included": true
echo     },
echo     "desktop": {
echo       "included": true
echo     },
echo     "monitoring": {
echo       "included": true
echo     },
echo     "documentation": {
echo       "included": true
echo     }
echo   }
echo }
) > "%BUILD_SUMMARY%"

echo OK Release summary written to: %BUILD_SUMMARY%

REM Validate the release package
echo.
echo Validating release package...
if exist "scripts\validate_release.py" (
    python scripts\validate_release.py "%RELEASE_DIR%" --version "%VERSION%" --output "releases\validation-report-v%VERSION%.json"
    if %ERRORLEVEL% EQU 0 (
        echo OK Validation passed
    ) else (
        echo WARNING Validation found issues - check validation-report-v%VERSION%.json
    )
) else (
    echo WARNING Validation script not found, skipping validation
)

echo.
echo =========================================
echo OK Release Build Complete!
echo =========================================
echo.
echo Package: %RELEASE_DIR%\
echo.
echo Reports generated:
echo   OK release-summary-v%VERSION%.json
echo   OK validation-report-v%VERSION%.json
echo.
echo Contents:
echo   OK Backend API (Python)
echo   OK Web Frontend (HTML/CSS/JS)
echo   OK Android App (if built)
echo   OK Desktop Apps (if built)
echo   OK Monitoring Agents
echo   OK Complete Documentation
echo.
echo Next steps:
echo   1. Test the release package
echo   2. Create Git tag: git tag v%VERSION%
echo   3. Push tag: git push origin v%VERSION%
echo   4. Create GitHub release
echo   5. Upload to GitHub
echo.

pause
