def patch_backend():
    with open('veya_server/main.py', 'r', encoding='utf-8') as f:
        text = f.read()
    
    old_model = '''class ProfileUpdateRequest(BaseModel):
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

    new_model = old_model + '\n    orbit: list = []'
    text = text.replace(old_model, new_model)

    old_upd = '''          req.calendars_connected, req.wearable_connected, req.twin_maturity_weeks,
          req.internal_uuid))'''

    new_upd = old_upd + '''
    
    cursor.execute("DELETE FROM household_profiles WHERE internal_uuid = ?", (req.internal_uuid,))
    for o in req.orbit:
        name = o.get('person_name', '').strip()
        rel = o.get('relationship_type', '').strip()
        if name and rel:
            import uuid
            pid = 'o_' + uuid.uuid4().hex[:12]
            cursor.execute("INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type) VALUES (?, ?, ?, ?)", (pid, req.internal_uuid, name, rel))
    '''
    text = text.replace(old_upd, new_upd)
    
    with open('veya_server/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Backend orbit saving patched")

if __name__ == '__main__':
    patch_backend()
