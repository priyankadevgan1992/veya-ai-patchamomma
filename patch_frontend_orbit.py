def patch_frontend():
    with open('veya_web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. CSS for disabled state
    css_injection = '''
    <style>
      .fval:disabled, .o-fval:disabled {
        color: #888;
        background: transparent;
        border: 1px solid transparent;
        appearance: none;
        -webkit-appearance: none;
      }
      .fval:not(:disabled), .o-fval:not(:disabled) {
        background: #fff;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px 8px;
        color: #000;
      }
      .orbit-row {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
        align-items: center;
      }
      .orbit-row input {
        flex: 1;
      }
    </style>
    '''
    if '<style>' not in html[:1000]: # simplistic check
        html = html.replace('</head>', css_injection + '</head>')
    
    # 2. Disable all existing inputs by default
    html = html.replace('class="fval"', 'class="fval" disabled')

    # 3. Change "Edit persona" alert back to toggle mode
    old_edit_btn = '''<div class="edit-pic-link" onclick="alert('Please edit your digital twin parameters in the form below.')">Edit persona</div>'''
    new_edit_btn = '''<div class="edit-pic-link" onclick="toggleEditMode()" id="editPersonaBtn">Edit persona</div>'''
    html = html.replace(old_edit_btn, new_edit_btn)
    
    # Also handle the case where the alert was not added perfectly
    html = html.replace('<div class="edit-pic-link">Edit persona</div>', new_edit_btn)
    
    # 4. Orbit list container and Add button
    old_orbit = '''<ul id="orbitList" style="list-style:none; padding:0 14px; font-size:14px;"></ul>'''
    new_orbit = '''
          <div id="orbitListContainer" style="padding:0 14px;"></div>
          <button id="addOrbitBtn" onclick="addOrbitRow()" style="display:none; margin: 8px 14px; background:none; border:1px solid #ccc; border-radius:4px; padding:4px 8px; cursor:pointer;">+ Add Person</button>
    '''
    html = html.replace(old_orbit, new_orbit)

    with open('veya_web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html patched")

    # Now for app.js
    with open('veya_web/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # JS 1: Remove homeGreetingTitle error
    js = js.replace('document.getElementById("homeGreetingTitle").textContent = `Hi ${name}`;', '')
    
    # JS 2: Add Edit mode logic
    edit_mode_logic = '''
let isEditMode = false;
function toggleEditMode() {
    isEditMode = !isEditMode;
    document.querySelectorAll('.fval, .o-fval').forEach(el => el.disabled = !isEditMode);
    document.getElementById('addOrbitBtn').style.display = isEditMode ? 'block' : 'none';
    document.getElementById('editPersonaBtn').textContent = isEditMode ? 'Cancel Edit' : 'Edit persona';
    
    // Hide remove buttons if not edit mode
    document.querySelectorAll('.orbit-remove').forEach(el => el.style.display = isEditMode ? 'block' : 'none');
}

function addOrbitRow(name = '', rel = '') {
    const cont = document.getElementById("orbitListContainer");
    const div = document.createElement("div");
    div.className = "orbit-row";
    div.innerHTML = `
      <input type="text" class="o-fval orbit-name" placeholder="Name" value="${escapeHtml(name)}" ${isEditMode ? '' : 'disabled'}>
      <input type="text" class="o-fval orbit-rel" placeholder="Relation (e.g. Husband)" value="${escapeHtml(rel)}" ${isEditMode ? '' : 'disabled'}>
      <button class="orbit-remove" onclick="this.parentElement.remove()" style="display: ${isEditMode ? 'block' : 'none'}; border:none; background:transparent; color:red; cursor:pointer;">x</button>
    `;
    cont.appendChild(div);
}
'''
    if 'function toggleEditMode' not in js:
        js = js.replace('function toggleProfileModal() {', edit_mode_logic + '\nfunction toggleProfileModal() {')
        
    # Modify profile modal toggle so it resets edit mode
    old_toggle = '''function toggleProfileModal() {
  const modal = document.getElementById("profileModal");
  if (modal.classList.contains("hidden")) {
    // About to open, fetch preferences and reminders
    fetchProfileAndReminders();
  }
  modal.classList.toggle("hidden");
}'''
    new_toggle = '''function toggleProfileModal() {
  const modal = document.getElementById("profileModal");
  if (modal.classList.contains("hidden")) {
    isEditMode = false;
    document.getElementById('editPersonaBtn').textContent = 'Edit persona';
    document.getElementById('addOrbitBtn').style.display = 'none';
    fetchProfileAndReminders();
  }
  modal.classList.toggle("hidden");
}'''
    js = js.replace(old_toggle, new_toggle)

    # JS 3: Populate orbit properly
    old_orbit_render = '''const oList = document.getElementById("orbitList");
      if (data.orbit && data.orbit.length > 0) {
        oList.innerHTML = data.orbit.map(o => `<li>dY`"??dY`c??dY` ${o.relationship_type}</li>`).join("");
      } else {
        oList.innerHTML = "<li><em>No members in orbit. Mention them in chat to add!</em></li>";
      }'''
    new_orbit_render = '''const oCont = document.getElementById("orbitListContainer");
      oCont.innerHTML = "";
      if (data.orbit && data.orbit.length > 0) {
        data.orbit.forEach(o => addOrbitRow(o.person_name, o.relationship_type));
      } else {
        if (!isEditMode) oCont.innerHTML = "<div style='color:#888;'><em>No members yet</em></div>";
      }'''
    js = js.replace(old_orbit_render, new_orbit_render)

    # JS 4: Save orbit in savePreferences
    old_save_payload = '''wearable_connected: wearable
      })'''
    new_save_payload = '''wearable_connected: wearable,
        orbit: Array.from(document.querySelectorAll('.orbit-row')).map(row => ({
           person_name: row.querySelector('.orbit-name').value.trim(),
           relationship_type: row.querySelector('.orbit-rel').value.trim()
        })).filter(o => o.person_name && o.relationship_type)
      })'''
    js = js.replace(old_save_payload, new_save_payload)
    
    # Final fix for when Done is clicked, close modal properly and make sure edit mode is off
    js = js.replace('toggleProfileModal();', 'toggleProfileModal(); // Done handles the closing\n    isEditMode = false;')

    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("app.js patched")

if __name__ == '__main__':
    patch_frontend()
