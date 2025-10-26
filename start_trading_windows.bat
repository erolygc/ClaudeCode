@echo off
REM Live Trading System - Windows Batch Launcher
REM Paper Trading Mode

echo ============================================================
echo    LIVE TRADING SYSTEM - PAPER MODE
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
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] yfinance not found, installing...
    pip install yfinance pandas numpy ta-lib-binary
)

echo [OK] All packages ready
echo.

REM Start trading system
echo ============================================================
echo Starting Live Trading System in PAPER MODE
echo Capital: 100,000 TL
echo Max Stocks: 20
echo Update Interval: 300 seconds (5 minutes)
echo ============================================================
echo.
echo Press Ctrl+C to stop the system
echo.

python run_live_trading.py --mode paper --capital 100000 --max-stocks 20 --interval 300

echo.
echo ============================================================
echo Trading system stopped
echo ============================================================
pause
