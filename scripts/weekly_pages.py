"""Render Week N skill, ADP, waiver, and injury pages."""
from __future__ import annotations

from pathlib import Path

from seo import (
    faq_html,
    faq_jsonld,
    rank_list_jsonld,
    rank_search_bar,
)
from weekly_analysis import opening_teaser, write_week1_opening
from weekly_kit import (
    ADP_SOURCES,
    DEPTH_SOURCES,
    INJURY_SOURCES,
    WEEK1_WAIVER_SOURCES,
    WEEKLY_FLEX_SOURCES,
    adp_rows,
    depth_rows,
    injury_rows,
    meta,
    usage_for,
    week_num,
    week1_waiver_board,
    weekly_board,
    weekly_flex,
    weekly_sources,
)

ROOT = Path(__file__).resolve().parents[1]


def _week_label():
    m = meta()
    return f"{m.get('season', 2026)} Week {m.get('week', 1)}"


def _fmt_val(r):
    v = r.get("value")
    try:
        return f"{int(v):,}"
    except (TypeError, ValueError):
        return ""


def _weekly_extra(r):
    fpts = r.get("fpts")
    fpts_txt = f"{float(fpts):.1f}" if isinstance(fpts, (int, float)) else ""
    return (
        f'<td class="desk-only">{r.get("avg", "")}</td>'
        f'<td class="desk-only">{r.get("n", "")}</td>'
        f'<td class="c-val val">{fpts_txt}</td>'
        f'<td class="desk-only">{_esc(r.get("opp") or "")}</td>'
        f'<td class="c-val val">{_fmt_val(r)}</td>'
    )


def _esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


WEEKLY_FAQ = [
    ("How is the weekly board built?", "Super Aggregate of every Week N board that ranked the name: 50% FantasyPros ECR, 50% RotoWire projections, FantasyPros projections, and 4for4."),
    ("What is the Proj column?", "RotoWire PPR points for this week, via Sleeper. Blank means that model skipped the name."),
    ("When does this refresh?", "A Monday and Tuesday job re-scrapes the public boards and rebuilds the pages."),
]


def write_weekly_pages(b, nfl, media, board_rows):
    write = b.write
    board_page = b.board_page
    rank_table = b.rank_table
    sources_panel = b.sources_panel
    pos_filter = b.pos_filter
    fmt_val = b.fmt_val  # noqa: F841
    page = b.page

    week = week_num()
    label = _week_label()
    flex = weekly_flex()
    boards = {pos: weekly_board(pos) for pos in ("QB", "RB", "WR", "TE")}
    adp = adp_rows(board_rows)
    waivers = week1_waiver_board()
    injuries = injury_rows()
    depth = depth_rows()

    def weekly_table(rows, chips=""):
        return rank_table(
            rows,
            ["Super", "Boards", "Proj", "Opp", "BK Value"],
            _weekly_extra,
            media=media,
            faces=True,
        )

    # --- position boards ---
    for pos, rows in boards.items():
        path = f"weekly-{pos.lower()}.html"
        chips, js = pos_filter(f"w{pos.lower()}-pos") if pos == "FLEX" else ("", "")
        src = weekly_sources(pos)
        lead = rows[0]["name"] if rows else ""
        chairs = {
            "QB": f"{lead} leads the quarterbacks.",
            "RB": f"{lead} opens the backfield.",
            "WR": f"{lead} sits first among receivers.",
            "TE": f"{lead} is the top tight end.",
        }
        body = f"""
    <p class="kicker">{label} · {pos} · {len(src)} boards</p>
    <h1>Week {week} {pos}</h1>
    <p class="note">This week's stream, not the season-long Board. Super Aggregate of {len(src)} published Week {week} boards. 50% FantasyPros ECR, 50% every other desk that ranked the name. {chairs.get(pos, lead + ' sits first.')} Proj is RotoWire PPR points.</p>
    {rank_search_bar()}
    <div class="panel">{weekly_table(rows)}</div>
    {sources_panel(src, heading="Boards in This Super Aggregate")}
    {faq_html(WEEKLY_FAQ, heading=f"How Week {week} {pos} is built.")}
    """
        write(path, board_page(
            f"Week {week} {pos}", path, body,
            extra_jsonld=[
                rank_list_jsonld(
                    f"Week {week} {pos} rankings",
                    f"https://ballkeep.com/{path}",
                    rows,
                    lambda r: f"https://ballkeep.com/players/{b.slugify(r['name'])}.html",
                    description=f"Week {week} {pos} start/sit from four weekly boards.",
                ),
                faq_jsonld(WEEKLY_FAQ),
            ],
        ))

    chips, js = pos_filter("weekly-pos")
    flex_body = f"""
    <p class="kicker">{label} · skill · Flex plus positions</p>
    <h1>Weekly</h1>
    <p class="note">Week {week} stream. Super Aggregate PPR flex (RB/WR/TE): 50% FantasyPros Flex ECR, 50% RotoWire projections. Quarterbacks, backs, receivers, and tight ends each have their own board. Proj is RotoWire PPR points.</p>
    {opening_teaser()}
    <div class="grid-3">
      <a class="tile" href="weekly-qb.html"><h3>Week {week} QB</h3><p>{(boards['QB'] or [{'name':''}])[0]['name']} leads the quarterbacks.</p></a>
      <a class="tile" href="weekly-rb.html"><h3>Week {week} RB</h3><p>{(boards['RB'] or [{'name':''}])[0]['name']} opens the backfield.</p></a>
      <a class="tile" href="weekly-wr.html"><h3>Week {week} WR</h3><p>{(boards['WR'] or [{'name':''}])[0]['name']} sits first among receivers.</p></a>
      <a class="tile" href="weekly-te.html"><h3>Week {week} TE</h3><p>{(boards['TE'] or [{'name':''}])[0]['name']} is the top tight end.</p></a>
      <a class="tile" href="waiver.html"><h3>Week 1 Waivers</h3><p>Preseason consensus adds.</p></a>
      <a class="tile" href="injuries.html"><h3>Injuries</h3><p>ESPN designations.</p></a>
    </div>
    {rank_search_bar(chips)}
    <div class="panel">{weekly_table(flex)}</div>
    {sources_panel(WEEKLY_FLEX_SOURCES, heading="Boards in This Super Aggregate")}
    {faq_html(WEEKLY_FAQ, heading="How the weekly flex board is built.")}
    """
    write("weekly.html", board_page(
        "Weekly", "weekly.html", flex_body, js,
        extra_jsonld=[
            rank_list_jsonld(
                f"Week {week} flex rankings",
                "https://ballkeep.com/weekly.html",
                flex,
                lambda r: f"https://ballkeep.com/players/{b.slugify(r['name'])}.html",
                description=f"Week {week} PPR flex from FantasyPros and RotoWire.",
            ),
            faq_jsonld(WEEKLY_FAQ),
        ],
    ))

    # --- ADP ---
    def adp_extra(r):
        return (
            f'<td class="desk-only">{r.get("board") or ""}</td>'
            f'<td class="desk-only">{r.get("espn_adp") if r.get("espn_adp") is not None else ""}</td>'
            f'<td class="desk-only">{r.get("ud_adp") if r.get("ud_adp") is not None else ""}</td>'
            f'<td class="c-val val">{r.get("delta") if r.get("delta") is not None else ""}</td>'
        )
    adp_faq = [
        ("What is Delta?", "ESPN ADP minus The Board rank. A plus means the room is drafting him later than we rank him."),
        ("Who is in this table?", "Anyone on The Board or with a public ESPN ADP. Kickers and DST stay off."),
    ]
    adp_chips, adp_js = pos_filter("adp-pos")
    adp_body = f"""
    <p class="kicker">{label} · The Board vs ADP</p>
    <h1>ADP</h1>
    <p class="note">The Board rank next to ESPN ADP and the Underdog/Sleeper ADP attached to RotoWire projections. Delta is ESPN ADP minus Board rank. Plus means value in the room.</p>
    {rank_search_bar(adp_chips)}
    <div class="panel">{rank_table(adp, ["Board", "ESPN ADP", "UD ADP", "Delta"], adp_extra, media=media, faces=True)}</div>
    {sources_panel(ADP_SOURCES, heading="Sources in This Table")}
    {faq_html(adp_faq, heading="How ADP vs The Board is built.")}
    """
    write("adp.html", board_page("ADP", "adp.html", adp_body, adp_js, extra_jsonld=[faq_jsonld(adp_faq)]))

    # --- Week 1 consensus waivers ---
    w_chips, w_js = pos_filter("waiver-pos")
    w_faq = [
        ("What is this list?", "A pre-Week 1 Super Aggregate of published waiver articles. Season has not started. A name needs two lists."),
        ("Is this FAAB advice?", "No dollar bids. Super Aggregate: 50% FantasyPros WW ECR, 50% every other desk that ranked the name."),
        ("Why is a drafted star missing?", "If a list did not put him on their waiver board, that list does not vote for him."),
    ]
    w_lead = waivers[0]["name"] if waivers else ""
    w_body = f"""
    <p class="kicker">{label} · consensus waivers · {len(WEEK1_WAIVER_SOURCES)} lists</p>
    <h1>Week 1 Waivers</h1>
    <p class="note">Preseason waiver Super Aggregate, before Week 1 kickoff. {len(WEEK1_WAIVER_SOURCES)} published pickup lists. 50% FantasyPros WW ECR, 50% every other desk that ranked the name. A name needs two lists. {w_lead} leads the mash. Kickers and team DST stay on their own Week 1 boards.</p>
    {rank_search_bar(w_chips)}
    <div class="panel">{weekly_table(waivers)}</div>
    {sources_panel(WEEK1_WAIVER_SOURCES, heading="Lists in This Super Aggregate")}
    {faq_html(w_faq, heading="How Week 1 Waivers is built.")}
    """
    write("waiver.html", board_page("Week 1 Waivers", "waiver.html", w_body, w_js, extra_jsonld=[faq_jsonld(w_faq)]))

    # --- injuries ---
    def inj_extra(r):
        return (
            f'<td class="c-val val">{_esc(r.get("status") or "")}</td>'
            f'<td class="desk-only">{_esc((r.get("note") or "")[:140])}</td>'
        )
    i_chips, i_js = pos_filter("inj-pos")
    i_body = f"""
    <p class="kicker">{label} · designations</p>
    <h1>Injuries</h1>
    <p class="note">Skill-position injury report from ESPN club tables. Out, Doubtful, Questionable, and injured reserve. Notes stay short.</p>
    {rank_search_bar(i_chips)}
    <div class="panel">{rank_table(injuries, ["Status", "Note"], inj_extra)}</div>
    {sources_panel(INJURY_SOURCES, heading="Source")}
    """
    write("injuries.html", board_page("Injuries", "injuries.html", i_body, i_js))

    # --- depth charts ---
    d_rows = []
    for i, t in enumerate(depth, 1):
        d_rows.append({
            "bk": i, "name": t["name"], "pos": "", "team": t["team"],
            "qb": t["qb"], "rb": t["rb"], "wr": t["wr"], "te": t["te"], "value": 0,
        })
    def depth_extra(r):
        return (
            f'<td class="desk-only">{_esc(r.get("qb") or "")}</td>'
            f'<td class="desk-only">{_esc(r.get("rb") or "")}</td>'
            f'<td class="desk-only">{_esc(r.get("wr") or "")}</td>'
            f'<td class="desk-only">{_esc(r.get("te") or "")}</td>'
        )
    d_body = f"""
    <p class="kicker">2026 · 32 clubs</p>
    <h1>Depth Charts</h1>
    <p class="note">Sleeper depth order for every club. First name in a cell is the listed starter.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(d_rows, ["QB", "RB", "WR", "TE"], depth_extra)}</div>
    {sources_panel(DEPTH_SOURCES, heading="Source")}
    """
    write("depth-charts.html", board_page("Depth Charts", "depth-charts.html", d_body))

    write_week1_opening(b)

    for rel in ("sos.html", "start-sit.html", "weekly-check.html"):
        old = ROOT / rel
        if old.exists():
            old.unlink()

    return {
        "week": week,
        "qb": boards["QB"],
        "rb": boards["RB"],
        "wr": boards["WR"],
        "te": boards["TE"],
        "flex": flex,
        "adp": adp,
        "waiver": waivers,
        "injuries": injuries,
    }


def usage_html(name: str) -> str:
    row = usage_for(name)
    if not row:
        return ""
    def cell(lab, val, fmt=None):
        if val in (None, ""):
            return ""
        if fmt == "pct":
            txt = f"{val:.1f}%"
        elif fmt == "pts":
            txt = f"{val:.1f}"
        elif isinstance(val, float) and val == int(val):
            txt = str(int(val))
        else:
            txt = str(val)
        return f'<div class="fact"><small>{lab}</small><strong>{txt}</strong></div>'
    bits = [
        cell("2025 snaps", row.get("off_snp")),
        cell("Snap %", row.get("snap_pct"), "pct"),
        cell("Targets", row.get("rec_tgt")),
        cell("Catches", row.get("rec")),
        cell("Rush att", row.get("rush_att")),
        cell("PPR pts", row.get("pts_ppr"), "pts"),
        cell("Games", row.get("gp")),
    ]
    bits = [x for x in bits if x]
    if not bits:
        return ""
    return (
        '<section class="panel usage">'
        '<p class="kicker">2025 usage</p>'
        "<h3>Snaps and targets</h3>"
        f'<div class="facts">{"".join(bits)}</div>'
        "</section>"
    )
