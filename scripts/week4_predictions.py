"""Week 4 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Twelve games finished inside a score last Sunday, and Thursday still has two clubs who both just won, waiting on a night in Cleveland that has not kicked yet."
DEK = (
    "Steelers at Browns on Prime. The mash has Pittsburgh by four votes to two. "
    "Achane is done. Hall is week to week. Mayfield has a thumb. "
    "Sunday and Monday are still a rumor."
)
PUBLISHED = "2026-10-01T02:30:00Z"
MODIFIED = "2026-10-01T02:30:00Z"
OG_IMAGE = "img/players/josh-allen.png"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week4-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=MODIFIED,
        image=OG_IMAGE,
        brand="Ball Keep",
        section="Week 4",
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
    <a class="opening-teaser recap-teaser" href="week4-matchups.html">
      <img src="{OG_IMAGE}" alt="Josh Allen" width="160" height="160" />
      <div>
        <p class="k">Week 4 · Thursday, Oct 1</p>
        <h2>Steelers at Browns. Thursday is still open.</h2>
        <p>Pittsburgh 2-1. Cleveland 2-1. The mash takes the Steelers. Sunday still has fifteen games left.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 4 · Thursday is still open · Thursday, October 1, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Thursday morning. No Week 4 final yet. The whole slate is still a card.</p>

      <div class="score-row recap-scores">
        <div class="score-card"><p class="when">Thu · Prime</p><p class="result">PIT at CLE</p><p class="meta">Rodgers on a short week · Browns +2.5</p></div>
        <div class="score-card"><p class="when">Sun · CBS</p><p class="result">NE at BUF</p><p class="meta">Allen after five turnovers and a win</p></div>
        <div class="score-card"><p class="when">Sun · NBC</p><p class="result">DET at CAR</p><p class="meta">Gibbs on the road · Young after 18</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">ATL at NO</p><p class="meta">Bijan after 194 · Shough at home</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from the Week 4 card">
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("lamar-jackson", "png", "Lamar Jackson")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
      </div>
      <p class="photo-cap">Allen at home against Maye. Gibbs on Sunday night. Mahomes in Las Vegas. Jackson against Ward. Smith-Njigba after Mariota ended the streak. Robinson on Monday. Purdy at home. Walker already has 360.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet, and a prediction page that also prints the argument starts to feel like a room you can sit in on a Thursday morning while Prime is still nine hours away and two AFC North clubs are both 2-1. Last Sunday put twelve games inside a single score, which is a league record for a Sunday, and it also took De'Von Achane's year, Baker Mayfield's next three weeks, and whatever Breece Hall thought he still had in his thigh. The mash above already voted. Thursday has not written a receipt. What follows is the walk through sixteen games in kickoff order, using the published cards from Bill Bender at Sporting News, Tyler Sullivan at CBS Sports, John Breech at CBS Sports, Cody Williams at FanSided, the SportsLine model, the market, and the tape we just watched, with a side on every game and the winners copied at the bottom of the table for anyone who wants the list without the sentences.</p>

      <h2>Thursday: Pittsburgh at Cleveland. Pick: PIT</h2>
      <p>Four of six. Bender printed 21-16 and still laid the two and a half. Sullivan printed 21-17. Breech took the Browns 19-16 because a 42-year-old quarterback on a short week is a sentence he has been waiting to write, and FanSided went with him. The market has Pittsburgh minus 2.5 in a building that has beaten the Steelers in four straight home meetings, which is a habit the mash decided was not enough. Aaron Rodgers threw three scores on Sunday and then had to pack for Cleveland on three days of rest. Deshaun Watson has completed 68 percent and won the last two, and Mason Graham already has four sacks, and none of that moved four cards off the road favorite. I am taking Pittsburgh with the mash because a short week still has T.J. Watt on it, and I am telling every room that streamed Cleveland last week against Carolina that Thursday night is a coin they already spent.</p>
      <p>Fantasy rooms already know the ugly version of this game. Start Watt if you rostered him. Stream Pittsburgh's defense, which sits fourth on the Week 4 DST mash and gets a Watson who has been sacked in every game. Stream Cleveland only if you enjoy a 38-and-a-half total and you already paid the FAAB. Boswell sits inside the top twelve on the kicker mash. Sit the Browns skill names unless Denzel Boston is the receiver you added last week and you are willing to start him on a Thursday that the published cards do not love.</p>

      <figure>
        <div class="photo-pair">
          {_shot("josh-allen", "png", "Josh Allen")}
          {_shot("lamar-jackson", "png", "Lamar Jackson")}
        </div>
        <figcaption>Allen still has a Sunday at home. Jackson gets Cam Ward and a number that is already 11.5.</figcaption>
      </figure>

      <h2>Sunday morning in London: Indianapolis at Washington. Pick: IND</h2>
      <p>Six of six. Bender 23-21. Sullivan 30-24. Every card we mashed found Daniel Jones and Jonathan Taylor in a soccer stadium and decided that was enough. Marcus Mariota just hung 33 on the Super Bowl champions and the Commanders have allowed 55 rushing yards a night the last two weeks, which is the sentence that made London a Colts game even after Jayden Daniels left the month with the same left elbow. Start Taylor. Start Tyler Warren if you rostered him. Stream neither defense unless you already paid for Indianapolis and you like a morning kick. Sit Washington's skill names unless you paid Keep money for Daniels and you are holding the years through October.</p>

      <h2>Sunday at one: eight games, eight names</h2>
      <p><strong>Tennessee at Baltimore. Pick: BAL.</strong> Eight of eight, the widest number on the early window besides Buffalo and Minnesota. Bender 30-17. Sullivan 33-16. The market is 11.5. Derrick Henry already has 301 and six. Cam Ward has 12.3 points a night as a club. Start Lamar Jackson and Henry. Stream Baltimore's defense, which sits third on the Week 4 DST mash after a month that allowed 31 a night against real offenses and now gets a Titans line that ranks 27th in pass-block win rate. Sit Tennessee unless you enjoy a double-digit number and a hope.</p>
      <p><strong>New England at Buffalo. Pick: BUF.</strong> Eight of eight. Bender 27-21 and still wrote the last-six-meetings paragraph about one-score games. Sullivan 30-20. Drake Maye has six interceptions and one passing score, and the Bills had five turnovers on Sunday and still beat the Chargers by eight, which is a sentence that should scare a room and somehow made every card louder about Josh Allen at home. Start Allen and James Cook. Stream Buffalo's defense, which sits fifth on the mash. Sit Maye unless Superflex already lost a chair and the wire is empty. The waiver board has Mack Hollins if a person still wants a Patriot.</p>
      <p><strong>New York Jets at Chicago. Pick: CHI.</strong> Six of seven. Bender 21-17. Sullivan 27-24 and still took the Jets against the number. Breech was the fade, 23-16 New York. Case Keenum just hung 27-7 on Philadelphia with two throwing scores and one with his legs, and Breece Hall left Detroit with a thigh, which is why Braelon Allen sits first on every Week 4 waiver list we mashed. Start Keenum in Superflex if you added him. Start the Bears defense, which sits inside the top ten after a Monday that looked like a clamp. Start Allen if the claim cleared. Sit the Jets defense. Geno Smith is a stream only in the rooms that already lost a quarterback and cannot find Shough or Young on the wire.</p>
      <p><strong>Jacksonville at Cincinnati. Pick: CIN.</strong> Five of eight, the split on the card. Bender 31-26. Sullivan 24-21. FanSided took the Jaguars. SportsLine printed Bengals 31, Jaguars 28 and called the over the play. Trevor Lawrence just knelt at the one in a 35-6 win that still looks like a clip people will send around in May, and Joe Burrow fumbled late in Pittsburgh and still has Ja'Marr Chase and Tee Higgins at home. I am taking Cincinnati because five cards did, and I am telling every room that drafted Chase like a ceiling to start him in a building that has averaged 55.5 combined in Burrow's last twelve home starts. Start Burrow and Chase. Sit both defenses. Evan McPherson sits second on the kicker mash and first on a couple of the weekly boards, which is a real sentence after eight makes.</p>
      <p><strong>Dallas at Houston. Pick: DAL.</strong> Four of six, against the number. Bender 28-26. Sullivan 27-23. Breech took the Texans 23-20 because 0-3 last year still made a playoff and he wanted the sequel. The market has Houston minus 2.5 after a 19-17 loss that dumped the preseason Super Bowl sentence to 0-3 again. C.J. Stroud has taken ten sacks. Dak Prescott just lost in Rio on a 56-yarder at the horn. I am taking Dallas with the mash and telling every room that drafted Stroud like a ceiling that three weeks have been a floor. Start Lamb and Aubrey, who still sits first on every kicker board we mashed. Sit Houston unless you enjoy an offensive line that ranks near the bottom in pressures allowed and you already paid Superflex money.</p>
      <p><strong>Arizona at the Giants. Pick: ARI.</strong> Five of eight. Bender 21-19. Sullivan 27-23. SportsLine liked the Giants to cover. Jameis Winston has been the starter since Jaxson Dart's knee ended the year in Week 2, and the Giants traded for J.J. McCarthy, which is a sentence that changes the next month and does not change Sunday if Winston still takes the first snap. Trey McBride has 26 catches on 33 targets. Cam Skattebo just ran it 20 times in a 12-7 win. Start McBride. Sit both defenses unless you streamed Arizona for the Winston matchup and already spent the FAAB. Kenyon Sadiq is a Jets name, not a Giants name, and he sits third on the waiver mash after 7, 105, and a score.</p>
      <p><strong>Los Angeles Rams at Philadelphia. Pick: LAR.</strong> Seven of seven. Bender 28-24. Sullivan 24-20. The Eagles have not scored in a first quarter all year, they just lost 27-7 at home to Keenum, and they are 0-5 straight up as a home underdog since Nick Sirianni took the job. Matthew Stafford threw for 390 in Denver and still lost. Puka Nacua might dress. Davante Adams is still the name if he does not. Start Stafford and Kyren Williams. Sit Philadelphia's defense, which has three sacks and zero takeaways. Tank Bigsby is a cuff a lot of rooms already added. Jalen Hurts is a start because the chair is the chair, and you do it knowing Monday already used the pretty script.</p>
      <p><strong>Green Bay at Tampa Bay. Pick: GB.</strong> Seven of seven. Bender 26-20. Sullivan 27-20. Baker Mayfield dislocated a thumb and Jalon Daniels, an undrafted rookie out of Kansas, is the name under center, which is why Green Bay's defense sits inside the top ten on the Week 4 DST mash after a Thursday that produced minus-2 fantasy points against Bijan. Jordan Love has completed 52 percent and still gets a club that has not covered in twelve straight. Start Love if you rostered him, because the other chair is a first start. Stream the Packers defense. Sit Tampa Bay's skill names unless Bucky Irving is already in the lineup and you have no other back.</p>

      <div class="photo-row">
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
      </div>
      <p class="photo-cap">Gibbs on Sunday night. Smith-Njigba at home after the streak ended. Robinson on Monday after 194. Mahomes in a building that just beat him last year without him.</p>

      <h2>Sunday late: Minneapolis, Las Vegas, Seattle, and Santa Clara</h2>
      <p><strong>Miami at Minnesota. Pick: MIN.</strong> Eight of eight, 10.5 on the number, the other blowout on the card. Bender 26-14. Sullivan 27-10. Brian Flores blitzes on 71 percent of snaps and the Dolphins just lost Achane to an ACL and have scored 12 a night, which is why Minnesota's defense sits first on every Week 4 DST board we mashed. Malik Willis is the quarterback. Ollie Gordon took 17 carries after Achane left and sits second on the waiver mash. Start the Minnesota names you rostered. Stream the Vikings defense even if you already paid for them in August. Sit Miami unless Gordon is the last running back a person has and hoping is the plan. Will Reichard sits inside the top eight on the kicker mash.</p>
      <p><strong>Kansas City at Las Vegas. Pick: KC.</strong> Seven of seven. Bender 24-23 and called it the game of the week. Sullivan 30-24. Kenneth Walker already has 360 rushing yards, which is a league lead that used to belong to a Seahawks argument and now belongs to a Chiefs feature. Kirk Cousins has the Raiders 3-0 with a 107 passer rating and Brock Bowers just caught 10 for 116 in his first game back, and none of that moved a card off Mahomes. Start Mahomes and Walker and Travis Kelce. Start Bowers, who sits first on the weekly tight end mash after one night. Stream Kansas City's defense, which sits sixth. Sit Las Vegas unless you already paid Keep money for Bowers and you start the years.</p>
      <p><strong>Los Angeles Chargers at Seattle. Pick: SEA.</strong> Seven of seven. Bender 24-20. Sullivan 33-20. SportsLine covered Seattle in 60 percent of the sims. Justin Herbert has 14.7 points a night as a club and four interceptions, and Sam Darnold came back and threw for 379 and four and still lost 33-31 to Mariota, which is why a lot of rooms will fade Seattle for one more week and why the mash did not. Start Jaxon Smith-Njigba, who sits first on the weekly receiver mash. Start Seattle's defense, which sits second after a night that was more mistakes than a bad outing. Sit the Chargers. Jason Myers is still a start on the kicker mash.</p>
      <p><strong>Denver at San Francisco. Pick: SF.</strong> Five of six. Bender 27-24. Sullivan took the Broncos 23-21, which is the fade. Brock Purdy is the name NFL.com just put first among quarterbacks, and Christian McCaffrey is still the back, and Bo Nix threw two scores in a 30-26 win that needed a late flag. Start Purdy and McCaffrey. Stream San Francisco at home if you need a defense that already has a top-ten pass rush without Nick Bosa. Sit Denver's defense on the road. Jonah Coleman is a name rooms already spent FAAB on last week, and he is a start if Dobbins is still in the hamstring sentence.</p>

      <figure>
        <div class="photo-pair">
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
          {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        </div>
        <figcaption>Walker already has 360 and now he gets a Raiders front that just forced nine turnovers. Smith-Njigba at home after Mariota ended the streak.</figcaption>
      </figure>

      <h2>Sunday night: Detroit at Carolina. Pick: DET</h2>
      <p>Seven of seven. Bender 34-28. Sullivan 30-27 and still took the Panthers against the number. Jahmyr Gibbs already has the league lead in carries of ten yards or more, and Bryce Young leads the league in passing yards per game and still lost 21-18 in Cleveland after a cleat to the leg. Start Gibbs and Amon-Ra St. Brown. Start Young if you added him two weeks ago, because 313 a night is still a Superflex chair even after 18 points. Sit Carolina's defense. Detroit is a start on offense and a sit on defense unless you like a building that just allowed 24 to Geno Smith.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
          {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        </div>
        <figcaption>Gibbs on the road after 31 at home. Robinson on Monday after 194 in a building that was supposed to own Thursday.</figcaption>
      </figure>

      <h2>Monday: Atlanta at New Orleans. Pick: ATL</h2>
      <p>Four of seven, against the number. Bender took the Saints 29-22. FanSided took the Saints. Sullivan printed Falcons 26-24 and Breech went with him, and the mash landed in Atlanta because a 194-yard Thursday still counts on a short week. Tyler Shough ranks second in passing yards and the dome will be loud on the twentieth anniversary of the first home game after the storm, which is a real sentence and also not a tackle. Bijan Robinson already has 349. Michael Penix Jr. just hung 35 in Lambeau. Start Robinson. Start Shough in Superflex. Start Olave. Sit both defenses. The number is New Orleans minus 2.5 and the votes did not care.</p>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the published picks in kickoff order if you came here for the list: PIT, IND, BAL, BUF, CHI, CIN, DAL, ARI, LAR, GB, MIN, KC, SEA, SF, DET, ATL. Thursday is still live. Sunday and Monday are still live. The mash is a vote, and the vote has not spent a night yet.</p>
      <p>The <a href="waiver.html">Week 4 waiver board</a> opens with Braelon Allen, then Ollie Gordon, Kenyon Sadiq, and Keenan Allen. Achane is done for the year and Hall is week to week, so the first two backs on the wire are the first two backs on the wire. Sadiq just went 7 for 105 and a score. Spend the leftover FAAB on the names Thursday actually moves.</p>
      <p>The <a href="week4-dst.html">Week 4 DST board</a> leans Minnesota, Seattle, and Baltimore. Minnesota gets Willis without Achane. Seattle gets Herbert at home. Baltimore gets Ward. The <a href="week4-kickers.html">kicker board</a> still loves Brandon Aubrey and has learned to say Ka'imi Fairbairn and Tyler Loop out loud. The <a href="weekly.html">weekly skill boards</a> rebuilt this morning from FantasyPros ECR dated October 1, plus RotoWire, 4for4, and the rest of the kit. Gibbs opens the flex. Smith-Njigba opens the receivers. Bowers sits first among the tight ends after one night back.</p>

      <div class="ramif">
        <h3>The sixteen, one more time</h3>
        <ul>
          <li>PIT over CLE. Thursday.</li>
          <li>IND over WAS. Sunday morning, in London.</li>
          <li>BAL over TEN. Sunday.</li>
          <li>BUF over NE. Sunday.</li>
          <li>CHI over NYJ. Sunday.</li>
          <li>CIN over JAX. Sunday.</li>
          <li>DAL over HOU. Sunday.</li>
          <li>ARI over NYG. Sunday.</li>
          <li>LAR over PHI. Sunday.</li>
          <li>GB over TB. Sunday.</li>
          <li>MIN over MIA. Sunday.</li>
          <li>KC over LV. Sunday.</li>
          <li>SEA over LAC. Sunday.</li>
          <li>SF over DEN. Sunday.</li>
          <li>DET over CAR. Sunday night.</li>
          <li>ATL over NO. Monday.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that still has sixteen arguments and zero receipts. Rodgers packing for Cleveland on a short week after three scores. Watson walking into a building that has owned this meeting. Allen waiting in a Highmark that already has a 24 next to a Chargers night that should have been a loss. Mahomes packing for Las Vegas with Walker already at 360. Darnold walking back into Seattle after Mariota ended the streak. Robinson packing for the dome after 194 in a building that was supposed to own Thursday. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both, then spend the wire on Allen and Gordon and Sadiq before the room remembers the names.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card), Tyler Sullivan at CBS Sports (Sep 30), John Breech at CBS Sports (Sep 29), Cody Williams at FanSided (Sep 29), the SportsLine model (10,000 sims), the published FanDuel and DraftKings numbers, a Week 3 winners board, and a short post-Week 3 power card. Waiver names from Justin Boone, RotoBaller, NFL.com, and FanDuel Research. Week 3 scores sit on <a href="week3-matchups.html">Week 3 Predictions</a> and <a href="week2-tape.html">The Second Sunday</a>.</p>
    </article>
    """
