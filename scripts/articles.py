"""Articles hub: Ball Keep essays in one list."""
from __future__ import annotations

from seo import also_on_desk, breadcrumb_jsonld, breadcrumbs, esc
from the_long_game import DEK as LONG_DEK
from the_long_game import HEADLINE as LONG_HEAD
from the_long_game import write_the_long_game

ARTICLES = [
    (
        "the-long-game.html",
        "The Long Game",
        "Thursday, Sep 17",
        LONG_HEAD,
        LONG_DEK,
        "img/players/josh-allen.png",
        "Josh Allen",
        True,
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
        "Wednesday, Sep 16",
        "Bills over Lions. A pick on every line.",
        "The mash likes Buffalo on Thursday and San Francisco in a landslide. Sixteen published winners.",
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
    <p class="note">Essays and strategy on Ball Keep, written so you can sit with a week that is shouting and still remember the years you paid for in a Superflex room. The boards stay on the boards. These pages are for the manager who wants the story next to the mash.</p>
    <section class="article-rail" aria-label="Ball Keep articles">
      {"".join(cards)}
    </section>
    """


def write_articles(b):
    write_the_long_game(b)
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
