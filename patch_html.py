import re
with open('veya_web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<div class=\"chat-input-row\">.*?</div>'
new_html = '''<div class=\"chat-input-row\">
        <input type=\"file\" id=\"chatFileInput\" class=\"hidden\" onchange=\"handleFileSelect(event)\">
        <button class=\"chat-icon-btn plus\" title=\"Attach file\" style=\"border:none;background:none;font-size:24px;color:#8E8E8E;cursor:pointer;padding:0 4px;font-weight:300;\" onclick=\"triggerFileUpload()\">+</button>
        <input type=\"text\" id=\"homeChatInput\" class=\"chat-input\" placeholder=\"Message Veya...\" onkeypress=\"handleHomeChatKeyPress(event)\">
        <button class=\"chat-icon-btn mic\" title=\"Voice input\" style=\"border:none;background:none;font-size:18px;color:#8E8E8E;cursor:pointer;padding:0 4px;\" onclick=\"toggleVoiceRecord()\">🎙️</button>
        <button class=\"chat-send\" onclick=\"sendHomeChatMessage()\">↑</button>
      </div>'''

html = re.sub(pattern, new_html, html, flags=re.DOTALL)
with open('veya_web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
