import json

with open('veya_agents/tools.py', 'r', encoding='utf-8') as f:
    tools_code = f.read()

start_idx = tools_code.find('def derive_metric_explanation')
end_idx = tools_code.find('def adjust_tomorrow_plan')

new_func = '''def derive_metric_explanation(internal_uuid: str, metric_id: str, score: int = None) -> str:
    from google.genai import Client
    import json
    try:
        signals = json.loads(fetch_connected_signals(internal_uuid))
        health = signals.get("health_connect_metrics", [{}])[0] if signals.get("health_connect_metrics") else {}
        events = signals.get("calendar_events", [])
        
        prompt = f"""You are Veya's internal reasoning engine.
The user clicked on their {metric_id} metric, which is currently scored at {score}/100.
Their current context:
- Sleep: {health.get('sleep_hours', 7.5)} hours ({health.get('sleep_quality', 'Unknown')})
- Steps: {health.get('steps', 0)}
- Calendar Events today: {len(events)}

Generate a JSON object strictly in this format (no markdown code blocks, just raw JSON):
{{
    "reason": "A 2-3 sentence empathetic explanation of why this score is {score}. Mention their health or calendar data if relevant.",
    "recommendation": "A 1-2 sentence actionable and realistic recommendation to improve or maintain this score.",
    "provenance": ["Short pill-sized factor 1", "Short pill-sized factor 2", "Short pill-sized factor 3"]
}}
"""
        client = Client(vertexai=True, project="prisha1910-token-2026", location="global")
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        text = res.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        return text
    except Exception as e:
        print(f"Derivation LLM failed: {e}")
        return json.dumps({
            "reason": f"Based on your recent activity, your {metric_id} is at {score}/100. You've had a busy schedule and your biological rhythm is adapting.",
            "recommendation": "Focus on a quick 10-minute reset before your next major activity to align your energy.",
            "provenance": [f"{len(events)} events today", "Recent activity levels", "Biological pacing"]
        })

'''

if start_idx != -1 and end_idx != -1:
    updated_code = tools_code[:start_idx] + new_func + tools_code[end_idx:]
    with open('veya_agents/tools.py', 'w', encoding='utf-8') as f:
        f.write(updated_code)
    print("Updated tools.py")
else:
    print("Failed to find bounds")
