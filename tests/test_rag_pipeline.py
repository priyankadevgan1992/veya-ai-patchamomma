import unittest
import json
import sqlite3
import os
from veya_data.db_schema import init_db, get_or_create_user, DB_PATH
from veya_agents.vector_rag import vector_store
from veya_agents.agent_system import orchestrator

class TestVectorRAGPipeline(unittest.TestCase):

    def setUp(self):
        init_db()
        self.meera_uuid = get_or_create_user("meera@gmail.com", persona_id="meera_pm")
        self.priya_uuid = get_or_create_user("priya@gmail.com", persona_id="priya_cycle")

    def test_vector_storage_and_retrieval(self):
        # Store an episodic memory
        doc_id = vector_store.store_memory(
            self.meera_uuid,
            "Husband is on a 4-day business trip to London; managing daughter's school routine alone.",
            category="FAMILY_EVENT"
        )
        self.assertTrue(doc_id.startswith("mem_"))

        # Query vector store
        results = vector_store.retrieve_relevant_context(self.meera_uuid, "Is my husband traveling?")
        self.assertGreater(len(results), 0)
        self.assertIn("husband", results[0]["document_text"].lower())

    def test_rag_agent_orchestration_flow(self):
        # Test full RAG-grounded conversation processing
        res = orchestrator.process_message(self.meera_uuid, "Managing alone while husband is traveling and have lots of meetings")
        self.assertIn("reply", res)
        self.assertTrue(res["has_action_card"])
        self.assertGreater(res["retrieved_memories_count"], 0)

if __name__ == "__main__":
    unittest.main()
