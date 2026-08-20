#!/usr/bin/env python3
"""Build the BaseBallKeep static section under bb/."""
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
UPDATED = "August 20, 2026"
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


BB_NAV = [
    ("index.html", "Home"),
    ("the-keep.html", "The Keep"),
    ("news.html", "News"),
    ("the-lineup.html", "The Lineup"),
    ("pitchers.html", "BK's Pitchers"),
    ("bullpen.html", "Bullpen SV"),
    ("bullpen-holds.html", "SV + Holds"),
    ("redraft.html", "Redraft"),
    ("trade.html", "Trade"),
    ("waivers-dynasty.html", "Dynasty Wire"),
    ("waivers-redraft.html", "Redraft Wire"),
    ("players/index.html", "Players"),
]


def wordmark():
    return '<span class="word-base">BASE</span><span class="word-ball">BALL</span><span class="word-keep">KEEP</span>'


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
    return False


def bb_page(title, path, body, extra_js="", depth=1):
    prefix = "../" * depth
    links = []
    for href, label in BB_NAV:
        cur = ' aria-current="page"' if bb_nav_current(href, path) else ""
        target = bb_nav_target(href, path, depth)
        links.append(f'<a href="{esc(target)}"{cur}>{esc(label)}</a>')
    fb = f"{prefix}index.html"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{esc(title)} — BaseBallKeep</title>
  <meta name="description" content="BaseBallKeep dynasty and redraft baseball rankings, trade calculators, and waiver wires." />
  <link rel="stylesheet" href="{prefix}css/bb.css" />
  <link rel="icon" href="{prefix}img/bb-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/bb-logo.jpg" alt="BaseBallKeep circular baseball logo" />
        <div>
          <h1>{wordmark()}</h1>
          <p>Dynasty · Redraft · Diamond</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {body}
    <footer>
      © {date.today().year} BaseBallKeep · ballkeep.com/bb · Rankings aggregated {UPDATED}. Not affiliated with MLB.
      <div><a class="sport-switch fb" href="{fb}">Ball Keep Football</a></div>
    </footer>
  </div>
  {extra_js}
</body>
</html>
"""


def rank_table(rows, extra_headers=None, extra_cells=None, player_prefix=""):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    head = "".join(f"<th>{esc(h)}</th>" for h in ["BK", "Player", "Pos", "Team"] + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        pos0 = pos.split("/")[0]
        slug = slugify(r["name"])
        href = f"{player_prefix}players/{slug}.html"
        body.append(
            f'<tr data-pos="{esc(pos0)}" data-group="{esc(r.get("group") or "")}">'
            f'<td class="rk">{r.get("bk","")}</td>'
            f'<td><a class="player-link" href="{esc(href)}"><strong>{esc(r["name"])}</strong></a></td>'
            f'<td><span class="pos {esc(pos.split("/")[0])}">{esc(pos)}</span></td>'
            f'<td>{esc(r.get("team",""))}</td>'
            f"{extra_cells(r)}"
            "</tr>"
        )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


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
    return f'<td>{r["avg"]}</td><td>{r["n"]}</td><td class="val">{int(r["value"]):,}</td>'


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


def banner(src, alt=""):
    return f'<p class="bb-banner"><img src="../img/{esc(src)}" alt="{esc(alt)}" /></p>'


def bb_grafs(r, lists=None):
    lists = lists or {}
    name, pos, team = r["name"], r.get("pos") or "", r.get("team") or ""
    keep = r.get("bk")
    n = r.get("n") or 0
    age = r.get("age") or ""
    g = r.get("group") or ""
    plus, minus = [], []
    if keep and keep <= 15:
        plus.append(f"Keep #{keep} — first-round dynasty capital on a 23-board mix.")
    elif keep and keep <= 50:
        plus.append(f"Keep #{keep} — still a building-block name on the 300.")
    elif keep and keep <= 150:
        plus.append(f"Keep #{keep} on the 300. Tradable, not a 1.01.")
    if keep and keep <= 40:
        plus.append(f"Average {r.get('avg')} across {n} boards.")
    if lists.get("The Lineup") and lists["The Lineup"] <= 40:
        plus.append(f"Lineup #{lists['The Lineup']} among dynasty bats.")
    if lists.get("BK Pitchers") and lists["BK Pitchers"] <= 25:
        plus.append(f"BK's Pitchers #{lists['BK Pitchers']} — ace-room capital.")
    if lists.get("BB Redraft") and lists["BB Redraft"] + 15 < (keep or 999):
        plus.append(f"Redraft #{lists['BB Redraft']} — helping this month more than the dynasty slot says.")
    if age and age <= 24:
        plus.append(f"Age {age} — still climbing the curve.")
    if age and age >= 33:
        minus.append(f"Age {age} is a dynasty tax even when 2026 is loud.")
    if g == "RP":
        minus.append("Reliever volatility: the ninth can vanish in a week.")
    if g == "SP" and keep and keep <= 30:
        plus.append("Ace-tier innings. Pitcher injuries are the tax, not the ranking.")
    if n >= 8:
        plus.append(f"On {n} boards — not a one-list darling.")
    if keep and keep >= 200:
        minus.append(f"Keep #{keep} is the edge of the 300. Deep-league / taxi-squad more than a foundation chip.")
    if not plus:
        plus.append(f"{pos} {team} sits on The Keep at #{keep}.")
    if not minus:
        minus.append("The rank is the comment until the next IL stint.")
    lineup_bit = f" Lineup #{lists['The Lineup']}." if lists.get("The Lineup") else ""
    pit_bit = f" BK's Pitchers #{lists['BK Pitchers']}." if lists.get("BK Pitchers") else ""
    rd_bit = f" Rest-of-season redraft #{lists['BB Redraft']}." if lists.get("BB Redraft") else ""
    grafs = [
        f"{name} is #{keep} on BaseBallKeep's overall dynasty 300, a 23-source mix anchored by RotoGraphs (Aug 14) and The Dynasty Guru points list (Aug 10). {pos} for {team or 'the org'}.{lineup_bit}{pit_bit}{rd_bit}",
        f"BK Value on this rank is {int(r.get('value') or 0):,}. Same decaying curve as football: 12,000 at 1.01, a late first a fraction of that. If someone is asking for two firsts, run the calculator.",
        "Flags fly forever. We will refresh this file with The Keep. September baseball is a proving ground, not a coronation.",
    ]
    return plus[:6], minus[:6], grafs


def write_player_pages(keep, lineup, pitchers, redraft, news_by_player=None):
    news_by_player = news_by_player or {}
    lu = {r["key"]: r for r in lineup}
    pit = {r["key"]: r for r in pitchers}
    rd = {r["key"]: r for r in redraft}
    cards = []
    urls = []
    files = []
    for r in keep:
        slug = slugify(r["name"])
        lists = {"BB Keep": r["bk"]}
        if r["key"] in lu:
            lists["The Lineup"] = lu[r["key"]]["bk"]
        if r["key"] in pit:
            lists["BK Pitchers"] = pit[r["key"]]["bk"]
        if r["key"] in rd:
            lists["BB Redraft"] = rd[r["key"]]["bk"]
        plus, minus, grafs = bb_grafs(r, lists)
        chips = [f'<span class="chip">Keep #{r["bk"]}</span>']
        chips.append(f'<span class="chip">BK {int(r.get("value") or 0):,}</span>')
        if lists.get("The Lineup"):
            chips.append(f'<span class="chip">Lineup #{lists["The Lineup"]}</span>')
        if lists.get("BK Pitchers"):
            chips.append(f'<span class="chip">Pitchers #{lists["BK Pitchers"]}</span>')
        if lists.get("BB Redraft"):
            chips.append(f'<span class="chip">Redraft #{lists["BB Redraft"]}</span>')
        if r.get("age"):
            chips.append(f'<span class="chip">Age {esc(r["age"])}</span>')
        ranks = r.get("ranks") or {}
        rank_bits = ""
        if ranks:
            bits = "".join(
                f"<div><small>{esc(s)}</small> {v}</div>"
                for s, v in sorted(ranks.items(), key=lambda kv: kv[1])[:8]
            )
            rank_bits = f'<div class="note" style="margin-top:10px"><strong>Boards</strong>{bits}</div>'
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
    <p class="kicker">Player File · {esc(r.get("pos",""))} {esc(r.get("team",""))}</p>
    <div class="player-hero">
      <img src="../../img/bb-logo.jpg" alt="" />
      <div>
        <h2>{esc(r["name"])}</h2>
        <p class="note">{esc(r.get("pos",""))} · {esc(r.get("team",""))}{" · age " + esc(str(r["age"])) if r.get("age") else ""}</p>
        <div class="chips">{''.join(chips)}</div>
        {rank_bits}
      </div>
    </div>
    <div class="plusminus">
      <div class="pm"><h3>Plus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in plus)}</ul></div>
      <div class="pm"><h3>Minus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in minus)}</ul></div>
    </div>
    <section class="panel">
      <p class="kicker">BaseBallKeep Take</p>
      {''.join(f'<p>{esc(g)}</p>' for g in grafs)}
    </section>
    {news_block}
    <p class="note"><a href="index.html">All players</a> · <a href="../the-keep.html">The Keep</a> · <a href="../news.html">BK News</a> · <a href="../the-lineup.html">The Lineup</a> · <a href="../pitchers.html">Pitchers</a> · <a href="../trade.html">Calculator</a></p>
    """
        write(f"bb/players/{slug}.html", bb_page(r["name"], f"players/{slug}.html", body, depth=2))
        cards.append(
            f'<a class="tile" href="{slug}.html" data-pos="{esc((r.get("pos") or "").split("/")[0])}" data-group="{esc(r.get("group") or "")}">'
            f'<h3>{esc(r["name"])}</h3>'
            f'<p>{esc(r.get("pos",""))} {esc(r.get("team",""))} · Keep #{r["bk"]}</p></a>'
        )
        urls.append(f"https://ballkeep.com/bb/players/{slug}.html")
        files.append({
            "key": r["key"],
            "slug": slug,
            "name": r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "age": r.get("age") or "",
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
            "image": "img/bb-logo.jpg",
        })
    flt, js = filter_js(["HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B"])
    hub = f"""
    <p class="kicker">Player Files</p>
    <h2>The Keep, one name at a time</h2>
    <p class="note">Every name in the baseball Keep top 300. Plus/minus, board dump, BK Value. Tape lives on the football desk; the diamond files stay in the cream and navy.</p>
    {flt}
    <div class="grid-3" id="bb-cards">{''.join(cards)}</div>
    """
    hub_js = js.replace("tbody tr", "#bb-cards .tile")
    write("bb/players/index.html", bb_page("Players", "players/index.html", hub, hub_js, depth=2))
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
      <a href="trade-redraft.html">Redraft</a>
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
    <p class="note">Injuries, IL stints, roster moves, and manager reports pulled from search and X, then clustered into short stories. Click a row for the aggregate summary, the original articles / X posts / video, and links back to every BaseBallKeep player page named in the tape. The scrape repeats on its own every hour. Football BK News lives on <a href="../news.html">Ball Keep</a>.</p>
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
                    f'{f"<p class=\\"note\\">{esc(snip)}</p>" if snip else ""}'
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
            named = '<p class="note" style="margin-top:18px">No BaseBallKeep player page matched this cluster yet.</p>'
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
    roster = keep_as_roster(keep)
    stories = rematch_stories(load_news_stories("baseball"), build_player_index(roster))
    news_by_player = defaultdict(list)
    for story in stories:
        for pl in story.get("players") or []:
            key = pl.get("key")
            if key:
                news_by_player[key].append(story)

    tiles = [
        ("the-keep.html", "The Keep", "Overall dynasty top 300. 23-board aggregate."),
        ("news.html", "BK News", "Hourly IL, roster, and manager tape. Click a story for the aggregate and the sources."),
        ("the-lineup.html", "The Lineup", "Dynasty hitters only. The bats you keep."),
        ("pitchers.html", "BK's Pitchers", "Top 100 dynasty arms, SP and the two-way unicorn."),
        ("bullpen.html", "Bullpen — Saves", "Top 100 relief pitchers for saves leagues."),
        ("bullpen-holds.html", "Bullpen — SV+H", "Same bullpen, holds counted. Different sport."),
        ("redraft.html", "Redraft", "2026 rest-of-season board. Age tax flipped."),
        ("trade.html", "Trade Calculators", "Keep, Lineup, Pitchers, Redraft. Same curve."),
        ("waivers-dynasty.html", "Dynasty Wire", "Prospects and IL stashes. Short on purpose."),
        ("waivers-redraft.html", "Redraft Wire", "Priority 1–50. Longer. This week matters."),
        ("players/index.html", "Player Files", "Keep top 300, one cream card each."),
    ]
    latest_news = stories[:5]
    latest_html = ""
    if latest_news:
        latest_html = (
            '<section class="panel" style="margin-top:16px">'
            '<p class="kicker">BK News · Baseball</p>'
            "<h2>Latest on the wire.</h2>"
            '<div class="news-list">'
            + "".join(bb_news_card(s) for s in latest_news)
            + "</div>"
            '<p class="note" style="margin-top:12px"><a href="news.html">All BK News</a></p>'
            "</section>"
        )
    home = f"""
    <section class="hero" style="background-image:url('../img/bb-hero.jpg')">
      <div class="hero-card">
        <p class="kicker" style="color:#ffd36a">Updated {UPDATED}</p>
        <h2>{wordmark()}</h2>
        <p>A navy-and-cream desk for dynasty baseball. Twenty-three boards. One Keep. The football site is still next door.</p>
      </div>
    </section>
    <section class="panel">
      <p class="kicker">What This Desk Is</p>
      <h2>Keep the guys who still mash in 2030.</h2>
      <p class="note"><strong>Redraft baseball</strong> is this summer's counting stats — you stream arms, you chase saves, you survive September. <strong>Dynasty baseball</strong> prices the next five years: peak age, prospect lists, and whether a 22-year-old shortstop is still a shortstop in 2030.</p>
      <p class="note">The Keep is an overall dynasty top 300 aggregated from 23 public boards, led by RotoGraphs' Aug 14 discounted-dollar model and The Dynasty Guru's Aug 10 points Top 500. The Lineup strips the pitchers. BK's Pitchers is the other half. The bullpen is two sports: saves, then saves-plus-holds.</p>
    </section>
    {latest_html}
    <p class="note" style="margin-top:18px"><img src="../img/bb-stitch.jpg" alt="Baseball on forest grass" style="width:100%;border-radius:16px" /></p>
    <div class="grid-3" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    """
    write("bb/index.html", bb_page("Home", "index.html", home))

    flt, js = filter_js(["HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B"])
    keep_body = f"""
    <p class="kicker">Keystone · Overall Dynasty</p>
    <h2>The Keep</h2>
    <p class="note">Baseball top 300, rebuilt {UPDATED}. Ball Keep rank is the average of every source that ranked the player — 23 boards, two of them 500 names long. BK Value uses the same decaying curve as football (12,000 at 1.01).</p>
    {flt}
    <div class="panel">{rank_table(keep, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
    write("bb/the-keep.html", bb_page("The Keep", "the-keep.html", keep_body, js))

    lu_body = f"""
    <p class="kicker">Hitters Only</p>
    <h2>The Lineup</h2>
    {banner("bb-lineup.jpg", "Bats in a dugout rack")}
    <p class="note">Every hitter we could pin to a dynasty board, re-ranked among bats only. Ohtani lives here as a DH. Pitchers have their own building.</p>
    <div class="panel">{rank_table(lineup, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
    write("bb/the-lineup.html", bb_page("The Lineup", "the-lineup.html", lu_body))

    pit_body = f"""
    <p class="kicker">Dynasty Arms</p>
    <h2>BK's Pitchers</h2>
    {banner("bb-pitch.jpg", "Baseball in a pitcher's grip")}
    <p class="note">Top 100 overall dynasty pitchers. Starting pitchers plus the two-way unicorn. Relievers who crack the overall pitcher board sneak in; the full bullpen lives next door.</p>
    <div class="panel">{rank_table(pitchers, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    {sources_panel()}
    """
    write("bb/pitchers.html", bb_page("BK's Pitchers", "pitchers.html", pit_body))

    sv_body = f"""
    <p class="kicker">Relief · Saves</p>
    <h2>BK's Bullpen — Saves</h2>
    {banner("bb-bullpen.jpg", "Bullpen mound at twilight")}
    <p class="note">Top 100 relief pitchers for traditional saves leagues. Chart mix: FantasyPros closer report (Aug 20), ESPN reliever depth chart, and RPs who survive the overall Keep. Bryan Baker has the MLB lead. Diaz is leaking. Scott is the add.</p>
    <div class="panel">{rank_table(saves, ["BK Value"], lambda r: f'<td class="val">{int(r["value"]):,}</td>')}</div>
    {sources_panel()}
    """
    write("bb/bullpen.html", bb_page("Bullpen Saves", "bullpen.html", sv_body))

    svh_body = f"""
    <p class="kicker">Relief · Saves + Holds</p>
    <h2>BK's Bullpen — SV+H</h2>
    {banner("bb-bullpen.jpg", "Bullpen mound at twilight")}
    <p class="note">Same bullpen, different sport. FantasyPros Week 21 SV+H board (Baker / Miller / Varland) plus setup men the ESPN chart actually uses. If your league counts holds, this is the page. The saves page is the other one.</p>
    <div class="panel">{rank_table(svh, ["BK Value"], lambda r: f'<td class="val">{int(r["value"]):,}</td>')}</div>
    {sources_panel()}
    """
    write("bb/bullpen-holds.html", bb_page("Bullpen SV+H", "bullpen-holds.html", svh_body))

    rd_flt, rd_js = filter_js(["HIT", "SP", "RP", "UT"])
    rd_body = f"""
    <p class="kicker">2026 Rest of Season</p>
    <h2>Redraft</h2>
    <p class="note">One-year board. We start from the dynasty mix, then tax kids who are not helping this month and boost veterans who still count. Relievers slide — unless you are in a saves crunch, use the wire.</p>
    {rd_flt}
    <div class="panel">{rank_table(redraft, ["Adj.", "BK Value"], lambda r: f'<td>{r["avg"]}</td><td class="val">{int(r["value"]):,}</td>')}</div>
    {sources_panel()}
    """
    write("bb/redraft.html", bb_page("Redraft", "redraft.html", rd_body, rd_js))

    modes = [
        trade_payload("Dynasty Overall", "trade-keep.html", "Uses The Keep overall ranks.", keep, picks),
        trade_payload("Dynasty Lineup", "trade-lineup.html", "Hitters only, The Lineup ranks.", lineup, picks),
        trade_payload("Dynasty Pitchers", "trade-pitchers.html", "BK's Pitchers ranks. Ohtani is here.", pitchers, picks),
        trade_payload("Redraft", "trade-redraft.html", "Rest-of-season board. No future picks.", redraft, []),
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

    waiver_page(
        "Dynasty Waiver Wire",
        "waivers-dynasty.html",
        "Stash List · Short on purpose",
        "Fifteen names. Prospects, IL stashes, and kids the long boards already stuffed. If he is a streamer this week, he is on the redraft wire — that page is longer and the priorities are louder.",
        DYNASTY_WAIVERS,
        hot=False,
    )
    waiver_page(
        "Redraft Waiver Wire",
        "waivers-redraft.html",
        "Priority 1–50 · September stretch",
        "This is the longer wire. Priority order is the whole point: P1–P10 are must-roster saves and aces, P11–P30 are stream bats and two-start arms, P31–P50 are SV+H specialists and deep-league speed. Check this before you stream a random fifth starter.",
        REDRAFT_WAIVERS,
        hot=True,
    )

    player_urls, player_files = write_player_pages(keep, lineup, pitchers, redraft, news_by_player)
    news_urls = render_bb_news_pages(stories)
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
                "the-keep.html", "the-lineup.html", "pitchers.html", "bullpen.html",
                "bullpen-holds.html", "redraft.html", "trade.html",
                "trade-keep.html", "trade-lineup.html", "trade-pitchers.html",
                "trade-redraft.html", "trade-saves.html", "trade-svh.html",
                "waivers-dynasty.html", "waivers-redraft.html", "players/",
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
