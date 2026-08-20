"""BK News clustering, player matching, and summary helpers.

The scrape job (news_scrape.py) pulls cheap RSS + a rotating slice of
player Google News queries every hour. This module turns those raw items
into clustered stories with player-page links. Football publishes at
/news.html; baseball publishes on BaseBallKeep at /bb/news.html.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

STOP = {
    "a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "at", "by",
    "from", "with", "as", "is", "are", "was", "be", "has", "have", "had",
    "his", "her", "its", "their", "after", "before", "over", "vs", "versus",
    "nfl", "mlb", "nba", "report", "reports", "says", "said", "per", "via",
    "source", "sources", "latest", "update", "updates", "breaking", "watch",
    "video", "news", "fantasy", "week", "game", "games", "season", "team",
    "about", "into", "than", "this", "that", "will", "not", "but", "out",
    "football", "preseason", "roundup", "tracker", "podcast", "notes",
}

INJURY_RE = re.compile(
    r"\b(injur(?:y|ies|ed)|questionable|doubtful|out for|dnp|limited|"
    r"hamstring|ankle|knee|concussion|calf|groin|shoulder|wrist|acl|"
    r"achilles|protocol|illness|rest day|inactive|active/inactive|"
    r"injured reserve|\bir\b|pup|designated to return|"
    r"injured list|\bil\b|10-day|15-day|60-day)\b",
    re.I,
)
ROSTER_RE = re.compile(
    r"\b(waiv(?:e|ed|es)|cut|released|signed|claimed|activated|roster|"
    r"practice squad|elevat(?:e|ed)|designated|returned to|added to|"
    r"dropped|re-sign(?:ed)?|contract|extension|"
    r"dfa|designated for assignment|optioned|called up|recalled|"
    r"outrighted|sent down)\b",
    re.I,
)
COACH_RE = re.compile(
    r"\b(coach|head coach|\bhc\b|\boc\b|\bdc\b|presser|press conference|"
    r"told reporters|said (monday|tuesday|wednesday|thursday|friday)|"
    r"scheme|play-caller|coordinator|manager|skipper)\b",
    re.I,
)
TRADE_RE = re.compile(r"\b(trade[ds]?|dealt|acquired|sent to|in exchange)\b", re.I)
PRACTICE_RE = re.compile(
    r"\b(practice|walkthrough|training camp|padded|walk-through|full go|"
    r"did not practice|returned to practice)\b",
    re.I,
)

AMBIGUOUS_LAST = {
    "williams", "brown", "jones", "johnson", "smith", "davis", "moore",
    "thomas", "wilson", "taylor", "allen", "hall", "harris", "martin",
    "clark", "lewis", "walker", "young", "king", "scott", "green", "adams",
    "baker", "bell", "cook", "price", "love", "jackson", "white", "hill",
    "murray", "cooper", "collins", "reed", "ford", "hunt", "grant", "brooks",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    for old, new in (
        (" GMT", " +0000"),
        (" UTC", " +0000"),
        (" EST", " -0500"),
        (" EDT", " -0400"),
        (" CST", " -0600"),
        (" CDT", " -0500"),
        (" MST", " -0700"),
        (" MDT", " -0600"),
        (" PST", " -0800"),
        (" PDT", " -0700"),
    ):
        text = text.replace(old, new)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(text, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    m = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", text)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    return None


def iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def strip_tags(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_google_title(title: str) -> tuple[str, str]:
    """Google News titles are 'Headline - Publisher'."""
    t = html.unescape((title or "").strip())
    if " - " in t:
        head, pub = t.rsplit(" - ", 1)
        if 1 < len(pub) <= 40:
            return head.strip(), pub.strip()
    return t, ""


def normalize_title(title: str) -> str:
    head, _pub = split_google_title(title)
    n = head.lower()
    n = n.replace("’", "'").replace("“", '"').replace("”", '"')
    n = re.sub(r"https?://\S+", " ", n)
    n = re.sub(r"[^a-z0-9\s']", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def tokens(title: str) -> set[str]:
    return {w for w in normalize_title(title).split() if w and w not in STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def categorize(text: str) -> str:
    blob = text or ""
    if INJURY_RE.search(blob):
        return "injury"
    if TRADE_RE.search(blob):
        return "trade"
    if ROSTER_RE.search(blob):
        return "roster"
    if COACH_RE.search(blob):
        return "coach"
    if PRACTICE_RE.search(blob):
        return "practice"
    return "wire"


CATEGORY_LABEL = {
    "injury": "Injury",
    "roster": "Roster",
    "coach": "Coach report",
    "trade": "Trade",
    "practice": "Practice",
    "wire": "Wire",
}


def load_news_stories(sport: str, root: Path | None = None) -> list:
    path = (root or ROOT) / "data" / "news" / f"{sport}.json"
    if not path.exists():
        return []
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    stories = []
    for s in doc.get("stories") or []:
        s = dict(s)
        for k in ("headline", "blurb", "summary"):
            s[k] = html.unescape(s.get(k) or "")
        for src in s.get("sources") or []:
            src["title"] = html.unescape(src.get("title") or "")
            src["snippet"] = html.unescape(src.get("snippet") or "")
        stories.append(s)
    cleaned = []
    for s in stories:
        blob = f"{s.get('headline')} {s.get('blurb')}".lower()
        if sport == "football" and re.search(r"\b(mlb|baseball)\b", blob) and not re.search(r"\bnfl\b", blob):
            continue
        if sport == "baseball" and "nfl" in blob and "mlb" not in blob:
            continue
        cleaned.append(s)
    return cleaned


def news_when(iso_s: str) -> str:
    dt = parse_dt(iso_s)
    if not dt:
        return iso_s or ""
    return dt.strftime("%b %d, %Y · %H:%M UTC")


def rematch_stories(stories: list[dict], index: dict) -> list[dict]:
    """Fill player links on existing clusters once a Keep roster is available."""
    if not index or not index.get("names"):
        return stories
    out = []
    for s in stories:
        s = dict(s)
        blob_parts = [s.get("headline") or "", s.get("blurb") or "", s.get("summary") or ""]
        for src in s.get("sources") or []:
            blob_parts.append(src.get("title") or "")
            blob_parts.append(src.get("snippet") or "")
        hits = match_players(" ".join(blob_parts), index)
        if hits:
            by_key = {p.get("key"): p for p in (s.get("players") or []) if p.get("key")}
            for h in hits:
                by_key[h["key"]] = h
            s["players"] = list(by_key.values())
        out.append(s)
    return out


def source_kind(url: str, title: str = "", publisher: str = "") -> str:
    host = urlparse(url or "").netloc.lower()
    blob = f"{host} {title} {publisher}".lower()
    if any(h in blob for h in ("youtube.com", "youtu.be", "youtube", "vimeo.com")) or "/video" in (url or "").lower():
        return "video"
    if any(h in blob for h in ("x.com", "twitter.com", "nitter", " on x")):
        return "x"
    return "article"


def publisher_from_url(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    host = re.sub(r"^www\.", "", host)
    aliases = {
        "espn.com": "ESPN",
        "nfl.com": "NFL.com",
        "cbssports.com": "CBS Sports",
        "sports.yahoo.com": "Yahoo Sports",
        "nbcsports.com": "NBC Sports",
        "profootballtalk.nbcsports.com": "PFT",
        "fantasypros.com": "FantasyPros",
        "rotowire.com": "RotoWire",
        "theathletic.com": "The Athletic",
        "nytimes.com": "NYT",
        "x.com": "X",
        "twitter.com": "X",
        "youtube.com": "YouTube",
        "youtu.be": "YouTube",
        "mlb.com": "MLB.com",
        "news.google.com": "Google News",
    }
    if host in aliases:
        return aliases[host]
    for key, label in aliases.items():
        if host.endswith(key):
            return label
    return host.split(":")[0] or "Web"


def item_hash(url: str, title: str) -> str:
    key = (url or "").split("?")[0].rstrip("/").lower() + "|" + normalize_title(title)
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def story_slug(headline: str, category: str, extra: str = "") -> str:
    base = normalize_title(headline)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    parts = [p for p in base.split("-") if p and p not in STOP][:8]
    stem = "-".join(parts) or category or "story"
    digest = hashlib.sha1((normalize_title(headline) + "|" + extra).encode()).hexdigest()[:8]
    slug = f"{stem[:72]}-{digest}"
    return slug.strip("-")


def build_player_index(roster: list[dict]) -> dict:
    """Full-name matchers plus unique last names that are safe to fire."""
    by_key = {}
    last_counts: dict[str, list[dict]] = {}
    names: list[tuple[str, dict]] = []
    for p in roster:
        key = (p.get("key") or "").strip()
        if not key:
            continue
        rec = {
            "key": key,
            "name": p.get("name") or key.title(),
            "slug": p.get("slug") or "",
            "pos": p.get("pos") or "",
            "team": p.get("team") or "",
        }
        by_key[key] = rec
        names.append((key, rec))
        last = key.split()[-1] if key.split() else ""
        if last:
            last_counts.setdefault(last, []).append(rec)
        # Common first-last without punctuation already in key.
        display = re.sub(r"[^a-z0-9\s]", " ", (p.get("name") or "").lower())
        display = re.sub(r"\s+", " ", display).strip()
        if display and display != key:
            names.append((display, rec))

    unique_last = {}
    for last, recs in last_counts.items():
        uniq = {r["key"]: r for r in recs}
        if len(uniq) == 1 and last not in AMBIGUOUS_LAST and len(last) >= 7:
            unique_last[last] = next(iter(uniq.values()))

    names.sort(key=lambda kv: len(kv[0]), reverse=True)
    return {"by_key": by_key, "names": names, "unique_last": unique_last}


def match_players(text: str, index: dict) -> list[dict]:
    blob = " " + re.sub(r"[^a-z0-9\s']", " ", (text or "").lower()) + " "
    blob = blob.replace("'", " ")
    blob = re.sub(r"\s+", " ", blob)
    hits = {}
    for name, rec in index.get("names") or []:
        if len(name) < 6:
            continue
        needle = " " + name + " "
        if needle in blob:
            hits[rec["key"]] = rec
    if not hits:
        for last, rec in (index.get("unique_last") or {}).items():
            first = rec["key"].split()[0]
            foreign = False
            for m in re.finditer(rf"\b([a-z]+)\s+{re.escape(last)}\b", blob):
                token = m.group(1)
                if token in {"wr", "rb", "qb", "te", "ol", "dl", "lb", "the"}:
                    continue
                if token != first:
                    foreign = True
                    break
            if foreign:
                continue
            if re.search(rf"\b{re.escape(last)}\b", blob):
                hits[rec["key"]] = rec
    return list(hits.values())


def cluster_items(items: list[dict], hours: float = 36.0) -> list[list[dict]]:
    """Greedy clusters: similar titles, or same player + category in a window."""
    groups: list[list[dict]] = []
    for item in items:
        placed = False
        for group in groups:
            if len(group) >= 12:
                ja = jaccard(tokens(item.get("title") or ""), tokens(group[0].get("title") or ""))
                if ja < 0.38:
                    continue
            if _same_cluster(item, group[0], hours):
                group.append(item)
                placed = True
                break
        if not placed:
            groups.append([item])
    return groups


GENERIC_LONG = {
    "injured", "hamstring", "questionable", "doubtful", "practice", "inactive",
    "concussion", "protocol", "limited", "available", "following", "statement",
    "addresses", "offensive", "defensive", "linebacker", "quarterback",
    "running", "receiver", "reserve", "outside", "commanders", "chargers",
    "panthers", "cowboys", "packers", "dolphins", "raiders", "broncos",
    "bengals", "browns", "falcons", "ravens", "texans", "colts", "jaguars",
    "chiefs", "saints", "giants", "eagles", "steelers", "seahawks", "buccaneers",
    "titans", "patriots", "vikings", "lions", "bears", "bills", "rams",
}


def _same_cluster(a: dict, b: dict, hours: float) -> bool:
    ta, tb = tokens(a.get("title") or ""), tokens(b.get("title") or "")
    ja = jaccard(ta, tb)
    if ja >= 0.38:
        return True
    long_hit = {t for t in (ta & tb) if len(t) >= 7 and t not in GENERIC_LONG}
    if ja >= 0.22 and long_hit:
        return True
    keys_a = {p["key"] for p in a.get("players") or []}
    keys_b = {p["key"] for p in b.get("players") or []}
    if (
        keys_a and keys_b and (keys_a & keys_b)
        and len(keys_a) <= 3 and len(keys_b) <= 3
        and a.get("category") == b.get("category")
        and a.get("category") not in {"wire", None}
    ):
        da, db = parse_dt(a.get("published")), parse_dt(b.get("published"))
        if da and db and abs((da - db).total_seconds()) <= hours * 3600:
            return True
    return False


def summarize(items: list[dict], players: list[dict]) -> tuple[str, str]:
    """Return (short blurb, aggregate summary)."""
    snippets = []
    seen = set()
    for it in items:
        raw = strip_tags(it.get("summary") or it.get("title") or "")
        if not raw:
            continue
        # Drop Google News related-link dumps that repeat the title.
        bits = re.split(r"(?<=[.!?])\s+", raw)
        for bit in bits:
            bit = bit.strip()
            if len(bit) < 28:
                continue
            key = normalize_title(bit)[:80]
            if key in seen:
                continue
            seen.add(key)
            snippets.append(bit)
            if len(snippets) >= 6:
                break
        if len(snippets) >= 6:
            break
    if not snippets:
        snippets = [split_google_title(items[0].get("title") or "Update")[0]]

    pubs = []
    for it in items:
        pub = it.get("publisher") or publisher_from_url(it.get("url") or "")
        if pub and pub not in pubs:
            pubs.append(pub)

    names = [p["name"] for p in players]
    who = ""
    if names:
        who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" and {names[-1]}"

    lead = snippets[0]
    if who and who.split()[0].lower() not in lead.lower():
        lead = f"{who}: {lead}"
    if pubs:
        if len(pubs) == 1:
            attrib = f" Desk reading of {pubs[0]}."
        else:
            attrib = f" Aggregated from {', '.join(pubs[:5])}" + ("." if len(pubs) <= 5 else f" and {len(pubs) - 5} more.")
    else:
        attrib = ""
    extra = " ".join(snippets[1:3])
    summary = (lead + " " + extra).strip() + attrib
    summary = re.sub(r"\s+", " ", summary).strip()
    blurb = snippets[0]
    if len(blurb) > 180:
        blurb = blurb[:177].rsplit(" ", 1)[0] + "…"
    return blurb, summary


def pick_headline(items: list[dict]) -> str:
    scored = []
    for it in items:
        head, _ = split_google_title(it.get("title") or "")
        if not head or len(head) < 18:
            continue
        if re.match(r"^(read more|watch now|subscribe)", head, re.I):
            continue
        kind = source_kind(it.get("url") or "", head, it.get("publisher") or "")
        pub = (it.get("publisher") or "").lower()
        kind_bonus = 80 if kind == "article" else 10 if kind == "video" else 0
        if "x.com" in pub or pub in {"x", "twitter"}:
            kind_bonus -= 40
        n = len(head)
        length_score = n if n <= 110 else max(20, 110 - (n - 110))
        scored.append((kind_bonus + length_score, head))
    scored.sort(reverse=True)
    headline = scored[0][1] if scored else "Update"
    if len(headline) > 140:
        headline = headline[:137].rsplit(" ", 1)[0] + "…"
    return headline


def merge_story(existing: dict | None, items: list[dict], sport: str) -> dict:
    players = []
    seen_p = set()
    for it in items:
        for p in it.get("players") or []:
            if p["key"] in seen_p:
                continue
            seen_p.add(p["key"])
            players.append(p)
    if existing:
        for p in existing.get("players") or []:
            if p["key"] not in seen_p:
                seen_p.add(p["key"])
                players.append(p)

    cats = [it.get("category") or "wire" for it in items]
    if existing and existing.get("category"):
        cats.insert(0, existing["category"])
    category = next((c for c in ("injury", "trade", "roster", "coach", "practice") if c in cats), cats[0] if cats else "wire")

    sources = list(existing.get("sources") or []) if existing else []
    seen_u = {s.get("url") for s in sources}
    for it in items:
        url = it.get("url") or ""
        if not url or url in seen_u:
            continue
        seen_u.add(url)
        sources.append({
            "title": split_google_title(it.get("title") or "")[0],
            "url": url,
            "publisher": it.get("publisher") or publisher_from_url(url),
            "kind": source_kind(url, it.get("title") or "", it.get("publisher") or ""),
            "snippet": strip_tags(it.get("summary") or "")[:280],
            "published": it.get("published") or "",
        })

    all_for_summary = items[:]
    if existing:
        for s in existing.get("sources") or []:
            all_for_summary.append({
                "title": s.get("title") or "",
                "summary": s.get("snippet") or existing.get("summary") or "",
                "publisher": s.get("publisher") or "",
                "url": s.get("url") or "",
            })
    blurb, summary = summarize(all_for_summary, players)
    headline = pick_headline(all_for_summary) if all_for_summary else (existing or {}).get("headline") or "Update"

    times = [parse_dt(it.get("published")) for it in items]
    times = [t for t in times if t]
    published = min(times) if times else parse_dt((existing or {}).get("published"))
    updated = max(times) if times else utcnow()
    if existing:
        old_u = parse_dt(existing.get("updated") or existing.get("published"))
        if old_u and old_u > updated:
            updated = old_u
        old_p = parse_dt(existing.get("published"))
        if old_p and (not published or old_p < published):
            published = old_p

    slug = (existing or {}).get("slug") or story_slug(headline, category, sport)
    return {
        "id": (existing or {}).get("id") or slug,
        "slug": slug,
        "sport": sport,
        "headline": headline,
        "blurb": blurb,
        "summary": summary,
        "category": category,
        "published": iso(published or updated),
        "updated": iso(updated),
        "players": players,
        "sources": sources,
    }


def player_query_slice(roster: list[dict], now: datetime, size: int = 8) -> list[dict]:
    """Each hour hits a rotating slice of Keep names instead of the full board."""
    keep = [p for p in roster if (p.get("lists") or {}).get("The Keep")]
    keep.sort(key=lambda p: (p.get("lists") or {}).get("The Keep", 999))
    pool = keep[:48] or roster[:48]
    if not pool:
        return []
    tick = now.timetuple().tm_yday * 24 + now.hour
    start = tick % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(min(size, len(pool)))]


def story_score(story: dict) -> float:
    nsrc = min(len(story.get("sources") or []), 10)
    nplay = min(len(story.get("players") or []), 4)
    cat_w = {"injury": 6, "trade": 5, "roster": 5, "coach": 4, "practice": 3, "wire": 1}
    cat = cat_w.get(story.get("category") or "wire", 1)
    dt = parse_dt(story.get("updated") or story.get("published"))
    hours = 24.0
    if dt:
        hours = max(0.0, (utcnow() - dt).total_seconds() / 3600.0)
    recency = max(0.2, 1.0 - (hours / 72.0))
    return (nsrc * 1.2 + nplay * 4 + cat) * recency


def is_publishable(story: dict) -> bool:
    sources = story.get("sources") or []
    kinds = {s.get("kind") for s in sources}
    title = story.get("headline") or ""
    if title in {"Update", ""} or len(title) < 18:
        return False
    if re.search(r"call/?text\s*->", title, re.I):
        return False
    blob = f"{title} {story.get('blurb') or ''}".lower()
    if story.get("sport") == "football":
        if re.search(r"\b(mlb|baseball)\b", blob) and not re.search(r"\bnfl\b", blob):
            return False
    if story.get("sport") == "baseball":
        if "nfl" in blob and "mlb" not in blob:
            return False
    if "article" in kinds or "video" in kinds:
        return True
    if story.get("players") and story.get("category") in {"injury", "roster", "coach", "trade", "practice"}:
        return True
    return False


def prune_stories(stories: list[dict], keep: int = 60) -> list[dict]:
    stories = [s for s in stories if is_publishable(s)]
    stories = sorted(
        stories,
        key=lambda s: (story_score(s), s.get("updated") or s.get("published") or ""),
        reverse=True,
    )
    return stories[:keep]


def prune_seen(seen: dict, keep: int = 4000) -> dict:
    """seen maps hash -> iso timestamp."""
    items = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)
    return dict(items[:keep])
