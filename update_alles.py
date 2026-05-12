"""
update_alles.py
Macht in einem Rutsch:
  1. Excel  -> articles.json        (convert_excel.py)
  2. Preise -> preisliste.json      (erstelle_preisliste_json.py)
  3. Preise in articles.json mergen (preise_update.py)
  4. Sanitycheck (Duplikate, leere Felder)
  5. Optional: HTML neu bauen (build_html.py)
  6. Optional: GitHub Pages deployen (deploy_github.py)

Aufruf:
  python update_alles.py               # nur Daten aktualisieren
  python update_alles.py --build       # zusätzlich HTML bauen
  python update_alles.py --deploy      # zusätzlich auf GitHub Pages pushen
"""
import subprocess, sys, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def run(script):
    print(f"\n=== {script} ===")
    r = subprocess.run([sys.executable, script], capture_output=False)
    if r.returncode != 0:
        print(f"FEHLER in {script} (Exit {r.returncode})")
        sys.exit(r.returncode)

# 1-3: Daten aktualisieren
run("convert_excel.py")
run("erstelle_preisliste_json.py")
run("preise_update.py")

# 4: Sanitycheck
print("\n=== Sanitycheck ===")
with open("articles.json", encoding="utf-8") as f:
    arts = json.load(f)

barcodes, numbers = {}, {}
dups_bc, dups_num, leer_bez, leer_preis = [], [], [], []
for a in arts:
    bc, nr = a.get("barcode","").strip(), a.get("number","").strip()
    if bc:
        if bc in barcodes: dups_bc.append(bc)
        barcodes[bc] = a
    if nr:
        if nr in numbers: dups_num.append(nr)
        numbers[nr] = a
    if not (a.get("bez1") or a.get("description")):
        leer_bez.append(nr)
    if not a.get("vkPreis"):
        leer_preis.append(nr)

print(f"  Artikel gesamt:        {len(arts)}")
print(f"  Doppelte Barcodes:     {len(dups_bc)}  {dups_bc[:5]}")
print(f"  Doppelte Nummern:      {len(dups_num)} {dups_num[:5]}")
print(f"  Ohne Bezeichnung:      {len(leer_bez)}")
print(f"  Ohne VK-Preis:         {len(leer_preis)}")

# Sanity-Report wegschreiben
with open("sanity_report.txt", "w", encoding="utf-8") as f:
    f.write(f"Artikel gesamt: {len(arts)}\n")
    f.write(f"\nDoppelte Barcodes ({len(dups_bc)}):\n" + "\n".join(dups_bc))
    f.write(f"\n\nDoppelte Nummern ({len(dups_num)}):\n" + "\n".join(dups_num))
    f.write(f"\n\nOhne Bezeichnung ({len(leer_bez)}):\n" + "\n".join(leer_bez))
    f.write(f"\n\nOhne VK-Preis ({len(leer_preis)}):\n" + "\n".join(leer_preis))
print("  -> sanity_report.txt geschrieben")

# 5: HTML bauen
if "--build" in sys.argv or "--deploy" in sys.argv:
    run("build_html.py")

# 6: Deploy
if "--deploy" in sys.argv:
    run("deploy_github.py")

print("\nAlles fertig.")
