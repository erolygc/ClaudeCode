@echo off
REM Windows Dashboard Launcher

echo ====================================================================
echo                 WEB DASHBOARD BASLATIYOR...
echo ====================================================================
echo.

cd /d "%~dp0"

python run_dashboard.py --host 127.0.0.1 --port 5000

pause
