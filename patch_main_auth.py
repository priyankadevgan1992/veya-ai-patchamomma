with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace AuthRequest
old_auth = '''class AuthRequest(BaseModel):
    email: str
    password: str'''
new_auth = '''class AuthRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""'''
text = text.replace(old_auth, new_auth)

# Replace signup logic
old_signup = '''@app.post("/api/auth/signup")
def signup(req: AuthRequest):
    email = req.email.strip().lower()
    if not email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM user_accounts WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Account already exists. Please sign in.")

    # Create new fresh user account
    internal_uuid = f"uuid_usr_{os.urandom(6).hex()}"
    pass_hash = hash_password(req.password)

    cursor.execute("""
        INSERT INTO twin_profiles'''

new_signup = '''@app.post("/api/auth/signup")
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
        INSERT INTO twin_profiles'''
text = text.replace(old_signup, new_signup)

# Now fix the user_accounts insert
old_insert_ua = '''cursor.execute("""
        INSERT INTO user_accounts (email, password_hash, internal_uuid)
        VALUES (?, ?, ?)
    """, (email, pass_hash, internal_uuid))'''

new_insert_ua = '''cursor.execute("""
        INSERT INTO user_accounts (username, email, password_hash, internal_uuid)
        VALUES (?, ?, ?, ?)
    """, (username, email, pass_hash, internal_uuid))'''

text = text.replace(old_insert_ua, new_insert_ua)

# Replace signin logic
old_signin = '''@app.post("/api/auth/signin")
def signin(req: AuthRequest):
    email = req.email.strip().lower()
    pass_hash = hash_password(req.password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT internal_uuid, password_hash FROM user_accounts WHERE email = ?", (email,))'''

new_signin = '''@app.post("/api/auth/signin")
def signin(req: AuthRequest):
    username = req.username.strip().lower()
    pass_hash = hash_password(req.password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT internal_uuid, password_hash FROM user_accounts WHERE username = ? OR email = ?", (username, username))'''

text = text.replace(old_signin, new_signin)

with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched main.py for username auth')
