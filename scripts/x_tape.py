"""The X — fun tape from X/Twitter via Google News site: filters.

No login. No scrape of x.com HTML. Same cheap RSS path as BK News.
"""
from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_algo import iso, item_hash, parse_dt, publisher_from_url, strip_tags, utcnow  # noqa: E402
from news_scrape import default_fetch  # noqa: E402

OUT = ROOT / "data" / "x-tape"
UA = "Mozilla/5.0 (compatible; BallKeepX/1.0; +https://ballkeep.com)"

QUERIES = {
    "football": [
        "NFL meme site:x.com",
        "fantasy football meme site:x.com",
        "NFL shitpost OR shitposting site:x.com",
        "NFL funny video site:x.com",
        "dynasty fantasy football meme",
    ],
    "baseball": [
        "MLB meme site:x.com",
        "fantasy baseball meme site:x.com",
        "MLB shitpost site:x.com",
        "baseball funny site:x.com",
    ],
    "soccer": [
        "Premier League meme site:x.com",
        "FPL meme site:x.com",
        "Premier League shitpost site:x.com",
        "football meme Haaland OR Saka site:x.com",
    ],
}

SPORT_FACE = {
    "football": "img/logo.jpg",
    "baseball": "img/bb-logo.jpg",
    "soccer": "img/pl-logo.jpg",
}


def google_news_url(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"


def _attr(node, *names):
    for child in list(node):
        tag = child.tag.split("}")[-1]
        if tag in names:
            return (child.attrib.get("url") or child.attrib.get("href") or child.text or "").strip()
    return ""


def parse_items(xml_text: str) -> list[dict]:
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out = []
    for node in root.findall("./channel/item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        desc = node.findtext("description") or node.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or ""
        pub = node.findtext("pubDate") or ""
        img = ""
        enc = node.find("enclosure")
        if enc is not None and (enc.attrib.get("type") or "").startswith("image"):
            img = enc.attrib.get("url") or ""
        if not img:
            img = _attr(node, "content", "thumbnail")
        if not img:
            m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc or "", re.I)
            if m:
                img = m.group(1)
        source_el = node.find("source")
        publisher = (source_el.text or "").strip() if source_el is not None else ""
        head = re.sub(r"\s+-\s+[^-]+$", "", title).strip() or title
        if publisher and " - " in title:
            head, _, maybe = title.rpartition(" - ")
            publisher = publisher or maybe
        out.append({
            "title": strip_tags(head)[:180],
            "url": link,
            "summary": strip_tags(desc)[:280],
            "published": pub,
            "publisher": publisher or publisher_from_url(link) or "X",
            "image": img,
        })
    return [it for it in out if it.get("title") and it.get("url")]


def load_tape(sport: str) -> dict:
    path = OUT / f"{sport}.json"
    if not path.exists():
        return {"sport": sport, "updated": "", "posts": []}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"sport": sport, "updated": "", "posts": []}


def scrape_sport(sport: str, fetch=default_fetch, sleep_s: float = 0.3) -> dict:
    seen = set()
    posts = []
    for q in QUERIES.get(sport) or []:
        xml_text = fetch(google_news_url(q))
        if sleep_s:
            time.sleep(sleep_s)
        for raw in parse_items(xml_text or ""):
            h = item_hash(raw["url"], raw["title"])
            if h in seen or len(raw["title"]) < 12:
                continue
            blob = f"{raw['title']} {raw['summary']}".lower()
            if sport == "football" and re.search(r"\b(mlb|premier league|fpl)\b", blob) and "nfl" not in blob:
                continue
            if sport == "baseball" and "nfl" in blob and "mlb" not in blob:
                continue
            if sport == "soccer" and re.search(r"\b(nfl|mlb)\b", blob) and not re.search(r"\b(premier|fpl|soccer|football)\b", blob):
                continue
            seen.add(h)
            raw["hash"] = h
            raw["kind"] = "x" if "x.com" in (raw["url"] or "").lower() or "twitter" in (raw.get("publisher") or "").lower() else "web"
            posts.append(raw)
            if len(posts) >= 36:
                break
        if len(posts) >= 36:
            break
    posts.sort(key=lambda p: parse_dt(p.get("published") or "") or utcnow(), reverse=True)
    doc = {"sport": sport, "updated": iso(utcnow()), "posts": posts[:36]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{sport}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"The X {sport}: {len(doc['posts'])} posts")
    return doc


def cards_html(sport: str, depth: int = 0, esc=None) -> str:
    import html as html_mod
    if esc is None:
        esc = lambda s: html_mod.escape(str(s), quote=True)
    prefix = "../" * depth
    doc = load_tape(sport)
    posts = doc.get("posts") or []
    if not posts:
        return '<p class="note">The X tape is empty until the next pull. Memes come through Google News site:x.com — no login.</p>'
    bits = []
    fallback = prefix + SPORT_FACE.get(sport, "img/logo.jpg")
    for p in posts:
        img = p.get("image") or ""
        src = img if img.startswith("http") else (prefix + img if img else fallback)
        kind = "X" if p.get("kind") == "x" else (p.get("publisher") or "Web")
        bits.append(
            f'<a class="x-card tile" href="{esc(p.get("url") or "#")}" target="_blank" rel="noopener">'
            f'<img src="{esc(src)}" alt="" />'
            f'<span class="x-kind">{esc(kind)}</span>'
            f'<h3>{esc(p.get("title") or "")}</h3>'
            f'<p>{esc((p.get("summary") or "")[:140])}</p>'
            f"</a>"
        )
    return f'<div class="x-grid">{"".join(bits)}</div>'


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Pull The X meme tape")
    ap.add_argument("--sport", choices=("football", "baseball", "soccer", "all"), default="all")
    args = ap.parse_args()
    sports = ["football", "baseball", "soccer"] if args.sport == "all" else [args.sport]
    for sport in sports:
        scrape_sport(sport)


if __name__ == "__main__":
    main()
