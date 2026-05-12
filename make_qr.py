"""
make_qr.py - Erstellt einen druckfaehigen QR-Code zur App.
Ausfuehren: python make_qr.py
"""
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

URL = "https://ferdl1000.github.io/dexis-scanner"
OUT = Path(__file__).parent / "Dorn-Teile-Scanner-QR.png"
A4_OUT = Path(__file__).parent / "Dorn-Teile-Scanner-QR-A4.png"

# 1) Basis-QR (sehr hohe Fehlerkorrektur, damit man Mittellogo platzieren koennte)
qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H,
                   box_size=20, border=2)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="#1a237e", back_color="white").convert("RGB")
img.save(OUT, "PNG")
print(f"OK: {OUT.name} ({img.size[0]}x{img.size[1]} px)")

# 2) A4-Druck-Layout: QR + Titel + URL + Anleitung
A4 = Image.new("RGB", (1200, 1700), "white")
draw = ImageDraw.Draw(A4)

def try_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/seguibl.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try: return ImageFont.truetype(c, size)
            except: pass
    return ImageFont.load_default()

f_title = try_font(70, bold=True)
f_sub   = try_font(36)
f_url   = try_font(34, bold=True)
f_body  = try_font(28)
f_small = try_font(24)

# Blauer Header
draw.rectangle([0, 0, 1200, 180], fill="#1a237e")
draw.text((600, 60), "Dorn Teile Scanner", fill="white", font=f_title, anchor="mm")
draw.text((600, 135), "Barcode-Scan-App der Firma Dorn", fill="#c5cae9", font=f_sub, anchor="mm")

# QR-Code zentriert
qr_size = 800
qr_img  = img.resize((qr_size, qr_size), Image.LANCZOS)
A4.paste(qr_img, ((1200 - qr_size)//2, 230))

# URL unter QR
draw.text((600, 1070), URL, fill="#1a237e", font=f_url, anchor="mm")

# Anleitung
draw.text((600, 1150), "So bekommst du die App aufs Handy:", fill="#222", font=f_body, anchor="mm")
draw.text((100, 1220), "1.", fill="#1a237e", font=f_body)
draw.text((150, 1220), "QR-Code mit Handy-Kamera scannen", fill="#222", font=f_body)
draw.text((100, 1270), "2.", fill="#1a237e", font=f_body)
draw.text((150, 1270), "Den erscheinenden Link antippen -> App oeffnet sich", fill="#222", font=f_body)
draw.text((100, 1320), "3.", fill="#1a237e", font=f_body)
draw.text((150, 1320), "iPhone (Safari): Teilen-Knopf -> 'Zum Home-Bildschirm'", fill="#222", font=f_body)
draw.text((150, 1360), "Android (Chrome): Menue (...) -> 'App installieren'", fill="#222", font=f_body)
draw.text((100, 1420), "4.", fill="#1a237e", font=f_body)
draw.text((150, 1420), "Beim ersten Start: Kamera erlauben - fertig!", fill="#222", font=f_body)

# Hinweis unten
draw.rectangle([0, 1600, 1200, 1700], fill="#fff9c4")
draw.text((600, 1650), "5.095 Artikel | Auto-Update | Offline-faehig | Drucken & E-Mail",
          fill="#5d4037", font=f_small, anchor="mm")

A4.save(A4_OUT, "PNG")
print(f"OK: {A4_OUT.name} ({A4.size[0]}x{A4.size[1]} px - A4-Druck)")
