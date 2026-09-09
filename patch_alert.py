with open('veya_web/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('<div class="edit-pic-link">Edit persona</div>', '<div class="edit-pic-link" onclick="alert(\'Please edit your digital twin parameters in the form below.\')">Edit persona</div>')

with open('veya_web/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
