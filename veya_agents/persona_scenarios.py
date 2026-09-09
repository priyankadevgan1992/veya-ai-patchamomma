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

class PersonaScenarioEngine:
    """
    Persona Scenario Engine:
    Crafts hyper-personalized, context-rich multi-turn responses and action cards
    for Meera, Priya, Arjun, and Kavita.
    """

    def generate_persona_response(self, persona_id: str, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        msg_lower = user_message.lower()
        
        # ==========================================
        # 1. MEERA (Senior PM, Multi-Calendar Chaos, Husband Traveling)
        # ==========================================
        if persona_id == "meera_pm":
            if any(k in msg_lower for k in ["travel", "husband", "alone", "managing alone"]):
                return {
                    "reply": "I know managing the household and the daughter's schedule while your husband is traveling adds extra cognitive load. Let's make sure we keep tonight's schedule very light after 6 PM.",
                    "has_action_card": True,
                    "action_card_type": "EVENING_PROTECTION",
                    "actions": [
                        {
                            "id": "act_meera_dinner_block",
                            "title": "Block 06:30 PM - 08:00 PM 'Dinner & Daughter Time'",
                            "description": "Declines incoming meeting invites during your home focus window.",
                            "type": "CALENDAR_LOCK"
                        }
                    ]
                }
            elif any(k in msg_lower for k in ["stress", "hectic", "back to back", "exhausted"]):
                return {
                    "reply": "I see your calendar was packed today. You have back-to-back reviews lined up again tomorrow afternoon. How about we shift the 6:00 PM US sync to Friday morning?",
                    "has_action_card": True,
                    "action_card_type": "CALENDAR_RESCHEDULE",
                    "actions": [
                        {
                            "id": "act_meera_reschedule_us_sync",
                            "title": "Draft Reschedule for 6:00 PM US Sync",
                            "description": "Propose Friday 09:30 AM to client team.",
                            "type": "EMAIL_DRAFT"
                        },
                        {
                            "id": "act_meera_lock_evening",
                            "title": "Lock 'Family & Unwind' (06:00 PM - 08:30 PM)",
                            "description": "Mark Google Calendar as Out-of-Office.",
                            "type": "CALENDAR_LOCK"
                        }
                    ]
                }
            elif any(k in msg_lower for k in ["yes", "sure", "tell me what", "what can i do", "help me"]):
                return {
                    "reply": "Here are 2 instant steps to protect your evening peace:",
                    "has_action_card": True,
                    "action_card_type": "CALENDAR_RESCHEDULE",
                    "actions": [
                        {
                            "id": "act_meera_reschedule_us_sync",
                            "title": "Draft Reschedule for 6:00 PM US Sync",
                            "description": "Propose Friday 09:30 AM to client team.",
                            "type": "EMAIL_DRAFT"
                        },
                        {
                            "id": "act_meera_lock_evening",
                            "title": "Lock 'Family & Unwind' (06:00 PM - 08:30 PM)",
                            "description": "Mark Google Calendar as Out-of-Office.",
                            "type": "CALENDAR_LOCK"
                        }
                    ]
                }

        # ==========================================
        # 2. PRIYA (UX Researcher, Cycle-Tracked Luteal Rhythm)
        # ==========================================
        elif persona_id == "priya_cycle":
            if any(k in msg_lower for k in ["low energy", "luteal", "tired", "fatigue", "cycle"]):
                return {
                    "reply": "You're in Day 23 of your cycle (luteal phase), so lower physical energy and a preference for focused synthesis are completely natural. Let's swap out intense workouts for gentle restoration.",
                    "has_action_card": True,
                    "action_card_type": "CYCLE_RECOVERY",
                    "actions": [
                        {
                            "id": "act_priya_walk",
                            "title": "Schedule 20-min Gentle Nature Walk at 06:30 PM",
                            "description": "Replaces 45-min HIIT to support progesterone balance.",
                            "type": "CALENDAR_UPDATE"
                        },
                        {
                            "id": "act_priya_tea_buffer",
                            "title": "Add 15-min Chamomile & Decompression Gap",
                            "description": "Inserts a quiet buffer before evening unwind.",
                            "type": "CALENDAR_LOCK"
                        }
                    ]
                }
            elif any(k in msg_lower for k in ["walk", "nature", "gentle", "sounds good", "yes"]):
                return {
                    "reply": "Wonderful! I've set up your restorative recovery routine for this evening:",
                    "has_action_card": True,
                    "action_card_type": "CYCLE_RECOVERY",
                    "actions": [
                        {
                            "id": "act_priya_walk",
                            "title": "Schedule 20-min Gentle Nature Walk at 06:30 PM",
                            "description": "Replaces HIIT session on Google Calendar.",
                            "type": "CALENDAR_UPDATE"
                        }
                    ]
                }

        # ==========================================
        # 3. ARJUN (Sales Manager, Pre-Salary Stress & Pitch Prep)
        # ==========================================
        elif persona_id == "arjun_sales":
            if any(k in msg_lower for k in ["presentation", "pitch", "client", "prep", "deck"]):
                return {
                    "reply": "With Friday's enterprise client pitch on the line, having your prep locked in early will eliminate last-minute panic. Let's carve out 45 minutes on Wednesday morning.",
                    "has_action_card": True,
                    "action_card_type": "PITCH_PREP_LOCK",
                    "actions": [
                        {
                            "id": "act_arjun_pitch_buffer",
                            "title": "Reserve Wednesday 11:00 AM Pitch Prep Window",
                            "description": "Blocks 45 minutes on Google Calendar and silences Slack notifications.",
                            "type": "CALENDAR_LOCK"
                        }
                    ]
                }
            elif any(k in msg_lower for k in ["salary", "stress", "commission", "month end"]):
                return {
                    "reply": "End-of-month salary and quota cycles always trigger spike stress. Let's make sure we protect your evening boundary and get a good 7.5 hours of sleep tonight.",
                    "has_action_card": True,
                    "action_card_type": "STRESS_REDUCTION",
                    "actions": [
                        {
                            "id": "act_arjun_unwind",
                            "title": "Set 07:30 PM Work Notification Cut-Off",
                            "description": "Mutes sales dashboards and email alerts until 08:30 AM tomorrow.",
                            "type": "NOTIFICATION_ALARM"
                        }
                    ]
                }

        # ==========================================
        # 4. KAVITA (Homemaker, Zero Google Calendar, Meds & Family)
        # ==========================================
        elif persona_id == "kavita_homemaker":
            if any(k in msg_lower for k in ["medicine", "doctor", "pharmacy", "remind", "bp"]):
                return {
                    "reply": "Your mother-in-law's hypertension medicine is due for a refill in 3 days. Shall I set a gentle reminder tomorrow morning right during your quiet window between 9:30 and 10:30 AM?",
                    "has_action_card": True,
                    "action_card_type": "HOUSEHOLD_CARE",
                    "actions": [
                        {
                            "id": "act_kavita_med_reminder",
                            "title": "Set 09:45 AM Pharmacy Reminder Tomorrow",
                            "description": "Alerts you during your morning grocery run window.",
                            "type": "NOTIFICATION_ALARM"
                        }
                    ]
                }
            elif any(k in msg_lower for k in ["exam", "revision", "kids", "children", "study"]):
                return {
                    "reply": "I have marked 04:00 PM to 06:00 PM for the children's math exam revision. I'll make sure to keep your afternoon free of other household errands.",
                    "has_action_card": True,
                    "action_card_type": "EXAM_WINDOW",
                    "actions": [
                        {
                            "id": "act_kavita_exam_study",
                            "title": "Protect 04:00 PM - 06:00 PM Study Window",
                            "description": "Keeps your mid-afternoon dedicated to school revision.",
                            "type": "NOTIFICATION_ALARM"
                        }
                    ]
                }

        # Generic Warm Conversational Fallback
        return {
            "reply": "Thank you for sharing with me! I'm constantly learning your daily rhythm so we can protect your peace and priority windows.",
            "has_action_card": False,
            "actions": []
        }
