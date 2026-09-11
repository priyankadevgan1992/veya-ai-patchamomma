with open('veya_agents/action_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_scenario_a = """        # Scenario A: Evening Household / Meeting Clash (Meera Style)
        elif ("husband" in mem_text or "daughter" in mem_text or cog_state["relational"]["spouse_away"]) and (
            any(w in msg_lower for w in ["hectic", "stress", "meetings", "travel", "alone", "help", "yes", "what can i do"])
        ):"""

new_scenario_a = """        # Scenario A: Evening Household / Meeting Clash (Meera Style)
        elif ("husband" in mem_text or "daughter" in mem_text or cog_state["relational"]["spouse_away"]) and (
            any(w in msg_lower for w in ["hectic", "stress", "meetings", "travel", "alone", "help", "what can i do"]) and not msg_lower.strip() == "yes"
        ):"""

old_scenario_b = """        # Scenario B: Luteal Biological Recovery (Priya Style)
        elif cog_state["biological"]["is_luteal"] and any(w in msg_lower for w in ["energy", "low", "tired", "cycle", "walk", "rest", "yes"]):"""

new_scenario_b = """        # Scenario B: Luteal Biological Recovery (Priya Style)
        elif cog_state["biological"]["is_luteal"] and (any(w in msg_lower for w in ["energy", "low", "tired", "cycle", "walk", "rest"]) and not msg_lower.strip() == "yes"):"""

old_scenario_c = """        # Scenario C: High-Stakes Prep Runway (Arjun Style)
        elif cog_state["cognitive"]["high_stakes_event_present"] or any(w in msg_lower for w in ["pitch", "deck", "prep", "client", "presentation", "yes"]):"""

new_scenario_c = """        # Scenario C: High-Stakes Prep Runway (Arjun Style)
        elif cog_state["cognitive"]["high_stakes_event_present"] or (any(w in msg_lower for w in ["pitch", "deck", "prep", "client", "presentation"]) and not msg_lower.strip() == "yes"):"""

content = content.replace(old_scenario_a, new_scenario_a)
content = content.replace(old_scenario_b, new_scenario_b)
content = content.replace(old_scenario_c, new_scenario_c)

with open('veya_agents/action_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched action agent triggers!")
