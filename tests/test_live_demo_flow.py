import unittest
import json
import sqlite3
import os
from veya_data.db_schema import init_db, DB_PATH
from veya_data.auth_db import init_auth_tables
from veya_agents.agent_system import orchestrator
from veya_server.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestLiveAuthAndDemoFlow(unittest.TestCase):

    def setUp(self):
        init_db()
        init_auth_tables()

    def test_live_signup_and_onboarding_flow(self):
        # 1. Real Signup with email & password
        email = f"demo_fresh_{os.urandom(3).hex()}@test.com"
        res = client.post("/api/auth/signup", json={"email": email, "password": "password123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        uuid = data["internal_uuid"]
        self.assertFalse(data["onboarding_completed"])

        # 2. Check Home initial greeting
        home_res = client.get(f"/api/home?uuid={uuid}")
        self.assertIn("what name would you like me to call you", home_res.json()["greeting"].lower())

        # 3. Conversational Onboarding Turn 1: Name
        t1 = client.post("/api/chat", json={"internal_uuid": uuid, "message": "Ananya"})
        self.assertIn("Ananya", t1.json()["reply"])
        self.assertTrue(t1.json()["onboarding_active"])

        # 4. Conversational Onboarding Turn 2: Role
        t2 = client.post("/api/chat", json={"internal_uuid": uuid, "message": "Founder & Lead Designer"})
        self.assertIn("protect ONE", t2.json()["reply"])

        # 5. Conversational Onboarding Turn 3: Life Anchor
        t3 = client.post("/api/chat", json={"internal_uuid": uuid, "message": "Morning meditation and evening family dinner"})
        self.assertIn("locked that into your Digital Twin", t3.json()["reply"])
        self.assertFalse(t3.json()["onboarding_active"])

    def test_enriched_testing_profile_signin(self):
        # Real Signin with enriched test account
        res = client.post("/api/auth/signin", json={"email": "test@veya.ai", "password": "password123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["onboarding_completed"])
        self.assertEqual(data["persona_name"], "Meera Sharma")

if __name__ == "__main__":
    import os
    unittest.main()
