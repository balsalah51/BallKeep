"""DeepBase: four baseball boards from one shared source.

Deep Dynasty, Deep Farm, Majors, and Lineups are built here and written to
both /bb/ and /deepbase/ so the copies always match.
"""
from __future__ import annotations

import html
from datetime import date
from pathlib import Path

from bb_data import (  # noqa: E402
    aggregate,
    as_map,
    build_meta,
    filter_group,
    load_fp_dynasty,
    load_raw,
)
from bb_prospects import FARM_SOURCES, load_farm  # noqa: E402
from bk_curve import bk_value  # noqa: E402
from seo import (  # noqa: E402
    CHROME_VER,
    breadcrumb_jsonld,
    breadcrumbs,
    canon,
    faq_html,
    faq_jsonld,
    grouped_nav,
    theme_toggle_btn,
    head_tags,
    legal_links,
    rank_list_jsonld,
    rank_search_bar,
    slim_banner,
    sports_footer,
    sports_top,
    sr_h1,
    strip_em,
    theme_boot,
    website_jsonld,
)

ROOT = Path(__file__).resolve().parents[1]
UPDATED = date.today().strftime("%B %-d, %Y")
DEEP_ACCENT = "#0d9488"

DEEP_SOURCES = [
    ("RotoGraphs Dynasty Model", "https://fantasy.fangraphs.com/rotographs-dynasty-rankings/", "Top 500 discounted-dollar model."),
    ("The Dynasty Guru - Points", "https://thedynastyguru.com/2026/08/10/the-tdg-top-500-for-points-leagues-2026-mid-season-updates/", "Mid-season Top 500."),
    ("FantasyPros Dynasty ECR", "https://www.fantasypros.com/mlb/rankings/dynasty-overall.php", "Keeper and dynasty expert consensus."),
]

PAGES = [
    {
        "id": "deep-dynasty",
        "file": "deep-dynasty.html",
        "title": "Deep Dynasty",
        "nav": "Deep Dynasty",
        "kicker": "Full tape · majors and farm",
        "blurb": "The long dynasty board. Majors plus prospects, mashed from the three deep lists.",
        "seo_title": "Deep Dynasty Baseball Rankings | DeepBase",
        "seo_desc": "Deep dynasty baseball full tape: major leaguers and prospects from RotoGraphs, The Dynasty Guru, and FantasyPros.",
    },
    {
        "id": "deep-farm",
        "file": "deep-farm.html",
        "title": "Deep Farm",
        "nav": "Deep Farm",
        "kicker": "Prospects past the top 100",
        "blurb": "Every ranked prospect on the five farm lists, not just the top 100.",
        "seo_title": "Deep Farm MLB Prospect Rankings | DeepBase",
        "seo_desc": "Deep MLB prospect rankings beyond the top 100. Pipeline, Baseball America, ESPN, SI, and FanGraphs.",
    },
    {
        "id": "majors",
        "file": "majors.html",
        "title": "Majors",
        "nav": "Majors",
        "kicker": "Big-league dynasty only",
        "blurb": "Dynasty ranks with the farm stripped out. Everyday majors, no kids.",
        "seo_title": "MLB Majors Dynasty Rankings | DeepBase",
        "seo_desc": "Dynasty baseball rankings for major-league names only. Prospects live on Deep Farm.",
    },
    {
        "id": "lineups",
        "file": "lineups.html",
        "title": "Lineups",
        "nav": "Lineups",
        "kicker": "Everyday bats",
        "blurb": "Who starts. Hitters only, ranked for a standard mixed-league lineup.",
        "seo_title": "Fantasy Baseball Lineup Rankings | DeepBase",
        "seo_desc": "Everyday hitter rankings for fantasy lineups. Catcher through outfield, majors only.",
    },
]

DEEPBASE_NAV_GROUPS = [
    ("rankings", "Rankings", [
        ("index.html", "Home"),
        ("deep-dynasty.html", "Deep Dynasty"),
        ("deep-farm.html", "Deep Farm"),
        ("majors.html", "Majors"),
        ("lineups.html", "Lineups"),
    ]),
    ("more", "More", [
        ("../bb/index.html", "BaseKeep"),
    ]),
]


def esc(s):
    return html.escape(str(s), quote=True)


def rerank(rows):
    out = [dict(r) for r in rows]
    out.sort(key=lambda r: (r.get("avg") or 999, -(r.get("n") or 0), r.get("name") or ""))
    for i, r in enumerate(out, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return out


def load_boards() -> dict:
    """One shared payload for BaseKeep and DeepBase copies."""
    rg, tdg = load_raw()
    meta = build_meta(rg, tdg)
    sources = {
        "RotoGraphs Model": as_map(rg),
        "TDG Points": as_map(tdg),
        "FantasyPros Dynasty ECR": load_fp_dynasty(),
    }
    dynasty = aggregate(sources, meta, min_n=1)
    farm = load_farm(limit=400)
    farm_keys = {r["key"] for r in farm}
    majors = rerank([r for r in dynasty if r.get("key") not in farm_keys])
    lineups = filter_group(majors, {"HIT", "UT"})
    by_id = {
        "deep-dynasty": dynasty,
        "deep-farm": farm,
        "majors": majors,
        "lineups": lineups,
    }
    pages = []
    for spec in PAGES:
        rec = dict(spec)
        rec["rows"] = by_id[spec["id"]]
        rec["count"] = len(rec["rows"])
        pages.append(rec)
    return {
        "pages": pages,
        "by_id": {p["id"]: p for p in pages},
        "sources": sources,
        "farm_n": len(farm),
        "dynasty_n": len(dynasty),
        "majors_n": len(majors),
        "lineups_n": len(lineups),
    }


def deep_cell(r):
    ranks = r.get("ranks") or {}
    rg = ranks.get("RotoGraphs Model")
    tdg = ranks.get("TDG Points")
    fp = ranks.get("FantasyPros Dynasty ECR")
    return (
        f'<td class="src-col">{rg if rg not in (None, "") else "-"}</td>'
        f'<td class="src-col">{tdg if tdg not in (None, "") else "-"}</td>'
        f'<td class="src-col">{fp if fp not in (None, "") else "-"}</td>'
        f'<td class="src-col">{r.get("avg", "-")}</td>'
        f'<td class="src-col">{r.get("n", "-")}</td>'
        f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


def farm_cell(r):
    ranks = r.get("ranks") or {}
    games = r.get("mlb_g")
    games_txt = "0" if games in (None, "") else str(games)
    return (
        f'<td class="desk-only">{esc(r.get("level") or "")}</td>'
        f'<td class="desk-only">{esc(games_txt)}</td>'
        f'<td class="c-eta">{esc(r.get("eta") or "")}</td>'
        f'<td class="c-path path-note">{esc(r.get("path") or "")}</td>'
        f'<td class="src-col">{ranks.get("MLB Pipeline") or "-"}</td>'
        f'<td class="src-col">{ranks.get("Baseball America") or "-"}</td>'
        f'<td class="src-col">{ranks.get("ESPN") or "-"}</td>'
        f'<td class="src-col">{r.get("n") or 0}</td>'
        f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


DEEP_HEADERS = ["RG", "TDG", "FP ECR", "Avg", "# Boards", "BK Value"]
FARM_HEADERS = ["Level", "MLB G", "Arrival", "Path", "Pipeline", "BA", "ESPN", "Boards", "BK Value"]

DEEPBASE_FAQ = [
    ("What is DeepBase?", "Four baseball boards that go deeper than The Keep and The Diamond: the full dynasty tape, the full farm, majors only, and everyday lineups."),
    ("How is Deep Dynasty built?", "RotoGraphs, The Dynasty Guru, and FantasyPros Dynasty ECR. Every name those three ranked. Unranked boards are skipped, never treated as 999."),
    ("How is Deep Farm different from The Farm?", "The Farm is the top 100. Deep Farm keeps every prospect those five lists ranked."),
]


def sources_html(farm=False):
    rows = FARM_SOURCES if farm else DEEP_SOURCES
    lis = "".join(
        f"<li><a href=\"{esc(u)}\">{esc(n)}</a> - {esc(note)}</li>" if u else f"<li><strong>{esc(n)}</strong> - {esc(note)}</li>"
        for n, u, note in rows
    )
    heading = "Prospect boards" if farm else "Deep dynasty boards"
    return (
        f'<section class="sources-box panel"><p class="kicker">Sources</p>'
        f"<h3>{esc(heading)}</h3><ol>{lis}</ol></section>"
    )


def board_body(page: dict, table_html: str, *, home_href: str, brand: str) -> str:
    is_farm = page["id"] == "deep-farm"
    return f"""
    {sr_h1(page["seo_title"].split("|")[0].strip())}
    {slim_banner(page["title"], UPDATED, "../img/bb-logo.jpg", f"{brand} logo", page["kicker"])}
    <p class="note">{esc(page["blurb"])} {page["count"]} names. Rebuilt {UPDATED}. <a href="{esc(home_href)}">{esc(brand)} home</a>.</p>
    {rank_search_bar()}
    <div class="panel">{table_html}</div>
    {sources_html(farm=is_farm)}
    {faq_html(DEEPBASE_FAQ, heading="How DeepBase works.")}
    """


def landing_body(payload: dict) -> str:
    cards = []
    for p in payload["pages"]:
        cards.append(
            f'<a class="tile deepbase-card" href="{esc(p["file"])}">'
            f'<p class="kicker">{esc(p["kicker"])}</p>'
            f'<h3>{esc(p["title"])}</h3>'
            f'<p>{esc(p["blurb"])}</p>'
            f'<p class="deepbase-count"><strong>{p["count"]}</strong> players</p>'
            "</a>"
        )
    return f"""
    {sr_h1("DeepBase Baseball Rankings")}
    {slim_banner("DeepBase", UPDATED, "../img/bb-logo.jpg", "DeepBase logo", "Four deep baseball boards")}
    <p class="note">The long baseball tape. Same ranks on BaseKeep. {UPDATED}.</p>
    <section class="home-snapshot deepbase-grid" aria-label="DeepBase boards">
      {"".join(f"<article>{c}</article>" for c in cards)}
    </section>
    {faq_html(DEEPBASE_FAQ, heading="How DeepBase works.")}
    """


def db_nav_target(href: str, path: str, depth: int) -> str:
    if href.startswith("../"):
        return ("../" * (depth - 1)) + href if depth > 1 else href
    if depth < 2:
        return href
    here = path.split("/")[0] + "/" if "/" in path else ""
    if here and href.startswith(here):
        return href[len(here):]
    return "../" + href


def db_nav_current(href: str, path: str) -> bool:
    return href == path or (href == "index.html" and path in ("index.html", ""))


def db_page(title, path, body, extra_js="", depth=1, description=None, extra_jsonld=None, body_class=""):
    prefix = "../" * depth
    packed = next((p for p in PAGES if p["file"] == path), None)
    full_title = (packed["seo_title"] if packed and path != "index.html" else None) or (
        "DeepBase Baseball Rankings | DeepBase" if path == "index.html" else f"{title} | DeepBase"
    )
    desc = description or (packed["seo_desc"] if packed else f"{title} on DeepBase. Deep dynasty baseball boards. Updated {UPDATED}.")
    page_links = []
    for p in PAGES:
        here = " is-here" if p["file"] == path else ""
        cur = ' aria-current="page"' if p["file"] == path else ""
        href = db_nav_target(p["file"], path, depth)
        page_links.append(f'<a class="db-page-link{here}" href="{esc(href)}"{cur}>{esc(p["nav"])}</a>')
    page_nav = f'<nav class="db-page-nav" aria-label="DeepBase boards">{"".join(page_links)}</nav>'
    back = f'<a class="sport-switch bb back-basekeep" href="{prefix}bb/index.html">Back to BaseKeep</a>'
    foot = grouped_nav(
        DEEPBASE_NAV_GROUPS,
        lambda h: db_nav_target(h, path, depth),
        lambda h: db_nav_current(h, path),
        skip_home=True,
        skip_current=True,
        nav_class="footer-nav site-nav",
        aria_label="On this board",
    )
    ld = extra_jsonld or []
    return strip_em(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path, "deepbase/"), image="img/bb-logo.jpg", brand="DeepBase", brand_url="https://ballkeep.com/deepbase/", extra_jsonld=ld, schema_type="CollectionPage")}
  <link rel="stylesheet" href="{prefix}css/bb.css?v={CHROME_VER}" />
  <link rel="stylesheet" href="{prefix}css/chrome.css?v={CHROME_VER}" />
  <link rel="icon" href="{prefix}img/bb-logo.jpg" />
  {theme_boot()}
</head>
<body class="deepbase{(' ' + esc(body_class)) if body_class else ''}">
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/bb-logo.jpg" alt="DeepBase circular baseball logo" width="56" height="56" />
        <div>
          <p class="brand-title"><span class="word-deep">DEEP</span><span class="word-base">BASE</span></p>
          <p>Deep Dynasty · Deep Farm · Majors · Lineups</p>
        </div>
      </a>
      {sports_top("db", depth)}
      {page_nav}
      {back}
      {theme_toggle_btn()}
    </header>
    {body}
    <footer>
      <div class="footer-mast">
        <p class="footer-mark"><span class="word-deep">DEEP</span><span class="word-base">BASE</span></p>
        <p>© {date.today().year} DeepBase · ballkeep.com/deepbase · Rankings aggregated {UPDATED}. Not affiliated with MLB.</p>
      </div>
      <div class="footer-cols">{foot}</div>
      {legal_links(depth)}
      {sports_footer("db", depth)}
    </footer>
  </div>
  <script src="{prefix}js/theme.js?v={CHROME_VER}" defer></script>
  {extra_js}
</body>
</html>
""")


def write_deepbase_copy(payload, table_fn, board_js: str):
    """Write /deepbase/index.html and the four board pages."""
    dest = ROOT / "deepbase"
    dest.mkdir(parents=True, exist_ok=True)
    landing = db_page(
        "Home",
        "index.html",
        landing_body(payload),
        extra_jsonld=[
            website_jsonld("DeepBase", "https://ballkeep.com/deepbase/"),
            faq_jsonld(DEEPBASE_FAQ),
        ],
        body_class="home",
    )
    (dest / "index.html").write_text(landing)
    urls = ["https://ballkeep.com/deepbase/", "https://ballkeep.com/deepbase/index.html"]
    for page in payload["pages"]:
        farm = page["id"] == "deep-farm"
        table = table_fn(
            page["rows"],
            FARM_HEADERS if farm else DEEP_HEADERS,
            farm_cell if farm else deep_cell,
            player_prefix="../bb/",
            media=None,
            faces=True,
            show_age=True,
            depth=1,
        )
        body = board_body(page, table, home_href="index.html", brand="DeepBase")
        extra_js = board_js
        doc = db_page(
            page["title"],
            page["file"],
            body,
            extra_js=extra_js,
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("DeepBase", "https://ballkeep.com/deepbase/"),
                    (page["title"], canon(page["file"], "deepbase/")),
                ]),
                rank_list_jsonld(
                    page["seo_title"],
                    canon(page["file"], "deepbase/"),
                    page["rows"],
                    lambda r: f"https://ballkeep.com/bb/players/{_slug(r.get('name'))}.html",
                    description=page["seo_desc"],
                ),
                faq_jsonld(DEEPBASE_FAQ),
            ],
        )
        (dest / page["file"]).write_text(doc)
        urls.append(f"https://ballkeep.com/deepbase/{page['file']}")
    return urls


def _slug(name: str) -> str:
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")
