#!/usr/bin/env python3
"""Download MLB headshots and 2026 stats for the BaseBallKeep 300."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bb_data import bb_norm, fold, load_universe  # noqa: E402

def slugify(name: str) -> str:
    s = fold(name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "img" / "bb-players"
OUT = ROOT / "data" / "bb-media.json"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

# Prospects the 26-man roster search misses. IDs from MLB draft / High-A lists.
KNOWN_IDS = {
    "cam caminiti": 807284,
    "caden scarborough": 807291,
    "michael forret": 702650,
    "kendry chourio": 830402,
}


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url, timeout=60):
    return json.loads(get(url, timeout=timeout))


def mlb_people(season: int):
    data = get_json(f"https://statsapi.mlb.com/api/v1/sports/1/players?season={season}")
    return data.get("people") or []


def mlb_teams(season: int = 2026):
    data = get_json(f"https://statsapi.mlb.com/api/v1/teams?sportId=1&season={season}")
    out = {}
    for t in data.get("teams") or []:
        out[t["id"]] = {
            "id": t["id"],
            "name": t.get("name") or "",
            "abbr": t.get("abbreviation") or "",
            "location": t.get("locationName") or "",
        }
    return out


def mlb_stats(group: str, season: int, sport_id: int = 1):
    url = (
        "https://statsapi.mlb.com/api/v1/stats"
        f"?stats=season&group={group}&season={season}&playerPool=all&limit=2500&sportId={sport_id}"
    )
    data = get_json(url)
    out = {}
    for split in (data.get("stats") or [{}])[0].get("splits") or []:
        pid = (split.get("player") or {}).get("id")
        if not pid:
            continue
        st = split.get("stat") or {}
        if group == "hitting":
            out[pid] = {
                "g": st.get("gamesPlayed"),
                "ab": st.get("atBats"),
                "r": st.get("runs"),
                "h": st.get("hits"),
                "2b": st.get("doubles"),
                "3b": st.get("triples"),
                "hr": st.get("homeRuns"),
                "rbi": st.get("rbi"),
                "sb": st.get("stolenBases"),
                "cs": st.get("caughtStealing"),
                "bb": st.get("baseOnBalls"),
                "so": st.get("strikeOuts"),
                "avg": st.get("avg"),
                "obp": st.get("obp"),
                "slg": st.get("slg"),
                "ops": st.get("ops"),
            }
        else:
            out[pid] = {
                "g": st.get("gamesPlayed"),
                "gs": st.get("gamesStarted"),
                "w": st.get("wins"),
                "l": st.get("losses"),
                "sv": st.get("saves"),
                "hld": st.get("holds"),
                "ip": st.get("inningsPitched"),
                "so": st.get("strikeOuts"),
                "bb": st.get("baseOnBalls"),
                "hr": st.get("homeRuns"),
                "era": st.get("era"),
                "whip": st.get("whip"),
                "k9": st.get("strikeoutsPer9Inn"),
            }
    return out


def milb_book(group: str, season: int):
    """Prefer higher minors (AAA → A) when a player has no MLB line."""
    out = {}
    for sport_id, label in ((11, "AAA"), (12, "AA"), (13, "A+"), (14, "A")):
        try:
            chunk = mlb_stats(group, season, sport_id)
        except Exception as exc:
            print("milb skip", group, season, sport_id, exc)
            continue
        for pid, st in chunk.items():
            if pid not in out:
                out[pid] = {**st, "level": label}
    return out


def search_person(name: str):
    q = urllib.parse.quote(name)
    try:
        data = get_json(f"https://statsapi.mlb.com/api/v1/people/search?names={q}")
    except Exception:
        return None
    people = data.get("people") or []
    want = bb_norm(name)
    for p in people:
        if bb_norm(p.get("fullName") or "") == want:
            return p
    return people[0] if people else None


def person_by_id(pid: int):
    try:
        data = get_json(f"https://statsapi.mlb.com/api/v1/people/{int(pid)}")
    except Exception:
        return None
    people = data.get("people") or []
    return people[0] if people else None


def wiki_image(name: str) -> str:
    titles = [name, f"{name} (baseball)", f"{name} (baseball pitcher)"]
    try:
        q = urllib.parse.quote(name + " baseball")
        data = get_json(
            "https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={q}&format=json&srlimit=3"
        )
        titles.extend(x.get("title") or "" for x in (data.get("query") or {}).get("search") or [])
    except Exception:
        pass
    seen = set()
    for title in titles:
        t = (title or "").strip()
        if not t or t in seen:
            continue
        seen.add(t)
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(t.replace(" ", "_"))
        try:
            data = get_json(url)
        except Exception:
            continue
        src = ((data.get("thumbnail") or {}).get("source")
               or ((data.get("originalimage") or {}).get("source")))
        if src and "wikipedia" in src:
            return src
    return ""


def slim_person(p, teams):
    team = p.get("currentTeam") or {}
    tid = team.get("id")
    tinfo = teams.get(tid) or {}
    bats = (p.get("batSide") or {}).get("code") or ""
    throws = (p.get("pitchHand") or {}).get("code") or ""
    pos = ((p.get("primaryPosition") or {}).get("abbreviation")) or ""
    return {
        "mlb_id": p.get("id"),
        "full_name": p.get("fullName") or "",
        "number": p.get("primaryNumber") or "",
        "bats": bats,
        "throws": throws,
        "height": p.get("height") or "",
        "weight": p.get("weight") or "",
        "age": p.get("currentAge") or "",
        "birth": p.get("birthDate") or "",
        "birth_city": p.get("birthCity") or "",
        "birth_country": p.get("birthCountry") or "",
        "debut": p.get("mlbDebutDate") or "",
        "draft": p.get("draftYear") or "",
        "pos": pos,
        "team": tinfo.get("abbr") or "",
        "team_name": tinfo.get("name") or team.get("name") or "",
        "active": bool(p.get("active")),
    }


def save_jpeg(raw: bytes, dest: Path) -> bool:
    if len(raw) < 1200 or raw[:10].lower().startswith(b"<!doctype"):
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(BytesIO(raw)).convert("RGBA")
        bg = Image.new("RGB", im.size, (11, 31, 58))
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        bg.thumbnail((420, 420), Image.Resampling.LANCZOS)
        bg.save(dest, "JPEG", quality=84, optimize=True)
        return dest.stat().st_size > 800
    except Exception:
        dest.write_bytes(raw)
        return dest.stat().st_size > 800


def download_headshot(mlb_id: int, dest: Path) -> bool:
    urls = [
        f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:silo:current.png/w_426,q_auto:best/v1/people/{mlb_id}/headshot/silo/current",
        f"https://midfield.mlbstatic.com/v1/people/{mlb_id}/spots/240",
        f"https://a.espncdn.com/i/headshots/mlb/players/full/{mlb_id}.png",
    ]
    for url in urls:
        try:
            raw = get(url, timeout=20)
            # MLB CDN serves a stock silhouette when no photo exists.
            if len(raw) < 9000:
                continue
            if save_jpeg(raw, dest):
                import hashlib
                digest = hashlib.md5(dest.read_bytes()).hexdigest()
                if digest == "f5d32ad2d885b9b407e483bcfd6b6735":
                    dest.unlink(missing_ok=True)
                    continue
                return True
        except Exception:
            continue
    return False


def index_people(people, teams):
    by_key = {}
    for p in people:
        k = bb_norm(p.get("fullName") or "")
        if not k:
            continue
        rec = slim_person(p, teams)
        prev = by_key.get(k)
        if not prev or (rec.get("active") and not prev.get("active")):
            by_key[k] = rec
    return by_key


def main():
    missing_only = "--missing-only" in sys.argv
    universe = load_universe()
    keep = universe["keep"]
    print("keep", len(keep))
    teams = mlb_teams(2026)
    people = mlb_people(2026) + mlb_people(2025)
    by_key = index_people(people, teams)
    hit = mlb_stats("hitting", 2026)
    pit = mlb_stats("pitching", 2026)
    hit25 = mlb_stats("hitting", 2025)
    pit25 = mlb_stats("pitching", 2025)
    hit_m = milb_book("hitting", 2026)
    pit_m = milb_book("pitching", 2026)

    media = {}
    if OUT.exists():
        media = json.loads(OUT.read_text())

    IMG.mkdir(parents=True, exist_ok=True)
    n_img = n_search = n_miss = 0
    for r in keep:
        key = r["key"]
        slug = slugify(r["name"])
        rec = media.get(key) or {}
        dest = IMG / f"{slug}.jpg"
        if missing_only and rec.get("image") and dest.exists() and dest.stat().st_size > 800:
            continue
        person = by_key.get(key)
        if not person:
            known = KNOWN_IDS.get(key)
            found = person_by_id(known) if known else None
            if not found:
                found = search_person(r["name"])
                n_search += 1
                time.sleep(0.12)
            if found:
                person = slim_person(found, teams)
                print("search", r["name"], "->", person.get("full_name"), person.get("mlb_id"))
        dest = IMG / f"{slug}.jpg"
        image = rec.get("image") or ""
        if dest.exists() and dest.stat().st_size > 800:
            image = f"img/bb-players/{slug}.jpg"
        if person and person.get("mlb_id"):
            pid = int(person["mlb_id"])
            if not image and download_headshot(pid, dest):
                image = f"img/bb-players/{slug}.jpg"
                n_img += 1
                print("img", r["name"], pid)
            elif not image:
                print("NOIMG", r["name"], pid)
            rec.update(person)
            rec["hit"] = hit.get(pid) or hit_m.get(pid) or {}
            rec["pit"] = pit.get(pid) or pit_m.get(pid) or {}
            rec["hit_2025"] = hit25.get(pid) or {}
            rec["pit_2025"] = pit25.get(pid) or {}
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
        })
        media[key] = rec
        if len(media) % 50 == 0:
            OUT.write_text(json.dumps(media, indent=2, default=str))

    OUT.write_text(json.dumps(media, indent=2, default=str))
    have = sum(1 for v in media.values() if v.get("image"))
    print("done", len(media), "photos", have, "new", n_img, "search", n_search, "noid", n_miss)


if __name__ == "__main__":
    main()
