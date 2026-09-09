import json
import sqlite3
import os
from db_schema import init_db, get_or_create_user, DB_PATH

def generate_synthetic_data():
    init_db()
    
    personas_map = [
        ("meera@gmail.com", "meera_pm", "Meera"),
        ("priya@gmail.com", "priya_cycle", "Priya"),
        ("arjun@gmail.com", "arjun_sales", "Arjun"),
        ("kavita@gmail.com", "kavita_homemaker", "Kavita")
    ]

    for email, persona_id, name in personas_map:
        user_uuid = get_or_create_user(email, persona_id=persona_id)

        conn = sqlite3.connect(DB_PATH, timeout=20)
        cursor = conn.cursor()

        # Seed initial greeting chat memory
        cursor.execute("SELECT COUNT(*) FROM chat_memories WHERE internal_uuid = ?", (user_uuid,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO chat_memories (memory_id, internal_uuid, role, content, extracted_facts)
            VALUES (?, ?, ?, ?, ?)
            """, (
                f"mem_init_{persona_id}",
                user_uuid,
                "assistant",
                f"Hey, I'm VeyaAI — I'm glad you chose me to be your companion. I will be improving over time to make your life decisions easy. Hope I'm of great help! So I would like to know more about you, {name} — tell me about yourself!",
                json.dumps({"persona_seeded": True, "name": name})
            ))

        # Seed Tomorrow Feasibility Plan
        cursor.execute("SELECT COUNT(*) FROM tomorrow_plans WHERE internal_uuid = ?", (user_uuid,))
        if cursor.fetchone()[0] == 0:
            if persona_id == "meera_pm":
                actions = [
                    {
                        "num": 1,
                        "action": "Keep 07:30–08:30 AM reserved for family & kid prep",
                        "reason": "Your husband is traveling, and morning routines run smoothest without work distractions."
                    },
                    {
                        "num": 2,
                        "action": "Block 10:00–11:30 AM for Deep Architecture Focus",
                        "reason": "Your peak cognitive energy window & prep needed for Friday's client presentation."
                    },
                    {
                        "num": 3,
                        "action": "Reschedule the 06:00 PM US Team Call to Friday morning",
                        "reason": "Daughter's parent-teacher meeting is at 4 PM and father-in-law's flight arrives at 8 PM."
                    }
                ]
            elif persona_id == "priya_cycle":
                actions = [
                    {
                        "num": 1,
                        "action": "Swap intense evening HIIT workout for a gentle 20-min walk",
                        "reason": "You're in Day 23 of your luteal phase and reported lower recovery energy today."
                    },
                    {
                        "num": 2,
                        "action": "Schedule UX synthesis for 10:00 AM",
                        "reason": "Your analytical focus is highest during mid-morning windows."
                    }
                ]
            elif persona_id == "arjun_sales":
                actions = [
                    {
                        "num": 1,
                        "action": "Insert 45-min Client Presentation Prep block at 11:00 AM Wednesday",
                        "reason": "Friday client sync has no prep block yet; historically, early prep prevents pre-salary stress spikes."
                    },
                    {
                        "num": 2,
                        "action": "Schedule 15-min evening unwind walk",
                        "reason": "Pre-payday week stress indicators are slightly elevated."
                    }
                ]
            else: # kavita_homemaker
                actions = [
                    {
                        "num": 1,
                        "action": "Set morning pharmacy reminder for 09:45 AM",
                        "reason": "Mother-in-law's hypertension medicine runs out in 3 days; your free household window is 09:30–10:30 AM."
                    },
                    {
                        "num": 2,
                        "action": "Keep 04:00–06:00 PM free for children's exam review",
                        "reason": "Kids' final exam week starts next Monday."
                    }
                ]

            cursor.execute("""
            INSERT INTO tomorrow_plans (plan_id, internal_uuid, plan_date, action_items, status)
            VALUES (?, ?, ?, ?, ?)
            """, (
                f"plan_{persona_id}_tomorrow",
                user_uuid,
                "2026-08-25",
                json.dumps(actions),
                "PENDING"
            ))

        conn.commit()
        conn.close()
    
    print("Synthetic persona arcs and database tables successfully generated!")

if __name__ == "__main__":
    generate_synthetic_data()
