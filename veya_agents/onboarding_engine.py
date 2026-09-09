import os
import json
import sqlite3
import datetime
from typing import Dict, Any, List

from veya_agents.vector_rag import vector_store
from veya_agents.context_agent import ContextAgent
from veya_agents.twin_builder import TwinBuilderAgent

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

ONBOARDING_STEPS = [
    {
        "step": 1,
        "question": "Welcome to Veya! I'm here to help you protect your energy, focus, and what matters most. To start, what name would you like me to call you?",
        "field": "name"
    },
    {
        "step": 2,
        "question": "Nice to meet you! What is your main role or what are you spending most of your daily hours on right now?",
        "field": "role"
    },
    {
        "step": 3,
        "question": "Got it. If you could protect ONE thing in your daily life from getting swallowed by work and chaos (like family dinners, morning workout, quiet reading, or sleep), what would it be?",
        "field": "life_anchor"
    },
    {
        "step": 4,
        "question": "Thank you for sharing that. I've initialized your Living Digital Twin and stored your priorities securely. How are you feeling right now about your day ahead?",
        "field": "current_feeling"
    }
]

class ConversationalOnboardingEngine:
    """
    Conversational Onboarding Engine:
    Guides new users through a warm, natural 3-step conversation.
    Extracts facts progressively, indexes them directly into SQLite and Vector RAG store,
    and seamlessly transitions the user to full companion mode upon completion.
    """

    def get_user_onboarding_state(self, internal_uuid: str) -> Dict[str, Any]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT onboarding_completed, persona_name, life_anchor FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
        row = cursor.fetchone()
        
        # Count user chat messages during onboarding
        cursor.execute("SELECT COUNT(*) FROM chat_memories WHERE internal_uuid = ? AND role = 'user'", (internal_uuid,))
        msg_count = cursor.fetchone()[0]
        conn.close()

        completed = bool(row["onboarding_completed"]) if row else False
        return {
            "onboarding_completed": completed,
            "step": min(msg_count + 1, 4),
            "persona_name": row["persona_name"] if row else "Friend"
        }

    def process_onboarding_turn(self, internal_uuid: str, user_message: str) -> Dict[str, Any]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT onboarding_completed, persona_name, life_anchor FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
        row = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM chat_memories WHERE internal_uuid = ? AND role = 'user'", (internal_uuid,))
        turn_count = cursor.fetchone()[0]

        # Step 1: User just provided their name
        if turn_count == 0:
            name = user_message.strip().title()
            cursor.execute("UPDATE twin_profiles SET persona_name = ? WHERE internal_uuid = ?", (name, internal_uuid))
            conn.commit()
            vector_store.store_memory(internal_uuid, f"User's preferred name is {name}", category="PREFERENCE")
            reply = f"Wonderful to meet you, {name}! What is your main professional role or what is your daily focus right now?"
            next_step = 2

        # Step 2: User just provided their role
        elif turn_count == 1:
            role = user_message.strip()
            cursor.execute("UPDATE twin_profiles SET life_anchor = ? WHERE internal_uuid = ?", (f"Daily role: {role}", internal_uuid))
            conn.commit()
            vector_store.store_memory(internal_uuid, f"User's daily role and focus: {role}", category="WORK_PATTERN")
            reply = f"Understood! If you could protect ONE life priority from getting overwhelmed by meetings and work (like evening family time, morning workout, quiet time, or uninterrupted sleep), what would it be?"
            next_step = 3

        # Step 3: User provided their primary life anchor
        elif turn_count == 2:
            anchor = user_message.strip()
            cursor.execute("""
                UPDATE twin_profiles 
                SET life_anchor = ?, onboarding_completed = 1 
                WHERE internal_uuid = ?
            """, (f"Protect: {anchor}", internal_uuid))
            conn.commit()
            vector_store.store_memory(internal_uuid, f"Core life anchor to protect: {anchor}", category="LIFE_ANCHOR")
            reply = f"I've locked that into your Digital Twin: we will actively help you protect '{anchor}'. I'm connected to your space now. How is your schedule or energy feeling today?"
            next_step = 4

        else:
            # Fallback completion
            cursor.execute("UPDATE twin_profiles SET onboarding_completed = 1 WHERE internal_uuid = ?", (internal_uuid,))
            conn.commit()
            reply = "I'm right here with you. What would you like to plan or review?"
            next_step = 4

        conn.close()
        return {
            "reply": reply,
            "onboarding_completed": (next_step >= 4),
            "step": next_step
        }

onboarding_engine = ConversationalOnboardingEngine()
