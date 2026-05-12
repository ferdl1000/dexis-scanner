"""
local_server.py
Lokaler HTTPS-Server fuer DEXIS Scanner.
Einfach doppelklicken - kein technisches Wissen noetig.

Voraussetzungen (werden automatisch installiert):
  pip install cryptography qrcode[pil]
"""

import sys
import os
import subprocess
import socket
import ssl
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ============================================================
# Auto-Install fehlender Pakete
# ============================================================
def install(pkg):
    print(f"  Installiere {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime
except ImportError:
    print("[INFO] Installiere 'cryptography'...")
    install("cryptography")
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime

try:
    import qrcode
except ImportError:
    print("[INFO] Installiere 'qrcode'...")
    install("qrcode[pil]")
    import qrcode

# ============================================================
PORT = 8443
SCRIPT_DIR = Path(__file__).parent
CERT_FILE = SCRIPT_DIR / "server.crt"
KEY_FILE  = SCRIPT_DIR / "server.key"

# ============================================================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_cert(ip):
    print("[INFO] Erzeuge SSL-Zertifikat...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, ip),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DEXIS Scanner"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.IPAddress(__import__("ipaddress").IPv4Address(ip)),
                x509.IPAddress(__import__("ipaddress").IPv4Address("127.0.0.1")),
                x509.DNSName("localhost"),
            ]), critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    KEY_FILE.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))
    print("[OK] Zertifikat erstellt.")

def print_qr(url):
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception as e:
        print(f"  [QR-Code Fehler: {e}]")

class SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # Keine Request-Logs

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

def start_server(ip):
    if not CERT_FILE.exists():
        generate_cert(ip)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(CERT_FILE), str(KEY_FILE))

    server = HTTPServer(("0.0.0.0", PORT), SilentHandler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    return server

def open_browser(url, delay=2.0):
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()

# ============================================================
if __name__ == "__main__":
    os.chdir(SCRIPT_DIR)

    # Prüfe ob scanner-app.html vorhanden
    if not (SCRIPT_DIR / "scanner-app.html").exists():
        print("[FEHLER] scanner-app.html nicht gefunden!")
        print("  Bitte dieses Skript im selben Ordner wie scanner-app.html starten.")
        input("Enter drücken zum Beenden...")
        sys.exit(1)

    ip = get_local_ip()

    print()
    print("=" * 52)
    print("  DEXIS Scanner - Lokaler HTTPS-Server")
    print("=" * 52)
    print()

    try:
        server = start_server(ip)
    except Exception as e:
        print(f"[FEHLER] Server konnte nicht gestartet werden: {e}")
        input("Enter drücken zum Beenden...")
        sys.exit(1)

    pc_url    = f"https://localhost:{PORT}/scanner-app.html"
    handy_url = f"https://{ip}:{PORT}/scanner-app.html"

    print(f"  PC:    {pc_url}")
    print(f"  Handy: {handy_url}")
    print()
    print("  QR-Code fuer Handy (gleiches WLAN):")
    print()
    print_qr(handy_url)
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║  WICHTIG: Browser-Warnung            ║")
    print("  ║  'Verbindung nicht sicher' erscheint.║")
    print("  ║  Klicke auf 'Erweitert' → 'Trotzdem  ║")
    print("  ║  aufrufen'. Das ist einmalig noetig.  ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  Server laeuft... [Strg+C zum Beenden]")
    print()

    open_browser(pc_url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server gestoppt.")
