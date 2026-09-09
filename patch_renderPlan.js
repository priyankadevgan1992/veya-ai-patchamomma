const fs = require('fs');
let appJs = fs.readFileSync('veya_web/app.js', 'utf8');

const startIdx = appJs.indexOf('function renderPlan() {');
const endIdx = appJs.indexOf('async function loadTomorrowPlan() {');

const newRenderPlan = `function renderPlan() {
    if (!window.cachedPlanData) return;
    const data = window.cachedPlanData;
    
    const extContainer = document.getElementById("planningExistingList");
    if (data.existing_items && data.existing_items.length > 0) {
        extContainer.innerHTML = data.existing_items.map(item => \`
          <div class="plan-row plan-fixed" style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="openDummyCalendar()">
            <div style="display:flex; gap:15px; align-items:center;">
                <div class="plan-time">\${item.time.split(" - ")[0]}</div>
                <div>
                  <div class="plan-title">\${escapeHtml(item.title)}</div>
                  <div class="plan-tag">Existing</div>
                </div>
            </div>
            <div onclick="event.stopPropagation(); removeCalendarItem('\${item.id}')" style="color:var(--danger); font-size:20px; padding:5px 10px; cursor:pointer;" title="Remove">✕</div>
          </div>
        \`).join("");
    } else {
        extContainer.innerHTML = '<div style="padding:15px 20px; color:#888; font-style:italic;">Nothing planned</div>';
    }

    const sugContainer = document.getElementById("planningSuggestedList");
    sugContainer.innerHTML = data.suggested_items.map(item => \`
      <div class="plan-row" id="plan-item-\${item.id}">
        <div class="plan-time">\${(item.time || '').split(" - ")[0]}</div>
        <div class="plan-card-body">
          <div class="tag-row"><span class="tag \${item.priority === 'High' ? 'conflict' : ''}">\${item.priority} Priority</span></div>
          <div class="plan-card-title">\${escapeHtml(item.title)}</div>
          <div class="plan-rationale">💡 \${escapeHtml(item.rationale || 'Suggested based on your flow.')}</div>
          <div class="pill-row">
            \${item.locked ? 
                \`<div class="pill fill" style="background:#E8F8EE; color:#1B7F3D;">✓ Confirmed</div>
                 <div class="pill text" onclick="openFeasibilityDrawer('\${item.id}', '\${escapeHtml(item.title)}')">⚙️ Adjust</div>\` : 
                \`<div class="pill outline plan-feasible-btn" onclick="markFeasible('\${item.id}')">✓ Lock In</div>
                 <div class="pill text" onclick="openFeasibilityDrawer('\${item.id}', '\${escapeHtml(item.title)}')">⚙️ Adjust</div>\`
            }
          </div>
        </div>
      </div>
    \`).join("");
}

`;

if (startIdx !== -1 && endIdx !== -1) {
    appJs = appJs.substring(0, startIdx) + newRenderPlan + appJs.substring(endIdx);
    fs.writeFileSync('veya_web/app.js', appJs, 'utf8');
    console.log("Patched renderPlan!");
} else {
    console.log("Could not find bounds for renderPlan");
}
