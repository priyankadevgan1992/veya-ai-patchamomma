import os

def patch_frontend():
    # 1. Update index.html
    with open('veya_web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    new_fields = '''          <div class="form-row">
            <div class="flabel">Anchor</div>
            <input id="prefAnchor" class="fval" value="">
          </div>
          <div class="form-row">
            <div class="flabel">Gender</div>
            <input id="prefGender" class="fval" value="">
          </div>
          <div class="form-row">
            <div class="flabel">Household</div>
            <input type="number" id="prefHousehold" class="fval" value="0" style="width:100%; border:none; text-align:right; outline:none; background:transparent; font-size:16px;">
          </div>
          <div class="form-row">
            <div class="flabel">Rel. Health</div>
            <select id="prefRelHealth" class="fval">
              <option value="Strong">Strong</option>
              <option value="Moderate">Moderate</option>
              <option value="Strained">Strained</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Bio Phase</div>
            <select id="prefBioPhase" class="fval">
              <option value="Normal">Normal</option>
              <option value="Follicular">Follicular</option>
              <option value="Luteal">Luteal</option>
              <option value="Menstrual">Menstrual</option>
              <option value="Ovulatory">Ovulatory</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Maturity (wks)</div>
            <input type="number" id="prefMaturity" class="fval" value="0" style="width:100%; border:none; text-align:right; outline:none; background:transparent; font-size:16px;">
          </div>
          <div class="form-row">
            <div class="flabel">Calendars</div>
            <select id="prefCalendars" class="fval">
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Wearable</div>
            <select id="prefWearable" class="fval">
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>'''
    
    html = html.replace('''          <div class="form-row">
            <div class="flabel">Anchor</div>
            <input id="prefAnchor" class="fval" value="">
          </div>''', new_fields)

    # I also need to make the modal scrollable if it's too long
    html = html.replace('<div class="screen active">', '<div class="screen active" style="overflow-y:auto; padding-bottom:50px;">')

    with open('veya_web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)


    # 2. Update app.js
    with open('veya_web/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    old_fetch = '''document.getElementById("prefName").value = data.persona_name || "";
      document.getElementById("prefStress").value = data.work_stress_level || "Moderate";
      document.getElementById("prefAnchor").value = data.life_anchor || "";'''
      
    new_fetch = '''document.getElementById("prefName").value = data.persona_name || "";
      document.getElementById("prefStress").value = data.work_stress_level || "Moderate";
      document.getElementById("prefAnchor").value = data.life_anchor || "";
      document.getElementById("prefGender").value = data.gender_identity || "";
      document.getElementById("prefHousehold").value = data.household_members || 0;
      document.getElementById("prefRelHealth").value = data.relationship_health || "Moderate";
      document.getElementById("prefBioPhase").value = data.biological_phase || "Normal";
      document.getElementById("prefMaturity").value = data.twin_maturity_weeks || 0;
      document.getElementById("prefCalendars").value = data.calendars_connected || 0;
      document.getElementById("prefWearable").value = data.wearable_connected || 0;'''

    js = js.replace(old_fetch, new_fetch)

    old_save = '''const name = document.getElementById("prefName").value;
  const stress = document.getElementById("prefStress").value;
  const anchor = document.getElementById("prefAnchor").value;
  
  try {
    await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        persona_name: name,
        work_stress_level: stress,
        life_anchor: anchor
      })'''
      
    new_save = '''const name = document.getElementById("prefName").value;
  const stress = document.getElementById("prefStress").value;
  const anchor = document.getElementById("prefAnchor").value;
  const gender = document.getElementById("prefGender").value;
  const household = parseInt(document.getElementById("prefHousehold").value) || 0;
  const relHealth = document.getElementById("prefRelHealth").value;
  const bioPhase = document.getElementById("prefBioPhase").value;
  const maturity = parseInt(document.getElementById("prefMaturity").value) || 0;
  const calendars = parseInt(document.getElementById("prefCalendars").value) || 0;
  const wearable = parseInt(document.getElementById("prefWearable").value) || 0;
  
  try {
    await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        persona_name: name,
        work_stress_level: stress,
        life_anchor: anchor,
        gender_identity: gender,
        household_members: household,
        relationship_health: relHealth,
        biological_phase: bioPhase,
        twin_maturity_weeks: maturity,
        calendars_connected: calendars,
        wearable_connected: wearable
      })'''

    js = js.replace(old_save, new_save)

    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    
    print("Frontend patched successfully")

if __name__ == "__main__":
    patch_frontend()
