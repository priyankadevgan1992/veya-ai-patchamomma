with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('const API_BASE = "http://localhost:8080/api";', 'const API_BASE = "/api";')
with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated API_BASE')
