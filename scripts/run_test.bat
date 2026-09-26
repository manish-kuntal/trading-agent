@echo off
call venv\Scripts\activate.bat
echo Running connection test...
python test_connection.py
pause
