with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(r'style=\"display', 'style="display')
text = text.replace(r'padding-bottom:8px;\"', 'padding-bottom:8px;"')
text = text.replace(r'style=\"font-weight', 'style="font-weight')
text = text.replace(r'color:#111;\"', 'color:#111;"')
text = text.replace(r'style=\"color', 'style="color')
text = text.replace(r'text-align:right;\"', 'text-align:right;"')

with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
