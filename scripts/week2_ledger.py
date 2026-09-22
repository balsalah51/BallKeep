"""The Week 2 ledger: what the lists learned after sixteen scores."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "Write RB2 on the card and then decide if you still believe it."
DEK = (
    "Week 2 closed. The lists rebuilt. Every board on this site now prints "
    "the chair next to the name, RB2, WR3, QB1, so a rank is a sentence "
    "you can say out loud at a table."
)
PUBLISHED = "2026-09-22T17:00:00Z"
OG_IMAGE = "img/players/jamarr-chase.jpg"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def ledger_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="week2-ledger.html">
      <img src="{OG_IMAGE}" alt="Ja'Marr Chase" width="160" height="160" />
      <div>
        <p class="k">Week 2 · The Ledger · Tuesday, Sep 22</p>
        <h2>Chase, Coker, Coleman, and the chairs on every list.</h2>
        <p>The boards now say RB2 next to the second back. Buy the names rooms punished. Sell the ones they just crowned.</p>
      </div>
    </a>
    """


def ledger_article_html() -> str:
    return f"""
    <article class="opening essay recap">
      <p class="opening-kicker">Articles · The Ledger · Tuesday, September 22, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Tuesday while The Keep and The Board were still warm from the mash</p>

      <div class="photo-row" aria-label="Faces the lists moved">
        {_shot("jamarr-chase", "jpg", "Ja'Marr Chase")}
        {_shot("jalen-coker", "jpg", "Jalen Coker")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("josh-allen", "png", "Josh Allen")}
      </div>
      <p class="photo-cap">Chase, Coker, Walker, Maye, Nacua, Robinson, Gibbs, Allen. Some of these names climbed. Some of them sat. All of them now carry a chair on the list they live on.</p>

      <p class="lede">A ranking list that only says RB is a list that makes you count with your finger, and I have watched enough draft rooms do that counting out loud to know it is a waste of a good night, so every board on Ball Keep now prints the in-position rank after the position, RB2 for the second back, WR3 for the third receiver, QB1 for the first quarterback, the way people already talk when the clock is running.</p>

      <p>That change is small on the page and large at the table. You can sort The Keep and still see that the second running back on a Superflex dynasty board is a different sentence from the second running back on The Board, because The Keep is years and The Board is this season, and a name can be RB4 in one room and RB1 in the other without either list being confused. Weekly does the same thing for Sunday. Best Ball does it for boom weeks. The Fence does it for the mixed board. If you came here for a number, you still get the number. You also get the chair.</p>

      <h2>What Week 2 did to the chairs</h2>
      <p>Ja'Marr Chase spent the opener on twelve yards and then spent Houston on two touchdowns. That is a WR1 week from a WR1 name, and the Super Aggregate already treated him like one. The buy was the empty opener. The receipt is the 20-6 road win. If your room still has him as a faded WR2 because of one Thursday, you are talking to a person who watches the first chapter and closes the book.</p>
      <p>Jalen Coker is the other receiver sentence. Eight for 138 and two against Chicago, then 76 percent of the snaps in a 34-3 win in Atlanta, Young finding him in a game that already had Waller twice. Waiver lists still have him first or second if anyone left him out there. On our lists he will show as whatever chair the mash gives him, and that chair is climbing. Year-two leaps look like this when they are real. They also look like this when they are a two-week spike. Pay the snap share. Do not pay a career.</p>
      <p>Jonah Coleman punched a score after J.K. Dobbins left with a hamstring and RJ Harvey was already out. Sports Illustrated already has him first on the wire. That is an RB add, and the list will call him whatever RB he is once the mash eats the new boards. TreVeyon Henderson ran 39 yards in Foxborough and now has a role next to a quarterback who just won ugly. Those two backs are the week-after market. Dobbins is the sell if a manager still wants the starter tag on a hamstring.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jamarr-chase", "jpg", "Ja'Marr Chase")}
          {_shot("jalen-coker", "jpg", "Jalen Coker")}
        </div>
        <figcaption>Chase after twelve yards, then two scores. Coker after 138, then 76 percent of a blowout. Two different kinds of climb.</figcaption>
      </figure>

      <h2>Buy the cart. Sell the carnival leftover.</h2>
      <p>Caleb Williams left the 9-3 rain night on a cart with a towel over his face. Jayden Daniels left Dallas with the left elbow again. Superflex rooms that just watched 0-2 and a medical tent will sell Keep quarterbacks for a stream and a prayer. Those are the buys. The Keep is climate. A hamstring and an elbow are weather that happens to last a month. Pay the years. Sit the weeks. Bryce Young just put up 287 and three after 361 and four and is still sitting on a lot of wires. That is a Superflex add even if you already have a chair, because Cleveland is next and the tape is loud.</p>
      <p>Davante Adams caught eight for 195 and two on a Monday when Puka Nacua was inactive. Stafford threw four. The tree paid the veteran. The tree is still Nacua's when he dresses. Buy Nacua from the manager who only watched Adams. Start Adams until the hip report changes. That is a same-building pair with two different clocks, and the lists will show both chairs without asking you to remember who is WR1 in Los Angeles this week.</p>
      <p>Tyler Shough beat Baltimore. Darren Waller scored twice. Those are holds and adds. D'Andre Swift still has managers who watched 59 points and three scores and have not watched 9-3 in the rain. Take that overpay. Tua Tagovailoa was inactive again in a 34-3 home loss. C.J. Stroud's home night was 20-6. Baker Mayfield's revenge script died on fourth down. Jaxson Dart's left knee ended a Sunday-night glow on the first series Monday. Those are sells if the other manager is still paying August money.</p>

      <h2>How to read RB2 on three different boards</h2>
      <p>On The Keep, RB2 is a years sentence. Bijan and Gibbs have been that sentence all summer, and a 72-yard afternoon in a 34-3 loss does not evict Bijan from the long board any more than a short week in Buffalo evicts Gibbs. You start them this Sunday if they dress. You do not sell them because one script was ugly. Climate is slow on purpose.</p>
      <p>On The Board, RB2 is a this-year sentence. Christian McCaffrey just scored his 100th touchdown and still has to share a backfield with Kaelon Black. Kenneth Walker just ran for 117 in overtime after 173 on opening night. James Cook just ran for 134 in a 41-point Thursday. Those chairs move faster because the season is the product. If you are drafting 2026 only, trust The Board's RB2 more than The Keep's. If you are drafting 2028, do the opposite.</p>
      <p>On Weekly, RB2 is a Sunday sentence. Henderson can be that for a week. Coleman can be that for a week. Swift can fall out of it after a rain night. The weekly boards stay on Week 2 until the next card is a real card. Use them to start. Use The Keep to trade. Use The Board to settle a redraft argument. Use the chair number so you stop asking the table to count.</p>

      <div class="photo-row">
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
      </div>
      <p class="photo-cap">McCaffrey at 100. Robinson in a 34-3. Walker in overtime. Maye winning ugly. Four backs and a quarterback, four different clocks.</p>

      <h2>A closing that sounds like a person</h2>
      <p>I keep coming back to the simple picture of a manager sitting with a laptop on a Tuesday, the waiver already open, the chat already loud, and a list that used to say RB next to twelve names as if those twelve names were the same job. They were never the same job. The second back on a Superflex dynasty board is a building. The second back on a weekly board is a Sunday. Printing RB2 is how we stop pretending those two sentences share a chair.</p>
      <p>Read <a href="week2-tape.html">The Second Sunday</a> if you want the week. Read <a href="hot-n-cold.html">Hot 'n' Cold</a> if you want the ten names to buy and the ten names to sell. Read The Keep if you want the years. Read The Board if you want this season. This page is for the manager who wants the lists to talk the way the room already talks, and who is willing to sit with a second week long enough to remember which interruptions deserve a new chair and which ones are just weather.</p>
      <p class="sources">Week 2 tape from Reuters, ESPN, NFL.com, Sportsnet, CBS Sports, and Sports Illustrated. The chairs are the in-position ranks on each Ball Keep list after the Super Aggregate rebuilt on September 22. The opener still lives on <a href="the-recap.html">The Recap</a>. The long-term argument still lives on <a href="the-long-game.html">The Long Game</a>.</p>
    </article>
    """


def write_week2_ledger(b):
    extra = also_on_desk(b.FB_ALSO.get("week2-ledger.html") or [])
    body = ledger_article_html() + extra
    b.write(
        "week2-ledger.html",
        b.page(
            "The Ledger",
            "week2-ledger.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", "articles.html"),
                ("The Ledger", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                    ("The Ledger", "https://ballkeep.com/week2-ledger.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/week2-ledger.html",
                    DEK,
                    published=PUBLISHED,
                    modified=PUBLISHED,
                    image=OG_IMAGE,
                    brand="Ball Keep",
                    section="Week 2",
                ),
            ],
            og_type="article",
            published=PUBLISHED,
            modified=PUBLISHED,
            body_class="opening-page recap-page essay-page",
            image=OG_IMAGE,
            description=DEK,
        ),
    )
