const fs = require('fs');

let toolsCode = fs.readFileSync('veya_agents/tools.py', 'utf8');

const startIdx = toolsCode.indexOf('def derive_metric_explanation');
const endIdx = toolsCode.indexOf('def adjust_tomorrow_plan');

if (startIdx !== -1 && endIdx !== -1) {
    const newFunc = `def derive_metric_explanation(internal_uuid: str, metric_id: str, score: int = None) -> str:
    from google.genai import Client
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
        # Strip markdown if present
        text = res.text.strip()
        if text.startswith("\`\`\`json"):
            text = text[7:-3].strip()
        elif text.startswith("\`\`\`"):
            text = text[3:-3].strip()
            
        return text
    except Exception as e:
        print(f"Derivation LLM failed: {e}")
        # Fallback
        return json.dumps({
            "reason": f"Based on your recent activity, your {metric_id} is at {score}/100. You've had a busy schedule and your biological rhythm is adapting.",
            "recommendation": "Focus on a quick 10-minute reset before your next major activity to align your energy.",
            "provenance": [f"{len(events)} events today", "Recent activity levels", "Biological pacing"]
        })

`;
    const updatedCode = toolsCode.substring(0, startIdx) + newFunc + toolsCode.substring(endIdx);
    fs.writeFileSync('veya_agents/tools.py', updatedCode, 'utf8');
    console.log("Updated tools.py");
} else {
    console.log("Failed to find function bounds.");
}
