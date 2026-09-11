with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        contentHtml += `
          <div class="action-card" id="${act.id}">
            <h4>${escapeHtml(act.title)}</h4>
            <button onclick="executeAction('${escapeHtml(escapeJsStr(act.id))}', '${escapeHtml(escapeJsStr(act.title))}')">
              ${act.type === 'VOICE_CALL_OFFER' ? 'Start Call' : 'Approve & Apply'}
            </button>
          </div>
        `;"""

new_block = """        contentHtml += `
          <div class="action-card" id="${act.id}">
            <h4>${escapeHtml(act.title)}</h4>
            <button class="action-approve-btn" onclick="executeAction('${escapeHtml(escapeJsStr(act.id))}', '${escapeHtml(escapeJsStr(act.title))}')">
              ${act.type === 'VOICE_CALL_OFFER' ? 'Start Call' : 'Approve & Apply'}
            </button>
          </div>
        `;"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched button class successfully!")
else:
    print("Could not find the block to replace")
