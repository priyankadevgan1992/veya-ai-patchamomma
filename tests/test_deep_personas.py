import unittest
import json
import sqlite3
import os
from veya_data.db_schema import init_db, get_or_create_user, DB_PATH
from veya_agents.context_agent import ContextAgent
from veya_agents.memory_graph import EvolvingMemoryGraph
from veya_agents.persona_scenarios import PersonaScenarioEngine
from veya_agents.agent_system import orchestrator

class TestDeepPersonaScenarios(unittest.TestCase):

    def setUp(self):
        init_db()
        self.meera_uuid = get_or_create_user("meera@gmail.com", persona_id="meera_pm")
        self.priya_uuid = get_or_create_user("priya@gmail.com", persona_id="priya_cycle")
        self.arjun_uuid = get_or_create_user("arjun@gmail.com", persona_id="arjun_sales")
        self.kavita_uuid = get_or_create_user("kavita@gmail.com", persona_id="kavita_homemaker")

    def test_memory_graph_extraction(self):
        graph = EvolvingMemoryGraph()
        facts = graph.extract_facts(self.meera_uuid, "My husband is traveling for 3 days and daughter has school exams", "meera_pm")
        self.assertEqual(facts.get("spouse_status"), "Traveling / Away")
        self.assertEqual(facts.get("family_priority"), "Children education / exam support")

    def test_meera_evening_protection_flow(self):
        res = orchestrator.process_message(self.meera_uuid, "Husband is traveling and I am managing alone")
        self.assertTrue(res["has_action_card"])
        self.assertEqual(res["actions"][0]["id"], "act_meera_dinner_block")

    def test_priya_luteal_cycle_flow(self):
        res = orchestrator.process_message(self.priya_uuid, "Feeling very low energy, cycle day 23 is tough")
        self.assertTrue(res["has_action_card"])
        self.assertIn("luteal", res["reply"].lower())
        self.assertEqual(res["actions"][0]["id"], "act_priya_walk")

    def test_arjun_pitch_prep_flow(self):
        res = orchestrator.process_message(self.arjun_uuid, "I need to prepare for Friday client presentation pitch")
        self.assertTrue(res["has_action_card"])
        self.assertIn("Wednesday", res["actions"][0]["title"])

    def test_kavita_medicine_reminder_flow(self):
        res = orchestrator.process_message(self.kavita_uuid, "Need to pick up mother-in-law's hypertension medicine")
        self.assertTrue(res["has_action_card"])
        self.assertIn("09:45 AM", res["actions"][0]["title"])

if __name__ == "__main__":
    unittest.main()
