#!/usr/bin/env python3
"""Build the PitchKeep static section under pl/."""
from __future__ import annotations

import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 20, 2026"

from pl_data import PL_SOURCES, bk_value, load_universe  # noqa: E402
from seo import canon, clip, dual_metric_graph, grafs_html, head_tags, rank_spread_graph, value_bars  # noqa: E402


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")


def write(path, doc):
    dest = ROOT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)


PL_NAV = [
    ("index.html", "Home"),
    ("the-pitch.html", "The Pitch"),
    ("attack.html", "Attack"),
    ("midfield.html", "Midfield"),
    ("defence.html", "Defence"),
    ("keepers.html", "Keepers"),
    ("trade.html", "Trade"),
    ("players/index.html", "Players"),
]


def wordmark():
    return '<span class="word-pitch">PITCH</span><span class="word-keep">KEEP</span>'


def sport_footer(depth=1):
    prefix = "../" * depth
    return (
        f'<div>'
        f'<a class="sport-switch fb" href="{prefix}index.html">Ball Keep Football</a>'
        f'<a class="sport-switch bb" href="{prefix}bb/index.html">BaseBallKeep</a>'
        f"</div>"
    )


PL_SEO = {
    "index.html": (
        "PitchKeep | Premier League Rankings on Sleeper BPL 2025 Points",
        "Purple-and-pitch desk for the Premier League. The Pitch top 400 is default Sleeper soccer scoring on 2025/26 counting stats. Haaland is #1, Bruno #2.",
        "img/pl-hero.jpg",
    ),
    "the-pitch.html": (
        "The Pitch — Sleeper BPL 2025 Premier League Rankings (Top 400) | PitchKeep",
        "Overall Premier League top 400 ranked on Sleeper BPL 2025 points. FWD/MID goals 9, DEF/GKP 10, assists 6/7. Erling Haaland leads at 317.2.",
        "img/pl-logo.jpg",
    ),
    "attack.html": (
        "Premier League Forward Rankings — Sleeper BPL 2025 | PitchKeep",
        "FPL forwards re-ranked on Sleeper BPL 2025 points. Haaland is the tax. Igor Thiago and João Pedro are the volume argument.",
        "img/pl-logo.jpg",
    ),
    "midfield.html": (
        "Premier League Midfielder Rankings — Sleeper BPL 2025 | PitchKeep",
        "Sleeper pays assists. Bruno Fernandes, Antoine Semenyo, Declan Rice — The Pitch midfield 150.",
        "img/pl-logo.jpg",
    ),
    "defence.html": (
        "Premier League Defender Rankings — Sleeper BPL 2025 | PitchKeep",
        "Clean sheets are 6 points and goals against are −2. Gabriel Magalhães outscores half the midfield on this table.",
        "img/pl-logo.jpg",
    ),
    "keepers.html": (
        "Premier League Goalkeeper Rankings — Sleeper BPL 2025 | PitchKeep",
        "Saves at 2 and clean sheets at 8. Kelleher, Raya, and Donnarumma is the real fight.",
        "img/pl-logo.jpg",
    ),
    "trade.html": (
        "Premier League Fantasy Trade Calculator | PitchKeep",
        "Pitch, Attack, Midfield, Defence, Keepers. Rank becomes BK Value. Fair is within 8%.",
        "img/pl-logo.jpg",
    ),
    "players/index.html": (
        "Premier League Player Files — Sleeper BPL 2025 | PitchKeep",
        "Every Pitch 400 name: Sleeper points, 2025/26 line, every board, tape.",
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


def pl_page(title, path, body, extra_js="", depth=1, description=None, image=None, doc_title=None):
    prefix = "../" * depth
    links = []
    for href, label in PL_NAV:
        cur = ' aria-current="page"' if href == path else ""
        if depth == 2:
            target = href if href.startswith("players/") else "../" + href
            if href.startswith("players/") and path.startswith("players/"):
                target = href[len("players/") :]
        else:
            target = href
        links.append(f'<a href="{esc(target)}"{cur}>{esc(label)}</a>')
    packed = PL_SEO.get(path)
    full_title = doc_title or (packed[0] if packed else f"{title} | PitchKeep")
    desc = description or (packed[1] if packed else f"{title} on PitchKeep. Premier League rankings on Sleeper BPL 2025 points. Updated {UPDATED}.")
    img = image or (packed[2] if packed else "img/pl-logo.jpg")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path, "pl/"), image=img, brand="PitchKeep")}
  <link rel="stylesheet" href="{prefix}css/pl.css" />
  <link rel="icon" href="{prefix}img/pl-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/pl-logo.jpg" alt="PitchKeep circular soccer logo" />
        <div>
          <p class="brand-title">{wordmark()}</p>
          <p>Premier League · FPL · The Pitch</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {body}
    <footer>
      © {date.today().year} PitchKeep · ballkeep.com/pl · Rankings aggregated {UPDATED}. Not affiliated with the Premier League or FPL.
      {sport_footer(depth)}
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
    elif label == "£":
        cls = "c-price"
    elif label not in ("PK", "Player", "Pos", "Club"):
        cls = "desk-only"
    attr = f' class="{cls}"' if cls else ""
    return f"<th{attr}>{esc(label)}</th>"


def rank_table(rows, extra_headers=None, extra_cells=None, player_prefix=""):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    head = "".join(_rank_th(h) for h in ["PK", "Player", "Pos", "Club"] + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        price = r.get("price")
        slug = slugify(r["name"])
        href = f"{player_prefix}players/{slug}.html"
        price_bit = f" · £{price}" if price not in (None, "") else ""
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}{esc(price_bit)}</div>"
        )
        body.append(
            f'<tr data-pos="{esc(pos)}" data-group="{esc(r.get("group") or pos)}">'
            f'<td class="rk c-rank">{r.get("bk","")}</td>'
            f'<td class="c-name"><a class="player-link" href="{esc(href)}"><strong>{esc(r["name"])}</strong></a>{meta}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f"{extra_cells(r)}</tr>"
        )
    return (
        f'<div class="table-wrap"><table class="rank-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def val_cell(r):
    return (
        f'<td class="desk-only">{r.get("sleeper_pts") if r.get("sleeper_pts") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("pts") if r.get("pts") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("gls") if r.get("gls") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("ast") if r.get("ast") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("minutes") if r.get("minutes") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("cs") if r.get("cs") not in (None, "") else "—"}</td>'
        f'<td class="desk-only">{r.get("tackles") if r.get("tackles") not in (None, "") else "—"}</td>'
        f'<td class="c-price">£{r.get("price") or "—"}</td>'
        f'<td class="c-val val">{int(r.get("value") or 0):,}</td>'
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


def sources_panel():
    items = []
    for name, url, note in PL_SOURCES:
        label = f'<a href="{esc(url)}">{esc(name)}</a>' if url else esc(name)
        items.append(f"<li>{label} — {esc(note)}</li>")
    return (
        '<section class="panel sources-box"><p class="kicker">Sources</p>'
        "<h3>Sleeper BPL 2025 is The Pitch. Extra boards sit on the player file. Unranked is skipped, never 999.</h3>"
        f"<ol>{''.join(items)}</ol></section>"
    )


def load_pl_media():
    path = ROOT / "data/pl-media.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def nz(v, dash="—"):
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
    if r.get("sel") not in (None, ""):
        items.append(("Owned", f"{r['sel']}%"))
    if r.get("sel_rank"):
        items.append(("Sel. rank", f"#{r['sel_rank']}"))
    if r.get("avg") is not None:
        items.append(("Pitch avg", r["avg"]))
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
        r.get("starts") if r.get("starts") not in (None, "") else "—",
        r.get("minutes") if r.get("minutes") not in (None, "") else "—",
        r.get("gls") if r.get("gls") not in (None, "") else "—",
        r.get("ast") if r.get("ast") not in (None, "") else "—",
        r.get("xg") if r.get("xg") not in (None, "") else "—",
        r.get("xa") if r.get("xa") not in (None, "") else "—",
        r.get("cs") if r.get("cs") not in (None, "") else "—",
        r.get("gc") if r.get("gc") not in (None, "") else "—",
        r.get("bonus") if r.get("bonus") not in (None, "") else "—",
        r.get("yc") if r.get("yc") not in (None, "") else "—",
        r.get("sleeper_pts") if r.get("sleeper_pts") not in (None, "") else "—",
        r.get("pts") if r.get("pts") not in (None, "") else "—",
    ]
    if r.get("pos") == "GKP":
        cells[8] = r.get("saves") if r.get("saves") not in (None, "") else "—"
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
        f"<p>{' — '.join(bits)}</p></section>"
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


def neighbors(pitch, idx):
    window = pitch[max(0, idx - 2) : idx] + pitch[idx + 1 : idx + 3]
    if not window:
        return ""
    links = " · ".join(
        f'<a class="player-link" href="{slugify(p["name"])}.html">{esc(p["name"])}</a> '
        f'(#{p["bk"]})'
        for p in window
    )
    return f'<p class="note" style="margin-top:18px"><strong>On The Pitch nearby</strong> — {links}</p>'


def same_pos(pitch, r, limit=6):
    pos = r.get("pos") or ""
    others = [p for p in pitch if p["key"] != r["key"] and p.get("pos") == pos][:limit]
    if not others:
        return ""
    links = " · ".join(
        f'<a class="player-link" href="{slugify(p["name"])}.html">{esc(p["name"])}</a> #{p["bk"]}'
        for p in others
    )
    return f'<p class="note"><strong>Same position on the 400</strong> — {links}</p>'


def video_block(media, name):
    yt = (media or {}).get("youtube_id") or ""
    if not yt:
        return (
            '<p class="note">Tape is still being matched. Refresh this file with The Pitch — '
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
    sel = r.get("sel")
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
        plus.append(f"{gls} G on {xg} xG — finishing ran cold.")
    if xg and gls is not None and gls - xg >= 4:
        minus.append(f"{gls} G on {xg} xG — finishing ran hot.")
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
    if sel not in (None, ""):
        bits.append(f"{sel}% owned")
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
    grafs = [graf] if graf else []
    if r.get("sleeper_pts") not in (None, "", 0, 0.0) and r.get("pts"):
        grafs.append(
            f"Sleeper BPL 2025 scores this {r.get('pos') or 'player'} at {r['sleeper_pts']} "
            f"on 2025/26 counting stats; official FPL had {r['pts']}."
        )
    return plus[:4], minus[:4], grafs


def list_cards(lists, r):
    items = [
        ("The Pitch", lists.get("The Pitch"), r.get("value")),
        ("Attack", lists.get("Attack"), None),
        ("Midfield", lists.get("Midfield"), None),
        ("Defence", lists.get("Defence"), None),
        ("Keepers", lists.get("Keepers"), None),
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


def write_player_pages(pitch, fwd, mid, defence, gkp):
    fm = {r["key"]: r for r in fwd}
    mm = {r["key"]: r for r in mid}
    dm = {r["key"]: r for r in defence}
    gm = {r["key"]: r for r in gkp}
    media_all = load_pl_media()
    cards, urls, files = [], [], []
    used_slugs = set()
    keep_html = {"index.html"}
    for i, r in enumerate(pitch):
        slug = slugify(r["name"])
        if slug in used_slugs:
            slug = slugify(f"{r['name']}-{r.get('team') or r['key']}")
        used_slugs.add(slug)
        media = media_all.get(r["key"]) or media_all.get(slug) or {}
        lists = {"The Pitch": r["bk"]}
        if r["key"] in fm:
            lists["Attack"] = fm[r["key"]]["bk"]
        if r["key"] in mm:
            lists["Midfield"] = mm[r["key"]]["bk"]
        if r["key"] in dm:
            lists["Defence"] = dm[r["key"]]["bk"]
        if r["key"] in gm:
            lists["Keepers"] = gm[r["key"]]["bk"]
        plus, minus, grafs = pl_grafs(r, lists, media)
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
        seo_title = f"{r['name']} PitchKeep Rank #{r['bk']} ({r.get('pos') or ''} {r.get('team') or ''})".strip()
        seo_desc = clip(
            f"{r['name']} is PitchKeep #{r['bk']} on Sleeper BPL 2025 points "
            f"({r.get('sleeper_pts') or '—'} pts, {r.get('gls') or 0}G {r.get('ast') or 0}A). "
            f"{r.get('pos') or ''} {r.get('team_name') or r.get('team') or ''}. Updated {UPDATED}."
        )
        body = f"""
    <p class="kicker">Player File · {esc(r.get("pos") or "")} {esc(r.get("team") or "")}</p>
    <div class="player-hero">
      <img src="{esc(img_src)}" alt="{esc(r['name'])}" />
      <div>
        <h1>{esc(r["name"])}</h1>
        <p class="note">{esc(bio)}</p>
      </div>
    </div>
    {facts_table(r, media)}
    {season_box(r)}
    {news_flag(r)}
    {list_cards(lists, r)}
    {grafs_html("The 2025/26 line", grafs, 2)}
    {plusminus_html(plus, minus)}
    {dual_metric_graph([
        ("Sleeper BPL", "#e8c547", r.get("sleeper_pts") or 0),
        ("FPL points", "#00c853", r.get("pts") or 0),
    ], "Sleeper vs FPL")}
    {rank_spread_graph(r.get("ranks") or {}, fill="#e8c547", kicker="Board graph")}
    {video_block(media, r["name"])}
    {boards_table(r.get("ranks") or {})}
    {neighbors(pitch, i)}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-pitch.html">The Pitch</a> · <a href="../trade.html">Calculator</a></p>
    """
        write(
            f"pl/players/{slug}.html",
            pl_page(
                r["name"],
                f"players/{slug}.html",
                body,
                depth=2,
                doc_title=seo_title,
                description=seo_desc,
                image=img,
            ),
        )
        keep_html.add(f"{slug}.html")
        cards.append(
            f'<a class="tile player-card" href="{slug}.html" data-pos="{esc(r.get("pos") or "")}" data-group="{esc(r.get("group") or "")}">'
            f'<img src="../../{esc(img)}" alt="" />'
            f'<h3>{esc(r["name"])}</h3>'
            f'<p>{esc(r.get("pos") or "")} {esc(r.get("team") or "")} · Pitch #{r["bk"]}</p></a>'
        )
        urls.append(f"https://ballkeep.com/pl/players/{slug}.html")
        files.append({
            "key": r["key"],
            "slug": slug,
            "name": r["name"],
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
            "value": r.get("value"),
            "bk": r["bk"],
            "keep_avg": r.get("avg"),
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
    <p class="kicker">Player Files</p>
    <h1>The Pitch, one name at a time</h1>
    <p class="note">The Pitch top 400. Sleeper BPL 2025 points, 2025/26 line, every board, tape. Filter the grid.</p>
    {flt}
    <div class="player-grid" id="pl-cards">{''.join(cards)}</div>
    """
    hub_js = js.replace("tbody tr", "#pl-cards .tile")
    write("pl/players/index.html", pl_page("Players", "players/index.html", hub, hub_js, depth=2))
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
        "picks": [],
    }


def write_trade(payload):
    body = f"""
    <p class="kicker">Trade Calculator</p>
    <h1>{esc(payload["label"])}</h1>
    <p class="note">{esc(payload["blurb"])} Fair is within 8%. Same BK Value curve: rank 1 = 12,000.</p>
    <p class="filters">
      <a href="trade.html">All</a>
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


def write_pitch_site():
    u = load_universe()
    pitch, fwd, mid, defence, gkp = u["pitch"], u["fwd"], u["mid"], u["def"], u["gkp"]

    tiles = [
        ("the-pitch.html", "The Pitch", "Premier League top 400. Ranked on Sleeper BPL 2025 points."),
        ("attack.html", "Attack", "Forwards only, re-ranked on Sleeper BPL points."),
        ("midfield.html", "Midfield", "The engine room. Bruno, Semenyo, Rice, still Sleeper-scored."),
        ("defence.html", "Defence", "Clean sheets pay on Sleeper. Gabriel lives here."),
        ("keepers.html", "Keepers", "Saves plus the clean-sheet tax."),
        ("trade.html", "Trade Calculators", "Pitch, Attack, Midfield, Defence, Keepers."),
        ("players/index.html", "Player Files", "400 faces, 2025/26 line, Sleeper points, tape."),
    ]
    home = f"""
    <section class="hero" style="background-image:url('../img/pl-hero.jpg')">
      <div class="hero-card">
        <p class="kicker" style="color:#e8c547">Updated {UPDATED}</p>
        <h1>{wordmark()}</h1>
        <p>A purple-and-pitch desk for the Premier League. The Pitch is Sleeper BPL 2025 points. Football and baseball still next door.</p>
      </div>
    </section>
    <section class="panel">
      <p class="kicker">What This Desk Is</p>
      <h2>Rank the shirts the way Sleeper scored them last year.</h2>
      <p class="note"><strong>Sleeper BPL</strong> is draft fantasy, not the £100m FPL app. Default scoring pays 9 for a forward/midfielder goal, 10 for a defender/keeper goal, 6/7 for an assist, 8 for a keeper clean sheet, 2 a save, and real defensive events. We ran that table across every 2025/26 Premier League counting line in the official FPL dump. That ranking <em>is</em> The Pitch — 400 names, not a 24-board FPL mash.</p>
      <p class="note">FPL price, ownership, ICT, xGI, and the short expert tapes still sit on every player file so you can see where Sleeper and the official game disagree. Unranked sources are skipped, never treated as 999. BK Value uses Pitch rank on the same curve as football (12,000 at 1.01).</p>
    </section>
    <p class="note" style="margin-top:18px"><img src="../img/pl-stitch.jpg" alt="Soccer ball on wet Premier League grass" style="width:100%;border-radius:16px" /></p>
    <div class="grid-3" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    """
    write("pl/index.html", pl_page("Home", "index.html", home))

    flt, js = filter_js(["FWD", "MID", "DEF", "GKP"])
    pitch_body = f"""
    <p class="kicker">Keystone · Sleeper BPL 2025</p>
    <h1>The Pitch</h1>
    <p class="note">Top 400, rebuilt {UPDATED}. Order is default Sleeper soccer scoring on 2025/26 Premier League counting stats — goals, assists, clean sheets, goals against, cards, saves, penalties, tackles, and a CBI blend. That is a different sport than official FPL points: Haaland's 27 goals pay, Bruno's 24 assists pay, and keepers are real because saves and clean sheets stack. BK Value uses this rank on the same curve as football (12,000 at 1.01).</p>
    {value_bars(pitch, 12, "#e8c547", "Sleeper points graph", key="sleeper_pts", heading="Sleeper BPL 2025, top 12", note="Default Sleeper soccer scoring on 2025/26 counting stats. Haaland is 317.2. Bruno is 293.8.")}
    {value_bars(pitch, 12, "#00c853", "Pitch value graph")}
    <section class="panel">
      <p class="kicker">Sleeper default table</p>
      <h3>What last year's box score is worth here</h3>
      <p class="note">FWD/MID goal 9, DEF/GKP goal 10. Assist 6 / 7. Clean sheet 0 / 1 / 6 / 8. Save 2. Yellow −2, red −7, own goal −5, missed penalty −4. DEF/GKP goals against −2. Tackles 1. FPL CBI × 0.4. Shots on target and key passes are not in the public FPL dump, so they are omitted rather than guessed.</p>
    </section>
    {flt}
    <div class="panel">{rank_table(pitch, ["Sleeper", "FPL", "G", "A", "Min", "CS", "Tck", "£", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
    write("pl/the-pitch.html", pl_page("The Pitch", "the-pitch.html", pitch_body, js))

    for path, title, kicker, note, rows in [
        ("attack.html", "Attack", "Forwards", "No. 9s only, re-ranked on Sleeper BPL 2025. Haaland is the tax. Igor Thiago and João Pedro are the volume argument.", fwd),
        ("midfield.html", "Midfield", "The Engine Room", "Sleeper pays assists. Bruno, Semenyo, Rice, Gibbs-White — this is the 150.", mid),
        ("defence.html", "Defence", "The Back Line", "Clean sheets are 6 points and goals against are −2. Gabriel outscores half the midfield on this table.", defence),
        ("keepers.html", "Keepers", "Between the Sticks", "Saves at 2 and clean sheets at 8. Kelleher / Raya / Donnarumma is the real fight.", gkp),
    ]:
        body = f"""
    <p class="kicker">{esc(kicker)}</p>
    <h1>{esc(title)}</h1>
    <p class="note">{esc(note)}</p>
    {value_bars(rows, 12, "#e8c547", f"{title} points graph", key="sleeper_pts", heading=f"Sleeper BPL 2025 {title.lower()}, top 12", note="Same Sleeper table as The Pitch, this position only.")}
    {value_bars(rows, 12, "#00c853", f"{title} value graph")}
    <div class="panel">{rank_table(rows, ["Sleeper", "FPL", "G", "A", "Min", "CS", "Tck", "£", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
        write("pl/" + path, pl_page(title, path, body))

    modes = [
        trade_payload("The Pitch", "trade-pitch.html", "Uses The Pitch overall ranks.", pitch),
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
    <h1>Five Calculators, One Curve</h1>
    <p class="note">Rank becomes BK Value the same way it does on the football desk. Rank 1 is 12,000. Fair is within 8%.</p>
    <div class="grid">{''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in hub_tiles)}</div>
    """
    write("pl/trade.html", pl_page("Trade Calculators", "trade.html", trade_hub))

    player_urls, player_files = write_player_pages(pitch, fwd, mid, defence, gkp)
    (ROOT / "data/pl-pitch.json").write_text(json.dumps({
        "updated": UPDATED,
        "pitch": pitch,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
    }, indent=2, default=str))
    return {
        "pitch": pitch,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
        "files": player_files,
        "source_names": [name for name, _u, _n in PL_SOURCES],
        "urls": ["https://ballkeep.com/pl/"] + [
            "https://ballkeep.com/pl/" + p
            for p in [
                "the-pitch.html", "attack.html", "midfield.html", "defence.html",
                "keepers.html", "trade.html", "trade-pitch.html", "trade-attack.html",
                "trade-midfield.html", "trade-defence.html", "trade-keepers.html", "players/",
            ]
        ] + player_urls,
        "n_pitch": len(pitch),
        "n_players": len(pitch),
    }
