#!/usr/bin/env python3
"""Match Ball Keep players to headshots and a 2025/college highlight video."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "img" / "players"
OUT = ROOT / "data" / "player_media.json"
SLEEPER = Path("/tmp/bk/sleeper_nfl.json")
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

ROOKIE_KEYS = {
    "jeremiyah love", "fernando mendoza", "carnell tate", "jordyn tyson",
    "makai lemon", "jadarian price", "kc concepcion", "ty simpson",
    "kenyon sadiq", "eli stowers", "omar cooper", "jonah coleman",
    "denzel boston", "antonio williams", "nick singleton", "germie bernard",
    "chris bell", "dezhaun stribling", "de zhaun stribling", "carson beck",
    "kaytron allen",
}

COLLEGE = {
    "jeremiyah love": "Notre Dame",
    "fernando mendoza": "Indiana",
    "carnell tate": "Ohio State",
    "jordyn tyson": "Arizona State",
    "makai lemon": "USC",
    "jadarian price": "Notre Dame",
    "kc concepcion": "Texas A&M",
    "ty simpson": "Alabama",
    "kenyon sadiq": "Oregon",
    "eli stowers": "Vanderbilt",
    "omar cooper": "Indiana",
    "jonah coleman": "Washington",
    "denzel boston": "Washington",
    "antonio williams": "Clemson",
    "nick singleton": "Penn State",
    "germie bernard": "Alabama",
    "chris bell": "Louisville",
    "dezhaun stribling": "Mississippi State",
    "carson beck": "Miami",
    "kaytron allen": "Penn State",
}


def norm_name(name: str) -> str:
    n = name.lower()
    n = n.replace(".", " ")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = n.replace("'", "").replace("’", "")
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "patrick mahomes ii": "patrick mahomes",
        "james cook iii": "james cook",
        "kenneth walker iii": "kenneth walker",
        "luther burden iii": "luther burden",
        "brian thomas jr": "brian thomas",
        "omar cooper jr": "omar cooper",
        "marvin harrison jr": "marvin harrison",
        "kyle pitts sr": "kyle pitts",
        "travis etienne jr": "travis etienne",
        "dandre swift": "dandre swift",
        "devon achane": "devon achane",
        "de'von achane": "devon achane",
        "amon ra st brown": "amon-ra st brown",
        "ja marr chase": "jamarr chase",
        "harold fannin jr": "harold fannin",
        "de zhaun stribling": "dezhaun stribling",
        "kc concepcion": "kc concepcion",
    }
    return aliases.get(n, n)


def age_from_sleeper(p) -> str | int:
    birth = p.get("birth_date") or ""
    if birth:
        try:
            y, m, d = [int(x) for x in str(birth)[:10].split("-")]
            today = date(2026, 8, 20)
            return today.year - y - ((today.month, today.day) < (m, d))
        except Exception:
            pass
    age = p.get("age")
    return age if age not in (None, "") else ""


def ensure_sleeper() -> bool:
    SLEEPER.parent.mkdir(parents=True, exist_ok=True)
    if SLEEPER.exists() and SLEEPER.stat().st_size > 50_000:
        return True
    print("downloading sleeper nfl players...")
    try:
        data = get("https://api.sleeper.app/v1/players/nfl", timeout=120)
        if len(data) < 50_000:
            print("sleeper payload too small", len(data))
            return False
        SLEEPER.write_bytes(data)
        return True
    except Exception as e:
        print("sleeper download failed", e)
        return False


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", norm_name(name))
    return s.strip("-")


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def post_json(url, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def sleeper_index():
    raw = json.loads(SLEEPER.read_text())
    by_name = {}
    for pid, p in raw.items():
        if not isinstance(p, dict):
            continue
        fn = p.get("full_name") or " ".join(filter(None, [p.get("first_name"), p.get("last_name")]))
        if not fn:
            continue
        key = norm_name(fn)
        pos = p.get("position") or ""
        team = p.get("team") or ""
        score = 0
        if p.get("active"):
            score += 2
        if p.get("espn_id"):
            score += 1
        rec = {
            "sleeper_id": pid,
            "espn_id": str(p.get("espn_id") or ""),
            "name": fn,
            "pos": pos,
            "team": team,
            "college": p.get("college") or "",
            "age": age_from_sleeper(p),
            "birth_date": p.get("birth_date") or "",
            "years_exp": p.get("years_exp"),
            "score": score,
        }
        prev = by_name.get(key)
        if not prev or rec["score"] > prev["score"]:
            by_name[key] = rec
    return by_name


def download_image(url, dest: Path) -> bool:
    try:
        data = get(url)
        if len(data) < 800 or data[:10].lower().startswith(b"<!doctype") or data[:5] == b"<?xml":
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def yt_search(query: str):
    data = post_json(
        "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
        {
            "context": {"client": {"clientName": "WEB", "clientVersion": "2.20240815.00.00"}},
            "query": query,
        },
    )
    items = (
        data.get("contents", {})
        .get("twoColumnSearchResultsRenderer", {})
        .get("primaryContents", {})
        .get("sectionListRenderer", {})
        .get("contents", [])
    )
    videos = []
    for section in items:
        for it in section.get("itemSectionRenderer", {}).get("contents", []):
            vr = it.get("videoRenderer")
            if not vr or not vr.get("videoId"):
                continue
            title = ""
            runs = (vr.get("title") or {}).get("runs") or []
            if runs:
                title = runs[0].get("text") or ""
            channel = ""
            by = (vr.get("longBylineText") or {}).get("runs") or []
            if by:
                channel = by[0].get("text") or ""
            length = ((vr.get("lengthText") or {}).get("simpleText")) or ""
            videos.append({
                "id": vr["videoId"],
                "title": title,
                "channel": channel,
                "length": length,
            })
    return videos


def length_seconds(txt: str) -> int:
    if not txt:
        return 10**9
    parts = txt.replace(".", "").replace(" minutes", ":00").replace(" minute", ":00")
    # "51 minutes" already handled poorly; parse H:M:S or M:S
    m = re.match(r"(?:(\d+)\s*minutes?)|(?:(\d+):(\d+)(?::(\d+))?)", txt.strip(), re.I)
    if not m:
        return 10**9
    if m.group(1):
        return int(m.group(1)) * 60
    if m.group(4) is not None:
        return int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
    return int(m.group(2)) * 60 + int(m.group(3))


def pick_video(name, key, pos, team, videos):
    last = name.split()[-1].lower()
    first = name.split()[0].lower()
    is_rook = key in ROOKIE_KEYS
    scored = []
    for v in videos:
        t = (v["title"] + " " + v["channel"]).lower()
        if last not in t and first not in t:
            continue
        score = 0
        if "nfl" in v["channel"].lower() or v["channel"].lower().endswith("football"):
            score += 8
        if any(x in t for x in ("can't-miss", "cant-miss", "can't miss", "best play", "top play")):
            score += 12
        if "2025" in t:
            score += 10
        if "highlight" in t:
            score += 6
        if is_rook and any(x in t for x in ("college", "ncaa", "notre dame", "ohio state", "alabama", "usc", "indiana")):
            score += 8
        if not is_rook and any(x in t for x in ("college", "ncaa", "commit")):
            score -= 4
        if any(x in t for x in ("mix", "edit", "slow motion", "mad city", "song")):
            score -= 6
        sec = length_seconds(v["length"])
        if 15 <= sec <= 180:
            score += 9
        elif 181 <= sec <= 600:
            score += 5
        elif sec > 2400:
            score -= 4
        scored.append((score, sec, v))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][2] if scored else (videos[0] if videos else None)


def espn_search_headshot(name, league="nfl"):
    q = urllib.parse.quote(name)
    url = f"https://site.web.api.espn.com/apis/common/v3/search?query={q}&limit=8&type=player"
    try:
        data = json.loads(get(url))
    except Exception:
        return ""
    items = (((data.get("items") or [{}])[0]).get("contents") if False else None)
    # structure varies; walk
    found = []
    def walk(o):
        if isinstance(o, dict):
            img = o.get("image") or o.get("headshot") or ""
            if isinstance(img, dict):
                img = img.get("href") or img.get("url") or ""
            display = o.get("displayName") or o.get("name") or ""
            if img and "headshot" in str(img) and display:
                found.append((display, img))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o[:40]:
                walk(v)
    walk(data)
    want = norm_name(name)
    for display, img in found:
        if norm_name(display) == want:
            return img
    return found[0][1] if found else ""


def wiki_thumb(name):
    title = urllib.parse.quote(name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        data = json.loads(get(url, timeout=15))
        src = ((data.get("thumbnail") or {}).get("source")) or ((data.get("originalimage") or {}).get("source"))
        return src or ""
    except Exception:
        return ""


def main():
    photos_only = "--photos-only" in sys.argv
    keep_only = "--keep-only" in sys.argv
    roster = json.loads((ROOT / "data" / "player_roster.json").read_text())
    if keep_only:
        roster = [p for p in roster if "The Keep" in (p.get("lists") or {})]
    ensure_sleeper()
    sleep_idx = sleeper_index() if SLEEPER.exists() else {}
    media = {}
    if OUT.exists():
        media = json.loads(OUT.read_text())

    IMG.mkdir(parents=True, exist_ok=True)
    n_img = n_age = n_miss = 0
    for i, p in enumerate(roster, 1):
        key = p["key"]
        slug = p["slug"]
        name = p["name"]
        rec = media.get(key, {})
        rec.update({
            "key": key, "slug": slug, "name": name, "pos": p["pos"], "team": p["team"],
            "is_rookie": key in ROOKIE_KEYS, "college": COLLEGE.get(key, rec.get("college", "")),
        })

        sp = sleep_idx.get(key)
        if not sp:
            # last-name + team fallback among sleeper rows
            last = key.split()[-1] if key else ""
            team = (p.get("team") or "").upper()
            hits = [
                v for v in sleep_idx.values()
                if last and last in (v.get("name") or "").lower()
                and (not team or (v.get("team") or "").upper() == team)
                and (v.get("pos") or "") == (p.get("pos") or "")
            ]
            if len(hits) == 1:
                sp = hits[0]
        if sp:
            rec["sleeper_id"] = sp["sleeper_id"]
            rec["espn_id"] = sp.get("espn_id") or rec.get("espn_id") or ""
            if sp.get("college"):
                rec["college"] = rec.get("college") or sp["college"]
            if sp.get("age") not in (None, ""):
                rec["age"] = sp["age"]
                n_age += 1
            elif p.get("age") not in (None, ""):
                rec["age"] = p["age"]
        elif p.get("age") not in (None, "") and rec.get("age") in (None, ""):
            rec["age"] = p["age"]

        dest = IMG / f"{slug}.jpg"
        png = IMG / f"{slug}.png"
        if not dest.exists() and png.exists():
            dest = png
        have_file = dest.exists() or png.exists()
        if have_file:
            rec["image"] = f"img/players/{dest.name if dest.exists() else png.name}"
        else:
            urls = []
            if rec.get("espn_id"):
                urls.append(f"https://a.espncdn.com/i/headshots/nfl/players/full/{rec['espn_id']}.png")
            if rec.get("sleeper_id"):
                urls.append(f"https://sleepercdn.com/content/nfl/players/{rec['sleeper_id']}.jpg")
            saved = False
            for u in urls:
                ext = ".png" if ".png" in u.split("?")[0].lower() else ".jpg"
                target = IMG / f"{slug}{ext}"
                if download_image(u, target):
                    rec["image"] = f"img/players/{slug}{ext}"
                    saved = True
                    n_img += 1
                    print("img", name, u[:80])
                    break
            if not saved:
                extras = []
                espn = espn_search_headshot(name)
                if espn:
                    extras.append(espn)
                wiki = wiki_thumb(name)
                if wiki:
                    extras.append(wiki)
                if key in COLLEGE:
                    for title in (f"{name} (American football)", f"{name} football"):
                        wiki2 = wiki_thumb(title)
                        if wiki2:
                            extras.append(wiki2)
                for u in extras:
                    ext = ".png" if ".png" in u.split("?")[0].lower() else ".jpg"
                    target = IMG / f"{slug}{ext}"
                    if download_image(u, target):
                        rec["image"] = f"img/players/{slug}{ext}"
                        saved = True
                        n_img += 1
                        print("img", name, u[:80])
                        break
            if not saved:
                rec["image"] = rec.get("image") or ""
                n_miss += 1
                print("NOIMG", name)
            time.sleep(0.05)

        if not photos_only and not rec.get("youtube_id"):
            is_rook = key in ROOKIE_KEYS
            college = rec.get("college") or COLLEGE.get(key, "")
            if is_rook:
                queries = [
                    f'{name} {college} 2025 highlight',
                    f'{name} 2025 college football touchdown',
                    f'{name} {college} football highlights',
                ]
            else:
                queries = [
                    f'{name} 2025 Can\'t-Miss Play',
                    f'{name} 2025 NFL highlight touchdown',
                    f'{name} 2025 season highlights',
                ]
            picked = None
            for q in queries:
                try:
                    vids = yt_search(q)
                except Exception as e:
                    print("YTERR", name, e)
                    time.sleep(1)
                    continue
                picked = pick_video(name, key, p["pos"], p["team"], vids)
                if picked:
                    break
                time.sleep(0.25)
            if picked:
                rec["youtube_id"] = picked["id"]
                rec["youtube_title"] = picked["title"]
                rec["youtube_channel"] = picked["channel"]
                print("yt", name, picked["id"], picked["title"][:70])
            else:
                rec["youtube_id"] = ""
                print("NOYT", name)
            time.sleep(0.35)

        media[key] = rec
        if i % 25 == 0:
            OUT.write_text(json.dumps(media, indent=2))
            print("progress", i, "/", len(roster), "photos", sum(1 for v in media.values() if v.get("image")))

    OUT.write_text(json.dumps(media, indent=2))
    have = sum(1 for v in media.values() if v.get("image"))
    aged = sum(1 for v in media.values() if v.get("age") not in (None, ""))
    print("done", len(media), "photos", have, "new", n_img, "ages", aged, "noimg", n_miss)


if __name__ == "__main__":
    main()
