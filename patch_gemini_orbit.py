import json

def patch_gemini_engine():
    with open('veya_agents/gemini_engine.py', 'r', encoding='utf-8') as f:
        text = f.read()

    old_context_block = """  User Profile & Context:
- Onboarding Completed: {context.get('onboarding_completed', False)}
- Persona: {context.get('persona_name')} ({context.get('persona_id')})
- Life Anchor: {context.get('life_anchor')}
- Stress Level: {context.get('work_stress_level')}
- Upcoming Live Google Calendar Events: {json.dumps(context.get('calendar_events', []))}
- Recent Chat History: {json.dumps(context.get('recent_chat_history', [])[-4:])}"""

    new_context_block = """  User Profile & Context:
- Onboarding Completed: {context.get('onboarding_completed', False)}
- Persona: {context.get('persona_name')} ({context.get('persona_id')})
- Life Anchor: {context.get('life_anchor')}
- Stress Level: {context.get('work_stress_level')}
- Household Orbit / Key People: {json.dumps(context.get('household_members', []))}
- Upcoming Live Google Calendar Events: {json.dumps(context.get('calendar_events', []))}
- Recent Chat History: {json.dumps(context.get('recent_chat_history', [])[-4:])}"""

    if old_context_block in text:
        text = text.replace(old_context_block, new_context_block)
        with open('veya_agents/gemini_engine.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Updated gemini_engine.py prompt context')
    else:
        print('Could not find exact block in gemini_engine.py. Trying regex...')
        import re
        text = re.sub(
            r'(- Stress Level: \{context.get\(\'work_stress_level\'\)\})',
            r'\1\n  - Household Orbit / Key People: {json.dumps(context.get(\'household_members\', []))}',
            text
        )
        with open('veya_agents/gemini_engine.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Updated using regex.')

if __name__ == '__main__':
    patch_gemini_engine()
