@echo off
REM Live Trading Monitor - Windows Batch Launcher

echo ============================================================
echo    LIVE TRADING MONITOR - DASHBOARD
echo ============================================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Start monitoring dashboard
echo ============================================================
echo Starting Live Trading Monitor Dashboard
echo Refresh Interval: 60 seconds
echo ============================================================
echo.
echo Press Ctrl+C to stop the monitor
echo.

python run_monitor.py --dashboard --refresh 60

echo.
echo ============================================================
echo Monitor stopped
echo ============================================================
pause
