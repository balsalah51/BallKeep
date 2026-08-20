#!/usr/bin/env python3
"""Build the BaseBallKeep static section under bb/."""
from __future__ import annotations

import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 20, 2026"

from bb_data import (  # noqa: E402
    BB_SOURCES,
    DYNASTY_WAIVERS,
    REDRAFT_WAIVERS,
    bk_value,
    load_universe,
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


def bb_page(title, path, body, extra_js="", depth=1):
    prefix = "../" * depth
    links = []
    for href, label in BB_NAV:
        cur = ' aria-current="page"' if href == path else ""
        if depth == 2:
            target = href if href.startswith("players/") else "../" + href
            if href.startswith("players/") and path.startswith("players/"):
                target = href[len("players/") :]
        else:
            target = href
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


def load_bb_media():
    path = ROOT / "data/bb-media.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


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


def facts_table(media, r):
    media = media or {}
    items = []
    if media.get("number"):
        items.append(("No.", f"#{media['number']}"))
    pos = r.get("pos") or media.get("pos") or ""
    if pos:
        items.append(("Pos", pos))
    team = media.get("team_name") or r.get("team") or media.get("team") or ""
    if team:
        items.append(("Team", team))
    age = r.get("age") or media.get("age") or ""
    if age:
        items.append(("Age", age))
    if media.get("bats") or media.get("throws"):
        items.append(("B / T", f"{media.get('bats') or '—'} / {media.get('throws') or '—'}"))
    if media.get("height"):
        items.append(("Height", media["height"]))
    if media.get("weight"):
        items.append(("Weight", f"{media['weight']} lbs"))
    if media.get("birth"):
        items.append(("Born", media["birth"]))
    home = ", ".join(x for x in (media.get("birth_city"), media.get("birth_country")) if x)
    if home:
        items.append(("From", home))
    if media.get("debut"):
        items.append(("MLB debut", media["debut"][:10]))
    if media.get("draft"):
        items.append(("Draft", media["draft"]))
    if media.get("mlb_id"):
        items.append(("MLB ID", media["mlb_id"]))
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
            "<table><thead><tr>"
            "<th>Year</th><th>G</th><th>AB</th><th>R</th><th>H</th><th>2B</th>"
            "<th>HR</th><th>RBI</th><th>SB</th><th>BB</th><th>SO</th>"
            "<th>AVG</th><th>OBP</th><th>SLG</th><th>OPS</th>"
            "</tr></thead><tbody>"
            f"{hit_rows}</tbody></table></div>"
        )
    if pit_rows:
        parts.append(
            '<div class="panel season">'
            '<p class="kicker">Pitching</p>'
            "<table><thead><tr>"
            "<th>Year</th><th>G</th><th>GS</th><th>W</th><th>L</th><th>SV</th>"
            "<th>HLD</th><th>IP</th><th>K</th><th>BB</th><th>HR</th>"
            "<th>ERA</th><th>WHIP</th><th>K/9</th>"
            "</tr></thead><tbody>"
            f"{pit_rows}</tbody></table></div>"
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
        ("Redraft", lists.get("BB Redraft"), None),
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
        f'<table class="boards"><thead><tr><th>Source</th><th>Rank</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></section>"
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
    name, pos, team = r["name"], r.get("pos") or "", r.get("team") or media.get("team") or ""
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
    if keep and keep <= 15:
        plus.append(f"Keep #{keep} — first-round dynasty capital on a 23-board mix.")
    elif keep and keep <= 50:
        plus.append(f"Keep #{keep} — still a building-block name on the 300.")
    elif keep and keep <= 150:
        plus.append(f"Keep #{keep} on the 300. Tradable, not a 1.01.")
    if keep and keep <= 40 and n:
        plus.append(f"Average {r.get('avg')} across {n} boards.")
    if lists.get("The Lineup") and lists["The Lineup"] <= 40:
        plus.append(f"Lineup #{lists['The Lineup']} among dynasty bats.")
    if lists.get("BK Pitchers") and lists["BK Pitchers"] <= 25:
        plus.append(f"BK's Pitchers #{lists['BK Pitchers']} — ace-room capital.")
    if lists.get("BB Redraft") and keep and lists["BB Redraft"] + 15 < keep:
        plus.append(f"Redraft #{lists['BB Redraft']} — helping this month more than the dynasty slot says.")
    if lists.get("BB Redraft") and keep and lists["BB Redraft"] > keep + 25:
        minus.append(f"Redraft #{lists['BB Redraft']} is colder than Keep #{keep} — this is a future, not a September stream.")
    if age_n and age_n <= 24:
        plus.append(f"Age {age_n} — still climbing the curve.")
    if age_n and age_n >= 33:
        minus.append(f"Age {age_n} is a dynasty tax even when 2026 is loud.")
    if g == "RP":
        minus.append("Reliever volatility: the ninth can vanish in a week.")
        if lists.get("Saves"):
            plus.append(f"Saves board #{lists['Saves']}.")
        if lists.get("SVH"):
            plus.append(f"SV+H board #{lists['SVH']}.")
    if g == "SP" and keep and keep <= 30:
        plus.append("Ace-tier innings. Pitcher injuries are the tax, not the ranking.")
    if n >= 8:
        plus.append(f"On {n} boards — not a one-list darling.")
    if ranks:
        vals = list(ranks.values())
        spread = max(vals) - min(vals)
        if spread >= 40:
            minus.append(f"Board spread is {spread} ranks. You are betting with one camp, not a unanimous tape.")
        elif spread <= 8 and n >= 6:
            plus.append(f"Tight tape — the boards only disagree by {spread} spots.")
    if hit.get("hr") and int(hit.get("hr") or 0) >= 25:
        plus.append(f"{hit['hr']} homers in 2026. The counting stats match the rank.")
    if hit.get("sb") and int(hit.get("sb") or 0) >= 25:
        plus.append(f"{hit['sb']} steals — category juice, not just a pretty OPS.")
    if pit.get("era") and g in ("SP", "UT"):
        try:
            era = float(pit["era"])
            if era <= 3.20:
                plus.append(f"{pit['era']} ERA in {pit.get('ip') or '?'} IP. The arm is doing the job this year.")
            elif era >= 4.50:
                minus.append(f"{pit['era']} ERA is the 2026 tax. Dynasty can wait; redraft has to live with it.")
        except (TypeError, ValueError):
            pass
    if not media.get("mlb_id"):
        minus.append("No 2026 MLB line yet — prospect file. The rank is the projection, not the box score.")
        plus.append("The long boards already stuffed him. That is how Keep names get made.")
    if keep and keep >= 200:
        minus.append(f"Keep #{keep} is the edge of the 300. Deep-league / taxi-squad more than a foundation chip.")
    if not plus:
        plus.append(f"{pos} {team} sits on The Keep at #{keep}.")
    if not minus:
        minus.append("The rank is the comment until the next IL stint.")

    lineup_bit = f" Lineup #{lists['The Lineup']}." if lists.get("The Lineup") else ""
    pit_bit = f" BK's Pitchers #{lists['BK Pitchers']}." if lists.get("BK Pitchers") else ""
    rd_bit = f" Rest-of-season redraft #{lists['BB Redraft']}." if lists.get("BB Redraft") else ""
    stat_bit = ""
    if hit.get("g"):
        stat_bit = f" 2026 line: {hit.get('avg') or '—'} / {hit.get('hr') or 0} HR / {hit.get('sb') or 0} SB / {hit.get('ops') or '—'} OPS in {hit.get('g')} games."
    elif pit.get("ip"):
        stat_bit = f" 2026 line: {pit.get('era') or '—'} ERA, {pit.get('whip') or '—'} WHIP, {pit.get('so') or 0} K in {pit.get('ip')} IP."
    debut = media.get("debut") or ""
    debut_bit = f" MLB since {debut[:4]}." if debut else (" Still a prospect clock." if not media.get("mlb_id") else "")
    home = media.get("birth_country") or ""
    home_bit = f" From {media.get('birth_city') or ''}{' / ' if media.get('birth_city') and home else ''}{home}." if home or media.get("birth_city") else ""
    bats = ""
    if media.get("bats") or media.get("throws"):
        bats = f" Bats {media.get('bats') or '—'}, throws {media.get('throws') or '—'}."
    grafs = [
        f"{name} is #{keep} on BaseBallKeep's overall dynasty 300, a 23-source mix anchored by RotoGraphs (Aug 14) and The Dynasty Guru points list (Aug 10). {pos} for {team or media.get('team_name') or 'the org'}.{lineup_bit}{pit_bit}{rd_bit}{debut_bit}{home_bit}{bats}",
        f"BK Value on this rank is {int(r.get('value') or 0):,}. Same decaying curve as football: 12,000 at 1.01, a late first a fraction of that. If someone is asking for two firsts, run the calculator.{stat_bit}",
        f"The 23-board average is {r.get('avg')} on {n} lists that actually ranked him — unranked sources are skipped, never treated as 999. "
        + (f"High {min(ranks.values())}, low {max(ranks.values())}." if ranks else "Short tape."),
        "Dynasty pays the next five years. Redraft pays September. If those two ranks diverge, that is the instruction: hold the kid or cash the veteran.",
        "Flags fly forever. We will refresh this file with The Keep. September baseball is a proving ground, not a coronation.",
    ]
    return plus[:7], minus[:7], grafs


def write_player_pages(keep, lineup, pitchers, redraft, saves=None, svh=None):
    lu = {r["key"]: r for r in lineup}
    pit = {r["key"]: r for r in pitchers}
    rd = {r["key"]: r for r in redraft}
    sv = {r["key"]: r for r in (saves or [])}
    svh_m = {r["key"]: r for r in (svh or [])}
    media_all = load_bb_media()
    cards = []
    urls = []
    files = []
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
        chips = [f'<span class="chip">Keep #{r["bk"]}</span>']
        chips.append(f'<span class="chip">BK {int(r.get("value") or 0):,}</span>')
        if lists.get("The Lineup"):
            chips.append(f'<span class="chip">Lineup #{lists["The Lineup"]}</span>')
        if lists.get("BK Pitchers"):
            chips.append(f'<span class="chip">Pitchers #{lists["BK Pitchers"]}</span>')
        if lists.get("BB Redraft"):
            chips.append(f'<span class="chip">Redraft #{lists["BB Redraft"]}</span>')
        if lists.get("Saves"):
            chips.append(f'<span class="chip">Saves #{lists["Saves"]}</span>')
        if lists.get("SVH"):
            chips.append(f'<span class="chip">SV+H #{lists["SVH"]}</span>')
        age = r.get("age") or media.get("age")
        if age:
            chips.append(f'<span class="chip">Age {esc(age)}</span>')
        if media.get("number"):
            chips.append(f'<span class="chip">#{esc(media["number"])}</span>')
        img = media.get("image") or "img/bb-logo.jpg"
        img_src = "../../" + img
        body = f"""
    <p class="kicker">Player File · {esc(r.get("pos") or media.get("pos") or "")} {esc(r.get("team") or media.get("team") or "")}</p>
    <div class="player-hero">
      <img src="{esc(img_src)}" alt="{esc(r['name'])}" />
      <div>
        <h2>{esc(r["name"])}</h2>
        <p class="note">{esc(bio_line(media, r))}</p>
        <div class="chips">{''.join(chips)}</div>
      </div>
    </div>
    {facts_table(media, r)}
    {stat_pills(media, r.get("group") or "")}
    {season_box(media)}
    {list_cards(lists, r)}
    <div class="plusminus">
      <div class="pm"><h3>Plus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in plus)}</ul></div>
      <div class="pm"><h3>Minus</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in minus)}</ul></div>
    </div>
    <section class="panel">
      <p class="kicker">BaseBallKeep Take</p>
      {''.join(f'<p>{esc(g)}</p>' for g in grafs)}
    </section>
    {boards_table(r.get("ranks") or {})}
    {waiver_note(r["name"], DYNASTY_WAIVERS, REDRAFT_WAIVERS)}
    {neighbors(keep, i)}
    {same_pos(keep, r)}
    <p class="note" style="margin-top:18px"><a href="index.html">All players</a> · <a href="../the-keep.html">The Keep</a> · <a href="../the-lineup.html">The Lineup</a> · <a href="../pitchers.html">Pitchers</a> · <a href="../trade-keep.html">Calculator</a></p>
    """
        write(f"bb/players/{slug}.html", bb_page(r["name"], f"players/{slug}.html", body, depth=2))
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
        })
    flt, js = filter_js(["HIT", "SP", "RP", "UT", "C", "SS", "OF", "1B", "2B", "3B"])
    hub = f"""
    <p class="kicker">Player Files</p>
    <h2>The Keep, one name at a time</h2>
    <p class="note">Every name in the baseball Keep top 300. Headshot, bio, 2026 and 2025 lines, plus/minus, every board, BK Value. Filter the grid. Click a face.</p>
    {flt}
    <div class="player-grid" id="bb-cards">{''.join(cards)}</div>
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


def write_baseball_site():
    u = load_universe()
    keep, lineup, pitchers = u["keep"], u["lineup"], u["pitchers"]
    saves, svh, redraft = u["saves"], u["svh"], u["redraft"]
    picks = [{"id": slugify(p["name"]), **p} for p in u["picks"]]

    tiles = [
        ("the-keep.html", "The Keep", "Overall dynasty top 300. 23-board aggregate."),
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

    player_urls, player_files = write_player_pages(keep, lineup, pitchers, redraft, saves, svh)
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
        "urls": ["https://ballkeep.com/bb/"] + [
            "https://ballkeep.com/bb/" + p
            for p in [
                "the-keep.html", "the-lineup.html", "pitchers.html", "bullpen.html",
                "bullpen-holds.html", "redraft.html", "trade.html",
                "trade-keep.html", "trade-lineup.html", "trade-pitchers.html",
                "trade-redraft.html", "trade-saves.html", "trade-svh.html",
                "waivers-dynasty.html", "waivers-redraft.html", "players/",
            ]
        ] + player_urls,
        "n_keep": len(keep),
        "n_players": len(keep),
        "n_saves": len(saves),
        "n_svh": len(svh),
        "n_lineup": len(lineup),
        "n_pitchers": len(pitchers),
    }
