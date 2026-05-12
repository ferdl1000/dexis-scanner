#!/usr/bin/env python
# deploy_github.py
# GitHub Pages Deployment ohne Browser-Auth
# Einfach doppelklicken oder: python deploy_github.py

import subprocess, sys, os, json, urllib.request, urllib.parse, base64, getpass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
HTML_FILE  = SCRIPT_DIR / "scanner-app.html"
JSON_FILE  = SCRIPT_DIR / "articles.json"
REPO_NAME  = "dexis-scanner"

def run(cmd, check=True, capture=False):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "Fehler")
    return r

def api(token, method, path, data=None):
    url = "https://api.github.com" + path
    body = json.dumps(data).encode() if data else None
    req  = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "token " + token)
    req.add_header("Accept",        "application/vnd.github+json")
    req.add_header("Content-Type",   "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"API {e.code}: {body}")

print()
print("="*54)
print("  DEXIS Scanner - GitHub Pages Deployment")
print("="*54)
print()

if not HTML_FILE.exists():
    print("[FEHLER] scanner-app.html nicht gefunden!")
    input("Enter druecken...")
    sys.exit(1)

# Schritt 1: Git pruefen
try:
    run("git --version", capture=True)
    print("[OK] Git gefunden.")
except:
    print("[FEHLER] Git nicht installiert!")
    print("  Bitte herunterladen: https://git-scm.com/download/win")
    import webbrowser; webbrowser.open("https://git-scm.com/download/win")
    input("Nach Installation Enter druecken...")
    sys.exit(1)

# Schritt 2: Anleitung Personal Access Token
print()
print("Fuer den Upload benoetigen wir ein GitHub Personal Access Token.")
print("So erstellen:")
print()
print("  1. Browser oeffnen: https://github.com/settings/tokens/new")
print("     (GitHub-Account benoetigt - kostenlos auf github.com registrieren)")
print()
print("  2. Ausfuellen:")
print("     - Note: dexis-scanner")
print("     - Expiration: No expiration")
print("     - Haken setzen bei: [x] repo  (ganzer Bereich)")
print()
print("  3. Ganz unten: 'Generate token' klicken")
print("  4. Den angezeigten Token (ghp_xxxxx...) kopieren")
print()
import webbrowser
webbrowser.open("https://github.com/settings/tokens/new")
print("  Browser wurde geoeffnet.")
print()

username = input("GitHub Benutzername eingeben: ").strip()
token    = getpass.getpass("GitHub Token (ghp_...) eingeben [unsichtbar]: ").strip()

if not username or not token:
    print("[FEHLER] Benutzername oder Token leer.")
    input("Enter...")
    sys.exit(1)

# Schritt 3: Token testen
print()
print("[INFO] Teste Token...")
try:
    user = api(token, "GET", "/user")
    print(f"[OK] Eingeloggt als: {user['login']}")
    username = user["login"]
except Exception as e:
    print(f"[FEHLER] Token ungueltig: {e}")
    input("Enter...")
    sys.exit(1)

# Schritt 4: Git konfigurieren
run(f'git config --global user.email "{username}@users.noreply.github.com"')
run(f'git config --global user.name "{username}"')
print("[OK] Git-Identitaet gesetzt.")

# Schritt 5: Repo erstellen (oder pruefen ob vorhanden)
print()
print(f"[INFO] Erstelle Repo '{REPO_NAME}'...")
try:
    api(token, "POST", "/user/repos", {
        "name": REPO_NAME, "private": False, "auto_init": False
    })
    print("[OK] Repo erstellt.")
except RuntimeError as e:
    if "already exists" in str(e) or "422" in str(e):
        print("[OK] Repo existiert bereits.")
    else:
        print(f"[FEHLER] {e}")
        input("Enter...")
        sys.exit(1)

# Schritt 6: Dateien via API hochladen (Helper)
def upload_file(local_path, remote_name, label):
    print(f"[INFO] Lade {label} hoch...")
    content_b64 = base64.b64encode(local_path.read_bytes()).decode()
    sha = None
    for branch in ("main", "master"):
        try:
            existing = api(token, "GET", f"/repos/{username}/{REPO_NAME}/contents/{remote_name}?ref={branch}")
            sha = existing.get("sha"); break
        except:
            pass
    payload = {"message": f"Update {remote_name}", "content": content_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    try:
        api(token, "PUT", f"/repos/{username}/{REPO_NAME}/contents/{remote_name}", payload)
        print(f"[OK] {label} hochgeladen.")
    except RuntimeError as e:
        payload["branch"] = "master"
        try:
            api(token, "PUT", f"/repos/{username}/{REPO_NAME}/contents/{remote_name}", payload)
            print(f"[OK] {label} hochgeladen (master).")
        except Exception as e2:
            print(f"[FEHLER] {label} Upload fehlgeschlagen: {e2}")
            raise

upload_file(HTML_FILE, "index.html", "scanner-app.html")
# Zweites Mal als scanner-app.html (damit beide URLs funktionieren)
upload_file(HTML_FILE, "scanner-app.html", "scanner-app.html (Alias)")

if JSON_FILE.exists():
    upload_file(JSON_FILE, "articles.json", "articles.json (Auto-Update Quelle)")
else:
    print("[WARN] articles.json fehlt – Auto-Update wird nicht funktionieren.")

# PWA-Dateien: Manifest, Service Worker, Icons
PWA_FILES = [
    ("manifest.json", "manifest.json", "manifest.json"),
    ("sw.js",         "sw.js",         "Service Worker"),
]
for local, remote, label in PWA_FILES:
    p = SCRIPT_DIR / local
    if p.exists():
        upload_file(p, remote, label)
    else:
        print(f"[WARN] {local} fehlt – PWA nicht voll funktionsfähig.")

# Icons (Verzeichnis)
icon_dir = SCRIPT_DIR / "icons"
if icon_dir.exists():
    for icon in icon_dir.glob("*.png"):
        upload_file(icon, f"icons/{icon.name}", f"icon {icon.name}")
    ico = icon_dir / "favicon.ico"
    if ico.exists():
        upload_file(ico, "icons/favicon.ico", "favicon.ico")
else:
    print("[WARN] icons/ Verzeichnis fehlt – bitte 'python make_icons.py' ausführen.")

# Schritt 7: GitHub Pages aktivieren
print("[INFO] Aktiviere GitHub Pages...")
for branch in ["main", "master"]:
    try:
        api(token, "POST", f"/repos/{username}/{REPO_NAME}/pages",
            {"source": {"branch": branch, "path": "/"}})
        print(f"[OK] GitHub Pages aktiviert (branch: {branch}).")
        break
    except:
        pass

pages_url = f"https://{username}.github.io/{REPO_NAME}"

print()
print("="*54)
print("  FERTIG!")
print("="*54)
print()
print(f"  App-URL (nach 2-3 Min aktiv):")
print()
print(f"    {pages_url}")
print()
print("  Diese URL bookmarken - sie aendert sich NIE!")
print()

# QR-Code
try:
    import qrcode
    qr = qrcode.QRCode(border=1)
    qr.add_data(pages_url)
    qr.make(fit=True)
    print("  QR-Code:")
    qr.print_ascii(invert=True)
except ImportError:
    print("  [QR-Code: pip install qrcode  dann nochmal starten]")

print()
input("Enter druecken zum Beenden...")
