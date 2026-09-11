with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_insights = '''def get_insights(uuid: str):
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
        }'''

new_insights = '''def get_insights(uuid: str):
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
        }'''

text = text.replace(old_insights, new_insights)

with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched main.py for Vaibhav insights format')
