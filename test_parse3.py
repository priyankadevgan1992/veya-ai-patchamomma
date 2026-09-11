import json

def parse_llm(llm_reply):
    speech_reply = llm_reply
    actions = []
    has_action_card = False
    
    start_idx = llm_reply.find("{")
    end_idx = llm_reply.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        try:
            parsed = json.loads(llm_reply[start_idx:end_idx+1])
            speech_reply = parsed.get("reply", llm_reply[:start_idx].strip() or llm_reply)
            if parsed.get("actions"):
                has_action_card = True
                actions = parsed.get("actions")
        except Exception as e:
            pass
            
    return speech_reply, has_action_card, actions

res = parse_llm('''Hey! You want to schedule a match? Is this for Rohan's football practice, or something else? Let me see what we can find for you. { "reply": "Hey! You want to schedule a match? Is this for Rohan's football practice, or something else? Let me see what we can find for you.", "actions": [ { "id": "dyn_action_1", "title": "Find Football Practice Slot for Rohan", "description": "Check Rohan's schedule for available football practice times.", "type": "CALENDAR_UPDATE", "badge": "Rohan's Football" }, { "id": "dyn_action_2", "title": "Schedule a Friendly Match", "description": "Find an open slot for a friendly match.", "type": "CALENDAR_UPDATE", "badge": "Friendly Match" } ] }''')
print("SPEECH:", res[0])
print("HAS_ACTIONS:", res[1])
print("ACTIONS:", res[2])
