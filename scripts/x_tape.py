"""The X — fun tape from X/Twitter via Google News site: filters.

No login. No scrape of x.com HTML. Same cheap RSS path as BK News.
Pictures are resolved (og:image / FixTweet) and saved under img/x-tape/
so the cards show the image on the site.
"""
from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_algo import iso, item_hash, parse_dt, publisher_from_url, strip_tags, utcnow  # noqa: E402
from news_scrape import default_fetch  # noqa: E402

OUT = ROOT / "data" / "x-tape"
IMG = ROOT / "img" / "x-tape"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
TIMEOUT = 14

REDDIT = {
    "football": [
        "https://www.reddit.com/r/nflmemes/.rss",
        "https://old.reddit.com/r/nflmemes/.rss",
        "https://old.reddit.com/r/nflcirclejerk/.rss",
        "https://old.reddit.com/r/fantasyfootball/.rss",
    ],
    "baseball": [
        "https://old.reddit.com/r/mlbmemes/.rss",
        "https://www.reddit.com/r/mlbmemes/.rss",
        "https://old.reddit.com/r/baseballcirclejerk/.rss",
        "https://old.reddit.com/r/baseball/.rss",
    ],
    "soccer": [
        "https://old.reddit.com/r/soccercirclejerk/.rss",
        "https://www.reddit.com/r/soccercirclejerk/.rss",
        "https://www.reddit.com/r/PremierLeague/.rss",
        "https://www.reddit.com/r/soccer/.rss",
    ],
    "basketball": [
        "https://old.reddit.com/r/nbamemes/.rss",
        "https://old.reddit.com/r/nbacirclejerk/.rss",
        "https://old.reddit.com/r/nba/.rss",
        "https://old.reddit.com/r/fantasybball/.rss",
    ],
}

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
    "basketball": [
        "NBA meme site:x.com",
        "fantasy basketball meme site:x.com",
        "NBA shitpost site:x.com",
        "basketball funny site:x.com",
    ],
}

SPORT_FACE = {
    "football": "img/logo.jpg",
    "baseball": "img/bb-logo.jpg",
    "soccer": "img/pl-logo.jpg",
    "basketball": "img/bk-logo.jpg",
}


STATUS_RE = re.compile(r"(?:twitter|x)\.com/(?:#!/)?[^/\s]+/status(?:es)?/(\d+)", re.I)
OG_RE = re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)[^>]+content=["\']([^"\']+)["\']', re.I)
OG_RE2 = re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)', re.I)
CANON_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)


def google_news_url(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"


def fetch_bytes(url: str, accept: str = "*/*") -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read(), resp.geturl()


def fetch_html(url: str) -> tuple[str, str]:
    raw, final = fetch_bytes(url, "text/html,application/xhtml+xml,application/json,*/*")
    return raw.decode("utf-8", errors="replace"), final


def save_image(raw: bytes, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(BytesIO(raw))
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        else:
            im = im.convert("RGB")
        im.thumbnail((900, 900))
        im.save(dest, "JPEG", quality=82, optimize=True)
    except Exception:
        dest.write_bytes(raw)
    if is_usable_image_file(dest):
        return True
    dest.unlink(missing_ok=True)
    return False


JUNK_TITLE_RE = re.compile(r"(?:\(@\w+\)\s*)?/\s*Posts\s*/\s*X\s*$", re.I)
BAD_IMG_HINTS = (
    "1x1", "pixel", "spacer", "logo.svg", "favicon",
    "lh3.googleusercontent.com", "encrypted-tbn",
    "gstatic.com/images", "news.google.com",
)


def looks_like_image_url(url: str) -> bool:
    u = (url or "").lower()
    if not u.startswith("http"):
        return False
    return not any(bad in u for bad in BAD_IMG_HINTS)


def is_junk_title(title: str) -> bool:
    t = (title or "").strip()
    if len(t) < 8:
        return True
    return bool(JUNK_TITLE_RE.search(t))


def is_usable_image_file(path: Path) -> bool:
    """Reject Google News icons and other site-logo placeholders saved as card art."""
    if not path.exists():
        return False
    size = path.stat().st_size
    if size < 2000:
        return False
    try:
        from PIL import Image
        im = Image.open(path)
        w, h = im.size
        if min(w, h) < 140:
            return False
        if w == 300 and h == 300 and size < 20000:
            return False
        return True
    except Exception:
        return size > 20000


def reddit_full_image(url: str) -> str:
    m = re.match(r"https://preview\.redd\.it/([^?]+)", url or "", re.I)
    if m:
        return "https://i.redd.it/" + m.group(1)
    return url or ""


def canon_post_url(url: str) -> str:
    u = (url or "").strip()
    u = re.sub(r"https://old\.reddit\.com/", "https://www.reddit.com/", u, flags=re.I)
    return u.split("?")[0]


def fxtwitter_image(status_id: str) -> str:
    try:
        raw, _ = fetch_bytes(f"https://api.fxtwitter.com/status/{status_id}", "application/json")
        data = json.loads(raw.decode("utf-8", errors="replace"))
        tweet = data.get("tweet") or data
        media = tweet.get("media") or {}
        photos = media.get("photos") or []
        if photos:
            return photos[0].get("url") or ""
        videos = media.get("videos") or media.get("video") or []
        if isinstance(videos, dict):
            videos = [videos]
        if videos:
            return (videos[0].get("thumbnail_url") or videos[0].get("url") or "")
    except Exception:
        return ""
    return ""


def page_image(url: str) -> tuple[str, str]:
    """Return (image_url, canonical_url)."""
    try:
        html_text, final = fetch_html(url)
    except Exception:
        return "", url
    m = STATUS_RE.search(html_text) or STATUS_RE.search(final)
    if m:
        pic = fxtwitter_image(m.group(1))
        if pic:
            return pic, final
    for rx in (OG_RE, OG_RE2):
        found = rx.search(html_text)
        if found and looks_like_image_url(found.group(1)):
            return found.group(1), final
    canon = CANON_RE.search(html_text)
    if canon:
        final = canon.group(1) or final
        m = STATUS_RE.search(final)
        if m:
            pic = fxtwitter_image(m.group(1))
            if pic:
                return pic, final
    return "", final


def download_pic(url: str, sport: str, hid: str) -> str:
    dest = IMG / sport / f"{hid}.jpg"
    if is_usable_image_file(dest):
        return f"img/x-tape/{sport}/{hid}.jpg"
    candidates = []
    full = reddit_full_image(url)
    if full and full != url:
        candidates.append(full)
    if url:
        candidates.append(url)
    for src in candidates:
        try:
            raw, _ = fetch_bytes(src)
        except Exception:
            continue
        if save_image(raw, dest):
            return f"img/x-tape/{sport}/{hid}.jpg"
    dest.unlink(missing_ok=True)
    return ""


def hydrate_images(posts: list[dict], sport: str) -> list[dict]:
    out = []
    lookups = 0
    for p in posts:
        hid = p.get("hash") or item_hash(p.get("url") or "", p.get("title") or "")
        p["hash"] = hid
        local = IMG / sport / f"{hid}.jpg"
        if is_usable_image_file(local):
            p["image"] = f"img/x-tape/{sport}/{hid}.jpg"
            out.append(p)
            continue
        img = p.get("image") or ""
        src = img if looks_like_image_url(img) else ""
        if not src and lookups < 40:
            lookups += 1
            src, final = page_image(p.get("url") or "")
            if final and final != p.get("url"):
                p["resolved"] = final
            if STATUS_RE.search(final or ""):
                p["kind"] = "x"
        if src:
            saved = download_pic(src, sport, hid)
            if saved:
                p["image"] = saved
                out.append(p)
                continue
        p["image"] = ""
    return out


def parse_reddit(xml_text: str) -> list[dict]:
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}
    out = []
    nodes = root.findall("atom:entry", ns) or root.findall("{http://www.w3.org/2005/Atom}entry")
    if not nodes:
        nodes = root.findall("./channel/item")
    for node in nodes:
        title = (node.findtext("{http://www.w3.org/2005/Atom}title") or node.findtext("title") or "").strip()
        link = ""
        for child in list(node):
            tag = child.tag.split("}")[-1]
            if tag == "link":
                link = (child.attrib.get("href") or child.text or "").strip()
                if link:
                    break
        if not link:
            link = (node.findtext("link") or "").strip()
        content = (
            node.findtext("{http://www.w3.org/2005/Atom}content")
            or node.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
            or node.findtext("description")
            or ""
        )
        img = ""
        thumb = node.find("{http://search.yahoo.com/mrss/}thumbnail")
        if thumb is not None:
            img = thumb.attrib.get("url") or ""
        if not img:
            m = IMG_SRC_RE.search(content)
            if m:
                img = m.group(1)
        pub = node.findtext("{http://www.w3.org/2005/Atom}updated") or node.findtext("pubDate") or ""
        if title and link:
            out.append({
                "title": strip_tags(title)[:180],
                "url": link,
                "summary": strip_tags(content)[:280],
                "published": pub,
                "publisher": "Reddit",
                "image": img,
                "kind": "meme",
            })
    return out


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

    def add(raw: dict) -> None:
        raw["url"] = canon_post_url(raw.get("url") or "")
        title = raw.get("title") or ""
        if is_junk_title(title) or not raw["url"]:
            return
        h = item_hash(raw["url"], title)
        if h in seen:
            return
        blob = f"{title} {raw.get('summary') or ''}".lower()
        if sport == "football" and re.search(r"\b(mlb|premier league|fpl)\b", blob) and "nfl" not in blob:
            return
        if sport == "baseball" and "nfl" in blob and "mlb" not in blob:
            return
        if sport == "soccer" and re.search(r"\b(nfl|mlb)\b", blob) and not re.search(r"\b(premier|fpl|soccer|football)\b", blob):
            return
        if sport == "basketball" and re.search(r"\b(nfl|mlb|premier league)\b", blob) and not re.search(r"\b(nba|basketball)\b", blob):
            return
        seen.add(h)
        raw["hash"] = h
        posts.append(raw)

    for feed in REDDIT.get(sport) or []:
        xml_text = fetch(feed)
        if sleep_s:
            time.sleep(sleep_s)
        for raw in parse_reddit(xml_text or ""):
            add(raw)
    for q in QUERIES.get(sport) or []:
        xml_text = fetch(google_news_url(q))
        if sleep_s:
            time.sleep(sleep_s)
        for raw in parse_items(xml_text or ""):
            raw["kind"] = "x" if "x.com" in (raw["url"] or "").lower() or "twitter" in (raw.get("publisher") or "").lower() else "web"
            add(raw)
            if len(posts) >= 80:
                break
        if len(posts) >= 80:
            break
    posts = hydrate_images(posts, sport)
    with_pic = []
    for p in posts:
        img = p.get("image") or ""
        if img.startswith("img/x-tape/") and is_usable_image_file(ROOT / img):
            with_pic.append(p)
        elif looks_like_image_url(img):
            with_pic.append(p)
    with_pic.sort(key=lambda p: parse_dt(p.get("published") or "") or utcnow(), reverse=True)
    have = {p.get("hash") for p in with_pic}
    for p in (load_tape(sport).get("posts") or []):
        img = p.get("image") or ""
        hid = p.get("hash") or item_hash(p.get("url") or "", p.get("title") or "")
        if hid in have:
            continue
        if img.startswith("img/x-tape/") and is_usable_image_file(ROOT / img):
            p["hash"] = hid
            with_pic.append(p)
            have.add(hid)
    with_pic.sort(key=lambda p: parse_dt(p.get("published") or "") or utcnow(), reverse=True)
    keep = with_pic[:36]
    doc = {"sport": sport, "updated": iso(utcnow()), "posts": keep}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{sport}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"The X {sport}: {len(doc['posts'])} posts with pictures")
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
    shown = 0
    for p in posts:
        img = p.get("image") or ""
        if not img or img.endswith("logo.jpg"):
            continue
        if not img.startswith("http") and not is_usable_image_file(ROOT / img):
            continue
        src = img if img.startswith("http") else prefix + img
        kind = "X" if p.get("kind") == "x" else (p.get("publisher") or "Web")
        bits.append(
            f'<a class="x-card tile" href="{esc(p.get("url") or "#")}" target="_blank" rel="noopener">'
            f'<img src="{esc(src)}" alt="{esc(p.get("title") or "Meme from X")}" />'
            f'<span class="x-kind">{esc(kind)}</span>'
            f'<h3>{esc(p.get("title") or "")}</h3>'
            f'<p>{esc((p.get("summary") or "")[:140])}</p>'
            f"</a>"
        )
        shown += 1
    if not bits:
        return '<p class="note">No pictures on the tape yet. Next hourly pull saves them onto the cards.</p>'
    return f'<div class="x-grid">{"".join(bits)}</div>'


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Pull The X meme tape")
    ap.add_argument("--sport", choices=("football", "baseball", "soccer", "basketball", "all"), default="all")
    args = ap.parse_args()
    sports = ["football", "baseball", "soccer", "basketball"] if args.sport == "all" else [args.sport]
    for sport in sports:
        scrape_sport(sport)


if __name__ == "__main__":
    main()
