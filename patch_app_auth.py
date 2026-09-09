with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace setAuthMode
old_set_auth = '''function setAuthMode(mode) {
  currentAuthMode = mode;
  document.getElementById("tabSignInBtn").classList.toggle("active", mode === "signin");
  document.getElementById("tabSignUpBtn").classList.toggle("active", mode === "signup");
  document.getElementById("authSubmitBtn").innerText = mode === "signin" ? "Sign In" : "Sign Up";
  document.getElementById("authSubTitle").innerText = mode === "signin" ? "Sign in to your life companion" : "Create your digital twin profile";
}'''

new_set_auth = '''function setAuthMode(mode) {
  currentAuthMode = mode;
  document.getElementById("tabSignInBtn").classList.toggle("active", mode === "signin");
  document.getElementById("tabSignUpBtn").classList.toggle("active", mode === "signup");
  document.getElementById("authSubmitBtn").innerText = mode === "signin" ? "Sign In" : "Sign Up";
  document.getElementById("authSubTitle").innerText = mode === "signin" ? "Sign in to your life companion" : "Create your digital twin profile";
  
  // Show optional email field only on signup
  const emailFieldDiv = document.getElementById("emailFieldDiv");
  if(emailFieldDiv) {
    emailFieldDiv.style.display = (mode === "signup") ? "block" : "none";
  }
}'''
text = text.replace(old_set_auth, new_set_auth)

# Replace handleAuthSubmit
old_submit = '''async function handleAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("authEmail").value.trim();
  const password = document.getElementById("authPassword").value.trim();

  const endpoint = currentAuthMode === "signup" ? `${API_BASE}/auth/signup` : `${API_BASE}/auth/signin`;

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });'''

new_submit = '''async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("authUsername").value.trim();
  const email = document.getElementById("authEmail") ? document.getElementById("authEmail").value.trim() : "";
  const password = document.getElementById("authPassword").value.trim();

  const endpoint = currentAuthMode === "signup" ? `${API_BASE}/auth/signup` : `${API_BASE}/auth/signin`;

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });'''
text = text.replace(old_submit, new_submit)

# Replace logoutUser
old_logout = '''function logoutUser() {
  localStorage.clear();
  toggleAuthModal();
}'''
new_logout = '''function logoutUser() {
  localStorage.clear();
  window.location.reload();
}'''
text = text.replace(old_logout, new_logout)

with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched app.js for auth form')
