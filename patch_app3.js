const fs = require('fs');
let appJs = fs.readFileSync('veya_web/app.js', 'utf8');

// 1. Find and replace loadTomorrowPlan with the stateful version
const startIdx = appJs.indexOf('async function loadTomorrowPlan() {');
const endIdx = appJs.indexOf('function markFeasible(itemId) {');

if (startIdx !== -1 && endIdx !== -1) {
  const newLogic = `
window.cachedPlanData = null;

function renderPlan() {
    if (!window.cachedPlanData) return;
    const data = window.cachedPlanData;
    
    const extContainer = document.getElementById("planningExistingList");
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
                \`<div class="pill fill" style="background:#E8F8EE; color:#1B7F3D;">✓ Confirmed</div>\` : 
                \`<div class="pill outline plan-feasible-btn" onclick="markFeasible('\${item.id}')">✓ Lock In</div>
                 <div class="pill text" onclick="openFeasibilityDrawer('\${item.id}', '\${escapeHtml(item.title)}')">⚙️ Adjust</div>\`
            }
          </div>
        </div>
      </div>
    \`).join("");
}

async function loadTomorrowPlan() {
  try {
    const res = await fetch(\`\${API_BASE}/planning/tomorrow?uuid=\${activeUser.internal_uuid}\`);
    window.cachedPlanData = await res.json();
    renderPlan();
  } catch (err) {
    console.error("Error loading plan:", err);
  }
}

function removeCalendarItem(itemId) {
    if (!window.cachedPlanData) return;
    const itemIndex = window.cachedPlanData.existing_items.findIndex(i => i.id === itemId);
    if (itemIndex > -1) {
        const item = window.cachedPlanData.existing_items.splice(itemIndex, 1)[0];
        window.cachedPlanData.suggested_items.push(item);
        renderPlan();
    }
}

`;
  appJs = appJs.substring(0, startIdx) + newLogic + appJs.substring(endIdx);
}

// 2. Replace markFeasible
appJs = appJs.replace(
  /function markFeasible\(itemId\) \{[\s\S]*?\}/,
  `function markFeasible(itemId) {
    if(!window.cachedPlanData) return;
    const item = window.cachedPlanData.suggested_items.find(i => i.id == itemId);
    if(item) {
        item.locked = true;
        renderPlan();
    }
  }`
);

// 3. Replace switchTab to toggle FAB
appJs = appJs.replace(
  /function switchTab\(tabId\) \{/g,
  `function switchTab(tabId) {
    const fab = document.getElementById('fabFinalList');
    if(fab) {
        if(tabId === 'planning') fab.classList.remove('hidden');
        else fab.classList.add('hidden');
    }`
);

// 4. Update applyFeasibilityAdjustment
const applyFeasRegex = /async function applyFeasibilityAdjustment\(adjustmentType\) \{[\s\S]*?body: JSON\.stringify\(\{[\s\S]*?new_status: adjustmentType[\s\S]*?\}\)[\s\S]*?\}\);[\s\S]*?\}/;

appJs = appJs.replace(applyFeasRegex, `async function applyFeasibilityAdjustment(adjustmentType) {
    if (!activeFeasibleItemId || !window.cachedPlanData) return;
    
    closeFeasibilityDrawer();
    
    if (adjustmentType === 'Cancel') {
        const idx = window.cachedPlanData.suggested_items.findIndex(i => i.id == activeFeasibleItemId);
        if (idx > -1) {
            window.cachedPlanData.suggested_items.splice(idx, 1);
            renderPlan();
        }
    } else {
        const item = window.cachedPlanData.suggested_items.find(i => i.id == activeFeasibleItemId);
        if (item) {
            item.title = \`[\${adjustmentType}] \` + item.title;
            item.locked = true; // Lock it if adjusted
            renderPlan();
        }
    }
}`);

// 5. Add Modal controls
appJs += `
function openDummyCalendar() {
    document.getElementById('dummyCalendarModal').classList.remove('hidden');
}
function closeDummyCalendar() {
    document.getElementById('dummyCalendarModal').classList.add('hidden');
}

function openFinalSchedule() {
    if(!window.cachedPlanData) return;
    
    const existing = window.cachedPlanData.existing_items || [];
    const locked = (window.cachedPlanData.suggested_items || []).filter(i => i.locked);
    
    let all = [...existing, ...locked];
    
    // Sort by time (naive extraction for demo)
    all.sort((a,b) => {
        const parseTime = (t) => {
            if(!t) return 0;
            const str = t.split(' - ')[0];
            let [time, modifier] = str.split(' ');
            let [hours, mins] = time.split(':');
            hours = parseInt(hours);
            if(hours === 12 && modifier === 'AM') hours = 0;
            if(modifier === 'PM' && hours < 12) hours += 12;
            return hours * 60 + parseInt(mins || 0);
        };
        return parseTime(a.time) - parseTime(b.time);
    });
    
    const list = document.getElementById('finalScheduleList');
    list.innerHTML = all.map(item => \`
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding-bottom:8px;">
            <div style="font-weight:bold; color:#111;">\${(item.time||'').split(' - ')[0]}</div>
            <div style="color:#555; text-align:right;">\${escapeHtml(item.title)}</div>
        </div>
    \`).join('');
    
    document.getElementById('finalScheduleModal').classList.remove('hidden');
}
function closeFinalSchedule() {
    document.getElementById('finalScheduleModal').classList.add('hidden');
}
`;

fs.writeFileSync('veya_web/app.js', appJs, 'utf8');
console.log('App JS successfully patched!');
