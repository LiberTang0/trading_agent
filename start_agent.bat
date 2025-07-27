@echo off
echo Starting Trading Agent 24/7...
echo.
echo This will run the trading agent continuously with automatic restart.
echo Press Ctrl+C to stop the agent.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "trading_agent_main.py" (
    echo Error: trading_agent_main.py not found
    pause
    exit /b 1
)

if not exist "trading_agent_core.py" (
    echo Error: trading_agent_core.py not found
    pause
    exit /b 1
)

if not exist "random_forest_model.joblib" (
    echo Error: random_forest_model.joblib not found
    pause
    exit /b 1
)

if not exist "scaler.joblib" (
    echo Error: scaler.joblib not found
    pause
    exit /b 1
)

echo All required files found. Starting agent...
echo.

REM Start the agent runner
python run_agent_24_7.py

echo.
echo Trading agent has stopped.
pause 