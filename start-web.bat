@echo off
echo Starting FastAPI backend...
start "FastAPI" cmd /k "python api_server.py"

timeout /t 3 /nobreak >nul

echo Starting Next.js frontend...
cd web
start "Next.js" cmd /k "npm run dev"

echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause

