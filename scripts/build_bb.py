#!/usr/bin/env python3
"""Build the BaseKeep static section under bb/."""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 22, 2026"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bb_data import (  # noqa: E402
    BB_SOURCES,
    DYNASTY_WAIVERS,
    REDRAFT_WAIVERS,
    bk_value,
    load_universe,
)
from news_algo import (  # noqa: E402
    CATEGORY_LABEL,
    build_player_index,
    load_news_stories,
    news_when,
    rematch_stories,
)
from x_tape import cards_html as x_cards  # noqa: E402
from seo import canon, clip, grafs_html, head_tags, legal_links, rank_spread_graph, sports_footer, sports_top, value_bars  # noqa: E402


def esc(s):
    return html.escape(str(s), quote=True)


def desk_block(kind, kicker, heading, note, tiles, extra=""):
    cards = "".join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h, t, p in tiles)
    cols = "grid" if len(tiles) <= 2 else "grid-3"
    return (
        f'<section class="desk-block {kind}">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h2>{esc(heading)}</h2>"
        f'<p class="note">{note}</p>'
        f'<div class="{cols}">{cards}</div>'
        f"{extra}"
        "</section>"
    )


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")


def write(path, doc):
    dest = ROOT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)


BB_NAV = [
    ("index.html", "Home"),
    ("the-keep.html", "The Keep"),
    ("the-diamond.html", "The Diamond"),
    ("news.html", "News"),
    ("the-x.html", "The X"),
    ("the-lineup.html", "The Lineup"),
    ("pitchers.html", "BK's Pitchers"),
    ("bullpen.html", "Bullpen SV"),
    ("bullpen-holds.html", "SV + Holds"),
    ("trade.html", "Trade"),
    ("players/index.html", "Players"),
]


def wordmark():
    return '<span class="word-base">BASE</span> <span class="word-keep">KEEP</span>'


def masthead(kicker, mark, sub, url="ballkeep.com/bb"):
    return (
        f'<section class="hero masthead" aria-label="{esc(kicker)}">'
        f'<div class="hero-card">'
        f'<div class="mast-row">'
        f'<img class="mast-mark" src="../img/bb-logo.jpg" alt="BaseKeep circular baseball logo" />'
        f'<div class="mast-copy">'
        f'<p class="mast-kicker">{esc(kicker)}</p>'
        f"<h2>{mark}</h2>"
        f'<span class="mast-rule" aria-hidden="true"></span>'
        f'<p class="mast-sub">{esc(sub)}</p>'
        f'<p class="mast-url">{esc(url)}</p>'
        f"</div>"
        f'<div class="mast-art" aria-hidden="true"><img src="../img/mast-ballkeep.jpg" alt="" /></div>'
        f"</div></div></section>"
    )


def bb_nav_target(href: str, path: str, depth: int) -> str:
    if depth < 2:
        return href
    here = path.split("/")[0] + "/" if "/" in path else ""
    if here and href.startswith(here):
        return href[len(here):]
    return "../" + href


def bb_nav_current(href: str, path: str) -> bool:
    if href == path:
        return True
    if href == "news.html" and (path == "news.html" or path.startswith("news/")):
        return True
    if href == "the-diamond.html" and path in ("the-diamond.html", "redraft.html"):
        return True
    return False


BB_SEO = {
    "index.html": (
        "BaseKeep | Dynasty Baseball Rankings and Trade Calculator",
        "Navy-and-cream dynasty baseball desk. The Keep is dynasty top 400. The Diamond is redraft. Lineup, Pitchers, bullpen, and BK News.",
        "img/bb-hero.jpg",
    ),
    "the-keep.html": (
        "The Keep 2026 Dynasty Baseball Rankings (Top 400) | BaseKeep",
        "Overall dynasty baseball top 400, rebuilt August 21, 2026. 23-board aggregate led by RotoGraphs' Aug 14 model and The Dynasty Guru points Top 500. BK Value starts at 12,000.",
        "img/bb-logo.jpg",
    ),
    "the-lineup.html": (
        "The Lineup — Dynasty Hitter Rankings | BaseKeep",
        "Dynasty hitters only. The bats you keep, re-ranked from The Keep. Ranked on the same 23-board average.",
        "img/bb-logo.jpg",
    ),
    "pitchers.html": (
        "BK's Pitchers — Dynasty SP and Two-Way Rankings | BaseKeep",
        "Top 150 dynasty arms, starters plus the two-way unicorn. Same BK Value curve as The Keep.",
        "img/bb-logo.jpg",
    ),
    "bullpen.html": (
        "Bullpen Saves Rankings — Top 100 Relievers | BaseKeep",
        "Top 100 relief pitchers for saves leagues. FantasyPros closer report plus ESPN reliever depth.",
        "img/bb-logo.jpg",
    ),
    "bullpen-holds.html": (
        "Saves Plus Holds Rankings | BaseKeep",
        "Same bullpen, holds counted. FantasyPros Week 21 SV+H board plus setup men the ESPN chart uses.",
        "img/bb-logo.jpg",
    ),
    "the-diamond.html": (
        "The Diamond — 2026 Redraft Baseball Rankings | BaseKeep",
        "The Diamond is BaseKeep's redraft ranking. This-year baseball top 400.",
        "img/bb-logo.jpg",
    ),
    "redraft.html": (
        "The Diamond — 2026 Redraft Baseball Rankings | BaseKeep",
        "The Diamond is BaseKeep's redraft ranking. This-year baseball top 400.",
        "img/bb-logo.jpg",
    ),
    "trade.html": (
        "Dynasty Baseball Trade Calculator | BaseKeep",
        "Keep, Lineup, Pitchers, The Diamond (redraft), Saves, SV+H. Rank becomes BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "news.html": (
        "BK News Baseball — IL, Roster, and Manager Tape | BaseKeep",
        "Hourly baseball IL, roster, and manager reports clustered with links back to Keep player files.",
        "img/bb-logo.jpg",
    ),
    "players/index.html": (
        "MLB Dynasty Player Files | BaseKeep",
        "The Keep top 400, one cream card each: 2026/2025 line, every board, tape.",
        "img/bb-logo.jpg",
    ),
    "the-x.html": (
        "The X — Baseball Memes from X | BaseKeep",
        "Fun tape, not news. MLB memes and shitposts pulled from X via Google News.",
        "img/bb-logo.jpg",
    ),
    "trade-keep.html": (
        "Dynasty Baseball Overall Trade Calculator | BaseKeep",
        "Trade calculator on The Keep overall ranks. Rank becomes BK Value (12,000 at 1.01). Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "trade-lineup.html": (
        "Dynasty Hitter Trade Calculator | BaseKeep",
        "Trade calculator on The Lineup. Hitters only. Rank becomes BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "trade-pitchers.html": (
        "Dynasty Pitcher Trade Calculator | BaseKeep",
        "Trade calculator on BK's Pitchers. Rank becomes BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "trade-redraft.html": (
        "The Diamond Trade Calculator | BaseKeep",
        "Trade calculator on The Diamond, BaseKeep's redraft ranking. No future picks. Rank becomes BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "trade-saves.html": (
        "Saves League Trade Calculator | BaseKeep",
        "Bullpen saves board as BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
    "trade-svh.html": (
        "Saves Plus Holds Trade Calculator | BaseKeep",
        "SV+H bullpen board as BK Value. Fair is within 8%.",
        "img/bb-logo.jpg",
    ),
}


def bb_page(title, path, body, extra_js="", depth=1, description=None, image=None, doc_title=None):
    prefix = "../" * depth
    links = []
    for href, label in BB_NAV:
        cur = ' aria-current="page"' if bb_nav_current(href, path) else ""
        target = bb_nav_target(href, path, depth)
        links.append(f'<a href="{esc(target)}"{cur}>{esc(label)}</a>')
    fb = f"{prefix}index.html"
    packed = BB_SEO.get(path)
    full_title = doc_title or (packed[0] if packed else f"{title} | BaseKeep")
    desc = description or (packed[1] if packed else f"{title} on BaseKeep. Dynasty baseball rankings, BK Value, and BK News. Updated {UPDATED}.")
    img = image or (packed[2] if packed else "img/bb-logo.jpg")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path, "bb/"), image=img, brand="BaseKeep")}
  <link rel="stylesheet" href="{prefix}css/bb.css?v=32" />
  <link rel="icon" href="{prefix}img/bb-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/bb-logo.jpg" alt="BaseKeep circular baseball logo" />
        <div>
          <p class="brand-title">{wordmark()}</p>
          <p>The Keep · The Diamond</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {sports_top("bb", depth)}
    {body}
    <footer>
      © {date.today().year} BaseKeep · ballkeep.com/bb · Rankings aggregated {UPDATED}. Not affiliated with MLB.
      {legal_links(depth)}
      {sports_footer("bb", depth)}
    </footer>
  </div>
  {extra_js}
</body>
</html>
"""


def _rank_th(label):
    cls = ""
    if label == "BK Value":
        cls = "c-val"
    elif label == "Age":
        cls = "c-age"
    elif label not in ("BK", "Player", "Pos", "Team"):
        cls = "desk-only"
    attr = f' class="{cls}"' if cls else ""
    return f"<th{attr}>{esc(label)}</th>"


def face_src(r, media, depth=1):
    key = r.get("key") or ""
    slug = slugify(r.get("name") or "")
    m = (media or {}).get(key) or (media or {}).get(slug) or {}
    img = m.get("image") or "img/bb-logo.jpg"
    return "../" * depth + img


def rank_table(rows, extra_headers=None, extra_cells=None, player_prefix="", media=None, faces=False, show_age=False, depth=1):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    media = media or {}
    cols = ["BK", "Player", "Pos", "Team"]
    head = "".join(_rank_th(h) for h in cols + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        pos0 = pos.split("/")[0]
        team = r.get("team") or ""
        slug = slugify(r["name"])
        href = f"{player_prefix}players/{slug}.html"
        age_txt = str(r["age"]) if r.get("age") not in (None, "") else ""
        if show_age and not age_txt:
            age_txt = str((media.get(r.get("key") or "") or {}).get("age") or "")
        age_label = f"age {age_txt}" if show_age and age_txt else ""
        age_span = f'<span class="age-desc">{esc(age_label)}</span>' if age_label else ""
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos0)}">{esc(pos)}</span>'
            f" · {esc(team)}</div>"
        )
        face = ""
        if faces:
            face = f'<img class="face" src="{esc(face_src(r, media, depth))}" alt="" />'
        stack = (
            f'<span class="name-stack"><a class="player-link" href="{esc(href)}">'
            f'<strong>{esc(r["name"])}</strong></a>{age_span}{meta}</span>'
        )
        body.append(
            f'<tr data-pos="{esc(pos0)}" data-group="{esc(r.get("group") or "")}">'
            f'<td class="rk c-rank">{r.get("bk","")}</td>'
            f'<td class="c-name">{face}{stack}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos0)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f"{extra_cells(r)}"
            "</tr>"
        )
    cls = "rank-table faces" if faces else "rank-table"
    return (
        f'<div class="table-wrap"><table class="{cls}">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def sources_panel():
    lis = []
    for name, url, note in BB_SOURCES:
        if url:
            lis.append(f'<li><a href="{esc(url)}">{esc(name)}</a> — {esc(note)}</li>')
        else:
            lis.append(f"<li><strong>{esc(name)}</strong> — {esc(note)}</li>")
    return (
        '<section class="sources-box panel">'
        '<p class="kicker">Sources</p><h3>Boards in This Aggregate</h3>'
        f"<ol>{''.join(lis)}</ol>"
        '<p class="note">23 public boards and compiled expert slices, August 2026. '
        "Unranked names are skipped in the mean — never treated as 999.</p></section>"
    )


def val_cell(r):
    ranks = r.get("ranks") or {}
    rg = ranks.get("RotoGraphs Model")
    tdg = ranks.get("TDG Points")
    return (
        f'<td class="desk-only">{rg if rg not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{tdg if tdg not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r["avg"]}</td>'
        f'<td class="desk-only">{r["n"]}</td>'
        f'<td class="c-val val">{int(r["value"]):,}</td>'
    )


def filter_js(groups):
    btns = "".join(f'<button type="button" data-pos="{g}">{g}</button>' for g in groups)
    return f"""
    <p class="note">Filter</p>
    <div class="filters" id="posf"><button type="button" class="active" data-pos="all">All</button>{btns}</div>
    """, """<script>
    const box = document.getElementById('posf');
    if (box) box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const p = b.dataset.pos;
      document.querySelectorAll('tbody tr').forEach(tr => {
        const hit = p === 'all' || tr.dataset.pos === p || tr.dataset.group === p;
        tr.style.display = hit ? '' : 'none';
      });
    });
    </script>"""


def page_label(kicker, title, sub=""):
    sub_html = f'<p class="mast-sub">{esc(sub)}</p>' if sub else ""
    return (
        f'<section class="hero page-label" aria-label="{esc(title)}">'
        f'<div class="hero-card">'
        f'<div class="mast-row">'
        f'<img class="mast-mark" src="../img/bb-logo.jpg" alt="BaseKeep circular baseball logo" />'
        f'<div class="mast-copy">'
        f'<p class="mast-kicker">{esc(kicker)}</p>'
        f"<h2>{esc(title)}</h2>"
        f'<span class="mast-rule" aria-hidden="true"></span>'
        f"{sub_html}"
        f"</div></div></div></section>"
    )


def load_bb_media():
    path = ROOT / "data/bb-media.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_bb_savant():
    path = ROOT / "data/bb-savant.json"
    if not path.exists():
        return {"batters": {}, "pitchers": {}}
    return json.loads(path.read_text())


BAT_STARCAST = [
    ("xwoba", "xwOBA"),
    ("xba", "xBA"),
    ("xslg", "xSLG"),
    ("xiso", "xISO"),
    ("xobp", "xOBP"),
    ("brl", "Barrels"),
    ("brl_percent", "Barrel %"),
    ("exit_velocity", "EV"),
    ("max_ev", "Max EV"),
    ("hard_hit_percent", "Hard Hit %"),
    ("k_percent", "K %"),
    ("bb_percent", "BB %"),
    ("whiff_percent", "Whiff %"),
    ("chase_percent", "Chase %"),
    ("sprint_speed", "Speed"),
    ("arm_strength", "Arm"),
    ("oaa", "OAA"),
    ("bat_speed", "Bat Speed"),
    ("squared_up_rate", "Squared Up"),
    ("swing_length", "Swing Len"),
]
PIT_STARCAST = [
    ("xera", "xERA"),
    ("xwoba", "xwOBA"),
    ("fb_velocity", "FB Velo"),
    ("fb_spin", "FB Spin"),
    ("curve_spin", "CU Spin"),
    ("k_percent", "K %"),
    ("bb_percent", "BB %"),
    ("whiff_percent", "Whiff %"),
    ("chase_percent", "Chase %"),
    ("brl_percent", "Barrel %"),
    ("hard_hit_percent", "Hard Hit %"),
    ("exit_velocity", "EV"),
    ("max_ev", "Max EV"),
]


def savant_color(pct: int) -> str:
    p = max(0, min(100, int(pct))) / 100.0
    if p < 0.5:
        t = p * 2
        r = int(200 + (236 - 200) * t)
        g = int(16 + (236 - 16) * t)
        b = int(46 + (236 - 46) * t)
    else:
        t = (p - 0.5) * 2
        r = int(236 + (22 - 236) * t)
        g = int(236 + (80 - 236) * t)
        b = int(236 + (160 - 236) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def savant_player_url(name: str, mlb_id) -> str:
    return f"https://baseballsavant.mlb.com/savant-player/{slugify(name)}-{int(mlb_id)}"


def savant_roles(r, media) -> list[str]:
    g = (r.get("group") or "").upper()
    hit = bool((media.get("hit") or {}).get("g") or (media.get("hit_2025") or {}).get("g"))
    pit = bool(
        (media.get("pit") or {}).get("ip")
        or (media.get("pit") or {}).get("g")
        or (media.get("pit_2025") or {}).get("ip")
    )
    if g == "UT" or (hit and pit):
        return ["batter", "pitcher"]
    if g in ("SP", "RP"):
        return ["pitcher"]
    return ["batter"]


def starcast_html(title: str, rec: dict, metrics) -> str:
    rows = []
    for key, label in metrics:
        val = rec.get(key)
        if val in (None, ""):
            continue
        try:
            pct = int(val)
        except (TypeError, ValueError):
            continue
        pct = max(0, min(100, pct))
        color = savant_color(pct)
        rows.append(
            f'<div class="starcast-row">'
            f'<span class="sc-lab">{esc(label)}</span>'
            f'<div class="sc-track"><i class="sc-fill" style="width:{pct}%;background:{color}"></i></div>'
            f'<span class="sc-pct">{pct}</span></div>'
        )
    if not rows:
        return ""
    year = rec.get("year") or ""
    return (
        f'<div class="starcast-pane">'
        f'<h3>{esc(title)}{f" · {year}" if year else ""}</h3>'
        f'{"".join(rows)}</div>'
    )


def savant_block(r, media, savant) -> str:
    mlb_id = media.get("mlb_id")
    if not mlb_id:
        return ""
    try:
        mlb_id = int(mlb_id)
    except (TypeError, ValueError):
        return ""
    href = savant_player_url(r["name"], mlb_id)
    roles = savant_roles(r, media)
    batters = (savant or {}).get("batters") or {}
    pitchers = (savant or {}).get("pitchers") or {}
    panes = []
    if "batter" in roles:
        panes.append(starcast_html("Batter", batters.get(str(mlb_id)) or {}, BAT_STARCAST))
    if "pitcher" in roles:
        panes.append(starcast_html("Pitcher", pitchers.get(str(mlb_id)) or {}, PIT_STARCAST))
    panes = [p for p in panes if p]
    starcast = f'<div class="starcast-grid">{"".join(panes)}</div>' if panes else (
        '<p class="note">No 2026 Savant percentile sample yet. The spray and pitch charts below still load from Baseball Savant.</p>'
    )
    frames = []
    if "batter" in roles:
        spray = (
            "https://baseballsavant.mlb.com/player-comparison"
            f"?playerIds={mlb_id}&seasons=2026&ddlChartType=spray"
        )
        frames.append(
            f'<div class="savant-chart">'
            f"<h3>Hits spray chart</h3>"
            f'<iframe class="savant-embed" title="{esc(r["name"])} spray chart" '
            f'src="{esc(spray)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            f'<p class="note"><a href="{esc(spray)}" target="_blank" rel="noopener">Open spray chart on Baseball Savant</a></p>'
            f"</div>"
        )
    if "pitcher" in roles:
        pitch = (
            "https://baseballsavant.mlb.com/player-comparison"
            f"?playerIds={mlb_id}&seasons=2026&ddlChartType=pitch"
        )
        frames.append(
            f'<div class="savant-chart">'
            f"<h3>Pitch chart</h3>"
            f'<iframe class="savant-embed" title="{esc(r["name"])} pitch chart" '
            f'src="{esc(pitch)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            f'<p class="note"><a href="{esc(pitch)}" target="_blank" rel="noopener">Open pitch chart on Baseball Savant</a></p>'
            f"</div>"
        )
    return f"""
    <section class="panel savant-panel">
      <p class="kicker">Baseball Savant</p>
      <h3>Starcast · spray · pitch</h3>
      <p class="note">Percentile ranks (Starcast) plus the official Savant spray chart for bats and pitch chart for arms. <a href="{esc(href)}" target="_blank" rel="noopener">Open the full Baseball Savant page</a>.</p>
      {starcast}
      {"".join(frames)}
    </section>
    """


def nz(v, dash="—"):
    if v in (None, "", []):
        return dash
    return v


def stat_pills(media, group):
    pills = []
    hit = (media or {}).get("hit") or {}
    pit = (media or {}).get("pit") or {}
    if group in ("HIT", "UT") and hit.get("g"):
        pills.extend([
            ("AVG", hit.get("avg")),
            ("HR", hit.get("hr")),
            ("SB", hit.get("sb")),
            ("OPS", hit.get("ops")),
            ("R", hit.get("r")),
            ("RBI", hit.get("rbi")),
            ("G", hit.get("g")),
            ("BB", hit.get("bb")),
        ])
    if group in ("SP", "RP", "UT") and (pit.get("g") or pit.get("ip")):
        pills.extend([
            ("ERA", pit.get("era")),
            ("WHIP", pit.get("whip")),
            ("K", pit.get("so")),
            ("IP", pit.get("ip")),
            ("W", pit.get("w")),
            ("SV", pit.get("sv")),
            ("HLD", pit.get("hld")),
            ("K/9", pit.get("k9")),
        ])
    pills = [(k, v) for k, v in pills if v not in (None, "", 0, "0", ".000") or k in ("AVG", "ERA", "SV")]
    if not pills:
        return ""
    cells = "".join(
        f'<div class="stat-pill"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in pills[:8]
    )
    return f'<div class="stat-strip">{cells}</div>'


def bio_line(media, r):
    bits = []
    if media.get("number"):
        bits.append(f"#{media['number']}")
    pos = r.get("pos") or media.get("pos") or ""
    team = r.get("team") or media.get("team") or ""
    if pos:
        bits.append(pos)
    if team or media.get("team_name"):
        bits.append(media.get("team_name") or team)
    age = r.get("age") or media.get("age") or ""
    if age:
        bits.append(f"age {age}")
    if media.get("bats") or media.get("throws"):
        bits.append(f"B/T {media.get('bats') or '—'}{media.get('throws') or ''}")
    if media.get("height"):
        ht = media["height"]
        if media.get("weight"):
            ht += f" / {media['weight']} lbs"
        bits.append(ht)
    if media.get("debut"):
        bits.append(f"MLB debut {media['debut'][:4]}")
    elif media.get("draft"):
        bits.append(f"Draft {media['draft']}")
    home = ", ".join(x for x in (media.get("birth_city"), media.get("birth_country")) if x)
    if home:
        bits.append(home)
    return " · ".join(str(b) for b in bits)


def plusminus_html(plus, minus):
    if not plus and not minus:
        return ""
    left = (
        f'<div class="pm"><h3>Plus</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in plus)}</ul></div>'
        if plus else ""
    )
    right = (
        f'<div class="pm"><h3>Minus</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in minus)}</ul></div>'
        if minus else ""
    )
    return f'<div class="plusminus">{left}{right}</div>'


def facts_table(media, r):
    media = media or {}
    items = []
    if r.get("avg") is not None:
        items.append(("Keep avg", r["avg"]))
    if r.get("n"):
        items.append(("# Boards", r["n"]))
    if r.get("value"):
        items.append(("BK Value", f"{int(r['value']):,}"))
    ranks = r.get("ranks") or {}
    if ranks:
        items.append(("Spread", f"{min(ranks.values())}–{max(ranks.values())}"))
    if not items:
        return ""
    cells = "".join(
        f'<div class="fact"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in items
    )
    return f'<div class="facts">{cells}</div>'


def _hit_row(year, st):
    if not st or not st.get("g"):
        return ""
    label = year
    if st.get("level") and st.get("level") != "MLB":
        label = f"{year} {st['level']}"
    cells = [
        label, st.get("g"), st.get("ab"), st.get("r"), st.get("h"), st.get("2b"),
        st.get("hr"), st.get("rbi"), st.get("sb"), st.get("bb"), st.get("so"),
        st.get("avg"), st.get("obp"), st.get("slg"), st.get("ops"),
    ]
    return "<tr>" + "".join(f"<td>{esc(nz(c))}</td>" for c in cells) + "</tr>"


def _pit_row(year, st):
    if not st or not (st.get("g") or st.get("ip")):
        return ""
    label = year
    if st.get("level") and st.get("level") != "MLB":
        label = f"{year} {st['level']}"
    cells = [
        label, st.get("g"), st.get("gs"), st.get("w"), st.get("l"), st.get("sv"),
        st.get("hld"), st.get("ip"), st.get("so"), st.get("bb"), st.get("hr"),
        st.get("era"), st.get("whip"), st.get("k9"),
    ]
    return "<tr>" + "".join(f"<td>{esc(nz(c))}</td>" for c in cells) + "</tr>"


def season_box(media):
    media = media or {}
    hit_rows = _hit_row("2026", media.get("hit")) + _hit_row("2025", media.get("hit_2025"))
    pit_rows = _pit_row("2026", media.get("pit")) + _pit_row("2025", media.get("pit_2025"))
    parts = []
    if hit_rows:
        parts.append(
        '<div class="panel season">'
            '<p class="kicker">Hitting</p>'
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Year</th><th>G</th><th>AB</th><th>R</th><th>H</th><th>2B</th>"
            "<th>HR</th><th>RBI</th><th>SB</th><th>BB</th><th>SO</th>"
            "<th>AVG</th><th>OBP</th><th>SLG</th><th>OPS</th>"
            "</tr></thead><tbody>"
            f"{hit_rows}</tbody></table></div></div>"
        )
    if pit_rows:
        parts.append(
            '<div class="panel season">'
            '<p class="kicker">Pitching</p>'
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Year</th><th>G</th><th>GS</th><th>W</th><th>L</th><th>SV</th>"
            "<th>HLD</th><th>IP</th><th>K</th><th>BB</th><th>HR</th>"
            "<th>ERA</th><th>WHIP</th><th>K/9</th>"
            "</tr></thead><tbody>"
            f"{pit_rows}</tbody></table></div></div>"
        )
    if not parts:
        return (
            '<p class="note">No MLB box score yet — prospect file. '
            "The Keep rank is the projection, not a 2026 line.</p>"
        )
    return "".join(parts)


def list_cards(lists, r):
    items = [
        ("The Keep", lists.get("BB Keep"), r.get("value")),
        ("The Lineup", lists.get("The Lineup"), None),
        ("BK's Pitchers", lists.get("BK Pitchers"), None),
        ("The Diamond", lists.get("BB Redraft"), None),
        ("Saves", lists.get("Saves"), None),
        ("SV+H", lists.get("SVH"), None),
    ]
    cards = []
    for label, rank, val in items:
        if not rank:
            continue
        value = val if val else bk_value(rank)
        cards.append(
            f'<div class="rank-card"><small>{esc(label)}</small>'
            f"<strong>#{rank}</strong><span>BK {int(value):,}</span></div>"
        )
    return f'<div class="rank-grid">{"".join(cards)}</div>' if cards else ""


def boards_table(ranks):
    if not ranks:
        return ""
    rows = sorted(ranks.items(), key=lambda kv: kv[1])
    vals = [v for _s, v in rows]
    lo, hi = min(vals), max(vals)
    body = []
    for src, rk in rows:
        cls = "hi" if rk == lo else ("lo" if rk == hi and hi != lo else "")
        body.append(f'<tr class="{cls}"><td>{esc(src)}</td><td class="rk">{rk}</td></tr>')
    return (
        '<section class="panel">'
        '<p class="kicker">Every Board</p>'
        f"<h3>Spread {lo}–{hi} · {len(rows)} sources</h3>"
        f'<div class="table-wrap"><table class="boards"><thead><tr><th>Source</th><th>Rank</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></div></section>"
    )


def neighbors(keep, idx):
    window = keep[max(0, idx - 2) : idx] + keep[idx + 1 : idx + 3]
    if not window:
        return ""
    links = " · ".join(
        f'<a class="player-link" href="{slugify(p["name"])}.html">{esc(p["name"])}</a> '
        f'(#{p["bk"]})'
        for p in window
    )
    return f'<p class="note" style="margin-top:18px"><strong>On The Keep nearby</strong> — {links}</p>'


def same_pos(keep, r, limit=6):
    pos = (r.get("pos") or "").split("/")[0]
    others = [p for p in keep if p["key"] != r["key"] and (p.get("pos") or "").split("/")[0] == pos][:limit]
    if not others:
        return ""
    links = " · ".join(
        f'<a class="player-link" href="{slugify(p["name"])}.html">{esc(p["name"])}</a> #{p["bk"]}'
        for p in others
    )
    return f'<p class="note"><strong>Same position on the 300</strong> — {links}</p>'


def waiver_note(name, dynasty, redraft):
    bits = []
    for w in dynasty:
        if w["name"].lower() == name.lower() or name.lower() in w["name"].lower():
            bits.append(f"Dynasty Wire P{w['pri']}: {w['why']}")
    for w in redraft:
        if w["name"].lower() == name.lower() or name.lower() in w["name"].lower():
            bits.append(f"Redraft Wire P{w['pri']}: {w['why']}")
    if not bits:
        return ""
    return (
        '<section class="panel">'
        '<p class="kicker">On the Wire</p>'
        + "".join(f"<p>{esc(b)}</p>" for b in bits)
        + "</section>"
    )


def bb_grafs(r, lists=None, media=None):
    lists = lists or {}
    media = media or {}
    keep = r.get("bk")
    n = r.get("n") or 0
    age = r.get("age") or media.get("age") or ""
    g = r.get("group") or ""
    hit = media.get("hit") or {}
    pit = media.get("pit") or {}
    ranks = r.get("ranks") or {}
    try:
        age_n = int(age) if age not in ("", None) else None
    except (TypeError, ValueError):
        age_n = None
    plus, minus = [], []
    if lists.get("BB Redraft") and keep and lists["BB Redraft"] + 20 < keep:
        plus.append(f"The Diamond #{lists['BB Redraft']} vs Keep #{keep} — helping now more than the dynasty slot.")
    if lists.get("BB Redraft") and keep and lists["BB Redraft"] > keep + 25:
        minus.append(f"The Diamond #{lists['BB Redraft']} vs Keep #{keep} — future, not a September stream.")
    if age_n and age_n >= 33:
        minus.append(f"Age {age_n} — dynasty tax.")
    if g == "RP":
        minus.append("RP: the ninth can vanish in a week.")
    if ranks:
        vals = list(ranks.values())
        spread = max(vals) - min(vals)
        if spread >= 40:
            minus.append(f"Board spread {min(vals)}–{max(vals)} ({spread} ranks).")
    if pit.get("era") and g in ("SP", "UT"):
        try:
            era = float(pit["era"])
            if era >= 4.50:
                minus.append(f"{pit['era']} ERA in {pit.get('ip') or '?'} IP.")
        except (TypeError, ValueError):
            pass
    if not media.get("mlb_id"):
        minus.append("No 2026 MLB line — prospect file. Rank is the projection.")
    bits = []
    if keep:
        bits.append(f"Keep #{keep}")
    if r.get("avg") is not None:
        bits.append(f"avg {r.get('avg')}")
    if n:
        bits.append(f"{n} boards")
    if hit.get("g"):
        bits.append(f"{hit.get('avg') or '—'} / {hit.get('hr') or 0} HR / {hit.get('sb') or 0} SB / {hit.get('ops') or '—'} OPS")
    elif pit.get("ip"):
        bits.append(f"{pit.get('era') or '—'} ERA, {pit.get('whip') or '—'} WHIP, {pit.get('so') or 0} K in {pit.get('ip')} IP")
    graf = " · ".join(str(b) for b in bits)
    return plus[:4], minus[:4], [graf] if graf else []


def write_player_pages(keep, lineup, pitchers, redraft, news_by_player=None, saves=None, svh=None):
    news_by_player = news_by_player or {}
    lu = {r["key"]: r for r in lineup}
    pit = {r["key"]: r for r in pitchers}
    rd = {r["key"]: r for r in redraft}
    sv = {r["key"]: r for r in (saves or [])}
    svh_m = {r["key"]: r for r in (svh or [])}
    media_all = load_bb_media()
    savant = load_bb_savant()
    cards = []
    urls = []
    files = []
    keep_html = {"index.html"}
    for i, r in enumerate(keep):
        slug = slugify(r["name"])
        media = media_all.get(r["key"]) or {}
        lists = {"BB Keep": r["bk"]}
        if r["key"] in lu:
            lists["The Lineup"] = lu[r["key"]]["bk"]
        if r["key"] in pit:
            lists["BK Pitchers"] = pit[r["key"]]["bk"]
        if r["key"] in rd:
            lists["BB Redraft"] = rd[r["key"]]["bk"]
        if r["key"] in sv:
            lists["Saves"] = sv[r["key"]]["bk"]
        if r["key"] in svh_m:
            lists["SVH"] = svh_m[r["key"]]["bk"]
        plus, minus, grafs = bb_grafs(r, lists, media)
        img = media.get("image") or "img/bb-logo.jpg"
        img_src = "../../" + img
        news_hits = news_by_player.get(r["key"]) or []
        news_block = ""
        if news_hits:
            lis = "".join(
                f'<li><a href="../news/{esc(s["slug"])}.html">{esc(s.get("headline") or "Update")}</a> '
                f'<span class="news-meta">{esc(CATEGORY_LABEL.get(s.get("category") or "", ""))} · '
                f'{esc(news_when(s.get("updated") or s.get("published") or ""))}</span></li>'
                for s in news_hits[:5] if s.get("slug")
            )
            news_block = (
                '<p class="kicker" style="margin-top:22px">BK News</p>'
                f'<ul class="source-list">{lis}</ul>'
            )
        body = f"""
    <p class="kicker">Player File · {esc(r.get("pos") or media.get("pos") or "")} {esc(r.get("team") or media.get("team") or "")}</p>
    <div class="player-hero">
      <img src="{esc(img_src)}" alt="{esc(r['name'])}" />
      <div>
        <h1>{esc(r["name"])}</h1>
        <p class="note">{esc(bio_line(media, r))}</p>
      </div>
    </div>
    {facts_table(media, r)}
    {season_box(media)}
    {list_cards(lists, r)}
    {grafs_html("The 2026 line", grafs, 2)}
    {savant_block(r, media, savant)}
    {plusminus_html(plus, minus)}
    {rank_spread_graph(r.get("ranks") or {}, fill="#1f6b3a", kicker="Board graph")}
    {boards_table(r.get("ranks") or {})}
    {news_block}
    {neighbors(keep, i)}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-keep.html">The Keep</a> · <a href="../the-diamond.html">The Diamond</a> · <a href="../news.html">BK News</a> · <a href="../the-lineup.html">The Lineup</a> · <a href="../pitchers.html">Pitchers</a> · <a href="../trade-keep.html">Calculator</a></p>
    """
        seo_title = f"{r['name']} Dynasty Rank #{r['bk']} ({r.get('pos') or ''} {r.get('team') or media.get('team') or ''})".strip()
        seo_desc = clip(
            f"{r['name']} is BaseKeep #{r['bk']}, {r.get('pos') or ''} "
            f"{r.get('team') or media.get('team') or ''}. Average {r.get('avg')} across {r.get('n') or 0} boards. "
            f"BK Value {int(r.get('value') or 0):,}. Updated {UPDATED}."
        )
        write(f"bb/players/{slug}.html", bb_page(r["name"], f"players/{slug}.html", body, depth=2, doc_title=seo_title, description=seo_desc, image=img))
        keep_html.add(f"{slug}.html")
        cards.append(
            f'<a class="tile player-card" href="{slug}.html" data-pos="{esc((r.get("pos") or "").split("/")[0])}" data-group="{esc(r.get("group") or "")}">'
            f'<img src="../../{esc(img)}" alt="" />'
            f'<h3>{esc(r["name"])}</h3>'
            f'<p>{esc(r.get("pos") or "")} {esc(r.get("team") or media.get("team") or "")} · Keep #{r["bk"]}</p></a>'
        )
        urls.append(f"https://ballkeep.com/bb/players/{slug}.html")
        files.append({
            "key": r["key"],
            "slug": slug,
            "name": r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or media.get("team") or "",
            "age": r.get("age") or media.get("age") or "",
            "group": r.get("group") or "",
            "lists": lists,
            "plus": plus,
            "minus": minus,
            "grafs": grafs,
            "sport": "baseball",
            "url": f"https://ballkeep.com/bb/players/{slug}.html",
            "value": r.get("value"),
            "bk": r["bk"],
            "keep_avg": r.get("avg"),
            "keep_n": r.get("n"),
            "image": img,
            "mlb_id": media.get("mlb_id") or "",
            "number": media.get("number") or "",
            "bats": media.get("bats") or "",
            "throws": media.get("throws") or "",
            "height": media.get("height") or "",
            "weight": media.get("weight") or "",
            "debut": media.get("debut") or "",
            "draft": media.get("draft") or "",
            "birth": media.get("birth") or "",
            "birth_city": media.get("birth_city") or "",
            "birth_country": media.get("birth_country") or "",
            "team_name": media.get("team_name") or "",
            "hit": media.get("hit") or {},
            "pit": media.get("pit") or {},
            "hit_2025": media.get("hit_2025") or {},
            "pit_2025": media.get("pit_2025") or {},
            "savant": savant_player_url(r["name"], media["mlb_id"]) if media.get("mlb_id") else "",
        })
    flt, js = filter_js(["HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B"])
    hub = f"""
    <p class="kicker">Player Files</p>
    <h2>The Keep, one name at a time</h2>
    <p class="note">The Keep top 400. Headshot, 2026/2025 line, ranks, every board. Filter the grid.</p>
    {flt}
    <div class="player-grid" id="bb-cards">{''.join(cards)}</div>
    """
    hub_js = js.replace("tbody tr", "#bb-cards .tile")
    write("bb/players/index.html", bb_page("Players", "players/index.html", hub, hub_js, depth=2))
    dest = ROOT / "bb" / "players"
    for old in dest.glob("*.html"):
        if old.name not in keep_html:
            old.unlink()
    return urls, files



def trade_payload(label, file, blurb, rows, picks):
    players = []
    for r in rows:
        players.append({
            "id": slugify(r["name"]),
            "name": r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "rank": r["bk"],
            "value": r.get("value") or bk_value(r["bk"]),
            "href": f"players/{slugify(r['name'])}.html",
        })
    return {
        "id": file.replace(".html", ""),
        "file": file,
        "label": label,
        "blurb": blurb,
        "players": players,
        "picks": picks if picks else [],
    }


def write_trade(payload, depth=1):
    body = f"""
    <p class="kicker">Trade Calculator</p>
    <h2>{esc(payload["label"])}</h2>
    <p class="note">{esc(payload["blurb"])} Fair is within 8%. Same BK Value curve as football: rank 1 = 12,000.</p>
    <p class="filters">
      <a href="trade.html">All calculators</a>
      <a href="trade-keep.html">Keep</a>
      <a href="trade-lineup.html">Lineup</a>
      <a href="trade-pitchers.html">Pitchers</a>
      <a href="trade-redraft.html">The Diamond</a>
      <a href="trade-saves.html">Saves</a>
      <a href="trade-svh.html">SV+H</a>
    </p>
    <div id="trade-app" class="trade-app"></div>
    """
    blob = json.dumps(payload, ensure_ascii=False)
    extra = f"<script>window.BK_TRADE = {blob};</script>\n<script src=\"../js/trade.js\"></script>"
    write("bb/" + payload["file"], bb_page(payload["label"], payload["file"], body, extra, depth=1))


def waiver_page(title, path, kicker, note, items, hot=False):
    cards = []
    for x in items:
        cards.append(
            f'<article class="tile waiver{" hot" if hot and x["pri"] <= 10 else ""}">'
            f'<p class="bb-pri">P{x["pri"]}</p>'
            f'<h3>{esc(x["name"])} <span class="pos {esc(x["pos"])}">{esc(x["pos"])}</span> {esc(x["team"])}</h3>'
            f'<p>{esc(x["why"])}</p></article>'
        )
    body = f"""
    <p class="kicker">{esc(kicker)}</p>
    <h2>{esc(title)}</h2>
    <p class="note">{esc(note)}</p>
    <div class="grid">{''.join(cards)}</div>
    """
    write("bb/" + path, bb_page(title, path, body))


def keep_as_roster(keep: list[dict]) -> list[dict]:
    rows = []
    for r in keep:
        rows.append({
            "key": r.get("key") or "",
            "name": r.get("name") or "",
            "slug": slugify(r.get("name") or ""),
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "lists": {"The Keep": r.get("bk")},
        })
    return rows


def bb_news_card(story: dict, prefix: str = "") -> str:
    cat = story.get("category") or "wire"
    label = CATEGORY_LABEL.get(cat, cat.title())
    href = f"{prefix}news/{esc(story['slug'])}.html"
    players = " ".join(
        f'<span class="chip">{esc(p.get("name") or "")}</span>'
        for p in (story.get("players") or [])[:6]
    )
    nsrc = len(story.get("sources") or [])
    kinds = {s.get("kind") for s in story.get("sources") or []}
    bits = [f"{nsrc} source" + ("s" if nsrc != 1 else "")]
    if "x" in kinds:
        bits.append("X")
    if "video" in kinds:
        bits.append("video")
    return (
        f'<a class="news-item tile" href="{href}">'
        f'<div class="news-meta"><span class="kind {esc(cat)}">{esc(label)}</span> '
        f'{esc(news_when(story.get("updated") or story.get("published") or ""))} · {esc(" · ".join(bits))}</div>'
        f'<h3>{esc(story.get("headline") or "Update")}</h3>'
        f'<p>{esc(story.get("blurb") or "")}</p>'
        f'<div class="news-players">{players}</div>'
        f"</a>"
    )


def bb_player_href(player: dict, depth: int) -> str | None:
    slug = player.get("slug") or slugify(player.get("name") or "")
    if not slug:
        return None
    prefix = "../" if depth >= 2 else ""
    return f"{prefix}players/{slug}.html"


def render_bb_news_pages(stories: list[dict]) -> list[str]:
    dest = ROOT / "bb" / "news"
    dest.mkdir(parents=True, exist_ok=True)
    keep = {f"{s['slug']}.html" for s in stories if s.get("slug")}
    for old in dest.glob("*.html"):
        if old.name not in keep:
            old.unlink()

    cards = "".join(bb_news_card(s) for s in stories) or (
        '<p class="note">The baseball wire is warming up. The hourly scrape will fill this desk.</p>'
    )
    chips = []
    for k, lab in (
        ("all", "All"),
        ("injury", "Injuries"),
        ("roster", "Roster"),
        ("coach", "Coach"),
        ("trade", "Trades"),
        ("practice", "Practice"),
        ("wire", "Wire"),
    ):
        cls = ' class="active"' if k == "all" else ""
        chips.append(f'<button type="button" data-cat="{esc(k)}"{cls}>{esc(lab)}</button>')
    updated = stories[0].get("updated") if stories else ""
    items_json = json.dumps([
        {
            "slug": s.get("slug"),
            "cat": s.get("category") or "wire",
            "html": bb_news_card(s),
        }
        for s in stories
    ]).replace("<", "\\u003c")
    extra = f"""<script>
    const NEWS = {items_json};
    const box = document.getElementById('news-list');
    function show(cat) {{
      const rows = NEWS.filter(s => cat === 'all' || s.cat === cat);
      box.innerHTML = rows.map(s => s.html).join('') || '<p class="note">No stories in this bucket yet.</p>';
    }}
    document.getElementById('news-filters').addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      document.querySelectorAll('#news-filters button').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); show(b.dataset.cat);
    }});
    </script>"""
    body = f"""
    <p class="kicker">BK News · Baseball · Hourly wire</p>
    <h2>BK News</h2>
    <p class="note">Injuries, IL stints, roster moves, and manager reports pulled from search and X, then clustered into short stories. Click a row for the aggregate summary, the original articles / X posts / video, and links back to every BaseKeep player page named in the tape. The scrape repeats on its own every hour. Football BK News lives on <a href="../news.html">Ball Keep</a>.</p>
    <p class="note">{f"Last cluster {esc(news_when(updated))}." if updated else "Awaiting first successful pull."}</p>
    <div class="filters" id="news-filters">{''.join(chips)}</div>
    <div class="news-list" id="news-list">{cards}</div>
    """
    write("bb/news.html", bb_page("BK News", "news.html", body, extra))

    urls = ["https://ballkeep.com/bb/news.html"]
    for s in stories:
        slug = s.get("slug")
        if not slug:
            continue
        cat = s.get("category") or "wire"
        label = CATEGORY_LABEL.get(cat, cat.title())
        sources = s.get("sources") or []
        groups = [("article", "Articles"), ("x", "X"), ("video", "Video")]
        blocks = []
        for kind, heading in groups:
            rows = [src for src in sources if src.get("kind") == kind]
            if not rows:
                continue
            lis = []
            for src in rows:
                pub = src.get("publisher") or ""
                when = news_when(src.get("published") or "")
                snip = src.get("snippet") or ""
                lis.append(
                    "<li class=\"source-row\">"
                    f'<a href="{esc(src.get("url") or "#")}" rel="noopener noreferrer">{esc(src.get("title") or pub or "Source")}</a>'
                    f'<span class="news-meta">{esc(pub)}{" · " + esc(when) if when else ""}</span>'
                    f'{f"<p class=\"note\">{esc(snip)}</p>" if snip else ""}'
                    "</li>"
                )
            blocks.append(f"<h3>{esc(heading)}</h3><ul class=\"source-list\">{''.join(lis)}</ul>")
        source_html = "".join(blocks) or "<p class=\"note\">Sources attached on the next hourly pass.</p>"
        people = s.get("players") or []
        if people:
            plist = "".join(
                f'<a class="tile" href="{esc(bb_player_href(p, 2) or "#")}"><h3>{esc(p.get("name") or "")}</h3>'
                f'<p class="note">{esc(p.get("pos") or "")} {esc(p.get("team") or "")}</p></a>'
                for p in people
                if bb_player_href(p, 2)
            )
            named = f'<p class="kicker" style="margin-top:22px">Players on this story</p><div class="grid-3">{plist}</div>'
        else:
            named = '<p class="note" style="margin-top:18px">No BaseKeep player page matched this cluster yet.</p>'
        nsrc = len(sources)
        story_body = f"""
    <p class="kicker">BK News · {esc(label)}</p>
    <p class="news-meta">{esc(news_when(s.get("updated") or s.get("published") or ""))} · {nsrc} source{"s" if nsrc != 1 else ""}</p>
    <h2>{esc(s.get("headline") or "Update")}</h2>
    <section class="panel">
      <p class="kicker">Aggregate</p>
      <p>{esc(s.get("summary") or s.get("blurb") or "")}</p>
    </section>
    {named}
    <section class="sources-box panel" style="margin-top:18px">
      <p class="kicker">Tape</p>
      <h3>Links back to the desks</h3>
      {source_html}
    </section>
    <p class="note" style="margin-top:18px"><a href="../news.html">All BK News</a> · <a href="../players/index.html">Player pages</a></p>
    """
        write(f"bb/news/{slug}.html", bb_page(s.get("headline") or "BK News", f"news/{slug}.html", story_body, depth=2))
        urls.append(f"https://ballkeep.com/bb/news/{slug}.html")
    return urls


def write_baseball_site():
    u = load_universe()
    keep, lineup, pitchers = u["keep"], u["lineup"], u["pitchers"]
    saves, svh, redraft = u["saves"], u["svh"], u["redraft"]
    picks = [{"id": slugify(p["name"]), **p} for p in u["picks"]]
    media = load_bb_media()
    for r in keep + lineup + pitchers + redraft:
        if r.get("age") in (None, "") and media.get(r.get("key") or ""):
            r["age"] = media[r["key"]].get("age") or ""
    roster = keep_as_roster(keep)
    stories = rematch_stories(load_news_stories("baseball"), build_player_index(roster))
    news_by_player = defaultdict(list)
    for story in stories:
        for pl in story.get("players") or []:
            key = pl.get("key")
            if key:
                news_by_player[key].append(story)

    latest_news = stories[:5]
    extra_news = ""
    if latest_news:
        extra_news = (
            '<div class="news-list">'
            + "".join(bb_news_card(s) for s in latest_news)
            + "</div>"
            '<p class="note" style="margin-top:12px"><a href="news.html">All BK News</a></p>'
        )
    home = f"""
    {masthead("Baseball rankings", wordmark(), "The Keep · The Diamond")}
    {desk_block("main", "Main", "The Keep and The Diamond.", "Dynasty overall, then the redraft ranking. Everything else on this page supports these.", [
        ("the-keep.html", "The Keep", "Overall dynasty top 400."),
        ("the-diamond.html", "The Diamond", "Redraft ranking. This year only."),
        ("the-lineup.html", "The Lineup", "Hitters only."),
        ("pitchers.html", "BK's Pitchers", "Top 150 arms."),
        ("trade.html", "Trade Calculators", "Keep, Lineup, Pitchers, The Diamond."),
        ("players/index.html", "Player Files", "Keep top 400."),
    ])}
    {desk_block("lists", "Lists", "The other boards.", "Bullpen and the files.", [
        ("bullpen.html", "Bullpen — Saves", "Top 100 relievers."),
        ("bullpen-holds.html", "Bullpen — SV+H", "Holds counted."),
    ])}
    {desk_block("extra", "Extra", "News and The X.", "Memes and the wire.", [
        ("the-x.html", "The X", "MLB memes. Pictures on the card."),
        ("news.html", "BK News", "IL, roster, managers."),
    ], extra_news)}
    """
    write("bb/index.html", bb_page("Home", "index.html", home))

    flt, js = filter_js(["HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B"])
    keep_body = f"""
    <p class="kicker">Keystone · Overall Dynasty</p>
    <h2>The Keep</h2>
    <p class="note">Baseball top 400, rebuilt {UPDATED}. Ball Keep rank is the average of every source that ranked the player — 23 boards, two of them 500 names long. Every row has a headshot and an age. BK Value uses the same decaying curve as football (12,000 at 1.01).</p>
    {flt}
    <div class="panel">{rank_table(keep, ["RG", "TDG", "Avg", "# Boards", "BK Value"], val_cell, media=media, faces=True, show_age=True)}</div>
    {value_bars(keep, 12, "#1f6b3a", "Keep value graph")}
    {sources_panel()}
    """
    write("bb/the-keep.html", bb_page("The Keep", "the-keep.html", keep_body, js))

    lu_body = f"""
    {page_label("BaseKeep", "The Lineup", "Hitters only")}
    <p class="note">Every hitter we could pin to a dynasty board, re-ranked among bats only. Ohtani lives here as a DH. Pitchers have their own building.</p>
    <div class="panel">{rank_table(lineup, ["RG", "TDG", "Avg", "# Boards", "BK Value"], val_cell, media=media, faces=True, show_age=True)}</div>
    {value_bars(lineup, 12, "#1f6b3a", "Lineup value graph")}
    {sources_panel()}
    """
    write("bb/the-lineup.html", bb_page("The Lineup", "the-lineup.html", lu_body))

    pit_body = f"""
    {page_label("BaseKeep", "BK's Pitchers", "Dynasty arms")}
    <p class="note">Top 150 overall dynasty pitchers. Starting pitchers plus the two-way unicorn. Relievers who crack the overall pitcher board sneak in; the full bullpen lives next door.</p>
    <div class="panel">{rank_table(pitchers, ["RG", "TDG", "Avg", "# Boards", "BK Value"], val_cell, media=media, faces=True, show_age=True)}</div>
    {value_bars(pitchers, 12, "#1f6b3a", "Pitcher value graph")}
    {sources_panel()}
    """
    write("bb/pitchers.html", bb_page("BK's Pitchers", "pitchers.html", pit_body))

    sv_body = f"""
    {page_label("BaseKeep", "BK's Bullpen — Saves", "Relief · Saves")}
    <p class="note">Top 100 relief pitchers for traditional saves leagues. Chart mix: FantasyPros closer report (Aug 20), ESPN reliever depth chart, and RPs who survive the overall Keep. Bryan Baker has the MLB lead. Diaz is leaking. Scott is the add.</p>
    <div class="panel">{rank_table(saves, ["BK Value"], lambda r: f'<td class="c-val val">{int(r["value"]):,}</td>')}</div>
    {value_bars(saves, 12, "#1f6b3a", "Saves value graph")}
    {sources_panel()}
    """
    write("bb/bullpen.html", bb_page("Bullpen Saves", "bullpen.html", sv_body))

    svh_body = f"""
    {page_label("BaseKeep", "BK's Bullpen — SV+H", "Relief · Saves + Holds")}
    <p class="note">Same bullpen, different sport. FantasyPros Week 21 SV+H board (Baker / Miller / Varland) plus setup men the ESPN chart actually uses. If your league counts holds, this is the page. The saves board is next door.</p>
    <div class="panel">{rank_table(svh, ["BK Value"], lambda r: f'<td class="c-val val">{int(r["value"]):,}</td>')}</div>
    {value_bars(svh, 12, "#1f6b3a", "SV+H value graph")}
    {sources_panel()}
    """
    write("bb/bullpen-holds.html", bb_page("Bullpen SV+H", "bullpen-holds.html", svh_body))

    rd_flt, rd_js = filter_js(["HIT", "SP", "RP", "UT"])
    rd_body = f"""
    <p class="kicker">Redraft ranking · this year</p>
    <h2>The Diamond</h2>
    <p class="note">This is the redraft list. One-year baseball, {len(redraft)} names. Use this board for 2026 rest-of-season and redraft startups.</p>
    {rd_flt}
    <div class="panel">{rank_table(redraft, ["Adj.", "BK Value"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="c-val val">{int(r["value"]):,}</td>', media=media, faces=True, show_age=True)}</div>
    {value_bars(redraft, 12, "#1f6b3a", "The Diamond value graph")}
    {sources_panel()}
    """
    write("bb/the-diamond.html", bb_page("The Diamond", "the-diamond.html", rd_body, rd_js))
    write("bb/redraft.html", bb_page(
        "The Diamond",
        "redraft.html",
        '<p class="kicker">Moved</p><h2>The Diamond</h2>'
        '<p class="note">The redraft ranking now lives on <a href="the-diamond.html">The Diamond</a>.</p>'
        '<p><a class="cta" href="the-diamond.html">The Diamond · Redraft</a></p>',
    ))

    modes = [
        trade_payload("Dynasty Overall", "trade-keep.html", "Uses The Keep overall ranks.", keep, picks),
        trade_payload("Dynasty Lineup", "trade-lineup.html", "Hitters only, The Lineup ranks.", lineup, picks),
        trade_payload("Dynasty Pitchers", "trade-pitchers.html", "BK's Pitchers ranks. Ohtani is here.", pitchers, picks),
        trade_payload("The Diamond", "trade-redraft.html", "The Diamond redraft ranking. This year only. No future picks.", redraft, []),
        trade_payload("Bullpen Saves", "trade-saves.html", "Saves-only RP board.", saves, []),
        trade_payload("Bullpen SV+H", "trade-svh.html", "Saves plus holds.", svh, []),
    ]
    for m in modes:
        write_trade(m)
    hub_tiles = [(m["file"], m["label"], m["blurb"]) for m in modes]
    trade_hub = f"""
    <p class="kicker">Trade Calculators</p>
    <h2>Six Calculators, One Curve</h2>
    <p class="note">Rank becomes BK Value the same way it does on the football desk. Rank 1 is 12,000. Fair is within 8%. Dynasty calcs include 2027/2028 pick chips mapped to equivalent ranks.</p>
    <div class="grid">{''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in hub_tiles)}</div>
    """
    write("bb/trade.html", bb_page("Trade Calculators", "trade.html", trade_hub))

    player_urls, player_files = write_player_pages(keep, lineup, pitchers, redraft, news_by_player, saves, svh)
    news_urls = render_bb_news_pages(stories)
    x_body = f"""
    <p class="kicker">Fun tape · not news</p>
    <h2>The X</h2>
    <p class="note">MLB memes and shitposts pulled from X. Pictures when the wire carries them.</p>
    {x_cards("baseball", 1, esc)}
    <p class="note" style="margin-top:16px"><a href="../the-x.html">Football The X</a> · <a href="../pl/the-x.html">PitchKeep The X</a></p>
    """
    write("bb/the-x.html", bb_page("The X", "the-x.html", x_body))
    (ROOT / "data/bb-keep.json").write_text(json.dumps({
        "updated": UPDATED,
        "keep": keep,
        "lineup": lineup,
        "pitchers": pitchers,
        "saves": saves,
        "svh": svh,
        "redraft": redraft,
    }, indent=2, default=str))
    return {
        "keep": keep,
        "lineup": lineup,
        "pitchers": pitchers,
        "saves": saves,
        "svh": svh,
        "redraft": redraft,
        "picks": picks,
        "files": player_files,
        "dynasty_waivers": DYNASTY_WAIVERS,
        "redraft_waivers": REDRAFT_WAIVERS,
        "source_names": [name for name, _u, _n in BB_SOURCES],
        "news": stories,
        "urls": ["https://ballkeep.com/bb/"] + [
            "https://ballkeep.com/bb/" + p
            for p in [
                "the-keep.html", "news.html", "the-x.html", "the-lineup.html", "pitchers.html", "bullpen.html",
                "bullpen-holds.html", "the-diamond.html", "redraft.html", "trade.html",
                "trade-keep.html", "trade-lineup.html", "trade-pitchers.html",
                "trade-redraft.html", "trade-saves.html", "trade-svh.html",
                "players/",
            ]
        ] + news_urls + player_urls,
        "n_keep": len(keep),
        "n_players": len(keep),
        "n_saves": len(saves),
        "n_svh": len(svh),
        "n_lineup": len(lineup),
        "n_pitchers": len(pitchers),
        "n_news": max(0, len(news_urls) - 1),
    }
