with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace get_tomorrow_plan
old_get_tomorrow = '''@app.get("/api/planning/tomorrow")
def get_tomorrow_plan(uuid: str):
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
    }'''

new_get_tomorrow = '''@app.get("/api/planning/tomorrow")
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
    }'''

text = text.replace(old_get_tomorrow, new_get_tomorrow)

# Replace get_insights
old_get_insights = '''@app.get("/api/insights")
def get_insights(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_id, work_stress_level, twin_maturity_weeks FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    p = cursor.fetchone()
    conn.close()

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

    return {'''

new_get_insights = '''@app.get("/api/insights")
def get_insights(uuid: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_id, persona_name, work_stress_level, twin_maturity_weeks FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    p = cursor.fetchone()
    conn.close()

    if p and p["persona_name"] == "Vaibhav":
        return {
            "energy_capacity": 42,
            "focus_depth": 85,
            "productivity_index": 92,
            "actionable_advice": {
                "text": "You have 5.5 hours of meetings today. You are at high risk of burnout. Block 30 mins to learn something new to break the monotony.",
                "nudge_action": "Remind me to read an article at 4:30 PM"
            },
            "metrics": [
                {"name": "Cognitive Load", "value": "Heavy", "trend": "up", "details": "Back-to-back architecture syncs."},
                {"name": "Relational Deficit", "value": "Rohan & Priya", "trend": "down", "details": "You've been working late. Time with wife and kid is dropping."}
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

    return {'''

text = text.replace(old_get_insights, new_get_insights)

with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched main.py for Vaibhav insights and plans')
