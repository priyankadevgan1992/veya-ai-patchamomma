import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

test_models = [
    'models/gemini-3.1-flash-lite',
    'models/gemini-3.5-flash-lite', 
    'models/gemini-3.5-flash',
    'models/gemini-3.6-flash',
    'models/gemini-pro',
    'models/gemini-1.5-flash',
    'models/gemma-4-26b-a4b-it'
]

working = []
for m in test_models:
    try:
        res = client.models.generate_content(model=m, contents='say hi')
        print(f"SUCCESS: {m} -> {res.text}")
        working.append(m)
    except Exception as e:
        print(f"FAILED: {m} -> {type(e).__name__}: {str(e).split('.')[0]}")

print("Working models:", working)
