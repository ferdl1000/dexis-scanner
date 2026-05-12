"""
preise_update.py
Bereinigt articles.json:
  1. Entfernt alle erfundenen Fake-Artikel (HY-xxx, FKS-xx, SCH-xx, G4-xx, GE-xx, GR-xx, SKF-xx, KB-xxx)
  2. Laedt preisliste.json (echte Artikel aus den 5 Preislisten-Bildern)
  3. Gleicht ab: wenn Nummer bereits in articles.json -> vkPreis + perMeter ergaenzen
  4. Neue Artikel werden hinzugefuegt
  5. Speichert alles in articles.json

Ausfuehren:
  python preise_update.py
"""

import json
import os

ARTICLES_FILE = "articles.json"
PREISLISTE_FILE = "preisliste.json"

# ─── 1. Laden ────────────────────────────────────────────────────────────────
if not os.path.exists(ARTICLES_FILE):
    print(f"FEHLER: {ARTICLES_FILE} nicht gefunden.")
    exit(1)

if not os.path.exists(PREISLISTE_FILE):
    print(f"FEHLER: {PREISLISTE_FILE} nicht gefunden. Bitte erst erstelle_preisliste_json.py ausfuehren.")
    exit(1)

with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

with open(PREISLISTE_FILE, "r", encoding="utf-8") as f:
    preisliste = json.load(f)

print(f"Geladene Artikel (vorher):  {len(articles)}")
print(f"Preislisten-Eintraege:      {len(preisliste)}")

# ─── 2. Fake-Artikel entfernen ───────────────────────────────────────────────
# Alle Artikel-Nummern die von der alten, falschen preise_update.py hinzugefuegt wurden.
FAKE_PREFIXES = ("HY-", "FKS-", "SCH-", "G4-", "GE-", "GR-", "SKF-", "KB-")

def is_fake(article):
    num = str(article.get("number", "")).strip()
    for prefix in FAKE_PREFIXES:
        if num.startswith(prefix):
            return True
    return False

original_count = len(articles)
articles = [a for a in articles if not is_fake(a)]
removed_count = original_count - len(articles)
print(f"Fake-Artikel entfernt:      {removed_count}")
print(f"Verbleibende Artikel:       {len(articles)}")

# ─── 3. Index aufbauen (Nummer -> Artikel) ────────────────────────────────────
number_index = {}
for a in articles:
    num = str(a.get("number", "")).strip()
    if num:
        number_index[num] = a

# ─── 4. Preisliste einspielen ────────────────────────────────────────────────
updated = 0
added = 0

for p in preisliste:
    nummer = str(p.get("nummer", "")).strip()
    if not nummer:
        continue

    vk = str(p.get("vkPreis", "")).strip()
    ek = str(p.get("ekPreis", "")).strip()
    per_meter = bool(p.get("perMeter", False))
    bezeichnung = str(p.get("bezeichnung", "")).strip()

    if nummer in number_index:
        # Vorhandenen Artikel aktualisieren
        a = number_index[nummer]
        if vk:
            a["vkPreis"] = vk
        if ek:
            a["ekPreis"] = ek
        a["perMeter"] = per_meter
        # Bezeichnung nur setzen wenn bez1 leer
        if not a.get("bez1") and bezeichnung:
            a["bez1"] = bezeichnung
            a["description"] = bezeichnung
        updated += 1
    else:
        # Neuen Artikel hinzufuegen
        new_article = {
            "barcode":      nummer,
            "number":       nummer,
            "bez1":         bezeichnung,
            "bez2":         "",
            "description":  bezeichnung,
            "orderQty":     "",
            "vkPreis":      vk,
            "ekPreis":      ek,
            "perMeter":     per_meter
        }
        articles.append(new_article)
        number_index[nummer] = new_article
        added += 1

print(f"Vorhandene Artikel aktualisiert: {updated}")
print(f"Neue Artikel hinzugefuegt:       {added}")

# ─── 5. Speichern ────────────────────────────────────────────────────────────
with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\nFertig! articles.json gespeichert: {len(articles)} Artikel gesamt")

# ─── 6. Zusammenfassung ──────────────────────────────────────────────────────
with_price = sum(1 for a in articles if a.get("vkPreis") and float(a.get("vkPreis") or 0) > 0)
with_meter = sum(1 for a in articles if a.get("perMeter"))
print(f"  davon mit VK-Preis:  {with_price}")
print(f"  davon Meterware:     {with_meter}")
