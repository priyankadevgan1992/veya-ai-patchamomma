const fs = require('fs');

let text = fs.readFileSync('veya_web/app.js', 'utf8');

const idx = text.indexOf('function markFeasible');

if (idx !== -1) {
    const newFuncs = `
let activeFeasibleItemId = null;
function openFeasibilityDrawer(itemId, title) {
    activeFeasibleItemId = itemId;
    document.getElementById("feasibilityItemName").textContent = '"' + title + '"';
    document.getElementById("feasibilityDrawer").classList.remove("hidden");
}

function closeFeasibilityDrawer() {
    document.getElementById("feasibilityDrawer").classList.add("hidden");
}

async function applyFeasibilityAdjustment(adjustmentType) {
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
            item.title = '[' + adjustmentType + '] ' + item.title;
            item.locked = true;
            renderPlan();
        }
    }
}
`;
    text = text.substring(0, idx) + newFuncs + text.substring(idx);
    fs.writeFileSync('veya_web/app.js', text, 'utf8');
    console.log('Added openFeasibilityDrawer back!');
} else {
    console.log('function markFeasible not found');
}
