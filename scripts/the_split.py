"""The Split: Keep clock vs Board clock, a window year, and the gap board.

No other public board prints both currencies on one name and then lets
you build a room to see which year that room is actually trying to win.
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

SAMPLE_NOW = [
    "Christian McCaffrey", "Derrick Henry", "Saquon Barkley",
    "Travis Kelce", "Davante Adams", "Joe Mixon",
]
SAMPLE_LATER = [
    "Drake Maye", "Ashton Jeanty", "Tetairoa McMillan",
    "Brock Bowers", "Caleb Williams", "Jeremiyah Love",
]

FAQ = [
    ("What is The Split?", "Two clocks on every name. The Keep is Superflex dynasty. The Board is redraft PPR. The gap is the argument. The room tool turns a set of names into a window year."),
    ("What is a window year?", "2026 means the room is paying for this season. 2028 means the room is paying for years. 2027 sits in the middle. Age and the two BK Values decide it."),
    ("What does a plus gap mean?", "Keep rank minus Board rank. A plus gap is a Sunday name: higher on The Board than on The Keep. A minus gap is a years name."),
    ("Is this a trade calculator?", "The trade calculators price one clock. The Split prices both clocks at once and then tells you which year the room is built for."),
]


def _norm(name: str) -> str:
    from build_site import norm_name
    return norm_name(name)


def split_rows(keep, board):
    """Names on both clocks, sorted by the size of the disagreement."""
    keep_m = {_norm(r.get("name")): r for r in (keep or []) if r.get("name")}
    rows = []
    for b in board or []:
        name = b.get("name") or ""
        k = keep_m.get(_norm(name))
        if not k:
            continue
        keep_rk = int(k.get("bk") or 0)
        board_rk = int(b.get("bk") or 0)
        if keep_rk <= 0 or board_rk <= 0:
            continue
        gap = keep_rk - board_rk
        if gap >= SUNDAY_GAP:
            clock = "Sunday"
        elif gap <= YEARS_GAP:
            clock = "Years"
        else:
            clock = "Even"
        rows.append({
            "name": name,
            "pos": b.get("pos") or k.get("pos") or "",
            "team": b.get("team") or k.get("team") or "",
            "age": k.get("age") if k.get("age") not in (None, "") else b.get("age"),
            "keep": keep_rk,
            "board": board_rk,
            "gap": gap,
            "abs_gap": abs(gap),
            "keep_val": int(k.get("value") or bk_value(keep_rk)),
            "board_val": int(b.get("value") or bk_value(board_rk)),
            "keep_pos": k.get("pos_label") or k.get("pos") or "",
            "board_pos": b.get("pos_label") or b.get("pos") or "",
            "pos_label": k.get("pos_label") or b.get("pos_label") or b.get("pos") or k.get("pos") or "",
            "clock": clock,
            "avg": abs(gap),
            "n": 2,
        })
    rows.sort(key=lambda r: (-r["abs_gap"], r["keep"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def room_window(players):
    """Turn a set of names into a window year from both clocks and age."""
    if not players:
        return {
            "year": None,
            "verdict": "Add names from the search. The two clocks stay dark until a room is in.",
            "keep_val": 0,
            "board_val": 0,
            "avg_age": None,
            "board_share": None,
            "score": None,
        }
    kv = sum(int(p.get("keep_val") or 0) for p in players)
    bv = sum(int(p.get("board_val") or 0) for p in players)
    ages = []
    for p in players:
        age = p.get("age")
        if age in (None, ""):
            continue
        try:
            ages.append(float(age))
        except (TypeError, ValueError):
            continue
    avg_age = (sum(ages) / len(ages)) if ages else None
    total = kv + bv
    board_share = (bv / total) if total else 0.5
    age_term = 0.0
    if avg_age is not None:
        age_term = (avg_age - 25.5) / 8.0
    score = (board_share - 0.5) * 2.2 + age_term
    if score >= 0.28:
        year = 2026
        verdict = "This room is trying to win 2026."
    elif score <= -0.28:
        year = 2028
        verdict = "This room is built for 2028."
    else:
        year = 2027
        verdict = "This room can win soon and still has years."
    return {
        "year": year,
        "verdict": verdict,
        "keep_val": kv,
        "board_val": bv,
        "avg_age": round(avg_age, 1) if avg_age is not None else None,
        "board_share": round(board_share, 3),
        "score": round(score, 3),
    }


def _pack(r, slug, image):
    return {
        "id": slug or _norm(r["name"]),
        "name": r["name"],
        "pos": r.get("pos") or "",
        "team": r.get("team") or "",
        "age": r.get("age") if r.get("age") not in (None, "") else None,
        "keep": r["keep"],
        "board": r["board"],
        "keep_val": r["keep_val"],
        "board_val": r["board_val"],
        "keep_pos": r.get("keep_pos") or "",
        "board_pos": r.get("board_pos") or "",
        "clock": r.get("clock") or "",
        "slug": slug or "",
        "image": image or "",
    }


def write_split_lookup(rows, media, updated):
    from build_site import face_src, slugify

    media = media or {}
    players = []
    for r in rows:
        slug = slugify(r["name"])
        image = face_src(r, media)
        players.append(_pack(r, slug, image))
    payload = {
        "updated": updated,
        "algorithm": ALGORITHM,
        "players": players,
        "samples": {
            "now": SAMPLE_NOW,
            "later": SAMPLE_LATER,
        },
    }
    dest = ROOT / "data/split-lookup.json"
    dest.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))
    return payload


def _split_extra(r):
    from build_site import esc, fmt_val
    gap = r["gap"]
    gap_txt = f"+{gap}" if gap > 0 else str(gap)
    return (
        f'<td class="desk-only">{r["keep_pos"] or r.get("pos") or ""}</td>'
        f'<td class="desk-only">{r["board_pos"] or r.get("pos") or ""}</td>'
        f'<td class="desk-only">{r["keep"]}</td>'
        f'<td class="desk-only">{r["board"]}</td>'
        f'<td class="c-val val">{esc(gap_txt)}</td>'
        f'<td class="desk-only">{fmt_val(r["keep_val"])}</td>'
        f'<td class="c-val val">{fmt_val(r["board_val"])}</td>'
        f'<td class="c-clock">{esc(r["clock"])}</td>'
    )


def split_tool_html():
    return """
    <section class="split-tool" id="split-app" aria-label="Build a room">
      <p class="kicker">Your room</p>
      <h2>Put names on both clocks.</h2>
      <p class="note">Search a name. Add it to the room. The Keep total is dynasty money. The Board total is this-year money. The window year is the sentence those two clocks write together.</p>
      <div class="split-search">
        <label for="split-q">Find a name</label>
        <input id="split-q" data-q type="search" placeholder="Allen, Gibbs, Maye…" autocomplete="off" />
        <div class="trade-hits" data-hits></div>
        <div class="trade-add-btns">
          <button type="button" class="cta" data-add="1">Add to room</button>
          <button type="button" class="cta alt" data-sample="now">Sample 2026 room</button>
          <button type="button" class="cta ghost" data-sample="later">Sample 2028 room</button>
          <button type="button" class="trade-clear" data-clear="1">Clear</button>
        </div>
      </div>
      <div class="split-clocks">
        <article class="split-clock keep">
          <p class="kicker">The Keep</p>
          <h3>Years</h3>
          <p class="split-total" data-keep-total>0</p>
          <p class="note">Superflex dynasty BK Value</p>
        </article>
        <article class="split-clock board">
          <p class="kicker">The Board</p>
          <h3>Sunday</h3>
          <p class="split-total" data-board-total>0</p>
          <p class="note">Redraft PPR BK Value</p>
        </article>
        <article class="split-clock window" data-window>
          <p class="kicker">Window</p>
          <h3 data-year>Year</h3>
          <p data-verdict>Add names from the search. The two clocks stay dark until a room is in.</p>
          <p class="note" data-meta></p>
        </article>
      </div>
      <ul class="split-room" data-room></ul>
    </section>
    """


def write_the_split(b, keep, board, media):
    from build_site import UPDATED, rank_table

    rows = split_rows(keep, board)
    write_split_lookup(rows, media, UPDATED)
    extra = also_on_desk(b.FB_ALSO.get("the-split.html") or [])
    sunday_n = sum(1 for r in rows if r["clock"] == "Sunday")
    years_n = sum(1 for r in rows if r["clock"] == "Years")
    body = f"""
    <p class="kicker">Two clocks · {UPDATED}</p>
    <h1>The Split</h1>
    <p class="note">Every other site gives you one number. Dynasty rooms live on two clocks at once: the years you paid for on The Keep, and the Sundays you have to start on The Board. The Split prints both, prices both, and then lets you build a room so you can see which year that room is actually trying to win. {len(rows)} names sit on both boards. {sunday_n} lean Sunday. {years_n} lean years.</p>
    {split_tool_html()}
    <p class="kicker" style="margin-top:28px">The gap board</p>
    <h2>Where the clocks disagree.</h2>
    <p class="note">Sorted by the size of the gap. A plus gap is Keep rank minus Board rank, a Sunday name. A minus gap is a years name. Chairs stay on both clocks. Sort and find a player the usual way.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(rows, ["Keep chair", "Board chair", "Keep", "Board", "Gap", "Keep $", "Board $", "Clock"], _split_extra, media=media, faces=True, show_age=True, overwrite_pos=False)}</div>
    {b.sources_panel([
        ("The Keep", "the-keep.html", "Superflex dynasty Super Aggregate. The years clock."),
        ("The Board", "board.html", "Redraft PPR Super Aggregate. The Sunday clock."),
        ("Two Clocks", "two-clocks.html", "The essay that belongs with this page."),
        ("The Method", "the-method.html", "Half the vote is the long boards. Rank 1 is 12,000."),
        ("Trade", "trade.html", "Price one clock when the deal is already in front of you."),
    ], heading="Boards behind The Split")}
    {faq_html(FAQ, heading="How The Split is built.")}
    {extra}
    """
    js = '<script src="js/split.js" defer></script>'
    b.write(
        "the-split.html",
        b.page(
            "The Split",
            "the-split.html",
            body,
            extra_js=js,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("The Split", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("The Split", "https://ballkeep.com/the-split.html"),
                ]),
                faq_jsonld(FAQ),
            ],
            body_class="split-page",
        ),
    )
    return rows
