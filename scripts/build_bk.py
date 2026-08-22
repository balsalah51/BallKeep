#!/usr/bin/env python3
"""Build the BasketKeep static section under bk/."""
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

from bk_cats import plus_minus as bk_plus_minus  # noqa: E402
from bk_data import (  # noqa: E402
    BK_SOURCES,
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
from seo import canon, clip, head_tags, sports_footer, sports_top, value_bars  # noqa: E402


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


BK_NAV = [
    ("index.html", "Home"),
    ("the-keep.html", "The Keep"),
    ("board.html", "The Board"),
    ("news.html", "News"),
    ("the-x.html", "The X"),
    ("guards.html", "Guards"),
    ("wings.html", "Wings"),
    ("bigs.html", "Bigs"),
    ("rookies.html", "Rookies"),
    ("trade.html", "Trade"),
    ("waivers-dynasty.html", "Dynasty Wire"),
    ("waivers-redraft.html", "Redraft Wire"),
    ("players/index.html", "Players"),
]


def wordmark():
    return '<span class="word-basket">BASKET</span><span class="word-ball">BALL</span><span class="word-keep">KEEP</span>'


def bk_nav_target(href: str, path: str, depth: int) -> str:
    if depth < 2:
        return href
    here = path.split("/")[0] + "/" if "/" in path else ""
    if here and href.startswith(here):
        return href[len(here):]
    return "../" + href


def bk_nav_current(href: str, path: str) -> bool:
    if href == path:
        return True
    if href == "news.html" and (path == "news.html" or path.startswith("news/")):
        return True
    return False


BK_SEO = {
    "index.html": (
        "BasketKeep | Dynasty Basketball Rankings and Trade Calculator",
        "Hardwood desk. The Keep is dynasty basketball top 400. The Board is this-year redraft. Guards, wings, bigs, BK News, and The X.",
        "img/bk-hero.jpg",
    ),
    "the-keep.html": (
        "The Keep 2026 Dynasty Basketball Rankings (Top 400) | BasketKeep",
        "Dynasty basketball top 400, rebuilt August 21, 2026. 18-board aggregate. Wembanyama is the 1.01. BK Value starts at 12,000.",
        "img/bk-logo.jpg",
    ),
    "board.html": (
        "The Board — 2026 Redraft Basketball Rankings | BasketKeep",
        "This-year basketball redraft. Veterans climb. Kids pay a tax. Same BK Value curve as The Keep.",
        "img/bk-logo.jpg",
    ),
    "guards.html": (
        "Guards — Dynasty PG and SG Rankings | BasketKeep",
        "Dynasty guards only. The Keep re-ranked among point guards and shooting guards.",
        "img/bk-logo.jpg",
    ),
    "wings.html": (
        "Wings — Dynasty SF and PF Rankings | BasketKeep",
        "Dynasty wings only. Forwards stripped from The Keep.",
        "img/bk-logo.jpg",
    ),
    "bigs.html": (
        "Bigs — Dynasty Center Rankings | BasketKeep",
        "Dynasty centers only. Wemby, Jokic, Chet, and the rest of the fives.",
        "img/bk-logo.jpg",
    ),
    "rookies.html": (
        "2026 NBA Rookie Rankings | BasketKeep",
        "Compiled 2026 class plus the sophomores still priced like kids.",
        "img/bk-logo.jpg",
    ),
    "trade.html": (
        "Dynasty Basketball Trade Calculator | BasketKeep",
        "Keep and Board. Rank becomes BK Value. Fair is within 8%.",
        "img/bk-logo.jpg",
    ),
    "news.html": (
        "BK News Basketball — Injury, Roster, and Coach Tape | BasketKeep",
        "Hourly NBA injury, roster, and coach reports clustered with links back to Keep player files.",
        "img/bk-logo.jpg",
    ),
    "the-x.html": (
        "The X — Basketball Memes from X | BasketKeep",
        "Fun tape, not news. NBA memes pulled from X. Pictures when the wire carries them.",
        "img/bk-logo.jpg",
    ),
    "players/index.html": (
        "BasketKeep Player Files — The Keep Top 400",
        "The Keep top 400, one hardwood card each.",
        "img/bk-logo.jpg",
    ),
    "waivers-dynasty.html": (
        "Dynasty Basketball Waiver Wire | BasketKeep",
        "Fifteen stashes. Prospects and kids the long boards already stuffed.",
        "img/bk-logo.jpg",
    ),
    "waivers-redraft.html": (
        "Redraft Basketball Waiver Wire | BasketKeep",
        "Priority 1–50. Streamers and six-man cats.",
        "img/bk-logo.jpg",
    ),
}


def bk_page(title, path, body, extra_js="", depth=1, description=None, image=None, doc_title=None):
    prefix = "../" * depth
    links = []
    for href, label in BK_NAV:
        cur = ' aria-current="page"' if bk_nav_current(href, path) else ""
        target = bk_nav_target(href, path, depth)
        links.append(f'<a href="{esc(target)}"{cur}>{esc(label)}</a>')
    packed = BK_SEO.get(path)
    full_title = doc_title or (packed[0] if packed else f"{title} | BasketKeep")
    desc = description or (packed[1] if packed else f"{title} on BasketKeep. Dynasty basketball rankings, BK Value, and BK News. Updated {UPDATED}.")
    img = image or (packed[2] if packed else "img/bk-logo.jpg")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path, "bk/"), image=img, brand="BasketKeep")}
  <link rel="stylesheet" href="{prefix}css/bk.css?v=26" />
  <link rel="icon" href="{prefix}img/bk-logo.jpg" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{'index.html' if depth == 1 else '../index.html'}">
        <img src="{prefix}img/bk-logo.jpg" alt="BasketKeep circular basketball logo" />
        <div>
          <p class="brand-title">{wordmark()}</p>
          <p>Dynasty · Redraft · Hardwood</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {sports_top("bk", depth)}
    {body}
    <footer>
      © {date.today().year} BasketKeep · ballkeep.com/bk · Rankings aggregated {UPDATED}. Not affiliated with the NBA.
      {sports_footer("bk", depth)}
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


def rank_table(rows, extra_headers=None, extra_cells=None, show_age=True):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    cols = ["BK", "Player", "Pos", "Team"]
    head = "".join(_rank_th(h) for h in cols + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        age_txt = str(r["age"]) if r.get("age") not in (None, "") else ""
        age_label = f"age {age_txt}" if show_age and age_txt else ""
        age_span = f'<span class="age-desc">{esc(age_label)}</span>' if age_label else ""
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}</div>"
        )
        href = f"players/{slugify(r['name'])}.html"
        name = f'<a class="player-link" href="{href}"><strong>{esc(r["name"])}</strong></a>'
        stack = f'<span class="name-stack">{name}{age_span}{meta}</span>'
        body.append(
            f'<tr data-pos="{esc(pos)}" data-group="{esc(r.get("group") or "")}">'
            f'<td class="rk c-rank">{r.get("bk","")}</td>'
            f'<td class="c-name">{stack}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f"{extra_cells(r)}"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="rank-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def filter_js(keys):
    btns = ['<button type="button" class="active" data-pos="all">All</button>']
    for k in keys:
        btns.append(f'<button type="button" data-pos="{esc(k)}">{esc(k)}</button>')
    html_f = f'<div class="filters" id="pos-f">{"".join(btns)}</div>'
    js = """<script>
    const box = document.getElementById('pos-f');
    box.addEventListener('click', e => {
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
    return html_f, js


def sources_panel():
    lis = "".join(
        f"<li><strong>{esc(n)}</strong> — {esc(note)} {f'<a href=\"{esc(u)}\">link</a>' if u else ''}</li>"
        for n, u, note in BK_SOURCES
    )
    return f'<section class="sources-box panel"><h3>Boards on this mash</h3><ol>{lis}</ol></section>'


def fmt_val(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return "—"


def val_cell(r):
    return (
        f'<td class="desk-only">{r.get("avg", "—")}</td>'
        f'<td class="desk-only">{r.get("n", "—")}</td>'
        f'<td class="c-val val">{fmt_val(r.get("value"))}</td>'
    )


def player_href(name, depth=1):
    return f"{'../' * (depth - 1)}players/{slugify(name)}.html" if depth > 1 else f"players/{slugify(name)}.html"


def keep_as_roster(keep):
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


def bk_news_card(story, prefix=""):
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


def bk_player_href(player, depth=1):
    slug = player.get("slug") or slugify(player.get("name") or "")
    if not slug:
        return None
    return f"{'../' * (depth - 1)}players/{slug}.html" if depth >= 1 else f"players/{slug}.html"


def render_bk_news_pages(stories):
    (ROOT / "bk/news").mkdir(parents=True, exist_ok=True)
    keep = {f"{s['slug']}.html" for s in stories if s.get("slug")}
    for old in (ROOT / "bk/news").glob("*.html"):
        if old.name not in keep:
            old.unlink()
    cards = "".join(bk_news_card(s) for s in stories) or (
        '<p class="note">The basketball wire is warming up. The hourly scrape will fill this desk.</p>'
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
        {"slug": s.get("slug"), "cat": s.get("category") or "wire", "html": bk_news_card(s)}
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
    <p class="kicker">BK News · Basketball · Hourly wire</p>
    <h2>BK News</h2>
    <p class="note">Injuries, roster moves, and coach reports pulled from search and X, then clustered into short stories. Click a row for the aggregate, the original tape, and links back to every BasketKeep player page named in the story. Football BK News lives on <a href="../news.html">Ball Keep</a>.</p>
    <p class="note">{f"Last cluster {esc(news_when(updated))}." if updated else "Awaiting first successful pull."}</p>
    <div class="filters" id="news-filters">{''.join(chips)}</div>
    <div class="news-list" id="news-list">{cards}</div>
    """
    write("bk/news.html", bk_page("BK News", "news.html", body, extra))
    urls = ["https://ballkeep.com/bk/news.html"]
    for s in stories:
        slug = s.get("slug")
        if not slug:
            continue
        cat = s.get("category") or "wire"
        label = CATEGORY_LABEL.get(cat, cat.title())
        sources = s.get("sources") or []
        blocks = []
        for kind, heading in (("article", "Articles"), ("x", "X"), ("video", "Video")):
            rows = [src for src in sources if src.get("kind") == kind]
            if not rows:
                continue
            lis = []
            for src in rows:
                pub = src.get("publisher") or ""
                when = news_when(src.get("published") or "")
                snip = src.get("snippet") or ""
                lis.append(
                    '<li class="source-row">'
                    f'<a href="{esc(src.get("url") or "#")}" rel="noopener noreferrer">{esc(src.get("title") or pub or "Source")}</a>'
                    f'<span class="news-meta">{esc(pub)}{" · " + esc(when) if when else ""}</span>'
                    f'{f"<p class=\"note\">{esc(snip)}</p>" if snip else ""}'
                    "</li>"
                )
            blocks.append(f"<h3>{esc(heading)}</h3><ul class=\"source-list\">{''.join(lis)}</ul>")
        source_html = "".join(blocks) or '<p class="note">Sources attached on the next hourly pass.</p>'
        people = s.get("players") or []
        if people:
            plist = "".join(
                f'<a class="tile" href="{esc(bk_player_href(p, 2) or "#")}"><h3>{esc(p.get("name") or "")}</h3>'
                f'<p class="note">{esc(p.get("pos") or "")} {esc(p.get("team") or "")}</p></a>'
                for p in people if bk_player_href(p, 2)
            )
            named = f'<p class="kicker" style="margin-top:22px">Players on this story</p><div class="grid-3">{plist}</div>'
        else:
            named = '<p class="note" style="margin-top:18px">No BasketKeep player page matched this cluster yet.</p>'
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
        write(f"bk/news/{slug}.html", bk_page(s.get("headline") or "BK News", f"news/{slug}.html", story_body, depth=2))
        urls.append(f"https://ballkeep.com/bk/news/{slug}.html")
    return urls


def write_player_pages(keep, board, news_by_player):
    board_map = {r["key"]: r for r in board}
    (ROOT / "bk/players").mkdir(parents=True, exist_ok=True)
    urls = []
    files = []
    keep_slugs = set()
    for r in keep:
        slug = slugify(r["name"])
        keep_slugs.add(f"{slug}.html")
        br = board_map.get(r["key"])
        ranks = r.get("ranks") or {}
        hi = min(ranks.values()) if ranks else r["bk"]
        lo = max(ranks.values()) if ranks else r["bk"]
        stories = news_by_player.get(r["key"]) or []
        news_html = ""
        if stories:
            news_html = (
                '<p class="kicker" style="margin-top:22px">On the wire</p>'
                '<div class="news-list">'
                + "".join(bk_news_card(s, prefix="../") for s in stories[:3])
                + "</div>"
            )
        plus, minus = bk_plus_minus(r)
        board_rows = "".join(
            f"<tr><td>{esc(src)}</td><td>{rk}</td></tr>" for src, rk in sorted(ranks.items(), key=lambda kv: kv[1])[:12]
        )
        body = f"""
    <div class="player-hero">
      <img src="../../img/bk-logo.jpg" alt="{esc(r['name'])}" />
      <div>
        <p class="kicker">{esc(r.get("pos") or "")} · {esc(r.get("team") or "")}</p>
        <h2>{esc(r["name"])}</h2>
        <div class="chips">
          <span class="chip">Keep #{r["bk"]}</span>
          {f'<span class="chip">Board #{br["bk"]}</span>' if br else ""}
          {f'<span class="chip">Age {esc(r.get("age"))}</span>' if r.get("age") else ""}
          <span class="chip">{fmt_val(r.get("value"))} BK Value</span>
        </div>
      </div>
    </div>
    <div class="rank-grid">
      <div class="rank-card"><small>The Keep</small><strong>{r["bk"]}</strong><span>Dynasty</span></div>
      <div class="rank-card"><small>The Board</small><strong>{br["bk"] if br else "—"}</strong><span>Redraft</span></div>
      <div class="rank-card"><small>Desks</small><strong>{r.get("n") or "—"}</strong><span>avg {r.get("avg") or "—"}</span></div>
    </div>
    <div class="plusminus">
      <div class="pm plus"><h3>Plus</h3><ul>{''.join(f"<li>{esc(x)}</li>" for x in plus)}</ul></div>
      <div class="pm minus"><h3>Minus</h3><ul>{''.join(f"<li>{esc(x)}</li>" for x in minus)}</ul></div>
    </div>
    <section class="panel">
      <p class="kicker">Boards</p>
      <h3>Where the desks put him</h3>
      <p class="note">High {hi} · low {lo}. Unranked desks are skipped.</p>
      <div class="table-wrap"><table class="boards"><thead><tr><th>Desk</th><th>Rank</th></tr></thead><tbody>{board_rows}</tbody></table></div>
    </section>
    {news_html}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-keep.html">The Keep</a> · <a href="../board.html">The Board</a> · <a href="../news.html">BK News</a></p>
    """
        write(f"bk/players/{slug}.html", bk_page(r["name"], f"players/{slug}.html", body, depth=2,
                                                 description=clip(f"{r['name']} is BasketKeep #{r['bk']} in dynasty. {r.get('pos')} {r.get('team')}.")))
        urls.append(f"https://ballkeep.com/bk/players/{slug}.html")
        files.append({
            "key": r.get("key") or "",
            "name": r["name"],
            "slug": slug,
            "pos": r.get("pos"),
            "team": r.get("team"),
            "age": r.get("age"),
            "keep": r["bk"],
            "board": br["bk"] if br else None,
            "bk": r["bk"],
            "value": r.get("value"),
            "lists": {"The Keep": r.get("bk")},
            "sport": "basketball",
            "url": f"https://ballkeep.com/bk/players/{slug}.html",
        })
    for old in (ROOT / "bk/players").glob("*.html"):
        if old.name not in keep_slugs and old.name != "index.html":
            old.unlink()
    cards = []
    for r in keep:
        slug = slugify(r["name"])
        cards.append(
            f'<a class="tile player-card" href="{slug}.html" data-pos="{esc(r.get("pos") or "")}">'
            f'<img src="../../img/bk-logo.jpg" alt="" />'
            f'<h3>{esc(r["name"])}</h3>'
            f'<p class="note">{esc(r.get("pos") or "")} {esc(r.get("team") or "")} · Keep #{r["bk"]}</p></a>'
        )
    flt, js = filter_js(["PG", "SG", "SF", "PF", "C"])
    hub = f"""
    <p class="kicker">Player files</p>
    <h2>The Keep, one name at a time</h2>
    <p class="note">The Keep top {len(keep)}. Rank, The Board redraft slot, every desk, plus/minus. Filter the grid.</p>
    {flt}
    <div class="player-grid">{''.join(cards)}</div>
    """
    write("bk/players/index.html", bk_page("Players", "players/index.html", hub, js))
    urls.insert(0, "https://ballkeep.com/bk/players/")
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


def write_trade(payload):
    body = f"""
    <p class="kicker">Trade Calculator</p>
    <h2>{esc(payload["label"])}</h2>
    <p class="note">{esc(payload["blurb"])} Fair is within 8%. Same BK Value curve as football: rank 1 = 12,000.</p>
    <p class="filters">
      <a href="trade.html">All calculators</a>
      <a href="trade-keep.html">Keep</a>
      <a href="trade-board.html">Board</a>
    </p>
    <div id="trade-app" class="trade-app"></div>
    """
    blob = json.dumps(payload, ensure_ascii=False)
    extra = f"<script>window.BK_TRADE = {blob};</script>\n<script src=\"../js/trade.js\"></script>"
    write("bk/" + payload["file"], bk_page(payload["label"], payload["file"], body, extra))


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
    write("bk/" + path, bk_page(title, path, body))


def write_basket_site():
    u = load_universe()
    keep, board = u["keep"], u["board"]
    guards, wings, bigs = u["guards"], u["wings"], u["bigs"]
    rookies = u["rookies"]
    picks = [{"id": slugify(p["name"]), **p} for p in u["picks"]]
    roster = keep_as_roster(keep)
    stories = rematch_stories(load_news_stories("basketball"), build_player_index(roster))
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
            + "".join(bk_news_card(s) for s in latest_news)
            + "</div>"
            '<p class="note" style="margin-top:12px"><a href="news.html">All BK News</a></p>'
        )
    home = f"""
    <section class="hero" style="background-image:url('../img/bk-hero.jpg')">
      <div class="hero-card">
        <p class="kicker" style="color:#fff">Updated {UPDATED}</p>
        <h2>{wordmark()}</h2>
        <p class="hero-lead">Dynasty first. Redraft right behind it. Same Keep / Board split as football, on hardwood.</p>
        <div class="hero-ctas">
          <a class="cta" href="the-keep.html">The Keep · Dynasty</a>
          <a class="cta alt" href="board.html">The Board · Redraft</a>
        </div>
      </div>
    </section>
    <section class="desk-block main">
      <p class="kicker">Hardwood</p>
      <h2>The Keep and The Board</h2>
      <p class="note">Two lists. Everything else on this page supports these.</p>
      <div class="home-leads">
        <a class="tile lead keep" href="the-keep.html">
          <h3>The Keep</h3>
          <p class="lead-sub">Dynasty basketball · top 400</p>
          <p>18 desks mashed into one rank. This is the list you trade on.</p>
        </a>
        <a class="tile lead board" href="board.html">
          <h3>The Board</h3>
          <p class="lead-sub">Redraft basketball · this year</p>
          <p>Veterans climb. Kids pay a tax.</p>
        </a>
      </div>
      <div class="grid">
        <a class="tile" href="trade.html"><h3>Trade Calculators</h3><p>Keep and Board. Rank becomes BK Value.</p></a>
        <a class="tile" href="players/index.html"><h3>Player Files</h3><p>Keep top 400.</p></a>
      </div>
    </section>
    {desk_block("lists", "Lists", "The other boards.", "Positions, rookies, and the wires.", [
        ("guards.html", "Guards", "PG and SG, Keep-ranked."),
        ("wings.html", "Wings", "SF and PF."),
        ("bigs.html", "Bigs", "Centers."),
        ("rookies.html", "Rookies", "2026 class plus the kids."),
        ("waivers-dynasty.html", "Dynasty Wire", "Fifteen stashes."),
        ("waivers-redraft.html", "Redraft Wire", "Priority 1–50."),
    ])}
    {desk_block("extra", "Extra", "News and The X.", "Memes and the wire. Not the ranks.", [
        ("the-x.html", "The X", "NBA memes. Pictures on the card."),
        ("news.html", "BK News", "Injuries, roster, coaches."),
    ], extra_news)}
    """
    write("bk/index.html", bk_page("Home", "index.html", home))

    flt, js = filter_js(["G", "F", "C", "PG", "SG", "SF", "PF"])
    keep_body = f"""
    <p class="kicker">Keystone · Dynasty basketball</p>
    <h2>The Keep</h2>
    <p class="note">This is the big one. Dynasty basketball top {len(keep)}, rebuilt {UPDATED}. Ball Keep rank is the average of every source that ranked the player — 18 boards. Unranked is skipped, never 999. BK Value uses the same decaying curve as football (12,000 at 1.01). The Board next door is this-year redraft.</p>
    {flt}
    <div class="panel">{rank_table(keep, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    {value_bars(keep, 12, "#e87722", "Keep value graph")}
    {sources_panel()}
    """
    write("bk/the-keep.html", bk_page("The Keep", "the-keep.html", keep_body, js))

    def board_extra(r):
        return (
            f'<td class="desk-only">{r.get("keep") or "—"}</td>'
            f'<td class="c-val val">{fmt_val(r.get("value"))}</td>'
        )
    board_body = f"""
    <p class="kicker">Redraft · this year</p>
    <h2>The Board</h2>
    <p class="note">Not The Keep. The Keep is dynasty. The Board is redraft — {len(board)} names, this season only. Veterans climb. Kids pay a tax. Use this list for 2026-27 startups.</p>
    <div class="panel">{rank_table(board, ["Keep", "BK Value"], board_extra)}</div>
    {value_bars(board, 12, "#1a1208", "Board value graph")}
    """
    write("bk/board.html", bk_page("The Board", "board.html", board_body))

    g_body = f"""
    <p class="kicker">Guards only</p>
    <h2>Guards</h2>
    <p class="note">Point guards and shooting guards stripped from The Keep and re-ranked among themselves.</p>
    <div class="panel">{rank_table(guards, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    """
    write("bk/guards.html", bk_page("Guards", "guards.html", g_body))

    w_body = f"""
    <p class="kicker">Wings only</p>
    <h2>Wings</h2>
    <p class="note">Small forwards and power forwards. The Keep, forwards only.</p>
    <div class="panel">{rank_table(wings, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    """
    write("bk/wings.html", bk_page("Wings", "wings.html", w_body))

    b_body = f"""
    <p class="kicker">Centers only</p>
    <h2>Bigs</h2>
    <p class="note">The fives. Wemby is the 1.01. Jokic is the this-year argument.</p>
    <div class="panel">{rank_table(bigs, ["Avg", "# Boards", "BK Value"], val_cell)}</div>
    """
    write("bk/bigs.html", bk_page("Bigs", "bigs.html", b_body))

    rook_rows = "".join(
        f'<article class="tile"><p class="kicker">#{r["bk"]}</p><h3>{esc(r["name"])} '
        f'<span class="pos">{esc(r["pos"])}</span> {esc(r["team"])}</h3><p>{esc(r["blurb"])}</p></article>'
        for r in rookies
    )
    rook_body = f"""
    <p class="kicker">2026 class · plus the kids</p>
    <h2>Rookies</h2>
    <p class="note">Compiled 2026 draftees and the sophomores still priced like the future. Not a mock. A Keep-adjacent board.</p>
    <div class="grid">{rook_rows}</div>
    """
    write("bk/rookies.html", bk_page("Rookies", "rookies.html", rook_body))

    write_trade(trade_payload("Dynasty Overall", "trade-keep.html", "Uses The Keep dynasty ranks.", keep, picks))
    write_trade(trade_payload("Redraft", "trade-board.html", "Uses The Board redraft ranks. No future picks.", board, []))
    hub = """
    <p class="kicker">Trade Calculators</p>
    <h2>Two Calculators, One Curve</h2>
    <p class="note">Rank becomes BK Value the same way it does on the football desk. Rank 1 is 12,000. Fair is within 8%. The Keep calc includes 2027/2028 pick chips.</p>
    <div class="grid">
      <a class="tile" href="trade-keep.html"><h3>The Keep</h3><p>Dynasty. First-round chips.</p></a>
      <a class="tile" href="trade-board.html"><h3>The Board</h3><p>Redraft. This year only.</p></a>
    </div>
    """
    write("bk/trade.html", bk_page("Trade Calculators", "trade.html", hub))

    waiver_page(
        "Dynasty Waiver Wire",
        "waivers-dynasty.html",
        "Stash List · Short on purpose",
        "Fifteen names. Prospects and kids the long boards already stuffed. If he is a streamer this week, he is on the redraft wire.",
        DYNASTY_WAIVERS,
        hot=False,
    )
    waiver_page(
        "Redraft Waiver Wire",
        "waivers-redraft.html",
        "Priority 1–50 · Opening night",
        "This is the longer wire. P1–P10 are must-roster six-men and stream cats. P11–P30 are threes and stocks. P31–P50 are deep-league fliers.",
        REDRAFT_WAIVERS,
        hot=True,
    )

    player_urls, player_files = write_player_pages(keep, board, news_by_player)
    news_urls = render_bk_news_pages(stories)
    x_body = f"""
    <p class="kicker">Fun tape · not news</p>
    <h2>The X</h2>
    <p class="note">NBA memes and shitposts pulled from X. Pictures when the wire carries them.</p>
    {x_cards("basketball", 1, esc)}
    <p class="note" style="margin-top:16px"><a href="../the-x.html">Football The X</a> · <a href="../bb/the-x.html">Baseball The X</a> · <a href="../pl/the-x.html">PitchKeep The X</a></p>
    """
    write("bk/the-x.html", bk_page("The X", "the-x.html", x_body))
    (ROOT / "data/bk-keep.json").write_text(json.dumps({
        "updated": UPDATED,
        "keep": keep,
        "board": board,
        "guards": guards,
        "wings": wings,
        "bigs": bigs,
        "rookies": rookies,
    }, indent=2, default=str))
    return {
        "keep": keep,
        "board": board,
        "guards": guards,
        "wings": wings,
        "bigs": bigs,
        "rookies": rookies,
        "picks": picks,
        "files": player_files,
        "dynasty_waivers": DYNASTY_WAIVERS,
        "redraft_waivers": REDRAFT_WAIVERS,
        "source_names": [name for name, _u, _n in BK_SOURCES],
        "news": stories,
        "urls": ["https://ballkeep.com/bk/"] + [
            "https://ballkeep.com/bk/" + p
            for p in [
                "the-keep.html", "board.html", "news.html", "the-x.html",
                "guards.html", "wings.html", "bigs.html", "rookies.html",
                "trade.html", "trade-keep.html", "trade-board.html",
                "waivers-dynasty.html", "waivers-redraft.html", "players/",
            ]
        ] + news_urls + player_urls,
        "n_keep": len(keep),
        "n_board": len(board),
        "n_news": max(0, len(news_urls) - 1),
    }
