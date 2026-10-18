#!/usr/bin/env python3
"""Vytvoří zmenšené WebP verze fotek pro rychlejší načítání (hlavně na mobilu).

Spuštění:  python3 tools/optimize_images.py   (potřebuje Pillow: pip install pillow)
K souboru assets/img/kocka.jpg vzniknou kocka-400.webp a kocka-800.webp.
tools/build.py je pak sám najde a použije v <picture> se srcset.
Spusťte znovu, kdykoli přidáte nebo vyměníte fotku.
"""
import pathlib

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDTHS = (400, 800)
FOLDERS = [ROOT / "assets/img", ROOT / "assets/img/domov"]

for folder in FOLDERS:
    for src in sorted(folder.glob("*.jpg")):
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        for w in WIDTHS:
            out = src.with_name(f"{src.stem}-{w}.webp")
            if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
                continue
            if im.width < w * 0.9 and w != WIDTHS[0]:
                continue  # větší verze než originál nemá smysl
            copy = im.copy()
            copy.thumbnail((w, w * 2), Image.LANCZOS)
            copy.save(out, "WEBP", quality=74, method=6)
            print(f"{out.relative_to(ROOT)}  {copy.width}x{copy.height}  {out.stat().st_size // 1024} kB")
