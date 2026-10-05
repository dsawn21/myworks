@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py "pasword manager.py"
) else (
    python "pasword manager.py"
)

echo.
pause
