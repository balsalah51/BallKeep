"""Unique titles, descriptions, Open Graph, and bar graphs for Ball Keep pages."""
from __future__ import annotations

import html
import json
import re

SITE = "https://ballkeep.com"

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
) -> str:
    full = branded(title, brand)
    desc = clip(description, 168)
    img = abs_img(image, "img/logo.jpg")
    home = brand_url or SITE
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": full,
        "description": desc,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": brand, "url": home},
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": home,
            "logo": {"@type": "ImageObject", "url": img},
        },
        "primaryImageOfPage": {"@type": "ImageObject", "url": img},
    }
    blobs = [json.dumps(jsonld, ensure_ascii=False)]
    for extra in extra_jsonld or []:
        if extra:
            blobs.append(json.dumps(extra, ensure_ascii=False))
    og_extra = ""
    if published:
        og_extra += f'\n  <meta property="article:published_time" content="{esc(published)}" />'
    if modified:
        og_extra += f'\n  <meta property="article:modified_time" content="{esc(modified)}" />'
    scripts = "\n".join(f'  <script type="application/ld+json">{b}</script>' for b in blobs)
    return (
        f"  <title>{esc(full)}</title>\n"
        f'  <meta name="description" content="{esc(desc)}" />\n'
        f'  <link rel="canonical" href="{esc(canonical)}" />\n'
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
) -> dict:
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": url,
    }
    if pos:
        obj["jobTitle"] = pos
    if team:
        obj["affiliation"] = {"@type": "SportsTeam", "name": team}
    if image:
        obj["image"] = abs_img(image, "img/logo.jpg")
    if description:
        obj["description"] = clip(description, 200)
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
) -> dict:
    home = brand_url or SITE
    obj = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": clip(headline, 110),
        "description": clip(description, 200),
        "url": url,
        "mainEntityOfPage": url,
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": home,
            "logo": {"@type": "ImageObject", "url": f"{SITE}/img/logo.jpg"},
        },
        "author": {"@type": "Organization", "name": brand, "url": home},
    }
    if image:
        obj["image"] = abs_img(image, "img/logo.jpg")
    if published:
        obj["datePublished"] = published
    if modified or published:
        obj["dateModified"] = modified or published
    return obj


def also_on_desk(
    tiles: list,
    kicker: str = "Also on this desk",
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
    return f'<nav class="footer-nav" aria-label="On this desk">{"".join(bits)}</nav>'


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
        "<h2>More names on this desk</h2>"
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
    for u in urls or []:
        if not u or u in seen:
            continue
        seen.add(u)
        rows.append(f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>\n")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(rows)
        + "</urlset>\n"
    )
