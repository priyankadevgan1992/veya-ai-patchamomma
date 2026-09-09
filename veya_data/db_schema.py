import sqlite3
import json
import uuid
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "veya_app.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Isolated Auth Mapping Table (PII isolated)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auth_vault (
        internal_uuid TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        phone_number TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Digital Twin Profiles (Indexed strictly by internal_uuid)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS twin_profiles (
        internal_uuid TEXT PRIMARY KEY,
        persona_id TEXT,
        persona_name TEXT,
        life_anchor TEXT,
        gender_identity TEXT,
        household_members INTEGER,
        work_stress_level TEXT,
        relationship_health TEXT,
        biological_phase TEXT,
        calendars_connected INTEGER,
        wearable_connected INTEGER,
        twin_maturity_weeks INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 3. Persistent Conversation Thread Memories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_memories (
        memory_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        role TEXT,
        content TEXT,
        extracted_facts TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 4. Tomorrow Feasibility Plans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tomorrow_plans (
        plan_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        plan_date TEXT,
        action_items TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 5. User Notifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        text TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 6. Household Orbit Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS household_profiles (
        profile_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        person_name TEXT,
        relationship_type TEXT,
        key_context TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 7. Action Outcomes (Feedback Loop)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS action_outcomes (
        id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        action_id TEXT,
        action_title TEXT,
        situation_hash TEXT,
        state_before TEXT,
        explicit_score INTEGER,
        implicit_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    # 8. Contextual Reminders (Intent-based memory)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contextual_reminders (
        id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        intent_text TEXT,
        proposed_time TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(internal_uuid) REFERENCES auth_vault(internal_uuid)
    );
    """)

    conn.commit()
    conn.close()

def get_or_create_user(email: str, phone: str = None, persona_id: str = "meera_pm"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT internal_uuid FROM auth_vault WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row:
        user_uuid = row[0]
    else:
        user_uuid = f"v_{uuid.uuid4().hex[:12]}"
        cursor.execute(
            "INSERT INTO auth_vault (internal_uuid, email, phone_number) VALUES (?, ?, ?)",
            (user_uuid, email, phone)
        )
        conn.commit()

        # Seed twin profile from personas.json template
        personas_file = os.path.join(os.path.dirname(__file__), "personas.json")
        if os.path.exists(personas_file):
            with open(personas_file, "r") as f:
                personas = json.load(f)
                template = next((p for p in personas if p["persona_id"] == persona_id), personas[0])
                
                cursor.execute("""
                INSERT OR REPLACE INTO twin_profiles (
                    internal_uuid, persona_id, persona_name, life_anchor, gender_identity,
                    household_members, work_stress_level, relationship_health, biological_phase,
                    calendars_connected, wearable_connected, twin_maturity_weeks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_uuid,
                    template["persona_id"],
                    template["name"],
                    template["life_anchor"],
                    template["gender_identity"],
                    template["household_members"],
                    template["work_stress_level"],
                    template["relationship_health"],
                    template.get("biological_phase", "Normal"),
                    1 if template["calendars_connected"] else 0,
                    1 if template["wearable_connected"] else 0,
                    template["twin_maturity_weeks"]
                ))
                conn.commit()

    conn.close()
    return user_uuid

if __name__ == "__main__":
    init_db()
    test_uuid = get_or_create_user("meera@gmail.com", persona_id="meera_pm")
    print(f"Database initialized cleanly. Test User UUID: {test_uuid}")
