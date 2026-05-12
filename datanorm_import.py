"""
datanorm_import.py
Liest DATANORM.001 (V050) und merged die Artikel in articles.json.

DATANORM A-Satz Format (24 Felder, ; getrennt):
  0:  'A'
  1:  Verarbeitungskennzeichen (N=Neu, A=Aend., X=Loesch)
  2:  Artikelnummer
  3:  Kurztext 1 (Hauptbezeichnung)
  4:  Kurztext 2 (Zusatz)
  5:  Mengeneinheit (Stk, m, kg, ...)
  6:  Preisbasis (auf wieviele Einheiten bezieht sich der Preis)
  7:  Preisfaktor
  8:  Preis in Cent (ohne Komma)
  9:  Rabattgruppe
  10: Hauptwarengruppe
  ...

Aufruf: python datanorm_import.py [DATANORM.001-Pfad]
"""
import json, sys, os
from pathlib import Path

ROOT = Path(__file__).parent
DEFAULT_DN = ROOT / "Datanorm" / "DATANORM.001"
ARTICLES_FILE = ROOT / "articles.json"

dn_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DN
if not dn_path.exists():
    print(f"FEHLER: {dn_path} nicht gefunden")
    sys.exit(1)
if not ARTICLES_FILE.exists():
    print(f"FEHLER: {ARTICLES_FILE} nicht gefunden")
    sys.exit(1)

# Encoding-Erkennung
ENCODINGS_TO_TRY = ["cp850", "cp437", "latin1", "cp1252"]
content = None
chosen_enc = None
for enc in ENCODINGS_TO_TRY:
    try:
        content = dn_path.read_text(encoding=enc)
        # Plausibilitaetscheck: Umlaute erkennbar?
        sample = content[:5000].lower()
        if any(ch in sample for ch in "äöüÄÖÜß"):
            chosen_enc = enc
            break
    except Exception:
        continue
if not content:
    print("FEHLER: DATANORM-Datei nicht lesbar")
    sys.exit(1)
if not chosen_enc:
    chosen_enc = "cp850"
    content = dn_path.read_text(encoding=chosen_enc, errors="replace")
print(f"DATANORM gelesen mit encoding={chosen_enc}")

# Header
lines = content.splitlines()
header = next((l for l in lines if l.startswith("V;")), "")
print(f"Header: {header[:80]}")

# Parsen
new_articles = []
skipped = 0
seen_in_dn = set()  # Duplikate INNERHALB DATANORM zusammenfassen

PER_METER_MES = {"m", "mtr", "meter", "lfd.m", "lfm"}

for line in lines:
    line = line.rstrip("\r\n")
    if not line.startswith("A;"):
        continue
    parts = line.split(";")
    if len(parts) < 11:
        skipped += 1
        continue

    proc      = parts[1].strip()
    nummer    = parts[2].strip()
    bez1      = parts[3].strip()
    bez2      = parts[4].strip()
    me        = parts[5].strip()
    preisbasis_raw = parts[6].strip()
    preis_raw      = parts[8].strip()

    # Loeschsaetze ignorieren
    if proc.upper() == "X":
        continue
    if not nummer or not bez1:
        skipped += 1
        continue
    if nummer in seen_in_dn:
        continue
    seen_in_dn.add(nummer)

    # Preis berechnen
    try:
        preisbasis = int(preisbasis_raw) if preisbasis_raw else 1
        if preisbasis < 1: preisbasis = 1
    except ValueError:
        preisbasis = 1
    try:
        preis_cent = int(preis_raw) if preis_raw else 0
    except ValueError:
        preis_cent = 0
    vk = ""
    if preis_cent > 0:
        eur = (preis_cent / 100.0) / preisbasis
        vk = f"{eur:.2f}"

    per_meter = me.lower() in PER_METER_MES

    desc = bez1 if not bez2 or bez2 == bez1 else f"{bez1} - {bez2}"

    new_articles.append({
        "barcode":    nummer,
        "number":     nummer,
        "bez1":       bez1,
        "bez2":       bez2,
        "description": desc,
        "orderQty":   "",
        "vkPreis":    vk,
        "ekPreis":    "",
        "perMeter":   per_meter,
        "_source":    "DATANORM"   # Kennzeichen, dass Artikel aus DATANORM stammt
    })

print(f"DATANORM-Artikel geparst: {len(new_articles)} (uebersprungen: {skipped})")

# Mit articles.json mergen
with open(ARTICLES_FILE, encoding="utf-8") as f:
    articles = json.load(f)

# Index der bestehenden Nummern
existing = {str(a.get("number","")).strip(): a for a in articles if a.get("number")}

updated, added = 0, 0
for new in new_articles:
    key = new["number"]
    if key in existing:
        a = existing[key]
        # Nur fehlende Felder ergaenzen, nichts ueberschreiben was schon da war
        if not a.get("vkPreis") and new["vkPreis"]:
            a["vkPreis"] = new["vkPreis"]
            updated += 1
        if not a.get("bez1") and new["bez1"]:
            a["bez1"] = new["bez1"]
            a["description"] = new["description"]
        if not a.get("bez2") and new["bez2"]:
            a["bez2"] = new["bez2"]
        # perMeter nur setzen wenn vorher nicht definiert
        if "perMeter" not in a:
            a["perMeter"] = new["perMeter"]
    else:
        # Komplett neu
        articles.append({k: v for k, v in new.items() if k != "_source"})
        added += 1

print(f"Bestehende ergaenzt: {updated}")
print(f"Neu hinzugefuegt:    {added}")

# Speichern
with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\nFertig. articles.json: {len(articles)} Artikel gesamt")
with_price = sum(1 for a in articles if a.get("vkPreis") and float(a.get("vkPreis") or 0) > 0)
per_meter  = sum(1 for a in articles if a.get("perMeter"))
print(f"  mit VK-Preis: {with_price}")
print(f"  Meterware:    {per_meter}")
