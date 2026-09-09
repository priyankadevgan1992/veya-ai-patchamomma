import unittest
import json
import sqlite3
import os
from veya_data.db_schema import init_db, DB_PATH
from veya_data.auth_db import init_auth_tables
from veya_agents.cognitive_matrix import cognitive_matrix
from veya_agents.agent_system import orchestrator

class TestCognitiveMatrixAndTradeoffs(unittest.TestCase):

    def setUp(self):
        init_db()
        init_auth_tables()
        self.uuid = "uuid_test_enriched_001"

    def test_cognitive_matrix_evaluation(self):
        context = {
            "calendar_events": [
                {"title": "Exec Review", "start": "14:00", "end": "15:00"},
                {"title": "Product Sync", "start": "15:00", "end": "16:00"},
                {"title": "Late US Sync", "start": "18:00", "end": "19:00"}
            ],
            "work_stress_level": "High",
            "biological_phase": "Luteal"
        }
        res = cognitive_matrix.evaluate_cognitive_state(self.uuid, context)
        
        # Verify attention residue and downstream risk calculated
        self.assertGreater(res["temporal"]["attention_residue_minutes"], 0)
        self.assertGreaterEqual(res["downstream_carryover_risk"], 80)
        self.assertTrue(res["relational"]["spouse_away"])

    def test_tradeoff_action_negotiation_options(self):
        # User expresses evening overload
        res = orchestrator.process_message(self.uuid, "Managing alone while husband travels and have a hectic evening sync")
        self.assertTrue(res["has_action_card"])
        self.assertEqual(res["action_card_type"], "TRADE_OFF_NEGOTIATION")
        
        # Verify 3 realistic trade-off options are provided
        self.assertGreaterEqual(len(res["actions"]), 2)
        titles = [a["title"] for a in res["actions"]]
        self.assertTrue(any("Option A" in t for t in titles))
        self.assertTrue(any("Option B" in t for t in titles))

if __name__ == "__main__":
    unittest.main()
