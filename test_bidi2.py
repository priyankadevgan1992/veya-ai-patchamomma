import asyncio
import websockets
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

async def test():
    model_name = "models/gemini-2.5-flash-native-audio-latest"
    uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    
    try:
        async with websockets.connect(uri) as gemini_ws:
            setup_msg = {
                "setup": {
                    "model": model_name,
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": "Aoede" # Warm female voice
                                }
                            }
                        }
                    },
                    "systemInstruction": {
                        "parts": [{"text": "You are Veya."}]
                    }
                }
            }
            await gemini_ws.send(json.dumps(setup_msg))
            print("Sent setup")
            resp = await gemini_ws.recv()
            print("Received:", resp)
    except Exception as e:
        print("Error:", type(e), e)

asyncio.run(test())
