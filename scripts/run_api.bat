@echo off
call venv\Scripts\activate.bat
echo Starting API server at http://localhost:8000
echo Dashboard docs at http://localhost:8000/docs
echo.
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause
