"""The Inheritance: if a starter sits, who walks in, priced on both clocks.

Depth charts name the next man. This page prices him on The Keep and The Board
and then prints how much Sunday money just left the room.
"""
from __future__ import annotations

import json
from pathlib import Path

from bk_curve import ALGORITHM, bk_value
from seo import (
    also_on_desk,
    breadcrumb_jsonld,
    breadcrumbs,
    faq_html,
    faq_jsonld,
    rank_search_bar,
)

ROOT = Path(__file__).resolve().parents[1]

SUNDAY_GAP = 12
YEARS_GAP = -12
HOLE_FAT = 2500
COVER_SHARE = 0.45

SAMPLE_HOLES = [
    "Christian McCaffrey", "Puka Nacua", "Saquon Barkley",
    "Derrick Henry", "Travis Kelce",
]
SAMPLE_YEARS = [
    "Drake Maye", "Jeremiyah Love", "Ashton Jeanty",
    "Caleb Williams", "Tetairoa McMillan",
]

FAQ = [
    ("What is The Inheritance?", "A starter sits. Someone inherits the snaps. The page names that man, prices him on The Keep and The Board, and prints the Sunday money that left the room."),
    ("What is the hole?", "Starter Board BK Value minus heir Board BK Value. A fat hole means the next man cannot replace this year's production. A covered chair means he can."),
    ("What does Years in mean?", "The heir is still a Keep name and already cheap on The Board. Years are walking into a Sunday chair."),
    ("Is this a depth chart?", "The depth chart is the order. The Inheritance is the price of that order on both clocks, plus the injury report on the starter."),
]


def _norm(name: str) -> str:
    from build_site import norm_name
    return norm_name(name)


def _clock(keep_rk: int, board_rk: int) -> str:
    if keep_rk > 0 and board_rk > 0:
        gap = keep_rk - board_rk
        if gap >= SUNDAY_GAP:
            return "Sunday"
        if gap <= YEARS_GAP:
            return "Years"
        return "Even"
    if board_rk > 0:
        return "Sunday"
    if keep_rk > 0:
        return "Years"
    return "Off"


def _pack_side(row, fallback_name, fallback_pos, fallback_team):
    if not row:
        return {
            "name": fallback_name,
            "pos": fallback_pos or "",
            "team": fallback_team or "",
            "keep": 0,
            "board": 0,
            "keep_val": 0,
            "board_val": 0,
            "keep_pos": fallback_pos or "",
            "board_pos": fallback_pos or "",
            "age": None,
            "clock": "Off",
        }
    keep_rk = int(row.get("keep") or 0)
    board_rk = int(row.get("board") or 0)
    return {
        "name": row.get("name") or fallback_name,
        "pos": row.get("pos") or fallback_pos or "",
        "team": row.get("team") or fallback_team or "",
        "keep": keep_rk,
        "board": board_rk,
        "keep_val": int(row.get("keep_val") or (bk_value(keep_rk) if keep_rk else 0)),
        "board_val": int(row.get("board_val") or (bk_value(board_rk) if board_rk else 0)),
        "keep_pos": row.get("keep_pos") or row.get("pos_label") or row.get("pos") or fallback_pos or "",
        "board_pos": row.get("board_pos") or row.get("pos") or fallback_pos or "",
        "age": row.get("age") if row.get("age") not in (None, "") else None,
        "clock": _clock(keep_rk, board_rk),
    }


def _price_map(keep, board):
    from build_site import norm_name

    out = {}
    for r in keep or []:
        name = r.get("name") or ""
        key = r.get("key") or norm_name(name)
        if not key:
            continue
        row = out.setdefault(key, {"name": name})
        row["name"] = name
        row["pos"] = r.get("pos") or row.get("pos") or ""
        row["team"] = r.get("team") or row.get("team") or ""
        row["age"] = r.get("age") if r.get("age") not in (None, "") else row.get("age")
        row["keep"] = int(r.get("bk") or 0)
        row["keep_val"] = int(r.get("value") or bk_value(row["keep"]) if row["keep"] else 0)
        row["keep_pos"] = r.get("pos_label") or r.get("pos") or ""
    for r in board or []:
        name = r.get("name") or ""
        key = r.get("key") or norm_name(name)
        if not key:
            continue
        row = out.setdefault(key, {"name": name})
        row["name"] = name or row.get("name")
        row["pos"] = r.get("pos") or row.get("pos") or ""
        row["team"] = r.get("team") or row.get("team") or ""
        if row.get("age") in (None, "") and r.get("age") not in (None, ""):
            row["age"] = r.get("age")
        row["board"] = int(r.get("bk") or 0)
        row["board_val"] = int(r.get("value") or bk_value(row["board"]) if row["board"] else 0)
        row["board_pos"] = r.get("pos_label") or r.get("pos") or ""
    return out


def room_verdict(starter, heir):
    """Spoken sentence for the hole between a starter and the next man."""
    s_clock = starter.get("clock") or "Off"
    h_clock = heir.get("clock") or "Off"
    s_board = int(starter.get("board_val") or 0)
    h_board = int(heir.get("board_val") or 0)
    hole = s_board - h_board
    if s_clock == "Years" and h_clock == "Sunday":
        return "Sunday behind", "A Sunday name sits behind years."
    if s_board and h_board >= s_board * COVER_SHARE:
        return "Covered", "The chair is covered."
    if hole >= HOLE_FAT and h_clock == "Years":
        return "Years in", "Years walk into a Sunday chair."
    if hole >= HOLE_FAT:
        return "Hole", "A hole opens on Sunday."
    if s_board == 0 and h_board == 0:
        return "Off", "Both names sit off The Board."
    return "Cheaper", "The next man is cheaper on Sunday."


def inherit_rows(keep, board, depth=None, injuries=None):
    """One row per listed starter with a name behind him."""
    priced = _price_map(keep, board)
    if depth is None:
        from weekly_kit import depth_rows
        depth = depth_rows()
    if injuries is None:
        from weekly_kit import injury_rows
        injuries = injury_rows()
    hurt = {}
    for row in injuries or []:
        key = _norm(row.get("name") or "")
        if key:
            hurt[key] = row.get("status") or ""

    rows = []
    for club in depth or []:
        team = club.get("team") or ""
        slots = club.get("slots") or {}
        for pos in ("QB", "RB", "WR", "TE"):
            line = list(slots.get(pos) or [])
            if len(line) < 2:
                continue
            starter_name = line[0].get("name") or ""
            heir_name = line[1].get("name") or ""
            if not starter_name or not heir_name:
                continue
            s_key = _norm(starter_name)
            h_key = _norm(heir_name)
            starter = _pack_side(priced.get(s_key), starter_name, pos, team)
            heir = _pack_side(priced.get(h_key), heir_name, pos, team)
            if starter["keep"] <= 0 and starter["board"] <= 0:
                continue
            tag, verdict = room_verdict(starter, heir)
            hole = starter["board_val"] - heir["board_val"]
            behind = [x.get("name") for x in line[1:4] if x.get("name")]
            status = hurt.get(s_key) or "Active"
            rows.append({
                "name": starter["name"],
                "pos": starter["pos"] or pos,
                "team": starter["team"] or team,
                "age": starter.get("age"),
                "status": status,
                "heir": heir["name"],
                "behind": behind,
                "keep": starter["keep"],
                "board": starter["board"],
                "keep_val": starter["keep_val"],
                "board_val": starter["board_val"],
                "keep_pos": starter["keep_pos"],
                "board_pos": starter["board_pos"],
                "pos_label": starter["keep_pos"] or starter["pos"] or pos,
                "heir_keep": heir["keep"],
                "heir_board": heir["board"],
                "heir_keep_val": heir["keep_val"],
                "heir_board_val": heir["board_val"],
                "heir_keep_pos": heir["keep_pos"],
                "heir_board_pos": heir["board_pos"],
                "heir_clock": heir["clock"],
                "starter_clock": starter["clock"],
                "hole": hole,
                "tag": tag,
                "verdict": verdict,
                "clock": tag,
                "avg": abs(hole),
                "n": 2,
                "starter": starter,
                "heir_side": heir,
            })
    hurt_rank = {
        "Out": 0, "Doubtful": 1, "Injured Reserve": 2, "Questionable": 3,
    }
    rows.sort(key=lambda r: (hurt_rank.get(r["status"], 4), -r["hole"], r["keep"] or 999, r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def write_inherit_lookup(rows, media, updated):
    from build_site import face_src, slugify

    media = media or {}
    rooms = []
    players = []
    for r in rows:
        starter = r["starter"]
        heir = r["heir_side"]
        sid = slugify(starter["name"])
        hid = slugify(heir["name"])
        room = {
            "id": sid,
            "team": r["team"],
            "pos": r["pos"],
            "status": r["status"],
            "hole": r["hole"],
            "tag": r["tag"],
            "verdict": r["verdict"],
            "behind": r["behind"],
            "starter": {
                "id": sid,
                "name": starter["name"],
                "pos": starter["pos"],
                "team": starter["team"],
                "keep": starter["keep"],
                "board": starter["board"],
                "keep_val": starter["keep_val"],
                "board_val": starter["board_val"],
                "keep_pos": starter["keep_pos"],
                "board_pos": starter["board_pos"],
                "clock": starter["clock"],
                "image": face_src({"name": starter["name"]}, media),
            },
            "heir": {
                "id": hid,
                "name": heir["name"],
                "pos": heir["pos"],
                "team": heir["team"],
                "keep": heir["keep"],
                "board": heir["board"],
                "keep_val": heir["keep_val"],
                "board_val": heir["board_val"],
                "keep_pos": heir["keep_pos"],
                "board_pos": heir["board_pos"],
                "clock": heir["clock"],
                "image": face_src({"name": heir["name"]}, media),
            },
        }
        rooms.append(room)
        players.append({
            "id": sid,
            "name": starter["name"],
            "pos": starter["pos"],
            "team": starter["team"],
            "role": "starter",
            "room": sid,
        })
        players.append({
            "id": hid,
            "name": heir["name"],
            "pos": heir["pos"],
            "team": heir["team"],
            "role": "heir",
            "room": sid,
        })
    payload = {
        "updated": updated,
        "algorithm": ALGORITHM,
        "rooms": rooms,
        "players": players,
        "samples": {
            "holes": SAMPLE_HOLES,
            "years": SAMPLE_YEARS,
        },
    }
    dest = ROOT / "data/inherit-lookup.json"
    dest.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))
    return payload


def _inherit_extra(r):
    from build_site import esc, fmt_val
    hole = r["hole"]
    hole_txt = f"+{hole}" if hole > 0 else str(hole)
    return (
        f'<td>{esc(r["heir"])}</td>'
        f'<td class="desk-only">{esc(r["status"])}</td>'
        f'<td class="desk-only">{esc(r["keep_pos"] or r.get("pos") or "")}</td>'
        f'<td class="desk-only">{esc(r["board_pos"] or r.get("pos") or "")}</td>'
        f'<td class="c-val val">{fmt_val(r["keep_val"])}</td>'
        f'<td class="c-val val">{fmt_val(r["board_val"])}</td>'
        f'<td class="c-val val">{esc(fmt_val(r["heir_board_val"]))}</td>'
        f'<td class="c-val val">{esc(hole_txt)}</td>'
        f'<td class="c-clock">{esc(r["tag"])}</td>'
    )


def inherit_tool_html():
    return """
    <section class="inherit-tool" id="inherit-app" aria-label="Name the next man">
      <p class="kicker">If he sits</p>
      <h2>Name a starter. Read the hole.</h2>
      <p class="note">Search a name. The left clock is the starter. The right clock is the man behind him. The hole is Sunday money that leaves the room if the starter sits.</p>
      <div class="split-search">
        <label for="inherit-q">Find a name</label>
        <input id="inherit-q" data-q type="search" placeholder="McCaffrey, Maye, Love…" autocomplete="off" />
        <div class="trade-hits" data-hits></div>
        <div class="trade-add-btns">
          <button type="button" class="cta" data-open="1">Open the room</button>
          <button type="button" class="cta alt" data-sample="holes">Sample Sunday holes</button>
          <button type="button" class="cta ghost" data-sample="years">Sample years chairs</button>
          <button type="button" class="trade-clear" data-clear="1">Clear</button>
        </div>
      </div>
      <div class="inherit-clocks">
        <article class="split-clock keep" data-starter>
          <p class="kicker">Starter</p>
          <h3 data-starter-name>Name him</h3>
          <p class="split-total" data-starter-total>0</p>
          <p class="note" data-starter-meta>Keep and Board on the starter.</p>
        </article>
        <article class="split-clock window" data-hole>
          <p class="kicker">The hole</p>
          <h3 data-hole-total>0</h3>
          <p data-verdict>Search a starter. The next man stays dark until a name is in.</p>
          <p class="note" data-status></p>
        </article>
        <article class="split-clock board" data-heir>
          <p class="kicker">The heir</p>
          <h3 data-heir-name>Next man</h3>
          <p class="split-total" data-heir-total>0</p>
          <p class="note" data-heir-meta>Keep and Board on the name behind him.</p>
        </article>
      </div>
      <ul class="split-room" data-line></ul>
    </section>
    """


def write_the_inheritance(b, keep, board, media):
    from build_site import UPDATED, rank_table

    rows = inherit_rows(keep, board)
    write_inherit_lookup(rows, media, UPDATED)
    extra = also_on_desk(b.FB_ALSO.get("the-inheritance.html") or [])
    hurt_n = sum(1 for r in rows if r["status"] != "Active")
    hole_n = sum(1 for r in rows if r["tag"] == "Hole")
    body = f"""
    <p class="kicker">The next man · {UPDATED}</p>
    <h1>The Inheritance</h1>
    <p class="note">Every other site will name the backup. Dynasty rooms need the price of that backup on two clocks, and they need the hole that opens when the starter sits. The Inheritance reads Sleeper depth, the ESPN report, The Keep, and The Board, then prints the Sunday money that leaves the room. {len(rows)} listed starters have a name behind them. {hurt_n} carry a designation. {hole_n} open a real Sunday hole.</p>
    {inherit_tool_html()}
    <p class="kicker" style="margin-top:28px">The hole board</p>
    <h2>Where Sunday money evaporates.</h2>
    <p class="note">Injured names sit first. Then the fattest holes. A plus hole is starter Board money minus heir Board money. Chairs stay on the starter. Sort and find a player the usual way.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(rows, ["Heir", "Status", "Keep chair", "Board chair", "Keep $", "Board $", "Heir $", "Hole", "Call"], _inherit_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    {b.sources_panel([
        ("Depth Charts", "depth-charts.html", "Sleeper depth order. The listed starter and the man behind him."),
        ("Injuries", "injuries.html", "ESPN designations on the starter."),
        ("The Keep", "the-keep.html", "Superflex dynasty Super Aggregate. The years clock."),
        ("The Board", "board.html", "Redraft PPR Super Aggregate. The Sunday clock."),
        ("The Split", "the-split.html", "Two clocks on a room you type."),
        ("The Next Chair", "next-chair.html", "The essay that belongs with this page."),
    ], heading="Boards behind The Inheritance")}
    {faq_html(FAQ, heading="How The Inheritance is built.")}
    {extra}
    """
    js = '<script src="js/inherit.js" defer></script>'
    b.write(
        "the-inheritance.html",
        b.page(
            "The Inheritance",
            "the-inheritance.html",
            body,
            extra_js=js,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("The Inheritance", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("The Inheritance", "https://ballkeep.com/the-inheritance.html"),
                ]),
                faq_jsonld(FAQ),
            ],
            body_class="inherit-page",
        ),
    )
    return rows
