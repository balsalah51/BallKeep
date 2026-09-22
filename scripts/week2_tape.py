"""The Second Sunday: a long Week 2 essay after every game has a final."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "Sixteen more scores, and a Monday that finally looked like a favorite."
DEK = (
    "Buffalo hung 41 on Thursday. Carolina hung 34 in Atlanta. San Francisco "
    "was almost perfect. Kansas City needed overtime. Los Angeles closed it "
    "28-6. This is the full Week 2 tape, written after the last snap."
)
PUBLISHED = "2026-09-22T16:00:00Z"
OG_IMAGE = "img/players/matthew-stafford.png"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def tape_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="week2-tape.html">
      <img src="{OG_IMAGE}" alt="Matthew Stafford" width="160" height="160" />
      <div>
        <p class="k">Week 2 · The Second Sunday · Tuesday, Sep 22</p>
        <h2>Rams 28-6. Mash 11-5. Sixteen scores are in.</h2>
        <p>Stafford threw four. Young hung 34 in Atlanta. Williams left on a cart. The whole week, written after Monday.</p>
      </div>
    </a>
    """


def tape_article_html() -> str:
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 2 · The Second Sunday · Tuesday, September 22, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Tuesday after Los Angeles finished New York</p>

      <div class="score-row recap-scores">
        <div class="score-card is-final"><p class="when">Thu · Prime</p><p class="result">Bills 41, Lions 31</p></div>
        <div class="score-card is-final"><p class="when">Sun · FOX</p><p class="result">Panthers 34, Falcons 3</p></div>
        <div class="score-card is-final"><p class="when">Sun · NBC</p><p class="result">Chiefs 33, Colts 30 OT</p></div>
        <div class="score-card is-final"><p class="when">Mon · ESPN</p><p class="result">Rams 28, Giants 6</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from Week 2">
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("bryce-young", "jpg", "Bryce Young")}
        {_shot("matthew-stafford", "png", "Matthew Stafford")}
        {_shot("davante-adams", "png", "Davante Adams")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
      </div>
      <p class="photo-cap">Allen, Young, Stafford, Adams, Gibbs, McCaffrey, Mahomes, Williams. The week started with five scores in a new building and ended with four in an old one.</p>

      <p class="lede">I have now watched two full weeks of this season, and the feeling after the second one is quieter than the feeling after the first, because opening week is a carnival and Week 2 is a ledger, and a ledger asks you to write the number next to the name and then sit with it long enough that you remember who you thought they were in August.</p>

      <p>The mash on this card finished eleven and five. Buffalo, Cincinnati, New England, Green Bay, Philadelphia, Denver, Seattle, Dallas, San Francisco, Kansas City, and Los Angeles paid. Atlanta, Baltimore, Chicago, Tampa Bay, and the Chargers missed. That is a grown-up record for a public pile of writers and a market. It is also a reminder that Carolina can hang 34 in a building the market still liked, and that a 59-point opener can turn into a 9-3 rain night with a quarterback on a cart.</p>

      <h2>Thursday already had a memory</h2>
      <p>Buffalo 41, Detroit 31, in a stadium that still smelled like paint. Josh Allen accounted for five scores. James Cook ran for 134. Jahmyr Gibbs had to spend his 156-yard opener on a short week after overtime, and he spent it, and it was still not enough. The new Highmark got the kind of first regular-season night a league dreams about when it spends that much money on a building. Fantasy rooms already knew the start list. They still know it. Allen is QB1 on the long board and RB2 is the language we now print next to Cook on a list that has a memory.</p>

      <h2>Sunday at one, where the writers got loud</h2>
      <p>Carolina 34, Atlanta 3 is the sentence that will live in every room until November. Bryce Young threw for 287 and three, two of them to Darren Waller. Jalen Coker played 76 percent of the snaps after an eight-catch, 138-yard opener. Devin Lloyd ran an interception back. Cooper Rush threw for 86 with two picks, and Michael Penix and Tua Tagovailoa were inactive again. Bijan Robinson was held to 72 on the ground in a game that asked him to be the offense. The mash took the building. The building lost by 31. Young is 5-1 against this club. Superflex rooms that still have him on the wire should feel a little sick.</p>
      <p>New Orleans 24, Baltimore 17. Tyler Shough threw for 252 and a score, then sneaked it with 1:28 left. Chris Olave had 86 and a touchdown. Zay Flowers sat with a hamstring. Rashod Bateman caught seven for 88 and a score and still left on the losing side. Every full card we mashed took Baltimore. The Saints took the building. Superflex streams that added Shough after Detroit just cashed a road game in a place that is supposed to be winter.</p>
      <p>Minnesota 9, Chicago 3, in the rain. Isaiah Rodgers recovered a fumble and blocked a late kick. Caleb Williams left with a right hamstring, cart, towel over the face, 15 of 26 for 138 and five carries for 42. Fifty-nine points from the opener stayed in Charlotte. D'Andre Swift, who had three scores in that carnival, spent Sunday looking like a back in a game that would not let anyone run. The Keep still has Williams inside the years. Weekly will have to live without him until the hamstring says so.</p>
      <p>Cincinnati 20, Houston 6. Joe Burrow found Ja'Marr Chase twice. The buy from the twelve-yard opener came due, and the mash cashed it. C.J. Stroud's home night asked a room that drafted a ceiling to sit with a floor. Pittsburgh went to New England and lost 20-3. TreVeyon Henderson ran 39 yards for a score in his season debut. Eli Ponder took a fumble the other way. Drake Maye still threw a bad ball and still won ugly, which is the chapter New England will take after Wednesday in Seattle. Green Bay 20, the Jets 17, in overtime. Cleveland 23, Tampa Bay 19, after a lightning delay that lasted two hours and twelve minutes, Deshaun Watson two scores, Denzel Boston 55 yards, Baker Mayfield's last ball past Emeka Egbuka. Philadelphia 24, Tennessee 20, Hurts to Darius Cooper with nine seconds left, DeVonta Smith ten for 117, turf at 157 degrees.</p>

      <div class="photo-row">
        {_shot("jalen-coker", "jpg", "Jalen Coker")}
        {_shot("treveyon-henderson", "jpg", "TreVeyon Henderson")}
        {_shot("jamarr-chase", "jpg", "Ja'Marr Chase")}
        {_shot("tyler-shough", "jpg", "Tyler Shough")}
      </div>
      <p class="photo-cap">Coker in Atlanta. Henderson in Foxborough. Chase in Houston. Shough in Baltimore. Sunday at one already had a waiver list hiding inside it.</p>

      <h2>Sunday late, where the card got wide</h2>
      <p>Denver 20, Jacksonville 13. Jaylen Waddle caught eight for 138. J.K. Dobbins left with a hamstring. Jonah Coleman punched a 3-yard score and caught all three of his targets. Jacksonville's nine-game regular-season streak ended at altitude. Las Vegas 26, Los Angeles 14. Kirk Cousins found Cody White twice. Jim Harbaugh's habit against this opponent broke in a building that was supposed to be safe. Seattle 31, Arizona 7. Drew Lock threw three scores on the road. Jaxon Smith-Njigba stayed the target. Dallas 37, Washington 20. Jayden Daniels left with the left elbow again, the same elbow that already cost him a month last year. San Francisco 35, Miami 13. Brock Purdy went 20 of 22 for 287, two throw scores and a run score. Christian McCaffrey became the fourth-fastest player in the Super Bowl era to 100 career touchdowns. The widest number on the card was also the cleanest vote.</p>
      <p>Sunday night was Kansas City 33, Indianapolis 30, in overtime. Patrick Mahomes threw for 382 and three. Kenneth Walker ran for 117 and caught six for 61, including the 22-yarder that set up Harrison Butker's 40-yard kick as time expired. Travis Kelce caught nine for 101 and a score. Jonathan Taylor scored twice and still left 0-2. The mash took Kansas City and Kansas City needed every minute, which is the kind of night that makes a room believe in a back and a quarterback at the same time.</p>

      <h2>Monday, at last</h2>
      <p>Los Angeles 28, New York 6. Matthew Stafford went 22 of 31 for 327 and four touchdowns, two of them to Davante Adams, one to Kyren Williams from ten yards, one to Terrance Ferguson from five. Adams caught eight for 195. Stafford moved into sixth place in league history with 427 career touchdown passes. Jaxson Dart grabbed for his left knee on the first series after Byron Young and Josaiah Stewart hit him high and low. Jameis Winston threw 11 of 27 for 111 and a pick. Puka Nacua was inactive with the hip. Aaron Donald played. The Rams are 1-1. The Giants are 1-1. Melbourne is a Thursday that now has a Monday next to it, and the Monday looked like the club people drafted in August.</p>
      <p>I told rooms on Wednesday to put Nacua back in and to hold Adams and Kyren. Adams paid immediately. Nacua sat. Kyren caught a score. That is a Week 2 sentence. The tree is still Nacua's when he dresses. The tree was Adams's when he did not. Buy the missed night. Start the veteran who just caught 195. That is the whole Monday market in three lines.</p>

      <figure>
        <div class="photo-pair">
          {_shot("matthew-stafford", "png", "Matthew Stafford")}
          {_shot("davante-adams", "png", "Davante Adams")}
        </div>
        <figcaption>Stafford after Australia, then four scores. Adams after a quiet opener, then 195 and two. Monday finally looked like a favorite.</figcaption>
      </figure>

      <h2>What the week did to the rooms</h2>
      <p>Two young quarterbacks left on carts or with a trainer. Williams and Daniels are Keep names with weeks they cannot play. Superflex rooms that panic after 0-2 and a medical tent will sell years for a stream. That is the trade you want to be on the other side of. Bryce Young just put up back-to-back explosions and is still sitting in a lot of those same rooms. TreVeyon Henderson announced himself. Jonah Coleman is the Denver add. Jalen Coker is still the Carolina add if anyone left him out there after 138. Chase reminded everyone why the twelve-yard opener was a buy.</p>
      <p>The lists on this site now print RB2 next to the second back and WR3 next to the third receiver, because a rank without a chair is a number that makes you do extra math at the table. The Keep still opens with years. The Board still opens with this season. Weekly still opens with Sunday. Hot 'n' Cold rebuilt this morning from the card you just read. The <a href="week2-ledger.html">Week 2 ledger</a> is the page for what those lists learned. This page is the page for the week itself.</p>

      <div class="ramif">
        <h3>The sixteen, closed</h3>
        <ul>
          <li>BUF 41, DET 31. Allen five scores. Cook 134.</li>
          <li>CAR 34, ATL 3. Young 287 and three. Waller twice.</li>
          <li>NO 24, BAL 17. Shough sneak, 1:28.</li>
          <li>MIN 9, CHI 3. Rain. Williams hamstring.</li>
          <li>CIN 20, HOU 6. Burrow to Chase twice.</li>
          <li>NE 20, PIT 3. Henderson 39-yard debut.</li>
          <li>GB 20, NYJ 17 OT.</li>
          <li>CLE 23, TB 19. Lightning, then Boston 55.</li>
          <li>PHI 24, TEN 20. Hurts to Cooper, nine seconds.</li>
          <li>DEN 20, JAX 13. Coleman after Dobbins.</li>
          <li>LV 26, LAC 14. Cousins to White twice.</li>
          <li>SEA 31, ARI 7. Lock three scores.</li>
          <li>DAL 37, WAS 20. Daniels elbow.</li>
          <li>SF 35, MIA 13. Purdy 20 of 22. CMC 100th.</li>
          <li>KC 33, IND 30 OT. Mahomes 382. Walker 117. Butker 40.</li>
          <li>LAR 28, NYG 6. Stafford four. Adams 195. Dart knee.</li>
        </ul>
      </div>

      <h2>A last look, because a second week deserves one</h2>
      <p>I keep a private list of pictures from a week that now has a full card. Allen pointing in a building that still smelled like paint. Young walking off Mercedes-Benz like he owns the place. Williams on a cart in the rain. Henderson hitting the edge in Foxborough. Adams with two fingers up on a Monday that finally looked like August. Stafford, old and exact, throwing the kind of ball that makes a room remember why they waited. Those pictures are why this page is crowded. A website that only prints ranks starts to feel like a filing cabinet. A website that also prints the week starts to feel like a room you can sit in on a Tuesday.</p>
      <p>The <a href="weekly.html">weekly boards</a> still carry Week 2 on them, because the card just closed and the next Sunday is still a rumor. The <a href="hot-n-cold.html">Hot 'n' Cold</a> list moved this morning. The <a href="week2-matchups.html">prediction page</a> now has every receipt under the table. The Keep and The Board rebuilt from the public lists we can still read. Spend the ranks. Spend the story. Then spend the wire on the names this card actually moved.</p>
      <p class="sources">Scores and notes from Reuters on the Rams, ESPN on Sunday takeaways and the NFC injuries, NFL.com on what Sunday taught, Sportsnet on the early window, CBS Sports on Monday night, Sports Illustrated on Coleman, and the published boxes. Mash on the finished card: 11-5. The opener still lives on <a href="the-recap.html">The Recap</a>. The argument for every pick still lives on <a href="week2-matchups.html">Week 2 Predictions</a>.</p>
    </article>
    """


def write_week2_tape(b):
    extra = also_on_desk(b.FB_ALSO.get("week2-tape.html") or [])
    body = tape_article_html() + extra
    b.write(
        "week2-tape.html",
        b.page(
            "The Second Sunday",
            "week2-tape.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Articles", "articles.html"),
                ("The Second Sunday", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Articles", "https://ballkeep.com/articles.html"),
                    ("The Second Sunday", "https://ballkeep.com/week2-tape.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/week2-tape.html",
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
