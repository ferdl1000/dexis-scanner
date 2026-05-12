"""
convert_excel.py
Konvertiert die DEXIS Artikelliste (Excel) in articles.json fuer die Scanner-App.

Spalten der Excel-Datei:
  DEXIS Art.Nr.          -> number  (Artikelnummer)
  Art.Bez.1              -> description1
  Art.Bez.2              -> description2
  Ausgabe Scanner        -> barcode  (Barcode-Wert fuer den Scanner)
  hinterlegte Bestellmenge -> orderQty

Ausfuehren:
  python convert_excel.py
  python convert_excel.py MeineAndereArtikelliste.xlsx ausgabe.json
"""

import sys
import json
import os
import pandas as pd

EXCEL_FILE = "Artikelliste Firma Dorn Dexis.xlsx"
OUTPUT_FILE = "articles.json"

if len(sys.argv) >= 2:
    EXCEL_FILE = sys.argv[1]
if len(sys.argv) >= 3:
    OUTPUT_FILE = sys.argv[2]

if not os.path.exists(EXCEL_FILE):
    print(f"FEHLER: Datei '{EXCEL_FILE}' nicht gefunden.")
    sys.exit(1)

print(f"Lese: {EXCEL_FILE}")
df = pd.read_excel(EXCEL_FILE, sheet_name="OUTPUT DORN", dtype=str)
df = df.fillna("")

articles = []
skipped = 0

for _, row in df.iterrows():
    barcode = str(row.get("Ausgabe Scanner", "")).strip()
    number  = str(row.get("DEXIS Art.Nr.", "")).strip()
    desc1   = str(row.get("Art.Bez.1", "")).strip()
    desc2   = str(row.get("Art.Bez.2", "")).strip()
    order_qty = str(row.get("hinterlegte Bestellmenge", "")).strip()

    # Barcode muss vorhanden sein
    if not barcode or barcode in ("nan", "0"):
        # Fallback: Artikelnummer als Barcode verwenden
        barcode = number

    if not number:
        skipped += 1
        continue

    description = desc1
    if desc2 and desc2 != desc1:
        description = f"{desc1} - {desc2}" if desc1 else desc2

    articles.append({
        "barcode":    barcode,
        "number":     number,
        "bez1":       desc1,
        "bez2":       desc2,
        "description": description,
        "orderQty":   order_qty
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Fertig! {len(articles)} Artikel exportiert -> {OUTPUT_FILE}")
if skipped:
    print(f"  ({skipped} Zeilen uebersprungen - keine Artikelnummer)")
