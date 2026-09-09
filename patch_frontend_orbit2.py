import os

def patch_frontend():
    # 1. Update index.html
    with open('veya_web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Add id to Done button and hide by default
    old_done = '<div class="ig-nav-done" onclick="savePreferences()">Done</div>'
    new_done = '<div class="ig-nav-done" id="profileDoneBtn" onclick="savePreferences()" style="display:none;">Done</div>'
    html = html.replace(old_done, new_done)

    with open('veya_web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html patched")

    # 2. Update app.js
    with open('veya_web/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # toggleEditMode update
    old_toggle_edit = '''    // Hide remove buttons if not edit mode
    document.querySelectorAll('.orbit-remove').forEach(el => el.style.display = isEditMode ? 'block' : 'none');
}'''
    new_toggle_edit = '''    // Hide remove buttons if not edit mode
    document.querySelectorAll('.orbit-remove').forEach(el => el.style.display = isEditMode ? 'block' : 'none');
    
    // Toggle Done button
    const doneBtn = document.getElementById('profileDoneBtn');
    if(doneBtn) doneBtn.style.display = isEditMode ? 'block' : 'none';
}'''
    js = js.replace(old_toggle_edit, new_toggle_edit)

    # toggleProfileModal update
    old_toggle_profile = '''function toggleProfileModal() {
  const modal = document.getElementById("profileModal");
  if (modal.classList.contains("hidden")) {
    isEditMode = false;
    document.getElementById('editPersonaBtn').textContent = 'Edit persona';
    document.getElementById('addOrbitBtn').style.display = 'none';
    fetchProfileAndReminders();
  }
  modal.classList.toggle("hidden");
}'''
    new_toggle_profile = '''function toggleProfileModal() {
  const modal = document.getElementById("profileModal");
  if (modal.classList.contains("hidden")) {
    isEditMode = false;
    document.getElementById('editPersonaBtn').textContent = 'Edit persona';
    document.getElementById('addOrbitBtn').style.display = 'none';
    const doneBtn = document.getElementById('profileDoneBtn');
    if(doneBtn) doneBtn.style.display = 'none';
    fetchProfileAndReminders();
  }
  modal.classList.toggle("hidden");
}'''
    js = js.replace(old_toggle_profile, new_toggle_profile)

    # addOrbitRow update
    old_add = '''function addOrbitRow(name = '', rel = '') {
    const cont = document.getElementById("orbitListContainer");
    const div = document.createElement("div");
    div.className = "orbit-row";
    div.innerHTML = `
      <input type="text" class="o-fval orbit-name" placeholder="Name" value="${escapeHtml(name)}" ${isEditMode ? '' : 'disabled'}>
      <input type="text" class="o-fval orbit-rel" placeholder="Relation (e.g. Husband)" value="${escapeHtml(rel)}" ${isEditMode ? '' : 'disabled'}>
      <button class="orbit-remove" onclick="this.parentElement.remove()" style="display: ${isEditMode ? 'block' : 'none'}; border:none; background:transparent; color:red; cursor:pointer;">x</button>
    `;
    cont.appendChild(div);
}'''
    new_add = '''function addOrbitRow(name = '', rel = '', ctx = '', imp = 50) {
    const cont = document.getElementById("orbitListContainer");
    const div = document.createElement("div");
    div.className = "orbit-row";
    div.style.flexDirection = "column";
    div.style.alignItems = "stretch";
    div.style.border = "1px solid #eee";
    div.style.padding = "8px";
    div.style.borderRadius = "6px";
    div.style.marginBottom = "8px";
    div.style.position = "relative";
    div.innerHTML = `
      <div style="display:flex; gap:8px; margin-bottom:4px;">
        <input type="text" class="o-fval orbit-name" placeholder="Name" value="${escapeHtml(name)}" ${isEditMode ? '' : 'disabled'} style="flex:1;">
        <input type="text" class="o-fval orbit-rel" placeholder="Relation (e.g. Husband)" value="${escapeHtml(rel)}" ${isEditMode ? '' : 'disabled'} style="flex:1;">
        <button class="orbit-remove" onclick="this.parentElement.parentElement.remove()" style="display: ${isEditMode ? 'block' : 'none'}; border:none; background:transparent; color:red; cursor:pointer;">x</button>
      </div>
      <div style="display:flex; gap:8px;">
        <input type="text" class="o-fval orbit-ctx" placeholder="1-liner context" value="${escapeHtml(ctx)}" ${isEditMode ? '' : 'disabled'} style="flex:2;">
        <input type="number" class="o-fval orbit-imp" placeholder="Importance %" value="${imp}" min="0" max="100" ${isEditMode ? '' : 'disabled'} style="flex:1;">
      </div>
    `;
    cont.appendChild(div);
}'''
    js = js.replace(old_add, new_add)

    # fetchProfileAndReminders orbit.forEach update
    old_orbit_render = '''data.orbit.forEach(o => addOrbitRow(o.person_name, o.relationship_type));'''
    new_orbit_render = '''data.orbit.forEach(o => addOrbitRow(o.person_name, o.relationship_type, o.key_context || '', o.importance_percent || 50));'''
    js = js.replace(old_orbit_render, new_orbit_render)

    # savePreferences orbit map update
    old_orbit_map = '''        orbit: Array.from(document.querySelectorAll('.orbit-row')).map(row => ({
           person_name: row.querySelector('.orbit-name').value.trim(),
           relationship_type: row.querySelector('.orbit-rel').value.trim()
        })).filter(o => o.person_name && o.relationship_type)'''
    new_orbit_map = '''        orbit: Array.from(document.querySelectorAll('.orbit-row')).map(row => ({
           person_name: row.querySelector('.orbit-name').value.trim(),
           relationship_type: row.querySelector('.orbit-rel').value.trim(),
           key_context: row.querySelector('.orbit-ctx').value.trim(),
           importance_percent: parseInt(row.querySelector('.orbit-imp').value) || 50
        })).filter(o => o.person_name && o.relationship_type)'''
    js = js.replace(old_orbit_map, new_orbit_map)

    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("app.js patched")

if __name__ == '__main__':
    patch_frontend()
