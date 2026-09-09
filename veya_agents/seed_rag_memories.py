import json
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from veya_data.db_schema import DB_PATH
from veya_agents.vector_rag import vector_store

def populate_initial_rag_memories():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT internal_uuid, persona_id, persona_name, life_anchor, relationship_health FROM twin_profiles")
    profiles = [dict(r) for r in cursor.fetchall()]
    conn.close()

    print(f"Ingesting memory vector graph for {len(profiles)} twin profiles...")

    for p in profiles:
        u_id = p["internal_uuid"]
        p_id = p["persona_id"]
        name = p["persona_name"]

        vector_store.store_memory(u_id, f"Core life anchor: {p['life_anchor']}", category="LIFE_ANCHOR")

        if p_id == "meera_pm":
            vector_store.store_memory(u_id, "Household Context: Husband is on a 4-day business trip; managing daughter's routine alone.", category="FAMILY_RHYTHM")
            vector_store.store_memory(u_id, "School Milestone: Daughter's parent-teacher meeting (PTM) and revision schedule this week.", category="FAMILY_RHYTHM")
            vector_store.store_memory(u_id, "Calendar Overload Pattern: Back-to-back reviews with late 6:00 PM US syncs cause high next-day stress.", category="WORK_PATTERN")
            vector_store.store_memory(u_id, "Preferred Boundary: Protect 06:30 PM to 08:30 PM for dinner, unwind, and family time.", category="PREFERENCE")
        elif p_id == "priya_cycle":
            vector_store.store_memory(u_id, "Biological Context: Currently in Day 23 of menstrual cycle (Luteal Phase). Progesterone rhythm requires recovery.", category="BIOLOGY_CYCLE")
            vector_store.store_memory(u_id, "Energy & Work Rhythm: High creative synthesis capacity in the mornings, but physical energy drops in evenings.", category="WORK_PATTERN")
            vector_store.store_memory(u_id, "Workout Preference: Replace high-intensity cardio with a 20-minute gentle evening nature walk during late luteal days.", category="PREFERENCE")
        elif p_id == "arjun_sales":
            vector_store.store_memory(u_id, "Upcoming Milestone: High-stakes enterprise client pitch presentation scheduled for Friday.", category="WORK_PATTERN")
            vector_store.store_memory(u_id, "Stress Trigger: Pre-salary and end-of-month revenue quota deadlines spike anxiety if prep is rushed.", category="STRESS_PATTERN")
            vector_store.store_memory(u_id, "Prep Window Preference: Must lock a dedicated 45-minute prep buffer on Wednesday 11:00 AM before client call.", category="PREFERENCE")
            vector_store.store_memory(u_id, "Notification Boundary: Mute work notifications after 07:30 PM to preserve sleep quality.", category="PREFERENCE")
        elif p_id == "kavita_homemaker":
            vector_store.store_memory(u_id, "Elderly Care Routine: Mother-in-law's hypertension prescription expires in 3 days; pharmacy refill needed.", category="CARE_SCHEDULE")
            vector_store.store_memory(u_id, "Household Windows: Free quiet window between 09:30 AM and 10:30 AM before afternoon cooking cycle.", category="HOUSEHOLD_RHYTHM")
            vector_store.store_memory(u_id, "Children Exam Window: Middle school math exams revision happens daily from 04:00 PM to 06:00 PM.", category="FAMILY_RHYTHM")

    print("[SUCCESS] RAG Vector Store successfully seeded from database profiles!")

if __name__ == "__main__":
    populate_initial_rag_memories()
