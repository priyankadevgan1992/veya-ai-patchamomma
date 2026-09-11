// --- VEYA AI LIFE COMPANION WEB CLIENT ---
const API_BASE = "/api";

// Active Session State
let activeUser = {
  email: localStorage.getItem("veya_email"),
  internal_uuid: localStorage.getItem("veya_uuid"),
  persona_name: localStorage.getItem("veya_name"),
  onboarding_completed: localStorage.getItem("veya_onboarding") === "true"
};

let currentAuthMode = "signin";

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  if (!activeUser.internal_uuid) {
    document.getElementById("authModal").classList.remove("hidden");
  } else {
    updateUserUI();
    loadHomeStream();
    loadInsights();
    loadTomorrowPlan();
    checkPendingFeedback();
  }
});

function updateUserUI() {
  const topAvatarBtn = document.getElementById("topAvatarBtn");
  if (topAvatarBtn) {
    topAvatarBtn.textContent = (activeUser.persona_name || activeUser.email).charAt(0).toUpperCase();
  }
  fetchNotifications();
}

// --- NOTIFICATIONS SYSTEM ---
async function fetchNotifications() {
  if (!activeUser.internal_uuid) return;
  try {
    const res = await fetch(`${API_BASE}/notifications?uuid=${activeUser.internal_uuid}`);
    if (res.ok) {
      const data = await res.json();
      renderNotifications(data.notifications);
    }
  } catch (err) {
    console.error("Error fetching notifications:", err);
  }
}

function renderNotifications(notifs) {
  const badge = document.getElementById("notifBadge");
  const list = document.getElementById("notifList");
  
  if (!notifs || notifs.length === 0) {
    badge.style.display = "none";
    list.innerHTML = `<div class="empty-plain">No new activity.</div>`;
    return;
  }
  
  badge.style.display = "inline-block";
  
  list.innerHTML = notifs.map(n => `
    <div class="activity-row unseen" id="notif-${n.id}">
      <div class="act-avatar">⏰</div>
      <div class="act-text"><b>Reminder</b> <span class="t">${n.text}</span></div>
      <div class="act-cta" onclick="dismissNotification('${n.id}')">Done</div>
    </div>
  `).join("");
}

function toggleNotifPopup() {
  document.getElementById("notifPopup").classList.toggle("hidden");
}

async function dismissNotification(id) {
  try {
    await fetch(`${API_BASE}/notifications/read`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        notification_id: id
      })
    });
    // Immediately remove from DOM to feel snappy
    const item = document.getElementById(`notif-${id}`);
    if (item) item.remove();
    
    // Re-fetch to sync count
    fetchNotifications();
  } catch (err) {
    console.error("Error dismissing notification:", err);
  }
}

// --- FEEDBACK LOOP ---
let currentPendingOutcomeId = null;

async function checkPendingFeedback() {
  if (!activeUser.internal_uuid) return;
  try {
    const res = await fetch(`${API_BASE}/feedback/pending?uuid=${activeUser.internal_uuid}`);
    if (res.ok) {
      const data = await res.json();
      const banner = document.getElementById("feedbackBanner");
      if (data.has_pending) {
        currentPendingOutcomeId = data.outcome.id;
        document.getElementById("feedbackText").textContent = `You chose "${data.outcome.action_title}" previously. Did it help?`;
        banner.classList.remove("hidden");
      } else {
        banner.classList.add("hidden");
      }
    }
  } catch (err) {
    console.error("Error checking feedback:", err);
  }
}

async function submitFeedback(score) {
  if (!currentPendingOutcomeId) return;
  try {
    await fetch(`${API_BASE}/feedback/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        outcome_id: currentPendingOutcomeId,
        feedback_score: score
      })
    });
    document.getElementById("feedbackBanner").classList.add("hidden");
    currentPendingOutcomeId = null;
  } catch (err) {
    console.error("Error submitting feedback:", err);
  }
}

// Check notifications every 30 seconds
setInterval(fetchNotifications, 30000);

// --- PROFILE & PREFERENCES MODAL ---

let isEditMode = false;
function toggleEditMode() {
    isEditMode = !isEditMode;
    document.querySelectorAll('.fval, .o-fval').forEach(el => el.disabled = !isEditMode);
    document.getElementById('addOrbitBtn').style.display = isEditMode ? 'block' : 'none';
    document.getElementById('editPersonaBtn').textContent = isEditMode ? 'Cancel Edit' : 'Edit persona';
    
    // Hide remove buttons if not edit mode
    document.querySelectorAll('.orbit-remove').forEach(el => el.style.display = isEditMode ? 'block' : 'none');
    
    // Toggle Done button
    const doneBtn = document.getElementById('profileDoneBtn');
    if(doneBtn) doneBtn.style.display = isEditMode ? 'block' : 'none';
}

function addOrbitRow(name = '', rel = '', ctx = '', imp = 50) {
    const cont = document.getElementById("orbitListContainer");
    const div = document.createElement("div");
    div.className = "orbit-row";
    div.style.flexDirection = "column";
    div.style.alignItems = "stretch";
    div.style.border = "1px solid #eee";
    div.style.padding = "8px";
    div.style.borderRadius = "6px";
    div.style.marginBottom = "8px";
    div.style.position = "relative";
    div.innerHTML = `
      <div style="display:flex; gap:8px; margin-bottom:4px;">
        <input type="text" class="o-fval orbit-name" placeholder="Name" value="${escapeHtml(name)}" ${isEditMode ? '' : 'disabled'} style="flex:1;">
        <input type="text" class="o-fval orbit-rel" placeholder="Relation (e.g. Husband)" value="${escapeHtml(rel)}" ${isEditMode ? '' : 'disabled'} style="flex:1;">
        <button class="orbit-remove" onclick="this.parentElement.parentElement.remove()" style="display: ${isEditMode ? 'block' : 'none'}; border:none; background:transparent; color:red; cursor:pointer;">x</button>
      </div>
      <div style="display:flex; gap:8px;">
        <input type="text" class="o-fval orbit-ctx" placeholder="1-liner context" value="${escapeHtml(ctx)}" ${isEditMode ? '' : 'disabled'} style="flex:2;">
        <input type="number" class="o-fval orbit-imp" placeholder="Importance %" value="${imp}" min="0" max="100" ${isEditMode ? '' : 'disabled'} style="flex:1;">
      </div>
    `;
    cont.appendChild(div);
}

function toggleProfileModal() {
  const modal = document.getElementById("profileModal");
  if (modal.classList.contains("hidden")) {
    isEditMode = false;
    document.getElementById('editPersonaBtn').textContent = 'Edit persona';
    document.getElementById('addOrbitBtn').style.display = 'none';
    const doneBtn = document.getElementById('profileDoneBtn');
    if(doneBtn) doneBtn.style.display = 'none';
    fetchProfileAndReminders();
  }
  modal.classList.toggle("hidden");
}

async function fetchProfileAndReminders() {
  try {
    const res = await fetch(`${API_BASE}/profile?uuid=${activeUser.internal_uuid}`);
    if (res.ok) {
      const data = await res.json();
      document.getElementById("prefName").value = data.persona_name || "";
      document.getElementById("prefStress").value = data.work_stress_level || "Moderate";
      document.getElementById("prefAnchor").value = data.life_anchor || "";
      document.getElementById("prefGender").value = data.gender_identity || "";
      document.getElementById("prefHousehold").value = data.household_members || 0;
      document.getElementById("prefRelHealth").value = data.relationship_health || "Moderate";
      document.getElementById("prefBioPhase").value = data.biological_phase || "Normal";
      document.getElementById("prefMaturity").value = data.twin_maturity_weeks || 0;
      document.getElementById("prefCalendars").value = data.calendars_connected || 0;
      document.getElementById("prefWearable").value = data.wearable_connected || 0;
      
      const rList = document.getElementById("remindersList");
      if (data.reminders && data.reminders.length > 0) {
        rList.innerHTML = data.reminders.map(r => `<li>🕒 ${r.title}</li>`).join("");
      } else {
        rList.innerHTML = "<li><em>No active reminders</em></li>";
      }

      const oCont = document.getElementById("orbitListContainer");
      if(oCont) {
        oCont.innerHTML = "";
        if (data.orbit && data.orbit.length > 0) {
          data.orbit.forEach(o => addOrbitRow(o.person_name, o.relationship_type, o.key_context || '', o.importance_percent || 50));
        } else {
          if (!isEditMode) oCont.innerHTML = "<div style='color:#888;'><em>No members yet</em></div>";
        }
      }
    }
  } catch (err) {
    console.error("Error fetching profile", err);
  }
}

async function savePreferences() {
  const name = document.getElementById("prefName").value;
  const stress = document.getElementById("prefStress").value;
  const anchor = document.getElementById("prefAnchor").value;
  const gender = document.getElementById("prefGender").value;
  const household = parseInt(document.getElementById("prefHousehold").value) || 0;
  const relHealth = document.getElementById("prefRelHealth").value;
  const bioPhase = document.getElementById("prefBioPhase").value;
  const maturity = parseInt(document.getElementById("prefMaturity").value) || 0;
  const calendars = parseInt(document.getElementById("prefCalendars").value) || 0;
  const wearable = parseInt(document.getElementById("prefWearable").value) || 0;
  
  try {
    await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        persona_name: name,
        work_stress_level: stress,
        life_anchor: anchor,
        gender_identity: gender,
        household_members: household,
        relationship_health: relHealth,
        biological_phase: bioPhase,
        twin_maturity_weeks: maturity,
        calendars_connected: calendars,
        wearable_connected: wearable,
        orbit: Array.from(document.querySelectorAll('.orbit-row')).map(row => ({
           person_name: row.querySelector('.orbit-name').value.trim(),
           relationship_type: row.querySelector('.orbit-rel').value.trim(),
           key_context: row.querySelector('.orbit-ctx').value.trim(),
           importance_percent: parseInt(row.querySelector('.orbit-imp').value) || 50
        })).filter(o => o.person_name && o.relationship_type)
      })
    });
    
    // Update local state
    activeUser.persona_name = name;
    localStorage.setItem("veya_name", name);
    
    
    toggleProfileModal(); // Done handles the closing
    isEditMode = false;
  } catch (err) {
    console.error("Error saving preferences", err);
  }
}

// --- AUTH MODAL CONTROLS ---
function toggleAuthModal() {
  const modal = document.getElementById("authModal");
  modal.classList.toggle("hidden");
}

function setAuthMode(mode) {
  currentAuthMode = mode;
  document.getElementById("tabSignInBtn").classList.toggle("active", mode === "signin");
  document.getElementById("tabSignUpBtn").classList.toggle("active", mode === "signup");
  document.getElementById("authSubTitle").textContent = mode === "signin" 
    ? "Sign in to your life companion" 
    : "Create a fresh account & start live onboarding";
  document.getElementById("authSubmitBtn").textContent = mode === "signin" ? "Sign In" : "Create Account";
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("authUsername").value.trim();
  const email = document.getElementById("authEmail") ? document.getElementById("authEmail").value.trim() : "";
  const password = document.getElementById("authPassword").value.trim();

  const endpoint = currentAuthMode === "signup" ? `${API_BASE}/auth/signup` : `${API_BASE}/auth/signin`;

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Authentication failed.");
      return;
    }

    // Save session
    activeUser = {
      email: data.email,
      internal_uuid: data.internal_uuid,
      persona_name: data.persona_name || "Friend",
      onboarding_completed: data.onboarding_completed
    };

    localStorage.setItem("veya_email", activeUser.email);
    localStorage.setItem("veya_uuid", activeUser.internal_uuid);
    localStorage.setItem("veya_name", activeUser.persona_name);
    localStorage.setItem("veya_onboarding", activeUser.onboarding_completed);

    updateUserUI();
    document.getElementById("authModal").classList.add("hidden");

    // Clear and reload fresh home stream
    document.getElementById("homeChatThread").innerHTML = "";
    loadHomeStream();
    loadInsights();
    loadTomorrowPlan();

  } catch (err) {
    console.error("Auth error:", err);
    alert("Connection error. Ensure backend server is running.");
  }
}

function logoutUser() {
  localStorage.clear();
  window.location.reload();
}

// --- HOME CHAT STREAM ---
async function loadHomeStream() {
  try {
    const res = await fetch(`${API_BASE}/home?uuid=${activeUser.internal_uuid}`);
    const data = await res.json();

    const titleEl = document.getElementById("homeGreetingTitle");
    if (titleEl) {
      titleEl.textContent = activeUser.onboarding_completed ? `Hi ${activeUser.persona_name}` : "Welcome to Veya";
    }

    const thread = document.getElementById("homeChatThread");
    thread.innerHTML = "";

    // Render historical messages if any
    // BUG FIX: User requested fresh chat on sign in, not keeping previous chat.
    // So we don't render data.history here.
    
    // Auto-scroll to bottom of empty/newly loaded chat
    thread.scrollTop = thread.scrollHeight;
    
    // First greeting
    appendAssistantMessage(data.greeting);

  } catch (err) {
    console.error("Error loading home:", err);
  }
}

function handleHomeChatKeyPress(e) {
  if (e.key === "Enter") {
    sendHomeChatMessage();
  }
}

async function sendHomeChatMessage() {
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

  // Show typing indicator
  const typing = document.getElementById("homeChatTyping");
  const thread = document.getElementById("homeChatThread");
  
  thread.appendChild(typing);
  typing.classList.remove("hidden");
  
  // Ensure the typing indicator is visible by scrolling to it
  setTimeout(() => {
    thread.scrollTop = thread.scrollHeight + 100;
  }, 10);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        message: msg || (payloadMedia ? "Please analyze this attached media." : ""),
        media_data: payloadMedia,
        media_mime_type: payloadMime
      })
    });

    const data = await res.json();
    typing.classList.add("hidden");

    // Check if onboarding completed during this turn
    if (data.onboarding_active === false && !activeUser.onboarding_completed) {
      activeUser.onboarding_completed = true;
      localStorage.setItem("veya_onboarding", "true");
    }

    appendAssistantMessage(data.reply, data.has_action_card ? data.actions : null);

  } catch (err) {
    typing.classList.add("hidden");
    appendAssistantMessage("I'm having a slight trouble connecting to my life graph right now.");
  }
}

function appendUserMessage(text) {
  const thread = document.getElementById("homeChatThread");
  const div = document.createElement("div");
  div.className = "msg user";
  div.textContent = text;
  thread.appendChild(div);
  thread.scrollTop = thread.scrollHeight;
}

function escapeJsStr(str) {
  if (!str) return "";
  return str.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/"/g, "\\\"").replace(/\n/g, "\\n");
}

function appendAssistantMessage(text, actions = null) {
  const thread = document.getElementById("homeChatThread");
  const div = document.createElement("div");
  div.className = "msg bot";
  
  let contentHtml = escapeHtml(text);
  
  if (actions && actions.length > 0) {
    contentHtml += `<div style="margin-top: 10px;">`;
    actions.forEach(act => {
      contentHtml += `
        <div class="action-card" id="${act.id}">
          <h4>${escapeHtml(act.title)}</h4>
          ${act.description ? `<p style="font-size: 13px; color: #555; margin-bottom: 8px;">${escapeHtml(act.description)}</p>` : ''}
          <button class="action-approve-btn" onclick="executeAction(\'${escapeHtml(escapeJsStr(act.id))}\', \'${escapeHtml(escapeJsStr(act.title))}\', this)">
            ${act.type === 'VOICE_CALL_OFFER' ? 'Start Call' : 'Approve & Apply'}
          </button>
        </div>
      `;
    });
    contentHtml += `</div>`;
  }

  div.innerHTML = contentHtml;
  thread.appendChild(div);
  thread.scrollTop = thread.scrollHeight;
}

let voiceCallWs = null;
let voiceCallStream = null;
let voiceCallAudioContext = null;
let voiceCallPlayContext = null;
let voiceFallbackAudio = null;

async function executeAction(actionId, title, btnElement = null) {
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
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${location.host}/api/voice/stream?uuid=${activeUser.internal_uuid}`;
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
  }

  let btn = btnElement;
  if (!btn) {
    const card = document.getElementById(actionId);
    if (card) {
      btn = card.querySelector(".action-approve-btn") || card.querySelector("button");
    }
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = "Applying to Calendar...";
  }

  try {
    const res = await fetch(`${API_BASE}/actions/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        action_id: actionId,
        title: title
      })
    });

    const data = await res.json();
    if (btn) {
      if (data.status === "EXECUTED_ON_GOOGLE_CALENDAR") {
        btn.className = "action-approve-btn applied-google";
        btn.textContent = "✓ Added to Google Calendar";
      } else {
        btn.className = "action-approve-btn applied";
        btn.textContent = "✓ Applied";
      }
    }
  } catch (err) {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Error - Retry";
    }
  }
}

function endVoiceCall() {
  document.getElementById("voiceCallModal").classList.add("hidden");
  
  if (voiceCallWs) {
    voiceCallWs.close();
    voiceCallWs = null;
  }
  if (voiceCallStream) {
    voiceCallStream.getTracks().forEach(track => track.stop());
    voiceCallStream = null;
  }
  if (voiceCallAudioContext) {
    voiceCallAudioContext.close();
    voiceCallAudioContext = null;
  }
  if (voiceCallPlayContext) {
    voiceCallPlayContext.close();
    voiceCallPlayContext = null;
  }
  
  if (voiceFallbackAudio) {
    voiceFallbackAudio.pause();
    voiceFallbackAudio.currentTime = 0;
    voiceFallbackAudio = null;
  }
  
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  
  // The specific chat message logging is now handled in the callbacks 
  // to differentiate between successful calls, manual hangups, and fallback MP3s.
}

// --- INSIGHTS & DERIVATION ---
async function loadInsights() {
  try {
    const res = await fetch(`${API_BASE}/insights?uuid=${activeUser.internal_uuid}`);
    const data = await res.json();

    document.getElementById("twinMaturityLabel").textContent = data.twin_maturity;
    
    if (data.actionable_advice) {
        document.getElementById("insightActionableBlock").classList.remove("hidden");
        document.getElementById("insightActionableText").textContent = data.actionable_advice.text;
        
        // Store the nudge intent globally for the button to use
        window.currentInsightNudge = data.actionable_advice.nudge_action;
        
        const btn = document.getElementById("insightNudgeBtn");
        btn.innerHTML = `<span style="font-size: 1rem;">🔔</span> Nudge Me`;
        btn.disabled = false;
        btn.style.opacity = "1";
    } else {
        document.getElementById("insightActionableBlock").classList.add("hidden");
    }

    const grid = document.getElementById("insightsGrid");
    grid.innerHTML = data.scores.map(s => `
      <div class="stat" onclick="openDerivationDrawer('${s.name}', ${s.value})">
        <div class="num">${s.value}</div>
        <div class="label">${s.name}</div>
        <div class="delta ${s.value < 70 ? 'down' : 'up'}">${s.value < 70 ? '↓ Attention' : '↑ Optimal'}</div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error loading insights:", err);
  }
}

async function triggerInsightNudge() {
  if (!window.currentInsightNudge) return;
  
  const btn = document.getElementById("insightNudgeBtn");
  btn.disabled = true;
  btn.style.opacity = "0.7";
  btn.innerHTML = `Setting...`;
  
  try {
    await fetch(`${API_BASE}/actions/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        action_id: "opt_set_reminder",
        title: window.currentInsightNudge
      })
    });
    
    btn.innerHTML = `✓ Nudge Scheduled`;
  } catch (e) {
    btn.innerHTML = `Error`;
  }
}

async function openDerivationDrawer(metricName, score) {
  const drawer = document.getElementById("derivationDrawer");
  document.getElementById("drawerMetricTitle").textContent = `${metricName} Derivation`;
  document.getElementById("drawerScoreBadge").textContent = `${score} / 100`;

  const list = document.getElementById("derivationList");
  list.innerHTML = "";
  document.getElementById("drawerTypingIndicator").classList.remove("hidden");
  drawer.classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/insights/derive`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_uuid: activeUser.internal_uuid,
        metric_name: metricName,
        score: score
      })
    });
    const data = await res.json();
    document.getElementById("drawerTypingIndicator").classList.add("hidden");

    
      list.innerHTML = `
        <div style="padding-bottom: 12px; font-size: 13.5px; color: #333; line-height: 1.4;">
          <strong>Analysis:</strong> ${escapeHtml(data.reason || '')}
        </div>
        <div style="padding-bottom: 16px; font-size: 13.5px; color: #333; line-height: 1.4;">
          <strong>Recommendation:</strong> ${escapeHtml(data.recommendation || '')}
        </div>
        <div class="pill-row">
          ${(data.provenance || []).map(line => `<div class="pill outline animate-fade-in">${escapeHtml(line)}</div>`).join("")}
        </div>
      `;

  } catch (err) {
    document.getElementById("drawerTypingIndicator").classList.add("hidden");
  }
}

function closeDerivationDrawer() {
  document.getElementById("derivationDrawer").classList.add("hidden");
}

// --- PLANNING MODULE ---

window.cachedPlanData = null;

function renderPlan() {
    if (!window.cachedPlanData) return;
    const data = window.cachedPlanData;
    
    const extContainer = document.getElementById("planningExistingList");
    if (data.existing_items && data.existing_items.length > 0) {
        extContainer.innerHTML = data.existing_items.map(item => `
          <div class="plan-row plan-fixed" style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="openDummyCalendar()">
            <div style="display:flex; gap:15px; align-items:center;">
                <div class="plan-time">${item.time.split(" - ")[0]}</div>
                <div>
                  <div class="plan-title">${escapeHtml(item.title)}</div>
                  <div class="plan-tag">Existing</div>
                </div>
            </div>
            <div onclick="event.stopPropagation(); removeCalendarItem('${item.id}')" style="color:var(--danger); font-size:20px; padding:5px 10px; cursor:pointer;" title="Remove">✕</div>
          </div>
        `).join("");
    } else {
        extContainer.innerHTML = '<div style="padding:15px 20px; color:#888; font-style:italic;">Nothing planned</div>';
    }

    const sugContainer = document.getElementById("planningSuggestedList");
    sugContainer.innerHTML = data.suggested_items.map(item => `
      <div class="plan-row" id="plan-item-${item.id}">
        <div class="plan-time">${(item.time || '').split(" - ")[0]}</div>
        <div class="plan-card-body">
          <div class="tag-row"><span class="tag ${item.priority === 'High' ? 'conflict' : ''}">${item.priority} Priority</span></div>
          <div class="plan-card-title">${escapeHtml(item.title)}</div>
          <div class="plan-rationale">💡 ${escapeHtml(item.rationale || 'Suggested based on your flow.')}</div>
          <div class="pill-row">
            ${item.locked ? 
                `<div class="pill fill" style="background:#E8F8EE; color:#1B7F3D;">✓ Confirmed</div>
                 <div class="pill text" onclick="openFeasibilityDrawer('${item.id}', '${escapeHtml(item.title)}')">⚙️ Adjust</div>` : 
                `<div class="pill outline plan-feasible-btn" onclick="markFeasible('${item.id}')">✓ Lock In</div>
                 <div class="pill text" onclick="openFeasibilityDrawer('${item.id}', '${escapeHtml(item.title)}')">⚙️ Adjust</div>`
            }
          </div>
        </div>
      </div>
    `).join("");
}

async function loadTomorrowPlan() {
  try {
    const res = await fetch(`${API_BASE}/planning/tomorrow?uuid=${activeUser.internal_uuid}`);
    window.cachedPlanData = await res.json();
    renderPlan();
  } catch (err) {
    console.error("Error loading plan:", err);
  }
}

function removeCalendarItem(itemId) {
    if (!window.cachedPlanData) return;
    const itemIndex = window.cachedPlanData.existing_items.findIndex(i => i.id === itemId);
    if (itemIndex > -1) {
        const item = window.cachedPlanData.existing_items.splice(itemIndex, 1)[0];
        window.cachedPlanData.suggested_items.push(item);
        renderPlan();
    }
}


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
        const item = window.cachedPlanData.suggested_items.find(i => i.id == activeFeasibleItemId);
        if (item) {
            item.locked = false;
            // Optionally remove [Reschedule] or [Delegate] tags if user canceled them
            item.title = item.title.replace(/^\[.*?\]\s*/, '');
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
function markFeasible(itemId) {
    if(!window.cachedPlanData) return;
    const item = window.cachedPlanData.suggested_items.find(i => i.id == itemId);
    if(item) {
        item.locked = true;
        renderPlan();
    }
}

// --- TAB NAVIGATION ---
function switchTab(tabId) {
    const fab = document.getElementById('fabFinalList');
    if(fab) {
        if(tabId === 'planning') fab.classList.remove('hidden');
        else fab.classList.add('hidden');
    }
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');

  document.querySelectorAll('.tabbar .tab').forEach(el => {
    el.classList.remove('active');
    el.classList.add('inactive');
  });
  
  const navBtn = document.getElementById('nav-' + tabId);
  if (navBtn) {
    navBtn.classList.remove('inactive');
    navBtn.classList.add('active');
  }
}
function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}


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

let speechRec = null;
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

function openDummyCalendar() {
    document.getElementById('dummyCalendarModal').classList.remove('hidden');
}
function closeDummyCalendar() {
    document.getElementById('dummyCalendarModal').classList.add('hidden');
}

function openFinalSchedule() {
    if(!window.cachedPlanData) return;
    
    const existing = window.cachedPlanData.existing_items || [];
    const locked = (window.cachedPlanData.suggested_items || []).filter(i => i.locked);
    
    let all = [...existing, ...locked];
    
    // Sort by time (naive extraction for demo)
    all.sort((a,b) => {
        const parseTime = (t) => {
            if(!t) return 0;
            const str = t.split(' - ')[0];
            let [time, modifier] = str.split(' ');
            let [hours, mins] = time.split(':');
            hours = parseInt(hours);
            if(hours === 12 && modifier === 'AM') hours = 0;
            if(modifier === 'PM' && hours < 12) hours += 12;
            return hours * 60 + parseInt(mins || 0);
        };
        return parseTime(a.time) - parseTime(b.time);
    });
    
    const list = document.getElementById('finalScheduleList');
    list.innerHTML = all.map(item => `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding-bottom:8px;"><div style="font-weight:bold; color:#111;">${(item.time||'').split(' - ')[0]}</div><div style="color:#555; text-align:right;">${escapeHtml(item.title)}</div></div>`).join('');
    
    document.getElementById('finalScheduleModal').classList.remove('hidden');
}
function closeFinalSchedule() {
    document.getElementById('finalScheduleModal').classList.add('hidden');
}
