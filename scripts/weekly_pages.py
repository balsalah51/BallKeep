"""Render Week N skill, ADP, waiver, and injury pages."""
from __future__ import annotations

from pathlib import Path

from seo import (
    faq_html,
    faq_jsonld,
    rank_list_jsonld,
    rank_search_bar,
)
from the_market import write_the_market
from the_recap import recap_teaser, write_the_recap
from week4_predictions import predictions_teaser
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
    gamelog_bundle,
    gamelog_for,
    opponent_for,
    week_num,
    yearly_usage,
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
    <p class="note">This week's stream, not the season-long Board. Super Aggregate of {len(src)} published Week {week} boards. 50% FantasyPros ECR, 50% every other board that ranked the name. {chairs.get(pos, lead + ' sits first.')} Proj is RotoWire PPR points.</p>
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
                    description=f"Week {week} {pos} start/sit from FantasyPros ECR, RotoWire, and 4for4.",
                ),
                faq_jsonld(WEEKLY_FAQ),
            ],
        ))

    chips, js = pos_filter("weekly-pos")
    flex_body = f"""
    <p class="kicker">{label} · skill · Flex plus positions</p>
    <h1>Weekly</h1>
    <p class="note">Week {week} stream. Super Aggregate PPR flex (RB/WR/TE): 50% FantasyPros Flex ECR, 50% RotoWire projections. Quarterbacks, backs, receivers, and tight ends each have their own board. Proj is RotoWire PPR points. The opener lives on <a href="the-recap.html">The Recap</a>. The Week 4 card, with a pick on every line, lives on <a href="week4-matchups.html">Week 4 Predictions</a>. The finished Week 3 card sits on <a href="week3-matchups.html">Week 3 Predictions</a>.</p>
    {recap_teaser()}
    {predictions_teaser()}
    <div class="grid-3">
      <a class="tile" href="weekly-qb.html"><h3>Week {week} QB</h3><p>{(boards['QB'] or [{'name':''}])[0]['name']} leads the quarterbacks.</p></a>
      <a class="tile" href="weekly-rb.html"><h3>Week {week} RB</h3><p>{(boards['RB'] or [{'name':''}])[0]['name']} opens the backfield.</p></a>
      <a class="tile" href="weekly-wr.html"><h3>Week {week} WR</h3><p>{(boards['WR'] or [{'name':''}])[0]['name']} sits first among receivers.</p></a>
      <a class="tile" href="weekly-te.html"><h3>Week {week} TE</h3><p>{(boards['TE'] or [{'name':''}])[0]['name']} is the top tight end.</p></a>
      <a class="tile" href="waiver.html"><h3>Week {week} Waivers</h3><p>Allen, Gordon, Sadiq, and the names Week 3 moved.</p></a>
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

    # --- Week N consensus waivers ---
    w_chips, w_js = pos_filter("waiver-pos")
    w_faq = [
        ("What is this list?", f"A Week {week} Super Aggregate of published waiver articles after the third Sunday. A name needs two lists."),
        ("Is this FAAB advice?", "No dollar bids. Super Aggregate of every list that ranked the name."),
        ("Why is a drafted star missing?", "If a list did not put him on their waiver board, that list does not vote for him."),
    ]
    w_lead = waivers[0]["name"] if waivers else ""
    w_body = f"""
    <p class="kicker">{label} · consensus waivers · {len(WEEK1_WAIVER_SOURCES)} lists</p>
    <h1>Week {week} Waivers</h1>
    <p class="note">Week {week} waiver Super Aggregate after the third Sunday. {len(WEEK1_WAIVER_SOURCES)} published pickup lists. {w_lead} leads the mash. Kickers and team DST stay on their own Week {week} boards. The finished Week 3 card lives on <a href="week3-matchups.html">Week 3 Predictions</a>. Finished Week 1 boards sit in the <a href="archive/week1/index.html">Week 1 archive</a>.</p>
    {rank_search_bar(w_chips)}
    <div class="panel">{weekly_table(waivers)}</div>
    {sources_panel(WEEK1_WAIVER_SOURCES, heading="Lists in This Super Aggregate")}
    {faq_html(w_faq, heading=f"How Week {week} Waivers is built.")}
    """
    write("waiver.html", board_page(f"Week {week} Waivers", "waiver.html", w_body, w_js, extra_jsonld=[faq_jsonld(w_faq)]))

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

    write_the_recap(b)
    write_the_market(b)

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


def _stat_num(row, key) -> float:
    if not row:
        return 0.0
    val = row.get(key)
    if val in (None, ""):
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _fmt_int(val) -> str:
    if val is None:
        return "—"
    return f"{int(round(float(val))):,}"


def _fmt_pct(val) -> str:
    if val is None:
        return "—"
    return f"{float(val):.1f}%"


def _fmt_pts(val) -> str:
    if val is None:
        return "—"
    return f"{float(val):.1f}"


def _snap_pct(row) -> float | None:
    if not row:
        return None
    stored = row.get("snap_pct")
    if stored not in (None, ""):
        try:
            return float(stored)
        except (TypeError, ValueError):
            pass
    off = _stat_num(row, "off_snp")
    tm = _stat_num(row, "tm_off_snp")
    if off and tm:
        return round(100.0 * off / tm, 1)
    return None


def _line(row, qb: bool) -> dict:
    rush_att = _stat_num(row, "rush_att")
    rush_yd = _stat_num(row, "rush_yd")
    rush_td = _stat_num(row, "rush_td")
    rec = _stat_num(row, "rec")
    rec_yd = _stat_num(row, "rec_yd")
    rec_td = _stat_num(row, "rec_td")
    tgt = _stat_num(row, "rec_tgt")
    pass_yd = _stat_num(row, "pass_yd")
    pass_td = _stat_num(row, "pass_td")
    touches = rush_att + rec
    if qb:
        yards = pass_yd
        tds = pass_td + rush_td
    else:
        yards = rush_yd + rec_yd
        tds = rush_td + rec_td
    catch = round(100.0 * rec / tgt, 1) if tgt else None
    ypt = round(yards / touches, 1) if touches and not qb else None
    return {
        "gp": _stat_num(row, "gp"),
        "snap": _snap_pct(row),
        "touches": touches,
        "tgt": tgt,
        "rec": rec,
        "yards": yards,
        "tds": tds,
        "rush_att": rush_att,
        "rush_yd": rush_yd,
        "rush_td": rush_td,
        "rec_yd": rec_yd,
        "pass_cmp": _stat_num(row, "pass_cmp"),
        "pass_att": _stat_num(row, "pass_att"),
        "pass_yd": pass_yd,
        "pass_td": pass_td,
        "pass_int": _stat_num(row, "pass_int"),
        "catch": catch,
        "ypt": ypt,
        "ppr": 0.0 if row.get("pts_ppr") in (None, "") else row.get("pts_ppr"),
        "off_snp": _stat_num(row, "off_snp"),
        "tm_off_snp": _stat_num(row, "tm_off_snp"),
    }


def _fact(label: str, text: str) -> str:
    return f'<div class="fact"><small>{_esc(label)}</small><strong>{text}</strong></div>'


def _th(labels: list[str]) -> str:
    return "<tr>" + "".join(f"<th scope=\"col\">{_esc(lab)}</th>" for lab in labels) + "</tr>"


def _tds(vals: list[str], kind: str = "") -> str:
    cls = f' class="{kind}"' if kind else ""
    return f"<tr{cls}>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>"


def usage_html(name: str, pos: str = "") -> str:
    """Yearly totals and the 2026 game log, shown at the top of a player page."""
    seasons = yearly_usage(name)
    log = gamelog_for(name) or {}
    games = list(log.get("games") or [])
    if not seasons and not games:
        return ""

    bundle = gamelog_bundle()
    through = int(bundle.get("through_week") or 0)
    season_now = int(bundle.get("season") or 2026)
    by_year = {year: row for year, row in seasons}
    sample = by_year.get(season_now) or (seasons[0][1] if seasons else {})
    pos_u = (pos or log.get("pos") or (sample or {}).get("pos") or "").upper()
    qb = pos_u.startswith("QB")
    team = (log.get("team") or (by_year.get(season_now) or {}).get("team") or "").upper()

    headline_row = by_year.get(season_now)
    headline_year = season_now if headline_row else (seasons[0][0] if seasons else season_now)
    if not headline_row and seasons:
        headline_row = seasons[0][1]
    if not headline_row and games:
        headline_row = _sum_games(games)

    line = _line(headline_row or {}, qb)
    if qb:
        facts = [
            _fact("Pass yds", _fmt_int(line["pass_yd"])),
            _fact("Touches", _fmt_int(line["touches"])),
            _fact("Catches", _fmt_int(line["rec"])),
            _fact("Targets", _fmt_int(line["tgt"])),
            _fact("TDs", _fmt_int(line["tds"])),
            _fact("Snap %", _fmt_pct(line["snap"])),
            _fact("Cmp", _fmt_int(line["pass_cmp"])),
            _fact("Att", _fmt_int(line["pass_att"])),
            _fact("INT", _fmt_int(line["pass_int"])),
            _fact("Rush yds", _fmt_int(line["rush_yd"])),
            _fact("PPR", _fmt_pts(line["ppr"])),
            _fact("Games", _fmt_int(line["gp"] if headline_row and headline_row.get("gp") not in (None, "") else len(games))),
        ]
        head = ["Year", "G", "Snap %", "Cmp", "Att", "Pass yds", "Pass TD", "INT", "Rush", "RuYd", "RuTD", "PPR"]
        ghead = ["Wk", "Opp", "Snap %", "Cmp", "Att", "Pass yds", "Pass TD", "INT", "Rush", "RuYd", "RuTD", "PPR"]
    else:
        facts = [
            _fact("Yards", _fmt_int(line["yards"])),
            _fact("Touches", _fmt_int(line["touches"])),
            _fact("Catches", _fmt_int(line["rec"])),
            _fact("Targets", _fmt_int(line["tgt"])),
            _fact("TDs", _fmt_int(line["tds"])),
            _fact("Snap %", _fmt_pct(line["snap"])),
            _fact("Rush yds", _fmt_int(line["rush_yd"])),
            _fact("Rec yds", _fmt_int(line["rec_yd"])),
            _fact("Catch %", _fmt_pct(line["catch"])),
            _fact("Yds/touch", "—" if line["ypt"] is None else f"{line['ypt']:.1f}"),
            _fact("PPR", _fmt_pts(line["ppr"])),
            _fact("Games", _fmt_int(line["gp"] if headline_row and headline_row.get("gp") not in (None, "") else len(games))),
        ]
        head = ["Year", "G", "Snap %", "Touches", "Tgt", "Rec", "Yds", "TD", "Rush", "RuYd", "ReYd", "PPR"]
        ghead = ["Wk", "Opp", "Snap %", "Touches", "Tgt", "Rec", "Yds", "TD", "Rush", "RuYd", "ReYd", "PPR"]

    if headline_year == season_now and through:
        kicker = f"{headline_year} · through Week {through}"
    else:
        kicker = f"{headline_year} season"
    missing_now = ""
    if headline_year != season_now:
        missing_now = f'<p class="note">No {season_now} regular-season line yet.</p>'

    year_rows = []
    for year, row in seasons:
        year_rows.append(_tds([str(year)] + _count_cells(_line(row, qb), qb, games=True)))
    yearly = ""
    if year_rows:
        yearly = (
            "<h3>Yearly</h3>"
            '<div class="table-wrap"><table class="stat-log">'
            f"<thead>{_th(head)}</thead><tbody>{''.join(year_rows)}</tbody></table></div>"
        )

    game_rows = []
    played_rows = []
    by_week = {int(g.get("week") or 0): g for g in games}
    weeks = list(range(1, through + 1)) if through else sorted(by_week)
    for week in weeks:
        raw = by_week.get(week)
        ha, opp = opponent_for(team, week) if team else ("", "")
        opp_txt = f"{ha} {opp}".strip() if opp and opp != "BYE" else (opp or "—")
        if raw:
            played_rows.append(raw)
            if opp == "BYE":
                opp_txt = "—"
            game_rows.append(_tds([str(week), _esc(opp_txt)] + _count_cells(_line(raw, qb), qb, games=False)))
        elif opp == "BYE":
            game_rows.append(_tds([str(week), "BYE"] + ["—"] * (len(ghead) - 2), "bye"))
        elif team:
            game_rows.append(_tds([str(week), _esc(opp_txt or "—")] + ["—"] * (len(ghead) - 2), "dnp"))
    game_html = ""
    if game_rows:
        total = _sum_games(played_rows) if played_rows else None
        foot = ""
        if total:
            foot = "<tfoot>" + _tds(["", "Total"] + _count_cells(_line(total, qb), qb, games=False), "total") + "</tfoot>"
        game_html = (
            f"<h3>Game by game · {season_now}</h3>"
            '<div class="table-wrap"><table class="stat-log">'
            f"<thead>{_th(ghead)}</thead><tbody>{''.join(game_rows)}</tbody>{foot}</table></div>"
        )

    if qb:
        note = "Regular-season line from Sleeper. Touches are carries plus catches. TDs are passing plus rushing. Snap % is offensive snaps divided by team offensive snaps."
    else:
        note = "Regular-season line from Sleeper. Touches are carries plus catches. Yards are rushing plus receiving. Snap % is offensive snaps divided by team offensive snaps."
    return (
        '<section class="panel player-stats" id="player-stats">'
        f'<p class="kicker">{_esc(kicker)}</p>'
        "<h2>Counting stats</h2>"
        f"{missing_now}"
        f'<div class="facts stat-facts">{"".join(facts)}</div>'
        f"{yearly}{game_html}"
        f'<p class="note">{note}</p>'
        "</section>"
    )


def _count_cells(line: dict, qb: bool, games: bool) -> list[str]:
    g = _fmt_int(line["gp"]) if games else None
    snap = _fmt_pct(line["snap"])
    ppr = _fmt_pts(line["ppr"])
    if qb:
        body = [
            _fmt_int(line["pass_cmp"]),
            _fmt_int(line["pass_att"]),
            _fmt_int(line["pass_yd"]),
            _fmt_int(line["pass_td"]),
            _fmt_int(line["pass_int"]),
            _fmt_int(line["rush_att"]),
            _fmt_int(line["rush_yd"]),
            _fmt_int(line["rush_td"]),
            ppr,
        ]
    else:
        body = [
            _fmt_int(line["touches"]),
            _fmt_int(line["tgt"]),
            _fmt_int(line["rec"]),
            _fmt_int(line["yards"]),
            _fmt_int(line["tds"]),
            _fmt_int(line["rush_att"]),
            _fmt_int(line["rush_yd"]),
            _fmt_int(line["rec_yd"]),
            ppr,
        ]
    if games:
        return [g, snap, *body]
    return [snap, *body]


def _sum_games(games: list[dict]) -> dict:
    keys = (
        "gp", "off_snp", "tm_off_snp", "rec_tgt", "rec", "rec_yd", "rec_td",
        "rush_att", "rush_yd", "rush_td", "pass_cmp", "pass_att", "pass_yd",
        "pass_td", "pass_int", "pts_ppr",
    )
    out = {k: 0.0 for k in keys}
    out["gp"] = float(len(games))
    for g in games:
        for k in keys:
            if k == "gp":
                continue
            out[k] += _stat_num(g, k)
    if out["off_snp"] and out["tm_off_snp"]:
        out["snap_pct"] = round(100.0 * out["off_snp"] / out["tm_off_snp"], 1)
    out["pts_ppr"] = round(out["pts_ppr"], 1)
    return out
