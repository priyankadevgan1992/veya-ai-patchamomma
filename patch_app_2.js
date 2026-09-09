const fs = require('fs');
let content = fs.readFileSync('veya_web/app.js', 'utf8');

const badLine = '${(data.provenance || []).map(line => \\`<div class="pill outline animate-fade-in">\\${escapeHtml(line)}</div>\\`).join("")}';
const goodLine = '${(data.provenance || []).map(line => `<div class="pill outline animate-fade-in">${escapeHtml(line)}</div>`).join("")}';

content = content.replace(badLine, goodLine);
fs.writeFileSync('veya_web/app.js', content, 'utf8');
console.log('Patched string replacement.');
