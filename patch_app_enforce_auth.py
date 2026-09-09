with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace activeUser
old_activeUser = '''let activeUser = {
  email: localStorage.getItem("veya_email") || "test@veya.ai",
  internal_uuid: localStorage.getItem("veya_uuid") || "uuid_test_enriched_001",
  persona_name: localStorage.getItem("veya_name") || "Meera",
  onboarding_completed: localStorage.getItem("veya_onboarding") === "true"
};'''

new_activeUser = '''let activeUser = {
  email: localStorage.getItem("veya_email"),
  internal_uuid: localStorage.getItem("veya_uuid"),
  persona_name: localStorage.getItem("veya_name"),
  onboarding_completed: localStorage.getItem("veya_onboarding") === "true"
};'''

text = text.replace(old_activeUser, new_activeUser)

old_domloaded = '''document.addEventListener("DOMContentLoaded", () => {
  updateUserUI();
  loadHomeStream();
  loadInsights();
  loadTomorrowPlan();
  checkPendingFeedback();
});'''

new_domloaded = '''document.addEventListener("DOMContentLoaded", () => {
  if (!activeUser.internal_uuid) {
    document.getElementById("authModal").classList.remove("hidden");
  } else {
    updateUserUI();
    loadHomeStream();
    loadInsights();
    loadTomorrowPlan();
    checkPendingFeedback();
  }
});'''

text = text.replace(old_domloaded, new_domloaded)

with open('veya_web/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched app.js for strict auth enforcement')
