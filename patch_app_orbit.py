import re
with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

pattern = re.compile(r'const oList = document\.getElementById\("orbitList"\);[\s\S]*?\} else \{[\s\S]*?\}')
new_orbit_render = '''const oCont = document.getElementById("orbitListContainer");
      if(oCont) {
        oCont.innerHTML = "";
        if (data.orbit && data.orbit.length > 0) {
          data.orbit.forEach(o => addOrbitRow(o.person_name, o.relationship_type));
        } else {
          if (!isEditMode) oCont.innerHTML = "<div style='color:#888;'><em>No members yet</em></div>";
        }
      }'''

if pattern.search(js):
    js = pattern.sub(new_orbit_render, js, count=1)
    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print('Replaced orbit rendering')
else:
    print('Pattern not found')
