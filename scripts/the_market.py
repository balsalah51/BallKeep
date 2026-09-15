"""The Market: buy-low and sell-high names after Week 1."""
from __future__ import annotations

from seo import faq_html, faq_jsonld, rank_search_bar

BUY = [
    {"name": "Puka Nacua", "pos": "WR", "team": "LAR", "why": "Seven points in Melbourne on a Thursday. The target tree is still his. Week 2 is the Giants at home. Buy the ugly opener while rooms are still staring at the 27-7."},
    {"name": "Drake Maye", "pos": "QB", "team": "NE", "why": "Three fourth-quarter picks in Seattle. The arm and the rushing still play. Pittsburgh visits in Week 2. Pay a discount, keep the long view."},
    {"name": "A.J. Brown", "pos": "WR", "team": "NE", "why": "High-ankle sprain, boot, three-to-four weeks. IR him if the league allows it. Contenders can buy the missed month."},
    {"name": "TreVeyon Henderson", "pos": "RB", "team": "NE", "why": "Missed the opener. The market already treated him like a ghost. The talent is still a Patriot backfield."},
    {"name": "Matthew Stafford", "pos": "QB", "team": "LAR", "why": "One half in Australia. Davante and Puka are still in the building. Monday night against the Giants is a cleaner stage."},
    {"name": "George Kittle", "pos": "TE", "team": "SF", "why": "Two catches, twelve yards, Achilles in the rearview. Shanahan metered him. That is a plan, and plans expire."},
    {"name": "Kyren Williams", "pos": "RB", "team": "LAR", "why": "The Melbourne box score is cold. The role is the same. Buy from someone who watched Thursday and closed the tab."},
    {"name": "Sam Darnold", "pos": "QB", "team": "SEA", "why": "Hip, out in Arizona. Lock starts. Superflex rooms can buy the weeks after the MRI."},
]

SELL = [
    {"name": "D'Andre Swift", "pos": "RB", "team": "CHI", "why": "Three scores and 124 yards in a 59-point game. Someone in your league now believes he is a top-five back. Take the overpay."},
    {"name": "Tyler Shough", "pos": "QB", "team": "NO", "why": "410 yards in a 21-0 hole. Superflex adds him. If a manager offers a real QB2 plus a pick, listen."},
    {"name": "Kyle Monangai", "pos": "RB", "team": "CHI", "why": "A 61-yard score on ten carries next to Swift. Fun tape. Fragile role. Sell the spike."},
    {"name": "Carson Wentz", "pos": "QB", "team": "MIN", "why": "A comeback in Green Bay already has people writing poems. The job is still a committee of circumstances."},
    {"name": "David Montgomery", "pos": "RB", "team": "HOU", "why": "Three scores in a loss to Buffalo. Houston will score again. The touchdown luck will calm down."},
    {"name": "Cairo Santos", "pos": "K", "team": "CHI", "why": "Every streamer list in the country just printed his name. If someone wants to trade a skill piece for a kicker, let them."},
]

FAQ = [
    ("What is The Market?", "A buy-low and sell-high board after Week 1. The names come from the opener, the waiver mash, and the rest-of-season lists."),
    ("Is this Hot 'n' Cold?", "Hot 'n' Cold is the dynasty tape. The Market is the week-after trade board. Both listen to the same Sunday."),
]


def _face(name):
    from pathlib import Path
    slug = _slug(name)
    root = Path(__file__).resolve().parents[1]
    for ext in ("jpg", "png"):
        rel = f"img/players/{slug}.{ext}"
        if (root / rel).exists():
            return (
                f'<img src="{rel}" alt="{name}" width="160" height="160" '
                f'loading="lazy" />'
            )
    return ""


def _cards(rows, kind):
    bits = []
    for r in rows:
        face = _face(r["name"])
        bits.append(
            f'<article class="tile {kind} market-card">'
            f"{face}"
            f'<p class="kicker">{r["pos"]} · {r["team"]}</p>'
            f'<h3><a href="players/{_slug(r["name"])}.html">{r["name"]}</a></h3>'
            f'<p>{r["why"]}</p>'
            f"</article>"
        )
    return "".join(bits)


def _slug(name):
    from build_site import slugify, PLAYER_PAGES, norm_name
    slug = PLAYER_PAGES.get(norm_name(name)) or slugify(name)
    return slug


def write_the_market(b):
    body = f"""
    <p class="kicker">2026 · After Week 1 · Buy low · Sell high</p>
    <h1>The Market</h1>
    <p class="note">The opener moves prices. Buy the names whose rooms overreacted to one ugly night. Sell the names whose rooms just watched a carnival. This sits next to <a href="hot-n-cold.html">Hot 'n' Cold</a> and <a href="trade.html">Trade</a>. Pictures live on the player pages. The recap lives on <a href="the-recap.html">The Recap</a>.</p>
    {rank_search_bar()}
    <div class="hc-grid">
      <section>
        <p class="kicker">Buy low</p>
        <h2>Pay the dip.</h2>
        <div class="grid-2 market-grid">{_cards(BUY, "hot")}</div>
      </section>
      <section>
        <p class="kicker">Sell high</p>
        <h2>Take the overpay.</h2>
        <div class="grid-2 market-grid">{_cards(SELL, "cold")}</div>
      </section>
    </div>
    {b.sources_panel([
        ("The Recap", "the-recap.html", "Full Week 1 essay and the sixteen scores."),
        ("Hot 'n' Cold", "hot-n-cold.html", "Dynasty buys and sells after the opener."),
        ("Week 2 Waivers", "waiver.html", "Coker, Black, Vele, Shough."),
        ("ESPN waiver wire", "https://www.espn.com/fantasy/football/story/_/page/FFWaiverWirePickUp-49939032/fantasy-football-waiver-wire-free-agent-pickups-nfl-week-2", "Shough, Black, Coker."),
        ("Reuters", "https://www.reuters.com/sports/nfl-roundup-bears-score-59-record-setting-week-1-win-over-panthers--flm-2026-09-14/", "Bears 59, Panthers 37."),
        ("Associated Press", "https://www.espn.com/nfl/recap?gameId=401872931", "Walker 173, Mahomes in the brace."),
    ], heading="Boards and reporting in this Market")}
    {faq_html(FAQ, heading="How The Market is built.")}
    """
    b.write("the-market.html", b.board_page(
        "The Market", "the-market.html", body,
        extra_jsonld=[faq_jsonld(FAQ)],
    ))
