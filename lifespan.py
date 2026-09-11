import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from veya_data.db_schema import init_db
from veya_data.auth_db import init_auth_tables
import seed_vaibhav

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup of the FastAPI app
    print("Initializing databases on startup...")
    init_db()
    init_auth_tables()
    try:
        seed_vaibhav.seed_vaibhav()
        print("Seeded Vaibhav test user.")
    except Exception as e:
        print("Failed to seed Vaibhav:", e)
    yield
    # Cleanup on shutdown could go here
