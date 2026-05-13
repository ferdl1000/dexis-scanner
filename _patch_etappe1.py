"""Etappe 1: Lagerbestand-UI in scanner-app.html einbauen."""
p = 'scanner-app.html'
t = open(p, encoding='utf-8').read()
orig = t

# 1) DEFAULTS erweitern
t = t.replace(
    "const DEFAULTS = {\n  firma:'Firma Dorn',\n  showPrices:'false',",
    "const DEFAULTS = {\n  firma:'Firma Dorn',\n  showPrices:'false',\n  showStock:'false',\n  orderEmail:'office@kfz-dorn.at',",
)

# 2) loadSettings: weitere Felder
t = t.replace(
    "  document.getElementById('setShowPrices').checked = (getSetting('showPrices') === 'true');",
    "  document.getElementById('setShowPrices').checked = (getSetting('showPrices') === 'true');\n"
    "  document.getElementById('setShowStock').checked  = (getSetting('showStock')  === 'true');\n"
    "  document.getElementById('setOrderEmail').value   = getSetting('orderEmail');"
)

# 3) Settings-Panel HTML: Toggle + Bestell-Mail
stock_settings = """
  <div class="settingRow">
    <div class="toggleRow">
      <label for="setShowStock">Lagerbestand anzeigen</label>
      <label class="toggleSwitch">
        <input type="checkbox" id="setShowStock" onchange="toggleStock(this)">
        <span class="toggleSlider"></span>
      </label>
    </div>
    <div class="settingInfo">Aus = niemand sieht Bestand. An = alle sehen, Admin kann editieren.</div>
  </div>
  <div class="settingRow">
    <label>Bestell-E-Mail (DEXIS / Lieferant)</label>
    <input type="email" id="setOrderEmail" placeholder="office@kfz-dorn.at"
           oninput="saveSetting('orderEmail',this.value)">
    <div class="settingInfo">An diese Adresse geht die Nachbestellung.</div>
  </div>
"""
t = t.replace(
    '<div class="settingRow">\n    <label>Firmenname (PDF-Kopfzeile)</label>',
    stock_settings + '\n  <div class="settingRow">\n    <label>Firmenname (PDF-Kopfzeile)</label>'
)

# 4) CSS
css_inject = """
/* Lagerbestand */
.stockRow{
  display:flex;align-items:center;gap:8px;margin-top:6px;
  padding:4px 8px;background:#e3f2fd;border-radius:8px;font-size:14px;
  flex-wrap:wrap;
}
.stockRow.low{background:#ffebee;color:#c62828;font-weight:600;}
.stockRow.warn{background:#fff8e1;color:#e65100;}
.stockRow.unknown{background:#f5f5f5;color:#888;font-style:italic;}
.stockRow .stockLabel{font-weight:600;}
.stockInput{
  width:54px;text-align:center;border:1px solid #bbb;border-radius:6px;
  padding:3px 4px;font-size:14px;background:#fff;
}
.stockInput:focus{outline:2px solid var(--primary);outline-offset:1px;}
.lowBadge{
  display:inline-block;background:#c62828;color:#fff;
  padding:2px 7px;border-radius:10px;font-size:11px;font-weight:700;
}
#orderSection{display:none;}
#orderSection.show{display:block;}
.orderItem{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 10px;border:1px solid #ffcdd2;background:#fff5f5;
  border-radius:8px;margin-bottom:6px;gap:8px;
}
.orderItem .oNum{font-weight:700;color:#c62828;}
.orderItem .oName{flex:1;margin:0 6px;font-size:14px;color:#444;}
.orderItem .oQty{font-size:13px;color:#666;white-space:nowrap;}
#orderBtn{
  width:100%;min-height:54px;font-size:18px;font-weight:700;
  background:#e65100;color:#fff;border:none;border-radius:12px;
  cursor:pointer;margin-top:10px;
  display:flex;align-items:center;justify-content:center;gap:8px;
}
#orderBtn:hover{background:#bf360c;}
"""
t = t.replace("/* FAB Scroll-to-top */", css_inject + "\n/* FAB Scroll-to-top */", 1)

# 5) HTML: Nachbestell-Section vor Kundendaten
order_section = """  <!-- NACHBESTELLEN -->
  <div class="section" id="orderSection">
    <h2><span class="icon">P</span> Nachzubestellen <span id="orderCount" style="font-size:14px;color:#666;font-weight:400;margin-left:8px;"></span></h2>
    <div id="orderList"></div>
    <button id="orderBtn" onclick="onBestellen()">
      Bestellung versenden
    </button>
  </div>

"""
# echte Emojis als Unicode reinschreiben
order_section = order_section.replace('<span class="icon">P</span>', '<span class="icon">' + '\U0001F4E6' + '</span>')
order_section = order_section.replace('Bestellung versenden', '\U0001F4E7 Bestellung versenden')

t = t.replace(
    "  <!-- KUNDENDATEN -->",
    order_section + "  <!-- KUNDENDATEN -->"
)

# 6) JS: Stock-Verwaltung
stock_js = """
// ===== LAGERBESTAND =====
let stockData = {};  // { artikelnummer: {s: stock, m: minStock} }

function loadStockLocal(){
  try{ stockData = JSON.parse(localStorage.getItem('dorn_stock') || '{}'); }
  catch{ stockData = {}; }
}
function saveStockLocal(){
  localStorage.setItem('dorn_stock', JSON.stringify(stockData));
}
function stockVisible(){
  return getSetting('showStock') === 'true';
}
function getStock(num){
  return stockData[num] || {};
}
function setStockValue(num, key, raw){
  const v = parseInt(String(raw).replace(/[^0-9-]/g,''), 10);
  if(!stockData[num]) stockData[num] = {};
  if(isNaN(v) || v < 0){ delete stockData[num][key]; }
  else { stockData[num][key] = v; }
  if(stockData[num].s === undefined && stockData[num].m === undefined){
    delete stockData[num];
  }
  saveStockLocal();
  renderOrderList();
  refreshStockRow(num);
}
function refreshStockRow(num){
  document.querySelectorAll('[data-stock-for="' + CSS.escape(num) + '"]').forEach(el => {
    el.outerHTML = buildStockRowHtml(num, el.dataset.context);
  });
}
function buildStockRowHtml(num, context){
  if(!stockVisible()) return '';
  const sd = getStock(num);
  const has = sd.s !== undefined;
  const hasMin = sd.m !== undefined;
  const low  = has && hasMin && sd.s <= sd.m;
  const warn = has && hasMin && !low && sd.s <= sd.m * 1.5;
  const cls  = low ? 'low' : (warn ? 'warn' : (has ? '' : 'unknown'));
  const editable = isAdminUnlocked();
  const lbl  = has ? sd.s : '–';
  const lblMin = hasMin ? sd.m : '–';
  const lowBadge = low ? '<span class="lowBadge">NACHBESTELLEN</span>' : '';

  if(editable){
    return '<div class="stockRow ' + cls + '" data-stock-for="' + esc(num) + '" data-context="' + (context||'') + '">' +
      '<span class="stockLabel">📦 Lager:</span>' +
      '<input type="number" class="stockInput" value="' + (has?sd.s:'') + '" min="0" placeholder="—" ' +
        'onchange="setStockValue(\\'' + esc(num) + '\\',\\'s\\',this.value)" onclick="this.select()">' +
      '<span class="stockLabel">Min:</span>' +
      '<input type="number" class="stockInput" value="' + (hasMin?sd.m:'') + '" min="0" placeholder="—" ' +
        'onchange="setStockValue(\\'' + esc(num) + '\\',\\'m\\',this.value)" onclick="this.select()">' +
      lowBadge +
      '</div>';
  } else {
    return '<div class="stockRow ' + cls + '" data-stock-for="' + esc(num) + '" data-context="' + (context||'') + '">' +
      '<span>📦 Lager: <b>' + lbl + '</b> / Min: ' + lblMin + '</span>' +
      lowBadge +
      '</div>';
  }
}
function toggleStock(checkbox){
  saveSetting('showStock', checkbox.checked ? 'true' : 'false');
  renderList();
  const sq = document.getElementById('searchInput').value.trim();
  if(sq.length >= 2) renderSearchResults(sq);
  renderOrderList();
}

// ===== NACHBESTELL-LISTE =====
function getLowStockArticles(){
  const out = [];
  for(const num in stockData){
    const sd = stockData[num];
    if(sd.s === undefined || sd.m === undefined) continue;
    if(sd.s <= sd.m){
      const art = NUMBER_MAP[num] || BARCODE_MAP[num];
      if(art){
        out.push({article: art, stock: sd.s, min: sd.m});
      }
    }
  }
  return out.sort(function(a,b){ return (a.stock - a.min) - (b.stock - b.min); });
}
function renderOrderList(){
  const sec  = document.getElementById('orderSection');
  const list = document.getElementById('orderList');
  const cnt  = document.getElementById('orderCount');
  if(!sec) return;
  if(!stockVisible()){ sec.classList.remove('show'); return; }
  const low = getLowStockArticles();
  if(!low.length){ sec.classList.remove('show'); return; }
  sec.classList.add('show');
  cnt.textContent = '(' + low.length + ' Artikel unter Mindestbestand)';
  list.innerHTML = low.map(function(l){
    return '<div class="orderItem">' +
      '<div class="oNum">' + esc(l.article.number) + '</div>' +
      '<div class="oName">' + esc(l.article.bez1 || l.article.description || '') + '</div>' +
      '<div class="oQty">Lager ' + l.stock + ' / Min ' + l.min + ' <b>(-' + (l.min - l.stock) + ')</b></div>' +
      '</div>';
  }).join('');
}
function onBestellen(){
  const low = getLowStockArticles();
  if(!low.length){ showToast('Keine Artikel unter Mindestbestand','warn'); return; }
  const to    = getSetting('orderEmail') || 'office@kfz-dorn.at';
  const firma = getSetting('firma') || 'Firma Dorn';
  const now   = new Date();
  const dateStr = now.toLocaleDateString('de-AT');
  const subj  = encodeURIComponent('Nachbestellung ' + firma + ' - ' + dateStr);
  let body = firma + ' - Nachbestellung\\n';
  body += 'Datum: ' + dateStr + '\\n\\n';
  body += 'Bitte folgende Artikel nachliefern:\\n';
  body += '----------------------------------------\\n';
  low.forEach(function(l, i){
    const fehlt = Math.max(1, l.min - l.stock);
    body += (i+1) + ') Art.Nr.: ' + l.article.number + '\\n';
    body += '   Bezeichnung: ' + (l.article.bez1 || l.article.description || '') + '\\n';
    body += '   Lagerbestand: ' + l.stock + '   Mindestbestand: ' + l.min + '\\n';
    body += '   Nachzubestellen: ' + fehlt + ' Stk\\n\\n';
  });
  body += '----------------------------------------\\n';
  body += 'Gesamt: ' + low.length + ' verschiedene Artikel\\n';
  window.location.href = 'mailto:' + to + '?subject=' + subj + '&body=' + encodeURIComponent(body);
}

// ===== INIT ====="""

t = t.replace("// ===== INIT =====", stock_js, 1)

# 7) INIT erweitern
t = t.replace(
    "  applyUrlPreiseFlag();\n  loadCachedDB();   // Offline-Cache laden bevor irgendwas anderes\n  loadItems();",
    "  applyUrlPreiseFlag();\n  loadCachedDB();   // Offline-Cache laden bevor irgendwas anderes\n  loadStockLocal();\n  loadItems();"
)
t = t.replace(
    "  renderList();\n  warnInAppBrowser();",
    "  renderList();\n  renderOrderList();\n  warnInAppBrowser();"
)

# 8) renderList: Stock-Zeile vor Preis-Zeile einbauen
t = t.replace(
    "${(price && pricesVisible()) ? `<div class=\"cardPrice\">VK: ${esc(price)}${total?",
    "${buildStockRowHtml(item.number, 'list')}\n        ${(price && pricesVisible()) ? `<div class=\"cardPrice\">VK: ${esc(price)}${total?"
)

# 9) renderSearchResults: Stock-Zeile auch
t = t.replace(
    "${(price && pricesVisible()) ? `<div class=\"srPrice\">${esc(price)}</div>` : ''}",
    "${(price && pricesVisible()) ? `<div class=\"srPrice\">${esc(price)}</div>` : ''}\n        ${stockVisible() ? buildStockRowHtml(a.number, 'search') : ''}"
)

# Save
open(p, 'w', encoding='utf-8').write(t)

# Sanity-Checks
checks = {
    'showStock default':          "showStock:'false'" in t,
    'orderEmail default':         "orderEmail:'office@kfz-dorn.at'" in t,
    'setShowStock loadSettings':  "document.getElementById('setShowStock').checked" in t,
    'Toggle in Settings':         'id="setShowStock"' in t,
    'orderEmail Input':           'id="setOrderEmail"' in t,
    'stockData Variable':         'let stockData = {}' in t,
    'loadStockLocal':             'function loadStockLocal()' in t,
    'buildStockRowHtml':          'function buildStockRowHtml(' in t,
    'getLowStockArticles':        'function getLowStockArticles()' in t,
    'onBestellen':                'function onBestellen()' in t,
    'orderSection HTML':          'id="orderSection"' in t,
    'orderBtn HTML':              'id="orderBtn"' in t,
    'Stock in renderList':        "buildStockRowHtml(item.number, 'list')" in t,
    'Stock in renderSearch':      "buildStockRowHtml(a.number, 'search')" in t,
    'INIT loadStockLocal':        '  loadStockLocal();' in t,
    'INIT renderOrderList':       'renderList();\n  renderOrderList();' in t,
    'CSS stockRow':               '.stockRow{' in t,
}
print()
for k,v in checks.items():
    print('  ' + ('OK' if v else 'FAIL') + '  -  ' + k)
print('\n' + ('GEAENDERT' if t != orig else 'UNVERAENDERT'))
