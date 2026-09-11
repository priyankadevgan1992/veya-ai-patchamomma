import json
from veya_agents.agent_system import orchestrator
from veya_agents.gemini_engine import GeminiLLMEngine

reply = orchestrator.process_message('test', 'give me options in my slot')
print('SYSTEM OUTPUT:')
print(json.dumps(reply, indent=2))
