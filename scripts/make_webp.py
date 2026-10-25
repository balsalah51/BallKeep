#!/usr/bin/env python3
"""Write WebP siblings for player headshots. Originals stay as the fallback."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ROOT / "img" / "players"


def main() -> int:
    n = 0
    for src in sorted(PLAYERS.iterdir()):
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        dest = src.with_suffix(".webp")
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        try:
            im = Image.open(src)
            im = im.convert("RGB")
            im.thumbnail((256, 256))
            im.save(dest, "WEBP", quality=72, method=4)
            n += 1
        except Exception as exc:
            print(f"skip {src.name}: {exc}")
    print(f"webp written {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
