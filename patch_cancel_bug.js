const fs = require('fs');

let text = fs.readFileSync('veya_web/app.js', 'utf8');

const oldLogic = `if (adjustmentType === 'Cancel') {
        const idx = window.cachedPlanData.suggested_items.findIndex(i => i.id == activeFeasibleItemId);
        if (idx > -1) {
            window.cachedPlanData.suggested_items.splice(idx, 1);
            renderPlan();
        }
    }`;

const newLogic = `if (adjustmentType === 'Cancel') {
        const item = window.cachedPlanData.suggested_items.find(i => i.id == activeFeasibleItemId);
        if (item) {
            item.locked = false;
            // Optionally remove [Reschedule] or [Delegate] tags if user canceled them
            item.title = item.title.replace(/^\[.*?\]\\s*/, '');
            renderPlan();
        }
    }`;

if (text.includes(oldLogic)) {
    text = text.replace(oldLogic, newLogic);
    fs.writeFileSync('veya_web/app.js', text, 'utf8');
    console.log('Cancel bug fixed!');
} else {
    console.log('Old logic not found! Searching with regex...');
    // In case of slight whitespace variations
    const regex = /if\s*\(adjustmentType\s*===\s*'Cancel'\)\s*\{[\s\S]*?renderPlan\(\);\s*\}/;
    if (regex.test(text)) {
        text = text.replace(regex, newLogic);
        fs.writeFileSync('veya_web/app.js', text, 'utf8');
        console.log('Cancel bug fixed using regex!');
    } else {
        console.log('Still not found.');
    }
}
