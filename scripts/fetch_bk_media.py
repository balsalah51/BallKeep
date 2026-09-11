"""Download NBA headshots for BasketKeep."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_data import bk_norm, load_universe  # noqa: E402
from fetch_player_media import download_image, espn_search_headshot, slugify, wiki_thumb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "img" / "bk-players"
OUT = ROOT / "data" / "bk-media.json"
PHOTO_ALIASES = {
    "Herb Jones": ["Herbert Jones"],
    "Deandre Hunter": ["De'Andre Hunter"],
    "Deanthony Melton": ["De'Anthony Melton"],
}


def pick_urls(name: str) -> list[str]:
    urls = []
    for query in [name, *PHOTO_ALIASES.get(name, [])]:
        espn = espn_search_headshot(query)
        if espn and espn not in urls:
            urls.append(espn)
        wiki = wiki_thumb(query)
        if wiki and wiki not in urls:
            urls.append(wiki)
    return urls


def main():
    u = load_universe()
    rows = []
    seen = set()
    for r in (u.get("keep") or []) + (u.get("board") or []):
        key = r.get("key") or bk_norm(r.get("name") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append(r)

    IMG.mkdir(parents=True, exist_ok=True)
    media = json.loads(OUT.read_text()) if OUT.exists() else {}
    n_img = n_miss = 0
    for r in rows:
        name = r.get("name") or ""
        key = r.get("key") or bk_norm(name)
        slug = slugify(name)
        rec = media.get(key) or {}
        dest_jpg = IMG / f"{slug}.jpg"
        dest_png = IMG / f"{slug}.png"
        existing = dest_jpg if dest_jpg.exists() else dest_png if dest_png.exists() else None
        if existing:
            rec.update({
                "key": key, "slug": slug, "name": name,
                "pos": r.get("pos") or "", "team": r.get("team") or "",
                "image": f"img/bk-players/{existing.name}",
            })
            if r.get("age") not in (None, ""):
                rec["age"] = r["age"]
            media[key] = rec
            n_img += 1
            continue
        saved = False
        for url in pick_urls(name):
            ext = ".png" if ".png" in url.split("?")[0].lower() else ".jpg"
            dest = IMG / f"{slug}{ext}"
            if dest.exists() or download_image(url, dest):
                rec.update({
                    "key": key, "slug": slug, "name": name,
                    "pos": r.get("pos") or "", "team": r.get("team") or "",
                    "image": f"img/bk-players/{dest.name}",
                })
                if r.get("age") not in (None, ""):
                    rec["age"] = r["age"]
                media[key] = rec
                saved = True
                n_img += 1
                print("img", name, flush=True)
                break
        if not saved:
            rec.update({
                "key": key, "slug": slug, "name": name,
                "pos": r.get("pos") or "", "team": r.get("team") or "",
                "image": rec.get("image") or "",
            })
            media[key] = rec
            n_miss += 1
            print("NOIMG", name, flush=True)
        time.sleep(0.04)
        if (n_img + n_miss) % 25 == 0:
            OUT.write_text(json.dumps(media, indent=2))
    OUT.write_text(json.dumps(media, indent=2))
    print("bk photos", n_img, "miss", n_miss, "media", len(media))


if __name__ == "__main__":
    main()
