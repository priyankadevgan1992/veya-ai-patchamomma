import os

def patch_backend():
    with open('veya_server/main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update ProfileUpdateRequest
    old_req = '''class ProfileUpdateRequest(BaseModel):
    internal_uuid: str
    persona_name: str
    work_stress_level: str
    life_anchor: str'''
    
    new_req = '''class ProfileUpdateRequest(BaseModel):
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
    twin_maturity_weeks: int = 0'''

    content = content.replace(old_req, new_req)

    # 2. Update get_profile
    old_get = '''cursor.execute("SELECT persona_name, work_stress_level, life_anchor FROM twin_profiles WHERE internal_uuid = ?", (uuid,))
    p = cursor.fetchone()'''
    
    new_get = '''cursor.execute("""
        SELECT persona_name, work_stress_level, life_anchor, gender_identity, 
               household_members, relationship_health, biological_phase,
               calendars_connected, wearable_connected, twin_maturity_weeks 
        FROM twin_profiles WHERE internal_uuid = ?""", (uuid,))
    p = cursor.fetchone()'''

    content = content.replace(old_get, new_get)

    old_ret = '''if p:
        return {
            "persona_name": p["persona_name"],
            "work_stress_level": p["work_stress_level"],
            "life_anchor": p["life_anchor"],
            "reminders": reminders,
            "orbit": orbit
        }
    return {"persona_name": "", "work_stress_level": "Moderate", "life_anchor": "", "reminders": [], "orbit": []}'''

    new_ret = '''if p:
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
    }'''

    content = content.replace(old_ret, new_ret)

    # 3. Update update_profile
    old_upd = '''cursor.execute("""
        UPDATE twin_profiles 
        SET persona_name = ?, work_stress_level = ?, life_anchor = ? 
        WHERE internal_uuid = ?
    """, (req.persona_name, req.work_stress_level, req.life_anchor, req.internal_uuid))'''

    new_upd = '''cursor.execute("""
        UPDATE twin_profiles 
        SET persona_name = ?, work_stress_level = ?, life_anchor = ?,
            gender_identity = ?, household_members = ?, relationship_health = ?,
            biological_phase = ?, calendars_connected = ?, wearable_connected = ?,
            twin_maturity_weeks = ?
        WHERE internal_uuid = ?
    """, (req.persona_name, req.work_stress_level, req.life_anchor, req.gender_identity,
          req.household_members, req.relationship_health, req.biological_phase,
          req.calendars_connected, req.wearable_connected, req.twin_maturity_weeks,
          req.internal_uuid))'''

    content = content.replace(old_upd, new_upd)

    with open('veya_server/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backend patched successfully")

if __name__ == "__main__":
    patch_backend()
