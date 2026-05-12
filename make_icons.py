"""
make_icons.py
Erstellt alle App-Icons (PNG) aus einem SVG-Design.
Wird für PWA-Installation auf iOS + Android + Windows gebraucht.
Ausfuehren: python make_icons.py
"""
from PIL import Image, ImageDraw
import os

ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(ICON_DIR, exist_ok=True)

# Farben (gleich wie App)
PRIMARY = (26, 35, 126)       # #1a237e
PRIMARY_LIGHT = (57, 73, 171) # #3949ab
GREEN = (46, 125, 50)         # #2e7d32
RED = (239, 83, 80)           # #ef5350
WHITE = (255, 255, 255)

def make_icon(size, rounded=True, maskable_pad=0):
    """Erstellt ein quadratisches Icon der Groesse `size`.
    maskable_pad: Anteil 0..0.2 Sicherheitsrand fuer Android Maskable Icons."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Hintergrund (Gradient simuliert per Stufen)
    if rounded:
        r = int(size * 0.22)
        # Voller Hintergrund (fuer Maskable: ganz fuellen)
        if maskable_pad > 0:
            d.rectangle([0, 0, size, size], fill=PRIMARY)
        else:
            d.rounded_rectangle([0, 0, size, size], radius=r, fill=PRIMARY)
    else:
        d.rectangle([0, 0, size, size], fill=PRIMARY)

    # Innere Zeichenflaeche (mit Sicherheitsrand)
    pad = int(size * (0.18 + maskable_pad))
    inner = size - 2 * pad

    # Scanner-Linien (Barcode)
    bar_y1 = pad + int(inner * 0.15)
    bar_y2 = pad + int(inner * 0.85)
    line_w = max(2, int(inner * 0.045))
    gap = max(1, int(inner * 0.04))
    n_lines = 9
    block_w = n_lines * line_w + (n_lines - 1) * gap
    x_start = pad + (inner - block_w) // 2
    for i in range(n_lines):
        x = x_start + i * (line_w + gap)
        # variable Linien-Breite (echter Barcode-Look)
        w = line_w if i % 3 != 1 else int(line_w * 1.4)
        d.rectangle([x, bar_y1, x + w, bar_y2], fill=WHITE)

    # Roter Scan-Strahl
    laser_y = pad + inner // 2
    laser_h = max(2, int(size * 0.018))
    d.rectangle(
        [pad - int(size*0.02), laser_y - laser_h, size - pad + int(size*0.02), laser_y + laser_h],
        fill=RED
    )

    # Gruener Check-Kreis oben rechts
    cr = int(inner * 0.18)
    cx = size - pad - cr + int(inner * 0.05)
    cy = pad + cr - int(inner * 0.05)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=GREEN, outline=WHITE, width=max(2, int(size*0.012)))
    # Check-Haken
    cw = max(2, int(size * 0.018))
    d.line(
        [(cx - cr*0.45, cy + cr*0.05),
         (cx - cr*0.10, cy + cr*0.40),
         (cx + cr*0.55, cy - cr*0.35)],
        fill=WHITE, width=cw, joint="curve"
    )

    return img

# Erforderliche Groessen fuer max. Kompatibilitaet
SIZES = {
    "icon-192.png":            (192, True,  0.0),
    "icon-512.png":            (512, True,  0.0),
    "icon-192-maskable.png":   (192, False, 0.05),
    "icon-512-maskable.png":   (512, False, 0.05),
    "apple-touch-icon.png":    (180, False, 0.0),  # iOS - kein eigenes Rounding (iOS macht das selbst)
    "favicon-32.png":          (32,  True,  0.0),
    "favicon-16.png":          (16,  True,  0.0),
}

for name, (size, rounded, mpad) in SIZES.items():
    img = make_icon(size, rounded=rounded, maskable_pad=mpad)
    path = os.path.join(ICON_DIR, name)
    img.save(path, "PNG", optimize=True)
    print(f"  -> {name}  ({size}x{size})")

# Favicon ICO (mehrere Aufloesungen)
fav32 = Image.open(os.path.join(ICON_DIR, "favicon-32.png"))
fav32.save(os.path.join(ICON_DIR, "favicon.ico"),
           format="ICO", sizes=[(16,16),(32,32),(48,48)])
print(f"  -> favicon.ico")

print(f"\nFertig. {len(SIZES)+1} Icons in {ICON_DIR}")
