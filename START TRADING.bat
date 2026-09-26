@echo off
cd C:\Users\manis\trading-agent
start "Agent" cmd /k "cd C:\Users\manis\trading-agent && call venv\Scripts\activate && python -m agent.main"
timeout /t 3 /nobreak >nul
start "API" cmd /k "cd C:\Users\manis\trading-agent && call venv\Scripts\activate && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"
timeout /t 4 /nobreak >nul
start http://localhost:8000/docs
