with open('veya_web/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_form = '''<form id="authForm" onsubmit="handleAuthSubmit(event)" class="auth-form">
          <div>
            <label><b>Email</b></label><br>
            <input type="email" id="authEmail" class="auth-input" placeholder="test@veya.ai" value="test@veya.ai" required>
          </div>
          <div>
            <label><b>Password</b></label><br>
            <input type="password" id="authPassword" class="auth-input" value="password123" required>
          </div>
          <button type="submit" id="authSubmitBtn" class="auth-submit-btn">Sign In</button>
        </form>'''

new_form = '''<form id="authForm" onsubmit="handleAuthSubmit(event)" class="auth-form">
          <div>
            <label><b>Username</b></label><br>
            <input type="text" id="authUsername" class="auth-input" placeholder="e.g. test@veya.ai" value="test@veya.ai" required>
          </div>
          <div id="emailFieldDiv" style="display: none;">
            <label><b>Email (Optional - for Calendar Sync)</b></label><br>
            <input type="email" id="authEmail" class="auth-input" placeholder="e.g. your@gmail.com" value="">
          </div>
          <div>
            <label><b>Password</b></label><br>
            <input type="password" id="authPassword" class="auth-input" value="password123" required>
          </div>
          <button type="submit" id="authSubmitBtn" class="auth-submit-btn">Sign In</button>
        </form>'''

text = text.replace(old_form, new_form)

# Add onclick handling in setAuthMode script? Or just do it in JS. Let's do it in JS.
with open('veya_web/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched index.html auth form')
