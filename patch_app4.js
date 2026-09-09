const fs = require('fs');
let js = fs.readFileSync('veya_web/app.js', 'utf8');

// I might have broken the replace logic by not escaping correctly. Let's fix lines 894 to 899 manually.
const badPattern = /list\.innerHTML = all\.map\(item => `[\s\S]*?`\)\.join\(''\);/;
const goodPattern = "list.innerHTML = all.map(item => `<div style=\\\"display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding-bottom:8px;\\\"><div style=\\\"font-weight:bold; color:#111;\\\">${(item.time||'').split(' - ')[0]}</div><div style=\\\"color:#555; text-align:right;\\\">${escapeHtml(item.title)}</div></div>`).join('');";

js = js.replace(badPattern, goodPattern);
fs.writeFileSync('veya_web/app.js', js, 'utf8');
