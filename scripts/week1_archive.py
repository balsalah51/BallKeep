"""Park finished Week 1 weekly pages under archive/week1/."""
from __future__ import annotations

import re

from seo import also_on_desk, breadcrumbs, faq_html, faq_jsonld, rank_list_jsonld, rank_search_bar
from week1_boards import (
    MATCH_SOURCES,
    W1_DST_SOURCES,
    W1_K_SOURCES,
    week1_dst_board,
    week1_kicker_board,
    week1_matchups,
)
from weekly_analysis import opening_article_html
from weekly_kit import historic_waiver_board, historic_waiver_sources


ARCHIVE = "archive/week1"
DEPTH = 2


def deepen_html(html: str, depth: int = DEPTH) -> str:
    """Prefix root-relative src/href so archive pages can sit two folders down."""
    if depth <= 0:
        return html
    prefix = "../" * depth

    def repl(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://", "#", "mailto:", "/", "../")):
            return m.group(0)
        return f'{attr}="{prefix}{url}"'

    return re.sub(r'(src|href)="([^"]+)"', repl, html)


def write_redirect(b, old_path: str, new_path: str, title: str):
    b.write(old_path, f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta http-equiv="refresh" content="0;url={new_path}" />
  <link rel="canonical" href="https://ballkeep.com/{new_path}" />
  <title>{title} moved to the Week 1 archive | Ball Keep</title>
</head>
<body>
  <p>This Week 1 page lives in the <a href="{new_path}">archive</a>.</p>
</body>
</html>
""")


def _also():
    p = "../" * DEPTH
    return also_on_desk([
        (f"{p}the-recap.html", "The Recap", "The full Week 1 essay, written after Monday night."),
        (f"{p}weekly.html", "Week 2 Weekly", "This week's skill boards."),
        (f"{p}waiver.html", "Week 2 Waivers", "Coker, Black, and the names the opener moved."),
        ("index.html", "Week 1 archive", "Opening, DST, kickers, matchups, waivers."),
    ])


def write_week1_archive(b, media=None):
    media = media or {}
    write = b.write
    page = b.page
    rank_table = b.rank_table
    sources_panel = b.sources_panel
    matchup_table = b.matchup_table
    fmt_val = b.fmt_val
    slugify = b.slugify
    PLAYER_PAGES = b.PLAYER_PAGES

    w1_dst = week1_dst_board()
    w1_kickers = week1_kicker_board()
    w1_match = week1_matchups()
    waivers = historic_waiver_board(1)
    w_src = historic_waiver_sources(1)
    extra = _also()
    live = "../../"

    dst_lead = w1_dst[0]["name"] if w1_dst else "Jacksonville Jaguars"
    k_lead = w1_kickers[0]["name"] if w1_kickers else "Brandon Aubrey"
    w_lead = waivers[0]["name"] if waivers else "Mike Washington Jr."

    from build_site import W1_DST_FAQ, W1_K_FAQ, W1_MATCH_FAQ

    dst_body = f"""
    <p class="kicker">2026 Week 1 · archive · DST Super Aggregate · {len(W1_DST_SOURCES)} boards</p>
    <h1>Week 1 DST</h1>
    <p class="note">Finished Week 1 stream, parked after the opener. Super Aggregate of {len(W1_DST_SOURCES)} published Week 1 boards. {dst_lead} led the stream. Live start/sit lives on <a href="{live}week2-dst.html">Week 2 DST</a>.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(w1_dst, ["Super", "Boards", "BK Value"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="desk-only">{r["n"]}</td><td class="c-val val">{fmt_val(r["value"])}</td>', depth=DEPTH)}</div>
    {sources_panel(W1_DST_SOURCES, heading="Boards in This Super Aggregate")}
    {faq_html(W1_DST_FAQ, heading="How Week 1 DST was built.")}
    """ + extra
    write(f"{ARCHIVE}/dst.html", page(
        "Week 1 DST", f"{ARCHIVE}/dst.html", dst_body, depth=DEPTH,
        extra_jsonld=[
            rank_list_jsonld(
                "Week 1 2026 Fantasy Football DST Rankings",
                "https://ballkeep.com/archive/week1/dst.html",
                w1_dst,
                lambda r: "https://ballkeep.com/archive/week1/dst.html",
                description="Archived Week 1 DST Super Aggregate.",
            ),
            faq_jsonld(W1_DST_FAQ),
        ],
    ))

    k_body = f"""
    <p class="kicker">2026 Week 1 · archive · K Super Aggregate · {len(W1_K_SOURCES)} boards</p>
    <h1>Week 1 Kickers</h1>
    <p class="note">Finished Week 1 stream, parked after the opener. Super Aggregate of {len(W1_K_SOURCES)} published Week 1 boards. {k_lead} sat first among the kickers. Live start/sit lives on <a href="{live}week2-kickers.html">Week 2 Kickers</a>.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(w1_kickers, ["Super", "Boards", "BK Value"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="desk-only">{r["n"]}</td><td class="c-val val">{fmt_val(r["value"])}</td>', media=media, faces=True, depth=DEPTH)}</div>
    {sources_panel(W1_K_SOURCES, heading="Boards in This Super Aggregate")}
    {faq_html(W1_K_FAQ, heading="How Week 1 Kickers was built.")}
    """ + extra
    write(f"{ARCHIVE}/kickers.html", page(
        "Week 1 Kickers", f"{ARCHIVE}/kickers.html", k_body, depth=DEPTH,
        extra_jsonld=[
            rank_list_jsonld(
                "Week 1 2026 Fantasy Football Kicker Rankings",
                "https://ballkeep.com/archive/week1/kickers.html",
                w1_kickers,
                lambda r: f"https://ballkeep.com/players/{slugify(r['name'])}.html" if slugify(r["name"]) in PLAYER_PAGES.values() else "https://ballkeep.com/archive/week1/kickers.html",
                description="Archived Week 1 kicker Super Aggregate.",
            ),
            faq_jsonld(W1_K_FAQ),
        ],
    ))

    match_note = (
        f"Finished Week 1 win picks from {len(MATCH_SOURCES)} published sources: four CBS straight-up experts, "
        "BUSR scores, the current market, seven Action Network books, five 1-32 power boards, "
        "the May DraftKings opener, TeamRankings predictive, FOX Sports DraftKings from Sep 3, "
        "plus short published fades. Unpicked games on a board were skipped. The pick is the side "
        "with more votes. Away and Home are raw vote counts."
    )
    match_body = f"""
    <p class="kicker">2026 Week 1 · archive · Matchups · {len(MATCH_SOURCES)} sources</p>
    <h1>Week 1 Matchups</h1>
    <p class="note">{match_note} Live cards live on <a href="{live}week2-matchups.html">Week 2 Matchups</a>.</p>
    <div class="panel">{matchup_table(w1_match)}</div>
    {sources_panel(MATCH_SOURCES, heading="Boards in This Aggregate")}
    {faq_html(W1_MATCH_FAQ, heading="How Week 1 matchups were built.")}
    """ + extra
    write(f"{ARCHIVE}/matchups.html", page(
        "Week 1 Matchups", f"{ARCHIVE}/matchups.html", match_body, depth=DEPTH,
        extra_jsonld=[faq_jsonld(W1_MATCH_FAQ)],
    ))

    w_faq = [
        ("What is this list?", "The finished Week 1 Super Aggregate of published waiver articles before kickoff. A name needed two lists."),
        ("Where is this week's wire?", "Week 2 waivers live on the live waiver page. This shelf keeps the preseason mash."),
    ]
    w_body = f"""
    <p class="kicker">2026 Week 1 · archive · consensus waivers · {len(w_src)} lists</p>
    <h1>Week 1 Waivers</h1>
    <p class="note">Preseason consensus adds, parked after the opener. {len(w_src)} published pickup lists. {w_lead} led the mash. The live wire lives on <a href="{live}waiver.html">Week 2 Waivers</a>.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(waivers, ["Super", "Boards", "Proj", "Opp", "BK Value"], lambda r: f'<td class="desk-only">{r.get("avg", "")}</td><td class="desk-only">{r.get("n", "")}</td><td class="c-val val"></td><td class="desk-only"></td><td class="c-val val">{fmt_val(r.get("value") or 0)}</td>', media=media, faces=True, depth=DEPTH)}</div>
    {sources_panel(w_src, heading="Lists in This Super Aggregate")}
    {faq_html(w_faq, heading="How Week 1 Waivers was built.")}
    """ + extra
    write(f"{ARCHIVE}/waivers.html", page(
        "Week 1 Waivers", f"{ARCHIVE}/waivers.html", w_body, depth=DEPTH,
        extra_jsonld=[faq_jsonld(w_faq)],
    ))

    opening_body = deepen_html(opening_article_html()) + extra
    write(f"{ARCHIVE}/opening.html", page(
        "Week 1 Opening", f"{ARCHIVE}/opening.html", opening_body, depth=DEPTH,
        crumbs=breadcrumbs([
            ("Ball Keep", "../../index.html"),
            ("Week 1 archive", "index.html"),
            ("Opening", None),
        ]),
        image="img/players/jaxon-smith-njigba.jpg",
        body_class="opening-page",
        description="Hand analysis of the first two Week 1 games. Seahawks 13, Patriots 10. 49ers 27, Rams 7.",
    ))

    index_body = f"""
    <p class="kicker">2026 · Week 1 archive · sixteen scores in the book</p>
    <h1>Week 1 Archive</h1>
    <p class="note">The first week began on Wednesday in Seattle and closed on Monday in Kansas City. These pages keep the preseason waiver mash, the Week 1 DST and kicker streams, the opening essay from Friday, and the win-pick card as they stood before Week 2. The full story now lives on <a href="{live}the-recap.html">The Recap</a>. This week's ranks live on <a href="{live}weekly.html">Weekly</a>.</p>
    <div class="photo-row" aria-label="Faces from Week 1">
      <a href="{live}the-recap.html"><img src="{live}img/players/jaxon-smith-njigba.jpg" alt="Jaxon Smith-Njigba" width="320" height="320" /></a>
      <a href="{live}the-recap.html"><img src="{live}img/players/brock-purdy.jpg" alt="Brock Purdy" width="320" height="320" /></a>
      <a href="{live}the-recap.html"><img src="{live}img/players/caleb-williams.jpg" alt="Caleb Williams" width="320" height="320" /></a>
      <a href="{live}the-recap.html"><img src="{live}img/players/kenneth-walker.jpg" alt="Kenneth Walker" width="320" height="320" /></a>
    </div>
    <p class="photo-cap">Smith-Njigba, Purdy, Williams, Walker. The first week already has a cast, and the shelf still holds the first boards.</p>
    <div class="grid-3">
      <a class="tile" href="opening.html"><h3>Opening</h3><p>Friday essay after Seattle 13-10 and Melbourne 27-7.</p></a>
      <a class="tile" href="dst.html"><h3>Week 1 DST</h3><p>{dst_lead} led the stream.</p></a>
      <a class="tile" href="kickers.html"><h3>Week 1 Kickers</h3><p>{k_lead} sat first.</p></a>
      <a class="tile" href="matchups.html"><h3>Week 1 Matchups</h3><p>Win picks from {len(MATCH_SOURCES)} sources.</p></a>
      <a class="tile" href="waivers.html"><h3>Week 1 Waivers</h3><p>{w_lead} led the preseason mash.</p></a>
      <a class="tile" href="{live}the-recap.html"><h3>The Recap</h3><p>The full Week 1 essay, written after Monday night.</p></a>
    </div>
    """ + extra
    write(f"{ARCHIVE}/index.html", page(
        "Week 1 Archive", f"{ARCHIVE}/index.html", index_body, depth=DEPTH,
        crumbs=breadcrumbs([
            ("Ball Keep", "../../index.html"),
            ("Week 1 archive", None),
        ]),
        description="Archived Week 1 DST, kickers, matchups, opening essay, and preseason waivers.",
    ))

    write_redirect(b, "week1-dst.html", f"{ARCHIVE}/dst.html", "Week 1 DST")
    write_redirect(b, "week1-kickers.html", f"{ARCHIVE}/kickers.html", "Week 1 Kickers")
    write_redirect(b, "week1-matchups.html", f"{ARCHIVE}/matchups.html", "Week 1 Matchups")
    write_redirect(b, "week1-opening.html", f"{ARCHIVE}/opening.html", "Week 1 Opening")

    return {
        "dst": w1_dst,
        "kickers": w1_kickers,
        "match": w1_match,
        "waiver": waivers,
    }
