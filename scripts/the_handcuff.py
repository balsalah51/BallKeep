"""The Handcuff: RB-only next men, ranked once for dynasty and once for redraft.

Every other site publishes one handcuff list. Dynasty rooms and Sunday rooms
need two. The cuff is the name on the board. The starter is the chair behind him.
"""
from __future__ import annotations

import json
from pathlib import Path

from seo import (
    also_on_desk,
    breadcrumb_jsonld,
    breadcrumbs,
    faq_html,
    faq_jsonld,
    rank_search_bar,
)
from the_inheritance import inherit_rows, write_inherit_lookup

ROOT = Path(__file__).resolve().parents[1]

STARTER_KEEP_SHARE = 0.12

SAMPLE_DYNASTY = [
    "Jeremiyah Love", "Ashton Jeanty", "Bijan Robinson",
    "Jahmyr Gibbs", "Breece Hall",
]
SAMPLE_REDRAFT = [
    "Christian McCaffrey", "Saquon Barkley", "Derrick Henry",
    "Jonathan Taylor", "Josh Jacobs",
]

FAQ = [
    ("What is The Handcuff?", "Running backs only. The listed cuff is the Sleeper name behind the starter. Dynasty ranks him by Keep money. Redraft ranks him by the Sunday hole that opens if the starter sits."),
    ("Why two lists?", "A cuff behind Christian McCaffrey is a redraft add. A cuff behind a young Keep back is a years stash. One list makes those rooms fight. Two lists let both rooms be right."),
    ("What is the dynasty score?", "The cuff's Keep BK Value plus a slice of the starter's Keep BK Value. A dart behind Bijan outranks a dart behind a late back."),
    ("Is this The Inheritance?", "The Inheritance prices every chair. The Handcuff is the running back room, ranked once for years and once for Sunday."),
]


def handcuff_rooms(keep, board, depth=None, injuries=None):
    """RB starter/heir rooms from The Inheritance math."""
    rows = inherit_rows(keep, board, depth=depth, injuries=injuries)
    return [r for r in rows if (r.get("pos") or "").upper() == "RB"]


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
        "dynasty_score": int(r.get("heir_keep_val") or 0) + int((r.get("keep_val") or 0) * STARTER_KEEP_SHARE),
        "avg": abs(r.get("hole") or 0),
        "n": 2,
        "starter": r.get("starter"),
        "heir_side": heir,
        "behind": r.get("behind") or [],
    }


def dynasty_handcuffs(rooms):
    """Cuffs ranked for Superflex dynasty: Keep money on the cuff and the chair."""
    rows = [_cuff_view(r) for r in rooms]
    rows.sort(key=lambda r: (-r["dynasty_score"], r["keep"] or 999, r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def redraft_handcuffs(rooms):
    """Cuffs ranked for redraft: fattest Sunday hole first."""
    rows = [_cuff_view(r) for r in rooms]
    rows.sort(key=lambda r: (-r["hole"], -r["board_val"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def write_handcuff_lookup(rooms, media, updated):
    return write_inherit_lookup(
        rooms,
        media,
        updated,
        dest=ROOT / "data/handcuff-lookup.json",
        samples={"dynasty": SAMPLE_DYNASTY, "redraft": SAMPLE_REDRAFT},
    )


def _dynasty_extra(r):
    from build_site import esc, fmt_val
    return (
        f'<td>{esc(r["starter_name"])}</td>'
        f'<td class="desk-only">{esc(r["status"])}</td>'
        f'<td class="desk-only">{esc(r["keep_pos"])}</td>'
        f'<td class="desk-only">{esc(r["starter_keep_pos"])}</td>'
        f'<td class="c-val val">{fmt_val(r["keep_val"])}</td>'
        f'<td class="desk-only">{fmt_val(r["starter_keep_val"])}</td>'
        f'<td class="c-val val">{fmt_val(r["dynasty_score"])}</td>'
        f'<td class="c-clock">{esc(r["tag"])}</td>'
    )


def _redraft_extra(r):
    from build_site import esc, fmt_val
    hole = r["hole"]
    hole_txt = f"+{hole}" if hole > 0 else str(hole)
    return (
        f'<td>{esc(r["starter_name"])}</td>'
        f'<td class="desk-only">{esc(r["status"])}</td>'
        f'<td class="desk-only">{esc(r["board_pos"])}</td>'
        f'<td class="desk-only">{esc(r["starter_board_pos"])}</td>'
        f'<td class="c-val val">{fmt_val(r["board_val"])}</td>'
        f'<td class="c-val val">{esc(hole_txt)}</td>'
        f'<td class="c-clock">{esc(r["tag"])}</td>'
    )


def handcuff_tool_html():
    return """
    <section class="inherit-tool" id="handcuff-app" aria-label="Name the cuff">
      <p class="kicker">Running backs</p>
      <h2>Name a back. Read both lists.</h2>
      <p class="note">Search a starter or a cuff. The left clock is the listed starter. The right clock is the handcuff. Dynasty money lives on The Keep. Sunday money lives on The Board. The hole is what leaves the room if the starter sits.</p>
      <div class="split-search">
        <label for="handcuff-q">Find a back</label>
        <input id="handcuff-q" data-q type="search" placeholder="McCaffrey, Gibbs, Love…" autocomplete="off" />
        <div class="trade-hits" data-hits></div>
        <div class="trade-add-btns">
          <button type="button" class="cta" data-open="1">Open the room</button>
          <button type="button" class="cta alt" data-sample="redraft">Sample Sunday cuffs</button>
          <button type="button" class="cta ghost" data-sample="dynasty">Sample years cuffs</button>
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
    <p class="note">Every other site prints one handcuff list and hopes dynasty rooms and redraft rooms can share it. They cannot. The Handcuff is running backs only. The dynasty board ranks the cuff by Keep money. The redraft board ranks the same rooms by the Sunday hole. {len(rooms)} listed backfields have a name behind the starter.</p>
    {handcuff_tool_html()}
    <p class="kicker" style="margin-top:28px">Dynasty</p>
    <h2>Years cuffs, on The Keep.</h2>
    <p class="note">Sorted by the cuff's Keep BK Value plus a slice of the starter's Keep chair. A dart behind a Keep RB1 outranks a dart behind a late back. The name on the left is the cuff.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(dynasty, ["Starter", "Status", "Cuff chair", "Starter chair", "Cuff $", "Starter $", "Score", "Call"], _dynasty_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    <p class="kicker" style="margin-top:28px">Redraft</p>
    <h2>Sunday cuffs, on The Board.</h2>
    <p class="note">Sorted by the hole: starter Board money minus cuff Board money. A fat hole is a redraft add. A covered chair is already priced. The name on the left is the cuff.</p>
    <div class="panel">{rank_table(redraft, ["Starter", "Status", "Cuff chair", "Starter chair", "Cuff $", "Hole", "Call"], _redraft_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    {b.sources_panel([
        ("The Inheritance", "the-inheritance.html", "Every position. The hole on any starter."),
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
