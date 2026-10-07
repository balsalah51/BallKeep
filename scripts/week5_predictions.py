"""Week 5 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Dallas is laying nine and a half on a Thursday against a second-start rookie, and the rest of the card still has two 4-0 clubs and a Monday that wants to be a Super Bowl preview."
DEK = (
    "Buccaneers at Cowboys opens Prime. London has the Eagles at the Jaguars. "
    "San Francisco and Minnesota are still unbeaten. Kansas City and Carolina sit. "
    "Thursday has not kicked."
)
PUBLISHED = "2026-10-07T02:30:00Z"
MODIFIED = "2026-10-07T02:30:00Z"
OG_IMAGE = "img/players/dak-prescott.png"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week5-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=MODIFIED,
        image=OG_IMAGE,
        brand="Ball Keep",
        section="Week 5",
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
    <a class="opening-teaser recap-teaser" href="week5-matchups.html">
      <img src="{OG_IMAGE}" alt="Dak Prescott" width="160" height="160" />
      <div>
        <p class="k">Week 5 · Wednesday, Oct 7</p>
        <h2>Cowboys on Thursday. Two 4-0 clubs still live.</h2>
        <p>Dallas lays 9.5 against Daniels. San Francisco visits Seattle. Bills at Rams on Monday. Kansas City and Carolina sit.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 5 · Thursday still open · Wednesday, October 7, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Wednesday morning. Thursday card still live. Sunday and Monday still live.</p>

      <div class="score-row recap-scores">
        <div class="score-card"><p class="when">Thu · Prime</p><p class="result">TB at DAL</p><p class="meta">Daniels, second start · Dallas 9.5</p></div>
        <div class="score-card"><p class="when">Sun · FOX</p><p class="result">SF at SEA</p><p class="meta">Purdy 4-0 · Macdonald at home</p></div>
        <div class="score-card"><p class="when">Sun · NBC</p><p class="result">BAL at ATL</p><p class="meta">Jackson ankle · Penix at home</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">BUF at LAR</p><p class="meta">Allen after 29-26 · Stafford at home</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from the Week 5 card">
        {_shot("dak-prescott", "png", "Dak Prescott")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("lamar-jackson", "png", "Lamar Jackson")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
      </div>
      <p class="photo-cap">Prescott on Thursday. Purdy on the road in Seattle. Allen on Monday. Gibbs in Arizona. Smith-Njigba at home. Robinson after 145. Jackson on an ankle. Walker already has 537 and a bye.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet, and a prediction page that also prints the argument starts to feel like a room you can sit in on a Wednesday while Thursday is still a rumor and two clubs are already packing for a bye. The mash above already voted. Week 4 already wrote sixteen receipts, including a Thursday the mash missed in Cleveland and a Monday that hung 45 in the dome. What follows is the walk through fifteen games in kickoff order, using the published cards from Bill Bender at Sporting News, John Breech at CBS Sports, Vinnie Iyer at Sporting News, the SportsLine model, the market, and the tape we just watched, with a side on every game and the winners copied at the bottom of the table for anyone who wants the list without the sentences.</p>

      <h2>Thursday: Tampa Bay at Dallas. Pick: DAL</h2>
      <p>Five of five among the boards that printed a side. Bender 31-19. Breech 27-17. Iyer 34-17 and still laid the nine and a half. The market is Dallas minus 9.5 in a building that just hung 34 in Houston, and Jalon Daniels is making a second start after 148 yards, one score, and two picks in a 17-14 loss that needed a 58-yarder from Trey Smack to end. I am taking Dallas with them on Wednesday morning because a short week still has CeeDee Lamb on it after 17 catches and 189 yards, and a rookie who just saw Green Bay does not get a softer Thursday for the second one.</p>
      <p>Fantasy rooms already know what to do with a night like that. Start Lamb. Start Aubrey, who still sits first on every kicker board we mashed. Stream Dallas's defense if you still have a hole and you already spent the week watching Daniels throw it to the other color. Sit Tampa Bay unless Bucky Irving is already in the lineup and you have no other back. The waiver board has already moved on to Wilson and Shipley, and Sunday still has fourteen games left to move it again.</p>

      <figure>
        <div class="photo-pair">
          {_shot("dak-prescott", "png", "Dak Prescott")}
          {_shot("brock-purdy", "jpg", "Brock Purdy")}
        </div>
        <figcaption>Prescott after 335 in Houston. Purdy still has not taken a sack and now he packs for Seattle.</figcaption>
      </figure>

      <h2>Sunday morning in London: Philadelphia at Jacksonville. Pick: JAX</h2>
      <p>Five of five. Bender 24-21. Breech 30-20. Iyer 27-20. Every card we mashed found Trevor Lawrence in a soccer stadium and decided that was enough. Saquon Barkley left Week 4 with a hamstring. Tank Bigsby is headed to IR. DeVonta Smith already sat. Jalen Hurts has 123 passing yards a night the last two weeks and a 52.8 percent completion number that looks like a club searching for a first read. Jacksonville has a plus-six turnover ratio and has not allowed more than 20 points. Start Lawrence if Superflex still has a hole. Stream Jacksonville's defense, which sits inside the top five after a month that held New England to six and Cincinnati to 17. Sit Philadelphia's defense. Will Shipley sits second on the waiver mash because the Eagles just ran out of healthy backs, and London is a brutal first week as the feature.</p>

      <h2>Sunday at one: seven games, seven names</h2>
      <p><strong>Cincinnati at Miami. Pick: CIN.</strong> Five of five, 7.5 on the number, the blowout on the early window. Bender 23-13. Breech 24-16. SportsLine covered Cincinnati in more than half the sims. The Dolphins have not scored more than 13 points in a game and just set season lows in yards and first downs without Achane. Ja'Marr Chase is in concussion protocol. Tee Higgins is doubtful with an adductor. Joe Burrow still has a 132.8 career rating against Miami, which is a sentence rooms will repeat even if both wideouts sit. Start Burrow. Start Chase if he clears. Start Gesicki and Dohnte Meyers if they do not. Stream Cincinnati's defense, which sits second on the Week 5 DST mash. Sit Miami unless Ollie Gordon is the last running back a person has and hoping is the plan. Evan McPherson sits second on the kicker mash.</p>
      <p><strong>Las Vegas at New England. Pick: NE.</strong> Five of six. Bender 23-20. Breech 27-24. Iyer 27-20 and still laid the three and a half. The market is New England minus 3.5 after Drake Maye hung 269 and three on Buffalo, and Kirk Cousins just threw 365 in a 30-27 loss that needed Kenneth Walker to find 177. The Raiders are 3-1 and 2-0 on the road. The mash still took Maye at home because a three-score night in Orchard Park is a real sentence after six interceptions to start the year. Start Maye. Start Romeo Doubs if you added him. Sit Las Vegas unless Bowers is already in the lineup, because 6 for 86 and a score still counts even after a loss. Matt Gay is a stream on the kicker mash after four makes in that same building.</p>
      <p><strong>Minnesota at New Orleans. Pick: MIN.</strong> Five of six, the split on the card. Bender took the Saints 23-19 because a 4-0 club on the road still has to settle for field goals. Breech took Minnesota 19-16. SportsLine covered the Vikings in 60 percent of the sims. Flores still blitzes like a man who has not found a reason to stop, and Tyler Shough has been sacked multiple times in every start. Justin Jefferson is a St. Rose native with an ankle that still has no stamp. T.J. Hockenson just caught 13 for 119 with Jefferson out. Start Hockenson. Stream Minnesota's defense, which sits inside the top four after a 15-10 that looked like a clamp. Sit New Orleans unless Olave is already in the lineup and you have no other receiver. Will Reichard sits inside the top five on the kicker mash.</p>
      <p><strong>Cleveland at the Jets. Pick: CLE.</strong> Four of six. Bender 21-19. Breech 20-17. Iyer and the market took New York minus 1.5, which is only the second time the Jets have been favored under Aaron Glenn. The Browns have 11 sacks and four interceptions over the last three games and just hung 27-24 on a Thursday the mash missed. Deshaun Watson found Denzel Boston for 60 on the first scoring drive of that night, and Quinshon Judkins already has a Thursday chapter. Start Judkins. Stream Cleveland's defense, which sits inside the top ten. Sit the Jets unless Braelon Allen is already in the lineup after Hall's thigh, because 14 for 59 against Chicago is a role and not a ceiling.</p>
      <p><strong>Indianapolis at Pittsburgh. Pick: PIT.</strong> Four of six. Bender 27-24. Breech took the Colts 22-19. The market is Pittsburgh minus 1.5 in a building where Rodgers has a 91.8 rating and the Steelers are 2-0 at home. Daniel Jones has thrown an interception in all four games. Jonathan Taylor just ran it 20 times for 95 and two in London. Start Taylor. Start Shrader, who is 11 for 11 and still available in half the rooms. Sit both defenses unless you already paid for Pittsburgh and you like a home favorite that just lost 27-24 on a short week.</p>
      <p><strong>Houston at Tennessee. Pick: HOU.</strong> Four of four among the boards that printed a side. Bender 26-14. Breech 20-13. Two 0-4 clubs in a building where Houston has won five straight, and Cam Ward has an interception in back-to-back games. C.J. Stroud took ten sacks through three weeks and then threw for 347 in a 34-30 loss that still dumped them to 0-4. Nico Collins went 7 for 118 and two. Start Collins. Stream Houston's defense, which sits first on every Week 5 DST board we mashed because 16.25 implied points is the softest number on the card. Sit Tennessee. Ka'imi Fairbairn sits inside the top five on the kicker mash.</p>
      <p><strong>New York Giants at Washington. Pick: NYG.</strong> Four of five. Bender 20-17. Breech 23-16. The market is Washington minus 3.5 because a home favorite still looks like a favorite until you write the quarterback sentence. Jayden Daniels has an elbow. Marcus Mariota has a knee. Athan Kaliakmanis started in London and the Commanders lost 30-13. Jameis Winston just hung 250 and three in a 36-24 win that also had Malik Nabers for 112. Start Nabers. Start Winston in Superflex if you added him. Sit Washington unless Terry McLaurin is upgraded and you already spent the chair.</p>

      <div class="photo-row">
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("josh-allen", "png", "Josh Allen")}
      </div>
      <p class="photo-cap">Gibbs in Arizona. Smith-Njigba at home against Purdy. Robinson after 145 and two. Allen packing for Los Angeles after 29-26 in Orchard Park.</p>

      <h2>Sunday late: Inglewood, Arizona, Lambeau, and Seattle</h2>
      <p><strong>Denver at the Chargers. Pick: DEN.</strong> Five of five. Bender 23-20. Breech 27-20. The Chargers are 0-4 and 0-4 against the number, Justin Herbert has an interception in every game, and the offensive line has 20 penalties. Patrick Surtain and Riley Moss both left San Francisco, and the mash still took Denver because a 0-4 home underdog with Mike McDaniel calling plays is a sentence rooms want to believe and the cards did not. Start Bo Nix if Superflex still has a hole. Stream Denver's defense, which sits inside the top five. Sit the Chargers. Keaton Mitchell sits on the waiver mash after 15 touches next to Hampton and Vidal, and that is a committee sentence, not a feature.</p>
      <p><strong>Detroit at Arizona. Pick: DET.</strong> Five of five. Bender 31-24. Breech 30-23. The Lions just lost 32-26 in Carolina after 412 from Goff, and the Cardinals have allowed 30 or more in three of four. Jacoby Brissett has three interceptions and a Lions secondary that has allowed 20 fantasy points to every quarterback it has faced. Start Gibbs. Start Amon-Ra St. Brown. Start Bates, who sits inside the top eight on the kicker mash. Sit Arizona unless McBride is already in the lineup, because 26 catches on 33 targets through three weeks still counts even after 1-3.</p>
      <p><strong>Chicago at Green Bay. Pick: CHI.</strong> Five of five, the loudest rivalry sentence on the card. Bender 24-19. Breech 30-23. The Bears are favored at Lambeau after 196 rushing yards a night and a 23-12 that looked like a clamp, and Tyson Bagent just threw for 268 after Case Keenum hung 27-7 on Philadelphia. Green Bay ranks 32nd in rushing yards, yards per carry, rushing first downs, and yards after contact. Jordan Love has completed 52 percent and still gets a club that just ran it 30 times for 146. Start the Bears skill names you already rostered. Stream Chicago's defense, which sits inside the top ten. Sit Green Bay unless Love is the last Superflex chair a person has. Trey Smack is a stream after the 58-yarder that beat Tampa Bay.</p>
      <p><strong>San Francisco at Seattle. Pick: SF.</strong> Five of six, against the number. Bender 28-23. Breech 27-24. Iyer 24-20. The market is Seattle minus 3 because Lumen is loud and Mike Macdonald has held Shanahan under 20 in four of the last five meetings. Brock Purdy has not been sacked. The 49ers average 30.5. Christian McCaffrey is still the back. Emanuel Wilson just took 21 carries, 81 yards, a rushing score, and a receiving score after Jadarian Price went on IR, and he sits first on every Week 5 waiver list we mashed. Start Purdy and McCaffrey. Start Smith-Njigba. Start Wilson if the claim cleared. Sit Seattle's defense unless you already paid for them in August and you like a building that just allowed 23 to Herbert. Jason Myers is still a start on the kicker mash.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        </div>
        <figcaption>Smith-Njigba at home after 76 and a 30-23. Walker already has 537 and now he sits with the rest of Kansas City.</figcaption>
      </figure>

      <h2>Sunday night: Baltimore at Atlanta. Pick: BAL</h2>
      <p>Three of four. Bender 24-17. Breech took the Falcons 30-27 because five NBC games have gone to the home team and Lamar Jackson has an ankle. The market is Baltimore minus 3.5. Michael Penix just hung 45 in the dome after 194 from Bijan on a Thursday that already feels like last month. Derrick Henry has 301 and six through three, then 73 and a score against Tennessee. I am taking Baltimore with the mash and telling every room that drafted Jackson like a ceiling to start him if he practices, and to start Huntley if he does not, because a Sunday night in Atlanta is still a Superflex chair. Start Robinson. Start Henry. Sit both defenses unless you already paid for Baltimore and you like a road favorite on an ankle.</p>

      <h2>Monday: Buffalo at the Rams. Pick: LAR</h2>
      <p>Four of six. Bender 33-26. Breech 34-31. Iyer took the Bills 34-31 because Allen's legs still decide Mondays. The market is Los Angeles minus 2.5 after Stafford threw for 317 in a 24-20 that saved a season in Philadelphia, and the Bills just allowed 29 to a Patriots club that had scored 29 through three weeks. Puka Nacua went 9 for 125. Josh Allen threw an interception that iced New England. Start Stafford, Nacua, and Kyren Williams. Start Allen and James Cook because the chair is the chair. Sit Buffalo's defense. Harrison Mevis sits inside the top fifteen on the kicker mash and first among the streamers who still have a name on the wire.</p>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the published picks in kickoff order if you came here for the list: DAL, JAX, CIN, NE, MIN, CLE, PIT, HOU, NYG, DEN, DET, CHI, SF, BAL, LAR. Thursday has not kicked. Sunday and Monday are still live. Kansas City and Carolina sit. The mash is a vote, and the vote is 0-0 on the night.</p>
      <p>The <a href="waiver.html">Week 5 waiver board</a> opens with Emanuel Wilson, then Will Shipley, Keon Coleman, and Keaton Mitchell. Price is on IR and Barkley left with a hamstring, so the first two backs on the wire are the first two backs on the wire. Gesicki and Dohnte Meyers are the Cincinnati names if Chase and Higgins sit. Spend the leftover FAAB on the names Thursday actually moves.</p>
      <p>The <a href="week5-dst.html">Week 5 DST board</a> leans Houston, Cincinnati, and Denver. Houston gets Ward at 0-4. Cincinnati gets Willis without Achane. Denver gets Herbert at 0-4. The <a href="week5-kickers.html">kicker board</a> still loves Brandon Aubrey and has learned to say Spencer Shrader and Will Reichard out loud. The <a href="weekly.html">weekly skill boards</a> rebuilt this morning from FantasyPros ECR dated October 7, plus RotoWire, 4for4, and the rest of the kit. Gibbs opens the flex. Smith-Njigba opens the receivers. McBride sits first among the tight ends.</p>

      <div class="ramif">
        <h3>The fifteen, one more time</h3>
        <ul>
          <li>DAL over TB. Thursday.</li>
          <li>JAX over PHI. Sunday morning, in London.</li>
          <li>CIN over MIA. Sunday.</li>
          <li>NE over LV. Sunday.</li>
          <li>MIN over NO. Sunday.</li>
          <li>CLE over NYJ. Sunday.</li>
          <li>PIT over IND. Sunday.</li>
          <li>HOU over TEN. Sunday.</li>
          <li>NYG over WAS. Sunday.</li>
          <li>DEN over LAC. Sunday.</li>
          <li>DET over ARI. Sunday.</li>
          <li>CHI over GB. Sunday.</li>
          <li>SF over SEA. Sunday.</li>
          <li>BAL over ATL. Sunday night.</li>
          <li>LAR over BUF. Monday.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that still has no receipt and fifteen arguments. Lamb after 189 in Houston. Daniels taking a second snap on a Thursday that already has a 9.5 next to it. Purdy packing for a building that has held Shanahan under 20. Wilson after 21 carries and two scores, waiting on a claim. Allen walking out of Highmark after 29-26 with a Monday still on the calendar. Robinson after 145 in a dome that just hung 45. Walker already at 537 and sitting with the rest of Kansas City. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both, then spend the wire on Wilson and Shipley before the room remembers the names.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card), John Breech at CBS Sports (Oct 6), Vinnie Iyer at Sporting News (ATS card with SU winners), the SportsLine model (10,000 sims), the published FanDuel and DraftKings numbers, a Week 4 winners board, and a short post-Week 4 power card. Thursday has not kicked. Waiver names from Justin Boone, FantasyPros, NFL.com, and FanDuel Research. Week 4 scores sit on <a href="week4-matchups.html">Week 4 Predictions</a>.</p>
    </article>
    """
