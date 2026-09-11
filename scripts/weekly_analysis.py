"""Week 1 opening analysis: first two games and fantasy notes."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "Seahawks 13, Patriots 10. 49ers 27, Rams 7. Most of Week 1 is still ahead."
DEK = (
    "Sam Darnold left Wednesday's Super Bowl rematch with a hip injury after a first-quarter "
    "sack and is expected to miss Week 2 at Arizona. A.J. Brown sustained a right high-ankle "
    "sprain in the third quarter and is anticipated to miss multiple weeks. On Thursday in "
    "Melbourne, Brock Purdy threw three touchdowns as San Francisco beat Los Angeles 27-7. "
    "De'Zhaun Stribling left with a non-contact ankle injury. Jake Tonges sustained an MCL sprain."
)
PUBLISHED = "2026-09-11T16:00:00Z"
OG_IMAGE = "img/players/jaxon-smith-njigba.jpg"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def opening_teaser():
    return f"""
    <a class="opening-teaser" href="week1-opening.html">
      <img src="{OG_IMAGE}" alt="Jaxon Smith-Njigba" width="160" height="160" />
      <div>
        <p class="k">Opening analysis · Friday, Sep 11</p>
        <h2>Seahawks 13, Patriots 10. 49ers 27, Rams 7.</h2>
        <p>Darnold left with a hip injury. A.J. Brown sustained a right high-ankle sprain. Those absences already change leftover Sunday lineups and the first waiver list.</p>
      </div>
    </a>
    """


def opening_article_html():
    return f"""
    <article class="opening">
      <p class="opening-kicker">Week 1 · Opening analysis · Friday, September 11, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Friday after the Netflix game in Melbourne</p>

      <div class="score-row">
        <div class="score-card">
          <p class="when">Wed, Sep 9 · 8:20 p.m. ET · NBC</p>
          <p class="result">Seahawks 13, Patriots 10</p>
          <p class="meta">Super Bowl rematch at Lumen Field. Darnold out with a hip injury. Lock closed it.</p>
        </div>
        <div class="score-card">
          <p class="when">Thu, Sep 10 · Netflix · Melbourne, Australia</p>
          <p class="result">49ers 27, Rams 7</p>
          <p class="meta">First regular-season NFL game in Australia. Purdy threw three touchdowns.</p>
        </div>
      </div>

      <div class="photo-row" aria-label="Players from the first two games">
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("sam-darnold", "png", "Sam Darnold")}
        {_shot("drew-lock", "png", "Drew Lock", linked=False)}
        {_shot("a-j-brown", "png", "A.J. Brown")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
      </div>
      <p class="photo-cap">Maye, Darnold, Lock, Brown, Smith-Njigba, Purdy, McCaffrey, Nacua. The first two nights already changed Sunday lineups and the Week 2 waiver list.</p>

      <p class="lede">Week 1 opened on two continents before most of the league had taken a snap. The Patriots went to Seattle on Wednesday and lost 13-10. The 49ers and Rams then played in Melbourne, and San Francisco left Australia with a 27-7 win. Those scores already sit in Week 1 totals. They also open holes for the Sunday remainder and set the first waiver list of the year.</p>

      <h2>Wednesday in Seattle</h2>
      <p>Sam Darnold lasted one series. He left in the first quarter after a sack, went to the locker room, and was ruled out before halftime with a hip injury. A CT scan ruled out a fracture. Coach Mike Macdonald said Thursday that the early news was "really, really good," and that Darnold is still expected to miss next week at Arizona. Tom Pelissero reported Drew Lock as the likely Week 2 starter against the Cardinals.</p>
      <p>New England led 7-0 at the break. Lock finished the comeback. Seattle's defense closed the night with a late interception. Drake Maye threw three fourth-quarter interceptions and called the mistakes unacceptable after the game.</p>
      <p>A.J. Brown sustained a right high-ankle sprain in the third quarter. He left in a walking boot. X-rays were negative. Ian Rapoport and Mike Garafolo reported the sprain, and early reporting pointed to about three to four weeks. New England avoided a fracture. Brown is still anticipated to miss multiple weeks, including the Sunday remainder.</p>
      <p>Jaxon Smith-Njigba still produced after Lock entered. If you rostered him, you already have his Week 1 line. Keep him in for Week 2 even if Lock starts. Waiver names that moved on the wire: <a href="players/romeo-doubs.html">Romeo Doubs</a> and <a href="players/demario-douglas.html">DeMario Douglas</a>. If Brown sits multiple weeks, add Douglas first among New England receivers. Rooms that need a replacement wideout this weekend will reach for Doubs. Leave Jadarian Price on the wire until he actually plays a real snap share.</p>

      <figure>
        <div class="photo-pair">
          {_shot("drake-maye", "jpg", "Drake Maye")}
          {_shot("a-j-brown", "png", "A.J. Brown")}
        </div>
        <figcaption>Drake Maye threw three fourth-quarter interceptions. A.J. Brown sustained a right high-ankle sprain and left in a walking boot.</figcaption>
      </figure>

      <div class="ramif">
        <h3>Fantasy notes from Seattle</h3>
        <ul>
          <li>Stream Lock in Week 2 against Arizona if you need a quarterback. Bench Darnold until the MRI and the Week 2 designation land.</li>
          <li>Hold Smith-Njigba. He already worked with Lock in the opener.</li>
          <li>Maye's Week 1 score is in. Do not drop him. For Week 2, start him only if you lack a cleaner Sunday option.</li>
          <li>Stash Brown or move him to IR if your league allows it. Fade him while he recovers from the high-ankle sprain, at least the next three weeks.</li>
          <li>Seattle's defense already scored. It remains a Week 2 stream if you like the Arizona matchup.</li>
          <li>Friday waiver tickets: Douglas if Brown is out, Doubs if you need a wideout, Lock if your quarterback just went down.</li>
        </ul>
      </div>

      <h2>Thursday in Melbourne</h2>
      <p>The first regular-season NFL game on Australian soil went to San Francisco, 27-7. Brock Purdy completed 25 of 34 for 205 yards, three touchdowns, and one interception. Matthew Stafford and the Rams never found a second half. Halftime sat 10-7. San Francisco had outgained Los Angeles 208-137 at the break and pulled away after it.</p>
      <p>Christian McCaffrey, George Kittle, and Nick Bosa all played. Kittle had returned from a January Achilles tear. Kyle Shanahan said the staff had to be smart with his snaps. Kittle finished with two catches for 12 yards. That is a Week 1 line you already own, not a reason to cut him.</p>
      <p>Rookie receiver <a href="players/dezhaun-stribling.html">De'Zhaun Stribling</a> sustained a non-contact ankle injury, was carted off, and was ruled out. Shanahan said the Achilles is intact. An MRI will set the rest of the timeline. Tight end Jake Tonges sustained an MCL sprain. Shanahan said the injury was "not good."</p>
      <p>Puka Nacua, Kyren Williams, and Davante Adams already spent their Week 1 snaps in a 7-point loss. Those points are in. Week 2 is a new slate. Do not drop a Rams skill name because Thursday in Melbourne was ugly.</p>

      <figure>
        <div class="photo-pair">
          {_shot("brock-purdy", "jpg", "Brock Purdy")}
          {_shot("matthew-stafford", "png", "Matthew Stafford")}
        </div>
        <figcaption>Brock Purdy: 25 of 34, 205 yards, three touchdowns, one interception. Matthew Stafford's Rams finished with seven points.</figcaption>
      </figure>

      <figure>
        <div class="photo-pair">
          {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
          {_shot("george-kittle", "png", "George Kittle")}
        </div>
        <figcaption>Christian McCaffrey played in Melbourne. George Kittle returned from a January Achilles tear and caught two passes for 12 yards.</figcaption>
      </figure>

      <div class="ramif">
        <h3>Fantasy notes from Melbourne</h3>
        <ul>
          <li>Purdy already banked three touchdowns. Leave him in Week 2 rooms.</li>
          <li>McCaffrey played. Treat him as a locked starter going forward.</li>
          <li>Kittle's catch total was low. Start him in Week 2 when you need a tight end.</li>
          <li>Stafford, Nacua, Williams, and Adams are closed for Week 1. Hold them.</li>
          <li>Stash Stribling if you have a bench spot. Wait for the ankle MRI before you spend real FAAB.</li>
          <li>Fade Tonges until Shanahan or the club publishes an MCL timeline.</li>
          <li>San Francisco's defense already scored in a 27-7 win. Stream it again only if the next matchup is soft.</li>
        </ul>
      </div>

      <h2>What still sits on Sunday</h2>
      <p>Most of Week 1 has not been played. The <a href="weekly.html">weekly boards</a> still set the remaining slates. If you started Darnold, you already need Lock or a Sunday stream while he recovers from the hip injury. If you started Brown, you need a receiver from the leftover games or from <a href="waiver.html">waivers</a> while he recovers from the high-ankle sprain. If you sat Purdy, you left three touchdowns on the table.</p>
      <p>Waiver order this weekend should start with the names this opener actually moved. Then go back to the Week 1 waiver mash for the names that were already consensus adds before kickoff. Check the <a href="injuries.html">injury report</a> before you lock a Sunday flex. The <a href="week1-matchups.html">matchup board</a> still covers every game that has not kicked.</p>
      <p class="sources">Reporting drawn from NFL Network, NBC Sports, The Athletic, club statements, and the BK News wire. Scores: Seahawks 13, Patriots 10; 49ers 27, Rams 7.</p>
    </article>
    """


def write_week1_opening(b):
    extra = also_on_desk(b.FB_ALSO.get("week1-opening.html") or [])
    body = opening_article_html() + extra
    b.write(
        "week1-opening.html",
        b.page(
            "Week 1 Opening",
            "week1-opening.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Weekly", "weekly.html"),
                ("Opening", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Weekly", "https://ballkeep.com/weekly.html"),
                    ("Opening", "https://ballkeep.com/week1-opening.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/week1-opening.html",
                    DEK,
                    published=PUBLISHED,
                    modified=PUBLISHED,
                    image=OG_IMAGE,
                    brand="Ball Keep",
                    section="Week 1",
                ),
            ],
            og_type="article",
            published=PUBLISHED,
            modified=PUBLISHED,
            image=OG_IMAGE,
            body_class="opening-page",
        ),
    )
