"""
Database Setup Script
Run this ONCE before starting the backend for the first time.
It creates all tables in the configured database automatically.

Usage:
    python setup_db.py
"""
import sys
import os

# Make sure we can import from the backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models  # noqa: F401 — must import so SQLAlchemy sees all table definitions

def setup():
    print("=" * 50)
    print("  AI Interview DB Setup")
    print("=" * 50)

    print("\n[1] Connecting to database...")
    try:
        with engine.connect() as conn:
            print("    [OK] Connection successful!")
    except Exception as e:
        print(f"    [FAIL] Connection failed: {e}")
        print("\n  Make sure:")
        print("  - Your DATABASE_URL in .env is correct")
        print("  - If using PostgreSQL, the server is running and the DB exists")
        sys.exit(1)

    print("\n[2] Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("    [OK] Tables created successfully!")
        print("\n  Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"    - {table.name}")
    except Exception as e:
        print(f"    [FAIL] Table creation failed: {e}")
        sys.exit(1)

    print("\n[3] Training initial hiring model...")
    try:
        from services.hiring_service import train_hiring_model
        train_hiring_model()
        print("    [OK] Hiring model trained and saved!")
    except Exception as e:
        print(f"    [FAIL] Model training failed: {e}")
        print("    (This is non-critical — model will auto-train on first API call)")

    print("\n" + "=" * 50)
    print("  Setup complete! You can now run:")
    print("  uvicorn main:app --reload")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    setup()
