import unittest
import os
import json
import sqlite3
from veya_data.db_schema import init_db, get_or_create_user, DB_PATH
from veya_agents.tools import derive_metric_explanation, adjust_tomorrow_plan

class TestVeyaSystem(unittest.TestCase):

    def setUp(self):
        init_db()
        self.user_uuid = get_or_create_user("test_user@gmail.com", persona_id="meera_pm")

    def test_pseudonymization_isolation(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify auth_vault maps email to internal_uuid
        cursor.execute("SELECT internal_uuid FROM auth_vault WHERE email = ?", ("test_user@gmail.com",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], self.user_uuid)
        
        # Verify twin_profiles has no email column (PII isolated)
        cursor.execute("PRAGMA table_info(twin_profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        self.assertNotIn("email", columns)
        self.assertNotIn("phone_number", columns)
        conn.close()

    def test_metric_derivation(self):
        result_json = derive_metric_explanation(self.user_uuid, "energy")
        data = json.loads(result_json)
        self.assertIn("metric_title", data)
        self.assertGreaterEqual(len(data["explanation_lines"]), 5) # 5-10 line requirement

    def test_tomorrow_plan_adjustment(self):
        # Seed test plan
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        actions = [{"num": 1, "action": "Test Action", "reason": "Test Reason"}]
        cursor.execute(
            "INSERT OR REPLACE INTO tomorrow_plans (plan_id, internal_uuid, plan_date, action_items, status) VALUES (?, ?, ?, ?, ?)",
            ("plan_test", self.user_uuid, "2026-08-25", json.dumps(actions), "PENDING")
        )
        conn.commit()
        conn.close()

        # Adjust plan item 1
        res = adjust_tomorrow_plan(self.user_uuid, 1, "Call is too late")
        self.assertIn("successfully adjusted", res)

if __name__ == "__main__":
    unittest.main()
