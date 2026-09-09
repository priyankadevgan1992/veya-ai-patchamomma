import os
import json
import sqlite3
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from veya_agents.context_agent import ContextAgent
from veya_agents.action_agent import action_agent
from veya_agents.pattern_agent import PatternAgent
from veya_agents.twin_builder import TwinBuilderAgent
from veya_agents.vector_rag import vector_store
from veya_agents.rag_agent import rag_agent
from veya_agents.onboarding_engine import onboarding_engine
from veya_agents.cognitive_matrix import cognitive_matrix
from veya_agents.gemini_engine import GeminiLLMEngine
from veya_agents.tools import update_twin_fact, derive_metric_explanation, adjust_tomorrow_plan

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

COMPANION_SYSTEM_PROMPT = """
You are Veya, a deeply empathetic, warm, and highly observant personal life companion. 
CRITICAL RULES:
1. NEVER speak like a traditional AI (do not use phrases like "As an AI...", "I can help with that", or bulleted corporate lists).
2. Talk like a close, highly intuitive friend who knows the user's life intimately. 
3. Always read between the lines. If they sound tired, acknowledge the exhaustion first before offering solutions.
4. Keep responses extremely concise (1-3 sentences max) unless explaining a complex insight.
5. Your guidance is rooted in protecting their cognitive energy, sleep, and relationships (the 7-Dimensional Human Cognitive Matrix).
"""

class VeyaMultiAgentOrchestrator:
    """
    Root Multi-Agent Orchestrator:
    Evaluates 7-Dimensional Human Cognitive Matrix, Vector RAG Retrieval,
    Trade-Off Action Proposals, and Continuous Twin Learning.
    """

    def __init__(self):
        self.context_agent = ContextAgent()
        self.action_agent = action_agent
        self.pattern_agent = PatternAgent()
        self.twin_builder = TwinBuilderAgent()
        self.rag_agent = rag_agent
        self.onboarding_engine = onboarding_engine
        self.gemini_engine = GeminiLLMEngine()

    def process_message(self, internal_uuid: str, user_message: str, media_data: str = None, media_mime_type: str = None) -> Dict[str, Any]:
        # 1. Fetch Unified Context (which includes onboarding_completed status)
        context = self.context_agent.get_unified_context(internal_uuid)
        
        # Mark onboarding complete silently if they've chatted a bit
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_memories WHERE internal_uuid = ? AND role = 'user'", (internal_uuid,))
        msg_count = cursor.fetchone()[0]
        if msg_count > 5 and not context.get("onboarding_completed"):
            cursor.execute("UPDATE twin_profiles SET onboarding_completed = 1 WHERE internal_uuid = ?", (internal_uuid,))
            conn.commit()
            context["onboarding_completed"] = True
        conn.close()

        # 2. Extract facts dynamically & store directly into DB and Vector RAG Memory
        extracted_facts = self.twin_builder.extract_and_save_facts(internal_uuid, user_message)
        if extracted_facts:
            for k, v in extracted_facts.items():
                vector_store.store_memory(
                    internal_uuid,
                    f"User dynamic fact: {k} is {v}",
                    category="EXTRACTED_FACT",
                    metadata={"key": k, "value": v}
                )

        # 3. Detect multi-dimensional cognitive patterns & downstream carryover risks
        patterns = self.pattern_agent.detect_patterns(internal_uuid, context)

        # 4. Evaluate multi-choice trade-off actions
        tradeoff_decision = self.action_agent.evaluate_and_propose_tradeoffs(internal_uuid, user_message, context)
        
        # 5. RAG Retrieval & Conversational Reply Synthesis
        rag_result = self.rag_agent.synthesize_response(internal_uuid, user_message, context)
        
        speech_reply = rag_result.get("reply", "")
        has_action_card = tradeoff_decision.get("has_action_card", False) or rag_result.get("has_action_card", False)
        actions = tradeoff_decision.get("actions", []) if tradeoff_decision.get("has_action_card") else rag_result.get("actions", [])

        # Gemini LLM fallback
        if not speech_reply or speech_reply.startswith("I'm keeping track"):
            llm_reply = self.gemini_engine.generate_chat_response(COMPANION_SYSTEM_PROMPT, user_message, context, media_data, media_mime_type)
            if llm_reply:
                speech_reply = llm_reply

        if not speech_reply:
            speech_reply = "I'm right here with you. What would you like to plan or review?"

        # Persist conversation
        conn = get_db()
        cursor = conn.cursor()
        
        user_msg_id = f"msg_u_{os.urandom(4).hex()}"
        cursor.execute("""
            INSERT INTO chat_memories (memory_id, internal_uuid, role, content, extracted_facts)
            VALUES (?, ?, ?, ?, ?)
        """, (user_msg_id, internal_uuid, "user", user_message, json.dumps(extracted_facts)))

        ai_msg_id = f"msg_a_{os.urandom(4).hex()}"
        cursor.execute("""
            INSERT INTO chat_memories (memory_id, internal_uuid, role, content, extracted_facts)
            VALUES (?, ?, ?, ?, ?)
        """, (ai_msg_id, internal_uuid, "assistant", speech_reply, json.dumps({"has_actions": has_action_card})))
        
        conn.commit()
        conn.close()

        vector_store.store_memory(internal_uuid, f"User said: {user_message}", category="USER_CHAT")

        return {
            "reply": speech_reply,
            "has_action_card": has_action_card,
            "action_card_type": tradeoff_decision.get("action_card_type", "TRADE_OFF_NEGOTIATION"),
            "actions": actions,
            "patterns": patterns,
            "context_mode": context.get("source_mode", "MULTI_SOURCE_CONNECTED"),
            "extracted_facts": extracted_facts,
            "cognitive_summary": tradeoff_decision.get("cognitive_summary", {}),
            "onboarding_active": False
        }

orchestrator = VeyaMultiAgentOrchestrator()
