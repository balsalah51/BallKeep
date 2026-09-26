"""The Recap: a long Week 1 essay after every game has been played."""
from __future__ import annotations

from seo import (
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
)

HEADLINE = "Sixteen scores, one opening week, and a league that already has a memory."
DEK = (
    "Seattle closed Wednesday 13-10. San Francisco left Melbourne 27-7. "
    "Chicago hung 59 in Charlotte. Kansas City sent Kenneth Walker through Denver "
    "for 173 yards on Monday night. This is the full Week 1 tape, written after "
    "the last snap, with the pictures still warm."
)
PUBLISHED = "2026-09-15T18:00:00Z"
OG_IMAGE = "img/players/caleb-williams.jpg"


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def _film(youtube_id, title):
    return (
        f'<figure class="recap-film">'
        f'<div class="video-wrap">'
        f'<iframe src="https://www.youtube.com/embed/{youtube_id}" title="{title}" '
        f'loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
        f'gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
        f"</div>"
        f"<figcaption>{title}</figcaption>"
        f"</figure>"
    )


def recap_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="the-recap.html">
      <img src="{OG_IMAGE}" alt="Caleb Williams" width="160" height="160" />
      <div>
        <p class="k">The Recap · Tuesday, Sep 15</p>
        <h2>Seahawks 13, Patriots 10. Chicago 59. Walker 173.</h2>
        <p>Sixteen scores are in. Read the whole week, then spend the wire on Coker, Black, and the names the tape actually moved.</p>
      </div>
    </a>
    """


def recap_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 1 · The Recap · Tuesday, September 15, 2026</p>
      <h1>{HEADLINE}</h1>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Tuesday after Kansas City finished Denver</p>

      <div class="score-row recap-scores">
        <div class="score-card"><p class="when">Wed · NBC</p><p class="result">Seahawks 13, Patriots 10</p></div>
        <div class="score-card"><p class="when">Thu · Netflix</p><p class="result">49ers 27, Rams 7</p></div>
        <div class="score-card"><p class="when">Sun · FOX</p><p class="result">Bears 59, Panthers 37</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">Chiefs 31, Broncos 10</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from Week 1">
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("jalen-hurts", "png", "Jalen Hurts")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
      </div>
      <p class="photo-cap">Smith-Njigba, Purdy, Williams, Walker, Gibbs, Allen, Hurts, Mahomes. The first Sunday of a new year already has a cast.</p>

      <p class="lede">A football week used to begin on Thursday and end on Monday, and for most of the country that is still how the clock feels. This one began on a Wednesday in Seattle, crossed an ocean on Thursday, spent a long American Sunday arguing with itself, and closed on a Monday night in Kansas City with a running back who used to wear Seattle green. Sixteen scores are in. The waiver list has a new first name. The rest-of-season boards have to listen to the tape they just watched.</p>

      <p>I want to write this the way a person writes after sitting with a whole slate, which means I will linger. Box scores travel fast. The feeling of a week travels slower. Wednesday still tastes like a Super Bowl rematch that turned into a backup-quarterback story. Thursday still tastes like Melbourne lights and a 27-7 score that looked even larger in person. Sunday tasted like Charlotte fireworks and a Cardinals club that refused the script in Los Angeles. Monday tasted like Kenneth Walker finding the edge again and again while Patrick Mahomes, brace on the left knee, looked like a man glad to hand the ball off.</p>

      {_film("2kwY6ve5E88", "Josh Allen tape. Buffalo already has four scores in the book, and Thursday night in Highmark will ask for more.")}
      {_film("sA1MsnZ-Dvw", "Drake Maye finds Harris and the dive still looks like a comic-book panel. The three picks in Seattle sit next to that arm.")}

      <h2>Wednesday, and the night the rematch got small</h2>
      <p>Seattle 13, New England 10. The number is modest. The evening was not. Sam Darnold lasted one series, left after a sack, and spent the rest of the night in the locker room with a hip that the club later described as structurally clean and still serious enough to keep him out of Arizona. Drew Lock finished the comeback. The Seahawks defense stole the last throw. Drake Maye, who has been living in the first sentence of every 2026 quarterback argument, threw three fourth-quarter interceptions and said afterward that those mistakes were unacceptable. He was right, and he was also a twenty-three-year-old playing his first September snap of a year that people had already decided belonged to him.</p>
      <p>A.J. Brown went down in the third quarter with a right high-ankle sprain and left in a walking boot. Ian Rapoport and Mike Garafolo put a three-to-four-week window on it. New England already has to live without that voice on the outside. Jaxon Smith-Njigba kept working after Lock entered, which is the kind of small professional fact that fantasy rooms should tattoo on a wrist: the target stays the target even when the quarterback changes. Romeo Doubs and DeMario Douglas are the names the wire reached for before the rest of the league even kicked off. Those names still matter. They now sit next to a longer list.</p>

      <figure>
        <div class="photo-pair">
          {_shot("drake-maye", "jpg", "Drake Maye")}
          {_shot("a-j-brown", "png", "A.J. Brown")}
        </div>
        <figcaption>Drake Maye and A.J. Brown. One night in Seattle already changed two Sunday lineups and a month of New England receiving depth.</figcaption>
      </figure>

      <h2>Thursday, and the first regular-season game on Australian grass</h2>
      <p>San Francisco 27, Los Angeles 7. Brock Purdy completed 25 of 34 for 205 yards and three touchdowns. Christian McCaffrey played. George Kittle, back from a January Achilles tear, caught two balls for twelve yards and looked like a man the staff was still metering. Kyle Shanahan said they had to be smart with those snaps. That sentence is going to follow Kittle for a month, and it should. Kaelon Black, the third-round back from Indiana, took fourteen carries and a target and left Melbourne as the clearest 49ers handcuff in the building. Jordan James truthers can keep the argument. The snap chart already voted.</p>
      <p>Matthew Stafford and the Rams never found a second half. Puka Nacua, Kyren Williams, and Davante Adams already spent their Week 1 snaps in a seven-point night. Those points are in the book. The temptation after an ugly Thursday is to treat a whole room like a sinking boat. Hold the names. Week 2 is New York Giants on a Monday, at home, with a chance to look like themselves again. De'Zhaun Stribling left on a cart with a non-contact ankle. Shanahan said the Achilles is intact. Jake Tonges sprained an MCL. The 49ers won big and still sent two young pass-catchers to the trainer.</p>

      <figure>
        <div class="photo-pair">
          {_shot("brock-purdy", "jpg", "Brock Purdy")}
          {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
        </div>
        <figcaption>Purdy banked three scores. McCaffrey shared the Australia night with Kaelon Black, who is about to cost real FAAB.</figcaption>
      </figure>

      <h2>Sunday morning, when the league finally sounded like a league</h2>
      <p>Jacksonville 34, Cleveland 10. The Jaguars did what the Week 1 defense boards asked them to do, Trevor Lawrence had the kind of clean afternoon that Liam Coen's second year is supposed to look like, and the Browns spent the day chasing. Rooms that streamed Jacksonville already cashed. Rooms that sat them to be clever now have Denver on the road, which is a colder ask and a different stream.</p>
      <p>Detroit 31, New Orleans 30, in overtime. Jared Goff found Amon-Ra St. Brown in the extra period. The Saints, down 21-0, let Tyler Shough throw fifty-six times for 410 yards and three scores. Devaughn Vele caught seven of nine for 69 and a touchdown on 82 snaps. Chris Olave still lives in that offense. Vele now lives next to him. The Lions survived two-point chaos and will take that survival to Buffalo on a short week, which is a vicious way to start a Thursday Night Football season. Jahmyr Gibbs already has his first chapter. The next one is Highmark Stadium, new grass, Josh Allen at home.</p>
      <p>Baltimore 41, Indianapolis 23. Lamar Jackson's club looked like a club that had been waiting since August. The Colts scored enough to keep the lights interesting and still left Baltimore with a deficit that felt larger than eighteen. Zay Flowers and Ja'Kobi Lane both picked up the kind of injury language that sends rooms toward Rashod Bateman. Watch the Wednesday report. The Ravens host New Orleans in Week 2, and that is a stream if you like points after turnovers.</p>
      <p>Buffalo 36, Houston 31. Josh Allen accounted for four scores on a night when the Texans' defense was supposed to be the grown-up in the room. C.J. Stroud threw for 274 and two. David Montgomery found the end zone three times. Houston lost and still looked like an offense that will score on people. Buffalo won and still looked like a defense that will give points back. Thursday against Detroit is going to be loud.</p>

      <div class="photo-row">
        {_shot("lamar-jackson", "jpg", "Lamar Jackson")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("amon-ra-st-brown", "jpg", "Amon-Ra St. Brown")}
        {_shot("trevor-lawrence", "jpg", "Trevor Lawrence")}
      </div>
      <p class="photo-cap">Jackson, Allen, St. Brown, Lawrence. Four Sunday afternoons that already have a shape.</p>

      <h2>Charlotte, and the highest-scoring Week 1 game the league has ever put on a ledger</h2>
      <p>Chicago 59, Carolina 37. Reuters called it a record. The building in Charlotte felt it in real time. Caleb Williams threw for two scores and ran for two more, 21 of 29 for 269, plus 65 on the ground. D'Andre Swift ran eighteen times for 124 and three touchdowns. Kyle Monangai added 100 yards on ten carries, one of them a 61-yard walk-in. Bryce Young threw three scores, two of them to Jalen Coker, who caught eight of nine for 138 yards and those two touchdowns and left the night as the most obvious waiver name in America. Tetairoa McMillan caught five for 75. Coker led every major receiving number. Sports Illustrated asked the question out loud: is he the Panthers' WR1. The snap chart is still going to love McMillan. The wire is going to love Coker. Both things can sit in the same paragraph.</p>
      {_film("vET4gxfvkso", "Caleb Williams scrambling until the field opens. Charlotte already has a 59-point story, and this is the kind of play that story is built from.")}

      <p>I keep thinking about what a 59-point night does to a fantasy room, because it makes people believe in a whole offense for four months, and sometimes that belief is correct. Chicago hosts Minnesota in Week 2, which is a different animal than Carolina at home, and Cairo Santos is on every kicker streamer list while the Bears defense that just gave up 37 has to be treated like a matchup instead of a season-long chair. The skill names earned another week. The defense has to earn the next one against a club that already remembered how to finish.</p>

      <figure>
        <div class="photo-pair">
          {_shot("caleb-williams", "jpg", "Caleb Williams")}
          {_shot("dandre-swift", "jpg", "D'Andre Swift")}
        </div>
        <figcaption>Williams and Swift turned Charlotte into a carnival. Coker, on the other sideline, turned the waiver wire into a footrace.</figcaption>
      </figure>

      <h2>The rest of the one o'clock window, because the rest still happened</h2>
      <p>Pittsburgh 20, Atlanta 13. The Steelers defense scored the kind of afternoon that Week 1 streamers dream about. Tua Tagovailoa, now in Atlanta, picked up oblique language later in the week and put the Falcons quarterback room on the injury report. Atlanta still gets Carolina at home in Week 2. Pittsburgh goes to New England. The market has the Patriots as a home favorite, which is a sentence that would have sounded like fan fiction in July and now has a 13-10 Seattle loss sitting behind it.</p>
      <p>New York Jets 23, Tennessee 10. The Jets looked like a club that could tackle. The Titans looked like a club still introducing themselves. Green Bay visits the Jets in Week 2, and that game will tell us more about both rooms than this one did.</p>
      <p>Cincinnati 33, Tampa Bay 27. Joe Burrow's club won a track meet. Tampa Bay still looks like a club that can score. Cleveland visits Tampa in Week 2, which is why every kicker and defense list in the country has the Buccaneers in bold. Chase McLaughlin is the cheap kicking name. The Bengals go to Houston, where the Texans just hung 31 on Buffalo and still lost.</p>
      <p>Philadelphia 24, Washington 22. Jalen Hurts' club survived a game that kept threatening to become a story about Washington, Jacory Croskey-Merritt scored early for the Commanders, and the Eagles closed it. Week 2 is Tennessee on the road, and the defense boards have Philadelphia first or second on almost every list I mashed, which is a stream for the rooms that already own them and a high waiver price for the rooms that do not.</p>

      <h2>Late Sunday, when the underdogs found a microphone</h2>
      <p>Arizona 26, Los Angeles Chargers 14. Jacoby Brissett and the Cardinals beat a double-digit favorite in a building that expected a parade. Trey McBride caught nine for 95 and a score on a Chargers defense that is about to host Las Vegas. The Chargers still sit high on several Week 2 DST boards because the Raiders just beat Miami and still look like a club you can hit. The Cardinals host Seattle in Week 2, which is a colder home game than this one was a road heist.</p>
      <p>Minnesota 39, Green Bay 22. Carson Wentz, the backup, walked a Packers lead into a comeback. The Vikings looked like a club that remembered how to finish. Green Bay goes to the Jets. Minnesota goes to Chicago, which just scored 59. That Bears-Vikings number is already a problem for people who want a clean script.</p>
      <p>Las Vegas 27, Miami 13. The Raiders won and Michael Mayer led the club in targets while Brock Bowers waits on a meniscus timeline that some rooms are treating as Week 2 and some rooms are treating as later. Tre Tucker ate. Malik Willis and De'Von Achane tried to make Miami's offense look like a plan. Sporting News already has San Francisco winning 38-13 next week. That is a brutal way to spend a Sunday in Santa Clara.</p>
      <p>New York Giants 28, Dallas 20, on Sunday night. The NFC East still knows how to make a prime-time game feel like a family argument. Wan'Dale Robinson is on every waiver list that still has room for a Giant. Dallas hosts Washington in Week 2. The Giants go to the Rams on Monday, which is a long flight toward a club that just lost in Australia and would like to remember what winning looks like.</p>

      <div class="photo-row">
        {_shot("trey-mcbride", "jpg", "Trey McBride")}
        {_shot("george-pickens", "jpg", "George Pickens")}
        {_shot("ceedee-lamb", "jpg", "CeeDee Lamb")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
      </div>
      <p class="photo-cap">McBride ate in Los Angeles. Pickens, Lamb, and Nacua already have their first lines in the book.</p>

      <h2>Monday night, and the back who changed cities</h2>
      {_film("fcu9F0Am9L8", "Kenneth Walker finding the edge. The cut is from a Seattle night, and Monday in Kansas City looked like the same runner in a new color.")}

      <p>Kansas City 31, Denver 10. Kenneth Walker III ran for 173 yards and two scores in a Chiefs debut that took some of the spotlight off Patrick Mahomes and then handed the spotlight right back when Mahomes, brace on the left knee, threw for 184 and two and ran for another. The Associated Press called it a dazzling debut. It looked like a man who had been waiting for a bigger alley. Walker used to be a Seahawk argument. He is now a Chiefs feature, and the rest-of-season boards have to move him. Denver scored ten and goes home to host Jacksonville, which just won 34-10 and still sits in the middle of the Week 2 DST mash because Denver at altitude is a different math than Cleveland in September.</p>
      <p>Mahomes lined up in a three-point stance beside Justin Fields on one snap and pitched to Walker for a walk-in. That is the kind of toy Andy Reid pulls out when he is having fun. Kansas City hosts Indianapolis on Sunday night. The Colts already know what a 41-point Ravens afternoon feels like. They now get Arrowhead.</p>

      <figure>
        <div class="photo-pair">
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
          {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        </div>
        <figcaption>Walker: 173 yards, two scores, new city. Mahomes: a brace, two passing scores, one rushing score, and a club that looked like itself.</figcaption>
      </figure>

      <h2>What the wire should do with all of this</h2>
      <p>Jalen Coker first. Kaelon Black second if you already roster Christian McCaffrey, and still second if you do not, because a Shanahan handcuff after fourteen carries in Australia is the kind of name that wins March arguments. Devaughn Vele if you need a receiver who just played 82 snaps. Tyler Shough in superflex rooms that lost Sam Darnold or Kyler Murray. Romeo Doubs if Green Bay's Sunday still left a hole. DeMario Douglas if Brown's boot is going to last. Wan'Dale Robinson if the Giants game convinced you. Those names are already on the <a href="waiver.html">Week 2 waiver board</a>, mashed from RotoBaller, FantasyPros, ESPN, SI, and the tape.</p>
      <p>The <a href="week2-matchups.html">Week 2 matchup board</a> has Buffalo over Detroit on Thursday, San Francisco over Miami by a wide published margin, and a few cards that still like Jacksonville in Denver. Copy the winners at the bottom if you want the list in kickoff order. The <a href="week2-dst.html">Week 2 DST board</a> leans San Francisco, Philadelphia, Tampa Bay, and Seattle. The <a href="week2-kickers.html">kicker board</a> still loves Brandon Aubrey and has learned to say Eddy Pineiro out loud.</p>

      <div class="ramif">
        <h3>Names the opener moved</h3>
        <ul>
          <li>Kenneth Walker is a Chiefs back now. Treat him like one on The Keep and The Board.</li>
          <li>Coker, Black, Vele, and Shough are the first four tickets on the wire.</li>
          <li>Darnold and Brown need IR spots or a bench you can stand to look at.</li>
          <li>Maye's three picks stay in the book. The talent stays on the roster.</li>
          <li>Chicago's skill names earned another week of trust. Chicago's defense earned a matchup test against Minnesota.</li>
          <li>Hold Nacua, Williams, Adams, and Stafford. Melbourne was one Thursday.</li>
        </ul>
      </div>

      <h2>A last look, because a week this long deserves one</h2>
      <p>I keep a private list of images from opening week. Maye on the sideline after the third pick. Purdy pointing after a score that felt easy. Williams in Chicago colors looking like the quarterback people drafted him to be. Coker with two fingers up. Walker, in red, finding the edge in a stadium that used to belong to a different kind of runner. Mahomes in the brace, smiling anyway. Those pictures are why this page is crowded. A website that only prints ranks starts to feel like a filing cabinet. A website that also prints faces and a little film starts to feel like a room you can sit in on a Tuesday.</p>
      <p>Week 2 starts Thursday in Buffalo. The <a href="weekly.html">weekly boards</a> are already rebuilt from FantasyPros ECR, thirty-six experts this week, plus RotoWire, 4for4, and the rest of the kit. The archive still holds the Week 1 DST, kicker, matchup, and opening pages, because a first week that began on Wednesday deserves a shelf. This essay is the shelf for the story. The ranks are the shelf for the next decision. Spend both.</p>
      <p class="sources">Reporting and scores drawn from PFF's Week 1 recap page, Reuters on the Bears-Panthers record, ESPN on Kansas City and the waiver wire, CBS Sports live notes, Sporting News and Sportsnaut on Week 2 cards, RotoBaller and FantasyPros on streamers and adds, Pro Football Network and 4for4 on defenses, the Associated Press on Walker and Mahomes, NFL Network and The Athletic on the Seattle injuries, and the BK News wire. Finals: SEA 13 NE 10; SF 27 LAR 7; ARI 26 LAC 14; PIT 20 ATL 13; BAL 41 IND 23; BUF 36 HOU 31; CHI 59 CAR 37; JAX 34 CLE 10; MIN 39 GB 22; LV 27 MIA 13; DET 31 NO 30; NYJ 23 TEN 10; CIN 33 TB 27; PHI 24 WAS 22; NYG 28 DAL 20; KC 31 DEN 10.</p>
    </article>
    """


def write_the_recap(b):
    extra = also_on_desk(b.FB_ALSO.get("the-recap.html") or [])
    body = recap_article_html() + extra
    b.write(
        "the-recap.html",
        b.page(
            "The Recap",
            "the-recap.html",
            body,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Weekly", "weekly.html"),
                ("The Recap", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Weekly", "https://ballkeep.com/weekly.html"),
                    ("The Recap", "https://ballkeep.com/the-recap.html"),
                ]),
                article_jsonld(
                    HEADLINE,
                    "https://ballkeep.com/the-recap.html",
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
            body_class="opening-page recap-page",
            image=OG_IMAGE,
            description=DEK,
        ),
    )
