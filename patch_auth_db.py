import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "veya_data", "veya_app.db")

def patch_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE user_accounts ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        pass # Column might already exist
        
    # Set username to whatever email is right now for backward compatibility
    cursor.execute("UPDATE user_accounts SET username = email WHERE username IS NULL")
    
    conn.commit()
    conn.close()
    print("Patched user_accounts table")

if __name__ == '__main__':
    patch_db()
