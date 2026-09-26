"""Articles hub: Ball Keep essays in one list."""
from __future__ import annotations

from seo import also_on_desk, breadcrumb_jsonld, breadcrumbs, esc
from the_long_game import DEK as LONG_DEK
from the_long_game import HEADLINE as LONG_HEAD
from the_long_game import write_the_long_game
from two_clocks import DEK as CLOCK_DEK
from two_clocks import HEADLINE as CLOCK_HEAD
from two_clocks import write_two_clocks
from week2_ledger import DEK as LEDGER_DEK
from week2_ledger import HEADLINE as LEDGER_HEAD
from week2_ledger import write_week2_ledger
from week2_tape import DEK as TAPE_DEK
from week2_tape import HEADLINE as TAPE_HEAD
from week2_tape import write_week2_tape

ARTICLES = [
    (
        "two-clocks.html",
        "Two Clocks",
        "Thursday, Sep 24",
        CLOCK_HEAD,
        CLOCK_DEK,
        "img/players/drake-maye.jpg",
        "Drake Maye",
        True,
    ),
    (
        "week2-tape.html",
        "The Second Sunday",
        "Tuesday, Sep 22",
        TAPE_HEAD,
        TAPE_DEK,
        "img/players/matthew-stafford.png",
        "Matthew Stafford",
        False,
    ),
    (
        "week2-ledger.html",
        "The Ledger",
        "Tuesday, Sep 22",
        LEDGER_HEAD,
        LEDGER_DEK,
        "img/players/jamarr-chase.jpg",
        "Ja'Marr Chase",
        False,
    ),
    (
        "the-long-game.html",
        "The Long Game",
        "Thursday, Sep 17",
        LONG_HEAD,
        LONG_DEK,
        "img/players/josh-allen.png",
        "Josh Allen",
        False,
    ),
    (
        "the-recap.html",
        "The Recap",
        "Tuesday, Sep 15",
        "Sixteen scores, one opening week, and a league that already has a memory.",
        "Seattle closed Wednesday 13-10. Chicago hung 59. Walker ran for 173 on Monday. The full Week 1 tape.",
        "img/players/caleb-williams.jpg",
        "Caleb Williams",
        False,
    ),
    (
        "week2-matchups.html",
        "Week 2 Predictions",
        "Tuesday, Sep 22",
        "Bills over Lions. Monday paid eleven.",
        "Rams 28-6. Carolina 34-3. San Francisco 35-13. Kansas City in overtime. Mash 11-5.",
        "img/players/josh-allen.png",
        "Josh Allen",
        False,
    ),
    (
        "the-market.html",
        "The Market",
        "Tuesday, Sep 15",
        "Buy low and sell high after Week 1.",
        "Buy the names rooms punished after one ugly night. Sell the names rooms just watched in a carnival.",
        "img/players/puka-nacua.jpg",
        "Puka Nacua",
        False,
    ),
    (
        "the-method.html",
        "The Method",
        "Wednesday, Sep 16",
        "How the Super Aggregate works.",
        "Half the vote is the long boards. Half is every other list that ranked the name. Rank 1 is 12,000.",
        "img/players/bijan-robinson.jpg",
        "Bijan Robinson",
        False,
    ),
]


def articles_hub_html() -> str:
    cards = []
    for href, kicker, when, title, dek, img, alt, lead in ARTICLES:
        cls = "article-card is-lead" if lead else "article-card"
        cards.append(
            f'<a class="{cls}" href="{esc(href)}">'
            f'<img src="{esc(img)}" alt="{esc(alt)}" width="240" height="240" loading="lazy" />'
            f"<div>"
            f'<p class="k">{esc(kicker)} · {esc(when)}</p>'
            f"<h2>{esc(title)}</h2>"
            f"<p>{esc(dek)}</p>"
            f"</div></a>"
        )
    return f"""
    <p class="kicker">Articles</p>
    <h1>The long reads.</h1>
    <p class="note">Long reads on Ball Keep, written the way a person talks after sitting with a week, so you can keep the years you paid for in a Superflex room even while Sunday is shouting. The boards stay on the boards. These pages are for the story that belongs next to the mash.</p>
    <section class="article-rail" aria-label="Ball Keep articles">
      {"".join(cards)}
    </section>
    """


def write_articles(b):
    write_the_long_game(b)
    write_two_clocks(b)
    write_week2_tape(b)
    write_week2_ledger(b)
    extra = also_on_desk(b.FB_ALSO.get("articles.html") or [])
    b.write(
        "articles.html",
        b.page(
            "Articles",
            "articles.html",
            articles_hub_html() + extra,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                ]),
            ],
            schema_type="CollectionPage",
            body_class="articles-page",
        ),
    )
