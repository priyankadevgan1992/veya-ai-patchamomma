import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
resp = requests.get(url).json()

for model in resp.get("models", []):
    if "bidiGenerateContent" in model.get("supportedGenerationMethods", []):
        print(model["name"])
