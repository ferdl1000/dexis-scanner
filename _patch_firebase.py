"""Etappe 3: Firebase Sync in scanner-app.html einbauen."""
p = 'scanner-app.html'
t = open(p, encoding='utf-8').read()
orig = t

# 1) Firebase SDKs vor </head> einfuegen (compat - kein build noetig)
fb_scripts = """
<!-- Firebase SDK (kein Build noetig - compat mode) -->
<script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-database-compat.js"></script>
"""
t = t.replace('</head>', fb_scripts + '</head>')

# 2) Firebase Config + Sync-Funktionen einfuegen (vor "// ===== LAGERBESTAND =====")
fb_init = """
// ===== FIREBASE (zentrale Bestand-Sync) =====
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyCOk3uRvSWvTXVN7ilI3iJ7Ls5Dh0UKK_E",
  authDomain: "dorn-teile-scanner.firebaseapp.com",
  databaseURL: "https://dorn-teile-scanner-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "dorn-teile-scanner",
  storageBucket: "dorn-teile-scanner.firebasestorage.app",
  messagingSenderId: "29269615974",
  appId: "1:29269615974:web:034cecc11e6064c0c714a7"
};
let fbApp = null, fbDb = null, fbConnected = false;
let fbStockRef = null, fbMetaRef = null;

function initFirebase(){
  try{
    if(typeof firebase === 'undefined'){
      console.warn('Firebase SDK nicht geladen');
      return false;
    }
    fbApp = firebase.initializeApp(FIREBASE_CONFIG);
    fbDb  = firebase.database();
    fbStockRef = fbDb.ref('stock');
    fbMetaRef  = fbDb.ref('meta');
    // Connection-Status
    fbDb.ref('.info/connected').on('value', s => {
      fbConnected = !!(s.val());
      updateSyncBadge();
    });
    // Realtime Listener: Bestandsdaten
    fbStockRef.on('value', snap => {
      const cloud = snap.val() || {};
      stockData = cloud;
      saveStockLocal();
      // UI aktualisieren
      try{ renderList(); renderOrderList(); }catch(e){}
      const sq = document.getElementById('searchInput');
      if(sq && sq.value.trim().length >= 2) renderSearchResults(sq.value.trim());
      updateSyncBadge();
    });
    return true;
  }catch(e){
    console.error('Firebase Init Fehler:', e);
    return false;
  }
}

function updateSyncBadge(){
  const b = document.getElementById('syncBadge');
  if(!b) return;
  if(!stockVisible()){ b.style.display = 'none'; return; }
  b.style.display = 'inline-block';
  if(fbConnected){
    b.textContent = '☁ live';
    b.className = 'syncBadge ok';
  } else {
    b.textContent = '⊘ offline';
    b.className = 'syncBadge off';
  }
}

// Schreiben in Firebase (atomar, nur wenn admin)
function fbSetStock(num, key, value){
  if(!fbStockRef) return Promise.resolve(false);
  const path = num.replace(/[.#$\\[\\]/]/g, '_');  // RTDB erlaubt diese Zeichen nicht in Keys
  const update = {};
  update[key] = value;
  update['ts'] = firebase.database.ServerValue.TIMESTAMP;
  return fbStockRef.child(path).update(update).catch(e => {
    console.error('fbSetStock Fehler:', e);
    showToast('Speichern fehlgeschlagen: ' + e.message, 'error');
  });
}
function fbRemoveStock(num){
  if(!fbStockRef) return Promise.resolve(false);
  const path = num.replace(/[.#$\\[\\]/]/g, '_');
  return fbStockRef.child(path).remove();
}

// Atomarer Abzug bei FERTIG-Klick (Transaktion)
function fbDecrement(num, qty){
  if(!fbStockRef || !qty || qty <= 0) return Promise.resolve();
  const path = num.replace(/[.#$\\[\\]/]/g, '_');
  return fbStockRef.child(path).child('s').transaction(cur => {
    if(cur === null || cur === undefined) return cur;  // kein Bestand definiert - nichts tun
    return Math.max(0, cur - qty);
  });
}

// Beim FERTIG-Klick: alle Mengen abziehen
async function processStockOnFertig(items){
  if(!fbStockRef) return;
  const tasks = items.map(it => fbDecrement(it.number, Math.round(parseFloat(it.qty)||1)));
  try{ await Promise.all(tasks); }catch(e){ console.error('Abzug-Fehler:', e); }
}

"""

t = t.replace('// ===== LAGERBESTAND =====', fb_init + '// ===== LAGERBESTAND =====', 1)

# 3) setStockValue erweitern: auch in Cloud schreiben
old_set = """function setStockValue(num, key, raw){
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
}"""
new_set = """function setStockValue(num, key, raw){
  const v = parseInt(String(raw).replace(/[^0-9-]/g,''), 10);
  if(!stockData[num]) stockData[num] = {};
  if(isNaN(v) || v < 0){
    delete stockData[num][key];
    // In Cloud: Feld entfernen
    if(fbStockRef){
      const path = num.replace(/[.#$\\[\\]/]/g, '_');
      fbStockRef.child(path).child(key).remove();
    }
  } else {
    stockData[num][key] = v;
    fbSetStock(num, key, v);  // -> Cloud
  }
  if(stockData[num].s === undefined && stockData[num].m === undefined){
    delete stockData[num];
    fbRemoveStock(num);
  }
  saveStockLocal();
  renderOrderList();
  refreshStockRow(num);
}"""
t = t.replace(old_set, new_set, 1)

# 4) Header: Sync-Badge neben Update-Badge
t = t.replace(
    '<h1>Dorn Teile Scanner <span id="updateBadge" title="Datenbank-Status"></span></h1>',
    '<h1>Dorn Teile Scanner <span id="updateBadge" title="Datenbank-Status"></span> <span id="syncBadge" title="Bestand-Sync" style="display:none;"></span></h1>'
)

# 5) CSS fuer syncBadge
sync_css = """
#syncBadge{
  font-size:11px;padding:3px 8px;border-radius:10px;margin-left:6px;
  font-weight:600;
}
#syncBadge.ok{background:#2e7d32;color:#fff;}
#syncBadge.off{background:#c62828;color:#fff;}
"""
t = t.replace('/* FAB Scroll-to-top */', sync_css + '\n/* FAB Scroll-to-top */', 1)

# 6) INIT: Firebase initialisieren + StockToggle ruft updateSyncBadge
t = t.replace(
    "  applyUrlPreiseFlag();\n  loadCachedDB();   // Offline-Cache laden bevor irgendwas anderes\n  loadStockLocal();\n  loadItems();",
    "  applyUrlPreiseFlag();\n  loadCachedDB();   // Offline-Cache laden bevor irgendwas anderes\n  loadStockLocal();\n  initFirebase();\n  loadItems();"
)

# 7) onFertig: am Anfang processStockOnFertig (vor PDF/Mail) - lassen nicht
# Eigentlich: nach erfolgreichem Versand. Wir machen das DIREKT am Anfang von onFertig
# damit es auch bei PDF-Fehler abzieht.
t = t.replace(
    "async function onFertig(){\n  const name = document.getElementById('custName').value.trim();",
    "async function onFertig(){\n  const name = document.getElementById('custName').value.trim();\n  // Lagerbestand-Abzug in Cloud\n  if(stockVisible() && scannedItems.length){ processStockOnFertig(scannedItems); }"
)

# 8) toggleStock soll auch updateSyncBadge aufrufen
t = t.replace(
    "function toggleStock(checkbox){\n  saveSetting('showStock', checkbox.checked ? 'true' : 'false');\n  renderList();\n  const sq = document.getElementById('searchInput').value.trim();\n  if(sq.length >= 2) renderSearchResults(sq);\n  renderOrderList();\n}",
    "function toggleStock(checkbox){\n  saveSetting('showStock', checkbox.checked ? 'true' : 'false');\n  renderList();\n  const sq = document.getElementById('searchInput').value.trim();\n  if(sq.length >= 2) renderSearchResults(sq);\n  renderOrderList();\n  updateSyncBadge();\n}"
)

open(p, 'w', encoding='utf-8').write(t)

# Sanity checks
checks = {
    'firebase-app-compat geladen':    'firebase-app-compat.js' in t,
    'FIREBASE_CONFIG':                'AIzaSyCOk3uRvSWvTXVN7ilI3iJ7Ls5Dh0UKK_E' in t,
    'initFirebase':                   'function initFirebase()' in t,
    'fbSetStock':                     'function fbSetStock(' in t,
    'fbDecrement':                    'function fbDecrement(' in t,
    'processStockOnFertig':           'function processStockOnFertig(' in t,
    'syncBadge HTML':                 'id="syncBadge"' in t,
    'syncBadge CSS':                  '#syncBadge.ok' in t,
    'INIT initFirebase':              '  initFirebase();' in t,
    'onFertig Abzug':                 'processStockOnFertig(scannedItems)' in t,
    'setStockValue Cloud':            'fbSetStock(num, key, v)' in t,
    'toggleStock updateSyncBadge':    'renderOrderList();\n  updateSyncBadge();' in t,
}
for k,v in checks.items():
    print('  ' + ('OK' if v else 'FAIL') + '  -  ' + k)
print('\n' + ('GEAENDERT' if t != orig else 'UNVERAENDERT'))
