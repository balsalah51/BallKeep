"""Unique titles, descriptions, Open Graph, internal links, and bar graphs."""
from __future__ import annotations

import html
import json
import re
from datetime import date

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


def ld_script(obj: dict) -> str:
    return f'  <script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def head_tags(
    *,
    title: str,
    description: str,
    canonical: str,
    image: str,
    brand: str,
    og_type: str = "website",
    extra_ld: list | None = None,
) -> str:
    full = branded(title, brand)
    desc = clip(description, 168)
    img = abs_img(image, "img/logo.jpg")
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": full,
        "description": desc,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": brand, "url": SITE},
        "primaryImageOfPage": {"@type": "ImageObject", "url": img},
    }
    scripts = [ld_script(jsonld)]
    for extra in extra_ld or []:
        if extra:
            scripts.append(ld_script(extra))
    return (
        f"  <title>{esc(full)}</title>\n"
        f'  <meta name="description" content="{esc(desc)}" />\n'
        f'  <link rel="canonical" href="{esc(canonical)}" />\n'
        f'  <meta property="og:type" content="{esc(og_type)}" />\n'
        f'  <meta property="og:site_name" content="{esc(brand)}" />\n'
        f'  <meta property="og:title" content="{esc(full)}" />\n'
        f'  <meta property="og:description" content="{esc(desc)}" />\n'
        f'  <meta property="og:url" content="{esc(canonical)}" />\n'
        f'  <meta property="og:image" content="{esc(img)}" />\n'
        f'  <meta name="twitter:card" content="summary_large_image" />\n'
        f'  <meta name="twitter:title" content="{esc(full)}" />\n'
        f'  <meta name="twitter:description" content="{esc(desc)}" />\n'
        f'  <meta name="twitter:image" content="{esc(img)}" />\n'
        + "\n".join(scripts)
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


def crumbs_html(items) -> str:
    """Visible breadcrumb trail. items: [(href_or_empty, label), ...] last is current."""
    items = [(h, l) for h, l in (items or []) if l]
    if len(items) < 2:
        return ""
    bits = []
    for i, (href, label) in enumerate(items):
        last = i == len(items) - 1
        if last or not href:
            bits.append(f'<span aria-current="page">{esc(label)}</span>')
        else:
            bits.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    return (
        '<nav class="crumbs" aria-label="Breadcrumb">'
        + '<span class="crumbs-sep" aria-hidden="true"> / </span>'.join(bits)
        + "</nav>"
    )


def path_crumbs(path: str, title: str, *, home_href: str, players_href: str, news_href: str) -> list:
    """Home → hub → current. Empty on the sport homepage."""
    if path in ("index.html", "", None):
        return []
    items = [(home_href, "Home")]
    if path.startswith("news/") and path != "news.html":
        items.append((news_href, "News"))
    elif path.startswith("players/") and path != "players/index.html":
        items.append((players_href, "Players"))
    short = (title or path).strip()
    if len(short) > 48:
        short = short[:47].rsplit(" ", 1)[0] + "…"
    items.append(("", short or "This page"))
    return items


def related_tiles(kicker: str, heading: str, tiles) -> str:
    """tiles: [(href, title, blurb)]"""
    tiles = [(h, t, p) for h, t, p in (tiles or []) if h and t]
    if not tiles:
        return ""
    cards = "".join(
        f'<a class="tile" href="{esc(h)}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>'
        for h, t, p in tiles
    )
    cols = "grid" if len(tiles) <= 2 else "grid-3"
    return (
        f'<section class="related desk-block" aria-label="{esc(heading)}">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h2>{esc(heading)}</h2>"
        f'<div class="{cols}">{cards}</div>'
        "</section>"
    )


def related_names(label: str, items) -> str:
    """items: [(href, name, note)]"""
    items = [(h, n, note) for h, n, note in (items or []) if n]
    if not items:
        return ""
    links = []
    for href, name, note in items:
        text = f"<strong>{esc(name)}</strong>"
        if href:
            text = f'<a class="player-link" href="{esc(href)}">{text}</a>'
        if note:
            text = f"{text} ({esc(note)})"
        links.append(text)
    return f'<p class="note related-names"><strong>{esc(label)}</strong> — {" · ".join(links)}</p>'


def nearby_window(rows: list, idx: int, n: int = 2) -> list:
    if idx is None or idx < 0 or not rows:
        return []
    return rows[max(0, idx - n) : idx] + rows[idx + 1 : idx + n + 1]


def same_field(rows: list, current: dict, field: str, *, key: str = "key", limit: int = 6) -> list:
    val = (current.get(field) or "").strip()
    if not val:
        return []
    ck = current.get(key)
    out = []
    for r in rows:
        if r.get(key) == ck:
            continue
        if (r.get(field) or "").strip() == val:
            out.append(r)
            if len(out) >= limit:
                break
    return out


def related_news(stories: list, current: dict, n: int = 5) -> list:
    """Stories that share players, then same category, then recency."""
    cur_slug = current.get("slug")
    cur_keys = {
        (p.get("key") or p.get("name") or "").strip().lower()
        for p in (current.get("players") or [])
        if p
    }
    cur_keys.discard("")
    cur_cat = current.get("category")
    scored = []
    for s in stories or []:
        if not s.get("slug") or s.get("slug") == cur_slug:
            continue
        keys = {
            (p.get("key") or p.get("name") or "").strip().lower()
            for p in (s.get("players") or [])
            if p
        }
        keys.discard("")
        shared = len(cur_keys & keys)
        cat = 1 if (cur_cat and s.get("category") == cur_cat) else 0
        scored.append((shared * 10 + cat, s))
    scored.sort(key=lambda kv: -kv[0])
    picked = []
    seen = {cur_slug}
    for score, s in scored:
        if score <= 0:
            break
        slug = s.get("slug")
        if slug in seen:
            continue
        picked.append(s)
        seen.add(slug)
        if len(picked) >= n:
            return picked
    for s in stories or []:
        slug = s.get("slug")
        if not slug or slug in seen:
            continue
        picked.append(s)
        seen.add(slug)
        if len(picked) >= n:
            break
    return picked


def related_news_html(stories: list, *, href_prefix: str = "") -> str:
    tiles = []
    for s in stories or []:
        slug = s.get("slug")
        if not slug:
            continue
        tiles.append((
            f"{href_prefix}{slug}.html",
            s.get("headline") or "Update",
            clip(s.get("blurb") or s.get("summary") or "", 110),
        ))
    return related_tiles("Related tape", "More from this desk", tiles)


def story_card(
    *,
    href: str,
    category: str,
    label: str,
    when: str,
    headline: str,
    blurb: str,
    player_html: str,
    nsrc: int,
    kinds,
) -> str:
    """News hub card: headline links to the story, player chips can be their own links."""
    bits = [f"{nsrc} source" + ("s" if nsrc != 1 else "")]
    kinds = set(kinds or [])
    if "x" in kinds:
        bits.append("X")
    if "video" in kinds:
        bits.append("video")
    chips = f'<div class="news-players">{player_html}</div>' if player_html else ""
    return (
        '<article class="news-item tile">'
        f'<a class="news-main" href="{esc(href)}">'
        f'<div class="news-meta"><span class="kind {esc(category)}">{esc(label)}</span> '
        f'{esc(when)} · {esc(" · ".join(bits))}</div>'
        f"<h3>{esc(headline or 'Update')}</h3>"
        f"<p>{esc(blurb or '')}</p>"
        "</a>"
        f"{chips}"
        "</article>"
    )


def person_ld(
    *,
    name: str,
    url: str,
    image: str,
    description: str,
    sport: str,
    team: str = "",
    pos: str = "",
) -> dict:
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": url,
        "image": abs_img(image, "img/logo.jpg"),
        "description": clip(description, 200),
        "sport": sport,
    }
    if team:
        obj["memberOf"] = {"@type": "SportsTeam", "name": team}
    if pos:
        obj["jobTitle"] = pos
    return obj


def news_ld(
    *,
    headline: str,
    url: str,
    description: str,
    image: str,
    brand: str,
    published: str = "",
    updated: str = "",
) -> dict:
    obj = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": clip(headline, 110),
        "url": url,
        "description": clip(description, 200),
        "image": abs_img(image, "img/logo.jpg"),
        "publisher": {
            "@type": "Organization",
            "name": brand,
            "url": SITE,
            "logo": {"@type": "ImageObject", "url": f"{SITE}/img/logo.jpg"},
        },
        "mainEntityOfPage": url,
    }
    if published:
        obj["datePublished"] = published
    if updated:
        obj["dateModified"] = updated
    return obj


def footer_nav(links) -> str:
    """Compact internal-link row under the copyright line."""
    links = [(h, l) for h, l in (links or []) if h and l]
    if not links:
        return ""
    bits = " · ".join(f'<a href="{esc(h)}">{esc(l)}</a>' for h, l in links)
    return f'<p class="footer-nav">{bits}</p>'


def sr_only(text: str) -> str:
    return f'<h1 class="sr-only">{esc(text)}</h1>'


def sitemap_xml(urls, lastmod: str | None = None) -> str:
    lastmod = lastmod or date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen = set()
    for u in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        pri = "0.5"
        path = u.replace(SITE, "") or "/"
        if path in ("/", ""):
            pri = "1.0"
        elif path in ("/the-keep.html", "/board.html", "/news.html", "/bb/", "/bk/", "/pl/", "/explore.html"):
            pri = "0.9"
        elif path.endswith("/players/") or path.endswith("players/index.html"):
            pri = "0.8"
        elif path.endswith("the-keep.html") or path.endswith("the-premier.html") or path.endswith("the-pitch.html"):
            pri = "0.8"
        lines.append(
            f"  <url><loc>{html.escape(u, quote=True)}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
            f"<changefreq>daily</changefreq>"
            f"<priority>{pri}</priority></url>"
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"
