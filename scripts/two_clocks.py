"""Two Clocks: the essay that belongs with The Split."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "A room has two clocks, and most sites only wind one of them."
DEK = (
    "Dynasty money and Sunday money live in the same name and almost never "
    "agree. The Split puts both on the table and then tells you which year "
    "your room is actually trying to win."
)
PUBLISHED = "2026-09-24T18:00:00Z"
OG_IMAGE = "img/players/drake-maye.jpg"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def clocks_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="two-clocks.html">
      <img src="{OG_IMAGE}" alt="Drake Maye" width="160" height="160" />
      <div>
        <p class="k">Articles · Two Clocks · Thursday, Sep 24</p>
        <h2>A room has two clocks. Most sites wind one.</h2>
        <p>Keep money and Board money on the same name, then a window year for the room you actually roster.</p>
      </div>
    </a>
    """


def clocks_article_html() -> str:
    return f"""
    <article class="opening essay recap">
      <p class="opening-kicker">Articles · Two Clocks · Thursday, September 24, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Thursday while Week 3 was still a card and The Split was still warm</p>

      <div class="photo-row" aria-label="Faces from both clocks">
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("ashton-jeanty", "jpg", "Ashton Jeanty")}
        {_shot("travis-kelce", "png", "Travis Kelce")}
        {_shot("tetairoa-mcmillan", "jpg", "Tetairoa McMillan")}
      </div>
      <p class="photo-cap">Maye, McCaffrey, Bijan, Gibbs, Allen, Jeanty, Kelce, McMillan. Some of these names are years. Some of them are Sundays. A few of them are both, and those are the expensive ones.</p>

      <p class="lede">I have sat in enough Superflex rooms to know the exact moment a deal dies, and it is almost never the moment someone names a price, it is the moment two people realize they are talking about the same player on two different clocks and neither of them has a page that will admit it.</p>

      <p>One manager is holding Drake Maye because The Keep still treats the arm like a decade. The other manager is holding Christian McCaffrey because The Board still treats the touches like a title. Both managers are right on the clock they are watching. Both managers will feel cheated if they trade into the other clock without saying so out loud. Every public site I know will give you one number for that moment. KeepTradeCut will give you a dynasty dollar. FantasyPros will give you a redraft rank. Sleeper will give you a league page that pretends those two sentences share a chair. They share a name. The year is the fight.</p>

      <h2>What a Sunday name costs you in years</h2>
      <p>A Sunday name is a player The Board loves and The Keep is already walking away from. Derrick Henry has been that sentence for two summers. Travis Kelce has been that sentence since the first grey hair in the highlight. McCaffrey is that sentence on a week when he looks like himself and a different sentence on a week when the cart is in the tunnel. You start those names in 2026. 2028 is a different roster. If a rebuilder offers you a late first for a Sunday name, take the first and thank him for watching the wrong clock. If a contender offers you a young receiver and a 2027 second for a Sunday back who still plays sixty snaps, you are being paid in years for a year you already own, and that is the trade you want to be on the receiving end of only if your roster is already loud in December.</p>
      <p>The Split prints that gap as a plus number. Keep rank minus Board rank. When the plus number is fat, the name is a Sunday. The chair on The Board might say RB2. The chair on The Keep might say he is off the top forty. Both chairs are honest. The plus sign is the argument.</p>

      <figure>
        <div class="photo-pair">
          {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
          {_shot("derrick-henry", "png", "Derrick Henry")}
        </div>
        <figcaption>McCaffrey and Henry. Sunday names when the health is right. Years names only in the memory of a room that drafted them in 2023.</figcaption>
      </figure>

      <h2>What a years name costs you on Sunday</h2>
      <p>A years name is a player The Keep still pays and The Board has already started to shrug at. Maye after an ugly opener was that sentence. Tetairoa McMillan in a Carolina offense that just hung 34 is becoming the other version of it, the one where Sunday is catching up. Ashton Jeanty and Jeremiyah Love live here on purpose. You hold those names through a quiet September because the clock you bought was 2028. You sit them on a weekly board that has already found a veteran with a better script this week. That sitting is the tax. People who refuse to pay the tax start selling years for a stream, and those are the deals The Split is built to catch before you make them.</p>
      <p>The minus gap is the years sign. Keep rank better than Board rank. QB2 on The Keep and QB8 on The Board is a Superflex sentence. RB4 on The Keep and RB18 on The Board is a rebuild sentence. You need both chairs in front of you or you will trade the wrong one.</p>

      <h2>The window year is the sentence a room writes</h2>
      <p>A single name has a gap. A room has a year. I wanted a page that would take the names you actually roster, add the two BK Values, look at the ages, and then say the year out loud. 2026 means the room is trying to win this season. 2028 means the room is built for the next window. 2027 means you can win soon and you still have years, which is the lucky room, and also the room that gets talked into wrecking itself because someone in the chat watched one carnival.</p>
      <p>The math is simple enough to say in a voice. Board money over total money is how loud this year is. Age is how long the bodies will last. A room full of 28-year-old Board darlings will print 2026 even if The Keep still has a couple of them inside the top fifty. A room full of 23-year-old Keep darlings will print 2028 even if Weekly has them on the bench. You can argue with a year. You should argue with a year. You should not have to invent the year in your head while twelve other people are talking.</p>

      <div class="photo-row">
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("ashton-jeanty", "jpg", "Ashton Jeanty")}
        {_shot("brock-bowers", "jpg", "Brock Bowers")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
      </div>
      <p class="photo-cap">Maye, Jeanty, Bowers, Williams. A sample 2028 room if you want to see the later clock light up. The other sample on The Split is the 2026 room, and it looks like a December roster.</p>

      <h2>How to use it on a Thursday</h2>
      <p>Go to <a href="the-split.html">The Split</a>. Search the names you actually start. Add them. Read the two totals. Read the year. If the year says 2026 and you were about to trade McCaffrey for a 2027 first and a dart, sit down. If the year says 2028 and you were about to spend a first on a 29-year-old tight end because he just scored twice, sit down. If the year says 2027, you have a choice, and the choice is the whole sport.</p>
      <p>The gap board under the tool is the public argument, sorted by the names the two clocks disagree on the most. That board will move when The Keep and The Board rebuild, because the Super Aggregate is alive and Thursday is a fine day to admit that a week just ended and another one is already asking for a start list. The chairs stay on the names. RB2 on The Board next to RB14 on The Keep is a sentence you can say at a table without counting on your fingers.</p>

      <h2>A closing that sounds like a person</h2>
      <p>I keep a private list of deals that only looked fair on one clock. The Maye sale after three picks. The Henry buy after a 44-yard race. The first-round pick that turned into a tight end who will be 31 when the pick would have been a player. Those deals all had a number. They were missing a year. The Split is the page that prints the year. Two Clocks is the reminder that you already knew the year if you sat still long enough, and that a website owes you the sitting.</p>
      <p>If you want the mash, it is on The Keep and The Board. If you want the stream, it is on Weekly. If you want to write us about a rank, The Method still has the address. This page is for the manager who is tired of translating dynasty into redraft in his head while the chat is already moving, which is every manager I have ever liked.</p>
      <p class="sources">The clocks are The Keep Super Aggregate and The Board Super Aggregate, rebuilt September 24. Rank 1 is 12,000 BK Value on each list. The window year lives on <a href="the-split.html">The Split</a>. The long-term argument still lives on <a href="the-long-game.html">The Long Game</a>. Week 2 still has a full tape on <a href="week2-tape.html">The Second Sunday</a>.</p>
    </article>
    """


def write_two_clocks(b):
    extra = also_on_desk(b.FB_ALSO.get("two-clocks.html") or [])
    body = clocks_article_html() + extra
    b.write(
        "two-clocks.html",
        b.page(
            "Two Clocks",
            "two-clocks.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", "articles.html"),
                ("Two Clocks", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                    ("Two Clocks", "https://ballkeep.com/two-clocks.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/two-clocks.html",
                    DEK,
                    published=PUBLISHED,
                    modified=PUBLISHED,
                    image=OG_IMAGE,
                    brand="Ball Keep",
                    section="Articles",
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
