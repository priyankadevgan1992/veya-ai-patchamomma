@echo off
echo ===================================================
echo 🚀 Starting Veya AI Life Companion...
echo ===================================================

echo [1/3] Checking environment...
if not exist "veya_data\veya_app.db" (
    echo [!] Database not found, initializing...
    python -c "from veya_data.db_schema import init_db; init_db()"
    python -c "from veya_data.auth_db import init_auth_tables; init_auth_tables()"
    echo [OK] Database initialized.
) else (
    echo [OK] Database exists.
)

echo [2/3] Checking dependencies...
python -m pip install -q fastapi uvicorn python-dotenv google-genai websockets || echo [!] Warning: Could not install/verify some dependencies.

echo [3/3] Starting FastAPI Backend Server...
echo ===================================================
echo 🌐 Web UI will be available at: http://127.0.0.1:8080/app/index.html
echo 🛑 Press CTRL+C to stop the server.
echo ===================================================

python -m uvicorn veya_server.main:app --host 0.0.0.0 --port 8080 --reload
