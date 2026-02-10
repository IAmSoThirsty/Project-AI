@echo off
:: Legion Mini Auto-Launch Wizard
:: Opens installation GUI automatically when USB is inserted

title Legion Mini Installation Wizard
cls

echo.
echo ================================================
echo    LEGION MINI - Personal AI Assistant
echo ================================================
echo.
echo    Launching installation wizard...
echo.

:: Launch the HTML wizard in default browser
start "" "autorun_wizard.html"

:: Keep window open briefly
timeout /t 2 /nobreak >nul

exit
