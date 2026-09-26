"""The Handcuff: RB-only next men, ranked once for dynasty and once for redraft.

Every other site publishes one handcuff list. Dynasty rooms and Sunday rooms
need two. The cuff is the name on the board. The starter is the chair behind him.
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
OPEN_FAT = 2500
COVER_SHARE = 0.45

SAMPLE_DYNASTY = [
    "Jeremiyah Love", "Ashton Jeanty", "Bijan Robinson",
    "Jahmyr Gibbs", "Breece Hall",
]
SAMPLE_REDRAFT = [
    "Christian McCaffrey", "Saquon Barkley", "Derrick Henry",
    "Jonathan Taylor", "Josh Jacobs",
]

FAQ = [
    ("What is The Handcuff?", "Running backs only. The listed cuff is the Sleeper name behind the starter. Dynasty ranks that backup by Keep value. Redraft ranks him by Board value."),
    ("Why two lists?", "A backup behind Christian McCaffrey is a redraft add. A backup behind a young Keep back is a stash. One list makes those rooms fight. Two lists let both rooms be right."),
    ("How are the lists sorted?", "Dynasty uses the cuff's Keep value. Redraft uses the cuff's Board value. Highest cuff value sits first. The starter's value sits next to it so you can see the gap."),
    ("How is a cuff picked?", "Sleeper depth order. The listed RB1 is the starter. The listed RB2 is the cuff. ESPN designations sit on the starter."),
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
    s_clock = starter.get("clock") or "Off"
    h_clock = heir.get("clock") or "Off"
    s_board = int(starter.get("board_val") or 0)
    h_board = int(heir.get("board_val") or 0)
    opened = s_board - h_board
    if s_clock == "Years" and h_clock == "Sunday":
        return "Play now", "The backup is the one you start this year."
    if s_board and h_board >= s_board * COVER_SHARE:
        return "Has a role", "This backup already plays enough to have a price."
    if opened >= OPEN_FAT and h_clock == "Years":
        return "Stash", "Hold him. If the starter sits, a big role opens."
    if opened >= OPEN_FAT:
        return "Open work", "If the starter sits, a lot of touches need a new name."
    if s_board == 0 and h_board == 0:
        return "Unranked", "Neither name is on The Board."
    return "Cheap backup", "The backup is cheaper than the starter."


def handcuff_rooms(keep, board, depth=None, injuries=None):
    """One room per listed RB1 with an RB2 behind him."""
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
        line = list((club.get("slots") or {}).get("RB") or [])
        if len(line) < 2:
            continue
        starter_name = line[0].get("name") or ""
        heir_name = line[1].get("name") or ""
        if not starter_name or not heir_name:
            continue
        starter = _pack_side(priced.get(_norm(starter_name)), starter_name, "RB", team)
        heir = _pack_side(priced.get(_norm(heir_name)), heir_name, "RB", team)
        if starter["keep"] <= 0 and starter["board"] <= 0:
            continue
        tag, verdict = room_verdict(starter, heir)
        hole = starter["board_val"] - heir["board_val"]
        rows.append({
            "name": starter["name"],
            "pos": "RB",
            "team": starter["team"] or team,
            "age": starter.get("age"),
            "status": hurt.get(_norm(starter_name)) or "Active",
            "heir": heir["name"],
            "behind": [x.get("name") for x in line[1:4] if x.get("name")],
            "keep": starter["keep"],
            "board": starter["board"],
            "keep_val": starter["keep_val"],
            "board_val": starter["board_val"],
            "keep_pos": starter["keep_pos"],
            "board_pos": starter["board_pos"],
            "pos_label": starter["keep_pos"] or "RB",
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
    return rows


def _cuff_view(r):
    heir = r.get("heir_side") or {}
    return {
        "name": r["heir"],
        "starter_name": r["name"],
        "pos": "RB",
        "team": r.get("team") or "",
        "age": heir.get("age") if heir.get("age") not in (None, "") else r.get("age"),
        "status": r.get("status") or "Active",
        "keep": r.get("heir_keep") or 0,
        "board": r.get("heir_board") or 0,
        "keep_val": r.get("heir_keep_val") or 0,
        "board_val": r.get("heir_board_val") or 0,
        "keep_pos": r.get("heir_keep_pos") or "RB",
        "board_pos": r.get("heir_board_pos") or "RB",
        "pos_label": r.get("heir_keep_pos") or r.get("heir_board_pos") or "RB",
        "starter_keep": r.get("keep") or 0,
        "starter_board": r.get("board") or 0,
        "starter_keep_val": r.get("keep_val") or 0,
        "starter_board_val": r.get("board_val") or 0,
        "starter_keep_pos": r.get("keep_pos") or "RB",
        "starter_board_pos": r.get("board_pos") or "RB",
        "hole": r.get("hole") or 0,
        "tag": r.get("tag") or "",
        "verdict": r.get("verdict") or "",
        "clock": r.get("tag") or "",
        "heir_clock": r.get("heir_clock") or "",
        "starter_clock": r.get("starter_clock") or "",
        "avg": abs(r.get("hole") or 0),
        "n": 2,
        "starter": r.get("starter"),
        "heir_side": heir,
        "behind": r.get("behind") or [],
    }


def dynasty_handcuffs(rooms):
    """Cuffs ranked for Superflex dynasty by the cuff's Keep value."""
    rows = [_cuff_view(r) for r in rooms]
    rows.sort(key=lambda r: (-r["keep_val"], r["keep"] or 999, r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def redraft_handcuffs(rooms):
    """Cuffs ranked for redraft by the cuff's Board value."""
    rows = [_cuff_view(r) for r in rooms]
    rows.sort(key=lambda r: (-r["board_val"], r["board"] or 999, r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def write_handcuff_lookup(rooms, media, updated):
    from build_site import face_src, slugify

    media = media or {}
    packed = []
    players = []
    for r in rooms:
        starter = r["starter"]
        heir = r["heir_side"]
        sid = slugify(starter["name"])
        hid = slugify(heir["name"])
        packed.append({
            "id": sid,
            "team": r["team"],
            "pos": "RB",
            "status": r["status"],
            "hole": r["hole"],
            "tag": r["tag"],
            "verdict": r["verdict"],
            "behind": r["behind"],
            "starter": {
                "id": sid,
                "name": starter["name"],
                "pos": "RB",
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
                "pos": "RB",
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
        })
        players.append({"id": sid, "name": starter["name"], "pos": "RB", "team": starter["team"], "role": "starter", "room": sid})
        players.append({"id": hid, "name": heir["name"], "pos": "RB", "team": heir["team"], "role": "heir", "room": sid})
    payload = {
        "updated": updated,
        "algorithm": ALGORITHM,
        "rooms": packed,
        "players": players,
        "samples": {"dynasty": SAMPLE_DYNASTY, "redraft": SAMPLE_REDRAFT},
    }
    (ROOT / "data/handcuff-lookup.json").write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))
    return payload


def _dynasty_extra(r):
    from build_site import esc, fmt_val
    return (
        f'<td>{esc(r["starter_name"])}</td>'
        f'<td class="desk-only">{esc(r["status"])}</td>'
        f'<td class="desk-only">{esc(r["keep_pos"])}</td>'
        f'<td class="desk-only">{esc(r["starter_keep_pos"])}</td>'
        f'<td class="c-val val">{fmt_val(r["keep_val"])}</td>'
        f'<td class="desk-only">{fmt_val(r["starter_keep_val"])}</td>'
        f'<td class="c-clock">{esc(r["tag"])}</td>'
    )


def _redraft_extra(r):
    from build_site import esc, fmt_val
    return (
        f'<td>{esc(r["starter_name"])}</td>'
        f'<td class="desk-only">{esc(r["status"])}</td>'
        f'<td class="desk-only">{esc(r["board_pos"])}</td>'
        f'<td class="desk-only">{esc(r["starter_board_pos"])}</td>'
        f'<td class="c-val val">{fmt_val(r["board_val"])}</td>'
        f'<td class="desk-only">{fmt_val(r["starter_board_val"])}</td>'
        f'<td class="c-clock">{esc(r["tag"])}</td>'
    )


def handcuff_tool_html():
    return """
    <section class="inherit-tool" id="handcuff-app" aria-label="Name the cuff">
      <p class="kicker">Running backs</p>
      <h2>Name a back. Read both lists.</h2>
      <p class="note">Search a starter or a backup. The left card is the listed starter. The right card is the handcuff. Dynasty uses Keep value. Redraft uses Board value. The middle card is what opens if the starter sits.</p>
      <div class="split-search">
        <label for="handcuff-q">Find a back</label>
        <input id="handcuff-q" data-q type="search" placeholder="McCaffrey, Gibbs, Love…" autocomplete="off" />
        <div class="trade-hits" data-hits></div>
        <div class="trade-add-btns">
          <button type="button" class="cta" data-open="1">Open the room</button>
          <button type="button" class="cta alt" data-sample="redraft">Sample redraft cuffs</button>
          <button type="button" class="cta ghost" data-sample="dynasty">Sample dynasty cuffs</button>
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
          <p class="kicker">If starter sits</p>
          <h3 data-hole-total>0</h3>
          <p data-verdict>Search a running back. The cuff stays dark until a name is in.</p>
          <p class="note" data-status></p>
        </article>
        <article class="split-clock board" data-heir>
          <p class="kicker">The cuff</p>
          <h3 data-heir-name>Next back</h3>
          <p class="split-total" data-heir-total>0</p>
          <p class="note" data-heir-meta>Keep and Board on the handcuff.</p>
        </article>
      </div>
      <ul class="split-room" data-line></ul>
    </section>
    """


def write_the_handcuff(b, keep, board, media):
    from build_site import UPDATED, rank_table

    rooms = handcuff_rooms(keep, board)
    write_handcuff_lookup(rooms, media, UPDATED)
    dynasty = dynasty_handcuffs(rooms)
    redraft = redraft_handcuffs(rooms)
    extra = also_on_desk(b.FB_ALSO.get("the-handcuff.html") or [])
    body = f"""
    <p class="kicker">RB handcuffs · {UPDATED}</p>
    <h1>The Handcuff</h1>
    <p class="note">Every other site prints one handcuff list and hopes dynasty rooms and redraft rooms can share it. They cannot. The Handcuff is running backs only. The dynasty board ranks the backup by Keep value. The redraft board ranks the same backup by Board value. {len(rooms)} listed backfields have a name behind the starter.</p>
    {handcuff_tool_html()}
    <p class="kicker" style="margin-top:28px">Dynasty</p>
    <h2>Dynasty cuffs, on The Keep.</h2>
    <p class="note">Sorted by the cuff's Keep value. The name on the left is the backup. The starter sits in Behind so you can see whose job he is next to.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(dynasty, ["Behind", "Status", "Cuff rank", "Starter rank", "Cuff value", "Starter value", "Read"], _dynasty_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    <p class="kicker" style="margin-top:28px">Redraft</p>
    <h2>Redraft cuffs, on The Board.</h2>
    <p class="note">Sorted by the cuff's Board value. The name on the left is the backup. Starter value is what the room already pays for the man in front of him.</p>
    <div class="panel">{rank_table(redraft, ["Behind", "Status", "Cuff rank", "Starter rank", "Cuff value", "Starter value", "Read"], _redraft_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    {b.sources_panel([
        ("The Keep", "the-keep.html", "Superflex dynasty Super Aggregate. The years clock."),
        ("The Board", "board.html", "Redraft PPR Super Aggregate. The Sunday clock."),
        ("Depth Charts", "depth-charts.html", "Sleeper RB order for 32 clubs."),
        ("Injuries", "injuries.html", "ESPN designations on the starter."),
        ("The Split", "the-split.html", "Two clocks on a room you type."),
    ], heading="Boards behind The Handcuff")}
    {faq_html(FAQ, heading="How The Handcuff is built.")}
    {extra}
    """
    js = '<script src="js/handcuff.js" defer></script>'
    b.write(
        "the-handcuff.html",
        b.page(
            "The Handcuff",
            "the-handcuff.html",
            body,
            extra_js=js,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("The Handcuff", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("The Handcuff", "https://ballkeep.com/the-handcuff.html"),
                ]),
                faq_jsonld(FAQ),
            ],
            body_class="inherit-page handcuff-page",
        ),
    )
    return rooms
