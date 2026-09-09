import os

def patch_backend():
    with open('veya_server/main.py', 'r', encoding='utf-8') as f:
        py = f.read()

    # GET profile orbit fetch
    old_orbit_fetch = '''cursor.execute("SELECT person_name, relationship_type FROM household_profiles WHERE internal_uuid = ?", (uuid,))
    orbit_rows = cursor.fetchall()
    orbit = [{"person_name": r["person_name"], "relationship_type": r["relationship_type"]} for r in orbit_rows]'''
    
    new_orbit_fetch = '''cursor.execute("SELECT person_name, relationship_type, key_context, importance_percent FROM household_profiles WHERE internal_uuid = ?", (uuid,))
    orbit_rows = cursor.fetchall()
    orbit = [{"person_name": r["person_name"], "relationship_type": r["relationship_type"], "key_context": r["key_context"], "importance_percent": r["importance_percent"]} for r in orbit_rows]'''
    
    py = py.replace(old_orbit_fetch, new_orbit_fetch)

    # POST profile orbit save
    old_orbit_save = '''cursor.execute("INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type) VALUES (?, ?, ?, ?)", (pid, req.internal_uuid, name, rel))'''
    
    new_orbit_save = '''ctx = o.get('key_context', '').strip()
            imp = int(o.get('importance_percent', 50))
            cursor.execute("INSERT INTO household_profiles (profile_id, internal_uuid, person_name, relationship_type, key_context, importance_percent) VALUES (?, ?, ?, ?, ?, ?)", (pid, req.internal_uuid, name, rel, ctx, imp))'''

    py = py.replace(old_orbit_save, new_orbit_save)

    with open('veya_server/main.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Backend patched")

if __name__ == '__main__':
    patch_backend()
