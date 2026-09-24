"""The Next Chair: the essay that belongs with The Inheritance."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "When a starter sits, the snaps still have to go somewhere."
DEK = (
    "Depth charts name the next man. The Inheritance prices him on both clocks "
    "and tells you how much Sunday money just left the room."
)
PUBLISHED = "2026-09-24T21:00:00Z"
OG_IMAGE = "img/players/christian-mccaffrey.png"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def next_chair_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="next-chair.html">
      <img src="{OG_IMAGE}" alt="Christian McCaffrey" width="160" height="160" />
      <div>
        <p class="k">Articles · The Next Chair · Thursday, Sep 24</p>
        <h2>When a starter sits, the snaps still have to go somewhere.</h2>
        <p>Price the heir on both clocks. Read the hole that opens on Sunday.</p>
      </div>
    </a>
    """


def next_chair_article_html() -> str:
    return f"""
    <article class="opening essay recap">
      <p class="opening-kicker">Articles · The Next Chair · Thursday, September 24, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Thursday night while the Week 3 report was still a rumor and The Inheritance was still warm</p>

      <div class="photo-row" aria-label="Faces from the next chair">
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        {_shot("kaelon-black", "jpg", "Kaelon Black")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("jacoby-brissett", "png", "Jacoby Brissett")}
        {_shot("jeremiyah-love", "jpg", "Jeremiyah Love")}
        {_shot("tyler-allgeier", "jpg", "Tyler Allgeier")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
        {_shot("george-kittle", "png", "George Kittle")}
      </div>
      <p class="photo-cap">McCaffrey and Black. Maye and Brissett. Love and Allgeier. Puka and Kittle. Every one of those pairs is a chair and a man standing behind it, and only one of those two names is priced like a starter on Sunday.</p>

      <p class="lede">I have watched enough Thursday night reports to know the exact moment a Superflex chat stops being a trade room and turns into a scavenger hunt, and it is the moment a starter gets a designation and twelve people type the same backup and zero people can say what that backup is actually worth on the clock they are trying to win.</p>

      <p>Sleeper will give you an order. ESPN will give you a word: Out, Doubtful, Questionable. FantasyPros will give you a weekly rank that already assumed the starter plays. KeepTradeCut will still be pricing the dynasty name as if the cart never rolled. You are left doing math in your head while the waiver timer is already moving. The snaps did not vanish. They moved one chair down. That chair has a Keep number and a Board number, and those two numbers almost never tell the same story, which is why the room that only reads one of them keeps buying the wrong handcuff and selling the wrong year.</p>

      <h2>A Sunday hole is a different injury than a years chair</h2>
      <p>Christian McCaffrey on a week he plays is Board RB3 and Keep RB12. That gap is already a Sunday sentence. If he sits, the 49ers still have to hand the ball to someone, and right now that someone is Kaelon Black after fourteen carries in Melbourne. Black can be a correct waiver in a redraft room and a dart in a dynasty room on the same night. The hole is the Board money that left with McCaffrey minus the Board money that walked in with Black. When that hole is fat, you are streaming. When a rebuilder offers you a 2027 second for Black because the report scared him, you are being paid in years for a week. Take the years if your room is already loud in December. Hold the handcuff if your room needs that Sunday chair this month.</p>
      <p>The Inheritance prints that hole as a number. Starter Board BK Value minus heir Board BK Value. Rank 1 is still 12,000. The plus sign is the argument. You can say it at a table without opening four tabs.</p>

      <figure>
        <div class="photo-pair">
          {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
          {_shot("kaelon-black", "jpg", "Kaelon Black")}
        </div>
        <figcaption>McCaffrey and Black. A Sunday name and the man who inherits the Shanahan touches. The hole is the whole conversation.</figcaption>
      </figure>

      <h2>Years walk into a Sunday chair more often than people admit</h2>
      <p>Jeremiyah Love is Arizona's listed back. Tyler Allgeier is the man behind him. Love is a years name on The Keep and a quieter name on The Board after two September weeks. If Love sits, Allgeier walks into a Sunday chair that dynasty rooms have been treating like a 2028 asset. That is the other inheritance, the one that makes a contender smile and a rebuilder sick. You held Love through a quiet card because the clock you bought was later. The tax is the week the veteran behind him scores twice and the chat decides the kid was a miss. The kid was a years buy. The veteran is a Sunday fill. Both can be true on the same depth chart, and the page that refuses to print both prices is the reason those rooms keep arguing past each other.</p>
      <p>Drake Maye after an ugly opener is the quarterback version. The Keep still pays the arm like a decade. The Board has already found veterans with a cleaner script this week. If Maye sits, Jacoby Brissett is a Sunday name behind years. Superflex rooms that only watch The Keep will feel rich and still lose the week. Superflex rooms that only watch The Board will start Brissett and then sell Maye for a stream, which is the trade The Split was built to catch and The Inheritance is built to explain before you make it.</p>

      <div class="photo-row">
        {_shot("jeremiyah-love", "jpg", "Jeremiyah Love")}
        {_shot("tyler-allgeier", "jpg", "Tyler Allgeier")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("jacoby-brissett", "png", "Jacoby Brissett")}
      </div>
      <p class="photo-cap">Love and Allgeier. Maye and Brissett. Years names with Sunday men behind them. The sample on The Inheritance that says years chairs will light this pairing up.</p>

      <h2>How to use it on a Thursday night</h2>
      <p>Go to <a href="the-inheritance.html">The Inheritance</a>. Search the name that just got a word on the report. Read the left clock. Read the right clock. Read the hole. If the call says Hole and you need that chair this week, the stream is already on the waiver board and you should spend the FAAB before the room finishes arguing about the starter. If the call says Years in and you are a contender, the veteran behind the kid just became a start. If the call says Covered, sit down, because the next man already has Sunday money and you are about to overpay for a name the board already priced. If the call says Sunday behind, your Superflex bench just got a week, and the years name on the starter chair is still the one you keep.</p>
      <p>The hole board under the tool is the public argument. Injured names sit first. Then the fattest holes. That board will move when Sleeper changes an order, when ESPN changes a word, and when The Keep and The Board rebuild, because a depth chart without a price is a list of rumors and a price without a depth chart is a list of ghosts. The chairs stay on the starters. RB3 on The Board next to a backup with no Board chair is a sentence you can say out loud.</p>

      <h2>A closing that sounds like a person</h2>
      <p>I keep a private list of weeks that were decided by a name nobody priced until Saturday. The handcuff who scored twice after a cart. The veteran quarterback who won a Superflex week while the kid's Keep number stayed pretty. The tight end who inherited twelve targets because the starter's knee said no and the waiver ran out at 3 a.m. Those weeks all had a depth chart. They were missing a hole. The Inheritance is the page that prints the hole. The Next Chair is the reminder that you already knew the snaps would go somewhere if you sat still long enough, and that a website owes you the sitting.</p>
      <p>If you want the year of the whole room, that is <a href="the-split.html">The Split</a>. If you want the mash, it is on The Keep and The Board. If you want the stream, it is on Weekly. This page is for the manager who is tired of translating a depth chart into money in his head while the report is still a rumor, which is every manager I have ever liked on a Thursday.</p>
      <p class="sources">The order is Sleeper depth. The designations are ESPN. The clocks are The Keep Super Aggregate and The Board Super Aggregate, rebuilt September 24. Rank 1 is 12,000 BK Value on each list. The hole lives on <a href="the-inheritance.html">The Inheritance</a>. Two clocks on a room you type still live on <a href="the-split.html">The Split</a>. Week 2 still has a full tape on <a href="week2-tape.html">The Second Sunday</a>.</p>
    </article>
    """


def write_the_next_chair(b):
    extra = also_on_desk(b.FB_ALSO.get("next-chair.html") or [])
    body = next_chair_article_html() + extra
    b.write(
        "next-chair.html",
        b.page(
            "The Next Chair",
            "next-chair.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", "articles.html"),
                ("The Next Chair", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                    ("The Next Chair", "https://ballkeep.com/next-chair.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/next-chair.html",
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
