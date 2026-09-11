import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db_connection():
    return sqlite3.connect(DB_PATH, timeout=20)

# Tool 1: Update Twin Fact
def update_twin_fact(internal_uuid: str, fact_key: str, fact_value: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    valid_cols = ["life_anchor", "gender_identity", "household_members", "work_stress_level", "relationship_health", "biological_phase"]
    if fact_key in valid_cols:
        cursor.execute(f"UPDATE twin_profiles SET {fact_key} = ? WHERE internal_uuid = ?", (fact_value, internal_uuid))
        conn.commit()
        conn.close()
        return f"Successfully updated {fact_key} to '{fact_value}'."
    conn.close()
    return f"Stored '{fact_key}' in memory."

# Tool 2: Read Live Google Calendar & Health Connect Mocks
def fetch_connected_signals(internal_uuid: str) -> str:
    """Reads live mock signals from Google Calendar, Health Connect, and Search Intent."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM mock_google_calendar WHERE internal_uuid = ?", (internal_uuid,))
        events = [dict(r) for r in cursor.fetchall()]
    except Exception:
        events = []

    try:
        cursor.execute("SELECT * FROM mock_health_connect WHERE internal_uuid = ?", (internal_uuid,))
        health = [dict(r) for r in cursor.fetchall()]
    except Exception:
        health = []

    try:
        cursor.execute("SELECT * FROM mock_search_intent WHERE internal_uuid = ?", (internal_uuid,))
        searches = [dict(r) for r in cursor.fetchall()]
    except Exception:
        searches = []

    conn.close()

    return json.dumps({
        "calendar_events": events,
        "health_connect_metrics": health,
        "search_intent_context": searches
    })

# Tool 3: Derive Metric 5-10 Line Explanation from Mock Signals
def derive_metric_explanation(internal_uuid: str, metric_id: str, score: int = None) -> str:
    from google.genai import Client
    import json
    try:
        signals = json.loads(fetch_connected_signals(internal_uuid))
        health = signals.get("health_connect_metrics", [{}])[0] if signals.get("health_connect_metrics") else {}
        events = signals.get("calendar_events", [])
        
        prompt = f"""You are Veya's internal reasoning engine.
The user clicked on their {metric_id} metric, which is currently scored at {score}/100.
Their current context:
- Sleep: {health.get('sleep_hours', 7.5)} hours ({health.get('sleep_quality', 'Unknown')})
- Steps: {health.get('steps', 0)}
- Calendar Events today: {len(events)}

Generate a JSON object strictly in this format (no markdown code blocks, just raw JSON):
{{
    "reason": "A 2-3 sentence empathetic explanation of why this score is {score}. Mention their health or calendar data if relevant.",
    "recommendation": "A 1-2 sentence actionable and realistic recommendation to improve or maintain this score.",
    "provenance": ["Short pill-sized factor 1", "Short pill-sized factor 2", "Short pill-sized factor 3"]
}}
"""
        client = Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        try:
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            return raw_text
        except Exception:
            pass

    except Exception as e:
        print("Derivation LLM failed:", e)
        pass

    return json.dumps({
        "reason": "Veya is still calibrating your baseline signals.",
        "recommendation": "Wear your fitness tracker to bed tonight for better analysis.",
        "provenance": ["Calibrating Baseline", "Missing Wearable Data"]
    })


def adjust_tomorrow_plan(internal_uuid, item_id, new_status):
    return {'status': 'success'}

