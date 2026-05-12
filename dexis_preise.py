"""
dexis_preise.py
Loggt sich bei DEXIS Austria (shop.dexis.at) ein,
sucht alle Excel-Artikel ohne VK-Preis per Artikelnummer,
liest den EK-Preis aus, rechnet mit kategorie-basiertem Aufschlag den VK-Preis,
und schreibt alles in articles.json zurueck.
"""

import requests
import re
import json
import time
import os

ARTICLES_FILE = "articles.json"
EMAIL    = "office@kfz-dorn.at"
PASSWORD = "doRn1996"
BASE_URL = "https://shop.dexis.at"

# Kategorie-basierte Aufschlaege (Median aus Preislisten-Bildern)
AUFSCHLAG = {
    'HYLEITUNG':      0.250,   # 25%
    'HYDRAULIKLTG':   0.668,   # 67%
    'FKS_SCHLAUCH':   0.667,   # 67%
    'G4':             2.705,   # 270%
    'GE_GR_KOR':      2.171,   # 217%
    'EVL_EVW_EVT':    2.123,   # 212%
    'G_W_SV_D_T_BKH': 2.125,  # 213%
    'PF':             2.705,   # 270%
    'MC':             2.334,   # 233%
    'SKF_LAGER':      1.500,   # 150%
    'KEILRIEMEN':     1.262,   # 126%
    'STANDARD':       1.565,   # 156% Mittelwert als Fallback
}

def get_kategorie(number, bez1):
    n = str(number).upper()
    b = str(bez1).upper()
    combined = n + ' ' + b
    if 'HYLEITUNG' in combined: return 'HYLEITUNG'
    if 'HYDRAULIKLEITUNG' in combined: return 'HYDRAULIKLTG'
    if any(x in combined for x in ('FKS','KUEHLERSCHLAUCH','SAUGSCHLAUCH','SANDSTRAHL','TANKWAGEN','FKDS')): return 'FKS_SCHLAUCH'
    if n.startswith('G4') or 'G4 0' in n: return 'G4'
    if any(combined.startswith(x) for x in ('GE ','GR ','KOR ')): return 'GE_GR_KOR'
    if any(combined.startswith(x) for x in ('EVL','EVW','EVT')): return 'EVL_EVW_EVT'
    if any(combined.startswith(x) for x in ('G ','W ','SV ','D ','T ','BKH')): return 'G_W_SV_D_T_BKH'
    if n.startswith('PF') or 'PRESSFASSUNG' in b: return 'PF'
    if n.startswith('MC '): return 'MC'
    if any(x in combined for x in ('SKF','KUGELLAGER','RILLENKUGEL','2RSH','2RS1','WAELZLAGER')): return 'SKF_LAGER'
    if any(x in combined for x in ('KEILRIEMEN','XPB','SPA','SPZ','SPB','SPC','5V-')): return 'KEILRIEMEN'
    return 'STANDARD'

def ek_zu_vk(ek_preis, kategorie):
    aufschlag = AUFSCHLAG.get(kategorie, AUFSCHLAG['STANDARD'])
    vk = ek_preis * (1 + aufschlag)
    return round(vk, 2)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
})

# --- Schritt 1: Access Key ermitteln ---
print("Lade Shop-Startseite...")
r = session.get(BASE_URL + '/', timeout=15)
keys = re.findall(r'SWSC[A-Z0-9]+', r.text)
if not keys:
    # Aus Nuxt-Bundle holen
    r2 = session.get("https://www.dexis.at/", timeout=15)
    keys = re.findall(r'SWSC[A-Z0-9]+', r2.text)

if keys:
    SW_KEY = keys[0]
    print(f"Access Key: {SW_KEY}")
else:
    SW_KEY = 'SWSCBG1QNHLCMDFEAFLDWKLJUG'
    print(f"Fallback Key: {SW_KEY}")

session.headers['sw-access-key'] = SW_KEY

# --- Schritt 2: Login ---
print(f"\nLogin als {EMAIL}...")
login_data = {'email': EMAIL, 'password': PASSWORD}

# Versuche verschiedene Basis-URLs
for base in [BASE_URL, 'https://www.dexis.at']:
    r = session.post(f'{base}/store-api/account/login', json=login_data, timeout=15)
    print(f"  {base}: Status {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        token = data.get('contextToken', '')
        if token:
            session.headers['sw-context-token'] = token
            print(f"  Login OK! Context-Token: {token[:20]}...")
            BASE_URL = base
            break
        else:
            print(f"  Response: {str(data)[:200]}")
    else:
        print(f"  Fehler: {r.text[:200]}")
else:
    print("\nLogin fehlgeschlagen - breche ab.")
    exit(1)

# --- Schritt 3: Artikel laden ---
with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
    articles = json.load(f)

# Nur Excel-Originalartikel ohne Preis
ohne_preis = [a for a in articles if not a.get('vkPreis') and re.match(r'^\d{5,7}$', str(a.get('number','')).strip())]
print(f"\n{len(ohne_preis)} Excel-Artikel ohne Preis gefunden")

# --- Schritt 4: Preise abrufen ---
gefunden = 0
nicht_gefunden = 0
fehler = 0

for i, article in enumerate(ohne_preis):
    number = str(article.get('number','')).strip()
    bez1   = article.get('bez1','')

    if i % 50 == 0:
        print(f"  Fortschritt: {i}/{len(ohne_preis)} (gefunden: {gefunden})")

    # Suche per Artikelnummer
    try:
        search_payload = {
            'search': number,
            'limit': 5,
        }
        r = session.post(
            f'{BASE_URL}/store-api/search',
            json=search_payload,
            timeout=10
        )

        if r.status_code != 200:
            fehler += 1
            continue

        data = r.json()
        products = data.get('elements', data.get('data', {}).get('elements', []))

        if not products:
            nicht_gefunden += 1
            continue

        # Bestes Ergebnis nehmen - erstes Produkt
        product = products[0]
        price_data = product.get('calculatedPrice', product.get('price', {}))

        if isinstance(price_data, dict):
            ek = price_data.get('unitPrice', price_data.get('net', 0))
        elif isinstance(price_data, list) and price_data:
            ek = price_data[0].get('net', price_data[0].get('gross', 0))
        else:
            ek = 0

        if ek and float(ek) > 0:
            ek = float(ek)
            kat = get_kategorie(number, bez1)
            vk  = ek_zu_vk(ek, kat)

            article['ekPreis']  = str(round(ek, 2))
            article['vkPreis']  = str(vk)
            article['perMeter'] = article.get('perMeter', False)
            gefunden += 1
        else:
            nicht_gefunden += 1

        time.sleep(0.1)  # kurze Pause

    except Exception as e:
        fehler += 1
        if fehler <= 5:
            print(f"  Fehler bei {number}: {e}")

print(f"\nErgebnis:")
print(f"  Gefunden mit Preis: {gefunden}")
print(f"  Nicht gefunden:     {nicht_gefunden}")
print(f"  Fehler:             {fehler}")

if gefunden > 0:
    with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\narticles.json gespeichert!")
else:
    print("\nKeine neuen Preise - nichts gespeichert.")
