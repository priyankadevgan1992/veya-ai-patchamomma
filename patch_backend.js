const fs = require('fs');

// 1. main.py
let mainCode = fs.readFileSync('veya_server/main.py', 'utf8');
mainCode = mainCode.replace(
  /class ChatRequest\(BaseModel\):\r?\n\s*internal_uuid: str\r?\n\s*message: str/,
  'class ChatRequest(BaseModel):\n    internal_uuid: str\n    message: str\n    media_data: Optional[str] = None\n    media_mime_type: Optional[str] = None'
);
mainCode = mainCode.replace(
  /def chat_stream\(req: ChatRequest\):\r?\n\s*response_payload = orchestrator\.process_message\(req\.internal_uuid, req\.message\)/,
  'def chat_stream(req: ChatRequest):\n    response_payload = orchestrator.process_message(req.internal_uuid, req.message, req.media_data, req.media_mime_type)'
);
fs.writeFileSync('veya_server/main.py', mainCode, 'utf8');

// 2. agent_system.py
let agentCode = fs.readFileSync('veya_agents/agent_system.py', 'utf8');
agentCode = agentCode.replace(
  'def process_message(self, internal_uuid: str, user_message: str) -> Dict[str, Any]:',
  'def process_message(self, internal_uuid: str, user_message: str, media_data: str = None, media_mime_type: str = None) -> Dict[str, Any]:'
);
agentCode = agentCode.replace(
  'llm_reply = self.gemini_engine.generate_chat_response(COMPANION_SYSTEM_PROMPT, user_message, context)',
  'llm_reply = self.gemini_engine.generate_chat_response(COMPANION_SYSTEM_PROMPT, user_message, context, media_data, media_mime_type)'
);
fs.writeFileSync('veya_agents/agent_system.py', agentCode, 'utf8');

// 3. gemini_engine.py
let engineCode = fs.readFileSync('veya_agents/gemini_engine.py', 'utf8');
engineCode = engineCode.replace(
  'def generate_chat_response(self, system_instruction: str, user_message: str, context: Dict[str, Any]) -> str:',
  'def generate_chat_response(self, system_instruction: str, user_message: str, context: Dict[str, Any], media_data: str = None, media_mime_type: str = None) -> str:'
);

const oldContentsCall = `                    res = self.client.models.generate_content(
                        model=m,
                        contents=prompt
                    )`;
                    
const newContentsCall = `                    contents = [prompt]
                    if media_data and media_mime_type:
                        import base64
                        from google.genai import types
                        try:
                            if "data:" in media_data and "base64," in media_data:
                                media_data = media_data.split("base64,")[1]
                            media_bytes = base64.b64decode(media_data)
                            part = types.Part.from_bytes(data=media_bytes, mime_type=media_mime_type)
                            contents.append(part)
                        except Exception as e:
                            print(f"Media encoding failed: {e}")

                    res = self.client.models.generate_content(
                        model=m,
                        contents=contents
                    )`;
engineCode = engineCode.replace(oldContentsCall, newContentsCall);
fs.writeFileSync('veya_agents/gemini_engine.py', engineCode, 'utf8');
console.log('Backend patched.');
