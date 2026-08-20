#!/usr/bin/env python3
"""Download Premier League headshots and a highlight clip for The Pitch 250."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pl_data import fold, load_universe  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "img" / "pl-players"
OUT = ROOT / "data" / "pl-media.json"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"


def slugify(name: str) -> str:
    s = fold(name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
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


def save_jpeg(raw: bytes, dest: Path) -> bool:
    if len(raw) < 1500 or raw[:10].lower().startswith(b"<!doctype"):
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(BytesIO(raw)).convert("RGBA")
        bg = Image.new("RGB", im.size, (55, 0, 60))
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        bg.thumbnail((420, 420), Image.Resampling.LANCZOS)
        bg.save(dest, "JPEG", quality=84, optimize=True)
        return dest.stat().st_size > 800
    except Exception:
        dest.write_bytes(raw)
        return dest.stat().st_size > 800


def download_headshot(code, dest: Path) -> bool:
    code = str(code or "").replace(".png", "").replace(".jpg", "")
    if not code:
        return False
    urls = [
        f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{code}.png",
        f"https://resources.premierleague.com/premierleague25/photos/players/250x250/p{code}.png",
        f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png",
    ]
    for url in urls:
        try:
            raw = get(url, timeout=20)
            if save_jpeg(raw, dest):
                return True
        except Exception:
            continue
    return False


def wiki_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "BallKeep/1.0 (https://ballkeep.com; player-file photos)", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wiki_headshot(name: str, team: str, dest: Path) -> bool:
    titles = [name]
    folded = fold(name)
    if folded != name:
        titles.append(folded)
    titles.append(f"{name} footballer")
    if team:
        titles.append(f"{name} {team}")
    seen = set()
    for title in titles:
        if title in seen:
            continue
        seen.add(title)
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)
        try:
            data = wiki_json(url)
        except Exception:
            continue
        src = ((data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get("source") or "")
        if not src:
            continue
        src = src.split("?")[0]
        try:
            raw = get(src, timeout=20)
            if save_jpeg(raw, dest):
                return True
        except Exception:
            continue
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
    m = re.match(r"(?:(\d+)\s*minutes?)|(?:(\d+):(\d+)(?::(\d+))?)", txt.strip(), re.I)
    if not m:
        return 10**9
    if m.group(1):
        return int(m.group(1)) * 60
    if m.group(4) is not None:
        return int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
    return int(m.group(2)) * 60 + int(m.group(3))


def pick_video(name, team, videos):
    last = name.split()[-1].lower()
    first = name.split()[0].lower()
    scored = []
    for v in videos:
        t = (v["title"] + " " + v["channel"]).lower()
        if last not in t and first not in t:
            continue
        score = 0
        if any(x in t for x in ("premier league", "epl", "bpl", "pl 25", "pl 26")):
            score += 10
        if "highlight" in t or "goals" in t:
            score += 8
        if "2025" in t or "2026" in t or "25/26" in t or "26/27" in t:
            score += 8
        if team and team.lower() in t:
            score += 4
        if any(x in t for x in ("fifa", "career mode", "pack opening", "song", "edit", "slow motion")):
            score -= 8
        sec = length_seconds(v["length"])
        if 20 <= sec <= 240:
            score += 9
        elif 241 <= sec <= 720:
            score += 5
        elif sec > 2400:
            score -= 5
        scored.append((score, sec, v))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][2] if scored else (videos[0] if videos else None)


def main():
    universe = load_universe()
    pitch = universe["pitch"]
    print("pitch", len(pitch))
    media = {}
    if OUT.exists():
        media = json.loads(OUT.read_text())
    IMG.mkdir(parents=True, exist_ok=True)
    n_img = n_yt = n_miss = 0
    for i, r in enumerate(pitch, 1):
        key = r["key"]
        slug = slugify(r["name"])
        rec = media.get(key) or {}
        dest = IMG / f"{slug}.jpg"
        image = rec.get("image") or ""
        if dest.exists() and dest.stat().st_size > 800:
            image = f"img/pl-players/{slug}.jpg"
        elif download_headshot(r.get("code") or r.get("photo"), dest):
            image = f"img/pl-players/{slug}.jpg"
            n_img += 1
            print("img", r["name"])
        elif wiki_headshot(r["name"], r.get("team_name") or r.get("team") or "", dest):
            image = f"img/pl-players/{slug}.jpg"
            n_img += 1
            print("wiki", r["name"])
        else:
            n_miss += 1
            print("NOIMG", r["name"], r.get("code"))
        if not rec.get("youtube_id"):
            q = f"{r['name']} {r.get('team_name') or ''} 2025 2026 highlights premier league"
            try:
                vids = yt_search(q)
                picked = pick_video(r["name"], r.get("team") or "", vids)
                if picked:
                    rec["youtube_id"] = picked["id"]
                    rec["youtube_title"] = picked["title"]
                    rec["youtube_channel"] = picked["channel"]
                    n_yt += 1
                    print("yt", r["name"], picked["id"])
            except Exception as exc:
                print("yt fail", r["name"], exc)
            time.sleep(0.12)
        rec.update({
            "key": key,
            "slug": slug,
            "name": r["name"],
            "image": image,
        })
        media[key] = rec
        if i % 25 == 0:
            OUT.write_text(json.dumps(media, indent=2, default=str))
            print("checkpoint", i)
    OUT.write_text(json.dumps(media, indent=2, default=str))
    have = sum(1 for v in media.values() if v.get("image"))
    yts = sum(1 for v in media.values() if v.get("youtube_id"))
    print("done", len(media), "photos", have, "new", n_img, "yt", yts, "noid", n_miss)


if __name__ == "__main__":
    main()
