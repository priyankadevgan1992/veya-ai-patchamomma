import json
import sqlite3
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

class ContextAgent:
    """
    Context Agent: Aggregates multi-source context with Adaptive Degradation:
    1. Reads Live Google Calendar if OAuth credentials/token exist.
    2. Fallback to mock tables if live is not connected.
    3. Seamlessly degrades to Conversational Memory if both are absent.
    """

    def __init__(self, name: str = "context_agent"):
        self.name = name

    def get_unified_context(self, internal_uuid: str) -> Dict[str, Any]:
        conn = get_db()
        cursor = conn.cursor()

        # 1. Fetch Twin Profile
        cursor.execute("SELECT * FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
        profile_row = cursor.fetchone()
        profile = dict(profile_row) if profile_row else {}

        # 2. Fetch Chat Memories
        cursor.execute("""
            SELECT role, content, extracted_facts, timestamp 
            FROM chat_memories 
            WHERE internal_uuid = ? 
            ORDER BY timestamp DESC LIMIT 10
        """, (internal_uuid,))
        memories = [dict(r) for r in cursor.fetchall()]
        memories.reverse()

        # 2.5 Fetch Household Orbit Profiles
        cursor.execute("SELECT person_name, relationship_type, key_context, importance_percent FROM household_profiles WHERE internal_uuid = ?", (internal_uuid,))
        household_members = [dict(r) for r in cursor.fetchall()]

        # 3. Fetch Google Calendar (Attempt Live Connector first)
        calendar_events = []
        is_live_google = False
        try:
            from veya_connectors.google_calendar import GoogleCalendarConnector
            gcal = GoogleCalendarConnector()
            if gcal.is_connected():
                calendar_events = gcal.fetch_upcoming_events(max_results=8)
                is_live_google = True
        except Exception as e:
            pass

        # Fallback to Mock Table if Live is not connected
        if not calendar_events:
            try:
                cursor.execute("SELECT * FROM mock_google_calendar WHERE internal_uuid = ?", (internal_uuid,))
                calendar_events = [dict(r) for r in cursor.fetchall()]
            except sqlite3.OperationalError:
                calendar_events = []

        # 4. Fetch Wearables / Health Connect
        wearable_metrics = {}
        try:
            cursor.execute("SELECT * FROM mock_health_connect WHERE internal_uuid = ?", (internal_uuid,))
            wearable_rows = [dict(r) for r in cursor.fetchall()]
            if wearable_rows:
                wearable_metrics = dict(wearable_rows[0])
        except sqlite3.OperationalError:
            wearable_metrics = {}

        # 5. Fetch Search Intent
        searches = []
        try:
            cursor.execute("SELECT * FROM mock_search_intent WHERE internal_uuid = ?", (internal_uuid,))
            searches = [dict(r) for r in cursor.fetchall()]
        except sqlite3.OperationalError:
            searches = []

        conn.close()

        has_calendar = bool(calendar_events)
        has_wearable = bool(wearable_metrics)
        source_mode = "LIVE_GOOGLE_CALENDAR_CONNECTED" if is_live_google else (
            "MULTI_SOURCE_CONNECTED" if (has_calendar and has_wearable) else (
                "CALENDAR_ONLY" if has_calendar else "CONVERSATIONAL_ONLY"
            )
        )

        return {
            "internal_uuid": internal_uuid,
            "persona_name": profile.get("persona_name", "Friend"),
            "persona_id": profile.get("persona_id", "meera_pm"),
            "life_anchor": profile.get("life_anchor", "Balance & Peace"),
            "work_stress_level": profile.get("work_stress_level", "Moderate"),
            "biological_phase": profile.get("biological_phase", "Normal"),
            "source_mode": source_mode,
            "is_live_google_calendar": is_live_google,
            "calendar_connected": has_calendar,
            "wearable_connected": has_wearable,
            "calendar_events": calendar_events,
            "wearable_metrics": wearable_metrics,
            "search_intents": searches,
            "recent_chat_history": memories,
            "household_members": household_members
        }

def get_user_life_context(internal_uuid: str) -> str:
    agent = ContextAgent()
    context = agent.get_unified_context(internal_uuid)
    return json.dumps(context)
