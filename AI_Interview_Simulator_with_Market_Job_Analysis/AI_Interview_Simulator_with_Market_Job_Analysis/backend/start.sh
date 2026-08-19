#!/bin/bash
echo "============================================"
echo "  AI Interview Backend — Quick Start"
echo "============================================"
echo ""

echo "[1] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run:  python3 -m venv venv"
    echo "Then run:    pip install -r requirements.txt"
    exit 1
fi
echo "    Done."

echo ""
echo "[2] Setting up database..."
python setup_db.py
if [ $? -ne 0 ]; then
    echo "ERROR: Database setup failed!"
    echo "Make sure .env is configured correctly."
    exit 1
fi

echo ""
echo "[3] Starting FastAPI backend..."
echo "    URL:  http://localhost:8000"
echo "    Docs: http://localhost:8000/docs"
echo "    Press CTRL+C to stop."
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
