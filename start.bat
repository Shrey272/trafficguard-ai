@echo off
echo ===================================================
echo Starting TrafficGuard AI in Production Mode
echo ===================================================

echo.
echo [1/3] Building frontend...
cd frontend
call npm install
call npm run build
if %errorlevel% neq 0 (
    echo Frontend build failed. Exiting...
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Setting up backend environment...
cd backend

rem Locate Python 3.14 executable
set "PYTHON_CMD=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
)

if not exist venv (
    echo Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
)
echo Installing dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Backend dependencies installation failed. Exiting...
    exit /b %errorlevel%
)

echo.
echo [3/3] Starting Production Server...
echo The application will be available at http://localhost:8000
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000

