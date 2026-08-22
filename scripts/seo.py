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
    blob = json.dumps(jsonld, ensure_ascii=False)
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
        f'  <script type="application/ld+json">{blob}</script>'
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
