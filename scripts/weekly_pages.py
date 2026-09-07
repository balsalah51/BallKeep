"""Render Week N skill, ADP, waiver, injury, SOS, and start/sit pages."""
from __future__ import annotations

import json

from seo import (
    faq_html,
    faq_jsonld,
    rank_list_jsonld,
    rank_search_bar,
)
from weekly_kit import (
    ADP_SOURCES,
    DEPTH_SOURCES,
    INJURY_SOURCES,
    SOS_SOURCES,
    WAIVER_SOURCES,
    WEEKLY_FLEX_SOURCES,
    adp_rows,
    depth_rows,
    injury_rows,
    meta,
    sos_rows,
    start_sit_players,
    usage_for,
    week_num,
    weekly_board,
    weekly_check_bits,
    weekly_flex,
    weekly_sources,
    waiver_board,
)


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
    ("How is the weekly board built?", "Mean of every Week N board that ranked the name: FantasyPros ECR, RotoWire projections, FantasyPros projections, and 4for4. Unranked on a board is a skip, never a last-place dump."),
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
    waivers = waiver_board()
    injuries = injury_rows()
    depth = depth_rows()
    sos = sos_rows(nfl, week)
    check = weekly_check_bits(nfl)

    def weekly_table(rows, chips=""):
        return rank_table(
            rows,
            ["Avg", "Boards", "Proj", "Opp", "BK Value"],
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
        body = f"""
    <p class="kicker">{label} · {pos} · {len(src)} boards</p>
    <h1>Week {week} {pos}</h1>
    <p class="note">Weekly start/sit, not the season-long Board. Mean of {len(src)} published Week {week} boards. Unranked on a board is a skip. {lead} is 1.01. Proj is RotoWire PPR points.</p>
    {rank_search_bar()}
    <div class="panel">{weekly_table(rows)}</div>
    {sources_panel(src, heading="Boards in This Aggregate")}
    {faq_html(WEEKLY_FAQ, heading=f"How Week {week} {pos} is built.")}
    """
        write(path, board_page(
            f"Week {week} {pos}", path, body,
            extra_jsonld=[
                rank_list_jsonld(
                    f"Week {week} {pos} rankings",
                    f"https://ballkeep.com/{path}",
                    rows,
                    lambda r: f"https://ballkeep.com/weekly-{pos.lower()}.html",
                    description=f"Week {week} {pos} start/sit from four weekly boards.",
                ),
                faq_jsonld(WEEKLY_FAQ),
            ],
        ))

    chips, js = pos_filter("weekly-pos")
    flex_body = f"""
    <p class="kicker">{label} · skill · Flex plus positions</p>
    <h1>Weekly</h1>
    <p class="note">Week {week} start/sit. The table is PPR flex (RB/WR/TE). Quarterbacks, backs, receivers, and tight ends each have their own board. Proj is RotoWire PPR points. Unranked is a skip.</p>
    <div class="grid-3">
      <a class="tile" href="weekly-qb.html"><h3>Week {week} QB</h3><p>{(boards['QB'] or [{'name':''}])[0]['name']} is 1.01.</p></a>
      <a class="tile" href="weekly-rb.html"><h3>Week {week} RB</h3><p>{(boards['RB'] or [{'name':''}])[0]['name']} is 1.01.</p></a>
      <a class="tile" href="weekly-wr.html"><h3>Week {week} WR</h3><p>{(boards['WR'] or [{'name':''}])[0]['name']} is 1.01.</p></a>
      <a class="tile" href="weekly-te.html"><h3>Week {week} TE</h3><p>{(boards['TE'] or [{'name':''}])[0]['name']} is 1.01.</p></a>
      <a class="tile" href="start-sit.html"><h3>Start/Sit</h3><p>Compare two names on this week's mash.</p></a>
      <a class="tile" href="weekly-check.html"><h3>Weekly Check</h3><p>Monday and Tuesday digest.</p></a>
    </div>
    {rank_search_bar(chips)}
    <div class="panel">{weekly_table(flex)}</div>
    {sources_panel(WEEKLY_FLEX_SOURCES, heading="Boards in This Aggregate")}
    {faq_html(WEEKLY_FAQ, heading="How the weekly flex board is built.")}
    """
    write("weekly.html", board_page(
        "Weekly", "weekly.html", flex_body, js,
        extra_jsonld=[
            rank_list_jsonld(
                f"Week {week} flex rankings",
                "https://ballkeep.com/weekly.html",
                flex,
                lambda r: "https://ballkeep.com/weekly.html",
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

    # --- waiver ---
    w_chips, w_js = pos_filter("waiver-pos")
    w_faq = [
        ("Who makes this list?", "Week N ranks, minus names already rostered in most rooms (70% owned or ADP inside the top 50)."),
        ("Is this FAAB advice?", "No dollar bids. It is the weekly mash of names that are still likely sitting out there."),
    ]
    w_body = f"""
    <p class="kicker">{label} · adds</p>
    <h1>Waiver</h1>
    <p class="note">Football waiver and stash list. Same Week {week} boards, cut down to names that are not roster locks. Unranked on a board is a skip.</p>
    {rank_search_bar(w_chips)}
    <div class="panel">{weekly_table(waivers)}</div>
    {sources_panel(WAIVER_SOURCES, heading="How the waiver cut is made")}
    {faq_html(w_faq, heading="How the waiver list is built.")}
    """
    write("waiver.html", board_page("Waiver", "waiver.html", w_body, w_js, extra_jsonld=[faq_jsonld(w_faq)]))

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

    # --- SOS ---
    def sos_extra(r):
        match = ""
        if r.get("opp"):
            match = f'{r.get("prep") or "vs"} {r["opp"]}'
        return (
            f'<td class="desk-only">{r.get("avg", "")}</td>'
            f'<td class="desk-only">{r.get("n", "")}</td>'
            f'<td class="c-val val">{_esc(match)}</td>'
            f'<td class="desk-only">{r.get("opp_dst") or ""}</td>'
        )
    sos_faq = [
        ("What is the average?", "Mean season-DST rank of leftover opponents. A higher number means weaker leftover fantasy defenses, which is usually easier for skill players."),
        ("What is this week's opponent?", "The club on the 2026 slate this week, plus that club's season DST rank."),
    ]
    sos_body = f"""
    <p class="kicker">{label} · leftover slate</p>
    <h1>Strength of Schedule</h1>
    <p class="note">Remaining 2026 opponents scored against our season DST board. Sorted easiest leftover slate first. This week's opponent sits on the row.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(sos, ["Avg DST", "Games left", "This week", "Opp DST"], sos_extra)}</div>
    {sources_panel(SOS_SOURCES, heading="How SOS is built")}
    {faq_html(sos_faq, heading="How strength of schedule is built.")}
    """
    write("sos.html", board_page("Strength of Schedule", "sos.html", sos_body, extra_jsonld=[faq_jsonld(sos_faq)]))

    # --- start/sit ---
    payload = start_sit_players()
    options = "".join(
        f'<option value="{_esc(p["name"])}" data-pos="{_esc(p["pos"])}"></option>'
        for p in payload
    )
    sit_js = f"""<script>
    const WK = {json.dumps(payload)};
    const byName = Object.fromEntries(WK.map(p => [p.name.toLowerCase(), p]));
    function card(id, p) {{
      const el = document.getElementById(id);
      if (!p) {{ el.innerHTML = '<p class="note">Type a name on the weekly board.</p>'; return; }}
      const fpts = (p.fpts == null) ? '' : Number(p.fpts).toFixed(1);
      el.innerHTML = '<div class="sit-card"><h3>' + p.name + '</h3>'
        + '<p class="note">' + p.pos + ' · ' + p.team + (p.opp ? ' · ' + p.opp : '') + '</p>'
        + '<div class="facts"><div class="fact"><small>Week rank</small><strong>#' + p.week_rk + '</strong></div>'
        + '<div class="fact"><small>Avg</small><strong>' + p.avg + '</strong></div>'
        + '<div class="fact"><small>Boards</small><strong>' + p.n + '</strong></div>'
        + '<div class="fact"><small>Proj</small><strong>' + fpts + '</strong></div></div>'
        + (p.injury && p.injury !== 'ACTIVE' ? '<p class="note">Status: ' + p.injury + '</p>' : '')
        + '</div>';
    }}
    function pick(which) {{
      const raw = document.getElementById(which + '-in').value.trim().toLowerCase();
      return byName[raw] || null;
    }}
    function render() {{
      const a = pick('a'); const b = pick('b');
      card('sit-a', a); card('sit-b', b);
      const out = document.getElementById('sit-call');
      if (!a || !b) {{ out.textContent = 'Pick two names.'; return; }}
      if (a.name === b.name) {{ out.textContent = 'Pick two different names.'; return; }}
      let winner = a, loser = b, why = 'week rank';
      if (a.week_rk !== b.week_rk) {{
        winner = a.week_rk < b.week_rk ? a : b;
        loser = winner === a ? b : a;
        why = 'week rank';
      }} else if (a.fpts != null && b.fpts != null && a.fpts !== b.fpts) {{
        winner = a.fpts > b.fpts ? a : b;
        loser = winner === a ? b : a;
        why = 'projected points';
      }}
      out.textContent = winner.name + ' over ' + loser.name + ' on ' + why + '.';
    }}
    ['a','b'].forEach(id => {{
      const box = document.getElementById(id + '-in');
      if (box) box.addEventListener('input', render);
    }});
    render();
    </script>"""
    sit_body = f"""
    <p class="kicker">{label} · comparer</p>
    <h1>Start/Sit</h1>
    <p class="note">Type two names from this week's skill boards. The call uses week rank first, then projected points if the ranks tie. This is not your roster and it does not sync a league.</p>
    <div class="sit-pick">
      <label>Player A <input id="a-in" list="sit-names" autocomplete="off" /></label>
      <label>Player B <input id="b-in" list="sit-names" autocomplete="off" /></label>
    </div>
    <datalist id="sit-names">{options}</datalist>
    <p class="kicker" id="sit-call">Pick two names.</p>
    <div class="plusminus"><div id="sit-a"></div><div id="sit-b"></div></div>
    """
    write("start-sit.html", board_page("Start/Sit", "start-sit.html", sit_body, sit_js))

    # --- weekly check ---
    def tiles(rows, href):
        return "".join(
            f'<a class="tile" href="{href}"><h3>{_esc(r["name"])}</h3><p>{_esc(r.get("pos") or "")} · #{r["bk"]} · proj {r.get("fpts") or ""}</p></a>'
            for r in rows
        )
    starts_html = ""
    for pos in ("QB", "RB", "WR", "TE"):
        starts_html += f'<p class="kicker">Week {week} {pos}</p><div class="grid-3">{tiles(check["starts"][pos], f"weekly-{pos.lower()}.html")}</div>'
    w_html = tiles(check["waivers"], "waiver.html")
    inj_html = "".join(
        f'<a class="tile" href="injuries.html"><h3>{_esc(r["name"])}</h3><p>{_esc(r["status"])} · {_esc(r.get("pos") or "")}</p></a>'
        for r in check["injuries"]
    )
    easy = "".join(
        f'<a class="tile" href="sos.html"><h3>{_esc(r["name"])}</h3><p>Leftover DST avg {r["avg"]}</p></a>'
        for r in check["easiest"]
    )
    check_body = f"""
    <p class="kicker">{label} · Monday and Tuesday</p>
    <h1>Weekly Check</h1>
    <p class="note">The Monday and Tuesday refresh dumps starts, waiver names, new designations, and leftover schedules onto one page. The scrape runs those two mornings and rebuilds the site.</p>
    <div class="grid-3">
      <a class="tile" href="weekly.html"><h3>Weekly boards</h3><p>QB, RB, WR, TE, flex.</p></a>
      <a class="tile" href="start-sit.html"><h3>Start/Sit</h3><p>Compare two names.</p></a>
      <a class="tile" href="waiver.html"><h3>Waiver</h3><p>Adds that are not locks.</p></a>
      <a class="tile" href="injuries.html"><h3>Injuries</h3><p>ESPN designations.</p></a>
      <a class="tile" href="adp.html"><h3>ADP</h3><p>Board vs ESPN.</p></a>
      <a class="tile" href="sos.html"><h3>Strength of Schedule</h3><p>Leftover opponents.</p></a>
      <a class="tile" href="depth-charts.html"><h3>Depth Charts</h3><p>32 clubs.</p></a>
    </div>
    <h2>Starts</h2>
    {starts_html}
    <h2>Waiver names</h2>
    <div class="grid-3">{w_html}</div>
    <h2>Watch the report</h2>
    <div class="grid-3">{inj_html}</div>
    <h2>Easiest leftover slates</h2>
    <div class="grid-3">{easy}</div>
    """
    write("weekly-check.html", board_page("Weekly Check", "weekly-check.html", check_body))

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
        "sos": sos,
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
