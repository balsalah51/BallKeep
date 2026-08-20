#!/usr/bin/env python3
"""Shared SEO, sharing, and optional analytics/ads tags for the static site.

Fill data/site.json to turn on Google Analytics (ga_measurement_id like G-XXXX)
and AdSense Auto ads (adsense_client like ca-pub-XXXX). Empty strings stay off.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
_SITE_CACHE: dict | None = None

ORIGIN_DEFAULT = "https://ballkeep.com"

FB_DEFAULT = (
    "Ball Keep dynasty and redraft rankings, trade calculators, hourly news, "
    "and player files for Superflex and 1QB leagues."
)
BB_DEFAULT = (
    "BaseBallKeep dynasty and redraft baseball rankings, trade calculators, "
    "waiver wires, and player files."
)
PL_DEFAULT = (
    "PitchKeep Premier League rankings. The Premier hybrid 400, Sleeper BPL 2025, "
    "and 24-board consensus."
)

# path -> (full <title>, meta description). Paths are site-relative inside each desk.
FB_PAGES = {
    "index.html": (
        "Ball Keep — Superflex Dynasty Rankings, Trade Calculator & News",
        "Daily Superflex dynasty top 400, four trade calculators, hourly injury news, "
        "and player files. Football first. Baseball and Premier League next door.",
    ),
    "the-keep.html": (
        "The Keep — Superflex Dynasty Top 400 Rankings | Ball Keep",
        "The Keep is Ball Keep's Superflex dynasty top 400. Consensus of FantasyPros, "
        "PFN, Dynasty Nerds, KeepTradeCut, ESPN, and more, turned into BK Value.",
    ),
    "news.html": (
        "BK News — NFL Injury, Roster & Coach Wire | Ball Keep",
        "Hourly NFL injury, roster, practice, and coach reports clustered into short "
        "stories with source links and Ball Keep player pages.",
    ),
    "trade.html": (
        "Fantasy Trade Calculator — Superflex, 1QB, PPR | Ball Keep",
        "Four Ball Keep trade calculators. Rank becomes BK Value. Superflex dynasty, "
        "1QB dynasty, redraft PPR, and redraft standard. Fair is within 8%.",
    ),
    "recent-trades.html": (
        "Recent Dynasty Trades — Superflex & 1QB Packages | Ball Keep",
        "Type a player and see every Superflex and 1QB package on the Ball Keep desk tape.",
    ),
    "trade-superflex.html": (
        "Superflex Dynasty Trade Calculator | Ball Keep",
        "Superflex dynasty trade calculator. BK Value from The Keep rank. Add two sides; fair is within 8%.",
    ),
    "trade-1qb.html": (
        "1QB Dynasty Trade Calculator | Ball Keep",
        "1QB dynasty trade calculator. Same Superflex ranks with quarterbacks taxed to 38% of BK Value.",
    ),
    "trade-ppr.html": (
        "PPR Redraft Trade Calculator | Ball Keep",
        "Full-PPR redraft trade calculator using Ball Keep's 2026 PPR board and BK Value.",
    ),
    "trade-standard.html": (
        "Standard Redraft Trade Calculator | Ball Keep",
        "Standard (non-PPR) redraft trade calculator using Ball Keep's 2026 standard board.",
    ),
    "redraft-ppr.html": (
        "2026 Fantasy Football PPR Rankings | Ball Keep",
        "2026 full-PPR redraft top 200. Consensus of Field Yates, FantasyPros ECR, and Eric Karabell.",
    ),
    "redraft-standard.html": (
        "2026 Fantasy Football Standard Rankings | Ball Keep",
        "2026 standard (non-PPR) redraft rankings. Same season, no reception point, different order.",
    ),
    "rookies-2026.html": (
        "2026 Dynasty Rookie Rankings | Ball Keep",
        "2026 drafted rookie class consensus ranks and Superflex BK Values for dynasty startups and rookie drafts.",
    ),
    "hot-n-cold.html": (
        "Dynasty Buys and Sells — BK Hot 'n' Cold | Ball Keep",
        "Dynasty buys and sells scraped from public desks and film shows. Hot names to acquire, cold names to move.",
    ),
    "board.html": (
        "The Board — Long Superflex Dynasty Aggregate | Ball Keep",
        "The Board is Ball Keep's long proprietary Superflex aggregate — every ranked name pulled from the source desks.",
    ),
    "nfl-schedule.html": (
        "2026 NFL Schedule — All 32 Teams | Ball Keep",
        "2026 NFL week-by-week slate and all 32 team pages on the Ball Keep football desk.",
    ),
    "mlb-schedule.html": (
        "MLB September Schedule | Ball Keep",
        "September MLB stretch-run schedules, filterable by club, on the Ball Keep desk.",
    ),
    "discord.html": (
        "Ball Keep Discord Bot — Ranks, Trades & Tape",
        "Add the Ball Keep bot to a league Discord: Keep ranks, trade calculator, recent deals, highlights, and player files.",
    ),
    "players/index.html": (
        "NFL Player Pages — Dynasty Ranks & Tape | Ball Keep",
        "Every Keep 400 name plus redraft, rookies, and Hot/Cold: ranks, board dump, headshot, and a 2025 or college clip.",
    ),
}

BB_PAGES = {
    "index.html": (
        "BaseBallKeep — Dynasty Baseball Rankings, Trade Calculator & News",
        "Dynasty baseball top 400, hitter and pitcher boards, bullpen charts, redraft, "
        "trade calculators, and hourly BK News. Navy diamond desk on ballkeep.com.",
    ),
    "the-keep.html": (
        "The Keep — Dynasty Baseball Top 400 | BaseBallKeep",
        "Overall dynasty baseball top 400 aggregated from 23 public boards, led by RotoGraphs and The Dynasty Guru.",
    ),
    "news.html": (
        "BK News Baseball — IL, Roster & Manager Wire | BaseBallKeep",
        "Hourly MLB injury, roster, DFA/call-up, and manager tape clustered into short stories with player-file links.",
    ),
    "the-lineup.html": (
        "The Lineup — Dynasty Hitter Rankings | BaseBallKeep",
        "Dynasty hitters only. The bats on the long boards, re-ranked among hitters, up to 400 names.",
    ),
    "pitchers.html": (
        "BK's Pitchers — Dynasty Pitcher Rankings | BaseBallKeep",
        "Top 150 overall dynasty pitchers on BaseBallKeep. Starting pitchers plus the two-way names.",
    ),
    "bullpen.html": (
        "Bullpen Saves Rankings | BaseBallKeep",
        "Top 100 relief pitchers for traditional saves leagues. FantasyPros closer chart plus ESPN reliever depth.",
    ),
    "bullpen-holds.html": (
        "Bullpen Saves + Holds Rankings | BaseBallKeep",
        "Top relievers for saves-plus-holds leagues. Setup men the ESPN chart actually uses.",
    ),
    "redraft.html": (
        "Fantasy Baseball Redraft Rankings | BaseBallKeep",
        "Rest-of-season baseball redraft 400 on the BaseBallKeep diamond desk.",
    ),
    "trade.html": (
        "Baseball Trade Calculator | BaseBallKeep",
        "BaseBallKeep trade calculators for Keep, Lineup, Pitchers, Redraft, Saves, and SV+H. Same BK Value curve.",
    ),
    "waivers-dynasty.html": (
        "Dynasty Baseball Waiver Wire | BaseBallKeep",
        "Fifteen dynasty baseball stashes on the BaseBallKeep Dynasty Wire. Short on purpose.",
    ),
    "waivers-redraft.html": (
        "Redraft Baseball Waiver Wire | BaseBallKeep",
        "Priority 1–50 rest-of-season baseball waiver adds on the BaseBallKeep Redraft Wire.",
    ),
    "players/index.html": (
        "MLB Player Pages — Dynasty Ranks | BaseBallKeep",
        "Keep 400 baseball player files: ranks, boards, headshots, and tape on the diamond desk.",
    ),
}

PL_PAGES = {
    "index.html": (
        "PitchKeep — Premier League Fantasy Rankings & Trade Calculator",
        "The Premier hybrid 400, The Pitch on Sleeper BPL 2025 points, position boards, "
        "and trade calculators for Premier League fantasy.",
    ),
    "the-premier.html": (
        "The Premier — Hybrid Premier League Top 400 | PitchKeep",
        "Top 400 blending 50% Sleeper BPL 2025 rank with 50% industry consensus. Full names, ages, and BK Value.",
    ),
    "the-pitch.html": (
        "The Pitch — Sleeper BPL 2025 Rankings | PitchKeep",
        "Top 400 ranked on Sleeper BPL 2025 default soccer scoring applied to 2025/26 counting stats.",
    ),
    "attack.html": (
        "Premier League Forward Rankings | PitchKeep",
        "Forwards only, re-ranked on Sleeper BPL 2025. Haaland is the tax; volume strikers sit underneath.",
    ),
    "midfield.html": (
        "Premier League Midfielder Rankings | PitchKeep",
        "Midfielders re-ranked on Sleeper BPL 2025. Assists pay; Bruno, Semenyo, Rice, Gibbs-White lead the room.",
    ),
    "defence.html": (
        "Premier League Defender Rankings | PitchKeep",
        "Defenders re-ranked on Sleeper BPL 2025. Clean sheets are 6 points; goals against are −2.",
    ),
    "keepers.html": (
        "Premier League Goalkeeper Rankings | PitchKeep",
        "Keepers re-ranked on Sleeper BPL 2025. Saves at 2 and clean sheets at 8.",
    ),
    "trade.html": (
        "Premier League Trade Calculator | PitchKeep",
        "PitchKeep trade calculators for The Pitch, Attack, Midfield, Defence, and Keepers. Same BK Value curve.",
    ),
    "players/index.html": (
        "Premier League Player Pages | PitchKeep",
        "Every Pitch 400 name: headshot, Sleeper points, 2025/26 line, every board, and YouTube tape.",
    ),
}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def load_site() -> dict:
    global _SITE_CACHE
    if _SITE_CACHE is not None:
        return _SITE_CACHE
    path = ROOT / "data" / "site.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text()) or {}
        except json.JSONDecodeError:
            data = {}
    data.setdefault("origin", ORIGIN_DEFAULT)
    data.setdefault("ga_measurement_id", "")
    data.setdefault("adsense_client", "")
    data.setdefault("twitter_handle", "")
    _SITE_CACHE = data
    return data


def origin() -> str:
    return (load_site().get("origin") or ORIGIN_DEFAULT).rstrip("/")


def canonical(path: str, desk: str = "fb") -> str:
    """Absolute URL. desk is fb (root), bb, or pl. index.html becomes a directory URL."""
    rel = (path or "").lstrip("/")
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    if desk in ("bb", "pl"):
        base = f"{origin()}/{desk}/"
    else:
        base = origin() + "/"
    return base + rel


def abs_asset(rel: str) -> str:
    rel = (rel or "").replace("\\", "/")
    while rel.startswith("../"):
        rel = rel[3:]
    rel = rel.lstrip("/")
    return f"{origin()}/{rel}"


def page_meta(path: str, desk: str, fallback_title: str) -> tuple[str, str]:
    table = {"fb": FB_PAGES, "bb": BB_PAGES, "pl": PL_PAGES}[desk]
    brand = {"fb": "Ball Keep", "bb": "BaseBallKeep", "pl": "PitchKeep"}[desk]
    default_desc = {"fb": FB_DEFAULT, "bb": BB_DEFAULT, "pl": PL_DEFAULT}[desk]
    if path in table:
        return table[path]
    if path.startswith("news/") and path != "news.html":
        return f"{fallback_title} | {brand}", default_desc
    if path.startswith("players/") and path != "players/index.html":
        if desk == "fb":
            return (
                f"{fallback_title} Dynasty Rankings, Trade Value & Tape | Ball Keep",
                default_desc,
            )
        if desk == "bb":
            return (
                f"{fallback_title} Dynasty Rankings & BK Value | BaseBallKeep",
                default_desc,
            )
        return (
            f"{fallback_title} Premier League Rankings & Tape | PitchKeep",
            default_desc,
        )
    title = fallback_title if ("—" in fallback_title or "|" in fallback_title) else f"{fallback_title} — {brand}"
    return title, default_desc


def player_description(name: str, pos: str = "", team: str = "", rank=None, sport: str = "football") -> str:
    bits = [name]
    if pos or team:
        bits.append(" ".join(x for x in (pos, team) if x).strip())
    if sport == "football":
        if rank:
            bits.append(f"Superflex dynasty rank #{rank}")
        bits.append("BK Value, plus/minus, expert boards, and tape on Ball Keep.")
    elif sport == "baseball":
        if rank:
            bits.append(f"dynasty Keep rank #{rank}")
        bits.append("boards, BK Value, and the BaseBallKeep player file.")
    else:
        if rank:
            bits.append(f"PitchKeep Premier rank #{rank}")
        bits.append("Sleeper BPL points, FPL line, and tape on PitchKeep.")
    text = ". ".join(bits)
    return text[:300]


def clip_desc(text: str, limit: int = 160) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def person_ld(name: str, url: str, image: str | None = None, extra: dict | None = None) -> dict:
    node = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": url,
    }
    if image:
        node["image"] = image
    if extra:
        node.update(extra)
    return node


def news_ld(headline: str, url: str, description: str, published: str | None = None, image: str | None = None) -> dict:
    node = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": headline,
        "description": description,
        "url": url,
        "mainEntityOfPage": url,
        "publisher": {
            "@type": "Organization",
            "name": "Ball Keep",
            "url": origin() + "/",
            "logo": abs_asset("img/logo.jpg"),
        },
    }
    if published:
        node["datePublished"] = published
        node["dateModified"] = published
    if image:
        node["image"] = image
    return node


def website_ld(desk: str = "fb") -> dict:
    names = {"fb": "Ball Keep", "bb": "BaseBallKeep", "pl": "PitchKeep"}
    urls = {"fb": origin() + "/", "bb": origin() + "/bb/", "pl": origin() + "/pl/"}
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": names[desk],
        "url": urls[desk],
        "publisher": {"@type": "Organization", "name": names[desk], "url": urls[desk]},
    }


def json_ld_tag(payload) -> str:
    if not payload:
        return ""
    blobs = payload if isinstance(payload, list) else [payload]
    parts = []
    for blob in blobs:
        raw = json.dumps(blob, ensure_ascii=True, separators=(",", ":"))
        raw = raw.replace("<", "\\u003c")
        parts.append(f'<script type="application/ld+json">{raw}</script>')
    return "\n  ".join(parts)


def tracking_tags() -> str:
    site = load_site()
    bits = []
    ga = (site.get("ga_measurement_id") or "").strip()
    if ga:
        bits.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(ga)}"></script>\n'
            f"  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
            f"gtag('js',new Date());gtag('config','{esc(ga)}');</script>"
        )
    ads = (site.get("adsense_client") or "").strip()
    if ads:
        bits.append(
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(ads)}" '
            f'crossorigin="anonymous"></script>'
        )
    return "\n  ".join(bits)


def twitter_site() -> str:
    handle = (load_site().get("twitter_handle") or "").strip()
    if not handle:
        return ""
    if not handle.startswith("@"):
        handle = "@" + handle
    return f'<meta name="twitter:site" content="{esc(handle)}" />'


def share_bar(url: str, title: str) -> str:
    reddit = "https://www.reddit.com/submit?url=" + quote(url, safe="") + "&title=" + quote(title, safe="")
    tweet = "https://x.com/intent/tweet?url=" + quote(url, safe="") + "&text=" + quote(title, safe="")
    return (
        f'<p class="share" data-url="{esc(url)}">'
        f"<span>Share</span>"
        f'<a href="{esc(reddit)}" target="_blank" rel="noopener noreferrer">Reddit</a>'
        f'<a href="{esc(tweet)}" target="_blank" rel="noopener noreferrer">X</a>'
        f'<button type="button" class="share-copy">Copy link</button>'
        f"</p>"
    )


SHARE_JS = """<script>
(function(){
  document.querySelectorAll('.share-copy').forEach(function(btn){
    btn.addEventListener('click', function(){
      var box = btn.closest('.share');
      var url = (box && box.getAttribute('data-url')) || location.href;
      function done(){ btn.textContent = 'Copied'; setTimeout(function(){ btn.textContent = 'Copy link'; }, 1600); }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function(){ window.prompt('Copy this link', url); });
      } else { window.prompt('Copy this link', url); }
    });
  });
})();
</script>"""


def head_tags(
    *,
    desk: str,
    path: str,
    fallback_title: str,
    css_href: str,
    icon_href: str,
    description: str | None = None,
    image: str | None = None,
    og_type: str = "website",
    json_ld=None,
    published: str | None = None,
) -> str:
    full_title, default_desc = page_meta(path, desk, fallback_title)
    desc = clip_desc(description or default_desc, 170)
    canon = canonical(path, desk)
    img = abs_asset(image) if image else {
        "fb": abs_asset("img/logo.jpg"),
        "bb": abs_asset("img/bb-logo.jpg"),
        "pl": abs_asset("img/pl-logo.jpg"),
    }[desk]
    og_title = full_title
    tw = twitter_site()
    published_tag = f'<meta property="article:published_time" content="{esc(published)}" />' if published else ""
    ld = json_ld
    if path == "index.html" and not ld:
        ld = website_ld(desk)
    tracking = tracking_tags()
    bits = [
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width,initial-scale=1" />',
        f"<title>{esc(full_title)}</title>",
        f'<meta name="description" content="{esc(desc)}" />',
        '<meta name="robots" content="index,follow" />',
        f'<link rel="canonical" href="{esc(canon)}" />',
        f'<meta property="og:type" content="{esc(og_type)}" />',
        f'<meta property="og:site_name" content="{esc({"fb": "Ball Keep", "bb": "BaseBallKeep", "pl": "PitchKeep"}[desk])}" />',
        f'<meta property="og:title" content="{esc(og_title)}" />',
        f'<meta property="og:description" content="{esc(desc)}" />',
        f'<meta property="og:url" content="{esc(canon)}" />',
        f'<meta property="og:image" content="{esc(img)}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{esc(og_title)}" />',
        f'<meta name="twitter:description" content="{esc(desc)}" />',
        f'<meta name="twitter:image" content="{esc(img)}" />',
        tw,
        published_tag,
        f'<link rel="stylesheet" href="{esc(css_href)}" />',
        f'<link rel="icon" href="{esc(icon_href)}" />',
        json_ld_tag(ld),
        tracking,
    ]
    return "\n  ".join(b for b in bits if b)


def sitemap_url(loc: str, lastmod: str | None = None, priority: str | None = None, changefreq: str | None = None) -> str:
    parts = [f"    <loc>{esc(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{esc(lastmod)}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{esc(changefreq)}</changefreq>")
    if priority:
        parts.append(f"    <priority>{esc(priority)}</priority>")
    return "  <url>\n" + "\n".join(parts) + "\n  </url>\n"
