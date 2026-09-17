"""The Long Game: a long-term Superflex dynasty strategy essay."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "Hold the years in your hands when the week is shouting."
DEK = (
    "A Superflex room is a years-long argument that happens to get interrupted every Sunday, "
    "and the work after Week 1 is remembering which interruptions deserve a new chair and which "
    "ones are just weather moving across a board you already trusted in August."
)
PUBLISHED = "2026-09-17T12:00:00Z"
OG_IMAGE = "img/players/josh-allen.png"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def long_game_teaser():
    return f"""
    <a class="opening-teaser recap-teaser long-game-teaser" href="the-long-game.html">
      <img src="{OG_IMAGE}" alt="Josh Allen" width="160" height="160" />
      <div>
        <p class="k">Articles · The Long Game · Thursday, Sep 17</p>
        <h2>Hold the years when the week is shouting.</h2>
        <p>Superflex strategy after one loud week. Youth, picks, BK Value, and the names the opener tried to make you forget.</p>
      </div>
    </a>
    """


def long_game_article_html() -> str:
    return f"""
    <article class="opening essay recap">
      <p class="opening-kicker">Articles · The Long Game · Thursday, September 17, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Thursday while Week 2 was still a card and The Keep was still the long board</p>

      <div class="photo-row" aria-label="Faces from the long board">
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("jamarr-chase", "jpg", "Ja'Marr Chase")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
        {_shot("ashton-jeanty", "jpg", "Ashton Jeanty")}
        {_shot("tetairoa-mcmillan", "jpg", "Tetairoa McMillan")}
        {_shot("brock-bowers", "jpg", "Brock Bowers")}
      </div>
      <p class="photo-cap">Allen, Robinson, Chase, Maye, Williams, Jeanty, McMillan, Bowers. The Keep still starts with years, even after a week that tried to start with noise.</p>

      <p class="lede">I have sat in enough Superflex rooms to know the sound a league makes after the first Sunday, and it is always the same sound, a mix of people who just watched a 59-point night and people who just watched a favorite look ordinary, and both groups want the board to move tonight because waiting feels like losing even when waiting is the whole point of a dynasty startup.</p>

      <p>A redraft room is allowed to panic because the season is the product, and if Christian McCaffrey looks like himself again or if A.J. Brown is in a boot, that room has twelve weeks to spend the news. A Superflex dynasty room bought years. You paid for Josh Allen's remaining prime and Bijan Robinson's twenties and Ja'Marr Chase's route tree and a pile of 2026 and 2027 picks that do not care what Charlotte did on Sunday. The Keep is built for that horizon. Weekly is built for the next kickoff. If you mix those two clocks you will sell the right player at the wrong time and feel clever about it until next August, when the name you dumped for a waiver dart is still first-round money and the dart is a memory.</p>

      <h2>Weather and climate</h2>
      <p>Week 1 is weather. The Keep is climate. Chicago hanging 59 on Carolina is a real afternoon, and Caleb Williams deserved every word The Recap spent on him, and the Bears skill names deserve to be started this week because the tape said so. Climate is the question of whether you would still take Williams over a proven Superflex chair in a startup that drafted last May, and that question moves slower than a box score, which is why The Keep still has him inside the top ten after one carnival and why the waiver mash is allowed to chase Kaelon Black without promoting him into the long 400 overnight.</p>
      <p>Drake Maye threw three picks in Seattle and the rest-of-season Superflex board still has to live with the arm that made rooms take him in the first round all summer. The Keep dropped him because the night was loud and the hip next to him on the New England sideline changed the offense, and that drop is honest. A long-term room that now wants to sell Maye for a mid first and a dart is answering weather with a climate decision, and those are the trades that look like process in September and look like a hole in 2028. Hold the years unless someone is paying you climate money for weather fear.</p>

      <h2>What a win-now room is actually buying</h2>
      <p>If your Superflex league is trying to win 2026, you already know the feeling, because you can taste it in the way people talk about Kenneth Walker after 173 yards in Denver and the way they talk about Puka Nacua after a quiet Thursday in Melbourne, and both conversations are about this year first. A win-now room should spend BK Value on the names that still play sixty snaps in December. That can mean buying a veteran who just had an ugly opener while the other manager is staring at a single box score. That can mean selling a rookie spike to a rebuilder who just watched a highlight and thinks a career just started on a Sunday afternoon. The Market is the page for those two sentences. The Long Game is the reminder that even a win-now room still has a taxi and a 2027 first, and those pieces are how you stay a win-now room next September instead of a team that mortgaged the building for one bye week.</p>
      <p>Patrick Mahomes played through a brace and handed the ball to Walker, and every Superflex contender in America wanted that backfield for three hours. Climate says Mahomes is still the kind of quarterback you build a decade around, and weather says Walker just became expensive in a way that will fade if Kansas City goes back to committee language in Week 4. Buy the decade if the price is a win-now piece you can replace. Sell the spike if the other manager is paying you a first plus a young starter because he watched Monday Night Football with the volume up.</p>

      <figure>
        <div class="photo-pair">
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
          {_shot("puka-nacua", "jpg", "Puka Nacua")}
        </div>
        <figcaption>Walker after Denver, Nacua after Melbourne. One night each. Both still have years, and the room that remembers that will still have them when the highlight cools.</figcaption>
      </figure>

      <h2>Youth is inventory, and inventory needs a shelf</h2>
      <p>Rebuilders love to say they are collecting youth, and then they collect so much youth that the roster looks like a prospect catalog with no one who can start in a Superflex slot in November. The Keep is 400 names deep because a real startup drafts that far, and the late names are the shelf. Tetairoa McMillan and Ashton Jeanty and the rest of the 2026 class are the reason you held picks in the first place. They are also the reason you should stop treating every Week 1 target share like a referendum on a career. A rookie who saw four targets in a bad script still has the same age and the same draft capital he had in August, and those two facts are the long-term ones. A rookie who exploded in Week 1 still has to do it again in a colder game, and the Keep rank already baked in a lot of that hope before the opener.</p>
      <p>The shelf is the taxi, the last roster spots, and the seconds and thirds you have not spent yet. If you are rebuilding, your job is to turn aging win-now value into that shelf without falling in love with the first shiny waiver name that The Recap mentioned. Jalen Coker can lead a Week 2 wire and still be a dart. Kaelon Black can cost FAAB and still be a handcuff with a pretty Monday. Those adds are correct for this week. They become a long-term mistake when they replace a pick or a young starter you meant to keep through 2028. Put the dart on the shelf. Leave the years in the starting lineup.</p>

      <h2>Picks are oxygen</h2>
      <p>Future picks are the only asset in a Superflex league that get younger every season, and I mean that in the simple way a room understands when the 2027 first is still sitting there in the chat after a bad Sunday and nobody can injure it. A contender who trades two future firsts for a rental tight end in Week 2 is buying a month and selling a draft. Sometimes that is the right month. Usually it is a manager who just watched Brock Bowers leave a game and decided the championship window was a weekend. Bowers is a Keep name with years. A rental is a week. Pay Keep prices for Keep names. Pay weekly prices for weekly names. The trade calculator on this site will tell you when the two sides are within 8%, and that number is a climate number, so use it when the deal is about 2027 and ignore the urge to add 20% because somebody scored last night.</p>
      <p>If you are rebuilding, you want those firsts the way a person wants air in a closed room, and you should take them from the manager who just decided his window is now. Give him the aging running back who just had 20 carries. Take the 2027 first and a young receiver who still has a fifth-year option. That is the whole rebuild. It is boring on purpose. Boring is how you still have a roster when the loud teams have turned their taxis into empty folders.</p>

      <h2>Quarterbacks are the furniture</h2>
      <p>Superflex is a quarterback league that also happens to have running backs and receivers, and I say that as someone who still has Bijan second on The Keep, because the skill is real and the clock on a back is real too. The furniture of the room is still the passers. Josh Allen is first because the rooms that publish 400 names keep putting him first. Jayden Daniels and Caleb Williams and Drake Maye are the next generation of furniture, and furniture is a word I am using on purpose, because you do not throw out a table because dinner was messy. You clean the table. You start Maye this week or you sit him this week based on the matchup and the hip next to him. You do not trade the table for a nice lamp unless the other manager is giving you two tables.</p>
      <p>The 1QB calculator on this site taxes passers to 38% of Superflex BK Value because a one-quarterback league treats a passer like another starter. Your Superflex league does the opposite. If someone offers you a pretty skill package for your QB2, open The Keep, look at how deep the quarterback room goes, and ask whether you can still start two passers in December. If the answer depends on a rookie who has not taken a regular-season snap, you are sitting on the floor and calling it a swap.</p>

      <h2>How to use the boards without letting them use you</h2>
      <p>The Keep is the long Super Aggregate, forty tapes, half the vote in the long core, and it is the page you should open when a trade is about the next three seasons. The Board is this year in PPR, and it is the page you should open when a redraft friend wants to talk shop or when your Superflex league still has a weekly lineup that scores like PPR. Weekly, Week 2 DST, Week 2 Kickers, and Waivers are the stream. The Recap is the story of the week that just ended. The Market is the buy and sell list after that story. The Method is how the mash is built. Articles is where this essay lives, next to those pages, so a person can read the years and the week in the same house.</p>
      <p>A good long-term habit is to make one climate decision and one weather decision each week, and to write them down so you can see when you started mixing them. Climate: I will not sell Maye for less than a late first plus a young starter. Weather: I will start the 49ers defense and I will bid on Black if McCaffrey's workload looks shared. That is a complete week. Ten weather decisions and zero climate decisions is how a dynasty roster turns into a redraft roster with extra bench spots.</p>

      <h2>The names the opener tried to make you forget</h2>
      <p>Every opening week produces a list of people the chat wants to bury, and this one already has a few, because Melbourne was ugly for the Rams skill group and Seattle was ugly for Maye and the Cardinals beat a favorite and now half the league wants to talk about Jacoby Brissett like a long-term quarterback plan. Hold the Rams names until the Giants game on Monday tells you something that one Thursday cannot. Hold the young receivers on bad scripts until the target share actually leaves. Sell the veteran who just had a career night only if the other manager is paying you the version of him that exists in his memory, the 2023 tape, the highlight that made him draft the player in the first place. Memory is expensive. You should charge for it.</p>
      <p>A.J. Brown in a boot is a redraft emergency and a dynasty pause. You hold a Keep receiver through a three-to-four week window unless the return is a first and you already have three other starters who can carry the slot. Most rooms have two real receivers and a prayer. Keep the prayer on the bench, start the healthy ones, and let Weekly tell you who those healthy ones are this Sunday.</p>

      <h2>A closing that sounds like a person</h2>
      <p>I keep coming back to the simple picture of a startup draft in late summer, the one where you sat there with a queue and a belief about 2028, and then September arrived and a few box scores tried to evict that belief. You are allowed to update. You are supposed to update. Updating is why The Keep rebuilt after Week 1 and why Maye moved and why Walker climbed and why the waiver has a new first name. Updating is different from abandoning the years you paid for. Read the week. Start the week. Trade the week only when the other side is paying you in years.</p>
      <p>If you want the mash, it is on The Keep. If you want the stream, it is on Weekly. If you want the story of the opener, it is on The Recap. If you want to write us about a rank, The Method still has the address. This page is for the manager who is still thinking about 2028 on a Thursday in September, which is the manager a Superflex league is supposed to be full of, even when the week is shouting and the waiver is open and the chat has already decided that one Sunday was a career.</p>
    </article>
    """


def write_the_long_game(b):
    extra = also_on_desk(b.FB_ALSO.get("the-long-game.html") or [])
    body = long_game_article_html() + extra
    b.write(
        "the-long-game.html",
        b.page(
            "The Long Game",
            "the-long-game.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", "articles.html"),
                ("The Long Game", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                    ("The Long Game", "https://ballkeep.com/the-long-game.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/the-long-game.html",
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
