import json
from veya_agents.gemini_engine import GeminiLLMEngine

engine = GeminiLLMEngine()
reply = engine.generate_chat_response('You are a helpful assistant.', 'give me options in my slot', {})
print('LLM OUTPUT:')
print(reply)
