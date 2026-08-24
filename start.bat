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
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Installing dependencies...
venv\Scripts\python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Backend dependencies installation failed. Exiting...
    exit /b %errorlevel%
)

echo.
echo [3/3] Starting Production Server...
echo The application will be available at http://localhost:8000
venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
