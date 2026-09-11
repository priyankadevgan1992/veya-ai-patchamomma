import os
import json
import sqlite3
import hashlib
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from veya_data.db_schema import init_db, DB_PATH
from veya_data.auth_db import init_auth_tables, hash_password
from veya_agents.agent_system import orchestrator
from veya_agents.tools import derive_metric_explanation, adjust_tomorrow_plan
from veya_connectors.google_calendar import GoogleCalendarConnector

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    import os
    # Add root to sys path so we can import seed_vaibhav
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from veya_data.db_schema import init_db
    from veya_data.auth_db import init_auth_tables
    import seed_vaibhav
    init_db()
    init_auth_tables()
    try:
        seed_vaibhav.seed_vaibhav()
    except Exception as e:
        print("Failed to seed:", e)
    yield

app = FastAPI(title="Veya AI Life Companion API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

# --- REQUEST SCHEMAS ---
class AuthRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""

class ChatRequest(BaseModel):
    internal_uuid: str
    message: str
    media_data: Optional[str] = None
    media_mime_type: Optional[str] = None

from typing import Optional

class ActionExecRequest(BaseModel):
    internal_uuid: str
    action_id: str
    title: str
    situation_context: Optional[str] = ""

class DeriveRequest(BaseModel):
    internal_uuid: str
    metric_name: str
    score: int

class FeasibilityRequest(BaseModel):
    internal_uuid: str
    item_id: int
    new_status: str

# --- AUTH ENDPOINTS (REAL SIGNUP & SIGNIN) ---
@app.post("/api/auth/signup")
def signup(req: AuthRequest):
    username = req.username.strip().lower()
    email = req.email.strip().lower() if req.email else ""
    if not username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM user_accounts WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Account already exists. Please sign in.")

    # Create new fresh user account
    internal_uuid = f"uuid_usr_{os.urandom(6).hex()}"
    pass_hash = hash_password(req.password)

    cursor.execute("""
        INSERT INTO twin_profiles 
        (internal_uuid, persona_id, persona_name, life_anchor, gender_identity, household_members, work_stress_level, relationship_health, calendars_connected, wearable_connected, twin_maturity_weeks, onboarding_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (internal_uuid, "custom_user", "New Friend", "Unset", "Unspecified", 1, "Moderate", "{}", 0, 0, 1, 0))

    cursor.execute("""
        INSERT INTO user_accounts (username, email, password_hash, internal_uuid)
        VALUES (?, ?, ?, ?)
    """, (username, email, pass_hash, internal_uuid))

    conn.commit()
    conn.close()

    return {
        "status": "CREATED",
        "internal_uuid": internal_uuid,
        "email": email,
        "onboarding_completed": False,
        "message": "Account created successfully!"
    }

@app.post("/api/auth/signin")
def signin(req: AuthRequest):
    username = req.username.strip().lower()
    pass_hash = hash_password(req.password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT internal_uuid, password_hash FROM user_accounts WHERE username = ? OR email = ?", (username, username))
    row = cursor.fetchone()
    
    if not row or row["password_hash"] != pass_hash:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    internal_uuid = row["internal_uuid"]
    cursor.execute("SELECT persona_name, onboarding_completed, twin_maturity_weeks FROM twin_profiles WHERE internal_uuid = ?", (internal_uuid,))
    prof = cursor.fetchone()
    conn.close()

    return {
        "status": "AUTHENTICATED",
        "internal_uuid": internal_uuid,
        "email": username,
        "persona_name": prof["persona_name"] if prof else "Friend",
        "onboarding_completed": bool(prof["onboarding_completed"]) if prof else False,
        "twin_maturity_weeks": prof["twin_maturity_weeks"] if prof else 1
    }

# --- HOME TAB (LIVE GREETING) ---
@app.get("/api/home")
def get_home_stream(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_name, life_anchor, onboarding_completed FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    user_row = cursor.fetchone()
    
    # Fetch chat history
    cursor.execute("SELECT role, content FROM chat_memories WHERE internal_uuid = ? ORDER BY timestamp ASC", (uuid,))
    history = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    onboarding_done = bool(user_row["onboarding_completed"])
    name = user_row["persona_name"] or "Friend"

    # Default greeting
    if not onboarding_done:
        greeting = f"Hi! I'm Veya, your personal life companion. To start, what name would you like me to call you?"
    else:
        greeting = f"Hi {name}, how has your day been treating you?"

    return {
        "greeting": greeting,
        "onboarding_completed": onboarding_done,
        "history": history
    }

class ProfileUpdateRequest(BaseModel):
    internal_uuid: str
    persona_name: str
    work_stress_level: str
    life_anchor: str
    gender_identity: str = ""
    household_members: int = 0
    relationship_health: str = ""
    biological_phase: str = ""
    calendars_connected: int = 0
    wearable_connected: int = 0
    twin_maturity_weeks: int = 0
    orbit: list = []

@app.get("/api/profile")
def get_profile(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT persona_name, work_stress_level, life_anchor, gender_identity, 
               household_members, relationship_health, biological_phase,
               calendars_connected, wearable_connected, twin_maturity_weeks 
        FROM twin_profiles WHERE internal_uuid = ?""", (uuid,))
    p = cursor.fetchone()
    
    # We will fetch active reminders from a dummy table or just return mocked ones if not implemented
    # For now let's query the chat_memories for any reminders we executed, or mock it.
    cursor.execute("SELECT content FROM chat_memories WHERE internal_uuid = ? AND content LIKE '%Set Reminder%'", (uuid,))
    rem_rows = cursor.fetchall()
    reminders = []
    for r in rem_rows:
        import json
        try:
            reminders.append({"title": json.loads(r["content"])["title"]})
        except:
            reminders.append({"title": r["content"][:30] + "..."})

    cursor.execute("SELECT person_name, relationship_type, key_context, importance_percent FROM household_profiles WHERE internal_uuid = ?", (uuid,))
    orbit_rows = cursor.fetchall()
    orbit = [{"person_name": r["person_name"], "relationship_type": r["relationship_type"], "key_context": r["key_context"], "importance_percent": r["importance_percent"]} for r in orbit_rows]

    conn.close()
    
    if p:
        return {
            "persona_name": p["persona_name"],
            "work_stress_level": p["work_stress_level"],
            "life_anchor": p["life_anchor"],
            "gender_identity": p["gender_identity"],
            "household_members": p["household_members"],
            "relationship_health": p["relationship_health"],
            "biological_phase": p["biological_phase"],
            "calendars_connected": p["calendars_connected"],
            "wearable_connected": p["wearable_connected"],
            "twin_maturity_weeks": p["twin_maturity_weeks"],
            "reminders": reminders,
            "orbit": orbit
        }
    return {
        "persona_name": "", "work_stress_level": "Moderate", "life_anchor": "", 
        "gender_identity": "", "household_members": 0, "relationship_health": "", 
        "biological_phase": "", "calendars_connected": 0, "wearable_connected": 0, 
        "twin_maturity_weeks": 0, "reminders": [], "orbit": []
    }

@app.post("/api/profile")
def update_profile(req: ProfileUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE twin_profiles 
        SET persona_name = ?, work_stress_level = ?, life_anchor = ?,
            gender_identity = ?, household_members = ?, relationship_health = ?,
            biological_phase = ?, calendars_connected = ?, wearable_connected = ?,
            twin_maturity_weeks = ?
        WHERE internal_uuid = ?
    """, (req.persona_name, req.work_stress_level, req.life_anchor, req.gender_identity,
          req.household_members, req.relationship_health, req.biological_phase,
          req.calendars_connected, req.wearable_connected, req.twin_maturity_weeks,
          req.internal_uuid))
    
    cursor.execute("DELETE FROM household_profiles WHERE internal_uuid = ?", (req.internal_uuid,))
    for o in req.orbit:
        name = o.get('person_name', '').strip()
        rel = o.get('relationship_type', '').strip()
        if name and rel:
            import uuid
            pid = 'o_' + uuid.uuid4().hex[:12]
            ctx = o.get('key_context', '').strip()
            imp = int(o.get('importance_percent', 50))
            cursor.execute("INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context, importance_percent) VALUES (?, ?, ?, ?, ?, ?)", (pid, req.internal_uuid, name, rel, ctx, imp))
    
    conn.commit()
    conn.close()
    return {"status": "UPDATED"}

# --- CONVERSATIONAL CHAT STREAM ---
@app.post("/api/chat")
def chat_stream(req: ChatRequest):
    response_payload = orchestrator.process_message(req.internal_uuid, req.message, req.media_data, req.media_mime_type)
    return response_payload

import asyncio
import websockets
import base64
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/api/voice/stream")
async def voice_stream(websocket: WebSocket, uuid: str):
    await websocket.accept()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        await websocket.close(code=1011)
        return
        
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    
    # We use gemini-2.0-flash-exp in the URI but allow failures gracefully.
    try:
        async with websockets.connect(uri) as gemini_ws:
            # Send setup message
            setup_msg = {
                "setup": {
                    "model": model_name,
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": "Aoede" # Warm female voice
                                }
                            }
                        }
                    },
                    "systemInstruction": {
                        "parts": [{"text": "You are Veya. Act like a close, empathetic best friend and a proactive personal secretary who knows my patterns. Be deeply supportive. Speak in 1-2 short, conversational sentences. Anticipate my needs based on my schedule without asking too many questions."}]
                    }
                }
            }
            await gemini_ws.send(json.dumps(setup_msg))
            setup_resp = await gemini_ws.recv()
            
            # Make the AI speak first
            initial_prompt = {
                "clientContent": {
                    "turns": [
                        {
                            "role": "user",
                            "parts": [{"text": "Hi Veya, I'm here."}]
                        }
                    ],
                    "turnComplete": True
                }
            }
            await gemini_ws.send(json.dumps(initial_prompt))
            
            async def receive_from_browser():
                try:
                    while True:
                        data = await websocket.receive_bytes()
                        # Forward audio to Gemini
                        msg = {
                            "realtimeInput": {
                                "mediaChunks": [
                                    {
                                        "mimeType": "audio/pcm;rate=16000",
                                        "data": base64.b64encode(data).decode('utf-8')
                                    }
                                ]
                            }
                        }
                        await gemini_ws.send(json.dumps(msg))
                except Exception:
                    pass
                    
            async def receive_from_gemini():
                try:
                    while True:
                        resp = await gemini_ws.recv()
                        resp_dict = json.loads(resp)
                        if "serverContent" in resp_dict:
                            model_turn = resp_dict["serverContent"].get("modelTurn", {})
                            for part in model_turn.get("parts", []):
                                if "inlineData" in part:
                                    audio_b64 = part["inlineData"]["data"]
                                    audio_bytes = base64.b64decode(audio_b64)
                                    await websocket.send_bytes(audio_bytes)
                except Exception:
                    pass

            await asyncio.gather(
                receive_from_browser(),
                receive_from_gemini()
            )
    except Exception as e:
        print(f"Voice Error: {e}")
        await websocket.close(code=1011)

class NotificationReadRequest(BaseModel):
    internal_uuid: str
    notification_id: str

@app.get("/api/notifications")
def get_notifications(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, created_at FROM notifications WHERE internal_uuid = ? AND is_read = 0 ORDER BY created_at DESC", (uuid,))
    rows = cursor.fetchall()
    conn.close()
    
    notifs = []
    for r in rows:
        notifs.append({
            "id": r["id"],
            "text": r["text"],
            "created_at": r["created_at"]
        })
    return {"notifications": notifs}

@app.post("/api/notifications/read")
def mark_notification_read(req: NotificationReadRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND internal_uuid = ?", (req.notification_id, req.internal_uuid))
    conn.commit()
    conn.close()
    return {"status": "READ"}

class FeedbackSubmitRequest(BaseModel):
    internal_uuid: str
    outcome_id: str
    feedback_score: int

@app.get("/api/feedback/pending")
def get_pending_feedback(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    # Get the most recent unrated outcome that is not a reminder or household addition (real actions)
    cursor.execute("""
        SELECT id, action_title, created_at FROM action_outcomes 
        WHERE internal_uuid = ? AND explicit_score IS NULL 
        AND action_id NOT IN ('opt_set_reminder', 'opt_add_household', 'opt_voice_call')
        ORDER BY created_at DESC LIMIT 1
    """, (uuid,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"has_pending": True, "outcome": {"id": row["id"], "action_title": row["action_title"]}}
    return {"has_pending": False}

@app.post("/api/feedback/submit")
def submit_feedback(req: FeedbackSubmitRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE action_outcomes SET explicit_score = ? WHERE id = ? AND internal_uuid = ?", 
                   (req.feedback_score, req.outcome_id, req.internal_uuid))
    conn.commit()
    conn.close()
    return {"status": "FEEDBACK_SAVED"}

# --- 1-TAP ACTION EXECUTION (LIVE GOOGLE CALENDAR) ---
@app.post("/api/actions/execute")
def execute_action(req: ActionExecRequest):
    # 1. Record outcome for feedback loop
    conn = get_db()
    cursor = conn.cursor()
    outcome_id = f"out_{os.urandom(4).hex()}"
    cursor.execute("""
        INSERT INTO action_outcomes (id, internal_uuid, action_id, action_title, situation_hash, state_before, explicit_score, implicit_score)
        VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
    """, (outcome_id, req.internal_uuid, req.action_id, req.title, req.situation_context, "{}"))
    conn.commit()
    conn.close()

    # Handle Household Member Draft & Confirm
    if req.action_id == "opt_add_household":
        relation = req.title.replace("Add ", "").replace(" to your Orbit", "").strip()
        conn = get_db()
        cursor = conn.cursor()
        profile_id = f"hh_{os.urandom(4).hex()}"
        cursor.execute("INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context) VALUES (?, ?, ?, ?, ?)",
                       (profile_id, req.internal_uuid, "Unknown", relation, f"Added via ambient chat listening"))
        cursor.execute("INSERT INTO chat_memories (memory_id, internal_uuid, role, content) VALUES (?, ?, ?, ?)",
                       (f"hh_rem_{os.urandom(4).hex()}", req.internal_uuid, "system", f"Added {relation} to Orbit"))
        conn.commit()
        conn.close()
        return {
            "status": "HOUSEHOLD_MEMBER_ADDED",
            "action_id": req.action_id,
            "title": f"Added {relation} to Orbit"
        }
        
    # Handle Smart Contextual Reminder
    if req.action_id == "opt_smart_reminder":
        conn = get_db()
        cursor = conn.cursor()
        rem_id = f"ctx_rem_{os.urandom(4).hex()}"
        cursor.execute("INSERT INTO contextual_reminders (id, internal_uuid, intent_text, proposed_time, status) VALUES (?, ?, ?, ?, ?)",
                       (rem_id, req.internal_uuid, req.title, "tomorrow at 9:45 AM", "PENDING"))
        cursor.execute("INSERT INTO chat_memories (memory_id, internal_uuid, role, content) VALUES (?, ?, ?, ?)",
                       (f"rem_log_{os.urandom(4).hex()}", req.internal_uuid, "system", f"Scheduled Smart Reminder: {req.title} for tomorrow at 9:45 AM"))
        
        # We also create an immediate notification just to prove it worked in the UI
        notif_id = f"notif_{os.urandom(4).hex()}"
        cursor.execute("INSERT INTO notifications (id, internal_uuid, text, is_read) VALUES (?, ?, ?, 0)",
                       (notif_id, req.internal_uuid, f"Contextual reminder set for tomorrow 9:45 AM: {req.title}"))
        
        conn.commit()
        conn.close()
        return {
            "status": "SMART_REMINDER_SET",
            "action_id": req.action_id,
            "title": "Smart Reminder Scheduled"
        }

    # Save standard reminder to db if it's a reminder
    if req.action_id == "opt_set_reminder" or "remind" in req.title.lower() or "alert" in req.title.lower():
        conn = get_db()
        cursor = conn.cursor()
        # Log to chat memories
        cursor.execute("INSERT INTO chat_memories (memory_id, internal_uuid, role, content) VALUES (?, ?, ?, ?)",
                       (f"rem_{os.urandom(4).hex()}", req.internal_uuid, "system", f"Set Reminder: {req.title}"))
        
        # Add to notifications popup
        notif_id = f"notif_{os.urandom(4).hex()}"
        cursor.execute("INSERT INTO notifications (id, internal_uuid, text, is_read) VALUES (?, ?, ?, 0)",
                       (notif_id, req.internal_uuid, req.title))
        
        conn.commit()
        conn.close()

    cal_conn = GoogleCalendarConnector(prompt_if_missing=False)
    
    if cal_conn.is_connected():
        # Insert real block directly onto Google Calendar
        import datetime
        now = datetime.datetime.now()
        start = (now + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:00:00+05:30")
        end = (now + datetime.timedelta(hours=3, minutes=30)).strftime("%Y-%m-%dT%H:00:00+05:30")
        
        cal_res = cal_conn.insert_calendar_block(
            title=req.title,
            start_iso=start,
            end_iso=end,
            description="Protected time block scheduled automatically by Veya AI"
        )
        return {
            "status": "EXECUTED_ON_GOOGLE_CALENDAR",
            "action_id": req.action_id,
            "title": req.title,
            "calendar_event": cal_res
        }
    else:
        return {
            "status": "EXECUTED_LOCAL_ONLY",
            "action_id": req.action_id,
            "title": req.title,
            "calendar_event": {"id": "mock_evt_local", "status": "CONFIRMED"}
        }

# --- LIVING TWIN INSIGHTS ---
@app.get("/api/insights")
def get_insights(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_id, persona_name, work_stress_level, twin_maturity_weeks FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    p = cursor.fetchone()
    conn.close()

    if p and p["persona_name"] == "Vaibhav":
        return {
            "twin_maturity": f"Week {p['twin_maturity_weeks']} Maturity",
            "actionable_advice": {
                "text": "You have 5.5 hours of meetings today. You are at high risk of burnout. Block 30 mins to learn something new to break the monotony.",
                "nudge_action": "Remind me to read an article at 4:30 PM"
            },
            "scores": [
                {"id": "energy", "name": "Energy Balance", "value": 42, "category": "Biological", "status": "Critical"},
                {"id": "family", "name": "Relational Deficit", "value": 55, "category": "Family", "status": "Warning"},
                {"id": "learning", "name": "Learning Goals", "value": 85, "category": "Growth", "status": "Optimal"},
                {"id": "work", "name": "Meeting Load", "value": 92, "category": "Work", "status": "Heavy"}
            ]
        }

    if p and p["work_stress_level"] == "High":
        energy_score, focus_score, prod_score = 62, 78, 85
        actionable_advice = {
            "text": "Your typing pattern and schedule show high stress. If you're at the office, go sit in the light for 5 mins. If WFH, step onto the balcony.",
            "nudge_action": "Remind me to take a 5 min light break after lunch"
        }
    else:
        energy_score, focus_score, prod_score = 75, 82, 80
        actionable_advice = {
            "text": "You are maintaining a good rhythm. Protect your evening transition window.",
            "nudge_action": "Remind me to start evening wind-down at 6:30 PM"
        }

    return {
        "twin_maturity": f"Week {p['twin_maturity_weeks'] if p else 1} Maturity",
        "actionable_advice": actionable_advice,
        "scores": [
            {"id": "energy", "name": "Energy Balance", "value": energy_score, "category": "Biological & Rest", "status": "Moderate"},
            {"id": "focus", "name": "Focus Capacity", "value": focus_score, "category": "Cognitive Rhythms", "status": "Optimal"},
            {"id": "productivity", "name": "Sustainable Output", "value": prod_score, "category": "Schedule Health", "status": "Balanced"}
        ]
    }

@app.post("/api/insights/derive")
def derive_insight(req: DeriveRequest):
    explanation_json = derive_metric_explanation(req.internal_uuid, req.metric_name, req.score)
    import json
    try:
        parsed = json.loads(explanation_json)
    except json.JSONDecodeError:
        parsed = {
            "reason": "Veya is still calibrating your baseline signals.",
            "recommendation": "Wear your fitness tracker to bed tonight for better analysis.",
            "provenance": ["Calibrating Baseline", "Missing Data"]
        }
    return {
        "metric": req.metric_name,
        "score": req.score,
        "reason": parsed.get("reason", ""),
        "recommendation": parsed.get("recommendation", ""),
        "provenance": parsed.get("provenance", [])
    }

# --- PLANNING MODULE ---
@app.get("/api/planning/tomorrow")
def get_tomorrow_plan(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_name FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    p = cursor.fetchone()
    conn.close()

    if p and p["persona_name"] == "Vaibhav":
        return {
            "date": "Tomorrow",
            "summary": "High Meeting Load (Optimize for Learning & Family)",
            "existing_items": [
                {"id": "cal_1", "time": "09:00 AM - 10:30 AM", "title": "Quarterly Strategy Review", "priority": "High", "status": "Active"},
                {"id": "cal_2", "time": "11:00 AM - 12:00 PM", "title": "1:1 with VP Engineering", "priority": "Medium", "status": "Active"},
                {"id": "cal_3", "time": "01:00 PM - 03:00 PM", "title": "Architecture Sync (Back-to-Back)", "priority": "Medium", "status": "Active"},
                {"id": "cal_4", "time": "03:30 PM - 04:30 PM", "title": "Hiring Committee", "priority": "High", "status": "Active"}
            ],
            "suggested_items": [
                {"id": 1, "time": "07:00 AM - 08:00 AM", "title": "Morning Gym & Podcast", "priority": "High", "rationale": "Targeting your Health & Learning anchors before the meeting rush.", "status": "Active"},
                {"id": 3, "time": "06:30 PM - 08:00 PM", "title": "Math Help with Rohan & Dinner", "priority": "High", "rationale": "Prioritizing your kid after a heavy work day.", "status": "Active"}
            ]
        }

    return {
        "date": "Tomorrow",
        "summary": "3-Anchor Balanced Day",
        "existing_items": [
            {"id": "cal_1", "time": "10:00 AM - 11:00 AM", "title": "Weekly Status Sync (Calendar)", "priority": "Medium", "status": "Active"},
            {"id": "cal_2", "time": "02:00 PM - 03:00 PM", "title": "Cross-Team Review (Calendar)", "priority": "Medium", "status": "Active"}
        ],
        "suggested_items": [
            {"id": 1, "time": "09:00 AM - 09:45 AM", "title": "Deep Product Synthesis", "priority": "High", "rationale": "High cognitive focus window before your 10 AM sync.", "status": "Active"},
            {"id": 3, "time": "06:00 PM - 08:30 PM", "title": "Protected Family & Dinner Block", "priority": "High", "rationale": "Preserves essential evening recovery time.", "status": "Active"}
        ]
    }

@app.post("/api/planning/feasibility")
def adjust_plan(req: FeasibilityRequest):
    result = adjust_tomorrow_plan(req.internal_uuid, req.item_id, req.new_status)
    return result

# --- STATIC FILES ---
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "veya_web")
if os.path.exists(STATIC_DIR):
    app.mount("/app", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    init_db()
    init_auth_tables()
    uvicorn.run("veya_server.main:app", host="0.0.0.0", port=8080, reload=True)
