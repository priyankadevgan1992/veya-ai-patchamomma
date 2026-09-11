with open('veya_web/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We will regex replace the executeAction function to add retry logic
old_execute_action_start = r'async function executeAction\(actionId, title\) \{.*?if \(actionId === "opt_voice_call"\) \{'
old_execute_action_end = r'return;\n  \}'

# The regex approach is fragile for multiline, let's just use split or string replacement
old_function_body = '''async function executeAction(actionId, title) {
  if (actionId === "opt_voice_call") {
    document.getElementById("voiceCallModal").classList.remove("hidden");
    
    // Stop existing standard TTS if any
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    
    // Prime the fallback audio during the click event to bypass strict browser autoplay policies
    voiceFallbackAudio = new Audio("/app/fallback.mp3");
    voiceFallbackAudio.play().then(() => {
        voiceFallbackAudio.pause();
        voiceFallbackAudio.currentTime = 0;
    }).catch(e => console.log("Audio priming skipped: ", e));
    
    try {
      const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${location.host}/api/voice/stream?uuid=${activeUser.internal_uuid}`;
      voiceCallWs = new WebSocket(wsUrl);
      voiceCallWs.binaryType = "arraybuffer";
      
      voiceCallWs.onopen = async () => {
        voiceCallStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        voiceCallAudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const source = voiceCallAudioContext.createMediaStreamSource(voiceCallStream);
        
        const scriptProcessor = voiceCallAudioContext.createScriptProcessor(4096, 1, 1);
        source.connect(scriptProcessor);
        scriptProcessor.connect(voiceCallAudioContext.destination);
        
        scriptProcessor.onaudioprocess = (e) => {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            let s = Math.max(-1, Math.min(1, inputData[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          if (voiceCallWs && voiceCallWs.readyState === WebSocket.OPEN) {
            voiceCallWs.send(pcm16.buffer);
          }
        };
      };
      
      voiceCallPlayContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
      
      voiceCallWs.onmessage = async (event) => {
        if (event.data instanceof ArrayBuffer) {
          const int16 = new Int16Array(event.data);
          const float32 = new Float32Array(int16.length);
          for (let i = 0; i < int16.length; i++) {
            float32[i] = int16[i] / 0x7FFF;
          }
          const audioBuffer = voiceCallPlayContext.createBuffer(1, float32.length, 24000);
          audioBuffer.getChannelData(0).set(float32);
          
          const source = voiceCallPlayContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(voiceCallPlayContext.destination);
          source.start();
        }
      };
      
      voiceCallWs.onclose = (e) => {
        if (e.code === 1011) {
            // Depleted credits - play the fallback MP3 instead of closing the modal
            console.log("Credits depleted, falling back to MP3");
            
            // Turn off local microphone stream to stop recording
            if (voiceCallStream) {
                voiceCallStream.getTracks().forEach(track => track.stop());
                voiceCallStream = null;
            }
            
            voiceFallbackAudio.play().catch(err => {
                console.error("Failed to play fallback audio", err);
                endVoiceCall();
                appendAssistantMessage("My Google AI Studio API key has run out of prepayment credits, and fallback audio failed to play.");
            });
            
            voiceFallbackAudio.onended = () => {
                endVoiceCall();
                appendAssistantMessage("It was nice talking to you,, feel free to call again");
            };
        } else {
            endVoiceCall();
            appendAssistantMessage("Voice call ended. I'm here if you need to talk again.");
        }
      };
      
    } catch(err) {
      console.error("Live Audio failed", err);
      appendAssistantMessage("Failed to start the audio stream. Please check console.");
      endVoiceCall();
    }
    
    return;
  }'''

new_function_body = '''async function executeAction(actionId, title) {
  if (actionId === "opt_voice_call") {
    document.getElementById("voiceCallModal").classList.remove("hidden");
    
    // Stop existing standard TTS if any
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    
    // Prime the fallback audio during the click event to bypass strict browser autoplay policies
    voiceFallbackAudio = new Audio("/app/fallback.mp3");
    voiceFallbackAudio.play().then(() => {
        voiceFallbackAudio.pause();
        voiceFallbackAudio.currentTime = 0;
    }).catch(e => console.log("Audio priming skipped: ", e));
    
    let wsRetries = 0;
    const MAX_WS_RETRIES = 3;
    let manualDisconnect = false;

    const connectWS = () => {
        try {
          const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
          const wsUrl = `${wsProtocol}//${location.host}/api/voice/stream?uuid=${activeUser.internal_uuid}`;
          voiceCallWs = new WebSocket(wsUrl);
          voiceCallWs.binaryType = "arraybuffer";
          
          voiceCallWs.onopen = async () => {
            wsRetries = 0; // Reset retries on successful connection
            if (!voiceCallStream) {
                voiceCallStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                voiceCallAudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                const source = voiceCallAudioContext.createMediaStreamSource(voiceCallStream);
                
                const scriptProcessor = voiceCallAudioContext.createScriptProcessor(4096, 1, 1);
                source.connect(scriptProcessor);
                scriptProcessor.connect(voiceCallAudioContext.destination);
                
                scriptProcessor.onaudioprocess = (e) => {
                  const inputData = e.inputBuffer.getChannelData(0);
                  const pcm16 = new Int16Array(inputData.length);
                  for (let i = 0; i < inputData.length; i++) {
                    let s = Math.max(-1, Math.min(1, inputData[i]));
                    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                  }
                  if (voiceCallWs && voiceCallWs.readyState === WebSocket.OPEN) {
                    voiceCallWs.send(pcm16.buffer);
                  }
                };
            }
          };
          
          if (!voiceCallPlayContext) {
            voiceCallPlayContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
          }
          
          voiceCallWs.onmessage = async (event) => {
            if (event.data instanceof ArrayBuffer) {
              const int16 = new Int16Array(event.data);
              const float32 = new Float32Array(int16.length);
              for (let i = 0; i < int16.length; i++) {
                float32[i] = int16[i] / 0x7FFF;
              }
              const audioBuffer = voiceCallPlayContext.createBuffer(1, float32.length, 24000);
              audioBuffer.getChannelData(0).set(float32);
              
              const source = voiceCallPlayContext.createBufferSource();
              source.buffer = audioBuffer;
              source.connect(voiceCallPlayContext.destination);
              source.start();
            }
          };
          
          voiceCallWs.onerror = (e) => {
              console.error("WebSocket error:", e);
          };

          voiceCallWs.onclose = (e) => {
            if (manualDisconnect) return; // Clean exit triggered by user

            if (e.code === 1011) {
                // Depleted credits - play the fallback MP3 instead of closing the modal
                console.log("Credits depleted, falling back to MP3");
                
                // Turn off local microphone stream to stop recording
                if (voiceCallStream) {
                    voiceCallStream.getTracks().forEach(track => track.stop());
                    voiceCallStream = null;
                }
                
                voiceFallbackAudio.play().catch(err => {
                    console.error("Failed to play fallback audio", err);
                    endVoiceCall();
                    appendAssistantMessage("My Google AI Studio API key has run out of prepayment credits, and fallback audio failed to play.");
                });
                
                voiceFallbackAudio.onended = () => {
                    endVoiceCall();
                    appendAssistantMessage("It was nice talking to you, feel free to call again.");
                };
            } else if (e.code !== 1000 && e.code !== 1005) {
                // Unexpected drop (e.g. 1006 network drop)
                if (wsRetries < MAX_WS_RETRIES) {
                    wsRetries++;
                    console.log(`WebSocket dropped (code ${e.code}). Retrying connection (${wsRetries}/${MAX_WS_RETRIES})...`);
                    setTimeout(connectWS, 1000); // Wait 1 sec before retrying
                } else {
                    console.log("Max WebSocket retries reached.");
                    endVoiceCall();
                    appendAssistantMessage("Veya is experiencing high traffic right now. The voice connection dropped after multiple retry attempts. Please try again later.");
                }
            } else {
                endVoiceCall();
                appendAssistantMessage("Voice call ended. I'm here if you need to talk again.");
            }
          };
          
        } catch(err) {
          console.error("Live Audio failed", err);
          if (wsRetries < MAX_WS_RETRIES) {
              wsRetries++;
              setTimeout(connectWS, 1000);
          } else {
              endVoiceCall();
              appendAssistantMessage("Veya is experiencing high traffic right now and failed to start the audio stream. Please try again later.");
          }
        }
    };
    
    // Intercept endVoiceCall to set manual disconnect flag
    const originalEndVoiceCall = window.endVoiceCall;
    window.endVoiceCall = function() {
        manualDisconnect = true;
        originalEndVoiceCall();
    }

    connectWS();
    return;
  }'''

if old_function_body in content:
    content = content.replace(old_function_body, new_function_body)
    with open('veya_web/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched app.js successfully for point 3!")
else:
    print("Failed to find exact block. Let's inspect differences.")
