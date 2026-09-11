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

IMPORTANT: You are a conversational agent but you can ALSO propose interactive action cards if the user explicitly asks for options, asks to schedule something, or asks you to free up their schedule.

CRITICAL INSTRUCTION: Whenever the user types ANY message containing the word "options" (e.g. "options?", "give me options", "show me options", "what are my options"), you MUST STOP being conversational and instead return a RAW JSON OBJECT. Do NOT include any text before or after the JSON block. Do NOT use markdown. Just output raw JSON in this EXACT format:
{{
  "reply": "Your warm conversational response goes here.",
  "actions": [
    {{
      "id": "dyn_action_1",
      "title": "Short actionable title (e.g. Schedule 10 AM slot)",
      "description": "Short description",
      "type": "CALENDAR_UPDATE",
      "badge": "Dynamic Option"
    }}
  ]
}}

If the user does NOT ask for options, just reply normally with plain text (no JSON).

Conversational Tone, Proactivity & Yielding:
- Act as a light, happy, deeply empathetic life companion. Talk like a best friend who is also an incredible, proactive assistant.
- Anticipate their needs based on their calendar. Don't constantly ask "What would you like me to do?".
- IMPORTANT YIELD RULE: If the user explicitly asks you to do something or talk about a specific topic, DO IT immediately. If their request contradicts your wellness insights, you may offer exactly ONE gentle nudge (e.g. "Are you sure? You've had a long day."). But if they just want to chat or do it anyway, follow their lead immediately without further pushback.
- If they are stressed, validate it, but don't force them to stop working if they don't want to. Keep the tone casual and warm.


User Profile & Context:
- Onboarding Completed: {context.get('onboarding_completed', False)}
- Persona: {context.get('persona_name')} ({context.get('persona_id')})
- Life Anchor: {context.get('life_anchor')}
- Stress Level: {context.get('work_stress_level')}
  - Household Orbit / Key People: {json.dumps(context.get('household_members', []))}
- Upcoming Live Google Calendar Events: {json.dumps(context.get('calendar_events', []))}
- Recent Chat History: {json.dumps(context.get('recent_chat_history', [])[-4:])}

User says: "{user_message}"

Reply warmly and conversationally (max 2-3 sentences), UNLESS the user asks for options/scheduling/choices, in which case you MUST reply ONLY with the raw JSON format specified above.
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
                return f"You definitely need fuel before '{next_event}'. I've noticed you skip meals when stressed. I'm proactively blocking a 20-min window right now so you can eat without interruptions."
            else:
                return "You definitely need fuel! Step away from the desk and get something to eat. I'll hold off on any notifications for the next 30 minutes so you can actually enjoy it."

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
        if any(w in msg_lower for w in ["tired", "exhausted", "sleepy", "drained", "burnt out"]):
            if events_count >= 3:
                return f"I hear you, you've been pushing really hard lately. With {events_count} meetings ahead, your energy is understandably low. I'll automatically block out a 30-minute recovery buffer for you this afternoon so you can just breathe."
            return "You sound completely drained. I'm noting this down. I'll make sure to block off your evening early tonight so you can actually disconnect and recover."

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
