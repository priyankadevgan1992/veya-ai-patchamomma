with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''    try {
      const wsUrl = `ws://${location.host}/api/voice/stream?uuid=${activeUser.internal_uuid}`;
      voiceCallWs = new WebSocket(wsUrl);'''

new_code = '''    try {
      const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${location.host}/api/voice/stream?uuid=${activeUser.internal_uuid}`;
      voiceCallWs = new WebSocket(wsUrl);'''

text = text.replace(old_code, new_code)

with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched app.js to use secure WebSocket (wss) if on HTTPS')
