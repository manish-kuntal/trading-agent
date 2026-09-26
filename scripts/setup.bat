@echo off
echo.
echo ============================================
echo  Trading Agent - Windows Setup
echo  Requires: Python 3.11
echo ============================================
echo.

:: Check Python 3.11
python --version 2>nul | findstr "3.11" >nul
if errorlevel 1 (
    echo [ERROR] Python 3.11 required.
    echo Download: https://www.python.org/downloads/release/python-3119/
    echo Make sure to check "Add to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python 3.11 found.

:: Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo [OK] Virtual environment ready.

:: Activate and install
echo Installing dependencies (this takes 2-5 minutes)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

:: Create .env from example
if not exist .env (
    copy .env.example .env >nul
    echo.
    echo [ACTION REQUIRED] Fill in your credentials in .env:
    echo   1. ANGEL_API_KEY
    echo   2. ANGEL_CLIENT_ID
    echo   3. ANGEL_PASSWORD
    echo   4. ANGEL_TOTP_SECRET
    echo.
)

:: Create necessary directories
if not exist logs       mkdir logs
if not exist ml\models  mkdir ml\models
if not exist data\cache mkdir data\cache

echo.
echo ============================================
echo  Setup complete!
echo ============================================
echo  Steps:
echo    1. Edit .env with your Angel One credentials
echo    2. Run:  scripts\run_test.bat
echo    3. Run:  scripts\run_agent.bat
echo ============================================
echo.
pause
