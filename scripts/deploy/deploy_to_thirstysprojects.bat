@echo off
REM ========================================
REM Deploy Project AI to thirstysprojects.com
REM ========================================

echo.
echo ========================================
echo Project AI - Deploy to thirstysprojects.com
echo ========================================
echo.

REM Check if web/index.html exists
if not exist "web\index.html" (
    echo ERROR: web\index.html not found!
    echo Please run this script from the Project-AI root directory.
    pause
    exit /b 1
)

echo Options:
echo.
echo 1. Deploy via FTP (requires FTP credentials)
echo 2. Copy to local web server (e.g., XAMPP, WAMP)
echo 3. Create deployment package (ZIP)
echo 4. Show deployment guide
echo 5. Exit
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" goto ftp_deploy
if "%choice%"=="2" goto local_deploy
if "%choice%"=="3" goto create_package
if "%choice%"=="4" goto show_guide
if "%choice%"=="5" goto end

echo Invalid choice. Exiting.
pause
exit /b 1

:ftp_deploy
echo.
echo ========================================
echo FTP Deployment
echo ========================================
echo.
echo Enter FTP credentials for thirstysprojects.com:
echo (Leave blank and press Enter to skip)
echo.

set /p FTP_HOST="FTP Host (e.g., ftp.thirstysprojects.com): "
if "%FTP_HOST%"=="" goto end

set /p FTP_USER="FTP Username: "
if "%FTP_USER%"=="" goto end

set /p FTP_PASS="FTP Password: "
if "%FTP_PASS%"=="" goto end

set /p REMOTE_PATH="Remote path (e.g., /public_html/): "
if "%REMOTE_PATH%"=="" set REMOTE_PATH=/public_html/

echo.
echo Uploading web/index.html to %FTP_HOST%%REMOTE_PATH%index.html...
echo.

REM Using curl for FTP upload
curl -T "web\index.html" ftp://%FTP_HOST%%REMOTE_PATH%index.html --user %FTP_USER%:%FTP_PASS%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Deployment Complete!
    echo ========================================
    echo.
    echo Your site should now be live at:
    echo https://thirstysprojects.com
    echo.
    echo Please verify:
    echo - Charter section loads
    echo - Timer starts automatically
    echo - Checkboxes work after 2 minutes
    echo.
) else (
    echo.
    echo ERROR: FTP upload failed!
    echo Please check your credentials and try again.
    echo.
)

pause
goto end

:local_deploy
echo.
echo ========================================
echo Local Web Server Deployment
echo ========================================
echo.
echo Enter the path to your local web server root:
echo Examples:
echo   C:\xampp\htdocs
echo   C:\wamp64\www
echo   C:\inetpub\wwwroot
echo.

set /p WEB_ROOT="Web server root path: "
if "%WEB_ROOT%"=="" goto end

if not exist "%WEB_ROOT%" (
    echo ERROR: Directory does not exist: %WEB_ROOT%
    pause
    goto end
)

echo.
echo Copying web/index.html to %WEB_ROOT%\...
copy /Y "web\index.html" "%WEB_ROOT%\index.html"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! File Copied!
    echo ========================================
    echo.
    echo Local URL: http://localhost
    echo.
    echo To deploy to thirstysprojects.com, you'll need to:
    echo 1. Upload %WEB_ROOT%\index.html to your hosting
    echo 2. Or use FTP option (option 1)
    echo.
) else (
    echo ERROR: Copy failed!
)

pause
goto end

:create_package
echo.
echo ========================================
echo Creating Deployment Package
echo ========================================
echo.

set PACKAGE_NAME=project-ai-web-deploy.zip

if exist "%PACKAGE_NAME%" del "%PACKAGE_NAME%"

echo Creating ZIP package: %PACKAGE_NAME%...
powershell -Command "Compress-Archive -Path 'web\index.html' -DestinationPath '%PACKAGE_NAME%'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Package Created!
    echo ========================================
    echo.
    echo Package: %PACKAGE_NAME%
    echo.
    echo To deploy:
    echo 1. Extract %PACKAGE_NAME%
    echo 2. Upload index.html to your web hosting
    echo 3. Place in public_html/ or www/ directory
    echo.
    echo Or use cPanel File Manager:
    echo 1. Login to cPanel
    echo 2. Open File Manager
    echo 3. Navigate to public_html/
    echo 4. Upload %PACKAGE_NAME%
    echo 5. Extract and move index.html to root
    echo.
) else (
    echo ERROR: Failed to create package!
)

pause
goto end

:show_guide
echo.
echo ========================================
echo Deployment Guide
echo ========================================
echo.
echo Full deployment guide available in:
echo   DEPLOY_TO_THIRSTYSPROJECTS.md
echo.
echo Quick Steps:
echo.
echo METHOD 1: cPanel / File Manager
echo   1. Login to hosting cPanel
echo   2. Open File Manager
echo   3. Navigate to public_html/
echo   4. Upload web/index.html
echo   5. Rename to index.html (if needed)
echo   6. Set permissions: 644
echo   7. Visit https://thirstysprojects.com
echo.
echo METHOD 2: FTP (Use option 1 above)
echo   - Requires FTP client or this script
echo.
echo METHOD 3: Netlify/Vercel
echo   1. Drag web/ folder to netlify.com
echo   2. Add custom domain: thirstysprojects.com
echo   3. Configure DNS
echo.
echo For detailed instructions, see:
echo   DEPLOY_TO_THIRSTYSPROJECTS.md
echo.

pause
goto end

:end
echo.
echo ========================================
echo Deployment script finished.
echo ========================================
echo.
echo For detailed deployment instructions, see:
echo   DEPLOY_TO_THIRSTYSPROJECTS.md
echo.
echo Your site: https://thirstysprojects.com
echo.
