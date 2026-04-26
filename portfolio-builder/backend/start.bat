@echo off
echo.
echo  =========================================
echo   Portfolio Builder - Starting Backend
echo  =========================================
echo.

cd /d "%~dp0"

REM Check if .env exists
IF NOT EXIST ".env" (
    echo  ERROR: .env file not found!
    echo  Make sure you are running this from the backend folder.
    pause
    exit /b 1
)

REM Check if python is available
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo  ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Install dependencies if needed
echo  Installing dependencies...
pip install -r requirements.txt -q

echo.
echo  Starting server at http://127.0.0.1:8000
echo  API docs at     http://127.0.0.1:8000/docs
echo.
echo  Press Ctrl+C to stop the server.
echo.

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause