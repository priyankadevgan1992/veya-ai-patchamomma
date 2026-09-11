with open('veya_data/auth_db.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_schema = '''        CREATE TABLE IF NOT EXISTS user_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,'''

new_schema = '''        CREATE TABLE IF NOT EXISTS user_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT NOT NULL,'''

text = text.replace(old_schema, new_schema)

old_insert = '''        cursor.execute("""
            INSERT INTO user_accounts (email, password_hash, internal_uuid)
            VALUES (?, ?, ?)
        """, (test_email, test_pass, test_uuid))'''

new_insert = '''        cursor.execute("""
            INSERT INTO user_accounts (username, email, password_hash, internal_uuid)
            VALUES (?, ?, ?, ?)
        """, ('meera', test_email, test_pass, test_uuid))'''

text = text.replace(old_insert, new_insert)

with open('veya_data/auth_db.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched auth_db.py for username')
