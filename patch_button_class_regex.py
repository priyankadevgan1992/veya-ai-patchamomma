with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
old_button = r'<button onclick="executeAction\(\'\$\{escapeHtml\(escapeJsStr\(act\.id\)\)\}\', \'\$\{escapeHtml\(escapeJsStr\(act\.title\)\)\}\'\)">'
new_button = r'<button class="action-approve-btn" onclick="executeAction(\'${escapeHtml(escapeJsStr(act.id))}\', \'${escapeHtml(escapeJsStr(act.title))}\')">'

content = re.sub(old_button, new_button, content)

with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Regex patched button!")
