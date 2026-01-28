@echo off
REM Create complete v1.0.0 release package with all platforms (Windows)

setlocal enabledelayedexpansion

set VERSION=1.0.0
set RELEASE_DIR=releases\project-ai-v%VERSION%
set DATE_STR=%date:~-4%-%date:~4,2%-%date:~7,2%

echo =========================================
echo Project AI v%VERSION% Release Builder
echo =========================================
echo Date: %DATE_STR%
echo.

REM Create release directories
mkdir "%RELEASE_DIR%\backend" 2>nul
mkdir "%RELEASE_DIR%\web" 2>nul
mkdir "%RELEASE_DIR%\android" 2>nul
mkdir "%RELEASE_DIR%\desktop" 2>nul
mkdir "%RELEASE_DIR%\docs" 2>nul

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

REM 5. Documentation
echo [5/5] Copying Documentation...
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

REM Create archive (requires 7-zip or similar)
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

echo.
echo =========================================
echo OK Release Build Complete!
echo =========================================
echo.
echo Package: %RELEASE_DIR%\
echo.
echo Contents:
echo   OK Backend API (Python)
echo   OK Web Frontend (HTML/CSS/JS)
echo   OK Android App (if built)
echo   OK Desktop Apps (if built)
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
