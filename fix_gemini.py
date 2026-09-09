import os

with open('veya_agents/gemini_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(r"context.get(\'household_members\', [])", "context.get('household_members', [])")

with open('veya_agents/gemini_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed syntax in gemini_engine.py")
