#!/usr/bin/env python3
"""Build the PitchKeep static section under pl/."""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from datetime import date
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 27, 2026"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pl_data import PL_SOURCES, bk_value, load_universe  # noqa: E402
from pl_copy import get_pl_copy  # noqa: E402
from news_algo import (  # noqa: E402
    CATEGORY_LABEL,
    build_player_index,
    load_news_stories,
    news_when,
    rematch_stories,
)
from x_tape import cards_html as x_cards  # noqa: E402
from seo import (  # noqa: E402
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
    canon,
    clip,
    dual_metric_graph,
    face_alt,
    faq_html,
    faq_jsonld,
    footer_nav,
    head_tags,
    legal_links,
    person_jsonld,
    rank_list_jsonld,
    rank_search_bar,
    rank_search_key,
    rank_spread_graph,
    related_players_html,
    related_stories_html,
    sports_footer,
    sports_top,
    strip_em,
    value_bars,
    video_jsonld,
    website_jsonld,
)


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
    dest.write_text(strip_em(doc))


PL_NAV = [
    ("index.html", "Home"),
    ("the-premier.html", "The Premier"),
    ("the-pitch.html", "The Pitch"),
    ("news.html", "News"),
    ("the-x.html", "The X"),
    ("attack.html", "Attack"),
    ("midfield.html", "Midfield"),
    ("defence.html", "Defence"),
    ("keepers.html", "Keepers"),
    ("trade.html", "Trade"),
    ("players/index.html", "Players"),
]


def wordmark():
    return '<span class="word-pitch">PITCH</span><span class="word-keep">KEEP</span>'


def masthead(kicker, mark, sub, url="ballkeep.com/pl"):
    return (
        f'<section class="hero masthead" aria-label="{esc(kicker)}">'
        f'<div class="hero-card">'
        f'<div class="mast-row">'
        f'<img class="mast-mark" src="../img/pl-logo.jpg" alt="PitchKeep circular soccer logo" />'
        f'<div class="mast-copy">'
        f'<p class="mast-kicker">{esc(kicker)}</p>'
        f"<h1>{mark}</h1>"
        f'<span class="mast-rule" aria-hidden="true"></span>'
        f'<p class="mast-sub">{esc(sub)}</p>'
        f'<p class="mast-url">{esc(url)}</p>'
        f"</div>"
        f'<div class="mast-art" aria-hidden="true"><img src="../img/mast-ballkeep.jpg" alt="" /></div>'
        f"</div></div></section>"
    )


PL_SEO = {
    "index.html": (
        "PitchKeep | The Premier Hybrid Rankings and Sleeper BPL 2025",
        "Purple-and-pitch boards for the Premier League. The Premier is 25 published 2026/27 pro lists. The Pitch is Sleeper only. Haaland is #1.",
        "img/pl-hero.jpg",
    ),
    "the-premier.html": (
        "The Premier - Hybrid Premier League Rankings (Top 400) | PitchKeep",
        "PitchKeep flagship 400: 25 published 2026/27 pro lists. Haaland is 1.01. Palmer, Saka, and Isak climb off last-year volume. Full names and ages on the row.",
        "img/pl-logo.jpg",
    ),
    "the-pitch.html": (
        "The Pitch - Sleeper BPL 2025 Premier League Rankings (Top 400) | PitchKeep",
        "Overall Premier League top 400 ranked on Sleeper BPL 2025 points. FWD/MID goals 9, DEF/GKP 10, assists 6/7. Erling Haaland leads at 317.2.",
        "img/pl-logo.jpg",
    ),
    "attack.html": (
        "Premier League Forward Rankings - Sleeper BPL 2025 | PitchKeep",
        "FPL forwards re-ranked on Sleeper BPL 2025 points. Haaland is the tax. Igor Thiago and João Pedro are the volume argument.",
        "img/pl-logo.jpg",
    ),
    "midfield.html": (
        "Premier League Midfielder Rankings - Sleeper BPL 2025 | PitchKeep",
        "Sleeper pays assists. Bruno Fernandes, Antoine Semenyo, Declan Rice - The Pitch midfield 150.",
        "img/pl-logo.jpg",
    ),
    "defence.html": (
        "Premier League Defender Rankings - Sleeper BPL 2025 | PitchKeep",
        "Clean sheets are 6 points and goals against are −2. Gabriel Magalhães outscores half the midfield on this table.",
        "img/pl-logo.jpg",
    ),
    "keepers.html": (
        "Premier League Goalkeeper Rankings - Sleeper BPL 2025 | PitchKeep",
        "Saves at 2 and clean sheets at 8. Kelleher, Raya, and Donnarumma is the real fight.",
        "img/pl-logo.jpg",
    ),
    "the-x.html": (
        "The X - Premier League Memes from X | PitchKeep",
        "Fun tape, not news. Premier League and FPL memes pulled from X via Google News.",
        "img/pl-logo.jpg",
    ),
    "news.html": (
        "PK News - Premier League Injury and Team Tape | PitchKeep",
        "Hourly Premier League injury, team, and manager reports clustered with links back to PitchKeep player files.",
        "img/pl-logo.jpg",
    ),
    "trade.html": (
        "Premier League Fantasy Trade Calculator | PitchKeep",
        "Premier, Pitch, Attack, Midfield, Defence, Keepers. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "players/index.html": (
        "Premier League Player Files - The Premier | PitchKeep",
        "Every Premier 400 name: hybrid rank, Sleeper points, 2025/26 line, five-graf take, tape.",
        "img/pl-logo.jpg",
    ),
    "trade-premier.html": (
        "The Premier Trade Calculator | PitchKeep",
        "Trade calculator on The Premier ranks - 25 published 2026/27 pro lists. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "trade-pitch.html": (
        "The Pitch Trade Calculator | PitchKeep",
        "Trade calculator on The Pitch overall Sleeper BPL 2025 ranks. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "trade-attack.html": (
        "Premier League Forward Trade Calculator | PitchKeep",
        "Attack-only trade calculator. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "trade-midfield.html": (
        "Premier League Midfielder Trade Calculator | PitchKeep",
        "Midfield-only trade calculator. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "trade-defence.html": (
        "Premier League Defender Trade Calculator | PitchKeep",
        "Defence-only trade calculator. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "trade-keepers.html": (
        "Premier League Goalkeeper Trade Calculator | PitchKeep",
        "Keepers-only trade calculator. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
}

PL_ALSO = {
    "the-premier.html": [
        ("the-pitch.html", "The Pitch", "Sleeper BPL 2025 only."),
        ("attack.html", "Attack", "Forwards."),
        ("midfield.html", "Midfield", "Mids."),
        ("trade-premier.html", "Premier Calculator", "Hybrid ranks as BK Value."),
        ("players/index.html", "Player Files", "Every Premier name."),
        ("news.html", "PK News", "Injuries and transfers."),
    ],
    "the-pitch.html": [
        ("the-premier.html", "The Premier", "25 published lists."),
        ("attack.html", "Attack", "Forwards."),
        ("defence.html", "Defence", "Defenders."),
        ("keepers.html", "Keepers", "Goalkeepers."),
        ("trade-pitch.html", "Pitch Calculator", "Sleeper ranks."),
        ("players/index.html", "Player Files", "Headshot and tape."),
    ],
    "attack.html": [
        ("midfield.html", "Midfield", "Mids."),
        ("defence.html", "Defence", "Defenders."),
        ("the-pitch.html", "The Pitch", "Overall Sleeper 400."),
        ("trade-attack.html", "Attack Calculator", "Forwards only."),
    ],
    "midfield.html": [
        ("attack.html", "Attack", "Forwards."),
        ("defence.html", "Defence", "Defenders."),
        ("the-pitch.html", "The Pitch", "Overall Sleeper 400."),
        ("trade-midfield.html", "Midfield Calculator", "Mids only."),
    ],
    "defence.html": [
        ("keepers.html", "Keepers", "Goalkeepers."),
        ("midfield.html", "Midfield", "Mids."),
        ("the-pitch.html", "The Pitch", "Overall Sleeper 400."),
        ("trade-defence.html", "Defence Calculator", "Defenders only."),
    ],
    "keepers.html": [
        ("defence.html", "Defence", "Defenders."),
        ("the-pitch.html", "The Pitch", "Overall Sleeper 400."),
        ("trade-keepers.html", "Keepers Calculator", "GKs only."),
        ("the-premier.html", "The Premier", "Hybrid 400."),
    ],
    "news.html": [
        ("the-premier.html", "The Premier", "The ranks the wire moves."),
        ("players/index.html", "Player Files", "Named in the tape."),
        ("../news.html", "Football BK News", "NFL injury tape."),
        ("the-x.html", "The X", "PL memes."),
    ],
    "the-x.html": [
        ("news.html", "PK News", "The actual wire."),
        ("../the-x.html", "Football The X", "NFL memes."),
        ("../bb/the-x.html", "BaseKeep The X", "MLB memes."),
    ],
    "trade.html": [
        ("the-premier.html", "The Premier", "Hybrid ranks."),
        ("the-pitch.html", "The Pitch", "Sleeper ranks."),
        ("players/index.html", "Player Files", "Every name in the calc."),
    ],
    "players/index.html": [
        ("the-premier.html", "The Premier", "Hybrid 400."),
        ("the-pitch.html", "The Pitch", "Sleeper 400."),
        ("news.html", "PK News", "Hourly wire."),
        ("trade.html", "Trade Calculators", "Price any name."),
    ],
}

PL_HOME_FAQ = [
    ("What is PitchKeep?", "PitchKeep is Premier League on Ball Keep. The Premier is a 2026/27 hybrid 400 from 25 published lists. The Pitch is last season's Sleeper BPL points. Same BK Value curve."),
    ("Premier vs Pitch?", "The Premier is who the boards ranked for 2026/27. The Pitch is who scored on Sleeper last season. Use Premier for drafts, Pitch for the counting-stat tape."),
    ("Where is the soccer news?", "PK News clusters injury, transfer, and manager tape hourly, with links back to PitchKeep player files."),
]
PL_PREMIER_FAQ = [
    ("What is The Premier?", "Top 400 from 25 published 2026/27 pro lists plus official FPL metrics. Half Sleeper BPL 2025, half the boards. Unranked skipped."),
    ("How does BK Value work here?", "Premier rank becomes BK Value. Rank 1 is 12,000. Fair is within 8%."),
    ("What is The Pitch?", "The same 400 names ranked on Sleeper BPL 2025 scoring of 2025/26 counting stats."),
]
PL_TRADE_FAQ = [
    ("How does the PitchKeep calculator work?", "Rank becomes BK Value. Rank 1 is 12,000. Fair is within 8%. Premier uses the 2026/27 list. Pitch uses Sleeper."),
    ("Which calc should I use?", "Premier for 2026/27 drafts. Pitch when the deal is last season's Sleeper points. Position calcs when the trade is all forwards, mids, defenders, or keepers."),
]
PL_NEWS_FAQ = [
    ("Where does PK News come from?", "Hourly clusters from Premier League RSS, Google News, X, and YouTube, linked to PitchKeep player files."),
    ("How often does it refresh?", "The scrape runs every hour with the rest of Ball Keep."),
]


def pl_nav_target(href: str, path: str, depth: int) -> str:
    if depth == 2:
        target = href if href.startswith("players/") else "../" + href
        if href.startswith("players/") and path.startswith("players/"):
            target = href[len("players/") :]
        return target
    return href


def pl_page(title, path, body, extra_js="", depth=1, description=None, image=None, doc_title=None,
            crumbs=None, extra_jsonld=None, og_type="website", published=None, modified=None,
            robots=None):
    prefix = "../" * depth
    links = []
    for href, label in PL_NAV:
        cur = ' aria-current="page"' if (
            href == path
            or (href == "news.html" and (path == "news.html" or path.startswith("news/")))
        ) else ""
        target = pl_nav_target(href, path, depth)
        links.append(f'<a href="{esc(target)}"{cur}>{esc(label)}</a>')
    packed = PL_SEO.get(path)
    full_title = doc_title or (packed[0] if packed else f"{title} | PitchKeep")
    desc = description or (packed[1] if packed else f"{title} on PitchKeep. Premier League rankings on Sleeper BPL 2025 points. Updated {UPDATED}.")
    img = image or (packed[2] if packed else "img/pl-logo.jpg")
    foot = footer_nav([(pl_nav_target(h, path, depth), lab) for h, lab in PL_NAV], pl_nav_target(path, path, depth))
    crumb_html = crumbs or ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path, "pl/"), image=img, brand="PitchKeep", brand_url="https://ballkeep.com/pl/", extra_jsonld=extra_jsonld, og_type=og_type, published=published, modified=modified, robots=robots)}
  <link rel="stylesheet" href="{prefix}css/pl.css?v=37" />
  <link rel="icon" href="{prefix}img/pl-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/pl-logo.jpg" alt="PitchKeep circular soccer logo" width="56" height="56" />
        <div>
          <p class="brand-title">{wordmark()}</p>
          <p>Premier League ranks</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {sports_top("pl", depth)}
    {crumb_html}
    {body}
    <footer>
      © {date.today().year} PitchKeep · ballkeep.com/pl · Rankings aggregated {UPDATED}. Not affiliated with the Premier League or FPL.
      {foot}
      {legal_links(depth)}
      {sports_footer("pl", depth)}
    </footer>
  </div>
  {extra_js}
</body>
</html>
"""


def pl_board_page(title, path, body, extra_js="", depth=1, extra_jsonld=None):
    extra = also_on_desk(PL_ALSO.get(path) or [])
    home = "index.html" if depth == 1 else "../index.html"
    ld = [breadcrumb_jsonld([
        ("PitchKeep", "https://ballkeep.com/pl/"),
        (title, canon(path, "pl/")),
    ])]
    for blob in extra_jsonld or []:
        if blob:
            ld.append(blob)
    return pl_page(
        title, path, body + extra, extra_js, depth=depth,
        crumbs=breadcrumbs([("PitchKeep", home), (title, None)]),
        extra_jsonld=ld,
    )


def _rank_th(label):
    cls = ""
    if label == "BK Value":
        cls = "c-val"
    elif label == "£":
        cls = "c-price"
    elif label == "Age":
        cls = "c-age"
    elif label not in ("PK", "Player", "Pos", "Club"):
        cls = "desk-only"
    attr = f' class="{cls}"' if cls else ""
    return f"<th{attr}>{esc(label)}</th>"


def face_src(r, media, depth=1):
    slug = slugify(r.get("name") or "")
    m = (media or {}).get(r.get("key") or "") or (media or {}).get(slug) or {}
    img = m.get("image") or "img/pl-logo.jpg"
    prefix = "../" * depth
    return prefix + img


def rank_table(rows, extra_headers=None, extra_cells=None, player_prefix="", media=None, faces=False, depth=1, full_names=False, show_age=False):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    media = media or {}
    cols = ["PK", "Player", "Pos", "Club"]
    head = "".join(_rank_th(h) for h in cols + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        price = r.get("price")
        label = ((r.get("full_name") or r.get("name") or "").strip() if full_names else r["name"])
        slug = slugify(r["name"])
        href = f"{player_prefix}players/{slug}.html"
        price_bit = f" · £{price}" if price not in (None, "") else ""
        age_txt = str(r["age"]) if r.get("age") not in (None, "") else ""
        age_label = f"age {age_txt}" if show_age and age_txt else ""
        age_span = f'<span class="age-desc">{esc(age_label)}</span>' if age_label else ""
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}{esc(price_bit)}</div>"
        )
        face = ""
        if faces:
            face = f'<img class="face" src="{esc(face_src(r, media, depth))}" alt="{esc(face_alt(label))}" loading="lazy" />'
        stack = (
            f'<span class="name-stack"><a class="player-link" href="{esc(href)}">'
            f"<strong>{esc(label)}</strong></a>{age_span}{meta}</span>"
        )
        dn = rank_search_key(r.get("name"), label, pos, team)
        body.append(
            f'<tr data-pos="{esc(pos)}" data-group="{esc(r.get("group") or pos)}" data-name="{dn}">'
            f'<td class="rk c-rank">{r.get("bk","")}</td>'
            f'<td class="c-name">{face}{stack}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f"{extra_cells(r)}</tr>"
        )
    cls = "rank-table faces" if faces else "rank-table"
    return (
        f'<div class="table-wrap"><table class="{cls}">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def val_cell(r):
    return (
        f'<td class="desk-only">{r.get("sleeper_pts") if r.get("sleeper_pts") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("pts") if r.get("pts") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("gls") if r.get("gls") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("ast") if r.get("ast") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("minutes") if r.get("minutes") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("cs") if r.get("cs") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("tackles") if r.get("tackles") not in (None, "") else "-"}</td>'
        f'<td class="c-price">£{r.get("price") or "-"}</td>'
        f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


def premier_cell(r):
    return (
        f'<td class="desk-only">{r.get("premier_score") if r.get("premier_score") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("sleeper_rank") if r.get("sleeper_rank") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("consensus") if r.get("consensus") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("sleeper_pts") if r.get("sleeper_pts") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("pts") if r.get("pts") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("gls") if r.get("gls") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("ast") if r.get("ast") not in (None, "") else "-"}</td>'
        f'<td class="desk-only">{r.get("n") if r.get("n") not in (None, "") else "-"}</td>'
        f'<td class="c-price">£{r.get("price") or "-"}</td>'
        f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
    )


def filter_js(groups):
    btns = "".join(f'<button type="button" data-pos="{g}">{g}</button>' for g in groups)
    return f"""
    <div class="filters" id="posf"><button type="button" class="active" data-pos="all">All</button>{btns}</div>
    """, """<script>
    const box = document.getElementById('posf');
    if (box) box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      if (window.applyRankFilter) { applyRankFilter(); return; }
      const p = b.dataset.pos;
      document.querySelectorAll('tbody tr').forEach(tr => {
        const hit = p === 'all' || tr.dataset.pos === p || tr.dataset.group === p;
        tr.style.display = hit ? '' : 'none';
      });
    });
    </script>"""


def sources_panel():
    items = []
    for name, url, note in PL_SOURCES:
        label = f'<a href="{esc(url)}">{esc(name)}</a>' if url else esc(name)
        items.append(f"<li>{label} - {esc(note)}</li>")
    return (
        '<section class="panel sources-box"><p class="kicker">Sources</p>'
        "<h3>Boards we track</h3>"
        f"<ol>{''.join(items)}</ol></section>"
    )


def load_pl_media():
    path = ROOT / "data/pl-media.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def nz(v, dash="-"):
    if v in (None, "", []):
        return dash
    return v


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


def facts_table(r, media):
    items = []
    if r.get("number") or media.get("number"):
        items.append(("No.", f"#{r.get('number') or media.get('number')}"))
    if r.get("sleeper_pts") not in (None, "", 0, 0.0):
        items.append(("Sleeper BPL", r["sleeper_pts"]))
    if r.get("sleeper_rank"):
        items.append(("Sleeper rk", f"#{r['sleeper_rank']}"))
    if r.get("price"):
        items.append(("FPL £", f"£{r['price']}m"))
    if r.get("premier"):
        items.append(("Premier", f"#{r['premier']}"))
    if r.get("premier_score") not in (None, ""):
        items.append(("Hybrid", r["premier_score"]))
    if r.get("consensus") not in (None, ""):
        items.append(("Consensus", r["consensus"]))
    if r.get("n"):
        items.append(("# Boards", r["n"]))
    if r.get("value"):
        items.append(("BK Value", f"{int(r['value']):,}"))
    ranks = r.get("ranks") or {}
    if ranks:
        items.append(("Spread", f"{min(ranks.values())}–{max(ranks.values())}"))
    if r.get("pens") == 1:
        items.append(("Pens", "1st choice"))
    elif r.get("pens"):
        items.append(("Pens", f"#{r['pens']}"))
    if r.get("corners") == 1:
        items.append(("Corners", "1st choice"))
    elif r.get("corners"):
        items.append(("Corners", f"#{r['corners']}"))
    if r.get("dfk") == 1:
        items.append(("Direct FK", "1st choice"))
    elif r.get("dfk"):
        items.append(("Direct FK", f"#{r['dfk']}"))
    status = r.get("status") or "a"
    if status and status != "a":
        label = {"d": "Doubtful", "i": "Injured", "s": "Suspended", "u": "Unavailable", "n": "Not in squad"}.get(status, status)
        items.append(("Status", label))
    if r.get("tackles"):
        items.append(("Tackles", r["tackles"]))
    if r.get("cbi"):
        items.append(("CBI", r["cbi"]))
    if r.get("ict") not in (None, "", 0, 0.0):
        items.append(("ICT", r["ict"]))
    if r.get("form") not in (None, "", 0, 0.0):
        items.append(("Form", r["form"]))
    if r.get("ep") not in (None, "", 0, 0.0):
        items.append(("EP next", r["ep"]))
    if not items:
        return ""
    cells = "".join(
        f'<div class="fact"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in items
    )
    return f'<div class="facts">{cells}</div>'


def stat_pills(r):
    pills = [
        ("Sleeper", r.get("sleeper_pts")),
        ("FPL", r.get("pts")),
        ("G", r.get("gls")),
        ("A", r.get("ast")),
        ("Min", r.get("minutes")),
        ("Starts", r.get("starts")),
        ("CS", r.get("cs")),
        ("Tck", r.get("tackles")),
        ("CBI", r.get("cbi")),
        ("Saves", r.get("saves") if r.get("pos") == "GKP" else None),
        ("xG", r.get("xg")),
        ("xA", r.get("xa")),
        ("xGI", r.get("xgi")),
        ("Bonus", r.get("bonus")),
        ("PPG", r.get("ppg")),
        ("Form", r.get("form")),
        ("EP", r.get("ep")),
    ]
    pills = [(k, v) for k, v in pills if v not in (None, "", 0, "0", 0.0)]
    if not pills:
        return ""
    cells = "".join(
        f'<div class="stat-pill"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in pills[:10]
    )
    return f'<div class="stat-strip">{cells}</div>'


def season_box(r):
    if not (r.get("minutes") or r.get("pts") or r.get("starts")):
        return ""
    cells = [
        "2025/26",
        r.get("starts") if r.get("starts") not in (None, "") else "-",
        r.get("minutes") if r.get("minutes") not in (None, "") else "-",
        r.get("gls") if r.get("gls") not in (None, "") else "-",
        r.get("ast") if r.get("ast") not in (None, "") else "-",
        r.get("xg") if r.get("xg") not in (None, "") else "-",
        r.get("xa") if r.get("xa") not in (None, "") else "-",
        r.get("cs") if r.get("cs") not in (None, "") else "-",
        r.get("gc") if r.get("gc") not in (None, "") else "-",
        r.get("bonus") if r.get("bonus") not in (None, "") else "-",
        r.get("yc") if r.get("yc") not in (None, "") else "-",
        r.get("sleeper_pts") if r.get("sleeper_pts") not in (None, "") else "-",
        r.get("pts") if r.get("pts") not in (None, "") else "-",
    ]
    if r.get("pos") == "GKP":
        cells[8] = r.get("saves") if r.get("saves") not in (None, "") else "-"
        gc_label = "Saves"
    else:
        gc_label = "GC"
    row = "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in cells) + "</tr>"
    return (
        '<div class="panel season">'
        '<p class="kicker">2025/26 Premier League</p>'
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Year</th><th>Starts</th><th>Min</th><th>G</th><th>A</th>"
        "<th>xG</th><th>xA</th><th>CS</th>"
        f"<th>{gc_label}</th><th>Bonus</th><th>YC</th><th>Sleeper</th><th>FPL</th>"
        f"</tr></thead><tbody>{row}</tbody></table></div></div>"
    )


def news_flag(r):
    news = (r.get("news") or "").strip()
    status = r.get("status") or "a"
    if not news and status == "a":
        return ""
    label = {"d": "Doubtful", "i": "Injured", "s": "Suspended", "u": "Unavailable", "n": "Not in squad"}.get(status, "")
    bits = []
    if label:
        bits.append(f"<strong>{esc(label)}</strong>")
    if news:
        bits.append(esc(news))
    if r.get("chance") not in (None, ""):
        bits.append(f"Chance of playing: {esc(r['chance'])}%")
    return (
        '<section class="panel news-flag">'
        '<p class="kicker">FPL news</p>'
        f"<p>{' - '.join(bits)}</p></section>"
    )


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


def neighbors(board, idx, label="On The Premier nearby"):
    if not board or idx < 0 or idx >= len(board):
        return ""
    return related_players_html(
        board,
        board[idx],
        lambda p: f"{p.get('slug') or slugify(p['name'])}.html",
        nearby_label=label,
        pos_label="Same position on the 400",
        team_label="Same club",
    )


def same_pos(pitch, r, limit=6):
    pos = r.get("pos") or ""
    others = [p for p in pitch if p["key"] != r["key"] and p.get("pos") == pos][:limit]
    if not others:
        return ""
    links = " · ".join(
        f'<a class="player-link" href="{slugify(p["name"])}.html">{esc(p["name"])}</a> #{p["bk"]}'
        for p in others
    )
    return f'<p class="note"><strong>Same position on the 400</strong> - {links}</p>'


def video_block(media, name):
    yt = (media or {}).get("youtube_id") or ""
    if not yt:
        return (
            '<p class="note">Tape is still being matched. Refresh this file with The Pitch - '
            "we embed a 2025/26 Premier League highlight when YouTube gives us a clean clip.</p>"
        )
    title = media.get("youtube_title") or f"{name} highlights"
    return f"""
    <p class="kicker" style="margin-top:22px">Tape · 2025/26 Premier League</p>
    <h3>{esc(title)}</h3>
    <div class="video-wrap">
      <iframe src="https://www.youtube-nocookie.com/embed/{esc(yt)}" title="{esc(title)}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen loading="lazy"></iframe>
    </div>
    """


def pl_grafs(r, lists, media):
    keep = r.get("bk")
    n = r.get("n") or 0
    avg = r.get("avg")
    ranks = r.get("ranks") or {}
    price = r.get("price")
    pts = r.get("pts") or 0
    gls = r.get("gls") or 0
    ast = r.get("ast") or 0
    minutes = r.get("minutes") or 0
    starts = r.get("starts") or 0
    xg = r.get("xg") or 0
    xa = r.get("xa") or 0
    news = (r.get("news") or "").strip()
    plus, minus = [], []
    if news:
        minus.append(news)
    if xg and gls is not None and xg - gls >= 4:
        plus.append(f"{gls} G on {xg} xG - finishing ran cold.")
    if xg and gls is not None and gls - xg >= 4:
        minus.append(f"{gls} G on {xg} xG - finishing ran hot.")
    bits = []
    if r.get("sleeper_pts") not in (None, "", 0, 0.0):
        bits.append(f"{r['sleeper_pts']} Sleeper")
    if keep:
        bits.append(f"Pitch #{keep}")
    if avg is not None:
        bits.append(f"avg {avg}")
    if n:
        bits.append(f"{n} boards")
    if price not in (None, ""):
        bits.append(f"£{price}m")
    if pts:
        bits.append(f"{pts} pts")
    if gls or ast:
        bits.append(f"{gls}G {ast}A")
    if starts:
        bits.append(f"{starts} starts")
    if minutes:
        bits.append(f"{minutes} min")
    if xg or xa:
        bits.append(f"{xg} xG / {xa} xA")
    graf = " · ".join(str(b) for b in bits)
    return plus[:4], minus[:4], [graf] if graf else []


def take_html(grafs):
    grafs = [g for g in (grafs or []) if g]
    if not grafs:
        return ""
    return (
        '<section class="panel analysis">'
        '<p class="kicker">PitchKeep Take · The Premier</p>'
        + "".join(f"<p>{esc(g)}</p>" for g in grafs)
        + "</section>"
    )


def list_cards(lists, r):
    items = [
        ("The Premier", lists.get("The Premier"), r.get("value") if lists.get("The Premier") == r.get("premier") else None),
        ("The Pitch", lists.get("The Pitch"), None),
        ("Attack", lists.get("Attack"), None),
        ("Midfield", lists.get("Midfield"), None),
        ("Defence", lists.get("Defence"), None),
        ("Keepers", lists.get("Keepers"), None),
    ]
    cards = []
    for label, rank, val in items:
        if not rank:
            continue
        value = bk_value(rank)
        cards.append(
            f'<div class="rank-card"><small>{esc(label)}</small>'
            f"<strong>#{rank}</strong><span>BK {int(value):,}</span></div>"
        )
    return f'<div class="rank-grid">{"".join(cards)}</div>' if cards else ""


def write_player_pages(pitch, premier, fwd, mid, defence, gkp, news_by_player=None):
    news_by_player = news_by_player or {}
    fm = {r["key"]: r for r in fwd}
    mm = {r["key"]: r for r in mid}
    dm = {r["key"]: r for r in defence}
    gm = {r["key"]: r for r in gkp}
    prem_map = {r["key"]: r for r in premier}
    pitch_map = {r["key"]: r for r in pitch}
    media_all = load_pl_media()
    # Premier 400 first; then anyone on The Pitch who missed the hybrid.
    ordered = list(premier)
    seen = {r["key"] for r in ordered}
    for r in pitch:
        if r["key"] not in seen:
            rec = dict(r)
            rec["bk"] = rec.get("premier") or rec.get("bk")
            ordered.append(rec)
            seen.add(r["key"])
    cards, urls, files = [], [], []
    used_slugs = set()
    keep_html = {"index.html"}
    for i, r in enumerate(ordered):
        slug = slugify(r["name"])
        if slug in used_slugs:
            slug = slugify(f"{r['name']}-{r.get('team') or r['key']}")
        used_slugs.add(slug)
        r["slug"] = slug
        media = media_all.get(r["key"]) or media_all.get(slug) or {}
        pitch_row = pitch_map.get(r["key"])
        prem_row = prem_map.get(r["key"]) or r
        lists = {}
        if prem_row:
            lists["The Premier"] = prem_row.get("premier") or prem_row.get("bk")
        if pitch_row:
            lists["The Pitch"] = pitch_row.get("sleeper_rank") or pitch_row.get("bk")
        if r["key"] in fm:
            lists["Attack"] = fm[r["key"]]["bk"]
        if r["key"] in mm:
            lists["Midfield"] = mm[r["key"]]["bk"]
        if r["key"] in dm:
            lists["Defence"] = dm[r["key"]]["bk"]
        if r["key"] in gm:
            lists["Keepers"] = gm[r["key"]]["bk"]
        near = [p for p in ordered[max(0, i - 2): i] + ordered[i + 1: i + 3]]
        copy = get_pl_copy(r["key"], prem_row, lists, near)
        plus, minus, grafs = copy["plus"], copy["minus"], copy["grafs"]
        img = media.get("image") or "img/pl-logo.jpg"
        img_src = "../../" + img
        bio = " · ".join(
            str(x) for x in (
                f"#{r['number']}" if r.get("number") else "",
                r.get("pos") or "",
                r.get("team_name") or r.get("team") or "",
                f"age {r['age']}" if r.get("age") else "",
                f"£{r['price']}m" if r.get("price") else "",
            ) if x
        )
        prem_rk = lists.get("The Premier")
        label = (r.get("full_name") or r.get("name") or "").strip()
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
                '<p class="kicker" style="margin-top:22px">PK News</p>'
                f'<ul class="source-list">{lis}</ul>'
            )
        body = f"""
    <p class="kicker">Player File · {esc(r.get("pos") or "")} {esc(r.get("team") or "")} · Premier #{prem_rk or "-"}</p>
    <div class="player-hero">
      <img src="{esc(img_src)}" alt="{esc(face_alt(label))}" />
      <div>
        <h1>{esc(r["name"])}</h1>
        <p class="note">{esc(bio)}</p>
      </div>
    </div>
    {facts_table(prem_row, media)}
    {season_box(prem_row)}
    {news_flag(prem_row)}
    {list_cards(lists, prem_row)}
    {plusminus_html(plus, minus)}
    {take_html(grafs)}
    {dual_metric_graph([
        ("Sleeper BPL", "#e8c547", r.get("sleeper_pts") or 0),
        ("FPL points", "#00c853", r.get("pts") or 0),
    ], "Sleeper vs FPL")}
    {rank_spread_graph(prem_row.get("ranks") or r.get("ranks") or {}, fill="#e8c547", kicker="Board graph")}
    {video_block(media, r["name"])}
    {boards_table(prem_row.get("ranks") or r.get("ranks") or {})}
    {news_block}
    {neighbors(ordered, i, "On The Premier nearby")}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-premier.html">The Premier</a> · <a href="../the-pitch.html">The Pitch</a> · <a href="../news.html">PK News</a> · <a href="../trade.html">Calculator</a></p>
    """
        seo_title = f"{label} The Premier Rank #{prem_rk or r['bk']} ({r.get('pos') or ''} {r.get('team') or ''})".strip()
        seo_desc = clip(
            f"{label} is PitchKeep Premier #{prem_rk or r['bk']}. "
            f"Sleeper BPL 2025 {r.get('sleeper_pts') or '-'} pts ({r.get('gls') or 0}G {r.get('ast') or 0}A). "
            f"{r.get('pos') or ''} {r.get('team_name') or r.get('team') or ''}. Updated {UPDATED}."
        )
        player_abs = f"https://ballkeep.com/pl/players/{slug}.html"
        extra_ld = [
                    breadcrumb_jsonld([
                        ("PitchKeep", "https://ballkeep.com/pl/"),
                        ("Players", "https://ballkeep.com/pl/players/"),
                        (label, player_abs),
                    ]),
                    person_jsonld(
                        label, player_abs,
                        pos=r.get("pos") or "",
                        team=r.get("team_name") or r.get("team") or "",
                        image=img,
                        description=seo_desc,
                        sport="Soccer",
                    ),
                ]
        yt = (media or {}).get("youtube_id") or ""
        if yt:
            extra_ld.append(video_jsonld(
                media.get("youtube_title") or f"{label} highlights",
                yt,
                description=seo_desc,
                brand="PitchKeep",
                brand_url="https://ballkeep.com/pl/",
            ))
        write(
            f"pl/players/{slug}.html",
            pl_page(
                label, f"players/{slug}.html", body, depth=2,
                doc_title=seo_title, description=seo_desc, image=img,
                crumbs=breadcrumbs([
                    ("PitchKeep", "../index.html"),
                    ("Players", "index.html"),
                    (label, None),
                ]),
                extra_jsonld=extra_ld,
            ),
        )
        keep_html.add(f"{slug}.html")
        cards.append(
            f'<a class="tile player-card" href="{slug}.html" data-pos="{esc(r.get("pos") or "")}" data-group="{esc(r.get("group") or "")}">'
            f'<img src="../../{esc(img)}" alt="{esc(face_alt(label))}" />'
            f'<h3>{esc(label)}</h3>'
            f'<p>{esc(r.get("pos") or "")} {esc(r.get("team") or "")} · Premier #{prem_rk or "-"}</p></a>'
        )
        urls.append(f"https://ballkeep.com/pl/players/{slug}.html")
        files.append({
            "key": r["key"],
            "slug": slug,
            "name": r["name"],
            "full_name": r.get("full_name") or r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "team_name": r.get("team_name") or "",
            "age": r.get("age") or "",
            "group": r.get("group") or "",
            "lists": lists,
            "plus": plus,
            "minus": minus,
            "grafs": grafs,
            "sport": "soccer",
            "url": f"https://ballkeep.com/pl/players/{slug}.html",
            "value": prem_row.get("value") or r.get("value"),
            "bk": prem_rk or r.get("bk"),
            "keep_avg": prem_row.get("premier_score") or r.get("avg"),
            "keep_n": r.get("n"),
            "image": img,
            "youtube_id": media.get("youtube_id") or "",
            "youtube_title": media.get("youtube_title") or "",
            "price": r.get("price"),
            "sel": r.get("sel"),
            "pts": r.get("pts"),
            "sleeper_pts": r.get("sleeper_pts"),
            "gls": r.get("gls"),
            "ast": r.get("ast"),
        })
    flt, js = filter_js(["FWD", "MID", "DEF", "GKP"])
    hub = f"""
    <p class="kicker">Player files</p>
    <h1>The Premier, one name at a time</h1>
    <p class="note">Headshot, 2025/26 line, boards, tape.</p>
    {flt}
    <div class="player-grid" id="pl-cards">{''.join(cards)}</div>
    {also_on_desk([
        ("../the-premier.html", "The Premier", "Hybrid 400."),
        ("../the-pitch.html", "The Pitch", "Sleeper 400."),
        ("../news.html", "PK News", "Hourly wire."),
        ("../trade.html", "Trade Calculators", "Price any name."),
    ])}
    """
    hub_js = js.replace("tbody tr", "#pl-cards .tile")
    write("pl/players/index.html", pl_page(
        "Players", "players/index.html", hub, hub_js, depth=2,
        crumbs=breadcrumbs([("PitchKeep", "../index.html"), ("Players", None)]),
        extra_jsonld=[breadcrumb_jsonld([
            ("PitchKeep", "https://ballkeep.com/pl/"),
            ("Players", "https://ballkeep.com/pl/players/"),
        ])],
    ))
    dest = ROOT / "pl" / "players"
    for old in dest.glob("*.html"):
        if old.name not in keep_html:
            old.unlink()
    return urls, files
def trade_payload(label, file, blurb, rows):
    players = []
    for r in rows:
        players.append({
            "id": slugify(r["name"]),
            "name": r.get("full_name") or r["name"],
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
        "picks": [],
    }


def write_trade(payload):
    body = f"""
    <p class="kicker">Trade Calculator</p>
    <h1>{esc(payload["label"])}</h1>
    <p class="note">{esc(payload["blurb"])} Fair is within 8%. Same BK Value curve: rank 1 = 12,000.</p>
    <p class="filters">
      <a href="trade.html">All</a>
      <a href="trade-premier.html">The Premier</a>
      <a href="trade-pitch.html">The Pitch</a>
      <a href="trade-attack.html">Attack</a>
      <a href="trade-midfield.html">Midfield</a>
      <a href="trade-defence.html">Defence</a>
      <a href="trade-keepers.html">Keepers</a>
    </p>
    <div id="trade-app" class="trade-app"></div>
    """
    blob = json.dumps(payload, ensure_ascii=False)
    extra = f"<script>window.BK_TRADE = {blob};</script>\n<script src=\"../js/trade.js\"></script>"
    write("pl/" + payload["file"], pl_page(payload["label"], payload["file"], body, extra, depth=1))


def pl_news_card(story: dict, prefix: str = "") -> str:
    cat = story.get("category") or "wire"
    label = CATEGORY_LABEL.get(cat, cat.title())
    href = f"{prefix}news/{esc(story['slug'])}.html"
    bits = [f"{len(story.get('sources') or [])} sources"]
    kinds = {src.get("kind") for src in (story.get("sources") or [])}
    if "x" in kinds:
        bits.append("X")
    if "video" in kinds:
        bits.append("video")
    chips = " ".join(
        f'<span class="chip">{esc(p.get("name") or "")}</span>'
        for p in (story.get("players") or [])[:6]
    )
    return (
        f'<a class="news-item tile" href="{href}">'
        f'<div class="news-meta"><span class="kind {esc(cat)}">{esc(label)}</span> '
        f'{esc(news_when(story.get("updated") or story.get("published") or ""))} · {esc(" · ".join(bits))}</div>'
        f'<h3>{esc(story.get("headline") or "Update")}</h3>'
        f'<p>{esc(story.get("blurb") or story.get("summary") or "")}</p>'
        f'<div class="news-players">{chips}</div></a>'
    )


def render_pl_news_pages(stories: list[dict]) -> list[str]:
    dest = ROOT / "pl" / "news"
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("*.html"):
        old.unlink()
    cards = "".join(pl_news_card(s) for s in stories) or '<p class="note">Awaiting first successful pull.</p>'
    cats = []
    for s in stories:
        c = s.get("category") or "wire"
        if c not in cats:
            cats.append(c)
    chips = ['<button type="button" class="active" data-cat="all">All</button>']
    chips += [f'<button type="button" data-cat="{esc(c)}">{esc(CATEGORY_LABEL.get(c, c))}</button>' for c in cats]
    payload = json.dumps([{"cat": s.get("category") or "wire", "html": pl_news_card(s)} for s in stories])
    extra = f"""<script>
    const STORIES = {payload};
    const box = document.getElementById('news-list');
    document.getElementById('news-filters').addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      document.querySelectorAll('#news-filters button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const cat = b.dataset.cat;
      box.innerHTML = STORIES.filter(s => cat === 'all' || s.cat === cat).map(s => s.html).join('') || '<p class="note">Nothing in this bucket.</p>';
    }});
    </script>"""
    updated = stories[0].get("updated") if stories else ""
    body = f"""
    <p class="kicker">PitchKeep News</p>
    <h1>Latest on the wire.</h1>
    <p class="note">Injuries, transfers, manager news. Same clustering as football.</p>
    <p class="note">{f"Last cluster {esc(news_when(updated))}." if updated else "Awaiting first successful pull."}</p>
    <div class="filters" id="news-filters">{''.join(chips)}</div>
    <div class="news-list" id="news-list">{cards}</div>
    {faq_html(PL_NEWS_FAQ, heading="How the PitchKeep wire works.")}
    {also_on_desk(PL_ALSO["news.html"])}
    """
    write("pl/news.html", pl_page(
        "PK News", "news.html", body, extra,
        crumbs=breadcrumbs([("PitchKeep", "index.html"), ("PK News", None)]),
        extra_jsonld=[
            breadcrumb_jsonld([
                ("PitchKeep", "https://ballkeep.com/pl/"),
                ("PK News", "https://ballkeep.com/pl/news.html"),
            ]),
            faq_jsonld(PL_NEWS_FAQ),
        ],
    ))
    urls = ["https://ballkeep.com/pl/news.html"]
    for s in stories:
        slug = s.get("slug") or ""
        if not slug:
            continue
        nsrc = len(s.get("sources") or [])
        source_html = "".join(
            f'<li><a href="{esc(src.get("url") or "#")}">{esc(src.get("title") or src.get("publisher") or "Source")}</a> '
            f'<span class="news-meta">{esc(src.get("publisher") or "")}</span></li>'
            for src in (s.get("sources") or [])
        )
        players = "".join(
            f'<a class="tile" href="../players/{esc(slugify(p.get("name") or ""))}.html"><h3>{esc(p.get("name") or "")}</h3></a>'
            for p in (s.get("players") or [])
        )
        related = related_stories_html(stories, s, lambda st: f"{st['slug']}.html")
        story_body = f"""
    <p class="kicker">{esc(CATEGORY_LABEL.get(s.get("category") or "", "Wire"))}</p>
    <h1>{esc(s.get("headline") or "PK News")}</h1>
    <p class="news-meta">{esc(news_when(s.get("updated") or s.get("published") or ""))} · {nsrc} source{"s" if nsrc != 1 else ""}</p>
    <section class="panel"><p class="note">{esc(s.get("summary") or s.get("blurb") or "")}</p></section>
    <section class="panel" style="margin-top:16px"><p class="kicker">Sources</p><ol>{source_html}</ol></section>
    <div class="grid" style="margin-top:16px">{players}</div>
    {related}
    <p class="note" style="margin-top:18px"><a href="../news.html">All PK News</a> · <a href="../players/index.html">Player files</a> · <a href="../the-premier.html">The Premier</a></p>
    """
        story_url = f"https://ballkeep.com/pl/news/{slug}.html"
        story_desc = clip(s.get("summary") or s.get("blurb") or s.get("headline") or "PitchKeep soccer story.")
        write(
            f"pl/news/{slug}.html",
            pl_page(
                s.get("headline") or "PK News", f"news/{slug}.html", story_body, depth=2,
                description=story_desc,
                crumbs=breadcrumbs([
                    ("PitchKeep", "../index.html"),
                    ("PK News", "../news.html"),
                    (s.get("headline") or "Update", None),
                ]),
                extra_jsonld=[
                    breadcrumb_jsonld([
                        ("PitchKeep", "https://ballkeep.com/pl/"),
                        ("PK News", "https://ballkeep.com/pl/news.html"),
                        (s.get("headline") or "Update", story_url),
                    ]),
                    article_jsonld(
                        s.get("headline") or "PK News", story_url, story_desc,
                        published=s.get("published") or "",
                        modified=s.get("updated") or "",
                        image="img/pl-logo.jpg",
                        brand="PitchKeep",
                        brand_url="https://ballkeep.com/pl/",
                        section=CATEGORY_LABEL.get(s.get("category") or "wire", "Wire"),
                    ),
                ],
                og_type="article",
                published=s.get("published"),
                modified=s.get("updated"),
            ),
        )
        urls.append(f"https://ballkeep.com/pl/news/{slug}.html")
    return urls


def write_pitch_site():
    u = load_universe()
    pitch, premier = u["pitch"], u["premier"]
    fwd, mid, defence, gkp = u["fwd"], u["mid"], u["def"], u["gkp"]
    media = load_pl_media()

    roster = [
        {"key": r.get("key") or "", "name": r["name"], "slug": slugify(r["name"]), "pos": r.get("pos") or "", "team": r.get("team") or ""}
        for r in premier
    ]
    stories = rematch_stories(load_news_stories("soccer"), build_player_index(roster))
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
            + "".join(pl_news_card(s) for s in latest_news)
            + "</div>"
            '<p class="note" style="margin-top:12px"><a href="news.html">All PK News</a></p>'
        )
    home = f"""
    {masthead("Premier League rankings", wordmark(), "The Premier · The Pitch")}
    {desk_block("main", "Main", "The Premier and The Pitch.", "Premier: 25 published 2026/27 lists. Pitch: Sleeper points.", [
        ("the-premier.html", "The Premier", "Hybrid 400."),
        ("the-pitch.html", "The Pitch", "Sleeper BPL 2025."),
    ])}
    {desk_block("lists", "Lists", "The position boards.", "Forwards, mids, defenders, keepers. Sleeper-ranked.", [
        ("attack.html", "Attack", "Forwards."),
        ("midfield.html", "Midfield", "Mids."),
        ("defence.html", "Defence", "Defenders."),
        ("keepers.html", "Keepers", "Keepers."),
    ])}
    {desk_block("tools", "Tools", "Calculators and files.", "Price a deal or open a player file.", [
        ("trade.html", "Trade Calculators", "Premier, Pitch, the lists."),
        ("players/index.html", "Player Files", "Headshot, line, boards, tape."),
    ])}
    {desk_block("extra", "Extra", "News and The X.", "Memes and the wire.", [
        ("the-x.html", "The X", "PL memes. Pictures on the card."),
        ("news.html", "PK News", "Injuries, transfers, managers."),
    ], extra_news)}
    {faq_html(PL_HOME_FAQ, heading="How PitchKeep works.")}
    """
    write("pl/index.html", pl_page(
        "Home", "index.html", home,
        extra_jsonld=[website_jsonld("PitchKeep", "https://ballkeep.com/pl/"), faq_jsonld(PL_HOME_FAQ)],
    ))

    flt, js = filter_js(["FWD", "MID", "DEF", "GKP"])
    premier_body = f"""
    <p class="kicker">Hybrid 400 · {UPDATED}</p>
    <h1>The Premier</h1>
    <p class="note">Top 400. Half Sleeper BPL 2025, half 25 published pro lists plus official FPL metrics. Unranked skipped. Rank 1 is 12,000.</p>
    {rank_search_bar(flt)}
    <div class="panel">{rank_table(premier, ["Hybrid", "Sleeper rk", "Cons.", "Sleeper", "FPL", "G", "A", "Boards", "£", "BK Value"], premier_cell, media=media, faces=True, full_names=True, show_age=True)}</div>
    {value_bars(premier, 12, "#e8c547", "Premier value graph")}
    {sources_panel()}
    {faq_html(PL_PREMIER_FAQ, heading="How The Premier is built.")}
    """
    write("pl/the-premier.html", pl_board_page(
        "The Premier", "the-premier.html", premier_body, js,
        extra_jsonld=[
            rank_list_jsonld(
                "The Premier 2026/27 Rankings",
                "https://ballkeep.com/pl/the-premier.html",
                premier,
                lambda r: f"https://ballkeep.com/pl/players/{slugify(r['name'])}.html",
                description="Premier League hybrid 400 from 25 published lists.",
            ),
            faq_jsonld(PL_PREMIER_FAQ),
        ],
    ))

    pitch_body = f"""
    <p class="kicker">Sleeper BPL 2025</p>
    <h1>The Pitch</h1>
    <p class="note">Top 400. Sleeper scoring. Goal 9/10, assist 6/7, clean sheet 0/1/6/8, save 2. Rank 1 is 12,000.</p>
    {rank_search_bar(flt)}
    <div class="panel">{rank_table(pitch, ["Sleeper", "FPL", "G", "A", "Min", "CS", "Tck", "£", "BK Value"], val_cell, media=media, faces=True)}</div>
    {value_bars(pitch, 12, "#e8c547", "Sleeper points graph", key="sleeper_pts", heading="Sleeper BPL 2025, top 12", note="Default Sleeper soccer scoring on 2025/26 counting stats. Haaland is 317.2. Bruno is 293.8.")}
    {value_bars(pitch, 12, "#00c853", "Pitch value graph")}
    {sources_panel()}
    """
    write("pl/the-pitch.html", pl_board_page("The Pitch", "the-pitch.html", pitch_body, js))

    for path, title, kicker, note, rows in [
        ("attack.html", "Attack", "Forwards", "Forwards only, Sleeper BPL 2025.", fwd),
        ("midfield.html", "Midfield", "Midfield", "Midfielders only, Sleeper BPL 2025.", mid),
        ("defence.html", "Defence", "Defence", "Defenders only, Sleeper BPL 2025.", defence),
        ("keepers.html", "Keepers", "Keepers", "Goalkeepers only, Sleeper BPL 2025.", gkp),
    ]:
        body = f"""
    <p class="kicker">{esc(kicker)}</p>
    <h1>{esc(title)}</h1>
    <p class="note">{esc(note)}</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(rows, ["Sleeper", "FPL", "G", "A", "Min", "CS", "Tck", "£", "BK Value"], val_cell)}</div>
    {value_bars(rows, 12, "#e8c547", f"{title} points graph", key="sleeper_pts", heading=f"Sleeper BPL 2025 {title.lower()}, top 12", note="Same Sleeper table as The Pitch, this position only.")}
    {value_bars(rows, 12, "#00c853", f"{title} value graph")}
    {sources_panel()}
    """
        write("pl/" + path, pl_board_page(title, path, body))

    modes = [
        trade_payload("The Premier", "trade-premier.html", "Uses The Premier ranks - 25 published 2026/27 pro lists.", premier),
        trade_payload("The Pitch", "trade-pitch.html", "Uses The Pitch overall ranks (Sleeper BPL 2025 only).", pitch),
        trade_payload("Attack", "trade-attack.html", "Forwards only.", fwd),
        trade_payload("Midfield", "trade-midfield.html", "Midfielders only.", mid),
        trade_payload("Defence", "trade-defence.html", "Defenders only.", defence),
        trade_payload("Keepers", "trade-keepers.html", "Goalkeepers only.", gkp),
    ]
    for m in modes:
        write_trade(m)
    hub_tiles = [(m["file"], m["label"], m["blurb"]) for m in modes]
    trade_hub = f"""
    <p class="kicker">Trade Calculators</p>
    <h1>Six calculators</h1>
    <p class="note">Premier uses the 2026/27 pro-list 400. Pitch uses Sleeper. Rank 1 is 12,000. Fair is within 8%.</p>
    <div class="grid">{''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in hub_tiles)}</div>
    {faq_html(PL_TRADE_FAQ, heading="How BK Value prices a Premier League trade.")}
    """
    write("pl/trade.html", pl_board_page(
        "Trade Calculators", "trade.html", trade_hub,
        extra_jsonld=[faq_jsonld(PL_TRADE_FAQ)],
    ))

    player_urls, player_files = write_player_pages(pitch, premier, fwd, mid, defence, gkp, news_by_player)
    news_urls = render_pl_news_pages(stories)
    x_body = f"""
    <p class="kicker">The X</p>
    <h1>The X</h1>
    <p class="note">Memes from X.</p>
    {x_cards("soccer", 1, esc)}
    <p class="note" style="margin-top:16px"><a href="../the-x.html">Football The X</a> · <a href="../bb/the-x.html">Baseball The X</a></p>
    """
    write("pl/the-x.html", pl_board_page("The X", "the-x.html", x_body))
    (ROOT / "data/pl-pitch.json").write_text(json.dumps({
        "updated": UPDATED,
        "pitch": pitch,
        "premier": premier,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
    }, indent=2, default=str))
    return {
        "pitch": pitch,
        "premier": premier,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
        "files": player_files,
        "source_names": [name for name, _u, _n in PL_SOURCES],
        "urls": ["https://ballkeep.com/pl/"] + [
            "https://ballkeep.com/pl/" + p
            for p in [
                "the-premier.html", "the-pitch.html", "news.html", "the-x.html",
                "attack.html", "midfield.html",
                "defence.html", "keepers.html", "trade.html", "trade-premier.html",
                "trade-pitch.html", "trade-attack.html", "trade-midfield.html",
                "trade-defence.html", "trade-keepers.html", "players/",
            ]
        ] + news_urls[1:] + player_urls,
        "n_pitch": len(pitch),
        "n_premier": len(premier),
        "n_players": len(player_files),
        "n_news": max(0, len(news_urls) - 1),
        "news": stories,
    }
