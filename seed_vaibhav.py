import sqlite3
import uuid
import os
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "veya_data", "veya_app.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_user(conn, username, email, persona_id, name, anchor, gender, members, stress, rel_health, maturity, household_data, notifications):
    cursor = conn.cursor()
    cursor.execute("SELECT internal_uuid FROM user_accounts WHERE username = ? OR email = ?", (username, email))
    row = cursor.fetchone()
    
    if row:
        user_uuid = row[0]
        # Clean up existing to re-seed cleanly
        cursor.execute("DELETE FROM twin_profiles WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM household_profiles WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM notifications WHERE internal_uuid = ?", (user_uuid,))
        cursor.execute("DELETE FROM tomorrow_plans WHERE internal_uuid = ?", (user_uuid,))
    else:
        if username == 'meera':
            user_uuid = "uuid_test_enriched_001"
        elif username == 'vaibhav':
            # Hardcoded to match the frontend LocalStorage cache
            user_uuid = "uuid_usr_cbc77f965f48"
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
        calendars_connected, wearable_connected, twin_maturity_weeks, onboarding_completed
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_uuid, persona_id, name, anchor, gender, members, stress, rel_health, "Normal", 1, 1, maturity, 1
    ))
    
    # 2. Household Orbit
    for hd in household_data:
        cursor.execute("""
        INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context, importance_percent)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_uuid, hd[0], hd[1], hd[2], hd[3]))
        
    # 3. Dummy Notifications
    for notif in notifications:
        cursor.execute(
            "INSERT INTO notifications (id, internal_uuid, text, is_read) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_uuid, notif, 0)
        )
        
    return user_uuid


def seed_vaibhav():
    conn = sqlite3.connect(DB_PATH)
    
    # Seed Vaibhav
    seed_user(
        conn=conn,
        username="vaibhav",
        email="vaibhav@veya.ai",
        persona_id="vaibhav_exec",
        name="Vaibhav",
        anchor="Optimize time for learning, kid, and health despite a meeting-heavy schedule. Prioritize Work > Learning > Kid > Wife > Health.",
        gender="Male",
        members=3,
        stress="High",
        rel_health="Moderate",
        maturity=2,
        household_data=[
            ("Rohan", "10-year old kid", "Loves playing football, needs help with math", 80),
            ("Priya", "Wife", "Working professional, busy schedule", 70)
        ],
        notifications=[
            "Your Energy Balance is 42/100 today. 5.5 hours of meetings are draining you.",
            "You are in a relational deficit with Rohan. Consider blocking 30 mins tonight."
        ]
    )
    
    # Seed Meera
    seed_user(
        conn=conn,
        username="meera",
        email="test@veya.ai",
        persona_id="meera_pm",
        name="Meera",
        anchor="Protect family dinner & focus time amid heavy calendar meetings",
        gender="Female",
        members=4,
        stress="High",
        rel_health=json.dumps({"spouse_status": "Traveling / Away", "family_priority": "Daughter school exams"}),
        maturity=5,
        household_data=[
            ("Aanya", "Daughter", "Has school exams coming up", 90),
            ("Rahul", "Husband", "Currently traveling for work", 85)
        ],
        notifications=[
            "Aanya's school exams start next week. Want me to block study time this weekend?",
            "Your sleep has been optimal (8.2 hrs/night). Good job!"
        ]
    )
    
    conn.commit()
    conn.close()
    print("Seed complete for Vaibhav and Meera.")

if __name__ == '__main__':
    seed_vaibhav()
