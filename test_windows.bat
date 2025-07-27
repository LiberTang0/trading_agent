@echo off
echo ============================================================
echo TRADING AGENT TESTS - WINDOWS COMPATIBLE
echo ============================================================
echo.

echo Running quick tests...
python run_tests.py --category quick

if %errorlevel% neq 0 (
    echo.
    echo [FAIL] Quick tests failed!
    pause
    exit /b 1
)

echo.
echo [PASS] Quick tests completed successfully!
echo.

echo Running integration tests...
python run_tests.py --category integration

if %errorlevel% neq 0 (
    echo.
    echo [FAIL] Integration tests failed!
    pause
    exit /b 1
)

echo.
echo [PASS] Integration tests completed successfully!
echo.

echo Running market hours tests...
python test_market_hours.py

if %errorlevel% neq 0 (
    echo.
    echo [FAIL] Market hours tests failed!
    pause
    exit /b 1
)

echo.
echo [PASS] Market hours tests completed successfully!
echo.

echo ============================================================
echo [PASS] ALL TESTS PASSED!
echo ============================================================
echo.
echo Your trading agent is ready for 24/7 operation!
echo.
pause 