#!/usr/bin/env python3
"""Hourly BK News scrape.

Efficiency:
  1. Always pull a small set of league RSS wires (one GET each).
  2. Run a fixed handful of Google News topic queries (injury, roster, coach).
  3. Pull X and YouTube via Google News `site:` filters — no login, no scrape of x.com HTML.
  4. Rotate ~8 Keep player queries per hour so the full desk is covered daily without
     hammering search engines.
  5. Hash every item; skip URLs already in data/news/state.json.
  6. Cluster leftover items into stories and merge into the existing sport JSON.

Football is published to the site. Baseball uses the same pipeline but is held
from the public nav until PUBLISH_BASEBALL_NEWS is flipped in build_site.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_algo import (  # noqa: E402
    _same_cluster,
    build_player_index,
    categorize,
    cluster_items,
    iso,
    item_hash,
    match_players,
    merge_story,
    player_query_slice,
    prune_seen,
    prune_stories,
    publisher_from_url,
    source_kind,
    split_google_title,
    strip_tags,
    utcnow,
)

UA = "Mozilla/5.0 (compatible; BallKeepNews/1.0; +https://ballkeep.com)"
TIMEOUT = 12
NEWS_DIR = ROOT / "data" / "news"
STATE_PATH = NEWS_DIR / "state.json"

FOOTBALL_FEEDS = [
    ("ESPN NFL", "https://www.espn.com/espn/rss/nfl/news"),
    ("CBS NFL", "https://www.cbssports.com/rss/headlines/nfl/"),
    ("Yahoo NFL", "https://sports.yahoo.com/nfl/rss.xml"),
    ("PFT", "https://www.nbcsports.com/nfl/profootballtalk/rss"),
    ("PFT feed", "https://profootballtalk.nbcsports.com/feed/"),
    ("FantasyPros", "https://www.fantasypros.com/feed/"),
    ("RotoWire NFL", "https://www.rotowire.com/rss/news.php?sport=NFL"),
]

BASEBALL_FEEDS = [
    ("ESPN MLB", "https://www.espn.com/espn/rss/mlb/news"),
    ("CBS MLB", "https://www.cbssports.com/rss/headlines/mlb/"),
    ("Yahoo MLB", "https://sports.yahoo.com/mlb/rss.xml"),
    ("RotoWire MLB", "https://www.rotowire.com/rss/news.php?sport=MLB"),
]

FOOTBALL_TOPICS = [
    "NFL injury report",
    "NFL injured reserve OR IR",
    "NFL roster cut OR waived OR signed",
    "NFL coach press conference OR told reporters",
    "NFL practice report DNP OR limited",
    "NFL trade",
]

BASEBALL_TOPICS = [
    "MLB injury IL injured",
    "MLB roster called up optioned DFA",
    "MLB manager told reporters",
    "MLB trade deadline OR traded",
]

X_QUERIES_FOOTBALL = [
    "NFL (injury OR IR OR questionable) site:x.com",
    "NFL (waived OR signed OR roster) site:x.com",
    "NFL (coach OR presser) site:x.com",
]
X_QUERIES_BASEBALL = [
    "MLB (IL OR injured) site:x.com",
    "MLB (DFA OR optioned OR called up) site:x.com",
]
VIDEO_QUERIES_FOOTBALL = [
    "NFL injury OR coach site:youtube.com",
]
VIDEO_QUERIES_BASEBALL = [
    "MLB injury OR manager site:youtube.com",
]

Fetcher = Callable[[str], str | None]


def google_news_url(query: str) -> str:
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def default_fetch(url: str) -> str | None:
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"  skip {url} ({exc.__class__.__name__})")
        return None


def parse_feed(xml_text: str, fallback_publisher: str = "") -> list[dict]:
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    for node in root.findall("./channel/item"):
        items.append(_rss_item(node, fallback_publisher))
    for node in root.findall("atom:entry", ns) or root.findall("{http://www.w3.org/2005/Atom}entry"):
        items.append(_atom_item(node, fallback_publisher))
    return [it for it in items if it.get("title") and it.get("url")]


def _text(node, tag: str) -> str:
    child = node.find(tag)
    if child is None:
        child = node.find(f"{{*}}{tag.split('}')[-1] if '}' in tag else tag}")
    if child is None:
        return ""
    return (child.text or "").strip()


def _rss_item(node, fallback_publisher: str) -> dict:
    title = _text(node, "title")
    link = _text(node, "link")
    desc = _text(node, "description") or _text(node, "content:encoded")
    pub = _text(node, "pubDate")
    source_el = node.find("source")
    publisher = ""
    if source_el is not None:
        publisher = (source_el.text or "").strip()
        href = source_el.attrib.get("url") or ""
        if href and (not link or "news.google.com" in link):
            # Keep Google link (it works) but prefer publisher name.
            pass
    head, gpub = split_google_title(title)
    publisher = publisher or gpub or fallback_publisher or publisher_from_url(link)
    extra = _related_from_description(desc)
    return {
        "title": head,
        "url": link,
        "summary": strip_tags(desc)[:600],
        "published": pub,
        "publisher": publisher,
        "related": extra,
    }


def _atom_item(node, fallback_publisher: str) -> dict:
    title = _text(node, "{http://www.w3.org/2005/Atom}title") or _text(node, "title")
    link = ""
    for el in list(node):
        if el.tag.endswith("link"):
            href = el.attrib.get("href") or ""
            rel = el.attrib.get("rel", "alternate")
            if href and rel in ("alternate", ""):
                link = href
                break
            if href and not link:
                link = href
    summary = _text(node, "{http://www.w3.org/2005/Atom}summary") or _text(node, "summary")
    published = _text(node, "{http://www.w3.org/2005/Atom}published") or _text(node, "published") or _text(node, "updated")
    head, gpub = split_google_title(title)
    return {
        "title": head,
        "url": link,
        "summary": strip_tags(summary)[:600],
        "published": published,
        "publisher": gpub or fallback_publisher or publisher_from_url(link),
        "related": [],
    }


def _related_from_description(desc: str) -> list[dict]:
    """Google News packs related story anchors into the description HTML."""
    out = []
    for m in re_find_anchors(desc or ""):
        href, label = m
        if href and label:
            out.append({"title": strip_tags(label), "url": href})
    return out[:6]


def re_find_anchors(html_text: str) -> list[tuple[str, str]]:
    return re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_text, flags=re.I | re.S)


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return default


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def load_roster() -> list[dict]:
    path = ROOT / "data" / "player_roster.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else []


def enrich_item(raw: dict, index: dict, sport: str) -> dict:
    title = raw.get("title") or ""
    summary = raw.get("summary") or ""
    blob = f"{title} {summary}"
    players = match_players(blob, index) if index else []
    url = raw.get("url") or ""
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "published": raw.get("published") or "",
        "publisher": raw.get("publisher") or publisher_from_url(url),
        "category": categorize(blob),
        "players": players,
        "kind": source_kind(url, title, raw.get("publisher") or ""),
        "sport": sport,
        "hash": item_hash(url, title),
    }


def collect_sport(
    sport: str,
    roster: list[dict],
    state: dict,
    fetch: Fetcher,
    sleep_s: float = 0.35,
    now: datetime | None = None,
) -> list[dict]:
    now = now or utcnow()
    index = build_player_index(roster if sport == "football" else [])
    seen = state.setdefault("seen", {}).setdefault(sport, {})
    feeds = FOOTBALL_FEEDS if sport == "football" else BASEBALL_FEEDS
    topics = FOOTBALL_TOPICS if sport == "football" else BASEBALL_TOPICS
    xq = X_QUERIES_FOOTBALL if sport == "football" else X_QUERIES_BASEBALL
    vq = VIDEO_QUERIES_FOOTBALL if sport == "football" else VIDEO_QUERIES_BASEBALL

    jobs: list[tuple[str, str]] = [(name, url) for name, url in feeds]
    for q in topics:
        jobs.append((f"topic:{q}", google_news_url(q)))
    for q in xq:
        jobs.append((f"x:{q}", google_news_url(q)))
    for q in vq:
        jobs.append((f"video:{q}", google_news_url(q)))
    if sport == "football":
        for p in player_query_slice(roster, now, size=8):
            q = f'"{p["name"]}" NFL (injury OR roster OR coach OR IR OR practice)'
            jobs.append((f"player:{p['name']}", google_news_url(q)))

    fresh = []
    for i, (label, url) in enumerate(jobs):
        xml_text = fetch(url)
        if i and sleep_s:
            time.sleep(sleep_s)
        if not xml_text:
            continue
        parsed = parse_feed(xml_text, fallback_publisher=label.split(":")[0])
        print(f"  {label}: {len(parsed)} items")
        for raw in parsed:
            item = enrich_item(raw, index, sport)
            title = item.get("title") or ""
            if len(title) < 18 or re.match(r"^(read more|watch now|subscribe)", title, re.I):
                continue
            if item["hash"] in seen:
                continue
            # Skip generic off-topic if football query returned NBA etc.
            blob = f"{item['title']} {item['summary']}".lower()
            if sport == "football" and re.search(r"\b(mlb|baseball)\b", blob) and not re.search(r"\bnfl\b", blob):
                continue
            if sport == "baseball" and "nfl" in blob and "mlb" not in blob:
                continue
            seen[item["hash"]] = iso(now)
            fresh.append(item)
            for rel in raw.get("related") or []:
                r = enrich_item({**rel, "published": raw.get("published"), "publisher": ""}, index, sport)
                if r["hash"] in seen or not r.get("url"):
                    continue
                seen[r["hash"]] = iso(now)
                fresh.append(r)
    return fresh


def fold_into_stories(sport: str, fresh: list[dict], previous: list[dict]) -> list[dict]:
    if not fresh:
        return prune_stories(previous)
    clusters = cluster_items(fresh)
    stories = list(previous)
    for group in clusters:
        existing = None
        for s in stories:
            probe = {
                "title": s.get("headline") or "",
                "players": s.get("players") or [],
                "category": s.get("category") or "wire",
                "published": s.get("updated") or s.get("published") or "",
            }
            if _same_cluster(group[0], probe, 48.0):
                existing = s
                break
        merged = merge_story(existing, group, sport)
        if existing:
            stories = [merged if x is existing else x for x in stories]
        else:
            stories.append(merged)
    return prune_stories(stories)


def run(sport: str, fetch: Fetcher = default_fetch, sleep_s: float = 0.35) -> dict:
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    state = load_json(STATE_PATH, {"seen": {}, "runs": {}})
    roster = load_roster() if sport == "football" else []
    dest = NEWS_DIR / f"{sport}.json"
    prev_doc = load_json(dest, {"sport": sport, "updated": "", "stories": []})
    previous = prev_doc.get("stories") or []

    print(f"BK News scrape: {sport}")
    fresh = collect_sport(sport, roster, state, fetch, sleep_s=sleep_s)
    stories = fold_into_stories(sport, fresh, previous)
    doc = {
        "sport": sport,
        "updated": iso(utcnow()),
        "fresh": len(fresh),
        "stories": stories,
    }
    save_json(dest, doc)
    state.setdefault("runs", {})[sport] = {
        "at": doc["updated"],
        "fresh": len(fresh),
        "stories": len(stories),
    }
    state["seen"][sport] = prune_seen(state.get("seen", {}).get(sport, {}))
    save_json(STATE_PATH, state)
    print(f"  fresh {len(fresh)} stories {len(stories)} -> {dest}")
    return doc


def main():
    ap = argparse.ArgumentParser(description="Scrape BK News wires into data/news/")
    ap.add_argument("--sport", choices=("football", "baseball", "both"), default="both")
    ap.add_argument("--sleep", type=float, default=0.35)
    args = ap.parse_args()
    sports = ["football", "baseball"] if args.sport == "both" else [args.sport]
    for sport in sports:
        run(sport, sleep_s=args.sleep)


if __name__ == "__main__":
    main()
