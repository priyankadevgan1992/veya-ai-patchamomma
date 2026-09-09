const fs = require('fs');
let html = fs.readFileSync('veya_web/index.html', 'utf8');

const regex = /<div class="form-row">\s*<div class="flabel">Anchor<\/div>\s*<input id="prefAnchor" class="fval" value="">\s*<\/div>/;

const new_fields = `          <div class="form-row">
            <div class="flabel">Anchor</div>
            <input id="prefAnchor" class="fval" value="">
          </div>
          <div class="form-row">
            <div class="flabel">Gender</div>
            <input id="prefGender" class="fval" value="">
          </div>
          <div class="form-row">
            <div class="flabel">Household</div>
            <input type="number" id="prefHousehold" class="fval" value="0" style="width:100%; border:none; text-align:right; outline:none; background:transparent; font-size:16px;">
          </div>
          <div class="form-row">
            <div class="flabel">Rel. Health</div>
            <select id="prefRelHealth" class="fval">
              <option value="Strong">Strong</option>
              <option value="Moderate">Moderate</option>
              <option value="Strained">Strained</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Bio Phase</div>
            <select id="prefBioPhase" class="fval">
              <option value="Normal">Normal</option>
              <option value="Follicular">Follicular</option>
              <option value="Luteal">Luteal</option>
              <option value="Menstrual">Menstrual</option>
              <option value="Ovulatory">Ovulatory</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Maturity (wks)</div>
            <input type="number" id="prefMaturity" class="fval" value="0" style="width:100%; border:none; text-align:right; outline:none; background:transparent; font-size:16px;">
          </div>
          <div class="form-row">
            <div class="flabel">Calendars</div>
            <select id="prefCalendars" class="fval">
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>
          <div class="form-row">
            <div class="flabel">Wearable</div>
            <select id="prefWearable" class="fval">
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>`;

if (regex.test(html)) {
    html = html.replace(regex, new_fields);
    html = html.replace('<div class="screen active">', '<div class="screen active" style="overflow-y:auto; padding-bottom:50px;">');
    fs.writeFileSync('veya_web/index.html', html, 'utf8');
    console.log('index.html successfully patched!');
} else {
    console.log('Regex did not match. Current anchor HTML:');
    const start = html.indexOf('<div class="flabel">Anchor</div>');
    console.log(html.substring(start - 100, start + 100));
}
