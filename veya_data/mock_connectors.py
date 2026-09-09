import json
import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "veya_app.db")

def seed_mock_connectors():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    # 1. Google Calendar API Mock Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_google_calendar (
        event_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        summary TEXT,
        start_time TEXT,
        end_time TEXT,
        calendar_type fontTEXT,   -- "WORK", "FAMILY", "PERSONAL"
        attendees_count INTEGER
    );
    """)

    # 2. Health Connect Wearable API Mock Data (Sleep, HRV, Steps)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_health_connect (
        record_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        date TEXT,
        sleep_hours REAL,
        sleep_quality TEXT,       -- "RESTORATIVE", "DISRUPTED", "LIGHT"
        steps INTEGER,
        resting_hr INTEGER,
        hrv_ms INTEGER            -- Heart Rate Variability
    );
    """)

    # 3. Browser Search Intent API Mock Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_search_intent (
        search_id TEXT PRIMARY KEY,
        internal_uuid TEXT,
        query TEXT,
        category TEXT,           -- "PREP", "FINANCE", "WELLNESS", "FAMILY"
        timestamp TEXT
    );
    """)

    # Fetch User UUIDs
    cursor.execute("SELECT internal_uuid, persona_id FROM twin_profiles")
    users = cursor.fetchall()

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    for user_uuid, persona_id in users:
        if persona_id == "meera_pm":
            # Meera: 3 conflicting calendars, kids meeting, flight
            cursor.execute("INSERT OR REPLACE INTO mock_google_calendar VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"cal_m1_{user_uuid}", user_uuid, "Daughter's Parent-Teacher Meeting", f"{tomorrow} 16:00", f"{tomorrow} 17:00", "FAMILY", 2))
            cursor.execute("INSERT OR REPLACE INTO mock_google_calendar VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"cal_m2_{user_uuid}", user_uuid, "US Architecture Team Sync", f"{tomorrow} 18:00", f"{tomorrow} 19:00", "WORK", 8))
            cursor.execute("INSERT OR REPLACE INTO mock_google_calendar VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"cal_m3_{user_uuid}", user_uuid, "Father-in-law Flight Arrival", f"{tomorrow} 20:00", f"{tomorrow} 21:00", "FAMILY", 1))

            cursor.execute("INSERT OR REPLACE INTO mock_health_connect VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (f"hc_m_{user_uuid}", user_uuid, today, 7.5, "RESTORATIVE", 6200, 64, 58))

            cursor.execute("INSERT OR REPLACE INTO mock_search_intent VALUES (?, ?, ?, ?, ?)",
                (f"si_m_{user_uuid}", user_uuid, "quick healthy dinner recipes for 4", "FAMILY", today))

        elif persona_id == "priya_cycle":
            # Priya: Cycle Luteal phase, low HRV
            cursor.execute("INSERT OR REPLACE INTO mock_google_calendar VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"cal_p1_{user_uuid}", user_uuid, "UX Research Synthesis Focus", f"{tomorrow} 10:00", f"{tomorrow} 12:00", "WORK", 1))

            cursor.execute("INSERT OR REPLACE INTO mock_health_connect VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (f"hc_p_{user_uuid}", user_uuid, today, 6.2, "LIGHT", 4100, 72, 42))

        elif persona_id == "arjun_sales":
            # Arjun: Pre-salary stress, missing prep block
            cursor.execute("INSERT OR REPLACE INTO mock_google_calendar VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"cal_a1_{user_uuid}", user_uuid, "Enterprise Client Pitch", f"{tomorrow} 14:00", f"{tomorrow} 15:30", "WORK", 12))

            cursor.execute("INSERT OR REPLACE INTO mock_search_intent VALUES (?, ?, ?, ?, ?)",
                (f"si_a_{user_uuid}", user_uuid, "effective client presentation frameworks", "PREP", today))

    conn.commit()
    conn.close()
    print("Mock connectors for Google Calendar, Health Connect, and Search Intent initialized!")

if __name__ == "__main__":
    seed_mock_connectors()
