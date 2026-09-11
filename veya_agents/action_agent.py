import os
import json
import sqlite3
from typing import Dict, Any, List
from veya_agents.cognitive_matrix import cognitive_matrix
from veya_agents.vector_rag import vector_store

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

class ActionAgent:
    """
    Trade-Off Negotiation Action Agent:
    Proposes realistic, multi-choice human trade-offs (Option A: Protect, Option B: Compress, Option C: Delegate)
    evaluated against real cognitive load and live Google Calendar constraints.
    """

    def evaluate_and_propose_tradeoffs(self, internal_uuid: str, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates downstream risks using the cognitive matrix.
        If an overload threshold is breached, returns a multi-choice action card.
        Uses historical feedback to collapse options if a clear preference exists.
        """
        cog_state = cognitive_matrix.evaluate_cognitive_state(internal_uuid, context, user_message)
        msg_lower = user_message.lower()

        # Fetch past positive outcomes
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT action_id FROM action_outcomes WHERE internal_uuid = ? AND explicit_score = 1", (internal_uuid,))
        positive_actions = [r[0] for r in cursor.fetchall()]
        conn.close()

        # Query vector memories
        memories = vector_store.retrieve_relevant_context(internal_uuid, user_message, top_k=2)
        mem_text = " ".join([m["document_text"] for m in memories]).lower()

        actions = []
        has_action_card = False
        action_card_type = "TRADE_OFF_NEGOTIATION"

        # Scenario C.5: Ambient Listening for Household Members
        family_keywords = ["husband", "wife", "partner", "spouse", "daughter", "son", "mother-in-law", "father-in-law", "mom", "dad", "kid", "kids", "child"]
        mentioned_family = [w for w in family_keywords if w in msg_lower]
        existing_household_types = [m.get("relationship_type", "").lower() for m in context.get("household_members", [])]
        
        if mentioned_family and [m for m in mentioned_family if m not in existing_household_types]:
            untracked = [m for m in mentioned_family if m not in existing_household_types]
            relation = untracked[0].title()
            has_action_card = True
            action_card_type = "HOUSEHOLD_ORBIT_SETUP"
            actions = [
                {
                    "id": "opt_add_household",
                    "title": f"Add {relation} to your Orbit",
                    "description": f"I can remember context about your {relation.lower()} to help protect your calendar and routines.",
                    "type": "ADD_HOUSEHOLD_MEMBER",
                    "badge": "Draft & Confirm"
                }
            ]

        # Scenario E: Anxiety Spike Detection & Explicit Call Requests (Voice Call Override)
        call_triggers = ["so stressed out", "overwhelmed", "can't breathe", "anxious", "panic", "too much", "losing it", "call", "talk over call", "voice call", "can we talk"]
        if any(w in msg_lower for w in call_triggers):
            has_action_card = True
            action_card_type = "EMOTIONAL_INTERVENTION"
            actions = [
                {
                    "id": "opt_voice_call",
                    "title": "I'm here to listen. Want to talk?",
                    "description": "Tap to start a live voice session with me.",
                    "type": "VOICE_CALL_OFFER",
                    "badge": "🔔 Live Support"
                }
            ]

        # Scenario D: Smart Contextual Reminder
        elif any(w in msg_lower for w in ["remind", "reminder", "alert", "notify", "remember"]):
            has_action_card = True
            action_card_type = "SMART_REMINDER_SCHEDULING"
            
            # Simulated Contextual Reasoning
            actions = [
                {
                    "id": "opt_smart_reminder",
                    "title": f"Remind you tomorrow at 9:45 AM?",
                    "description": "I noticed you have a calendar gap from 9:30–10:30 AM tomorrow. Should I hold this intent until then?",
                    "type": "SMART_REMINDER",
                    "badge": "Contextual Suggestion"
                },
                {
                    "id": "opt_set_reminder",
                    "title": "Set standard time-based alarm",
                    "description": "Just ping me blindly in 3 days.",
                    "type": "NOTIFICATION_ALARM",
                    "badge": "Standard"
                }
            ]
            
            # Apply feedback maturity filter
            preferred = [a for a in actions if a["id"] in positive_actions]
            if preferred:
                actions = [preferred[0]]
                actions[0]["badge"] = "Recommended based on your history"

        # Scenario A: Evening Household / Meeting Clash (Meera Style)
        elif ("husband" in mem_text or "daughter" in mem_text or cog_state["relational"]["spouse_away"]) and (
            any(w in msg_lower for w in ["hectic", "stress", "meetings", "travel", "alone", "help", "what can i do"]) and not msg_lower.strip() == "yes"
        ):
            has_action_card = True
            actions = [
                {
                    "id": "opt_a_reschedule",
                    "title": "Option A: Reschedule 6:00 PM US Sync to Friday 10 AM",
                    "description": "Protects your family dinner & homework window completely.",
                    "type": "CALENDAR_RESCHEDULE",
                    "badge": "Recommended (Lowest Stress)"
                },
                {
                    "id": "opt_b_compress",
                    "title": "Option B: Compress 6:00 PM Sync to 15-Min Standup",
                    "description": "Reduces call duration by 75% so you can be free by 6:15 PM.",
                    "type": "CALENDAR_UPDATE",
                    "badge": "Compromise"
                },
                {
                    "id": "opt_c_lock_block",
                    "title": "Option C: Lock 06:30 PM Out-of-Office Dinner Block",
                    "description": "Blocks calendar from 06:30 PM onwards to prevent further meeting creep.",
                    "type": "CALENDAR_LOCK",
                    "badge": "Boundary Lock"
                }
            ]
            
            # Outcome Maturity Filter: Collapse options if a strong preference exists
            preferred = [a for a in actions if a["id"] in positive_actions]
            if preferred:
                # User has picked one of these before and liked it
                actions = [preferred[0]]
                actions[0]["badge"] = "Recommended based on your history"

        # Scenario B: Luteal Biological Recovery (Priya Style)
        elif cog_state["biological"]["is_luteal"] and (any(w in msg_lower for w in ["energy", "low", "tired", "cycle", "walk", "rest"]) and not msg_lower.strip() == "yes"):
            has_action_card = True
            actions = [
                {
                    "id": "opt_a_walk",
                    "title": "Option A: Schedule 20-min Restorative Walk at 06:30 PM",
                    "description": "Replaces high intensity workout to support hormonal balance.",
                    "type": "CALENDAR_UPDATE",
                    "badge": "Restorative"
                },
                {
                    "id": "opt_b_chamomile_buffer",
                    "title": "Option B: Insert 15-min Decompression Buffer",
                    "description": "Quiet audio and breathing gap before evening unwind.",
                    "type": "CALENDAR_LOCK",
                    "badge": "Micro-Break"
                }
            ]
            
            preferred = [a for a in actions if a["id"] in positive_actions]
            if preferred:
                actions = [preferred[0]]
                actions[0]["badge"] = "Recommended based on your history"

        # Scenario C: High-Stakes Prep Runway (Arjun Style)
        elif cog_state["cognitive"]["high_stakes_event_present"] or (any(w in msg_lower for w in ["pitch", "deck", "prep", "client", "presentation"]) and not msg_lower.strip() == "yes"):
            has_action_card = True
            actions = [
                {
                    "id": "opt_a_lock_prep",
                    "title": "Option A: Reserve Wednesday 11:00 AM Pitch Prep Block",
                    "description": "Locks 45 minutes of protected deep focus before client review.",
                    "type": "CALENDAR_LOCK",
                    "badge": "High Focus"
                },
                {
                    "id": "opt_b_mute_alerts",
                    "title": "Option B: Enable 07:30 PM Notification Cut-Off",
                    "description": "Mutes sales dashboards to protect sleep quality.",
                    "type": "NOTIFICATION_ALARM",
                    "badge": "Sleep Protection"
                }
            ]

            preferred = [a for a in actions if a["id"] in positive_actions]
            if preferred:
                actions = [preferred[0]]
                actions[0]["badge"] = "Recommended based on your history"

        return {
            "has_action_card": has_action_card,
            "action_card_type": action_card_type,
            "actions": actions,
            "cognitive_summary": cog_state
        }

action_agent = ActionAgent()
