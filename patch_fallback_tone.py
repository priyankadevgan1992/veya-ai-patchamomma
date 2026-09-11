with open('veya_agents/gemini_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_fallback_1 = '''        # Intent: User is tired / exhausted
        if any(w in msg_lower for w in ["tired", "exhausted", "sleepy", "drained"]):
            if events_count >= 3:
                return f"I see you have {events_count} meetings ahead. Your energy is low—do you want me to try and reschedule some of the non-essential ones?"
            return "Your biological battery seems depleted. Please make sure to protect your evening window tonight for some solid recovery."'''

new_fallback_1 = '''        # Intent: User is tired / exhausted
        if any(w in msg_lower for w in ["tired", "exhausted", "sleepy", "drained", "burnt out"]):
            if events_count >= 3:
                return f"I hear you, you've been pushing really hard lately. With {events_count} meetings ahead, your energy is understandably low. I'll automatically block out a 30-minute recovery buffer for you this afternoon so you can just breathe."
            return "You sound completely drained. I'm noting this down. I'll make sure to block off your evening early tonight so you can actually disconnect and recover."'''

old_fallback_2 = '''        # Intent: Eating / Food
        if any(w in msg_lower for w in ["eat", "hungry", "food", "lunch", "dinner", "breakfast", "snack", "starving"]):
            if events_count > 0:
                next_event = events[0].get("title", "your next meeting")
                return f"I see you have '{next_event}' coming up soon. We should definitely get you fed before that so your glucose levels don't crash. Shall I find a quick 20-min window to block for a meal?"
            else:
                return "You definitely need fuel! Since your schedule is clear, take a proper break. Maybe step away from the desk to eat so you get a real mental reset."'''

new_fallback_2 = '''        # Intent: Eating / Food
        if any(w in msg_lower for w in ["eat", "hungry", "food", "lunch", "dinner", "breakfast", "snack", "starving"]):
            if events_count > 0:
                next_event = events[0].get("title", "your next meeting")
                return f"You definitely need fuel before '{next_event}'. I've noticed you skip meals when stressed. I'm proactively blocking a 20-min window right now so you can eat without interruptions."
            else:
                return "You definitely need fuel! Step away from the desk and get something to eat. I'll hold off on any notifications for the next 30 minutes so you can actually enjoy it."'''

if old_fallback_1 in content:
    content = content.replace(old_fallback_1, new_fallback_1)
if old_fallback_2 in content:
    content = content.replace(old_fallback_2, new_fallback_2)

with open('veya_agents/gemini_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched fallback logic for better tone.")
