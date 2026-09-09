const fs = require('fs');

// 1. index.html
let html = fs.readFileSync('veya_web/index.html', 'utf8');

const oldInputRow = `      <div class="chat-input-row">
        <button class="chat-icon-btn plus" title="Attach file" style="border:none;background:none;font-size:24px;color:#8E8E8E;cursor:pointer;padding:0 4px;font-weight:300;">+</button>
        <input type="text" id="homeChatInput" class="chat-input" placeholder="Message Veya..." onkeypress="handleHomeChatKeyPress(event)">
        <button class="chat-icon-btn mic" title="Voice input" style="border:none;background:none;font-size:18px;color:#8E8E8E;cursor:pointer;padding:0 4px;">🎙️</button>
        <button class="chat-send" onclick="sendHomeChatMessage()">↑</button>
      </div>`;

const newInputRow = `      <div class="chat-input-row">
        <input type="file" id="chatFileInput" class="hidden" onchange="handleFileSelect(event)">
        <button class="chat-icon-btn plus" title="Attach file" style="border:none;background:none;font-size:24px;color:#8E8E8E;cursor:pointer;padding:0 4px;font-weight:300;" onclick="triggerFileUpload()">+</button>
        <input type="text" id="homeChatInput" class="chat-input" placeholder="Message Veya..." onkeypress="handleHomeChatKeyPress(event)">
        <button class="chat-icon-btn mic" title="Voice input" style="border:none;background:none;font-size:18px;color:#8E8E8E;cursor:pointer;padding:0 4px;" onclick="toggleVoiceRecord()">🎙️</button>
        <button class="chat-send" onclick="sendHomeChatMessage()">↑</button>
      </div>`;

html = html.replace(oldInputRow, newInputRow);
fs.writeFileSync('veya_web/index.html', html, 'utf8');

console.log('Frontend HTML patched.');
