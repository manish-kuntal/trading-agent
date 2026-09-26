content = '@echo off\n'
content += 'cd c:\\trading-agent\n'
content += 'start "Agent" cmd /k "cd c:\\trading-agent && call venv\\Scripts\\activate && python -m agent.main"\n'
content += 'timeout /t 3 /nobreak >nul\n'
content += 'start "API" cmd /k "cd c:\\trading-agent && call venv\\Scripts\\activate && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"\n'
content += 'timeout /t 4 /nobreak >nul\n'
content += 'start http://localhost:8000/docs\n'

with open(r'c:\trading-agent\START.bat', 'w') as f:
    f.write(content)

print("START.bat created!")
