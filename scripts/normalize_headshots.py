#!/usr/bin/env python3
"""Normalize player headshots to a 96x96 top-aligned square WebP."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ROOT / "img" / "players"
SIZE = 96


def square_top(im: Image.Image, size: int = SIZE) -> Image.Image:
    im = im.convert("RGB")
    w, h = im.size
    side = min(w, h)
    left = max(0, (w - side) // 2)
    top = 0
    im = im.crop((left, top, left + side, top + side))
    return im.resize((size, size), Image.Resampling.LANCZOS)


def convert_one(src: Path) -> bool:
    dest = src.with_suffix(".webp")
    try:
        im = Image.open(src)
        out = square_top(im)
        out.save(dest, "WEBP", quality=78, method=4)
        return True
    except Exception as exc:
        print(f"skip {src.name}: {exc}")
        return False


def main() -> int:
    n = 0
    if not PLAYERS.exists():
        print("no img/players")
        return 1
    for src in sorted(PLAYERS.iterdir()):
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        if convert_one(src):
            n += 1
    print(f"normalized {n} headshots to {SIZE}x{SIZE} webp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
