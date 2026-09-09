const fs = require('fs');
let content = fs.readFileSync('veya_web/app.js', 'utf8');
content = content.replace(
  /\\\`<div class="pill outline animate-fade-in">\\\\\$\{escapeHtml\(line\)\}<\/div>\\\`/g,
  '`<div class="pill outline animate-fade-in">${escapeHtml(line)}</div>`'
);
fs.writeFileSync('veya_web/app.js', content, 'utf8');
