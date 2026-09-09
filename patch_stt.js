const fs = require('fs');

let js = fs.readFileSync('veya_web/app.js', 'utf8');

const regex = /function toggleVoiceRecord\(\) \{[\s\S]*?\}\n\}\n/;

const newFunction = `let speechRec = null;
let isRecording = false;

function toggleVoiceRecord() {
  const micBtn = document.querySelector(".chat-icon-btn.mic");
  const inputField = document.getElementById("homeChatInput");
  
  if (isRecording && speechRec) {
    speechRec.stop();
    return;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Please use Chrome.");
    return;
  }
  
  speechRec = new SpeechRecognition();
  speechRec.continuous = true;
  speechRec.interimResults = true;
  
  let originalValue = inputField.value;
  
  speechRec.onstart = () => {
    isRecording = true;
    if(micBtn) micBtn.style.color = "var(--danger)";
    inputField.placeholder = "Listening...";
  };
  
  speechRec.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    inputField.value = originalValue + (originalValue && transcript ? " " : "") + transcript;
  };
  
  speechRec.onerror = (event) => {
    console.error("Speech recognition error", event.error);
  };
  
  speechRec.onend = () => {
    isRecording = false;
    if(micBtn) micBtn.style.color = "#8E8E8E";
    inputField.placeholder = "Message Veya...";
  };
  
  speechRec.start();
}
`;

js = js.replace(regex, newFunction);
fs.writeFileSync('veya_web/app.js', js, 'utf8');
console.log('toggleVoiceRecord replaced with STT');
