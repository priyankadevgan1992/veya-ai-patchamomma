const fs = require('fs');

let jsCode = fs.readFileSync('veya_web/app.js', 'utf8');

const newFunctions = `
// --- MULTIMODAL INPUT ---
let currentAttachedMedia = null;
let currentAttachedMimeType = null;
let mediaRecorder = null;
let audioChunks = [];

function triggerFileUpload() {
  document.getElementById("chatFileInput").click();
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = function(e) {
    currentAttachedMedia = e.target.result;
    currentAttachedMimeType = file.type;
    document.getElementById("homeChatInput").placeholder = "File attached. Message...";
    const plusBtn = document.querySelector(".chat-icon-btn.plus");
    if(plusBtn) plusBtn.style.color = "var(--link)";
  };
  reader.readAsDataURL(file);
}

function toggleVoiceRecord() {
  const micBtn = document.querySelector(".chat-icon-btn.mic");
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    if(micBtn) micBtn.style.color = "var(--link)";
    document.getElementById("homeChatInput").placeholder = "Audio attached. Message...";
  } else {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      if(micBtn) micBtn.style.color = "var(--danger)"; // Turn red to indicate recording
      document.getElementById("homeChatInput").placeholder = "Recording audio...";
      
      mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];
        
        const reader = new FileReader();
        reader.onload = function(e) {
          currentAttachedMedia = e.target.result;
          currentAttachedMimeType = "audio/webm";
        };
        reader.readAsDataURL(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
      };
    }).catch(err => {
      console.error("Mic access denied", err);
      alert("Microphone access denied or unavailable.");
    });
  }
}
`;

jsCode += "\n" + newFunctions;

const oldSend = `async function sendHomeChatMessage() {
  const input = document.getElementById("homeChatInput");
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";
  appendUserMessage(msg);

  // Show typing indicator`;

const newSend = `async function sendHomeChatMessage() {
  const input = document.getElementById("homeChatInput");
  const msg = input.value.trim();
  if (!msg && !currentAttachedMedia) return;

  input.value = "";
  input.placeholder = "Message Veya...";
  
  // reset icons
  const plusBtn = document.querySelector(".chat-icon-btn.plus");
  if(plusBtn) plusBtn.style.color = "#8E8E8E";
  const micBtn = document.querySelector(".chat-icon-btn.mic");
  if(micBtn) micBtn.style.color = "#8E8E8E";

  let displayMsg = msg;
  if (currentAttachedMedia) {
      displayMsg += (msg ? " " : "") + (currentAttachedMimeType.startsWith("audio") ? "[Audio Attached]" : "[File Attached]");
  }
  appendUserMessage(displayMsg);
  
  const payloadMedia = currentAttachedMedia;
  const payloadMime = currentAttachedMimeType;
  currentAttachedMedia = null;
  currentAttachedMimeType = null;

  // Show typing indicator`;

jsCode = jsCode.replace(oldSend, newSend);

const oldFetch = `    const res = await fetch(\`\${API_BASE}/chat\`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        message: msg
      })
    });`;

const newFetch = `    const res = await fetch(\`\${API_BASE}/chat\`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        message: msg || (payloadMedia ? "Please analyze this attached media." : ""),
        media_data: payloadMedia,
        media_mime_type: payloadMime
      })
    });`;

jsCode = jsCode.replace(oldFetch, newFetch);

fs.writeFileSync('veya_web/app.js', jsCode, 'utf8');
console.log('app.js patched');
