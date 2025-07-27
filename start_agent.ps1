# Trading Agent 24/7 Starter Script
# Run this script to start the trading agent continuously

Write-Host "Starting Trading Agent 24/7..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required files exist
$requiredFiles = @(
    "trading_agent_main.py",
    "trading_agent_core.py", 
    "random_forest_model.joblib",
    "scaler.joblib"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "Error: $file not found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "All required files found." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists and activate it if present
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
}

# Install/upgrade required packages
Write-Host "Checking and installing required packages..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet

Write-Host "Starting trading agent..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the agent." -ForegroundColor Yellow
Write-Host ""

# Start the agent runner
try {
    python run_agent_24_7.py
} catch {
    Write-Host "Error running trading agent: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Trading agent has stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
} 