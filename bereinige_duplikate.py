"""
bereinige_duplikate.py
Bereinigt articles.json:

1. Findet Excel-Artikel deren bez1/bez2 mit einer Preislisten-Nummer beginnt
   (z.B. bez1="GE 18-LR OMD" -> passt zu Preislisten-Nr "GE 18-LR" -> VK=2.39)
2. Traegt vkPreis + perMeter in den Excel-Artikel ein
3. Entfernt die nun redundante standalone Preislisten-Kopie aus articles.json
4. Entfernt reine Duplikate (identische Nummer mehrfach eingetragen)

Ausfuehren:
  python bereinige_duplikate.py
"""

import json
import re
from collections import defaultdict

ARTICLES_FILE = "articles.json"
PREISLISTE_FILE = "preisliste.json"

with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

with open(PREISLISTE_FILE, "r", encoding="utf-8") as f:
    preisliste = json.load(f)

print(f"Artikel gesamt (vorher): {len(articles)}")

def norm(s):
    """Normalisierung: Leerzeichen entfernen, Grossbuchstaben"""
    return re.sub(r"\s+", "", str(s)).upper().strip()

# ─── Preislisten-Index ────────────────────────────────────────────────────────
# normalisierte Nummer -> Preislisten-Eintrag
preis_dict = {}
for p in preisliste:
    preis_dict[norm(p["nummer"])] = p

# Auch nach Originalformat (mit Leerzeichen, Upper) indexieren fuer Teilvergleich
preis_list_sorted = sorted(preisliste, key=lambda p: len(p["nummer"]), reverse=True)

# ─── Hilfsfunktion: Passt Preislisten-Nr zum Artikelfeld? ────────────────────
def find_preisliste_match(article):
    """
    Sucht den passenden Preislisten-Eintrag fuer einen Excel-Artikel.
    Strategie:
    1. norm(number) == norm(preis_nummer)           -> exakte Nummer
    2. norm(bez1).startswith(norm(preis_nummer))    -> bez1 beginnt mit Preis-Nr
    3. norm(preis_nummer) in norm(bez1)             -> Preis-Nr enthalten in bez1
    Laengste Treffer gewinnen (verhindert Fehl-Zuordnung z.B. "G 6-L" fuer "G 6-L OMD")
    """
    n_num  = norm(article.get("number", ""))
    n_bez1 = norm(article.get("bez1", ""))
    n_bez2 = norm(article.get("bez2", ""))

    best = None
    best_len = 0

    for p in preis_list_sorted:
        pn = norm(p["nummer"])
        if not pn or len(pn) < 3:
            continue

        matched = False
        if pn == n_num:
            matched = True
        elif pn and n_bez1 and (n_bez1.startswith(pn) or pn == n_bez1):
            matched = True
        elif pn and n_bez2 and (n_bez2.startswith(pn) or pn == n_bez2):
            matched = True
        # Teilmatch: Preis-Nr enthalten in bez1 (fuer "6311 310 022" in "726311310022BG3...")
        elif pn and n_bez1 and pn in n_bez1 and len(pn) >= 8:
            matched = True

        if matched and len(pn) > best_len:
            best = p
            best_len = len(pn)

    return best


# ─── Schritt 1: Excel-Artikel mit Preisen versorgen ──────────────────────────
# Excel-Artikel = hat KEIN vkPreis gesetzt (die originalen)
preislisten_nummern_vergeben = set()  # welche Preis-Nummern wurden zugeordnet
updated_excel = 0

for a in articles:
    if a.get("vkPreis"):
        continue  # hat schon einen Preis -> ueberspringen

    match = find_preisliste_match(a)
    if match:
        vk = match.get("vkPreis", "")
        ek = match.get("ekPreis", "")
        pm = match.get("perMeter", False)

        if vk:
            a["vkPreis"]  = vk
            a["perMeter"] = pm
            if ek:
                a["ekPreis"] = ek
            preislisten_nummern_vergeben.add(norm(match["nummer"]))
            updated_excel += 1

print(f"Excel-Artikel mit Preis versorgt: {updated_excel}")
print(f"Preislisten-Nummern vergeben:     {len(preislisten_nummern_vergeben)}")

# ─── Schritt 2: Redundante Standalone-Preislisten-Kopien entfernen ───────────
# Ein Standalone-Eintrag ist redundant, wenn seine Nummer einem Excel-Artikel
# zugeordnet wurde (Preislisten-Nr als barcode == number, kein eigener langer Barcode)
def is_standalone_preislisteneintrag(a):
    """
    Standalone-Eintraege haben barcode == number (wurden von preise_update.py hinzugefuegt)
    und KEIN 7-stelliges Nummernformat
    """
    num = str(a.get("number", "")).strip()
    bar = str(a.get("barcode", "")).strip()
    # Original-Excel-Artikel: barcode enthaelt oft mehr Ziffern als number
    # Standalone: barcode == number (genau gleich)
    return bar == num and not re.match(r"^\d{7}$", num)

removed_standalone = 0
articles_clean = []
for a in articles:
    if is_standalone_preislisteneintrag(a):
        n = norm(a.get("number", ""))
        if n in preislisten_nummern_vergeben:
            # Dieser Eintrag ist jetzt redundant -> entfernen
            removed_standalone += 1
            continue
    articles_clean.append(a)

articles = articles_clean
print(f"Redundante Standalone-Kopien entfernt: {removed_standalone}")

# ─── Schritt 3: Reine Duplikate entfernen ─────────────────────────────────────
# Gleiche Nummer + gleiche barcode -> nur einmal behalten
seen = set()
articles_dedup = []
removed_dup = 0
for a in articles:
    key = (norm(a.get("number","")), norm(a.get("barcode","")))
    if key in seen:
        removed_dup += 1
        continue
    seen.add(key)
    articles_dedup.append(a)

articles = articles_dedup
print(f"Reine Duplikate entfernt:              {removed_dup}")

# ─── Schritt 4: Speichern ────────────────────────────────────────────────────
with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\nFertig! articles.json gespeichert: {len(articles)} Artikel gesamt")

with_price  = sum(1 for a in articles if a.get("vkPreis") and float(a.get("vkPreis") or 0) > 0)
with_meter  = sum(1 for a in articles if a.get("perMeter"))
excel_orig  = sum(1 for a in articles if re.match(r"^\d{5,7}$", str(a.get("number","")).strip()))
standalone  = sum(1 for a in articles if is_standalone_preislisteneintrag(a))
print(f"  Excel-Originalartikel:   {excel_orig}")
print(f"  Standalone Preis-Eintr.: {standalone}")
print(f"  davon mit VK-Preis:      {with_price}")
print(f"  davon Meterware:         {with_meter}")
