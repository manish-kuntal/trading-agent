@echo off
call venv\Scripts\activate.bat
echo Starting Trading Agent (paper mode by default)...
echo Press Ctrl+C to stop.
echo.
python -m agent.main
pause
