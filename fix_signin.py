with open('veya_server/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_signin = '''    return {
        "status": "AUTHENTICATED",
        "internal_uuid": internal_uuid,
        "email": email,'''

new_signin = '''    return {
        "status": "AUTHENTICATED",
        "internal_uuid": internal_uuid,
        "email": username,'''

text = text.replace(old_signin, new_signin)

with open('veya_server/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed NameError in signin')
