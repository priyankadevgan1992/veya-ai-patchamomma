import json
import sqlite3
import os
import datetime
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

class CognitiveDecisionMatrix:
    """
    7-Dimensional Human Cognitive Parameter Matrix:
    Evaluates real human life friction, attention residue, relational deficits,
    biological budget, and downstream carryover costs.
    """

    def evaluate_cognitive_state(self, internal_uuid: str, context: Dict[str, Any], user_message: str = "") -> Dict[str, Any]:
        calendar_events = context.get("calendar_events", [])
        work_stress = context.get("work_stress_level", "Moderate")
        bio_phase = context.get("biological_phase", "None")

        # 1. TEMPORAL & ATTENTION RESIDUE
        meeting_count = len(calendar_events)
        total_meeting_minutes = 0
        back_to_back_count = 0
        attention_residue_minutes = 0

        prev_end = None
        for ev in calendar_events:
            # Parse start and end if ISO
            total_meeting_minutes += 60 # Default average if mock
            if prev_end:
                back_to_back_count += 1
                attention_residue_minutes += 20 # 20 mins attention residue penalty
            prev_end = ev.get("end")

        circadian_peak_available = (total_meeting_minutes < 180)

        # 2. RELATIONAL & HOUSEHOLD DEFICIT
        # Check dynamic facts from twin_profiles
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT relationship_health, life_anchor FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
        row = cursor.fetchone()
        conn.close()

        rel_notes = row["relationship_health"] if row else "{}"
        spouse_away = "travel" in rel_notes.lower()
        caregiving_active = "medicine" in rel_notes.lower() or "exam" in rel_notes.lower() or "daughter" in rel_notes.lower()
        
        relational_deficit_score = 75 if spouse_away and meeting_count >= 3 else 35

        # 3. COGNITIVE LOAD & HIGH-STAKES RUNWAY
        high_stakes_event_present = any("pitch" in ev.get("title", "").lower() or "board" in ev.get("title", "").lower() or "review" in ev.get("title", "").lower() for ev in calendar_events)
        prep_runway_deficit = high_stakes_event_present and total_meeting_minutes >= 180

        # 4. BIOLOGICAL & SOMATIC BUDGET
        is_luteal = (bio_phase == "Luteal")
        somatic_fatigue_index = 85 if (is_luteal and total_meeting_minutes >= 120) or work_stress == "High" else 45

        # 5. TRANSIT & SPATIAL LOGISTICS
        transit_buffer_risk = True if meeting_count >= 4 else False

        # 6. PSYCHOLOGICAL & DECISION FATIGUE
        decision_fatigue_score = min(meeting_count * 18 + (25 if work_stress == "High" else 10), 100)

        # 7. DOWNSTREAM CARRYOVER RISK (Second-Order Effect)
        # If evening meeting exists (18:00+, 6 PM+) or high stress with multiple meetings
        late_evening_event = any(
            any(t in str(ev.get("start", "")).lower() for t in ["18:", "19:", "20:", "21:", "06:", "07:", "08:", "6:", "7:", "8:", "pm"])
            for ev in calendar_events
        )
        downstream_carryover_risk = 92 if (late_evening_event or meeting_count >= 3) and (spouse_away or work_stress == "High") else 50


        return {
            "temporal": {
                "meeting_minutes": total_meeting_minutes,
                "attention_residue_minutes": attention_residue_minutes,
                "circadian_peak_available": circadian_peak_available
            },
            "relational": {
                "spouse_away": spouse_away,
                "caregiving_active": caregiving_active,
                "relational_deficit_score": relational_deficit_score
            },
            "cognitive": {
                "high_stakes_event_present": high_stakes_event_present,
                "prep_runway_deficit": prep_runway_deficit
            },
            "biological": {
                "is_luteal": is_luteal,
                "somatic_fatigue_index": somatic_fatigue_index
            },
            "downstream_carryover_risk": downstream_carryover_risk,
            "overall_overload_confidence": max(downstream_carryover_risk, somatic_fatigue_index)
        }

cognitive_matrix = CognitiveDecisionMatrix()
