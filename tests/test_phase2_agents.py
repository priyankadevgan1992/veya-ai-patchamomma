import unittest
import json
import sqlite3
import os
from veya_data.db_schema import init_db, get_or_create_user, DB_PATH
from veya_agents.context_agent import ContextAgent
from veya_agents.action_agent import ActionAgent
from veya_agents.pattern_agent import PatternAgent
from veya_agents.twin_builder import TwinBuilderAgent
from veya_agents.agent_system import orchestrator

class TestPhase2MultiAgentSystem(unittest.TestCase):

    def setUp(self):
        init_db()
        self.user_uuid = get_or_create_user("meera@gmail.com", persona_id="meera_pm")

    def test_context_agent_adaptive_degradation(self):
        agent = ContextAgent()
        ctx = agent.get_unified_context(self.user_uuid)
        self.assertEqual(ctx["persona_id"], "meera_pm")
        self.assertIn("source_mode", ctx)
        self.assertIn(ctx["source_mode"], ["LIVE_GOOGLE_CALENDAR_CONNECTED", "MULTI_SOURCE_CONNECTED", "CALENDAR_ONLY", "CONVERSATIONAL_ONLY"])

    def test_pattern_agent_confidence_scores(self):
        agent = PatternAgent()
        patterns = agent.detect_patterns(self.user_uuid, {"persona_id": "meera_pm"})
        self.assertTrue(len(patterns) > 0)
        self.assertGreaterEqual(patterns[0]["confidence_score"], 0.8)

    def test_action_agent_concrete_proposals(self):
        agent = ActionAgent()
        res = agent.evaluate_and_propose_actions(self.user_uuid, "yes pls - tell me what can i do", {"persona_id": "meera_pm"})
        self.assertTrue(res["has_action_card"])
        self.assertEqual(len(res["actions"]), 2)
        self.assertEqual(res["actions"][0]["id"], "act_reschedule_1")

    def test_twin_builder_fact_extraction(self):
        agent = TwinBuilderAgent()
        facts = agent.extract_and_save_facts(self.user_uuid, "Today was a crazy day, feeling exhausted")
        self.assertEqual(facts.get("work_stress_level"), "High")

    def test_orchestrator_end_to_end_flow(self):
        result = orchestrator.process_message(self.user_uuid, "yes pls - tell me what can i do")
        self.assertTrue(result["has_action_card"])
        self.assertTrue(len(result["actions"]) > 0)

if __name__ == "__main__":
    unittest.main()
