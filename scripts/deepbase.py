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
    load_fp_dynasty,
    load_raw,
)
from bb_prospects import FARM_SOURCES  # noqa: E402
from bk_curve import bk_value  # noqa: E402
from mlb_deep import (  # noqa: E402
    FARM_AB_MAX,
    FARM_IP_MAX,
    build_lineups,
    build_universe,
    fetch_all,
    is_farm_eligible,
    is_majors_eligible,
)
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
    ("BK model", "", "3-year weighted 5/4/3 MLB production. Fills remaining Majors spots; labeled BK model."),
]
DEEP_FARM_SOURCES = FARM_SOURCES + [
    ("MLB Pipeline team top 30s", "https://www.mlb.com/prospects", "Public Pipeline top 30 for each of the 30 clubs."),
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
        "kicker": "130 AB and 50 IP or fewer",
        "blurb": "Prospects who have not crossed 130 career MLB at-bats or 50 innings. Pipeline team top 30s plus the public farm lists.",
        "seo_title": "Deep Farm MLB Prospect Rankings | DeepBase",
        "seo_desc": "Deep MLB prospect rankings beyond the top 100. Pipeline, Baseball America, ESPN, SI, and FanGraphs.",
    },
    {
        "id": "majors",
        "file": "majors.html",
        "title": "Majors",
        "nav": "Majors",
        "kicker": "More than 130 AB or 50 IP",
        "blurb": "Dynasty names who have crossed the farm cutoff, plus other active MLB players filled by the BK model.",
        "seo_title": "MLB Majors Dynasty Rankings | DeepBase",
        "seo_desc": "Dynasty baseball rankings for major-league names only. Prospects live on Deep Farm.",
    },
    {
        "id": "lineups",
        "file": "lineups.html",
        "title": "Lineups",
        "nav": "Lineups",
        "kicker": "2027 projected nines",
        "blurb": "All 30 clubs, alphabetical. FanGraphs Roster Resource 2027 batting order with Depth Charts projections.",
        "seo_title": "2027 MLB Projected Lineups | DeepBase",
        "seo_desc": "Projected 2027 starting lineups for all 30 MLB teams from FanGraphs Roster Resource. Batting order, age, BK dynasty score, FanGraphs Depth Charts projections.",
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
    raw_dynasty = aggregate(sources, meta, min_n=1)
    cache = fetch_all()
    uni = build_universe(raw_dynasty, cache)
    dynasty, farm, majors = uni["dynasty"], uni["farm"], uni["majors"]
    lineup_blocks = build_lineups(dynasty, cache)
    by_id = {
        "deep-dynasty": dynasty,
        "deep-farm": farm,
        "majors": majors,
        "lineups": lineup_blocks,
    }
    pages = []
    for spec in PAGES:
        rec = dict(spec)
        rec["rows"] = by_id[spec["id"]]
        if spec["id"] == "lineups":
            rec["count"] = sum(len(b.get("hitters") or []) for b in lineup_blocks)
            rec["team_count"] = len(lineup_blocks)
        else:
            rec["count"] = len(rec["rows"])
        pages.append(rec)
    return {
        "pages": pages,
        "by_id": {p["id"]: p for p in pages},
        "sources": sources,
        "farm_n": len(farm),
        "dynasty_n": len(dynasty),
        "majors_n": len(majors),
        "lineups_n": pages[-1]["count"],
        "unmatched": uni["unmatched"],
        "shortfalls": uni["shortfalls"],
        "lineup_blocks": lineup_blocks,
    }


def _ab_ip_cells(r):
    ab = r.get("ab")
    ip = r.get("ip")
    ab_txt = "-" if ab in (None, "") else str(int(ab))
    if ip in (None, ""):
        ip_txt = "-"
    else:
        ip_txt = f"{float(ip):.1f}".rstrip("0").rstrip(".")
    return f'<td class="c-ab">{esc(ab_txt)}</td><td class="c-ip">{esc(ip_txt)}</td>'


def deep_cell(r):
    ranks = r.get("ranks") or {}
    rg = ranks.get("RotoGraphs Model")
    tdg = ranks.get("TDG Points")
    fp = ranks.get("FantasyPros Dynasty ECR")
    return (
        _ab_ip_cells(r)
        + f'<td class="src-col">{rg if rg not in (None, "") else "-"}</td>'
        + f'<td class="src-col">{tdg if tdg not in (None, "") else "-"}</td>'
        + f'<td class="src-col">{fp if fp not in (None, "") else "-"}</td>'
        + f'<td class="src-col">{r.get("avg", "-")}</td>'
        + f'<td class="src-col">{r.get("n", "-")}</td>'
        + f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


def farm_cell(r):
    ranks = r.get("ranks") or {}
    pipe = r.get("pipeline_team_rank") or ranks.get("MLB Pipeline") or "-"
    return (
        f'<td class="desk-only">{esc(r.get("level") or "")}</td>'
        + _ab_ip_cells(r)
        + f'<td class="c-eta">{esc(r.get("eta") or "")}</td>'
        + f'<td class="c-path path-note">{esc(r.get("path") or "")}</td>'
        + f'<td class="src-col">{esc(pipe)}</td>'
        + f'<td class="src-col">{ranks.get("Baseball America") or "-"}</td>'
        + f'<td class="src-col">{ranks.get("ESPN") or "-"}</td>'
        + f'<td class="src-col">{r.get("n") or 0}</td>'
        + f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


DEEP_HEADERS = ["AB", "IP", "RG", "TDG", "FP ECR", "Avg", "# Boards", "BK Value"]
FARM_HEADERS = ["Level", "AB", "IP", "Arrival", "Path", "Pipeline", "BA", "ESPN", "Boards", "BK Value"]

DEEPBASE_FAQ = [
    ("What is DeepBase?", "Four baseball boards that go deeper than The Keep and The Diamond: the full dynasty tape, the full farm, majors only, and 2027 projected lineups."),
    ("Who is a farm name?", f"Career regular-season MLB hitting at-bats of {FARM_AB_MAX} or fewer AND pitching innings of {int(FARM_IP_MAX)} or fewer. A two-way player must clear both. Stats from the MLB Stats API through 2026."),
    ("Who is a major-league name?", f"More than {FARM_AB_MAX} career AB or more than {int(FARM_IP_MAX)} career IP. Ohtani and other two-way names sit here. Unmatched IDs are withheld, not guessed onto Majors."),
    ("How is Deep Dynasty built?", "RotoGraphs, The Dynasty Guru, and FantasyPros Dynasty ECR, then every eligible farm and majors name. BK Value uses the same rank-1 = 12,000 curve."),
    ("Where do the lineups come from?", "FanGraphs Roster Resource projected starting nines, in batting order. Counting stats are FanGraphs Depth Charts 2027 projections. A blank means FanGraphs did not publish that number. Bench names are FanGraphs depth-chart backups, not guesses."),
]


def sources_html(farm=False, majors=False):
    rows = DEEP_FARM_SOURCES if farm else DEEP_SOURCES
    if majors:
        heading = "Majors boards"
    elif farm:
        heading = "Prospect boards"
    else:
        heading = "Deep dynasty boards"
    lis = "".join(
        f"<li><a href=\"{esc(u)}\">{esc(n)}</a> - {esc(note)}</li>" if u else f"<li><strong>{esc(n)}</strong> - {esc(note)}</li>"
        for n, u, note in rows
    )
    return (
        f'<section class="sources-box panel"><p class="kicker">Sources</p>'
        f"<h3>{esc(heading)}</h3><ol>{lis}</ol></section>"
    )


def _pos_filters():
    btns = "".join(
        f'<button type="button" data-pos="{g}">{g}</button>'
        for g in ("HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B")
    )
    return (
        '<div class="filters" id="posf">'
        '<button type="button" class="active" data-pos="all">All</button>'
        f"{btns}</div>"
    )


def board_body(page: dict, table_html: str, *, home_href: str, brand: str) -> str:
    is_farm = page["id"] == "deep-farm"
    is_majors = page["id"] == "majors"
    n = page["count"]
    src = sources_html(farm=is_farm, majors=is_majors) if page["id"] != "lineups" else ""
    return f"""
    {sr_h1(page["seo_title"].split("|")[0].strip())}
    {slim_banner(page["title"], UPDATED, "../img/bb-logo.jpg", f"{brand} logo", page["kicker"])}
    <p class="note">{esc(page["blurb"])} <strong>{n} players</strong>. Rebuilt {UPDATED}. <a href="{esc(home_href)}">{esc(brand)} home</a>.</p>
    {rank_search_bar(_pos_filters())}
    <div class="panel">{table_html}</div>
    {src}
    {faq_html(DEEPBASE_FAQ, heading="How DeepBase works.")}
    """


def _fmt_proj(v, kind="int"):
    if v in (None, ""):
        return "—"
    if kind == "obp":
        return f"{float(v):.3f}".lstrip("0") if float(v) < 1 else f"{float(v):.3f}"
    return str(int(round(v)))


def lineup_body(blocks: list, *, home_href: str, brand: str) -> str:
    options = "".join(
        f'<option value="team-{esc(b["abbr"])}">{esc(b["name"])}</option>' for b in blocks
    )
    sections = []
    for b in blocks:
        rows = []
        for h in b.get("hitters") or []:
            proj = h.get("proj") or {}
            fa = ' <span class="lineup-fa">FA</span>' if h.get("fa") else ""
            alt = h.get("alt") or {}
            alt_html = ""
            if alt.get("name"):
                alt_html = (
                    f'<span class="lineup-alt">Possible alternate: {esc(alt["name"])}'
                    f' — {esc(alt.get("reason") or "playing-time split")}.</span>'
                )
            val = h.get("value")
            val_txt = f"{int(val):,}" if val not in (None, "") else "—"
            rows.append(
                "<tr>"
                f'<td>{h.get("slot") or ""}</td>'
                f'<td>{esc(h.get("pos") or "")}</td>'
                f'<td><strong>{esc(h.get("name") or "")}</strong>{fa}{alt_html}</td>'
                f'<td>{esc(h.get("age") or "—")}</td>'
                f'<td>{esc(val_txt)}</td>'
                f'<td>{_fmt_proj(proj.get("ab"))}</td>'
                f'<td>{_fmt_proj(proj.get("obp"), "obp")}</td>'
                f'<td>{_fmt_proj(proj.get("hr"))}</td>'
                f'<td>{_fmt_proj(proj.get("rbi"))}</td>'
                f'<td>{_fmt_proj(proj.get("sb"))}</td>'
                "</tr>"
            )
        sections.append(
            f'<details class="lineup-team" id="team-{esc(b["abbr"])}" open>'
            f'<summary>{esc(b["name"])}</summary>'
            '<table class="lineup-table">'
            "<caption>AB / OBP / HR / RBI / SB are FanGraphs Depth Charts 2027 projections.</caption>"
            "<thead><tr>"
            "<th>#</th><th>Pos</th><th>Hitter</th><th>Age</th><th>BK</th>"
            "<th>AB</th><th>OBP</th><th>HR</th><th>RBI</th><th>SB</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></details>"
        )
    jump = (
        '<label class="lineup-jump">Jump to team '
        f'<select onchange="var v=this.value; if(v) location.hash=v">'
        f'<option value="">All 30</option>{options}</select></label>'
    )
    return f"""
    {sr_h1("2027 MLB Projected Lineups")}
    {slim_banner("Lineups", UPDATED, "../img/bb-logo.jpg", f"{brand} logo", "2027 projected nines")}
    <p class="note">Most likely 2027 starting nine for every club, in batting order, from <strong>FanGraphs Roster Resource</strong>. Counting stats are <strong>FanGraphs Depth Charts</strong> 2027 projections. Blank means FanGraphs did not publish that number. Last updated {UPDATED}. <a href="{esc(home_href)}">{esc(brand)} home</a>.</p>
    <p class="proj-note">Every name is on that club’s current FanGraphs depth chart and projected to start. Possible alternates are FanGraphs bench players at the same spot, not guesses.</p>
    {jump}
    {''.join(sections)}
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
            f'<p class="deepbase-count"><strong>{p["count"] if p["id"] != "lineups" else p.get("team_count") or 30}</strong> {"teams" if p["id"]=="lineups" else "players"}</p>'
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
        if page["id"] == "lineups":
            body = lineup_body(payload.get("lineup_blocks") or page["rows"], home_href="index.html", brand="DeepBase")
            extra_js = ""
        else:
            farm = page["id"] == "deep-farm"
            table = table_fn(
                page["rows"],
                FARM_HEADERS if farm else DEEP_HEADERS,
                farm_cell if farm else deep_cell,
                player_prefix="../bb/",
                media=None,
                faces=False,
                show_age=True,
                depth=1,
                show_all=True,
            )
            body = board_body(page, table, home_href="index.html", brand="DeepBase")
            extra_js = board_js
        doc = db_page(
            page["title"],
            page["file"],
            body,
            extra_js=extra_js,
            extra_jsonld=_page_jsonld(page),
        )
        (dest / page["file"]).write_text(doc)
        urls.append(f"https://ballkeep.com/deepbase/{page['file']}")
    return urls


def _page_jsonld(page: dict) -> list:
    bits = [
        breadcrumb_jsonld([
            ("DeepBase", "https://ballkeep.com/deepbase/"),
            (page["title"], canon(page["file"], "deepbase/")),
        ]),
        faq_jsonld(DEEPBASE_FAQ),
    ]
    rows = page.get("rows") or []
    if page["id"] == "lineups":
        flat = []
        for block in rows:
            for h in block.get("hitters") or []:
                flat.append(h)
        rows = flat
    if rows and rows[0].get("name"):
        bits.insert(1, rank_list_jsonld(
            page["seo_title"],
            canon(page["file"], "deepbase/"),
            rows,
            lambda r: f"https://ballkeep.com/bb/players/{_slug(r.get('name'))}.html",
            description=page["seo_desc"],
        ))
    return bits


def _slug(name: str) -> str:
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")
