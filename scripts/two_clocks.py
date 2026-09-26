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

      <p class="lede">A Superflex deal usually dies in the second silence, after somebody has already said a number and the other person has already nodded, when both of them realize they have been talking about the same player and two different years and neither of them has a page that will admit the difference out loud.</p>

      <p>One manager is holding Drake Maye because The Keep still treats the arm like a decade, and the other is holding Christian McCaffrey because The Board still treats the touches like a title, and both of them are right on the clock they came to defend. The cheat happens when they trade into the other clock without saying the year. KeepTradeCut will hand you a dynasty dollar, FantasyPros will hand you a redraft rank, and Sleeper will hand you a league page that treats those two prices as if they were the same furniture. They share a name. The year is the fight, and it has been the fight in every room I have liked since the first time a 29-year-old back was called fair for a 2028 first.</p>

      <h2>What a Sunday name costs you in years</h2>
      <p>A Sunday name is a player The Board still loves while The Keep is already walking away, which is Derrick Henry for two summers now and Travis Kelce since the first grey hair in the highlight and McCaffrey on the weeks he looks like himself, with a different price on the weeks the cart is in the tunnel. You start those names in 2026 because they still touch the ball in December, and you stop pretending they are a 2028 roster because the body will not sign that contract for you. A rebuilder who offers a late first for a Sunday name is paying you in years for a year you already own, and a contender who offers a young receiver and a 2027 second for a Sunday back who still plays sixty snaps is doing the same trade from the other side of the table, which is only a gift when your roster is already loud in December and you can afford to collect the later clock.</p>
      <p>The Split prints that gap as a plus number, Keep rank minus Board rank, and when the plus number is fat the name is a Sunday even when the two lists refuse to use the same language. The Board might call him RB2 and The Keep might have him outside the top forty, and both of those chairs can be honest on the same Thursday because one of them is counting this season and the other is counting the ones after it. The plus sign is the argument you used to have to make with your hands.</p>

      <figure>
        <div class="photo-pair">
          {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
          {_shot("derrick-henry", "png", "Derrick Henry")}
        </div>
        <figcaption>McCaffrey and Henry. Sunday names when the health is right. Years names only in the memory of a room that drafted them in 2023.</figcaption>
      </figure>

      <h2>What a years name costs you on Sunday</h2>
      <p>A years name is a player The Keep still pays while The Board has already started to shrug, which was Maye after the ugly opener and is becoming Tetairoa McMillan now that Carolina hung 34 and Sunday has begun to catch the name the long boards were already carrying. Ashton Jeanty and Jeremiyah Love live here on purpose. You hold them through a quiet September because the clock you bought was 2028, and you sit them on a weekly board that has already found a veteran with a better script this week, and that sitting is the tax a dynasty room agreed to pay when it spent a first on a birthday instead of a snap count. The people who refuse the tax start selling years for a stream, and those are the deals The Split is built to catch while the chat is still congratulating itself.</p>
      <p>The minus gap is the years sign, Keep rank better than Board rank, and you need both chairs in front of you or you will trade the wrong one. QB2 on The Keep next to QB8 on The Board is a Superflex sentence about a passer you are supposed to keep through the ugly weeks. RB4 on The Keep next to RB18 on The Board is a rebuild sentence about a back the Sunday rooms have already replaced. The two numbers together are the thing a person can say at a table without flipping between tabs.</p>

      <h2>The window year is the sentence a room writes</h2>
      <p>A single name has a gap and a room has a year, and I wanted a page that would take the names you actually roster, add the two BK Values, weigh the ages, and then say the year out loud so the chat could argue with a date instead of a feeling. 2026 means the room is trying to win this season. 2028 means the room is built for the next window. 2027 means you can win soon and you still have years, which is the lucky room and also the room that gets talked into wrecking itself because somebody watched one carnival and decided the window had arrived on a Sunday afternoon.</p>
      <p>The math is simple enough to say in a voice. Board money over total money is how loud this year is, and age is how long the bodies will last, so a room full of 28-year-old Board darlings will print 2026 even when The Keep still has a couple of them inside the top fifty, and a room full of 23-year-old Keep darlings will print 2028 even when Weekly has them on the bench. You can argue with a year, and you should, because a year is a claim about a roster and claims should be tested. You should not have to invent the year in your head while twelve other people are talking.</p>

      <div class="photo-row">
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("ashton-jeanty", "jpg", "Ashton Jeanty")}
        {_shot("brock-bowers", "jpg", "Brock Bowers")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
      </div>
      <p class="photo-cap">Maye, Jeanty, Bowers, Williams. A sample 2028 room if you want to see the later clock light up. The other sample on The Split is the 2026 room, and it looks like a December roster.</p>

      <h2>How to use it on a Thursday</h2>
      <p>Go to <a href="the-split.html">The Split</a>, search the names you actually start, and let the two totals sit next to the year before you send a name out of the room. A 2026 stamp next to a roster that was about to trade McCaffrey for a 2027 first and a dart is the site telling you the club is trying to win this season and you were about to sell the season. A 2028 stamp next to a first you were about to spend on a 29-year-old tight end because he scored twice is the same warning from the other direction. A 2027 stamp is the lucky middle, which is also the dangerous middle, because that is when a room still has years and still has a chance and the chat can talk it into either one before Thursday is over.</p>
      <p>The gap board under the tool is the public argument, sorted by the names the two clocks disagree on the most, and it will move when The Keep and The Board rebuild because the Super Aggregate is alive and Thursday is a fine day to admit that a week just ended and another one is already asking for a start list. The chairs stay on the names. RB2 on The Board next to RB14 on The Keep is a sentence you can say at a table without counting on your fingers.</p>

      <h2>The year you already knew</h2>
      <p>I keep a private list of deals that only looked fair on one clock: the Maye sale after three picks, the Henry buy after a 44-yard race, the first-round pick that turned into a tight end who will be 31 when the pick would have been a player. Those deals all had a number and they were missing a year. The Split is the page that prints the year. This essay is the reminder that you already knew the year when you sat still long enough, and that a website owes you the sitting instead of another single price pretending to be the whole sport.</p>
      <p>The Keep and The Board still hold the mash, Weekly still holds the stream, and The Method still has the address if a rank needs a letter. This page is for the manager who is tired of translating dynasty into redraft in his head while the chat is already moving, which is every manager I have ever liked.</p>
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
