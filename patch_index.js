const fs = require('fs');
let indexHtml = fs.readFileSync('veya_web/index.html', 'utf8');

// Add FAB button
const fabHtml = `<div id="fabFinalList" class="hidden" style="position:absolute; bottom:80px; right:20px; background:var(--link); color:white; border-radius:50%; width:50px; height:50px; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.2); z-index:50;" onclick="openFinalSchedule()">📅</div>`;

indexHtml = indexHtml.replace('<!-- Bottom Tab Bar -->', fabHtml + '\n    <!-- Bottom Tab Bar -->');

// Add final schedule modal
const finalScheduleModal = `
    <div id="finalScheduleModal" class="overlay-screen hidden" style="background:rgba(0,0,0,0.5); justify-content:center; align-items:center;">
      <div style="background:#fff; border-radius:16px; width:90%; max-height:80%; overflow-y:auto; position:relative; padding:20px;">
        <div class="sheet-close" onclick="closeFinalSchedule()" style="position:absolute; top:10px; right:15px; font-size:20px; cursor:pointer;">✕</div>
        <h3 style="margin-top:0; border-bottom:1px solid #eee; padding-bottom:10px;">Final Daily Flow</h3>
        <div id="finalScheduleList" style="margin-top:15px; display:flex; flex-direction:column; gap:12px;"></div>
      </div>
    </div>
    
    <!-- Dummy Calendar Redirect Modal -->
    <div id="dummyCalendarModal" class="overlay-screen hidden" style="background:rgba(0,0,0,0.5); justify-content:center; align-items:center;">
      <div style="background:#fff; border-radius:16px; width:80%; text-align:center; padding:30px 20px;">
        <div style="font-size:40px; margin-bottom:10px;">🗓️</div>
        <h3 style="margin-top:0; color:#333;">Redirecting to Google Calendar...</h3>
        <p style="color:#666; font-size:14px;">(This is a dummy UX to showcase the flow)</p>
        <div class="pill fill" style="display:inline-block; margin-top:15px;" onclick="closeDummyCalendar()">Got it</div>
      </div>
    </div>
`;

indexHtml = indexHtml.replace('<!-- VOICE CALL OVERLAY -->', finalScheduleModal + '\n    <!-- VOICE CALL OVERLAY -->');

fs.writeFileSync('veya_web/index.html', indexHtml, 'utf8');
console.log('FAB and Modal added to index.html');
