import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

working = []
print("Fetching available models...")
models = list(client.models.list())
for m in models:
    name = m.name
    if "flash" in name or "pro" in name or "gemma" in name:
        try:
            res = client.models.generate_content(model=name, contents='hi')
            print(f"SUCCESS: {name}")
            working.append(name)
            break # just need one
        except Exception as e:
            # print(f"FAILED: {name} -> {type(e).__name__}")
            pass

print("\nFirst working model found:", working)
