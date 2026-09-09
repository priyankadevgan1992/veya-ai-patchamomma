import sqlite3
import uuid
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "veya_data", "veya_app.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_vaibhav():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    username = "vaibhav"
    email = "vaibhav@veya.ai"
    cursor.execute("SELECT internal_uuid FROM user_accounts WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if row:
        user_uuid = row[0]
        # Clean up existing to re-seed cleanly
        cursor.execute("DELETE FROM twin_profiles WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM household_profiles WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM notifications WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM tomorrow_plans WHERE internal_uuid = ?", (user_uuid,))
    else:
        user_uuid = f"uuid_usr_{os.urandom(6).hex()}"
        cursor.execute(
            "INSERT INTO user_accounts (username, email, password_hash, internal_uuid) VALUES (?, ?, ?, ?)",
            (username, email, hash_password("password123"), user_uuid)
        )
    
    # 1. Twin Profile
    cursor.execute("""
    INSERT INTO twin_profiles (
        internal_uuid, persona_id, persona_name, life_anchor, gender_identity,
        household_members, work_stress_level, relationship_health, biological_phase,
        calendars_connected, wearable_connected, twin_maturity_weeks
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_uuid,
        "vaibhav_exec",
        "Vaibhav",
        "Optimize time for learning, kid, and health despite a meeting-heavy schedule. Prioritize Work > Learning > Kid > Wife > Health.",
        "Male",
        3,
        "High",
        "Moderate",
        "Normal",
        1,
        1,
        2
    ))
    
    # 2. Household Orbit
    cursor.execute("""
    INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context, importance_percent)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), user_uuid, "Rohan", "10-year old kid", "Loves playing football, needs help with math", 80))
    
    cursor.execute("""
    INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context, importance_percent)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), user_uuid, "Priya", "Wife", "Working professional, busy schedule", 70))
    
    # 3. Dummy Notifications/Insights
    n1_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO notifications (id, internal_uuid, text, is_read) VALUES (?, ?, ?, ?)",
        (n1_id, user_uuid, "Your Energy Balance is 45/100 today. 6 back-to-back meetings are draining you.", 0)
    )
    
    n2_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO notifications (id, internal_uuid, text, is_read) VALUES (?, ?, ?, ?)",
        (n2_id, user_uuid, "You are in a relational deficit with Rohan. Consider blocking 30 mins tonight.", 0)
    )

    conn.commit()
    conn.close()
    print(f"Vaibhav seeded successfully with UUID: {user_uuid}")

if __name__ == '__main__':
    seed_vaibhav()
