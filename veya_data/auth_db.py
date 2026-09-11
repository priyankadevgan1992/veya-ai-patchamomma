import sqlite3
import hashlib
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Real User Accounts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT NOT NULL,
            internal_uuid TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(internal_uuid) REFERENCES twin_profiles(internal_uuid)
        )
    """)

    # 2. Add onboarding_completed flag to twin_profiles if not exists
    cursor.execute("PRAGMA table_info(twin_profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    if "onboarding_completed" not in columns:
        cursor.execute("ALTER TABLE twin_profiles ADD COLUMN onboarding_completed INTEGER DEFAULT 0")

    conn.commit()

    # 3. Seed / Ensure Enriched Test Profile exists (Real Live Account)
    test_email = "test@veya.ai"
    test_pass = hash_password("password123")
    test_uuid = "uuid_test_enriched_001"

    cursor.execute("SELECT email FROM user_accounts WHERE email = ?", (test_email,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT OR REPLACE INTO twin_profiles 
            (internal_uuid, persona_id, persona_name, life_anchor, gender_identity, household_members, work_stress_level, relationship_health, calendars_connected, wearable_connected, twin_maturity_weeks, onboarding_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_uuid,
            "meera_pm",
            "Meera Sharma",
            "Protect family dinner & focus time amid heavy calendar meetings",
            "Female",
            4,
            "High",
            json.dumps({"spouse_status": "Traveling / Away", "family_priority": "Daughter school exams"}),
            1,
            1,
            5,
            1
        ))

        cursor.execute("""
            INSERT INTO user_accounts (username, email, password_hash, internal_uuid)
            VALUES (?, ?, ?, ?)
        """, ('meera', test_email, test_pass, test_uuid))

        print(f"Created enriched test account: {test_email}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_auth_tables()
    print("Auth schema initialized successfully!")
