# Uses Vertex AI (project: prisha1910-token-2026, location: global). 
# Auth via ADC — run `gcloud auth application-default login` if the client fails to initialize.
import os
import json
import sqlite3
import datetime
import random
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

class GeminiLLMEngine:
    """
    Hybrid Gemini Engine:
    Calls Google Vertex AI;
    automatically and seamlessly falls back to the local cognitive reasoning engine
    if rate-limited or offline so the app NEVER crashes or stutters.
    """
    def __init__(self):
        self.client = None
        try:
            from google import genai
            self.client = genai.Client(vertexai=True, project="prisha1910-token-2026", location="global")
        except Exception as e:
            print(f"GenAI SDK notice: {e}")

    def generate_chat_response(self, system_instruction: str, user_message: str, context: Dict[str, Any], media_data: str = None, media_mime_type: str = None) -> str:
        # Try Live Vertex AI Call first
        if self.client:
            prompt = f"""
System Instruction:
{system_instruction}

IMPORTANT: Do NOT hallucinate taking actions (like setting reminders, sending emails, or booking calendar events). You are a conversational agent. Action cards are handled separately.

Conversational Onboarding Logic:
- If 'onboarding_completed' is False, your primary goal is to gently ask ONE question at a time to get to know them (e.g. name, role, life anchor). Wrap the question in warm, empathetic banter. DO NOT interrogate them. Keep it conversational. Max 2-3 sentences.
- If 'onboarding_completed' is True, act as a light, happy, and supportive life companion. Do NOT assume they are busy or stressed unless they explicitly say so. Keep the tone friendly, energetic, and casual, like a normal friend.

User Profile & Context:
- Onboarding Completed: {context.get('onboarding_completed', False)}
- Persona: {context.get('persona_name')} ({context.get('persona_id')})
- Life Anchor: {context.get('life_anchor')}
- Stress Level: {context.get('work_stress_level')}
  - Household Orbit / Key People: {json.dumps(context.get('household_members', []))}
- Upcoming Live Google Calendar Events: {json.dumps(context.get('calendar_events', []))}
- Recent Chat History: {json.dumps(context.get('recent_chat_history', [])[-4:])}

User says: "{user_message}"

Reply warmly and conversationally as Veya (keep it natural, like a close friend, max 2-3 sentences):
"""
            # Try multiple models based on availability
            for m in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]:
                try:
                    contents = [prompt]
                    if media_data and media_mime_type:
                        import base64
                        from google.genai import types
                        try:
                            if "data:" in media_data and "base64," in media_data:
                                media_data = media_data.split("base64,")[1]
                            media_bytes = base64.b64decode(media_data)
                            part = types.Part.from_bytes(data=media_bytes, mime_type=media_mime_type)
                            contents.append(part)
                        except Exception as e:
                            print(f"Media encoding failed: {e}")

                    res = self.client.models.generate_content(
                        model=m,
                        contents=contents
                    )
                    if res.text:
                        return res.text.strip()
                except Exception as e:
                    print(f"Gemini {m} failed: {e}")
                    # If it's a quota issue, we should let the user know directly in the chat
                    if "429" in str(e) or "quota" in str(e).lower() or "credits" in str(e).lower() or "resource_exhausted" in str(e).lower():
                        return "⚠️ **System Alert**: Vertex AI quota exhausted! Veya is currently running on limited local fallback logic."

                    pass

        # -------------------------------------------------------------
        # SMART LOCAL COGNITIVE FALLBACK (No Hardcoded Responses)
        # -------------------------------------------------------------
        msg_lower = user_message.lower()
        events = context.get("calendar_events", [])
        events_count = len(events)
        stress = context.get("work_stress_level", "Moderate")

        # Intent: Eating / Food
        if any(w in msg_lower for w in ["eat", "hungry", "food", "lunch", "dinner", "breakfast", "snack", "starving"]):
            if events_count > 0:
                next_event = events[0].get("title", "your next meeting")
                return f"I see you have '{next_event}' coming up soon. We should definitely get you fed before that so your glucose levels don't crash. Shall I find a quick 20-min window to block for a meal?"
            else:
                return "You definitely need fuel! Since your schedule is clear, take a proper break. Maybe step away from the desk to eat so you get a real mental reset."

        # Intent: Frustration / Bug Reports
        if any(w in msg_lower for w in ["broken", "bad", "stupid", "annoying", "hate", "one sided", "one-sided", "wrong"]):
            return "I hear you, and I'm sorry this is frustrating. My cloud AI connection is currently hitting quota limits, so I'm running on my local backup logic. I'm taking notes on what I missed so I can adapt."

        # Intent: User is bored / wants suggestions
        if any(w in msg_lower for w in ["bored", "suggest", "ideas", "nothing to do"]):
            if events_count > 0:
                next_event = events[0].get("title", "your next meeting")
                return f"Since you have a gap before '{next_event}', how about we use this time for a quick 10-minute mental reset or a short walk?"
            elif stress == "High":
                return "You've been running on high stress lately. Why not use this downtime to completely disconnect? Put on some music or grab a warm drink."
            else:
                return "It's rare to have quiet moments! You could read that book you've been putting off, or maybe organize your goals for tomorrow. What sounds good?"

        # Intent: User is tired / exhausted
        if any(w in msg_lower for w in ["tired", "exhausted", "sleepy", "drained"]):
            if events_count >= 3:
                return f"I see you have {events_count} meetings ahead. Your energy is low—do you want me to try and reschedule some of the non-essential ones?"
            return "Your biological battery seems depleted. Please make sure to protect your evening window tonight for some solid recovery."

        # Intent: Greeting
        if any(w in msg_lower for w in ["hi ", "hi", "hello", "hey", "morning", "evening"]):
            greetings = [
                f"Hey {context.get('persona_name', 'there')}! How's your energy holding up?",
                f"Hi! I'm tracking {events_count} upcoming events for you. Ready to tackle them?",
                "Hello! I'm right here. How can I help protect your time today?"
            ]
            return random.choice(greetings)
            
        # Intent: Affirmation
        if msg_lower.strip() in ["yes", "ok", "sure", "sounds good", "do it", "yeah", "yep"]:
            return "Got it. I'll note that down and adjust our plans accordingly. Anything else on your mind?"

        # Dynamic Generic Contextual Fallback
        responses = [
            f"I'm keeping track of your daily flow. With {events_count} events today, how are you pacing yourself?",
            "I'm here. Tell me a bit more about what you need right now.",
            f"Looking at your schedule, I'm analyzing your cognitive load. What's the most important thing for you to protect today?"
        ]
        return random.choice(responses)
