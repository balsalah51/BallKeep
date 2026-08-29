#!/usr/bin/env python3
"""Download MLB headshots for The Farm (top 100 prospects)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bb_prospects import load_farm  # noqa: E402
from fetch_bb_media import (  # noqa: E402
    IMG,
    KNOWN_IDS,
    download_headshot,
    get,
    mlb_teams,
    person_by_id,
    save_jpeg,
    search_person,
    slim_person,
    slugify,
    wiki_image,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bb-prospect-media.json"

# IDs the 26-man roster search misses. Pipeline / draft / High-A lists.
FARM_IDS = {
    "jesus made": 815908,
    "leo de vries": 815888,
    "franklin arias": 808265,
    "max clark": 703601,
    "eli willits": 805339,
    "kade anderson": 805340,
    "josue de paula": 805273,
    "sebastian walcott": 805274,
    "ethan salas": 805275,
    "walker jenkins": 691176,
    "george lombard jr": 805276,
    "theo gillen": 805277,
}


def main():
    farm = load_farm()
    print("farm", len(farm))
    teams = mlb_teams(2026)
    media = {}
    if OUT.exists():
        media = json.loads(OUT.read_text())
    IMG.mkdir(parents=True, exist_ok=True)
    n_img = n_search = n_miss = 0
    for r in farm:
        key = r["key"]
        slug = slugify(r["name"])
        rec = media.get(key) or {}
        dest = IMG / f"{slug}.jpg"
        person = None
        pid = rec.get("mlb_id") or FARM_IDS.get(key) or KNOWN_IDS.get(key)
        if pid:
            found = person_by_id(int(pid))
            if found:
                person = slim_person(found, teams)
        if not person:
            found = search_person(r["name"])
            n_search += 1
            time.sleep(0.12)
            if found:
                person = slim_person(found, teams)
                print("search", r["name"], "->", person.get("full_name"), person.get("mlb_id"))
        image = rec.get("image") or ""
        if dest.exists() and dest.stat().st_size > 800:
            image = f"img/bb-players/{slug}.jpg"
        if person and person.get("mlb_id"):
            pid = int(person["mlb_id"])
            if (not image or not dest.exists()) and download_headshot(pid, dest):
                image = f"img/bb-players/{slug}.jpg"
                n_img += 1
                print("img", r["name"], pid)
            rec.update(person)
        else:
            n_miss += 1
            print("NOID", r["name"])
        if not image:
            wiki = wiki_image(r["name"])
            if wiki:
                try:
                    if save_jpeg(get(wiki, timeout=20), dest):
                        image = f"img/bb-players/{slug}.jpg"
                        n_img += 1
                        print("wiki", r["name"])
                except Exception:
                    pass
        rec.update({
            "key": key,
            "slug": slug,
            "name": r["name"],
            "image": image,
            "eta": r.get("eta") or "",
            "path": r.get("path") or "",
            "level": r.get("level") or "",
            "mlb_g": r.get("mlb_g") or 0,
        })
        media[key] = rec
    OUT.write_text(json.dumps(media, indent=2, default=str))
    have = sum(1 for v in media.values() if v.get("image"))
    print("done", len(media), "photos", have, "new", n_img, "search", n_search, "noid", n_miss)


if __name__ == "__main__":
    main()
