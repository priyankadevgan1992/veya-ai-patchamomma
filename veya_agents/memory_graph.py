import json
import sqlite3
import os
import re
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

class EvolvingMemoryGraph:
    """
    Evolving Memory Graph:
    Extracts, stores, and connects dynamic life nodes (family events, travel dates,
    work rhythms, recovery cycles, emotional markers) in the twin profile.
    """

    def __init__(self):
        pass

    def extract_facts(self, internal_uuid: str, user_message: str, current_persona_id: str) -> Dict[str, Any]:
        msg = user_message.lower()
        extracted = {}

        # 1. Family & Relationship Anchor Facts
        if any(w in msg for w in ["travel", "traveling", "trip", "flight", "away"]):
            if "husband" in msg or "partner" in msg or "spouse" in msg:
                extracted["spouse_status"] = "Traveling / Away"
            elif "father" in msg or "father-in-law" in msg or "dad" in msg:
                extracted["family_travel"] = "Father/In-law flight or arrival"
            else:
                extracted["travel_notice"] = "Upcoming travel mentioned"

        if any(w in msg for w in ["ptm", "parent teacher", "school", "exam", "revision", "kids", "children", "daughter", "son"]):
            extracted["family_priority"] = "Children education / exam support"

        if any(w in msg for w in ["medicine", "doctor", "hypertension", "bp", "pharmacy", "prescription"]):
            extracted["health_caregiving"] = "Elderly care / medicine schedule"

        # 2. Work Rhythms & Stress State Facts
        if any(w in msg for w in ["back to back", "hectic", "crazy", "overwhelmed", "exhausted", "burnout", "too much", "stress"]):
            extracted["work_stress_level"] = "High"
            extracted["current_state"] = "Needs evening boundary protection"
        elif any(w in msg for w in ["landed it", "went well", "great", "celebrate", "deal", "closed"]):
            extracted["work_stress_level"] = "Moderate"
            extracted["recent_achievement"] = "Major sync or deal achieved"
        elif any(w in msg for w in ["prep", "pitch", "deck", "presentation", "client sync"]):
            extracted["upcoming_milestone"] = "High-stakes presentation / client sync"

        # 3. Biology, Energy & Recovery Facts
        if any(w in msg for w in ["luteal", "cycle", "period", "cramps", "low energy", "fatigue", "tired"]):
            extracted["energy_rhythm"] = "Luteal / Low Energy Recovery Mode"
        elif any(w in msg for w in ["walk", "nature", "gentle", "yoga", "rest"]):
            extracted["recovery_preference"] = "Gentle restorative movement"
        elif any(w in msg for w in ["hiit", "gym", "heavy", "run"]):
            extracted["exercise_preference"] = "High intensity workouts"

        # Update Database Twin Profile Graph
        if extracted:
            conn = get_db()
            cursor = conn.cursor()
            
            # Update work stress level if present
            if "work_stress_level" in extracted:
                cursor.execute("UPDATE twin_profiles SET work_stress_level = ? WHERE internal_uuid = ?", (extracted["work_stress_level"], internal_uuid))
            
            # Fetch existing dynamic graph facts
            cursor.execute("SELECT relationship_health FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
            row = cursor.fetchone()
            current_facts = {}
            if row and row[0]:
                try:
                    current_facts = json.loads(row[0]) if row[0].startswith("{") else {"notes": row[0]}
                except Exception:
                    current_facts = {"notes": row[0]}

            current_facts.update(extracted)
            cursor.execute("UPDATE twin_profiles SET relationship_health = ? WHERE internal_uuid = ?", (json.dumps(current_facts), internal_uuid))
            conn.commit()
            conn.close()

        return extracted
