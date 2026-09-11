with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_app = 'app = FastAPI(title="Veya AI Life Companion API", version="2.0.0")'

new_app = '''from contextlib import asynccontextmanager

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

app = FastAPI(title="Veya AI Life Companion API", version="2.0.0", lifespan=lifespan)'''

text = text.replace(old_app, new_app)

with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched main.py for lifespan')
