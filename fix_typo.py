with open('veya_web/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('8button id="tabSignUpBtn"', '<button id="tabSignUpBtn"')

with open('veya_web/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed 8button typo in index.html')
