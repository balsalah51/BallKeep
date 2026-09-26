"""The Method: how Ball Keep builds Super Aggregates, BK Value, and the boards."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
    faq_html,
    faq_jsonld,
)

HEADLINE = "How Ball Keep ranks a name, prices a trade, and keeps the boards honest."
DEK = (
    "Half the vote is the long boards. Half is every other list that ranked the name. "
    "Rank 1 is 12,000 BK Value. Fair is within 8%. This is the full method, written "
    "so you can read a rank the way a room should."
)
PUBLISHED = "2026-09-16T18:30:00Z"
OG_IMAGE = "img/players/josh-allen.png"

METHOD_FAQ = [
    (
        "What is a Super Aggregate?",
        "Half the vote is the long boards, the tapes that go hundreds of names deep. "
        "Half is every other published list that ranked that player.",
    ),
    (
        "What happens when a short list leaves a name off?",
        "That list stays silent on him. The long-core mean still holds the chair. "
        "A short board only moves the names it printed.",
    ),
    (
        "What is BK Value?",
        "Rank 1 is 12,000. The curve decays so a late first still holds about half "
        "of the 1.01, and rank 80 still holds about 29%. Fair is within 8%.",
    ),
    (
        "Which lists are rest of season?",
        "The Keep, The Board, Superflex, Classic, Standard, Best Ball, Rookies, "
        "Top Defenses, Top Kickers, and The Fence. Week 2 boards, Weekly, Waivers, "
        "and Predictions are this week's stream.",
    ),
    (
        "Where do the pictures and news come from?",
        "Player files carry ESPN headshots and 2025 tape. BK News clusters injury, "
        "roster, and coach reports every hour from RSS, Google News, X, and YouTube.",
    ),
    (
        "How do I write the site?",
        "Open an issue on the Ball Keep GitHub, or put the Discord bot in a server "
        "and talk to the boards there.",
    ),
]


def _shot(slug, ext, name):
    return (
        f'<a href="players/{slug}.html">'
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="160" height="160" loading="lazy" /></a>'
    )


def method_article_html() -> str:
    faces = (
        '<div class="home-faces method-faces" aria-label="Faces from the boards">'
        + _shot("josh-allen", "png", "Josh Allen")
        + _shot("jamarr-chase", "jpg", "Ja'Marr Chase")
        + _shot("bijan-robinson", "jpg", "Bijan Robinson")
        + _shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")
        + _shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")
        + _shot("puka-nacua", "jpg", "Puka Nacua")
        + _shot("caleb-williams", "jpg", "Caleb Williams")
        + _shot("patrick-mahomes", "png", "Patrick Mahomes")
        + "</div>"
    )
    return f"""
    <article class="method-article">
      <p class="kicker">The Method</p>
      <h1>How the Super Aggregate works.</h1>
      <p class="method-dek">{DEK}</p>
      {faces}
      <section class="method-grafs">
        <p>Ball Keep is a house of boards. The Keep is Superflex dynasty, top 400, forty tapes. The Board is redraft PPR for this year. The Fence mixes Superflex skill names with IDP. BaseKeep, BasketKeep, and PitchKeep use the same curve in their own colors. Every list on this site can tell you who voted and how the mash was built.</p>
        <p>A Super Aggregate is a split vote. Half belongs to the long boards, the published tapes that actually go 300, 400, 500 names deep. The other half belongs to every other list that ranked that player. A short board still moves the names it printed. A name a short list never published keeps the long-core mean. That is how a 40-board mash stays honest when half the industry only ranks 80 people.</p>
        <p>On The Keep the long core is Pro Football Network, Dynasty Nerds, FantasyPros Superflex ECR, and KeepTradeCut. On The Board the long core is Field Yates, FantasyPros PPR ECR, and Eric Karabell. Weekly skill boards give half the chair to FantasyPros ECR. DST and kickers name their own long cores on the page. Each board prints the catalog at the bottom so you can walk the votes yourself.</p>
      </section>
      <section class="method-split" aria-label="The split vote">
        <article>
          <p class="kicker">Long core</p>
          <h2>Half the chair.</h2>
          <p>The long tapes go deep enough that a late-round name still has a rank. Their mean is 50% of Super. If only the long boards ranked him, Super is that mean. He still has to appear on at least one long-core list to sit on The Keep.</p>
        </article>
        <article>
          <p class="kicker">The rest</p>
          <h2>The other half.</h2>
          <p>Short lists, public overlays, and specialist boards vote on the names they published. A Derek Brown rank moves Ja'Marr Chase. It stays quiet on a taxi-squad dart he never wrote down. That silence is the point.</p>
        </article>
      </section>
      <section class="method-grafs">
        <h2>BK Value</h2>
        <p>Every rank becomes a number. Rank 1 is 12,000. The curve decays on purpose: the drop from 1 to 2 is larger than the drop from 50 to 51. A late first, around rank 28, holds about half of the 1.01. Rank 80 still holds about 29%. Trade math is addition. Two sides are fair when they sit within 8%.</p>
        <p>Superflex keeps quarterback price. The 1QB calculator taxes passers to 38% of that number. PPR, Classic, and Standard calculators read their own boards. Same curve. Separate chairs.</p>
        <h2>Rest of season and this week</h2>
        <p>The Keep, The Board, Redraft Superflex, The Classic, Standard, Best Ball, Rookies, Top Defenses, Top Kickers, and The Fence are rest-of-season values. Week 2 Weekly, DST, Kickers, Predictions, and Waivers are this week's stream. The Recap is the finished Week 1 essay. The Market is the buy-low and sell-high board after the opener. Finished Week 1 lists live in the archive.</p>
        <h2>How to read a board</h2>
        <p>Find a player sits above every rank table. Position chips filter the list. A face next to a name opens the player file: Keep rank, Board rank, BK Value, 2025 tape, and the news that named him. Sources sit under the table. The FAQ on each page says which tapes got the long-core half.</p>
        <p>The Split sits next to Trade. Type the names you actually roster and it prints Keep money, Board money, and the year that room is trying to win. The Inheritance sits next to the report. Search a starter and it prices the man behind him on both clocks, then prints the Sunday hole. The Handcuff is the running back room only: one list for Keep money, one list for the Sunday hole. Week 2 Predictions is a vote mash of published sides, written as an essay with a pick on every line. The Market and Hot 'n' Cold are editorial boards tied to the ranks. They argue. The mash still holds the chair on the big lists. The Next Chair, Two Clocks, and The Long Game, on Articles, are the Superflex essays for the years after one loud week.</p>
      </section>
      <section class="method-map" aria-label="The boards">
        <p class="kicker">The house</p>
        <h2>Where each list lives.</h2>
        <div class="grid-3">
          <a class="tile" href="the-keep.html"><h3>The Keep</h3><p>Superflex dynasty, top 400, 40 boards.</p></a>
          <a class="tile" href="board.html"><h3>The Board</h3><p>Redraft PPR, this year, 40 boards.</p></a>
          <a class="tile" href="the-fence.html"><h3>The Fence</h3><p>Superflex plus IDP on one mixed board.</p></a>
          <a class="tile" href="the-split.html"><h3>The Split</h3><p>Two clocks. A window year for the room.</p></a>
          <a class="tile" href="the-inheritance.html"><h3>The Inheritance</h3><p>If a starter sits, price the next man.</p></a>
          <a class="tile" href="the-handcuff.html"><h3>The Handcuff</h3><p>RB only. Dynasty list and redraft list.</p></a>
          <a class="tile" href="trade.html"><h3>Trade</h3><p>BK Value on six calculators.</p></a>
          <a class="tile" href="weekly.html"><h3>Weekly</h3><p>Week 2 skill start and sit.</p></a>
          <a class="tile" href="week2-matchups.html"><h3>Predictions</h3><p>A published pick on every game.</p></a>
          <a class="tile" href="league.html"><h3>My Team</h3><p>Your Sleeper league, priced on these ranks.</p></a>
          <a class="tile" href="news.html"><h3>BK News</h3><p>Hourly injury, roster, and coach tape.</p></a>
          <a class="tile" href="articles.html"><h3>Articles</h3><p>The long reads, including The Long Game.</p></a>
          <a class="tile" href="discord.html"><h3>Discord</h3><p>Ranks and trades inside a server.</p></a>
        </div>
      </section>
      <section class="method-grafs">
        <h2>The other sports</h2>
        <p>BaseKeep is dynasty baseball. BasketKeep is dynasty basketball. PitchKeep is Premier League. Each one keeps its own long core and its own palette. The rank-to-value idea stays the same so a trade in March still speaks the same language as a trade in September.</p>
      </section>
      <section class="method-write" id="write">
        <p class="kicker">Write</p>
        <h2>How to reach the boards.</h2>
        <p>Questions about a rank, a source, privacy, or a missing page can go to the <a href="https://github.com/balsalah51/BallKeep" rel="noopener">Ball Keep GitHub</a>. The <a href="discord.html">Discord bot</a> will search The Keep, run a trade, and drop tape in a server. The privacy policy lives on its own page. This site is independent. It has no league affiliation.</p>
      </section>
      {faq_html(METHOD_FAQ, heading="How to read The Method.")}
    </article>
    """


def write_the_method(b):
    extra = also_on_desk(b.FB_ALSO.get("the-method.html") or [])
    body = method_article_html() + extra
    b.write(
        "the-method.html",
        b.page(
            "The Method",
            "the-method.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("The Method", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("The Method", "https://ballkeep.com/the-method.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/the-method.html",
                    DEK,
                    published=PUBLISHED,
                    modified=PUBLISHED,
                    image=OG_IMAGE,
                    brand="Ball Keep",
                    section="Method",
                ),
                faq_jsonld(METHOD_FAQ),
            ],
            og_type="article",
            published=PUBLISHED,
            modified=PUBLISHED,
            body_class="method-page",
            image=OG_IMAGE,
            description=DEK,
        ),
    )
