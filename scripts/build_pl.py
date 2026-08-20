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


def pl_page(title, path, body, extra_js="", depth=1):
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
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{esc(title)} — PitchKeep</title>
  <meta name="description" content="PitchKeep Premier League rankings. The Pitch top 250, super-aggregated FPL boards, player files with tape." />
  <link rel="stylesheet" href="{prefix}css/pl.css" />
  <link rel="icon" href="{prefix}img/pl-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/pl-logo.jpg" alt="PitchKeep circular soccer logo" />
        <div>
          <h1>{wordmark()}</h1>
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


def rank_table(rows, extra_headers=None, extra_cells=None, player_prefix=""):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    head = "".join(f"<th>{esc(h)}</th>" for h in ["PK", "Player", "Pos", "Club"] + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        slug = slugify(r["name"])
        href = f"{player_prefix}players/{slug}.html"
        body.append(
            f'<tr data-pos="{esc(pos)}" data-group="{esc(r.get("group") or pos)}">'
            f'<td class="rk">{r.get("bk","")}</td>'
            f'<td><a class="player-link" href="{esc(href)}"><strong>{esc(r["name"])}</strong></a></td>'
            f'<td><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td>{esc(r.get("team") or "")}</td>'
            f"{extra_cells(r)}</tr>"
        )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def val_cell(r):
    return (
        f'<td>{r.get("avg")}</td><td>{r.get("n")}</td>'
        f'<td>£{r.get("price") or "—"}</td>'
        f'<td class="val">{int(r.get("value") or 0):,}</td>'
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
        "<h3>Twenty-four boards. Unranked is skipped, never 999.</h3>"
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


def facts_table(r, media):
    items = []
    if r.get("number") or media.get("number"):
        items.append(("No.", f"#{r.get('number') or media.get('number')}"))
    if r.get("pos"):
        items.append(("Pos", r["pos"]))
    if r.get("team_name") or r.get("team"):
        items.append(("Club", r.get("team_name") or r.get("team")))
    if r.get("age"):
        items.append(("Age", r["age"]))
    if r.get("price"):
        items.append(("FPL £", f"£{r['price']}m"))
    if r.get("sel") not in (None, ""):
        items.append(("Owned", f"{r['sel']}%"))
    if r.get("pts") not in (None, ""):
        items.append(("25/26 pts", r["pts"]))
    if r.get("ict") not in (None, ""):
        items.append(("ICT", r["ict"]))
    if r.get("xgi") not in (None, ""):
        items.append(("xGI", r["xgi"]))
    if r.get("birth"):
        items.append(("Born", str(r["birth"])[:10]))
    if r.get("pens") == 1:
        items.append(("Pens", "1st choice"))
    if not items:
        return ""
    cells = "".join(
        f'<div class="fact"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in items
    )
    return f'<div class="facts">{cells}</div>'


def stat_pills(r):
    pills = [
        ("Pts", r.get("pts")),
        ("G", r.get("gls")),
        ("A", r.get("ast")),
        ("Min", r.get("minutes")),
        ("CS", r.get("cs")),
        ("Saves", r.get("saves") if r.get("pos") == "GKP" else None),
        ("xGI", r.get("xgi")),
        ("Form", r.get("form")),
        ("EP", r.get("ep")),
    ]
    pills = [(k, v) for k, v in pills if v not in (None, "", 0, "0", 0.0)]
    if not pills:
        return ""
    cells = "".join(
        f'<div class="stat-pill"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in pills[:8]
    )
    return f'<div class="stat-strip">{cells}</div>'


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
        f'<table class="boards"><thead><tr><th>Source</th><th>Rank</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></section>"
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
    return f'<p class="note"><strong>Same position on the 250</strong> — {links}</p>'


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
    <p class="note">Best available public clip. Not affiliated with the Premier League, the club, or the posting channel.</p>
    <div class="video-wrap">
      <iframe src="https://www.youtube-nocookie.com/embed/{esc(yt)}" title="{esc(title)}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen loading="lazy"></iframe>
    </div>
    """


def pl_grafs(r, lists, media):
    name = r["name"]
    pos = r.get("pos") or ""
    team = r.get("team_name") or r.get("team") or "his club"
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
    xgi = r.get("xgi") or 0
    ict = r.get("ict") or 0
    age = r.get("age") or ""
    news = (r.get("news") or "").strip()
    pens = r.get("pens") == 1
    value = int(r.get("value") or 0)
    hi = min(ranks.values()) if ranks else None
    lo = max(ranks.values()) if ranks else None

    role = {
        "FWD": "a centre-forward you captain when the fixtures smile",
        "MID": "a midfielder who scores FPL points from the middle of the pitch, not just the box",
        "DEF": "a defender in the new FPL world where attacking full-backs and set-piece centre-halves print",
        "GKP": "a goalkeeper whose clean sheets and save points still decide mini-leagues",
    }.get(pos, "a Premier League name")

    g1 = (
        f"{name} is #{keep} on PitchKeep's The Pitch — a 24-source Premier League super-aggregate "
        f"built for 2026/27 FPL and for anyone who still argues about who actually belongs in a "
        f"season-long XI. He is {role} at {team}. The number is not a vibe. It is the average of "
        f"every board that ranked him ({n} of 24), led by official FPL 2025/26 points, 2026/27 price, "
        f"Gameweek 1 ownership, ICT, xGI, and the August expert tapes from Premier League Scout, "
        f"Fantasy Football Fix, Yahoo, and the rest of the public desk. Unranked sources are skipped. "
        f"We do not invent a 999 to punish a name the Athletic did not print."
    )
    g2 = (
        f"Last season's counting stats are the floor: {pts} FPL points, {gls} goals, {ast} assists, "
        f"{minutes} minutes, ICT {ict}, xGI {xgi}. That is the 2025/26 tape, not a projection dressed "
        f"up as a memory. The 2026/27 market then reprices him at £{price}m with {sel}% ownership "
        f"into the Friday 18:30 BST Gameweek 1 deadline. If those two stories diverge — cheap with "
        f"a monster year, or expensive off a quiet one — The Pitch is the place the split shows up "
        f"as a rank instead of a tweet. BK Value on this slot is {value:,}, the same decaying curve "
        f"as football and baseball: 12,000 at 1.01, a late-board name a fraction of that."
    )
    spread = (
        f"High {hi}, low {lo} — that gap is the argument."
        if hi is not None
        else "Short tape this week."
    )
    g3 = (
        f"The 24-board average is {avg}. {spread} Premium desks (price, Hub, Sky) stuff the "
        f"£9m+ names because FPL is a constrained budget game and those shirts are the ones "
        f"everyone else already owns. Value desks (Scout lean, Faithful gems, Yahoo enablers) "
        f"try to find the £4.5m–£6.5m minutes that let you afford Haaland and Bruno in the same "
        f"XI. If {name} is climbing one of those and falling off the other, you are not confused. "
        f"You are looking at two sports that happen to share a fixture list."
    )
    age_bit = f" He is {age}, which still matters when the World Cup summer just emptied the legs." if age else ""
    pens_bit = (
        " First-choice penalties are a ranking event of their own — one spot on the order list is worth "
        "a midfielder's worth of projected returns."
        if pens
        else ""
    )
    news_bit = (
        f" The FPL news line right now: {news} That is a minutes flag, not a character study."
        if news
        else " No injury flag on the FPL ticker this morning, which is the whole scouting report until Saturday."
    )
    g4 = (
        f"The Pitch is not FIFA overall and it is not a beauty contest.{age_bit}{pens_bit} "
        f"It is who you would actually pick in a 15-man FPL squad and who you would actually keep "
        f"in a season-long draft if the £100m cap vanished. Those two games disagree at the edges — "
        f"draft loves 180-point midfielders even at £8m; classic FPL sometimes prefers the £5.5m "
        f"enabler so the rest of the money can sit on Haaland's shoulders. {news_bit}"
    )
    g5 = (
        f"Watch the clip. Then look at the board dump. If the film is a 1.01 and The Pitch has him "
        f"in the thirties, somebody is late or you are early. Refresh this file with the next "
        f"Gameweek. Flags fly forever; FPL ranks do not. We will rebuild The Pitch the same way "
        f"we rebuild The Keep: more boards when they exist, honest about compiled expert slices, "
        f"and never pretending a podcast XI is a 250-man sheet."
    )
    plus, minus = [], []
    if keep and keep <= 10:
        plus.append(f"Pitch #{keep} — template capital. You do not need a hot take to start him.")
    elif keep and keep <= 40:
        plus.append(f"Pitch #{keep} is still a core 250 name, not a bench dart.")
    if n >= 18:
        plus.append(f"On {n} boards. That is a consensus shirt, not a one-list meme.")
    if sel and sel >= 30:
        plus.append(f"{sel}% owned. The template already voted.")
    if pts >= 160:
        plus.append(f"{pts} FPL points last season. The floor is real.")
    if price and price <= 6.5 and (pts or 0) >= 120:
        plus.append(f"£{price}m after a {pts}-point year — this is how mini-leagues get broken.")
    if pens:
        plus.append("Pens. The rank should already have that baked in; if a rival does not, take it.")
    if age and int(age) <= 24:
        plus.append(f"Age {age}. The next three FPL seasons still like him.")
    if keep and keep >= 180:
        minus.append(f"Pitch #{keep} is the deep end of the 250. Streamer / bench / draft-only.")
    if news:
        minus.append("FPL has a news flag. Minutes first, points later.")
    if sel and sel >= 50 and keep and keep >= 15:
        minus.append(f"{sel}% owned and Pitch #{keep} — the public may be ahead of the aggregate, or trapped.")
    if price and price >= 10:
        minus.append(f"£{price}m is a structural cost. You are paying two mid-board names to own him.")
    if ranks and hi and lo and (lo - hi) >= 40:
        minus.append(f"Spread {hi}–{lo}. You are picking a camp, not a unanimous board.")
    if not plus:
        plus.append(f"{pos} {r.get('team')} sits on The Pitch at #{keep}.")
    if not minus:
        minus.append("The rank is the comment until the next international break.")
    return plus[:7], minus[:7], [g1, g2, g3, g4, g5]


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
        chips = [
            f'<span class="chip">Pitch #{r["bk"]}</span>',
            f'<span class="chip">BK {int(r.get("value") or 0):,}</span>',
            f'<span class="chip">£{r.get("price") or "—"}m</span>',
        ]
        if r.get("age"):
            chips.append(f'<span class="chip">Age {esc(r["age"])}</span>')
        if r.get("sel") not in (None, ""):
            chips.append(f'<span class="chip">{r["sel"]}% owned</span>')
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
        body = f"""
    <p class="kicker">Player File · {esc(r.get("pos") or "")} {esc(r.get("team") or "")}</p>
    <div class="player-hero">
      <img src="{esc(img_src)}" alt="{esc(r['name'])}" />
      <div>
        <h2>{esc(r["name"])}</h2>
        <p class="note">{esc(bio)}</p>
        <div class="chips">{''.join(chips)}</div>
      </div>
    </div>
    {facts_table(r, media)}
    {stat_pills(r)}
    {list_cards(lists, r)}
    <div class="plusminus">
      <div class="pm"><h3>Plus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in plus)}</ul></div>
      <div class="pm"><h3>Minus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in minus)}</ul></div>
    </div>
    <section class="panel analysis">
      <p class="kicker">PitchKeep Take</p>
      {''.join(f'<p>{esc(g)}</p>' for g in grafs)}
    </section>
    {video_block(media, r["name"])}
    {boards_table(r.get("ranks") or {})}
    {neighbors(pitch, i)}
    {same_pos(pitch, r)}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-pitch.html">The Pitch</a> · <a href="../trade.html">Calculator</a></p>
    """
        write(f"pl/players/{slug}.html", pl_page(r["name"], f"players/{slug}.html", body, depth=2))
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
            "gls": r.get("gls"),
            "ast": r.get("ast"),
        })
    flt, js = filter_js(["FWD", "MID", "DEF", "GKP"])
    hub = f"""
    <p class="kicker">Player Files</p>
    <h2>The Pitch, one name at a time</h2>
    <p class="note">Every name in the Premier League Pitch top 250. Headshot, 2025/26 line, long take, every board, tape, BK Value. Filter the grid. Click a face.</p>
    {flt}
    <div class="player-grid" id="pl-cards">{''.join(cards)}</div>
    """
    hub_js = js.replace("tbody tr", "#pl-cards .tile")
    write("pl/players/index.html", pl_page("Players", "players/index.html", hub, hub_js, depth=2))
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
    <h2>{esc(payload["label"])}</h2>
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
        ("the-pitch.html", "The Pitch", "Premier League top 250. 24-board FPL super-aggregate."),
        ("attack.html", "Attack", "Forwards only, re-ranked among the No. 9s."),
        ("midfield.html", "Midfield", "The FPL engine room. Saka, Bruno, Semenyo."),
        ("defence.html", "Defence", "Clean sheets plus the new attacking CB."),
        ("keepers.html", "Keepers", "The £4.5m question and the Raya tax."),
        ("trade.html", "Trade Calculators", "Pitch, Attack, Midfield, Defence, Keepers."),
        ("players/index.html", "Player Files", "250 faces, long takes, tape."),
    ]
    home = f"""
    <section class="hero" style="background-image:url('../img/pl-hero.jpg')">
      <div class="hero-card">
        <p class="kicker" style="color:#e8c547">Updated {UPDATED}</p>
        <h2>{wordmark()}</h2>
        <p>A purple-and-pitch desk for the Premier League. Twenty-four FPL boards. One Pitch. Football and baseball still next door.</p>
      </div>
    </section>
    <section class="panel">
      <p class="kicker">What This Desk Is</p>
      <h2>Pick the shirts that still score in May.</h2>
      <p class="note"><strong>Fantasy Premier League</strong> is a £100m squad, a Friday deadline, and a captain you live with for 38 Gameweeks. <strong>Season-long / draft FPL</strong> is the same league without the price cap — last year's 180-point midfielder is a first-rounder even if he costs £8m in the official game.</p>
      <p class="note">The Pitch is an overall Premier League top 250 aggregated from 24 public boards, led by official FPL 2025/26 points, 2026/27 prices, Gameweek 1 ownership, ICT and xGI, then compiled expert slices from Premier League Scout, Fantasy Football Fix, Yahoo, Football Faithful, and the usual content desks. Bruno and Haaland are the argument at the top. The rest of the 250 is who you actually own.</p>
    </section>
    <p class="note" style="margin-top:18px"><img src="../img/pl-stitch.jpg" alt="Soccer ball on wet Premier League grass" style="width:100%;border-radius:16px" /></p>
    <div class="grid-3" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    """
    write("pl/index.html", pl_page("Home", "index.html", home))

    flt, js = filter_js(["FWD", "MID", "DEF", "GKP"])
    pitch_body = f"""
    <p class="kicker">Keystone · Premier League</p>
    <h2>The Pitch</h2>
    <p class="note">Top 250 for 2026/27 FPL and season-long drafts, rebuilt {UPDATED}. PitchKeep rank is the average of every source that ranked the player — 24 boards, five of them the entire FPL universe. BK Value uses the same decaying curve as football (12,000 at 1.01). Gameweek 1 deadline: Friday 21 August, 18:30 BST.</p>
    {flt}
    <div class="panel">{rank_table(pitch, ["Avg", "# Boards", "£", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
    write("pl/the-pitch.html", pl_page("The Pitch", "the-pitch.html", pitch_body, js))

    for path, title, kicker, note, rows in [
        ("attack.html", "Attack", "Forwards", "No. 9s only. Haaland is the tax. João Pedro is the template argument.", fwd),
        ("midfield.html", "Midfield", "The Engine Room", "FPL is won in midfield. Bruno, Semenyo, Saka, Rice, Szoboszlai.", mid),
        ("defence.html", "Defence", "The Back Line", "Clean sheets, plus the new FPL world where Gabriel outscores half the midfield.", defence),
        ("keepers.html", "Keepers", "Between the Sticks", "Raya money versus Kinsky money. That is the whole page.", gkp),
    ]:
        body = f"""
    <p class="kicker">{esc(kicker)}</p>
    <h2>{esc(title)}</h2>
    <p class="note">{esc(note)}</p>
    <div class="panel">{rank_table(rows, ["Avg", "# Boards", "£", "BK Value"], val_cell)}</div>
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
    <h2>Five Calculators, One Curve</h2>
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
