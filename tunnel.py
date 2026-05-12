"""
tunnel.py
Oeffnet einen temporaeren HTTPS-Tunnel (via localtunnel).
Einfach doppelklicken - Browser oeffnet sich automatisch.

Voraussetzungen:
  - Node.js (https://nodejs.org) muss installiert sein
  - Wird automatisch geprüft
"""

import sys
import os
import subprocess
import threading
import re
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 8080
SCRIPT_DIR = Path(__file__).parent

# ============================================================
def check_node():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def check_npx():
    try:
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def print_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode", "-q"])
            import qrcode
            qr = qrcode.QRCode(border=1)
            qr.add_data(url)
            qr.make(fit=True)
            qr.print_ascii(invert=True)
        except Exception as e:
            print(f"  [QR-Code nicht verfügbar: {e}]")
            print(f"  QR generieren: https://qr-code-generator.com mit URL: {url}")

class SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

def start_local_server():
    server = HTTPServer(("127.0.0.1", PORT), SilentHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def start_tunnel():
    """Startet localtunnel und gibt die URL zurueck."""
    print("[INFO] Starte localtunnel (kann 10-30 Sekunden dauern)...")

    # Verwende localtunnel via npx
    cmd = ["npx", "--yes", "localtunnel", "--port", str(PORT)]

    if sys.platform == "win32":
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    tunnel_url = None
    deadline = time.time() + 60  # Max 60s warten

    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        print(f"  [localtunnel] {line.strip()}")
        # URL aus Output extrahieren
        match = re.search(r'(https://[a-z0-9\-]+\.loca\.lt)', line)
        if match:
            tunnel_url = match.group(1)
            break

    return proc, tunnel_url

# ============================================================
if __name__ == "__main__":
    os.chdir(SCRIPT_DIR)

    print()
    print("=" * 52)
    print("  DEXIS Scanner - Online Tunnel (temporaer)")
    print("=" * 52)
    print()

    # Node.js prüfen
    node_ver = check_node()
    if not node_ver:
        print("[FEHLER] Node.js ist nicht installiert!")
        print()
        print("  Bitte Node.js herunterladen und installieren:")
        print("  https://nodejs.org/de/download")
        print("  (LTS-Version empfohlen)")
        print()
        try:
            import webbrowser
            webbrowser.open("https://nodejs.org/de/download")
        except Exception:
            pass
        input("Nach der Installation Enter drücken zum erneuten Versuch...")
        # Nochmal prüfen
        node_ver = check_node()
        if not node_ver:
            print("[FEHLER] Node.js immer noch nicht gefunden. Bitte PC neu starten.")
            input("Enter drücken zum Beenden...")
            sys.exit(1)

    print(f"[OK] Node.js {node_ver} gefunden.")

    # scanner-app.html prüfen
    if not (SCRIPT_DIR / "scanner-app.html").exists():
        print("[FEHLER] scanner-app.html nicht gefunden!")
        input("Enter drücken zum Beenden...")
        sys.exit(1)

    # Lokalen HTTP-Server starten
    print(f"[INFO] Starte lokalen HTTP-Server auf Port {PORT}...")
    try:
        local_server = start_local_server()
        time.sleep(0.5)
        print(f"[OK] Lokaler Server aktiv.")
    except Exception as e:
        print(f"[FEHLER] Lokaler Server: {e}")
        input("Enter drücken zum Beenden...")
        sys.exit(1)

    # Tunnel starten
    proc, url = start_tunnel()

    if not url:
        print()
        print("[FEHLER] Konnte keine Tunnel-URL ermitteln.")
        print("  Mögliche Ursachen:")
        print("  - Kein Internet")
        print("  - localtunnel-Dienst nicht erreichbar")
        print("  - Versuche stattdessen local_server.py")
        proc.terminate()
        input("Enter drücken zum Beenden...")
        sys.exit(1)

    app_url = url + "/scanner-app.html"

    print()
    print("=" * 52)
    print("  FERTIG! Deine temporäre URL:")
    print()
    print(f"    {app_url}")
    print()
    print("  QR-Code (mit Handy scannen):")
    print()
    print_qr(app_url)
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║  HINWEIS: Diese URL ist TEMPORAER!   ║")
    print("  ║  Sie ist nur gueltig solange dieses  ║")
    print("  ║  Fenster offen ist.                  ║")
    print("  ║                                      ║")
    print("  ║  Fuer permanente URL:                ║")
    print("  ║  deploy_github.bat verwenden!        ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  Browser wird geöffnet...")
    print("  [Strg+C zum Beenden]")
    print()

    time.sleep(1)
    webbrowser.open(app_url)

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Tunnel gestoppt.")
        proc.terminate()
        local_server.shutdown()
