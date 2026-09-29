#!/usr/bin/env python3
"""Copia o kit de favicon do Institucional (V-mark) para public/.

Direção 2026-09-29: a pasta de marca foi reorganizada em um kit por marca
(gerar-kit.py). O Institucional usa o V-mark e o kit já vem com os PNGs/SVG/ICO
prontos em favicon/ — este script só copia para public/, não desenha mais nada.
"""
import os
import shutil

BRAND = os.path.expanduser(
    "~/OneDrive/Viktus - Gestão/Viktus/Viktus Brand/institucional/favicon"
)
OUT = os.path.expanduser("~/dev/viktus-institucional/public")

# Nomes que o site referencia (src/layouts/Site.astro, public/site.webmanifest).
FILES = [
    "favicon.svg",
    "favicon-32.png",
    "favicon.ico",
    "apple-touch-icon.png",
    "android-chrome-192.png",
    "android-chrome-512.png",
]

print("Copiando kit do Institucional:", BRAND)
for f in FILES:
    src = os.path.join(BRAND, f)
    dst = os.path.join(OUT, f)
    shutil.copyfile(src, dst)
    print(f"  {f:26} {os.path.getsize(dst):>7} bytes")
