"""
build_html.py
Ersetzt die eingebettete ARTICLES_DB-Zeile in scanner-app.html
mit dem aktuellen Inhalt von articles.json.

ACHTUNG: ueberschreibt KEIN HTML, sondern aktualisiert NUR die DB-Zeile
in der bestehenden Datei. Alle JS/CSS-Aenderungen bleiben erhalten.

Ausfuehren: python build_html.py
"""
import json, re, sys, os
from pathlib import Path

ROOT = Path(__file__).parent
HTML_FILE = ROOT / "scanner-app.html"
JSON_FILE = ROOT / "articles.json"

if not HTML_FILE.exists():
    print(f"FEHLER: {HTML_FILE} nicht gefunden")
    sys.exit(1)
if not JSON_FILE.exists():
    print(f"FEHLER: {JSON_FILE} nicht gefunden")
    sys.exit(1)

data = json.load(open(JSON_FILE, encoding="utf-8"))
compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

html = HTML_FILE.read_text(encoding="utf-8")

# Sucht: let ARTICLES_DB = [...] ODER const ARTICLES_DB = [...]
# bis zum schliessenden ];  am Zeilenende
pattern = re.compile(
    r'^(let|const|var)\s+ARTICLES_DB\s*=\s*\[.*?\];\s*$',
    re.MULTILINE | re.DOTALL
)

if not pattern.search(html):
    print("FEHLER: ARTICLES_DB-Zeile nicht gefunden in scanner-app.html")
    sys.exit(1)

new_line = f"let ARTICLES_DB = {compact};"
new_html, n = pattern.subn(new_line, html)
if n != 1:
    print(f"FEHLER: {n} Treffer (erwartet 1)")
    sys.exit(1)

# Backup
backup = HTML_FILE.with_suffix(".html.bak")
backup.write_text(html, encoding="utf-8")

HTML_FILE.write_text(new_html, encoding="utf-8")
print(f"OK: ARTICLES_DB in scanner-app.html aktualisiert ({len(data)} Artikel)")
print(f"     Backup: {backup.name}")
