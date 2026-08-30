"""Unique titles, descriptions, Open Graph, and bar graphs for Ball Keep pages."""
from __future__ import annotations

import html
import json
import re

SITE = "https://ballkeep.com"
FONT_HREF = "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800&display=swap"

BRANDS = {
    "Ball Keep": {
        "url": SITE,
        "logo": "img/logo.jpg",
        "theme": "#c8102e",
        "sameAs": ["https://github.com/balsalah51/BallKeep"],
        "rss_title": "BK News",
        "rss": f"{SITE}/feed.xml",
        "sport": "American Football",
    },
    "BasketKeep": {
        "url": f"{SITE}/bk/",
        "logo": "img/bk-logo.jpg",
        "theme": "#e87722",
        "sameAs": ["https://github.com/balsalah51/BallKeep"],
        "rss_title": "BasketKeep News",
        "rss": f"{SITE}/bk/feed.xml",
        "sport": "Basketball",
    },
    "BaseKeep": {
        "url": f"{SITE}/bb/",
        "logo": "img/bb-logo.jpg",
        "theme": "#0b1f3a",
        "sameAs": ["https://github.com/balsalah51/BallKeep"],
        "rss_title": "BaseKeep News",
        "rss": f"{SITE}/bb/feed.xml",
        "sport": "Baseball",
    },
    "PitchKeep": {
        "url": f"{SITE}/pl/",
        "logo": "img/pl-logo.jpg",
        "theme": "#37003c",
        "sameAs": ["https://github.com/balsalah51/BallKeep"],
        "rss_title": "PitchKeep News",
        "rss": f"{SITE}/pl/feed.xml",
        "sport": "Soccer",
    },
}

SPORT_LINKS = [
    ("fb", "", "BallKeep"),
    ("bb", "bb/", "BaseKeep"),
    ("bk", "bk/", "BasketKeep"),
    ("pl", "pl/", "PitchKeep"),
]


def sport_pills(here: str, depth: int = 0) -> str:
    """Clickable sport-switch pills, same look in the header strip and the footer."""
    prefix = "../" * depth
    bits = []
    for key, folder, label in SPORT_LINKS:
        if key == here:
            continue
        href = f"{prefix}{folder}index.html" if folder else f"{prefix}index.html"
        bits.append(f'<a class="sport-switch {key}" href="{href}">{label}</a>')
    return "".join(bits)


def sports_top(here: str, depth: int = 0) -> str:
    return f'<div class="sports-top">{sport_pills(here, depth)}</div>'


def sports_footer(here: str, depth: int = 0) -> str:
    return f"<div>{sport_pills(here, depth)}</div>"


def legal_links(depth: int = 0) -> str:
    prefix = "../" * depth
    return f'<p class="legal-links"><a href="{prefix}privacy.html">Privacy Policy</a></p>'


def esc(s):
    return html.escape(str(s), quote=True)


def strip_em(text: str) -> str:
    """Site copy does not use em dashes."""
    if not text:
        return text
    return (
        text.replace("\u2014", "-")
        .replace("&mdash;", "-")
        .replace("&#8212;", "-")
        .replace("&#x2014;", "-")
    )


def canon(path: str, prefix: str = "") -> str:
    path = (path or "index.html").lstrip("/")
    if path in ("index.html", ""):
        return f"{SITE}/{prefix}" if prefix else f"{SITE}/"
    return f"{SITE}/{prefix}{path}"


def abs_img(path: str, fallback: str) -> str:
    p = (path or fallback or "").lstrip("/")
    if p.startswith("http"):
        return p
    if not p:
        p = fallback.lstrip("/")
    return f"{SITE}/{p}"


def clip(text: str, n: int = 168) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= n:
        return t
    cut = t[: n - 1].rsplit(" ", 1)[0]
    return (cut or t[: n - 1]).rstrip(".,;:") + "…"


def grafs_html(kicker: str, grafs, limit: int = 2) -> str:
    grafs = [g for g in (grafs or []) if g]
    if not grafs:
        return ""
    return (
        f'<section class="panel analysis"><p class="kicker">{esc(kicker)}</p>'
        + "".join(f"<p>{esc(g)}</p>" for g in grafs[:limit])
        + "</section>"
    )


def branded(title: str, brand: str) -> str:
    t = (title or "").strip()
    if not t:
        return brand
    low = t.lower()
    b = brand.lower()
    if low.endswith(b) or low.startswith(b) or f" | {b}" in low or f" — {b}" in low:
        return t
    return f"{t} | {brand}"


def _brand_meta(brand: str, brand_url: str | None = None) -> dict:
    meta = dict(BRANDS.get(brand) or BRANDS["Ball Keep"])
    if brand_url:
        meta["url"] = brand_url
    return meta


def _image_mime(path: str) -> str:
    low = (path or "").split("?", 1)[0].lower()
    if low.endswith(".png"):
        return "image/png"
    if low.endswith(".webp"):
        return "image/webp"
    if low.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"


def org_jsonld(brand: str, brand_url: str | None = None) -> dict:
    meta = _brand_meta(brand, brand_url)
    home = meta["url"]
    obj = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": brand,
        "url": home,
        "logo": {"@type": "ImageObject", "url": abs_img(meta["logo"], meta["logo"])},
    }
    if meta.get("sameAs"):
        obj["sameAs"] = list(meta["sameAs"])
    return obj


def website_jsonld(brand: str, brand_url: str | None = None) -> dict:
    meta = _brand_meta(brand, brand_url)
    home = meta["url"]
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": brand,
        "url": home,
        "inLanguage": "en-US",
        "publisher": org_jsonld(brand, brand_url),
    }


def head_tags(
    *,
    title: str,
    description: str,
    canonical: str,
    image: str,
    brand: str,
    og_type: str = "website",
    extra_jsonld=None,
    published: str | None = None,
    modified: str | None = None,
    brand_url: str | None = None,
    robots: str | None = None,
    rss: tuple | None = None,
) -> str:
    full = branded(title, brand)
    desc = clip(description, 168)
    meta = _brand_meta(brand, brand_url)
    img = abs_img(image, meta["logo"])
    logo = abs_img(meta["logo"], meta["logo"])
    home = meta["url"]
    robots_content = robots or "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": full,
        "description": desc,
        "url": canonical,
        "inLanguage": "en-US",
        "isPartOf": {"@type": "WebSite", "name": brand, "url": home},
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": home,
            "logo": {"@type": "ImageObject", "url": logo},
        },
        "primaryImageOfPage": {"@type": "ImageObject", "url": img},
    }
    if published:
        jsonld["datePublished"] = published
    if modified or published:
        jsonld["dateModified"] = modified or published
    blobs = [json.dumps(jsonld, ensure_ascii=False)]
    for extra in extra_jsonld or []:
        if extra:
            blobs.append(json.dumps(extra, ensure_ascii=False))
    og_extra = (
        f'\n  <meta property="og:locale" content="en_US" />\n'
        f'  <meta property="og:image:alt" content="{esc(full)}" />\n'
        f'  <meta property="og:image:type" content="{esc(_image_mime(img))}" />'
    )
    if published:
        og_extra += f'\n  <meta property="article:published_time" content="{esc(published)}" />'
    if modified:
        og_extra += f'\n  <meta property="article:modified_time" content="{esc(modified)}" />'
    rss_pair = rss if rss is not None else (meta.get("rss_title"), meta.get("rss"))
    rss_link = ""
    if rss_pair and rss_pair[0] and rss_pair[1]:
        rss_link = (
            f'  <link rel="alternate" type="application/rss+xml" '
            f'title="{esc(rss_pair[0])}" href="{esc(rss_pair[1])}" />\n'
        )
    scripts = "\n".join(f'  <script type="application/ld+json">{b}</script>' for b in blobs)
    return (
        f"  <title>{esc(full)}</title>\n"
        f'  <meta name="description" content="{esc(desc)}" />\n'
        f'  <meta name="robots" content="{esc(robots_content)}" />\n'
        f'  <meta name="googlebot" content="{esc(robots_content)}" />\n'
        f'  <meta name="theme-color" content="{esc(meta["theme"])}" />\n'
        f'  <link rel="canonical" href="{esc(canonical)}" />\n'
        f'  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
        f'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
        f'  <link rel="stylesheet" href="{esc(FONT_HREF)}" />\n'
        f'  <link rel="apple-touch-icon" href="{esc(logo)}" />\n'
        f"{rss_link}"
        f'  <meta property="og:type" content="{esc(og_type)}" />\n'
        f'  <meta property="og:site_name" content="{esc(brand)}" />\n'
        f'  <meta property="og:title" content="{esc(full)}" />\n'
        f'  <meta property="og:description" content="{esc(desc)}" />\n'
        f'  <meta property="og:url" content="{esc(canonical)}" />\n'
        f'  <meta property="og:image" content="{esc(img)}" />'
        f"{og_extra}\n"
        f'  <meta name="twitter:card" content="summary_large_image" />\n'
        f'  <meta name="twitter:title" content="{esc(full)}" />\n'
        f'  <meta name="twitter:description" content="{esc(desc)}" />\n'
        f'  <meta name="twitter:image" content="{esc(img)}" />\n'
        f"{scripts}"
    )


def _fmt_bar(v: float) -> str:
    if abs(v - round(v)) < 0.05:
        return f"{int(round(v)):,}"
    return f"{v:,.1f}"


def rank_spread_graph(ranks: dict, fill: str = "#c8102e", kicker: str = "Board graph") -> str:
    if not ranks:
        return ""
    items = sorted(ranks.items(), key=lambda kv: kv[1])
    if len(items) < 2:
        return ""
    shown = items[:18]
    max_r = max(rk for _s, rk in shown) or 1
    rows = []
    for src, rk in shown:
        pct = max(10, min(100, round(100 * (max_r + 1 - rk) / max_r)))
        rows.append(
            f'<div class="bar-row"><span class="bar-lab">{esc(src)}</span>'
            f'<div class="bar-track"><span class="bar-fill" style="width:{pct}%;background:{esc(fill)}"></span></div>'
            f'<span class="bar-val">#{rk}</span></div>'
        )
    lo, hi = items[0][1], items[-1][1]
    return (
        '<section class="panel graph">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h3>Spread {lo}–{hi} · {len(items)} sources</h3>"
        f'<div class="bar-chart" role="img" aria-label="Rank on every published board">'
        f"{''.join(rows)}</div></section>"
    )


def value_bars(
    rows: list,
    n: int = 12,
    fill: str = "#c8102e",
    kicker: str = "Value graph",
    key: str = "value",
    heading: str | None = None,
    note: str | None = None,
) -> str:
    top = []
    for r in (rows or [])[:n]:
        try:
            val = float(r.get(key) or 0)
        except (TypeError, ValueError):
            val = 0.0
        if val:
            top.append((r, val))
    if len(top) < 3:
        return ""
    mx = max(v for _r, v in top) or 1
    bars = []
    for r, val in top:
        pct = max(8, min(100, round(100 * val / mx)))
        name = r.get("name") or ""
        rk = r.get("bk") or ""
        bars.append(
            f'<div class="bar-row"><span class="bar-lab">#{rk} {esc(name)}</span>'
            f'<div class="bar-track"><span class="bar-fill" style="width:{pct}%;background:{esc(fill)}"></span></div>'
            f'<span class="bar-val">{_fmt_bar(val)}</span></div>'
        )
    if heading is None:
        heading = f"BK Value, top {len(top)}" if key == "value" else f"Top {len(top)}"
    if note is None and key == "value":
        note = "Rank 1 is 12,000. The curve decays so mid-board names still trade, they just do not trade like 1.01."
    note_html = f'<p class="note">{esc(note)}</p>' if note else ""
    return (
        '<section class="panel graph">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h3>{esc(heading)}</h3>"
        f"{note_html}"
        f'<div class="bar-chart" role="img" aria-label="{esc(heading)}">'
        f"{''.join(bars)}</div></section>"
    )


def dual_metric_graph(pairs, kicker: str = "Points graph", fill_a: str = "#e8c547", fill_b: str = "#00c853") -> str:
    cleaned = []
    for item in pairs:
        if len(item) == 3:
            label, color, val = item
        else:
            continue
        try:
            n = float(val or 0)
        except (TypeError, ValueError):
            n = 0.0
        if n:
            cleaned.append((label, color, n))
    if len(cleaned) < 2:
        return ""
    mx = max(v for _l, _c, v in cleaned) or 1
    rows = []
    for label, color, val in cleaned:
        pct = max(8, min(100, round(100 * val / mx)))
        rows.append(
            f'<div class="bar-row"><span class="bar-lab">{esc(label)}</span>'
            f'<div class="bar-track"><span class="bar-fill" style="width:{pct}%;background:{esc(color)}"></span></div>'
            f'<span class="bar-val">{_fmt_bar(val)}</span></div>'
        )
    return (
        '<section class="panel graph">'
        f'<p class="kicker">{esc(kicker)}</p>'
        "<h3>Same 2025/26 line, two scoring tables</h3>"
        f'<div class="bar-chart" role="img" aria-label="Sleeper BPL points versus official FPL points">'
        f"{''.join(rows)}</div></section>"
    )


def face_alt(name: str) -> str:
    n = (name or "").strip()
    return f"{n} headshot" if n else "Player headshot"


def card_alt(name: str) -> str:
    n = (name or "").strip()
    return n or "Player"


def clip_label(text: str, n: int = 48) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= n:
        return t
    cut = t[: n - 1].rsplit(" ", 1)[0]
    return (cut or t[: n - 1]).rstrip(".,;:") + "…"


def breadcrumbs(trail: list) -> str:
    """trail: [(label, href_or_None), ...] — last item is the current page."""
    items = [(str(label or "").strip(), href) for label, href in (trail or []) if label]
    if len(items) < 2:
        return ""
    lis = []
    for i, (label, href) in enumerate(items):
        last = i == len(items) - 1
        if href and not last:
            lis.append(f'<li><a href="{esc(href)}">{esc(label)}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{esc(clip_label(label))}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def breadcrumb_jsonld(trail_abs: list) -> dict | None:
    """trail_abs: [(label, absolute_url), ...]"""
    items = [(str(label or "").strip(), url) for label, url in (trail_abs or []) if label and url]
    if len(items) < 2:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": label, "item": url}
            for i, (label, url) in enumerate(items, 1)
        ],
    }


def person_jsonld(
    name: str,
    url: str,
    *,
    pos: str = "",
    team: str = "",
    image: str = "",
    description: str = "",
    sport: str = "",
) -> dict:
    obj = {
        "@context": "https://schema.org",
        "@type": ["Person", "Athlete"] if sport or pos else "Person",
        "name": name,
        "url": url,
    }
    if pos:
        obj["jobTitle"] = pos
    if team:
        obj["affiliation"] = {"@type": "SportsTeam", "name": team}
        obj["memberOf"] = {"@type": "SportsTeam", "name": team}
    if image:
        obj["image"] = abs_img(image, "img/logo.jpg")
    if description:
        obj["description"] = clip(description, 200)
    if sport:
        obj["sport"] = sport
    return obj


def article_jsonld(
    headline: str,
    url: str,
    description: str,
    *,
    published: str = "",
    modified: str = "",
    image: str = "",
    brand: str = "Ball Keep",
    brand_url: str | None = None,
    section: str = "",
) -> dict:
    meta = _brand_meta(brand, brand_url)
    home = meta["url"]
    logo = abs_img(meta["logo"], meta["logo"])
    obj = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": clip(headline, 110),
        "description": clip(description, 200),
        "url": url,
        "mainEntityOfPage": url,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": home,
            "logo": {"@type": "ImageObject", "url": logo},
        },
        "author": {"@type": "Organization", "name": brand, "url": home},
    }
    if image:
        obj["image"] = abs_img(image, meta["logo"])
    if published:
        obj["datePublished"] = published
    if modified or published:
        obj["dateModified"] = modified or published
    if section:
        obj["articleSection"] = section
    return obj


def also_on_desk(
    tiles: list,
    kicker: str = "Also on this board",
    heading: str = "Keep going.",
) -> str:
    """tiles: [(href, title, note), ...] — sibling boards, calculators, hubs."""
    tiles = [t for t in (tiles or []) if t and t[0] and t[1]]
    if not tiles:
        return ""
    cards = "".join(
        f'<a class="tile" href="{esc(h)}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>'
        for h, t, p in tiles
    )
    cols = "grid" if len(tiles) <= 2 else "grid-3"
    return (
        f'<section class="related related-boards" aria-label="{esc(kicker)}">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h2>{esc(heading)}</h2>"
        f'<div class="{cols}">{cards}</div>'
        "</section>"
    )


def footer_nav(items: list, current_path: str = "") -> str:
    """items: [(href, label), ...] with hrefs already resolved for the page depth."""
    bits = []
    for href, label in items or []:
        if not href or not label or label == "Home":
            continue
        if href == current_path:
            continue
        bits.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    if not bits:
        return ""
    return f'<nav class="footer-nav" aria-label="On this board">{"".join(bits)}</nav>'


def _rank_int(row: dict, rank_key: str = "bk") -> int:
    try:
        return int(row.get(rank_key) or 0)
    except (TypeError, ValueError):
        return 0


def _pos0(pos: str) -> str:
    return (pos or "").split("/")[0].split(",")[0].strip().upper()


def _team0(team: str) -> str:
    return (team or "").strip().upper()


def related_players_html(
    rows: list,
    current: dict,
    href_fn,
    *,
    name_key: str = "name",
    pos_key: str = "pos",
    team_key: str = "team",
    rank_key: str = "bk",
    id_key: str = "key",
    nearby_label: str = "On this board nearby",
    pos_label: str = "Same position",
    team_label: str = "Same club",
) -> str:
    """Neighbors, teammates, and same-position names — crawl paths off a player file."""
    if not rows or not current:
        return ""
    cid = current.get(id_key)
    idx = next((i for i, r in enumerate(rows) if cid and r.get(id_key) == cid), None)
    if idx is None:
        cname = current.get(name_key)
        idx = next((i for i, r in enumerate(rows) if cname and r.get(name_key) == cname), None)
    shown = {cid} if cid else set()

    def link_row(r: dict) -> str:
        href = href_fn(r) if href_fn else None
        name = r.get(name_key) or ""
        rk = r.get(rank_key)
        extra = f" (#{rk})" if rk not in (None, "") else ""
        if href:
            return f'<a class="player-link" href="{esc(href)}">{esc(name)}</a>{esc(extra)}'
        return f"<strong>{esc(name)}</strong>{esc(extra)}"

    sections = []
    if idx is not None:
        nearby = rows[max(0, idx - 2) : idx] + rows[idx + 1 : idx + 3]
        for r in nearby:
            if r.get(id_key):
                shown.add(r.get(id_key))
        if nearby:
            sections.append((nearby_label, nearby))

    crk = _rank_int(current, rank_key)
    team = _team0(current.get(team_key) or "")
    if team:
        cands = [
            r for r in rows
            if r.get(id_key) not in shown and _team0(r.get(team_key) or "") == team
        ]
        cands.sort(key=lambda r: abs(_rank_int(r, rank_key) - crk))
        teammates = cands[:5]
        for r in teammates:
            if r.get(id_key):
                shown.add(r.get(id_key))
        if teammates:
            sections.append((team_label, teammates))

    pos = _pos0(current.get(pos_key) or "")
    if pos:
        cands = [
            r for r in rows
            if r.get(id_key) not in shown and _pos0(r.get(pos_key) or "") == pos
        ]
        cands.sort(key=lambda r: abs(_rank_int(r, rank_key) - crk))
        same = cands[:5]
        if same:
            sections.append((pos_label, same))

    if not sections:
        return ""
    body = "".join(
        f'<p class="related-row"><strong>{esc(label)}</strong> {" · ".join(link_row(r) for r in group)}</p>'
        for label, group in sections
    )
    return (
        '<section class="related related-players" aria-label="Related players">'
        '<p class="kicker">Related</p>'
        "<h2>More names on this board</h2>"
        f"{body}</section>"
    )


def related_stories_html(
    stories: list,
    current: dict,
    href_fn,
    *,
    limit: int = 5,
    heading: str = "More on this wire",
) -> str:
    """Stories that share players, then same category, then latest — so crawlers leave the leaf."""
    if not stories or not current:
        return ""
    cur_slug = current.get("slug")
    cur_keys = {p.get("key") for p in (current.get("players") or []) if p.get("key")}
    cur_cat = current.get("category") or ""
    others = [s for s in stories if s.get("slug") and s.get("slug") != cur_slug]
    if not others:
        return ""

    def score(s: dict) -> tuple:
        keys = {p.get("key") for p in (s.get("players") or []) if p.get("key")}
        shared = len(cur_keys & keys)
        same_cat = 1 if cur_cat and s.get("category") == cur_cat else 0
        return (shared, same_cat, s.get("updated") or s.get("published") or "")

    others.sort(key=score, reverse=True)
    picked = others[:limit]
    cards = []
    for s in picked:
        href = href_fn(s) if href_fn else None
        if not href:
            continue
        blurb = clip(s.get("blurb") or s.get("summary") or "", 110)
        cards.append(
            f'<a class="tile" href="{esc(href)}"><h3>{esc(s.get("headline") or "Update")}</h3>'
            f"<p>{esc(blurb)}</p></a>"
        )
    if not cards:
        return ""
    cols = "grid" if len(cards) <= 2 else "grid-3"
    return (
        f'<section class="related related-news" aria-label="{esc(heading)}">'
        '<p class="kicker">Related</p>'
        f"<h2>{esc(heading)}</h2>"
        f'<div class="{cols}">{"".join(cards)}</div>'
        "</section>"
    )


def sitemap_xml(urls: list, lastmod: str) -> str:
    rows = []
    seen = set()
    has_image = False
    for u in urls or []:
        if isinstance(u, dict):
            loc = (u.get("loc") or "").strip()
            image = (u.get("image") or "").strip()
            image_title = u.get("image_title") or ""
            when = u.get("lastmod") or lastmod
        else:
            loc = (u or "").strip()
            image = ""
            image_title = ""
            when = lastmod
        if not loc or loc in seen:
            continue
        seen.add(loc)
        inner = f"<loc>{loc}</loc><lastmod>{esc(when)}</lastmod>"
        if image:
            has_image = True
            title = f"<image:title>{esc(image_title)}</image:title>" if image_title else ""
            inner += f"<image:image><image:loc>{esc(image)}</image:loc>{title}</image:image>"
        rows.append(f"  <url>{inner}</url>\n")
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
    if has_image:
        ns += ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<urlset {ns}>\n"
        + "".join(rows)
        + "</urlset>\n"
    )


def item_list_jsonld(name: str, url: str, items: list, *, description: str = "") -> dict | None:
    """items: [(name, url), ...] — first 25 names on a ranking board."""
    shown = [(str(n or "").strip(), u) for n, u in (items or []) if n and u][:25]
    if len(shown) < 3:
        return None
    obj = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "url": url,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(shown),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "url": u}
            for i, (n, u) in enumerate(shown, 1)
        ],
    }
    if description:
        obj["description"] = clip(description, 200)
    return obj


def rank_list_jsonld(name: str, url: str, rows: list, href_fn, *, description: str = "", limit: int = 25) -> dict | None:
    items = []
    for r in (rows or [])[:limit]:
        label = (r or {}).get("name")
        href = href_fn(r) if href_fn and r else None
        if label and href:
            items.append((label, href))
    return item_list_jsonld(name, url, items, description=description)


def faq_jsonld(pairs: list) -> dict | None:
    qs = [(str(q or "").strip(), str(a or "").strip()) for q, a in (pairs or []) if q and a]
    if len(qs) < 2:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qs
        ],
    }


def faq_html(
    pairs: list,
    kicker: str = "FAQ",
    heading: str = "How this board works.",
) -> str:
    qs = [(str(q or "").strip(), str(a or "").strip()) for q, a in (pairs or []) if q and a]
    if not qs:
        return ""
    items = "".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        for q, a in qs
    )
    return (
        f'<section class="faq" aria-label="{esc(kicker)}">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h2>{esc(heading)}</h2>"
        f"{items}</section>"
    )


def video_jsonld(
    name: str,
    youtube_id: str,
    *,
    description: str = "",
    brand: str = "Ball Keep",
    brand_url: str | None = None,
) -> dict | None:
    yt = (youtube_id or "").strip()
    if not yt:
        return None
    meta = _brand_meta(brand, brand_url)
    return {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": name,
        "description": clip(description or name, 200),
        "embedUrl": f"https://www.youtube.com/embed/{yt}",
        "thumbnailUrl": f"https://i.ytimg.com/vi/{yt}/hqdefault.jpg",
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": meta["url"],
            "logo": {"@type": "ImageObject", "url": abs_img(meta["logo"], meta["logo"])},
        },
    }


def _rfc822(iso: str) -> str:
    from datetime import datetime, timezone

    raw = (iso or "").strip()
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
    except ValueError:
        return raw


def _iso_z(raw: str) -> str:
    t = (raw or "").strip()
    if not t:
        return ""
    if t.endswith("Z") or "+" in t[10:]:
        return t
    if "T" in t:
        return t + "Z"
    if len(t) == 10:
        return t + "T00:00:00Z"
    return t


def rss_xml(
    *,
    title: str,
    link: str,
    description: str,
    items: list,
    self_url: str = "",
    language: str = "en-us",
) -> str:
    """items: dicts with title, link, description, date, guid."""
    bits = []
    for it in items or []:
        loc = it.get("link") or ""
        head = it.get("title") or "Update"
        if not loc:
            continue
        when = _rfc822(it.get("date") or "")
        desc = clip(it.get("description") or head, 280)
        guid = it.get("guid") or loc
        pub = f"      <pubDate>{esc(when)}</pubDate>\n" if when else ""
        bits.append(
            "    <item>\n"
            f"      <title>{esc(head)}</title>\n"
            f"      <link>{esc(loc)}</link>\n"
            f"      <guid isPermaLink=\"true\">{esc(guid)}</guid>\n"
            f"{pub}"
            f"      <description>{esc(desc)}</description>\n"
            "    </item>\n"
        )
    atom = f'    <atom:link href="{esc(self_url)}" rel="self" type="application/rss+xml" />\n' if self_url else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{esc(title)}</title>\n"
        f"    <link>{esc(link)}</link>\n"
        f"    <description>{esc(description)}</description>\n"
        f"    <language>{esc(language)}</language>\n"
        f"{atom}"
        + "".join(bits)
        + "  </channel>\n"
        "</rss>\n"
    )


def news_sitemap_xml(entries: list) -> str:
    """entries: dicts with loc, title, date, publication."""
    rows = []
    seen = set()
    for e in entries or []:
        loc = (e.get("loc") or "").strip()
        title = (e.get("title") or "").strip()
        when = _iso_z(e.get("date") or "")
        pub = (e.get("publication") or "Ball Keep").strip()
        if not loc or loc in seen or not title or not when:
            continue
        seen.add(loc)
        rows.append(
            "  <url>\n"
            f"    <loc>{esc(loc)}</loc>\n"
            "    <news:news>\n"
            "      <news:publication>\n"
            f"        <news:name>{esc(pub)}</news:name>\n"
            "        <news:language>en</news:language>\n"
            "      </news:publication>\n"
            f"      <news:publication_date>{esc(when)}</news:publication_date>\n"
            f"      <news:title>{esc(title)}</news:title>\n"
            "    </news:news>\n"
            "  </url>\n"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'
        + "".join(rows)
        + "</urlset>\n"
    )


def rank_search_key(*parts: str) -> str:
    """Lowercased name/pos/team blob for ranking-row search."""
    bits = []
    seen = set()
    for p in parts:
        t = " ".join(str(p or "").split())
        if not t:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        bits.append(t)
    return html.escape(" ".join(bits).lower(), quote=True)


def rank_search_js() -> str:
    return """<script>
(function () {
  function needle() {
    var inp = document.querySelector(".rank-search-input");
    return inp ? String(inp.value || "").trim().toLowerCase() : "";
  }
  function wantPos() {
    var btn = document.querySelector(".rank-bar .filters button.active")
      || document.querySelector(".filters button.active");
    if (!btn) return "all";
    return String(btn.getAttribute("data-pos") || btn.getAttribute("data-group") || "all").toLowerCase();
  }
  window.applyRankFilter = function () {
    var q = needle();
    var pos = wantPos();
    document.querySelectorAll("table.rank-table tbody tr").forEach(function (tr) {
      var hay = (tr.getAttribute("data-name") || "").toLowerCase();
      var nameOk = !q || hay.indexOf(q) !== -1;
      var rowPos = (tr.getAttribute("data-pos") || "").toLowerCase();
      var rowGroup = (tr.getAttribute("data-group") || "").toLowerCase();
      var posOk = pos === "all" || rowPos === pos || rowGroup === pos;
      tr.style.display = (nameOk && posOk) ? "" : "none";
    });
  };
  document.addEventListener("input", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("rank-search-input")) {
      window.applyRankFilter();
    }
  });
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".rank-bar .filters button");
    if (!b) return;
    var box = b.closest(".filters");
    if (!box) return;
    box.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
    b.classList.add("active");
    window.applyRankFilter();
  });
})();
</script>
"""


def rank_search_bar(filters: str = "") -> str:
    """Player search plus optional position chips above a ranking table."""
    return (
        '<div class="rank-bar">'
        '<p class="rank-search">'
        '<input type="search" class="rank-search-input" placeholder="Find a player" '
        'aria-label="Find a player" autocomplete="off" spellcheck="false">'
        "</p>"
        f"{filters}"
        "</div>"
        + rank_search_js()
    )


def draft_check_js() -> str:
    """Session-only taken marks. No storage: a refresh clears every box."""
    return """<script>
(function () {
  document.addEventListener("click", function (e) {
    var mark = e.target && e.target.closest && e.target.closest(".draft-mark");
    if (mark) e.stopPropagation();
  });
  document.addEventListener("change", function (e) {
    var cb = e.target;
    if (!cb || !cb.classList || !cb.classList.contains("draft-check")) return;
    var tr = cb.closest("tr");
    if (!tr) return;
    tr.classList.toggle("crossed-off", !!cb.checked);
  });
})();
</script>
"""


def robots_txt(sitemaps: list) -> str:
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: Googlebot",
        "Allow: /",
        "",
        "User-agent: Googlebot-News",
        "Allow: /",
        "",
        "User-agent: Googlebot-Image",
        "Allow: /",
        "",
    ]
    for sm in sitemaps or []:
        if sm:
            lines.append(f"Sitemap: {sm}")
    lines.append("")
    return "\n".join(lines)
