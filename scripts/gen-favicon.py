#!/usr/bin/env python3
"""Gera o kit de favicon da marca-mãe Viktus (símbolo V) a partir dos PNGs oficiais.
Direção nova do brand (2026-06-09): SVG adaptativo + transparente; tiles opacos navy p/ iOS/Android.
"""
import base64, io, os
from PIL import Image

BRAND = os.path.expanduser("~/OneDrive/Viktus - Gestão/Viktus/Viktus Brand/assets/parts")
OUT   = os.path.expanduser("~/dev/viktus-institucional/public")

NAVY = (14, 19, 48, 255)   # #0E1330  (tile opaco / V modo claro)
bone_src = Image.open(os.path.join(BRAND, "v-mark.png")).convert("RGBA")       # V bone (fundo escuro)
navy_src = Image.open(os.path.join(BRAND, "v-mark-navy.png")).convert("RGBA")  # V navy (fundo claro)

def fit_center(mark, canvas_px, scale, bg=None):
    """Coloca o V centrado num canvas quadrado. bg=None => transparente."""
    W = H = canvas_px
    base = Image.new("RGBA", (W, H), bg if bg else (0, 0, 0, 0))
    target_h = int(H * scale)
    target_w = int(mark.width * (target_h / mark.height))
    m = mark.resize((target_w, target_h), Image.LANCZOS)
    base.alpha_composite(m, ((W - target_w) // 2, (H - target_h) // 2))
    return base

def b64_png(img):
    buf = io.BytesIO(); img.save(buf, "PNG"); return base64.b64encode(buf.getvalue()).decode()

# --- 1. favicon.svg adaptativo + transparente (embute navy p/ claro, bone p/ escuro) ---
# Usa os PNGs em alta densidade (nativos 90x98) centrados num viewBox quadrado com respiro.
navy_sq = fit_center(navy_src, 100, 0.86)
bone_sq = fit_center(bone_src, 100, 0.86)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <style>
    .v-dark {{ display: none }}
    @media (prefers-color-scheme: dark) {{
      .v-light {{ display: none }}
      .v-dark {{ display: block }}
    }}
  </style>
  <image class="v-light" x="0" y="0" width="100" height="100" href="data:image/png;base64,{b64_png(navy_sq)}"/>
  <image class="v-dark" x="0" y="0" width="100" height="100" href="data:image/png;base64,{b64_png(bone_sq)}"/>
</svg>
'''
open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(svg)

# --- 2. favicon-32.png (transparente, navy — fallback p/ navegadores sem SVG) ---
fit_center(navy_src, 32, 0.86).save(os.path.join(OUT, "favicon-32.png"))

# --- 3. favicon.ico (16+32 navy transparente) ---
ico = fit_center(navy_src, 64, 0.86)
ico.save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# --- 4. apple-touch-icon.png (180 opaco navy + V bone — iOS exige fundo opaco) ---
fit_center(bone_src, 180, 0.56, bg=NAVY).save(os.path.join(OUT, "apple-touch-icon.png"))

# --- 5. android-chrome 192/512 (opaco navy + V bone; maskable-safe) ---
fit_center(bone_src, 192, 0.56, bg=NAVY).save(os.path.join(OUT, "android-chrome-192.png"))
fit_center(bone_src, 512, 0.56, bg=NAVY).save(os.path.join(OUT, "android-chrome-512.png"))

print("OK — gerados:")
for f in ["favicon.svg","favicon-32.png","favicon.ico","apple-touch-icon.png","android-chrome-192.png","android-chrome-512.png"]:
    p = os.path.join(OUT, f); print(f"  {f:26} {os.path.getsize(p):>7} bytes")
