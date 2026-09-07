@echo off
REM Start Flask backend with venv activated
start "Flask Backend" cmd /k "echo [BACKEND] Starting Flask... && cd backend && call ..\.venv\Scripts\activate.bat && python app.py"

REM Start React frontend
start "React Frontend" cmd /k "echo [FRONTEND] Starting React... && cd frontend && npm start"