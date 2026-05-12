"""
build_html.py
Baut scanner-app.html mit eingebettetem ARTICLES_DB JSON.
Ausfuehren: python build_html.py
"""
import json, os

data = json.load(open("articles.json", encoding="utf-8"))
compact_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>DEXIS Scanner</title>
<style>
:root{
  --primary:#1a237e;--primary-light:#3949ab;--primary-dark:#0d1257;
  --danger:#c62828;--danger-light:#ef5350;
  --success:#2e7d32;--warn:#e65100;
  --bg:#f5f6fa;--card:#fff;--text:#1a1a2e;--muted:#666;
  --border:#dde1f0;--radius:14px;--shadow:0 2px 12px rgba(26,35,126,.10);
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Segoe UI',Arial,sans-serif;font-size:18px;}

/* HEADER */
#header{
  position:sticky;top:0;z-index:100;
  background:var(--primary);color:#fff;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 16px;height:60px;
  box-shadow:0 2px 8px rgba(0,0,0,.3);
}
#header h1{font-size:22px;font-weight:700;letter-spacing:.5px;}
#menuBtn{
  background:none;border:none;color:#fff;cursor:pointer;
  padding:8px;border-radius:8px;display:flex;flex-direction:column;gap:5px;
  min-width:44px;min-height:44px;align-items:center;justify-content:center;
}
#menuBtn span{display:block;width:26px;height:3px;background:#fff;border-radius:2px;}

/* MAIN */
#main{max-width:700px;margin:0 auto;padding:16px 12px 100px;}

/* SECTIONS */
.section{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px 16px;margin-bottom:16px;}
.section h2{font-size:20px;font-weight:700;color:var(--primary);margin-bottom:14px;display:flex;align-items:center;gap:8px;}
.section h2 .icon{font-size:22px;}

/* SCANNER AREA */
#cameraContainer{position:relative;width:100%;max-width:420px;margin:0 auto 14px;display:none;}
#videoEl{width:100%;border-radius:12px;background:#000;}
#scanOverlay{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:70%;height:40%;border:3px solid #fff;border-radius:8px;
  box-shadow:0 0 0 9999px rgba(0,0,0,.45);pointer-events:none;
}
#scanLine{
  position:absolute;top:0;left:0;right:0;height:3px;background:#ef5350;
  animation:scanAnim 2s linear infinite;
}
@keyframes scanAnim{0%{top:0}50%{top:calc(100% - 3px)}100%{top:0}}

#switchCameraBtn{
  display:none;position:absolute;top:8px;right:8px;
  background:rgba(0,0,0,.55);color:#fff;border:none;border-radius:8px;
  padding:8px 12px;font-size:16px;cursor:pointer;
}

.scanMode{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;}
.modeBtn{
  flex:1;min-width:130px;min-height:44px;border:2px solid var(--primary);
  background:#fff;color:var(--primary);border-radius:10px;
  font-size:17px;font-weight:600;cursor:pointer;transition:.2s;
}
.modeBtn.active{background:var(--primary);color:#fff;}

#scanInputWrap{position:relative;}
#scanInput{
  width:100%;min-height:58px;font-size:20px;padding:10px 52px 10px 16px;
  border:3px solid var(--primary);border-radius:12px;outline:none;
  background:#fff;color:var(--text);
  transition:border-color .2s;
}
#scanInput:focus{border-color:var(--primary-light);box-shadow:0 0 0 3px rgba(57,73,171,.18);}
#scanInput::placeholder{color:#aaa;}
#clearScanBtn{
  position:absolute;right:12px;top:50%;transform:translateY(-50%);
  background:none;border:none;font-size:24px;cursor:pointer;color:#aaa;
  min-width:40px;min-height:40px;display:flex;align-items:center;justify-content:center;
}

#scanStatus{margin-top:8px;font-size:16px;color:var(--muted);min-height:22px;}

/* SCAN-BUTTON */
#scanBtn{
  width:100%;min-height:62px;font-size:22px;font-weight:700;
  background:var(--primary);color:#fff;border:none;border-radius:12px;
  cursor:pointer;margin-bottom:12px;letter-spacing:.5px;
  box-shadow:0 4px 14px rgba(26,35,126,.3);
  transition:.2s;display:flex;align-items:center;justify-content:center;gap:10px;
}
#scanBtn.ready{background:var(--primary);}
#scanBtn.waiting{background:#78909c;cursor:not-allowed;}
#scanBtn.scanned{background:var(--success);}
#scanCountdown{font-size:14px;font-weight:400;opacity:.85;}

/* ====================================================
   SUCHE
   ==================================================== */
.searchWrap{
  display:flex;gap:8px;align-items:center;margin-bottom:10px;
}
#searchInput{
  flex:1;min-height:52px;font-size:18px;padding:10px 14px;
  border:2px solid var(--border);border-radius:12px;outline:none;
  background:#fff;color:var(--text);transition:border-color .2s;
}
#searchInput:focus{border-color:var(--primary);}
#searchInput::placeholder{color:#aaa;}
#micBtn{
  width:52px;height:52px;border-radius:50%;
  border:2px solid var(--primary-light);
  background:#fff;color:var(--primary);
  font-size:22px;cursor:pointer;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  transition:.2s;
}
#micBtn.active{
  background:#c62828;border-color:#c62828;color:#fff;
  animation:micPulse 1s ease-in-out infinite;
}
@keyframes micPulse{
  0%,100%{box-shadow:0 0 0 0 rgba(198,40,40,.5);}
  50%{box-shadow:0 0 0 10px rgba(198,40,40,0);}
}
#searchResults{
  border-radius:12px;overflow:hidden;
  border:1px solid var(--border);
  display:none;
  max-height:340px;overflow-y:auto;
  background:#fff;
  box-shadow:var(--shadow);
}
.srItem{
  display:flex;align-items:center;gap:10px;
  padding:12px 14px;cursor:pointer;
  border-bottom:1px solid var(--border);
  transition:background .15s;
}
.srItem:last-child{border-bottom:none;}
.srItem:hover,.srItem:active{background:#eef0fb;}
.srLeft{flex:1;min-width:0;}
.srNum{font-size:13px;font-weight:800;color:var(--primary);}
.srName{font-size:15px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.srRight{text-align:right;flex-shrink:0;}
.srPrice{font-size:14px;font-weight:700;color:var(--success);}
.srMeter{font-size:12px;color:var(--warn);font-weight:600;}
.srNoResult{padding:14px;color:var(--muted);font-size:15px;text-align:center;}

/* ====================================================
   ARTIKEL LISTE
   ==================================================== */
#articleCount{font-size:16px;color:var(--muted);margin-bottom:10px;}
#emptyHint{text-align:center;padding:24px 0;color:#aaa;font-size:17px;display:block;}

.articleCard{
  background:var(--card);border-radius:12px;
  margin-bottom:8px;border:2px solid var(--border);
  box-shadow:0 1px 6px rgba(26,35,126,.08);
  display:flex;align-items:stretch;overflow:hidden;
  transition:border-color .2s;
}
.articleCard.unknown{border-color:#ffa726;background:#fffbf0;}
.articleCard.new-flash{animation:cardFlash .4s ease;}
@keyframes cardFlash{0%{background:#c8e6ff}100%{background:var(--card)}}

.cardStripe{width:6px;background:var(--primary);flex-shrink:0;}
.articleCard.unknown .cardStripe{background:#ffa726;}

.cardBody{flex:1;padding:10px 12px;min-width:0;}
.cardNum{font-size:15px;font-weight:800;color:var(--primary);letter-spacing:.3px;}
.cardName{font-size:16px;font-weight:600;color:var(--text);margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.cardBC{font-size:12px;color:var(--muted);font-family:monospace;margin-top:2px;}
.cardPrice{font-size:13px;color:var(--success);font-weight:700;margin-top:3px;}
.unknownBadge{font-size:12px;color:#f57c00;font-weight:700;}

/* Menge + Loeschen */
.cardRight{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:8px 10px;gap:10px;
  flex-shrink:0;border-left:1px solid var(--border);
  background:#fafbff;
}
.qtyBadge{display:flex;align-items:center;gap:4px;}
.qtyMinus,.qtyPlus{
  width:34px;height:34px;border:none;border-radius:8px;
  font-size:22px;font-weight:700;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
}
.qtyMinus{background:#ffebee;color:var(--danger);}
.qtyPlus{background:#e8f5e9;color:var(--success);}
.qtyNum{min-width:28px;text-align:center;font-size:20px;font-weight:700;color:var(--text);}
.deleteBtn{
  width:40px;height:40px;border:none;
  background:#ffebee;color:var(--danger);
  border-radius:8px;font-size:20px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
}
.deleteBtn:active{background:var(--danger);color:#fff;}

/* Meter-Eingabe */
.meterWrap{display:flex;align-items:center;gap:4px;}
.meterInput{
  width:68px;height:38px;font-size:18px;text-align:center;font-weight:700;
  border:2px solid var(--primary-light);border-radius:8px;outline:none;
  background:#fff;color:var(--text);
}
.meterInput:focus{border-color:var(--primary);box-shadow:0 0 0 2px rgba(57,73,171,.18);}
.meterUnit{font-size:16px;font-weight:700;color:var(--muted);}

/* Gesamtsumme */
#totalBar{
  margin-top:14px;padding:14px 18px;
  background:linear-gradient(135deg,var(--primary),var(--primary-light));
  border-radius:12px;display:flex;align-items:center;
  justify-content:space-between;color:#fff;
}
.totalLabel{font-size:15px;font-weight:600;opacity:.9;}
#totalAmt{font-size:26px;font-weight:800;letter-spacing:.5px;}

/* KUNDENDATEN */
.formRow{display:flex;flex-direction:column;gap:6px;margin-bottom:14px;}
.formRow label{font-size:20px;font-weight:700;color:var(--text);}
.formRow label .req{color:var(--danger);}
.formRow input,.formRow textarea{
  width:100%;min-height:52px;font-size:18px;padding:10px 14px;
  border:2px solid var(--border);border-radius:10px;outline:none;
  font-family:inherit;background:#fff;color:var(--text);
  transition:border-color .2s;
}
.formRow input:focus,.formRow textarea:focus{border-color:var(--primary);}
.formRow input.error{border-color:var(--danger);}
.formRow textarea{min-height:80px;resize:vertical;}

/* FERTIG BUTTON */
#fertigBtn{
  width:100%;min-height:64px;font-size:24px;font-weight:700;
  background:var(--success);color:#fff;border:none;border-radius:14px;
  cursor:pointer;letter-spacing:.5px;box-shadow:0 4px 16px rgba(46,125,50,.3);
  transition:.2s;display:flex;align-items:center;justify-content:center;gap:10px;
}
#fertigBtn:hover{background:#1b5e20;transform:translateY(-1px);}
#fertigBtn:active{transform:translateY(0);}

/* TOAST */
#toastContainer{
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
  z-index:9999;display:flex;flex-direction:column;gap:8px;
  pointer-events:none;max-width:90vw;
}
.toast{
  background:#323232;color:#fff;padding:14px 22px;border-radius:12px;
  font-size:17px;text-align:center;pointer-events:auto;
  animation:toastIn .3s ease;box-shadow:0 4px 16px rgba(0,0,0,.3);
  min-width:200px;
}
.toast.success{background:var(--success);}
.toast.error{background:var(--danger);}
.toast.warn{background:var(--warn);}
@keyframes toastIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

/* SETTINGS MODAL */
#settingsOverlay{
  display:none;position:fixed;inset:0;z-index:200;
  background:rgba(0,0,0,.55);align-items:flex-start;justify-content:flex-end;
}
#settingsOverlay.open{display:flex;}
#settingsPanel{
  background:#fff;width:320px;max-width:95vw;height:100%;
  overflow-y:auto;padding:24px 20px;
  box-shadow:-4px 0 24px rgba(0,0,0,.2);
}
#settingsPanel h2{font-size:22px;color:var(--primary);margin-bottom:20px;}
.settingRow{margin-bottom:18px;}
.settingRow label{display:block;font-size:17px;font-weight:600;margin-bottom:6px;}
.settingRow input[type=text],.settingRow input[type=email]{
  width:100%;min-height:48px;font-size:16px;padding:8px 12px;
  border:2px solid var(--border);border-radius:10px;outline:none;
}
.settingRow input:focus{border-color:var(--primary);}
.settingRow select{
  width:100%;min-height:48px;font-size:16px;padding:8px 12px;
  border:2px solid var(--border);border-radius:10px;background:#fff;
}
.settingInfo{font-size:14px;color:var(--muted);margin-top:4px;}
#closeSettingsBtn{
  width:100%;min-height:52px;font-size:18px;font-weight:700;
  background:var(--primary);color:#fff;border:none;border-radius:12px;
  cursor:pointer;margin-top:10px;
}
#dangerClearBtn{
  width:100%;min-height:52px;font-size:17px;
  background:#ffebee;color:var(--danger);border:2px solid var(--danger);
  border-radius:12px;cursor:pointer;font-weight:600;margin-top:8px;
}

/* FAB Scroll-to-top */
#fabScroll{
  display:none;position:fixed;bottom:84px;right:16px;z-index:50;
  width:52px;height:52px;border-radius:50%;
  background:var(--primary);color:#fff;border:none;cursor:pointer;
  font-size:24px;box-shadow:0 4px 16px rgba(26,35,126,.4);
}

@media(max-width:480px){
  #main{padding:10px 8px 90px;}
  .section{padding:14px 12px;}
}
</style>
</head>
<body>

<!-- HEADER -->
<div id="header">
  <h1>DEXIS Scanner</h1>
  <button id="menuBtn" aria-label="Einstellungen" onclick="openSettings()">
    <span></span><span></span><span></span>
  </button>
</div>

<!-- MAIN -->
<div id="main">

  <!-- SCANNER SECTION -->
  <div class="section">
    <h2><span class="icon">📷</span> Barcode scannen</h2>

    <div class="scanMode">
      <button class="modeBtn active" id="btnModeAuto"   onclick="setMode('auto')">Automatisch</button>
      <button class="modeBtn"        id="btnModeCamera" onclick="setMode('camera')">Kamera</button>
      <button class="modeBtn"        id="btnModeUSB"    onclick="setMode('usb')">USB-Scanner</button>
    </div>

    <div id="cameraContainer">
      <div id="videoEl" style="width:100%;border-radius:12px;overflow:hidden;"></div>
      <button id="switchCameraBtn" onclick="switchCamera()">🔄 Kamera wechseln</button>
    </div>

    <button id="scanBtn" class="ready" onclick="onScanBtnClick()">
      📷 SCANNEN
      <span id="scanCountdown"></span>
    </button>

    <div id="scanInputWrap">
      <input type="text" id="scanInput" placeholder="Barcode manuell eingeben..."
             autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
             inputmode="none">
      <button id="clearScanBtn" onclick="clearScanInput()" title="Leeren">✕</button>
    </div>
    <div id="scanStatus">Bereit – SCANNEN drücken.</div>
  </div>

  <!-- SUCHE SECTION -->
  <div class="section">
    <h2><span class="icon">🔍</span> Artikel suchen &amp; hinzufügen</h2>
    <div class="searchWrap">
      <input type="text" id="searchInput"
             placeholder="Suchen: z.B. Hydraulikleitung 8x1 ..."
             autocomplete="off" autocorrect="off" spellcheck="false"
             oninput="onSearchInput()">
      <button id="micBtn" onclick="toggleVoice()" title="Sprachsuche starten">🎤</button>
    </div>
    <div id="searchResults"></div>
  </div>

  <!-- ARTIKEL LISTE -->
  <div class="section">
    <h2><span class="icon">📋</span> Gescannte Artikel</h2>
    <div id="articleCount"></div>
    <span id="emptyHint">Noch keine Artikel gescannt.</span>
    <div id="articleList"></div>
    <!-- Gesamtsumme (nur sichtbar wenn Preise vorhanden) -->
    <div id="totalBar" style="display:none;">
      <span class="totalLabel">&#x3A3; Gesamtbetrag exkl. MwSt.</span>
      <strong id="totalAmt">&#x20AC;&nbsp;0,00</strong>
    </div>
  </div>

  <!-- KUNDENDATEN -->
  <div class="section">
    <h2><span class="icon">👤</span> Kundendaten</h2>
    <div class="formRow">
      <label for="custName">Name <span class="req">*</span></label>
      <input type="text" id="custName" placeholder="Kundenname" oninput="saveCustomer()">
    </div>
    <div class="formRow">
      <label for="custAddr">Adresse</label>
      <textarea id="custAddr" placeholder="Strasse, PLZ Ort (optional)" oninput="saveCustomer()"></textarea>
    </div>
  </div>

  <!-- FERTIG BUTTON -->
  <button id="fertigBtn" onclick="onFertig()">
    FERTIG ✓
  </button>

</div><!-- /main -->

<!-- SCROLL FAB -->
<button id="fabScroll" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Nach oben">▲</button>

<!-- TOAST CONTAINER -->
<div id="toastContainer"></div>

<!-- SETTINGS OVERLAY -->
<div id="settingsOverlay" onclick="overlayClick(event,'settingsOverlay')">
<div id="settingsPanel">
  <h2>⚙️ Einstellungen</h2>

  <div class="settingRow">
    <label>Firmenname (PDF-Kopfzeile)</label>
    <input type="text" id="setFirma" value="DEXIS" oninput="saveSetting('firma',this.value)">
  </div>
  <div class="settingRow">
    <label>E-Mail Empfänger</label>
    <input type="email" id="setEmail" value="office@kfz-dorn.at" oninput="saveSetting('email',this.value)">
  </div>
  <div class="settingRow">
    <label>E-Mail CC</label>
    <input type="email" id="setEmailCC" placeholder="cc@beispiel.at" oninput="saveSetting('emailCC',this.value)">
  </div>
  <div class="settingRow">
    <label>Scanner-Modus</label>
    <select id="setMode" onchange="saveSetting('mode',this.value);applyMode(this.value)">
      <option value="auto">Automatisch</option>
      <option value="camera">Kamera</option>
      <option value="usb">USB-Tastatur</option>
    </select>
  </div>
  <div class="settingRow">
    <label>Kamera wählen</label>
    <select id="setCameraSelect" onchange="changeCamera(this.value)">
      <option value="">– Standardkamera –</option>
    </select>
    <div class="settingInfo">Wird nach Kamerastart befüllt</div>
  </div>
  <div class="settingRow">
    <div class="settingInfo">App-Version: 2.0.0 | Artikel in DB: <span id="dbCount"></span></div>
  </div>

  <button id="dangerClearBtn" onclick="confirmClear()">🗑️ Liste komplett löschen</button>
  <button id="closeSettingsBtn" onclick="closeSettings()">Schließen ✕</button>
</div>
</div>


<script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.6.0/jspdf.plugin.autotable.min.js"></script>

<script>
// ===== ARTIKEL DATENBANK =====
const ARTICLES_DB = ARTICLES_PLACEHOLDER;

const BARCODE_MAP = {};
const NUMBER_MAP  = {};
ARTICLES_DB.forEach(a => {
  if(a.barcode) BARCODE_MAP[String(a.barcode).trim()] = a;
  if(a.number)  NUMBER_MAP[String(a.number).trim()]   = a;
});

// ===== HILFSFUNKTIONEN =====
function hatBuchstaben(str){
  return str && (str.match(/[a-zA-Z\u00c0-\u024f]/g)||[]).length >= 3;
}
function getDisplayName(a){
  if(hatBuchstaben(a.bez1)) return a.bez1;
  if(hatBuchstaben(a.bez2)) return a.bez2;
  return a.description || a.barcode || a.number || '';
}
function esc(s){
  return String(s||'')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}
function fmtQty(item){
  const q = parseFloat(item.qty) || 1;
  return item.perMeter ? q.toFixed(1).replace('.',',') + '\u00a0m' : String(Math.round(q)) + '\u00a0Stk';
}
function fmtPrice(price, perMeter){
  if(!price) return '';
  const p = parseFloat(price);
  if(isNaN(p)||p<=0) return '';
  return '\u20ac\u00a0' + p.toFixed(2).replace('.',',') + (perMeter ? '/m' : '/Stk');
}
function fmtTotal(item){
  if(!item.vkPreis) return '';
  const p = parseFloat(item.vkPreis);
  const q = parseFloat(item.qty) || 1;
  if(isNaN(p)||p<=0) return '';
  return '\u20ac\u00a0' + (p*q).toFixed(2).replace('.',',');
}

// ===== SETTINGS =====
const DEFAULTS = { firma:'DEXIS', email:'office@kfz-dorn.at', emailCC:'', mode:'auto' };
function getSetting(k){ return localStorage.getItem('dexis_s_'+k) ?? DEFAULTS[k] ?? ''; }
function saveSetting(k,v){ localStorage.setItem('dexis_s_'+k, v); }
function loadSettings(){
  document.getElementById('setFirma').value   = getSetting('firma');
  document.getElementById('setEmail').value   = getSetting('email');
  document.getElementById('setEmailCC').value = getSetting('emailCC');
  document.getElementById('setMode').value    = getSetting('mode');
  document.getElementById('dbCount').textContent = ARTICLES_DB.length;
}

// ===== STATE =====
let scannedItems = [];

function loadItems(){
  try{ scannedItems = JSON.parse(localStorage.getItem('dexis_items') || '[]'); }
  catch{ scannedItems = []; }
}
function saveItems(){
  try{ localStorage.setItem('dexis_items', JSON.stringify(scannedItems)); }
  catch{ showToast('Speicher voll \u2013 bitte Liste leeren!','error'); }
}
function loadCustomer(){
  document.getElementById('custName').value = localStorage.getItem('dexis_custName') || '';
  document.getElementById('custAddr').value = localStorage.getItem('dexis_custAddr') || '';
}
function saveCustomer(){
  localStorage.setItem('dexis_custName', document.getElementById('custName').value);
  localStorage.setItem('dexis_custAddr', document.getElementById('custAddr').value);
}

// ===== SCAN-BUTTON LOGIK =====
const SCAN_COOLDOWN_SEC = 10;
let scanEnabled      = false;
let cooldownTimer    = null;
let countdownInterval= null;

async function onScanBtnClick(){
  if(getCurrentMode() === 'usb'){ enableScan(); return; }
  if(!cameraActive){ await startCamera(); }
  if(!scanEnabled) enableScan();
}

function enableScan(){
  scanEnabled = true;
  const btn = document.getElementById('scanBtn');
  const cd  = document.getElementById('scanCountdown');
  btn.className = 'ready';
  btn.childNodes[0].textContent = '\ud83d\udcf7 BEREIT \u2013 jetzt scannen! ';
  cd.textContent = '';
  setStatus('Jetzt Barcode scannen!');
  clearTimeout(cooldownTimer);
  clearInterval(countdownInterval);
  let sec = SCAN_COOLDOWN_SEC;
  countdownInterval = setInterval(() => {
    sec--;
    cd.textContent = '(' + sec + 's)';
    if(sec <= 0){ clearInterval(countdownInterval); disableScan(); }
  }, 1000);
}

function disableScan(){
  scanEnabled = false;
  clearInterval(countdownInterval);
  clearTimeout(cooldownTimer);
  const btn = document.getElementById('scanBtn');
  const cd  = document.getElementById('scanCountdown');
  btn.className = 'waiting';
  btn.childNodes[0].textContent = '\ud83d\udcf7 SCANNEN ';
  cd.textContent = '';
  setStatus('SCANNEN dr\u00fccken um n\u00e4chsten Artikel zu scannen.');
}

function afterScan(){ disableScan(); }

// ===== ARTIKEL HINZUFUEGEN =====
function buildItem(article, code){
  return {
    barcode:     code || article.barcode || article.number,
    number:      article.number,
    bez1:        article.bez1        || '',
    bez2:        article.bez2        || '',
    description: article.description || '',
    orderQty:    article.orderQty    || '',
    vkPreis:     article.vkPreis     || '',
    perMeter:    article.perMeter    || false,
    qty:         1,
    ts:          new Date().toLocaleTimeString('de-AT'),
    unknown:     false
  };
}

function addBarcode(raw){
  const code = String(raw).trim();
  if(!code) return;
  if(!scanEnabled) return;

  let article = BARCODE_MAP[code] || NUMBER_MAP[code] || null;
  const existing = scannedItems.find(i =>
    i.barcode === code || (article && i.number === article.number));

  if(existing){
    if(!existing.perMeter){
      existing.qty = (existing.qty || 1) + 1;
      saveItems(); renderList();
      showToast('Menge +1: ' + (article ? article.number : code), 'success');
    } else {
      showToast('Bereits in der Liste \u2013 Meter anpassen!', 'warn');
    }
    vibrate([50,30,50]);
    flashCard(existing.barcode);
    afterScan();
    return;
  }

  const item = article
    ? buildItem(article, code)
    : { barcode:code, number:code, bez1:'Unbekannter Artikel', bez2:'',
        description:'Unbekannt', orderQty:'', vkPreis:'', perMeter:false,
        qty:1, ts:new Date().toLocaleTimeString('de-AT'), unknown:true };

  scannedItems.unshift(item);
  saveItems(); renderList();

  if(!article){ showToast('Unbekannt: ' + code + ' \u2013 hinzugef\u00fcgt','warn'); vibrate([100,50,100]); }
  else        { showToast('OK: ' + article.number, 'success'); vibrate([50]); }
  afterScan();
}

function addArticleFromSearch(number){
  const article = NUMBER_MAP[number] || BARCODE_MAP[number];
  if(!article){ showToast('Artikel nicht gefunden','error'); return; }

  const existing = scannedItems.find(i => i.number === article.number);
  if(existing){
    if(!existing.perMeter){
      existing.qty = (existing.qty || 1) + 1;
      saveItems(); renderList();
      showToast('Menge +1: ' + article.number, 'success');
      flashCard(existing.barcode);
    } else {
      showToast('Bereits in der Liste \u2013 Meter anpassen!', 'warn');
      flashCard(existing.barcode);
    }
  } else {
    const item = buildItem(article, article.barcode || number);
    scannedItems.unshift(item);
    saveItems(); renderList();
    showToast('Hinzugef\u00fcgt: ' + article.number, 'success');
    vibrate([50]);
  }
  // Suche leeren
  document.getElementById('searchInput').value = '';
  document.getElementById('searchResults').style.display = 'none';
  document.getElementById('searchResults').innerHTML = '';
}

function removeItem(barcode){
  scannedItems = scannedItems.filter(i => i.barcode !== barcode);
  saveItems(); renderList();
}

function changeQty(barcode, delta){
  const item = scannedItems.find(i => i.barcode === barcode);
  if(!item || item.perMeter) return;
  item.qty = Math.max(1, (item.qty || 1) + delta);
  saveItems(); renderList();
}

function setMeter(barcode, val){
  const item = scannedItems.find(i => i.barcode === barcode);
  if(!item) return;
  const v = parseFloat(String(val).replace(',','.'));
  if(!isNaN(v) && v > 0){
    item.qty = Math.round(v * 10) / 10;
    saveItems(); renderTotal();
  }
}

function flashCard(barcode){
  const el = document.querySelector('[data-barcode="' + CSS.escape(barcode) + '"]');
  if(el){ el.classList.remove('new-flash'); void el.offsetWidth; el.classList.add('new-flash'); }
}

// ===== RENDER =====
function renderList(){
  const list  = document.getElementById('articleList');
  const empty = document.getElementById('emptyHint');
  const count = document.getElementById('articleCount');

  if(!scannedItems.length){
    empty.style.display  = 'block';
    list.innerHTML       = '';
    count.textContent    = '';
    renderTotal();
    return;
  }
  empty.style.display = 'none';

  // Zaehler
  const stk   = scannedItems.filter(i => !i.perMeter).reduce((s,i) => s + (Math.round(i.qty)||1), 0);
  const meter = scannedItems.filter(i =>  i.perMeter).reduce((s,i) => s + (parseFloat(i.qty)||1), 0);
  let cStr = scannedItems.length + ' Artikel';
  if(stk   > 0) cStr += ' | ' + stk + ' Stk';
  if(meter > 0) cStr += ' | ' + meter.toFixed(1).replace('.',',') + ' m';
  count.textContent = cStr;

  list.innerHTML = scannedItems.map(item => {
    const name  = getDisplayName(item);
    const price = fmtPrice(item.vkPreis, item.perMeter);
    const total = fmtTotal(item);

    let qtyHtml;
    if(item.perMeter){
      qtyHtml = `<div class="meterWrap">
        <input type="number" class="meterInput"
               value="${(parseFloat(item.qty)||1).toFixed(1)}"
               min="0.1" step="0.1"
               onchange="setMeter('${esc(item.barcode)}',this.value)"
               onclick="this.select()">
        <span class="meterUnit">m</span>
      </div>`;
    } else {
      qtyHtml = `<div class="qtyBadge">
        <button class="qtyMinus" onclick="changeQty('${esc(item.barcode)}',-1)">&minus;</button>
        <span class="qtyNum">${Math.round(item.qty)||1}</span>
        <button class="qtyPlus"  onclick="changeQty('${esc(item.barcode)}',+1)">+</button>
      </div>`;
    }

    return `<div class="articleCard ${item.unknown?'unknown':''}" data-barcode="${esc(item.barcode)}">
      <div class="cardStripe"></div>
      <div class="cardBody">
        <div class="cardNum">${esc(item.number)}${item.unknown?' <span class="unknownBadge">\u26a0 Unbekannt</span>':''}</div>
        <div class="cardName" title="${esc(name)}">${esc(name)}</div>
        <div class="cardBC">Barcode: ${esc(item.barcode)}</div>
        ${price ? `<div class="cardPrice">VK: ${esc(price)}${total?' &nbsp;|&nbsp; \u03a3 '+esc(total):''}` + `</div>` : ''}
      </div>
      <div class="cardRight">
        ${qtyHtml}
        <button class="deleteBtn" onclick="removeItem('${esc(item.barcode)}')" title="L\u00f6schen">\ud83d\uddd1</button>
      </div>
    </div>`;
  }).join('');

  renderTotal();
}

function renderTotal(){
  const bar = document.getElementById('totalBar');
  const amt = document.getElementById('totalAmt');
  const hasPrices = scannedItems.some(i => i.vkPreis && parseFloat(i.vkPreis) > 0);
  if(!hasPrices || !scannedItems.length){ bar.style.display = 'none'; return; }
  let total = 0;
  scannedItems.forEach(i => {
    const p = parseFloat(i.vkPreis) || 0;
    const q = parseFloat(i.qty)     || 1;
    total  += p * q;
  });
  bar.style.display = 'flex';
  amt.textContent   = '\u20ac\u00a0' + total.toFixed(2).replace('.',',');
}

// ===== SUCHE =====
let searchTimeout = null;

function onSearchInput(){
  const q = document.getElementById('searchInput').value.trim();
  clearTimeout(searchTimeout);
  const sr = document.getElementById('searchResults');
  if(q.length < 2){ sr.style.display='none'; sr.innerHTML=''; return; }
  searchTimeout = setTimeout(() => renderSearchResults(q), 120);
}

function smartMatch(article, query){
  const words   = query.toLowerCase().replace(/[,\-]/g,' ').split(/\s+/).filter(Boolean);
  const haystack = [
    article.number      || '',
    article.bez1        || '',
    article.bez2        || '',
    article.description || ''
  ].join(' ').toLowerCase();
  return words.every(w => haystack.includes(w));
}

function renderSearchResults(query){
  const results = ARTICLES_DB.filter(a => smartMatch(a, query)).slice(0, 30);
  const sr = document.getElementById('searchResults');

  if(!results.length){
    sr.innerHTML = '<div class="srNoResult">Kein Artikel gefunden.</div>';
    sr.style.display = 'block';
    return;
  }

  sr.innerHTML = results.map(a => {
    const name  = getDisplayName(a);
    const price = fmtPrice(a.vkPreis, a.perMeter);
    return `<div class="srItem" onclick="addArticleFromSearch('${esc(a.number)}')">
      <div class="srLeft">
        <div class="srNum">${esc(a.number)}</div>
        <div class="srName">${esc(name)}</div>
      </div>
      <div class="srRight">
        ${price ? `<div class="srPrice">${esc(price)}</div>` : ''}
        ${a.perMeter ? '<div class="srMeter">\ud83d\udccf pro Meter</div>' : ''}
      </div>
    </div>`;
  }).join('');
  sr.style.display = 'block';
}

// ===== SPRACHSUCHE =====
let voiceRecognition = null;
let voiceActive      = false;

function toggleVoice(){
  if(voiceActive) stopVoice();
  else            startVoice();
}

function startVoice(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){
    showToast('Sprachsuche nicht unterst\u00fctzt (Chrome / Edge empfohlen)', 'warn');
    return;
  }
  voiceRecognition = new SR();
  voiceRecognition.lang            = 'de-DE';
  voiceRecognition.continuous      = false;
  voiceRecognition.interimResults  = true;
  voiceRecognition.maxAlternatives = 1;

  voiceRecognition.onstart = () => {
    voiceActive = true;
    const btn = document.getElementById('micBtn');
    btn.classList.add('active');
    btn.textContent = '\ud83d\udd34';
    showToast('Sprechen Sie jetzt\u2026', '');
  };
  voiceRecognition.onresult = e => {
    const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
    document.getElementById('searchInput').value = transcript;
    onSearchInput();
  };
  voiceRecognition.onerror = e => {
    stopVoice();
    if(e.error !== 'no-speech') showToast('Spracherkennung: ' + e.error, 'warn');
  };
  voiceRecognition.onend = () => stopVoice();
  try{ voiceRecognition.start(); }
  catch(err){ showToast('Sprachfehler: ' + err.message, 'error'); stopVoice(); }
}

function stopVoice(){
  voiceActive = false;
  const btn = document.getElementById('micBtn');
  btn.classList.remove('active');
  btn.textContent = '\ud83c\udf99\ufe0f';
  if(voiceRecognition){ try{ voiceRecognition.stop(); }catch(e){} voiceRecognition = null; }
}

// ===== SCAN INPUT =====
document.getElementById('scanInput').addEventListener('keydown', function(e){
  if(e.key === 'Enter'){
    const val = this.value.trim();
    if(val){ scanEnabled = true; addBarcode(val); }
    this.value = '';
    e.preventDefault();
  }
});

// USB-Scanner Autodetect (schnelle Eingabe + Enter)
document.addEventListener('keydown', function(e){
  const tag = document.activeElement.tagName;
  if(tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
  if(e.key === 'Enter'){
    if(usbBuffer.length > 2){ addBarcode(usbBuffer); usbBuffer = ''; }
    return;
  }
  if(e.key.length === 1){
    if(usbTimer) clearTimeout(usbTimer);
    usbBuffer += e.key;
    usbTimer = setTimeout(() => { usbBuffer = ''; }, 300);
  }
});
let usbBuffer = '';
let usbTimer  = null;

function clearScanInput(){
  document.getElementById('scanInput').value = '';
  document.getElementById('scanInput').focus();
}

// Refocus (USB-Modus)
document.addEventListener('click', function(e){
  const si = document.getElementById('scanInput');
  if(getCurrentMode() === 'usb' || getCurrentMode() === 'auto'){
    if(!e.target.closest('button') && !e.target.closest('input') &&
       !e.target.closest('textarea') && !e.target.closest('select')){
      si.focus();
    }
  }
});

// ===== SCANNER MODUS =====
let codeReader     = null;
let cameraActive   = false;
let currentDeviceId= null;
let allDevices     = [];

function getCurrentMode(){ return getSetting('mode'); }

function setMode(m){
  saveSetting('mode',m);
  document.getElementById('setMode').value = m;
  applyMode(m);
  ['auto','camera','usb'].forEach(x =>
    document.getElementById('btnMode'+x.charAt(0).toUpperCase()+x.slice(1))
    .classList.toggle('active', x===m)
  );
}

async function applyMode(m){
  const cc = document.getElementById('cameraContainer');
  const si = document.getElementById('scanInput');
  const sw = document.getElementById('switchCameraBtn');

  if(m === 'camera'){
    await startCamera();
  } else if(m === 'usb'){
    stopCamera();
    cc.style.display = 'none'; sw.style.display = 'none';
    si.placeholder = 'USB-Scanner: Barcode hier einscannen...';
    si.focus();
    setStatus('USB-Tastatur-Modus aktiv. Ins Feld scannen.');
  } else {
    setStatus('Automatische Erkennung \u2013 versuche Kamera\u2026');
    try{ await startCamera(); }
    catch(err){
      setStatus('Kamera nicht verf\u00fcgbar \u2013 USB-Modus aktiv.');
      si.placeholder = 'USB-Scanner: Barcode hier einscannen...';
      si.focus();
    }
  }
}

// ===== KAMERA =====
let html5Scanner = null;
const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);

async function startCamera(){
  const cc = document.getElementById('cameraContainer');
  const sw = document.getElementById('switchCameraBtn');
  try{
    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)
      throw new Error('NO_HTTPS');

    await stopCamera();
    setStatus('Kamera startet\u2026');
    cc.style.display = 'block';

    html5Scanner = new Html5Qrcode('videoEl', { verbose: false });
    const config = { fps:10, qrbox:{ width:240, height:140 } };

    let cameraConfig;
    if(isIOS){
      cameraConfig = { facingMode: 'environment' };
    } else {
      let cameras = [];
      try{ cameras = await Html5Qrcode.getCameras(); }catch(e){}
      allDevices = cameras;
      populateCameraSelect(cameras);
      if(cameras.length > 1) sw.style.display = 'block';
      let camId = localStorage.getItem('dexis_cameraId') || null;
      if(!camId && cameras.length){
        const back = cameras.find(c => /back|rear|environment/i.test(c.label));
        camId = back ? back.id : cameras[cameras.length-1].id;
      }
      currentDeviceId = camId;
      cameraConfig = camId
        ? { deviceId:{ exact:camId } }
        : { facingMode:{ ideal:'environment' } };
    }

    await html5Scanner.start(cameraConfig, config,
      decodedText => { if(scanEnabled){ addBarcode(decodedText); vibrateCamera(); } },
      null
    );
    cameraActive = true;

    if(isIOS){
      try{
        const cameras = await Html5Qrcode.getCameras();
        allDevices = cameras;
        populateCameraSelect(cameras);
        if(cameras.length > 1) sw.style.display = 'block';
      }catch(e){}
    }
    setStatus('Kamera aktiv \u2013 SCANNEN dr\u00fccken.');
    document.getElementById('scanInput').placeholder = 'Oder Barcode manuell eingeben...';

  }catch(err){
    cameraActive = false;
    cc.style.display = 'none'; sw.style.display = 'none';
    const msg  = String(err.message || err);
    const isCriOS = navigator.userAgent.includes('CriOS');
    if(/denied|notallowed|permission/i.test(msg)){
      if(isIOS){
        const browser = isCriOS ? 'Chrome' : 'Safari';
        setStatus('Kamera gesperrt! Einstellungen \u2192 ' + browser +
          ' \u2192 Kamera \u2192 Zulassen \u2192 Seite neu laden.' +
          (isCriOS ? ' (erfordert iOS 16.4+)' : ''));
      } else {
        setStatus('Kamera gesperrt! Adressleiste \u2192 Schloss \u2192 Kamera \u2192 Zulassen \u2192 neu laden.');
      }
      showToast('Kamera-Erlaubnis fehlt!', 'error');
    } else if(/no_https/i.test(msg)){
      setStatus('HTTPS fehlt \u2013 bitte https://ferdl1000.github.io/dexis-scanner verwenden.');
      showToast('Kein HTTPS \u2013 Kamera nicht verf\u00fcgbar', 'warn');
    } else {
      setStatus('Kamera: ' + msg.slice(0,90));
      showToast('Kamera-Fehler \u2013 manuelle Eingabe m\u00f6glich', 'warn');
    }
    document.getElementById('scanInput').placeholder = 'Barcode manuell eingeben...';
    throw err;
  }
}

async function stopCamera(){
  if(html5Scanner){
    try{ await html5Scanner.stop(); }catch(e){}
    try{ html5Scanner.clear(); }catch(e){}
    html5Scanner = null;
  }
  cameraActive = false;
}

async function switchCamera(){
  if(!allDevices.length) return;
  const idx  = allDevices.findIndex(d => d.id === currentDeviceId);
  const next = allDevices[(idx + 1) % allDevices.length];
  currentDeviceId = next.id;
  localStorage.setItem('dexis_cameraId', currentDeviceId);
  await stopCamera(); await startCamera();
  showToast('Kamera gewechselt: ' + (next.label || next.id.slice(0,8)));
}

async function changeCamera(deviceId){
  if(!deviceId) return;
  localStorage.setItem('dexis_cameraId', deviceId);
  if(cameraActive){ await stopCamera(); await startCamera(); }
}

function populateCameraSelect(cameras){
  const sel = document.getElementById('setCameraSelect');
  sel.innerHTML = '<option value="">– Standardkamera –</option>';
  cameras.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.label || ('Kamera ' + c.id.slice(0,8));
    if(c.id === currentDeviceId) opt.selected = true;
    sel.appendChild(opt);
  });
}

function setStatus(msg){ document.getElementById('scanStatus').textContent = msg; }
function vibrateCamera(){ vibrate([60]); }
function vibrate(pattern){ try{ if(navigator.vibrate) navigator.vibrate(pattern); }catch{} }

// ===== TOAST =====
function showToast(msg, type=''){
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.style.opacity='0', 2700);
  setTimeout(() => t.remove(), 3000);
}

// ===== FERTIG (PDF + EMAIL) =====
async function onFertig(){
  const name = document.getElementById('custName').value.trim();
  const addr = document.getElementById('custAddr').value.trim();

  if(!scannedItems.length){
    showToast('Bitte zuerst Artikel scannen!', 'error');
    return;
  }
  if(!name){
    showToast('Kundenname ist Pflichtfeld!', 'error');
    document.getElementById('custName').classList.add('error');
    document.getElementById('custName').focus();
    return;
  }
  document.getElementById('custName').classList.remove('error');

  const firma       = getSetting('firma') || 'DEXIS';
  const now         = new Date();
  const dateStr     = now.toLocaleDateString('de-AT');
  const timeStr     = now.toLocaleTimeString('de-AT',{hour:'2-digit',minute:'2-digit'});
  const fileDateStr = now.toISOString().slice(0,10).replace(/-/g,'');

  // Gesamtbetrag berechnen
  const hasPrices = scannedItems.some(i => i.vkPreis && parseFloat(i.vkPreis) > 0);
  let grandTotal  = 0;
  if(hasPrices){
    scannedItems.forEach(i => {
      grandTotal += (parseFloat(i.vkPreis)||0) * (parseFloat(i.qty)||1);
    });
  }

  // --- PDF ---
  try{
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({orientation:'portrait',unit:'mm',format:'a4'});

    // Header
    doc.setFillColor(26,35,126);
    doc.rect(0,0,210,28,'F');
    doc.setTextColor(255,255,255);
    doc.setFontSize(20); doc.setFont(undefined,'bold');
    doc.text(firma + ' \u2013 Gescannte Teile', 14, 12);
    doc.setFontSize(11); doc.setFont(undefined,'normal');
    doc.text('Erstellt: ' + dateStr + ' ' + timeStr, 14, 22);

    // Kundendaten
    doc.setTextColor(26,35,126);
    doc.setFontSize(13); doc.setFont(undefined,'bold');
    doc.text('Kundendaten', 14, 38);
    doc.setTextColor(30,30,30); doc.setFont(undefined,'normal'); doc.setFontSize(11);
    doc.text('Name: ' + name, 14, 46);
    if(addr) doc.text('Adresse: ' + addr, 14, 53);

    const startY = addr ? 60 : 55;

    // Tabelleninhalt
    const head = hasPrices
      ? [['#','Art.Nr.','Bezeichnung','Menge','VK-Preis','Gesamt']]
      : [['#','Art.Nr.','Bezeichnung 1','Bezeichnung 2','Barcode','Stk']];

    const tableData = scannedItems.map((item, i) => {
      if(hasPrices){
        const name2 = getDisplayName(item);
        const menge = fmtQty(item);
        const vk    = item.vkPreis ? '\u20ac ' + parseFloat(item.vkPreis).toFixed(2).replace('.',',') : '';
        const ges   = (item.vkPreis && parseFloat(item.vkPreis)>0)
          ? '\u20ac ' + ((parseFloat(item.vkPreis)||0)*(parseFloat(item.qty)||1)).toFixed(2).replace('.',',')
          : '';
        return [String(i+1), item.number, name2, menge, vk, ges];
      } else {
        return [String(i+1), item.number, item.bez1||item.description, item.bez2||'', item.barcode, String(Math.round(item.qty)||1)];
      }
    });

    if(hasPrices){
      doc.autoTable({
        startY,
        head, body: tableData,
        headStyles:{fillColor:[26,35,126], textColor:255, fontStyle:'bold', fontSize:10},
        bodyStyles:{fontSize:9},
        columnStyles:{
          0:{cellWidth:7,  halign:'center'},
          1:{cellWidth:22},
          2:{cellWidth:66},
          3:{cellWidth:18, halign:'center'},
          4:{cellWidth:22, halign:'right'},
          5:{cellWidth:25, halign:'right', fontStyle:'bold'}
        },
        alternateRowStyles:{fillColor:[240,243,255]},
        styles:{overflow:'linebreak'},
        margin:{left:10,right:10}
      });

      // Gesamtzeile
      const lastY = doc.lastAutoTable.finalY + 6;
      doc.setFontSize(12); doc.setFont(undefined,'bold'); doc.setTextColor(26,35,126);
      doc.text('Gesamtbetrag exkl. MwSt.:', 14, lastY);
      doc.text('\u20ac ' + grandTotal.toFixed(2).replace('.',','), 190, lastY, {align:'right'});
      doc.setDrawColor(26,35,126);
      doc.setLineWidth(0.5);
      doc.line(14, lastY+2, 196, lastY+2);
    } else {
      doc.autoTable({
        startY,
        head, body: tableData,
        headStyles:{fillColor:[26,35,126], textColor:255, fontStyle:'bold', fontSize:10},
        bodyStyles:{fontSize:9},
        columnStyles:{
          0:{cellWidth:8,  halign:'center'},
          1:{cellWidth:24},
          2:{cellWidth:55},
          3:{cellWidth:45},
          4:{cellWidth:28, font:'courier', fontSize:8},
          5:{cellWidth:12, halign:'center'}
        },
        alternateRowStyles:{fillColor:[240,243,255]},
        styles:{overflow:'linebreak'},
        margin:{left:10,right:10}
      });
    }

    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for(let p=1;p<=pageCount;p++){
      doc.setPage(p);
      doc.setTextColor(150); doc.setFontSize(9); doc.setFont(undefined,'normal');
      doc.text(firma + ' | Seite ' + p + '/' + pageCount, 14, 290);
    }

    const safeName = name.replace(/[^a-zA-Z0-9\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc]/g,'_');
    doc.save(firma + '_' + safeName + '_' + fileDateStr + '.pdf');
    showToast('PDF gespeichert!', 'success');
  } catch(e){
    showToast('PDF-Fehler: ' + e.message, 'error');
    console.error(e);
  }

  // --- E-Mail ---
  try{
    const to  = getSetting('email');
    const cc  = getSetting('emailCC');
    const sub = encodeURIComponent(firma + ' \u2013 Gescannte Teile von ' + name);
    let body  = firma + ' - Gescannte Teile\n';
    body += 'Datum: ' + dateStr + ' ' + timeStr + '\n\n';
    body += 'Kundenname: ' + name + '\n';
    if(addr) body += 'Adresse: ' + addr + '\n';
    const trenn = '--------------------------------------------\n';
    body += '\nGescannte Artikel:\n';
    body += trenn;

    scannedItems.forEach((item, i) => {
      const bez   = (item.bez1 && item.bez1.trim()) || '';
      const det   = (item.bez2 && item.bez2.trim()) || '';
      const menge = fmtQty(item);
      const vk    = item.vkPreis && parseFloat(item.vkPreis)>0
        ? '\u20ac ' + parseFloat(item.vkPreis).toFixed(2).replace('.',',') + (item.perMeter ? '/m' : '/Stk')
        : '';
      const ges   = item.vkPreis && parseFloat(item.vkPreis)>0
        ? '\u20ac ' + ((parseFloat(item.vkPreis)||0)*(parseFloat(item.qty)||1)).toFixed(2).replace('.',',')
        : '';

      body += (i+1) + ') Art.Nr.: ' + item.number + '    Menge: ' + menge + '\n';
      if(bez) body += '   Bezeichnung:  ' + bez + '\n';
      if(det) body += '   Details:      ' + det + '\n';
      if(vk)  body += '   VK-Preis:     ' + vk  + '\n';
      if(ges) body += '   Zeilensumme:  ' + ges + '\n';
      body += '   Barcode:      ' + item.barcode + '\n\n';
    });

    body += trenn;
    if(hasPrices){
      body += 'Gesamtbetrag exkl. MwSt.: \u20ac ' + grandTotal.toFixed(2).replace('.',',') + '\n';
      body += trenn;
    }
    body += 'Gesamt: ' + scannedItems.reduce((s,i) => s + (Math.round(parseFloat(i.qty))||1), 0) + ' Einheiten';

    let mailto = 'mailto:' + to + '?subject=' + sub + '&body=' + encodeURIComponent(body);
    if(cc) mailto += '&cc=' + encodeURIComponent(cc);
    setTimeout(() => { window.location.href = mailto; }, 500);
  } catch(e){
    showToast('E-Mail konnte nicht ge\u00f6ffnet werden.', 'warn');
  }

  // Reset
  setTimeout(() => {
    scannedItems = [];
    saveItems();
    document.getElementById('custName').value = '';
    document.getElementById('custAddr').value = '';
    localStorage.removeItem('dexis_custName');
    localStorage.removeItem('dexis_custAddr');
    renderList();
    showToast('Bereit f\u00fcr den n\u00e4chsten Auftrag.', 'success');
  }, 1500);
}

// ===== SETTINGS MODAL =====
function openSettings(){
  loadSettings();
  document.getElementById('settingsOverlay').classList.add('open');
}
function closeSettings(){
  document.getElementById('settingsOverlay').classList.remove('open');
}
function overlayClick(e, id){
  if(e.target.id === id) document.getElementById(id).classList.remove('open');
}
function confirmClear(){
  if(confirm('Wirklich alle gescannten Artikel l\u00f6schen?')){
    scannedItems = [];
    saveItems(); renderList();
    closeSettings();
    showToast('Liste geleert.', 'warn');
  }
}

// ===== SCROLL FAB =====
window.addEventListener('scroll', () => {
  document.getElementById('fabScroll').style.display = window.scrollY > 200 ? 'block' : 'none';
});

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
  loadItems();
  loadSettings();
  loadCustomer();
  renderList();

  const m = getCurrentMode();
  ['auto','camera','usb'].forEach(x =>
    document.getElementById('btnMode'+x.charAt(0).toUpperCase()+x.slice(1))
    .classList.toggle('active', x===m)
  );

  if(m === 'usb'){
    await applyMode('usb');
  } else if(isIOS){
    saveSetting('mode','auto');
    document.getElementById('setMode').value = 'auto';
    setStatus('SCANNEN dr\u00fccken um Kamera zu starten.');
  } else {
    await applyMode(m);
  }

  document.getElementById('scanInput').focus();
});
</script>
</body>
</html>
"""

HTML = HTML.replace("ARTICLES_PLACEHOLDER", compact_json)

with open("scanner-app.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"scanner-app.html erstellt ({len(HTML)//1024} KB)")
