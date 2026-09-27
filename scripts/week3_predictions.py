"""Week 3 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Bijan found 194 yards in a building that was supposed to own Thursday, and Sunday still has fifteen games left to argue with."
DEK = (
    "Atlanta hung 35-14 at Lambeau. The mash had Green Bay on every card. "
    "Penix came back. Robinson ran through a home opener that had lasted thirteen years. "
    "The rest of the slate is still Sunday and Monday."
)
PUBLISHED = "2026-09-24T14:00:00Z"
MODIFIED = "2026-09-27T14:00:00Z"
OG_IMAGE = "img/players/bijan-robinson.jpg"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week3-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=MODIFIED,
        image=OG_IMAGE,
        brand="Ball Keep",
        section="Week 3",
    ),
]


def _shot(slug, ext, name, linked=True):
    img = (
        f'<img src="img/players/{slug}.{ext}" alt="{name}" '
        f'width="320" height="320" loading="lazy" />'
    )
    if linked:
        return f'<a href="players/{slug}.html">{img}</a>'
    return f'<span>{img}</span>'


def predictions_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="week3-matchups.html">
      <img src="{OG_IMAGE}" alt="Bijan Robinson" width="160" height="160" />
      <div>
        <p class="k">Week 3 · Sunday, Sep 27</p>
        <h2>Falcons in Lambeau. Sunday is still open.</h2>
        <p>Atlanta 35-14. Bijan 194 and two. The mash took Green Bay on Thursday and missed. Fifteen games left.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 3 · Thursday is in · Sunday, September 27, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Thursday. Lambeau final added Friday. Sunday card still live.</p>

      <div class="score-row recap-scores">
        <div class="score-card is-final"><p class="when">Thu · Final</p><p class="result">ATL 35, GB 14</p><p class="meta">Bijan 194 rush · two scores · 242 as a club</p></div>
        <div class="score-card"><p class="when">Sun · FOX</p><p class="result">LAC at BUF</p><p class="meta">Allen after nine scores · Bills -7</p></div>
        <div class="score-card"><p class="when">Sun · NBC</p><p class="result">LAR at DEN</p><p class="meta">Stafford on the road · Puka still out</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">PHI at CHI</p><p class="meta">Hurts after a cart in Chicago</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from the Week 3 card">
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("michael-penix", "jpg", "Michael Penix Jr.")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("jalen-hurts", "png", "Jalen Hurts")}
        {_shot("matthew-stafford", "png", "Matthew Stafford")}
      </div>
      <p class="photo-cap">Robinson and Penix already spent Thursday. Allen, Gibbs, Mahomes, Smith-Njigba, Hurts, and Stafford still have a night in front of them.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet, and a prediction page that also prints the argument starts to feel like a room you can sit in on a Sunday morning while the first window is still a rumor. The mash above already voted. Thursday already wrote one receipt, and it wrote it in a building that had won thirteen home openers in a row. What follows is the walk through sixteen games in kickoff order, using the published cards from Bill Bender at Sporting News, Tyler Sullivan at CBS Sports, the five editors at NFL.com, the SportsLine model, the market, and the tape we just watched, with a side on every game and the winners copied at the bottom of the table for anyone who wants the list without the sentences.</p>

      <h2>Thursday: Atlanta at Green Bay. Pick: GB. Final: ATL 35-14</h2>
      <p>Every published card we mashed took the Packers. Bender printed 24-17. Sullivan printed 26-21 and still laid the points the other way. NFL.com's five editors all found a home-opener sentence and a thirteen-year habit and decided that was enough. The market had Green Bay minus 4.5 at kickoff, later minus 6.5 on some boards, and the Week 2 winners board liked the club that had just survived overtime in New York. I took Green Bay with them on Thursday afternoon because a habit that long usually gets one more night before it breaks.</p>
      <p>Friday morning now has the receipt. Atlanta 35, Green Bay 14. Bijan Robinson ran for 194 yards and two scores. The Falcons as a club ran for 242 and held Green Bay to 17 on the ground. Michael Penix Jr. came back from the injury that had left Cooper Rush and an undrafted rookie to throw the ball around in a 34-3 loss four days earlier, and he found Austin Hooper from five yards after a motion that emptied the left side of the field. Drake London caught the 40-yarder that set up the last punch. Jordan Love went 28 of 53 for 312, two scores and a pick, and Trey Smack's 47-yard try that would have tied it at ten got blocked. The mash took the building. The building lost by 21. Both clubs are 1-2, and the rest of the card is still Sunday and Monday.</p>
      <p>Fantasy rooms already know what to do with a night like that. Robinson is a start every week and now he has a Thursday chapter that looks like the one people drafted in August. London ate. Penix looked like a quarterback who had been waiting for a clean pocket. Green Bay's defense was the stream a lot of rooms paid for, and those rooms spent Thursday watching a 27-point Falcons run. Sit the Packers this week if you streamed them. Start Atlanta's names if you rostered them. The waiver board has already moved on to Denver and Cleveland and Philadelphia.</p>

      <figure>
        <div class="photo-pair">
          {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
          {_shot("drake-london", "jpg", "Drake London")}
        </div>
        <figcaption>Robinson: 194 and two in a building that was supposed to own the night. London: the 40-yarder that finished it.</figcaption>
      </figure>

      <h2>Sunday at one: nine games, nine names</h2>
      <p><strong>Los Angeles Chargers at Buffalo. Pick: BUF.</strong> Seven of seven. Bender 31-26. Sullivan 31-20. SportsLine 31-21. NFL.com's five editors all found a sentence about fooling themselves twice and then refused to do it a third time. Josh Allen already has nine scores through two weeks and the Chargers have scored 14 a night under a new coordinator, so the mash is loud about Buffalo and I am taking the home side with them. Herbert has been pressured on nearly half his dropbacks. Allen has been an MVP sentence people are already tired of typing. Start Allen and James Cook. Sit the Chargers defense. If you still roster Justin Herbert in a one-quarterback room, you start him because the chair is the chair, and you do it knowing the script is ugly.</p>
      <p><strong>Carolina at Cleveland. Pick: CAR.</strong> Seven of seven. Bender 24-16. Sullivan 24-21. Bryce Young has 361 and four, then 287 and three, and Jalen Coker just played 76 percent of the snaps in a 34-3 win that also gave Darren Waller two scores. Cleveland beat Tampa after a two-hour lightning delay and Deshaun Watson looked like a quarterback who could complete a ball again, which is a real sentence and also a low bar. The mash stayed with Carolina. Start Young if you added him. Start Coker. Stream Carolina's defense, which sits third on the Week 3 DST mash after a night that produced turnovers and a score. Cleveland's defense is a sit unless you enjoy watching a post-Garrett line try to find Young for three hours.</p>
      <p><strong>New York Jets at Detroit. Pick: DET.</strong> Six of six. Bender 33-16. Sullivan 33-21. SportsLine 36-23. Jahmyr Gibbs already has a Thursday chapter from Buffalo and now he gets a home afternoon against a Jets defense that has been stout against lesser backfields. Aaron Glenn comes back to the building he used to coordinate. The mash does not care about the reunion. Start Gibbs and Amon-Ra St. Brown. Sit the Jets defense. Geno Smith is a stream only in the rooms that already lost a quarterback and cannot find Bryce Young on the wire.</p>
      <p><strong>Houston at Indianapolis. Pick: HOU.</strong> Five of six. Bender 26-21. Sullivan took the Colts 26-23. NFL.com's Gennaro Filice called it an elimination game in September and still printed the Texans, because 2.9 percent of 0-3 clubs since 1990 have made a playoff and last year's Texans were one of those five. C.J. Stroud has taken seven sacks. Jonathan Taylor still has to be a one-man army with Daniel Jones working back from an Achilles. I am taking Houston by a field goal and telling every room that drafted Stroud like a ceiling to start him anyway, because a 0-2 road favorite in a desperation building is still a start when the other chair is worse.</p>
      <p><strong>New England at Jacksonville. Pick: JAX.</strong> Three of six, the split on the card. Bender took the Patriots 20-19. Sullivan took the Jaguars. NFL.com took the Jaguars. The market has Jacksonville minus 3. Ties on this board go to the side with more votes, and the votes landed in Florida. Drake Maye has four interceptions through two weeks and still won 20-3 at home because the defense made Pittsburgh look finished. Trevor Lawrence just lost a lead in Denver. Start Maye if you rostered him. Start Lawrence if you rostered him. Stream neither defense unless you already paid for New England last week and want one more night of that 20-3 feeling on the road, which is a hope more than a plan.</p>

      <div class="photo-row">
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("bryce-young", "jpg", "Bryce Young")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("jalen-coker", "jpg", "Jalen Coker")}
      </div>
      <p class="photo-cap">Allen at home. Young on the road after 287 and three. Gibbs after a short week. Coker still first among the names rooms should have already added.</p>

      <p><strong>Kansas City at Miami. Pick: KC.</strong> Seven of seven, the widest number on the one o'clock window, 10 and a half. Bender 27-17. Sullivan 33-16. SportsLine 32-16. Patrick Mahomes threw for 382 and three in overtime last Sunday and Kenneth Walker already has 290 rushing yards, which is a league lead that used to belong to a Seahawks argument and now belongs to a Chiefs feature. Malik Willis has taken nine sacks and the Dolphins have scored 13 in each of two blowouts. Start Mahomes and Walker and Travis Kelce. Stream Kansas City's defense, which sits second on the Week 3 DST mash. Sit Miami unless Achane is the last running back a person has and hoping is the plan.</p>
      <p><strong>Tennessee at the Giants. Pick: NYG.</strong> Five of six. Bender 21-18. Sullivan took the Titans 23-20. NFL.com's Gennaro Filice wrote the moral-victory paragraph about Tennessee hanging with Philadelphia and then printed the Titans, which is the fade the mash did not follow. Jaxson Dart left Monday with a knee. Jameis Winston threw 11 of 27 in Inglewood. Cam Ward has 323 yards and one score through two weeks. I am taking the home side because five cards did, and I am telling Superflex rooms that Winston is a stream only if the rest of the wire is empty. Start the Giants names you already rostered. Sit both defenses unless you streamed New York for the Cam Ward matchup and already spent the FAAB.</p>
      <p><strong>Cincinnati at Pittsburgh. Pick: CIN.</strong> Seven of seven. Bender 24-17. Sullivan 27-20. Joe Burrow found Ja'Marr Chase twice in a 20-6 win in Houston, and Cincinnati's defense has eight sacks and four turnovers through two weeks, which is why the DST mash has them in the top ten even on the road. Aaron Rodgers took four sacks in a 20-3 loss in New England. Start Burrow and Chase. Stream Cincinnati's defense if you need a road name that has already scored. Sit Pittsburgh's skill names only if you enjoy fading a building that still has T.J. Watt, which I do not, so Watt's rooms start him and the rest of the Steelers offense is a matchup.</p>
      <p><strong>Seattle at Washington. Pick: SEA.</strong> Six of six. Bender 24-15. Sullivan 27-17. Jayden Daniels dislocated the left elbow again and Marcus Mariota starts against a defense that has allowed 17 points through two weeks. Drew Lock threw three scores to Jaxon Smith-Njigba in Arizona. Sam Darnold practiced and still looks like next week. Start Smith-Njigba. Start Seattle's defense, which sits first on every Week 3 DST board we mashed. Sit Washington's skill names unless you already paid Keep money for Daniels and are holding the years through the month.</p>

      <figure>
        <div class="photo-pair">
          {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
          {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        </div>
        <figcaption>Mahomes on the road in Miami after 382. Smith-Njigba with Lock again, this time in Landover.</figcaption>
      </figure>

      <h2>Sunday late: Santa Clara, Tampa, Rio, and a dome that just learned how to finish</h2>
      <p><strong>Arizona at San Francisco. Pick: SF.</strong> Six of six. Bender 28-16. Sullivan 33-23. Brock Purdy went 20 of 22 for 287 in a 35-13 win over Miami and Christian McCaffrey became the fourth-fastest player in the Super Bowl era to 100 career touchdowns. The Cardinals managed 151 yards against Seattle. Start Purdy and McCaffrey. Stream San Francisco's defense, which sits fourth on the mash. Sit Arizona unless Trey McBride is the tight end you already paid for, in which case you start him and you live with the building.</p>
      <p><strong>Minnesota at Tampa Bay. Pick: MIN.</strong> Six of six. Bender 21-19. Sullivan 23-21. The Vikings have allowed 12.5 points a night under Brian Flores and Carson Wentz has them 2-0 after Green Bay and a 9-3 rain night in Chicago. Baker Mayfield lost the revenge script at home after a lightning delay. Kyler Murray is expected back from the concussion protocol, which is a sentence that changes the Buccaneers' ceiling and does not change the mash. Start the Minnesota names you rostered. Sit Tampa Bay's defense. Mayfield is a start in the rooms that already used him and a fade in the rooms that can find Young on the wire.</p>
      <p><strong>Baltimore versus Dallas, in Rio. Pick: BAL.</strong> Six of seven. Bender 31-27. Sullivan 31-29 and still took the Cowboys against the number. The market has Baltimore minus 3.5 in a building that is actually a soccer stadium in Brazil, which is a travel sentence both clubs get to share. Derrick Henry already has 212 and four. Dak Prescott just threw four in a 37-20 win. Start Lamar Jackson and Henry and CeeDee Lamb. Sit both defenses. Aubrey still sits first on the Week 3 kicker mash, even in Rio, because the offense around him still moves the ball far enough to kick it.</p>
      <p><strong>Las Vegas at New Orleans. Pick: NO.</strong> Four of five. Bender 26-24. Sullivan 24-20. Tyler Shough beat Baltimore 24-17 with a sneak at 1:28 and Chris Olave had 86 and a score. Kirk Cousins has the Raiders 2-0 without Brock Bowers, and Tre Tucker just caught five for 119 and a score, which is why Tucker sits on the waiver mash. Start Shough in Superflex. Start Olave. Stream New Orleans at home if you need a defense that already took a bite out of Baltimore. Sit Las Vegas unless Jeanty is the back you already paid for.</p>

      <div class="photo-row">
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("lamar-jackson", "png", "Lamar Jackson")}
        {_shot("ceedee-lamb", "png", "CeeDee Lamb")}
        {_shot("joe-burrow", "png", "Joe Burrow")}
      </div>
      <p class="photo-cap">Purdy at home after 20 of 22. Jackson in Rio. Lamb in the same stadium. Burrow on the road in Pittsburgh. The late window is where the card gets wide.</p>

      <h2>Sunday night: the Rams at Denver. Pick: LAR</h2>
      <p>Four of five. Bender took the Broncos 23-21, which is the fade. Sullivan took the Rams 23-20. The market has Los Angeles minus 2.5 on the road after a short week. Matthew Stafford threw for 327 and four on Monday and Davante Adams caught eight for 195, and Puka Nacua is doubtful again with the hip, which is why Adams is still the name and why Terrance Ferguson sits on the waiver mash. Jonah Coleman punched a 3-yard score after J.K. Dobbins left with a hamstring, and Coleman is first on every Week 3 waiver list we mashed, so rooms that need a back already know the bid. Start Stafford and Adams and Kyren Williams. Start Coleman if Dobbins sits. Sit Denver's defense unless you like a night that already has Aaron Donald language attached to it and you enjoy hoping.</p>

      <figure>
        <div class="photo-pair">
          {_shot("matthew-stafford", "png", "Matthew Stafford")}
          {_shot("jonah-coleman", "jpg", "Jonah Coleman")}
        </div>
        <figcaption>Stafford after four scores on Monday, now a road night at altitude. Coleman first on the wire after Dobbins left.</figcaption>
      </figure>

      <h2>Monday: Philadelphia at Chicago. Pick: PHI</h2>
      <p>Six of six. Bender 28-18. Sullivan 26-20. Caleb Williams left a 9-3 rain night with a hamstring and the 59 points from the opener stayed in Charlotte. Tyson Bagent is the name in the concussion protocol conversation, which is a brutal way to host a club that just survived Tennessee on a last-second throw to Darius Cooper. Jalen Hurts and Saquon Barkley are the Monday names. Tank Bigsby ran 13 times for a score when Barkley left with a stinger, and Bigsby sits fourth on the waiver mash, so rooms that already roster the starter still add the cuff. Stream Philadelphia's defense if you like a backup quarterback in the rain building. Sit Chicago's skill names unless D'Andre Swift is the back you already paid for and you are willing to start him behind whoever takes the snaps.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jalen-hurts", "png", "Jalen Hurts")}
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        </div>
        <figcaption>Hurts on the road after a last-second throw in Tennessee. Walker already has 290, and Miami is the next alley.</figcaption>
      </figure>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the published picks in kickoff order if you came here for the list: GB, BUF, CAR, DET, HOU, JAX, KC, NYG, CIN, SEA, SF, MIN, BAL, NO, LAR, PHI. Thursday missed. Sunday and Monday are still live. The mash is a vote, and the vote already spent one night in the wrong building.</p>
      <p>The <a href="waiver.html">Week 3 waiver board</a> opens with Jonah Coleman, then Denzel Boston, Emanuel Wilson, and Tank Bigsby. Bryce Young is the Superflex add if a room still has him sitting there after 648 yards and six scores. Tre Tucker and Darren Waller are the cheap skill names. Spend the leftover FAAB on the names Sunday actually moves.</p>
      <p>The <a href="week3-dst.html">Week 3 DST board</a> leans Seattle, Kansas City, and Carolina. Seattle has allowed 17 points through two weeks and now gets Mariota. Kansas City gets Willis. Carolina already scored on defense in Atlanta. The <a href="week3-kickers.html">kicker board</a> still loves Brandon Aubrey and has learned to say Ka'imi Fairbairn and Jason Myers out loud. The <a href="weekly.html">weekly skill boards</a> rebuilt this morning from FantasyPros ECR dated September 27, plus RotoWire, 4for4, and the rest of the kit.</p>

      <div class="ramif">
        <h3>The sixteen, one more time</h3>
        <ul>
          <li>GB over ATL. Final ATL 35-14. Missed.</li>
          <li>BUF over LAC. Sunday.</li>
          <li>CAR over CLE. Sunday.</li>
          <li>DET over NYJ. Sunday.</li>
          <li>HOU over IND. Sunday.</li>
          <li>JAX over NE. Sunday.</li>
          <li>KC over MIA. Sunday.</li>
          <li>NYG over TEN. Sunday.</li>
          <li>CIN over PIT. Sunday.</li>
          <li>SEA over WAS. Sunday.</li>
          <li>SF over ARI. Sunday.</li>
          <li>MIN over TB. Sunday.</li>
          <li>BAL over DAL. Sunday, in Rio.</li>
          <li>NO over LV. Sunday.</li>
          <li>LAR over DEN. Sunday night.</li>
          <li>PHI over CHI. Monday.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that already has one receipt and fifteen arguments left. Robinson finding the edge in a building that had not lost a home opener since the last time a different commissioner was still new on the job. Penix coming back from the cart language and throwing a five-yard ball to a tight end nobody had written a sentence about since August. Love throwing it 53 times and still leaving 14 on the board. Allen waiting in a new Highmark that already has a 41 next to it. Mahomes packing for Miami with 382 still in his arm. Stafford packing for altitude with four scores still in his Monday. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both, then spend the wire on the names the card actually moves.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card), Tyler Sullivan at CBS Sports (Sep 23), the five-editor NFL.com card (Sep 24), the SportsLine model (10,000 sims), the published FanDuel and DraftKings numbers, a Week 2 winners board, and a short post-Week 2 power card. Thursday final from the published box in Green Bay. Waiver names from Justin Boone, RotoBaller, FantasyPros, and FanDuel Research. Scores from the first two weeks sit on <a href="week2-tape.html">The Second Sunday</a> and <a href="the-recap.html">The Recap</a>.</p>
    </article>
    """
