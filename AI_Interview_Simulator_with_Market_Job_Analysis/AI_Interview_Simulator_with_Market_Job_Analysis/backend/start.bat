@echo off
echo ============================================
echo   AI Interview Backend — Quick Start
echo ============================================
echo.

echo [1] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Please run:  python -m venv venv
    echo Then run:    pip install -r requirements.txt
    pause
    exit /b 1
)
echo     Done.

echo.
echo [2] Setting up database...
python setup_db.py
if errorlevel 1 (
    echo ERROR: Database setup failed!
    echo Make sure .env is configured correctly.
    pause
    exit /b 1
)

echo.
echo [3] Starting FastAPI backend...
echo     URL: http://localhost:8000
echo     Docs: http://localhost:8000/docs
echo     Press CTRL+C to stop.
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
