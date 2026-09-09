import re

# 1. Update main.py
with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

pattern = r'def derive_insight\(req: DeriveRequest\):\s*explanation_json = derive_metric_explanation\(req\.internal_uuid, req\.metric_name\)\s*import json\s*parsed = json\.loads\(explanation_json\)\s*return \{\"metric\": req\.metric_name, \"score\": req\.score, \"provenance\": parsed\.get\(\"explanation_lines\", \[\]\)\}'

new_func = '''def derive_insight(req: DeriveRequest):
    explanation_json = derive_metric_explanation(req.internal_uuid, req.metric_name, req.score)
    import json
    parsed = json.loads(explanation_json)
    return {
        "metric": req.metric_name,
        "score": req.score,
        "reason": parsed.get("reason", ""),
        "recommendation": parsed.get("recommendation", ""),
        "provenance": parsed.get("provenance", [])
    }'''

main_code = re.sub(pattern, new_func, main_code)
with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(main_code)

# 2. Update app.js
with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    app_code = f.read()

js_pattern = r'list\.innerHTML = data\.provenance\.map\(line => `\s*<li class=\"derivation-item animate-fade-in\">\$\{escapeHtml\(line\)\}<\/li>\s*`\)\.join\(\"\"\);'

new_js = '''
      list.innerHTML = `
        <div style="padding-bottom: 12px; font-size: 13.5px; color: #333; line-height: 1.4;">
          <strong>Analysis:</strong> ${escapeHtml(data.reason || '')}
        </div>
        <div style="padding-bottom: 16px; font-size: 13.5px; color: #333; line-height: 1.4;">
          <strong>Recommendation:</strong> ${escapeHtml(data.recommendation || '')}
        </div>
        <div class="pill-row">
          ${(data.provenance || []).map(line => \`<div class="pill outline animate-fade-in">\${escapeHtml(line)}</div>\`).join("")}
        </div>
      `;
'''

app_code = re.sub(js_pattern, new_js, app_code)
with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(app_code)

print('UX and backend patched!')
