#!/usr/bin/env python3
"""Write WebP siblings for player headshots. Originals stay as the fallback."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ROOT / "img" / "players"


def write_webp(src: Path, max_edge: int, quality: int) -> bool:
    dest = src.with_suffix(".webp")
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return False
    im = Image.open(src)
    im = im.convert("RGB")
    im.thumbnail((max_edge, max_edge))
    im.save(dest, "WEBP", quality=quality, method=4)
    return True


def main() -> int:
    n = 0
    for src, edge, quality in (
        (ROOT / "img" / "hero.jpg", 1400, 68),
        (ROOT / "img" / "logo.jpg", 256, 72),
    ):
        if src.exists() and write_webp(src, edge, quality):
            n += 1
    for src in sorted(PLAYERS.iterdir()):
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        dest = src.with_suffix(".webp")
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        try:
            if write_webp(src, 256, 72):
                n += 1
        except Exception as exc:
            print(f"skip {src.name}: {exc}")
    print(f"webp written {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
