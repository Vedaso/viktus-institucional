#!/usr/bin/env python3
"""Gera public/og-image.png (1200x630) do Grupo Viktus.

Composicao: fundo deep-navy com vinheta radial, o lockup "Viktus GESTAO" (bone)
centralizado e uma tagline sob ele. O wordmark vem do lockup PNG (fonte de marca
Space Grotesk correta); a tagline usa uma sans neutra do sistema.

Reexecutar apos trocar o lockup ou a tagline:
    python scripts/gen-og-image.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "public" / "brand"
OUT = ROOT / "public" / "og-image.png"

W, H = 1200, 630
DEEP = (5, 7, 20)       # #050714
NAVY = (14, 19, 48)     # #0E1330
BONE = (242, 238, 227)  # #F2EEE3

TAGLINE = "Tecnologia para saúde e gestão de negócios"

# ── fundo: navy no centro esvaindo para deep nas bordas (vinheta radial) ──────
bg = Image.new("RGB", (W, H), DEEP)
px = bg.load()
cx, cy = W / 2, H * 0.42
maxd = (cx**2 + cy**2) ** 0.5
for y in range(H):
    for x in range(0, W, 2):  # passo 2 no x: metade do custo, imperceptivel
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd
        t = min(1.0, d * 1.15)
        r = int(NAVY[0] + (DEEP[0] - NAVY[0]) * t)
        g = int(NAVY[1] + (DEEP[1] - NAVY[1]) * t)
        b = int(NAVY[2] + (DEEP[2] - NAVY[2]) * t)
        px[x, y] = (r, g, b)
        if x + 1 < W:
            px[x + 1, y] = (r, g, b)

img = bg.convert("RGBA")

# ── lockup "Viktus GESTAO" (bone) centralizado ────────────────────────────────
lock = Image.open(BRAND / "gestao-horizontal.png").convert("RGBA")
target_w = int(W * 0.46)
scale = target_w / lock.width
lock = lock.resize((target_w, int(lock.height * scale)), Image.LANCZOS)
lx = (W - lock.width) // 2
ly = int(H * 0.30) - lock.height // 2
img.alpha_composite(lock, (lx, ly))

# ── tagline sob o lockup ──────────────────────────────────────────────────────
def load_font(size):
    for name in ("segoeui.ttf", "arial.ttf", "calibri.ttf"):
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

draw = ImageDraw.Draw(img)
font = load_font(38)
# letter-spacing manual para dar ar de marca
text = TAGLINE
spacing = 1
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
ty = ly + lock.height + 46
draw.text(((W - tw) // 2, ty), text, font=font, fill=(242, 238, 227, 220))

# ── filete decorativo (acentos dos 3 produtos) ────────────────────────────────
# navy(financas) · sage(care) · fumaca(spaces) — barra fina sob a tagline
accents = [(79, 111, 96), (47, 51, 56), (14, 19, 48)]  # sage-ink, fumaca, navy
bar_w, bar_h, gap = 46, 5, 10
total = len(accents) * bar_w + (len(accents) - 1) * gap
bx = (W - total) // 2
by = ty + 64
for c in accents:
    draw.rounded_rectangle([bx, by, bx + bar_w, by + bar_h], radius=2, fill=c + (255,))
    bx += bar_w + gap

img.convert("RGB").save(OUT, "PNG", optimize=True)
print(f"OK -> {OUT}  ({W}x{H})")
