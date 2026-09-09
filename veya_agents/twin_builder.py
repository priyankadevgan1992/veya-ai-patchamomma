import json
import sqlite3
import os
import re
from typing import Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

class TwinBuilderAgent:
    """
    Twin Builder Agent: Extracts life facts, anchors, household shifts,
    and stress states during conversation and updates twin_profiles.
    """

    def __init__(self, name: str = "twin_builder_agent"):
        self.name = name

    def extract_and_save_facts(self, internal_uuid: str, user_message: str) -> Dict[str, Any]:
        msg_lower = user_message.lower()
        extracted = {}

        # Detect family / household context
        if "travel" in msg_lower or "husband" in msg_lower or "trip" in msg_lower:
            extracted["household_context"] = "Spouse traveling"
        if "daughter" in msg_lower or "ptm" in msg_lower or "school" in msg_lower or "exam" in msg_lower:
            extracted["family_focus"] = "Child school / exam commitments"

        # Detect stress signals
        if any(w in msg_lower for w in ["stressed", "overwhelmed", "exhausted", "too much", "hectic", "crazy day"]):
            extracted["work_stress_level"] = "High"
        elif any(w in msg_lower for w in ["good", "peaceful", "calm", "smooth", "landed it"]):
            extracted["work_stress_level"] = "Moderate"

        if extracted:
            conn = get_db()
            cursor = conn.cursor()
            if "work_stress_level" in extracted:
                cursor.execute("UPDATE twin_profiles SET work_stress_level = ? WHERE internal_uuid = ?", (extracted["work_stress_level"], internal_uuid))
            conn.commit()
            conn.close()

        return extracted
