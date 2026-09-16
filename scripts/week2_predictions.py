"""Week 2 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Sixteen games, a new Highmark, and a card that already has a memory."
DEK = (
    "Thursday in Buffalo opens the week. The mash likes the Bills. Sunday asks "
    "the rest of the league to prove the opener meant something. This is the "
    "full Week 2 card, written Wednesday, with a published pick on every line."
)
PUBLISHED = "2026-09-16T14:00:00Z"
OG_IMAGE = "img/players/josh-allen.png"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week2-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=PUBLISHED,
        image=OG_IMAGE,
        brand="Ball Keep",
        section="Week 2",
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


def predictions_teaser():
    return f"""
    <a class="opening-teaser recap-teaser" href="week2-matchups.html">
      <img src="{OG_IMAGE}" alt="Josh Allen" width="160" height="160" />
      <div>
        <p class="k">Week 2 Predictions · Wednesday, Sep 16</p>
        <h2>Bills over Lions. A pick on every line.</h2>
        <p>The mash likes Buffalo on Thursday, San Francisco in a landslide, and Kansas City under the lights. Read the card, then copy the winners in kickoff order.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 2 · Predictions · Wednesday, September 16, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Wednesday before Detroit flies to Buffalo</p>

      <div class="score-row recap-scores">
        <div class="score-card"><p class="when">Thu · Prime</p><p class="result">Pick: BUF</p><p class="meta">DET at BUF · BUF -4.5</p></div>
        <div class="score-card"><p class="when">Sun · FOX</p><p class="result">Pick: SF</p><p class="meta">MIA at SF · SF -12.5</p></div>
        <div class="score-card"><p class="when">Sun · NBC</p><p class="result">Pick: KC</p><p class="meta">IND at KC · KC -5.5</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">Pick: LAR</p><p class="meta">NYG at LAR · LAR -9.5</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from the Week 2 card">
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("jalen-hurts", "png", "Jalen Hurts")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
      </div>
      <p class="photo-cap">Allen, Gibbs, Purdy, Hurts, Mahomes, Williams, Maye, McCaffrey. Week 2 already has a cast, and every name on this row has a Sunday or a Thursday attached to it.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet. A prediction page that also prints the argument starts to feel like a room you can sit in on a Wednesday. The mash above already voted. What follows is the walk: sixteen games, kickoff order, published cards from Sporting News, CBS Sports, Sports Brackets, Sportsnaut, the market, and the tape we just watched. Every game has a side. Copy the winners at the bottom of the table if you want the list without the sentences.</p>

      {_film("2kwY6ve5E88", "Josh Allen tape. Four scores in the opener, and Thursday night in the new Highmark asks for another chapter.")}

      <h2>Thursday: Detroit at Buffalo. Pick: BUF</h2>
      <p>The new Highmark Stadium gets its first regular-season night, and the league handed it the two clubs that just scored 67 points between them. Buffalo beat Houston 36-31. Detroit survived New Orleans 31-30 in overtime. Bill Bender at Sporting News has the Bills 28-26. John Breech at CBS Sports has them 38-31. NFL Spin Zone printed 31-23. Sportsnaut printed 35-31. The Game Haus leaned Detroit against the number and still left the favorite on the moneyline. The mash is loud about Buffalo. Seven of the eight boards that bothered to pick this game took the home side. I am taking the home side with them.</p>
      <p>Jahmyr Gibbs already has his first chapter, 156 yards of it, and now he has to spend it on a short week after an overtime. That is a brutal way to open Thursday Night Football. Josh Allen accounted for four scores against a Texans defense that was supposed to be the grown-up in the room. Tyler Shough threw for 410 on that same Detroit secondary. If a Saints backup can find that much grass, Allen will find more. The Lions can still hang 27. The Bills hang 30 and walk out of their own new building with a 2-0 start.</p>
      <p>Fantasy rooms already know the start list. Allen. Gibbs. Amon-Ra St. Brown. James Cook. The stream if you like points after turnovers is Buffalo's defense only if you already rostered it. Detroit's defense just watched Shough throw fifty-six times. Sit that one.</p>

      <figure>
        <div class="photo-pair">
          {_shot("josh-allen", "png", "Josh Allen")}
          {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        </div>
        <figcaption>Allen at home on a short week. Gibbs on the road after overtime. The mash has already chosen a building.</figcaption>
      </figure>

      <h2>Sunday at one: eight games, eight names</h2>
      <p><strong>Carolina at Atlanta. Pick: ATL.</strong> The mash splits. Sporting News and CBS both printed the Panthers, 23-20 and 24-17. The market still has Atlanta minus a point and a half. Week 1 winners like Carolina because Carolina already scored 37. Post-opener power likes Atlanta. Ties go home on this board, and the home club is Atlanta, which is also where Bijan Robinson just piled 173 total yards and where Tua Tagovailoa's oblique is still a Wednesday question. Jalen Coker caught eight for 138 and two scores in Charlotte. He will cost real FAAB even if the mash fades his club. I am taking the Falcons by a field goal and telling every room to spend the wire on Coker anyway.</p>
      <p><strong>New Orleans at Baltimore. Pick: BAL.</strong> Lamar Jackson's club hung 41 on Indianapolis. Derrick Henry ran for 144 and three. Tyler Shough just threw for 410 in Detroit and now has to do it in Baltimore, which is a colder ask. Bender has the Ravens 29-22. Breech has them 34-23. Every full card we mashed took Baltimore. Stream the Ravens defense if you like points after turnovers. Stream Shough in superflex rooms that lost Sam Darnold. Sit Shough in one-quarterback rooms that still have a cleaner Sunday name.</p>
      <p><strong>Minnesota at Chicago. Pick: CHI.</strong> Chicago hung 59 in Charlotte. Caleb Williams threw for two and ran for two. D'Andre Swift ran for 124 and three. Kyle Monangai added 100. Minnesota, with Carson Wentz likely starting for Kyler Murray, just beat Green Bay 39-22 and now has to visit a building that just set a Week 1 scoring record. Bender has the Bears 30-23. Breech has them 20-17, which is the nervous version of the same sentence. The mash is clean. Start Williams. Start Swift. Start Cairo Santos. Treat Chicago's defense like a matchup, because Minnesota already remembered how to finish.</p>

      <div class="photo-row">
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("jalen-coker", "jpg", "Jalen Coker")}
        {_shot("lamar-jackson", "png", "Lamar Jackson")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
      </div>
      <p class="photo-cap">Robinson in Atlanta. Coker on the wire. Jackson at home. Williams after 59. The one o'clock window already has a weather report.</p>

      <p><strong>Cincinnati at Houston. Pick: CIN.</strong> This is the one the market and the writers split on last week and then watched the Bengals win a track meet, 33-27, in Tampa. Bender has Cincinnati 30-28. Breech has Cincinnati 23-20. Sports Brackets took the Bengals too. The Texans just hung 31 on Buffalo and still lost, which is the kind of afternoon that makes a room believe in C.J. Stroud and then ask the same room to fade him at home. I am taking Burrow on the road. Ja'Marr Chase had two catches for twelve in the opener. That line is a buy, and this is the week the buy comes due.</p>
      <p><strong>Pittsburgh at New England. Pick: NE.</strong> Four boards on each side. Bender likes the Steelers 21-19. Breech likes the Patriots 27-20. The market has New England minus 5.5, which is a sentence that would have sounded like fan fiction in July and now has a 13-10 Seattle loss sitting behind it. Drake Maye threw three fourth-quarter interceptions and said those mistakes were unacceptable. Aaron Rodgers and T.J. Watt just beat Atlanta 20-13. Ties go home. The home club is New England, and the home club still has Maye's arm even after Wednesday's mess. Start Maye if you rostered him. Stream New England's defense only if you like the idea of Watt being the one who has to travel.</p>
      <p><strong>Green Bay at the Jets. Pick: GB.</strong> Jordan Love threw for 387 and two, then watched a 22-point fourth quarter evaporate in Minnesota. The Jets looked like a club that could tackle against Tennessee. Bender has the Packers 28-21. Breech has them 26-23. The market has Green Bay minus 4.5. PFF put Love on the Week 2 waiver list because forty-two percent of ESPN rooms still have him sitting there, which is a fact that should embarrass those rooms. Start Love. Start Breece Hall. Fade the Jets defense against a quarterback who just proved he can still throw it fifty times.</p>
      <p><strong>Cleveland at Tampa Bay. Pick: TB.</strong> Baker Mayfield against the club that traded him is the revenge script every column already wrote, and the mash agrees with the script. Bender 31-21. Breech 34-16. Four clean votes for Tampa, zero for Cleveland. The Browns just lost 34-10 in Jacksonville. Deshaun Watson took five sacks. The Buccaneers gave up four turnovers and still look like a club that can score at home. Start Mayfield. Start Chase McLaughlin. Start Tampa Bay's defense. That is the cheapest three-piece on the stream this week.</p>
      <p><strong>Philadelphia at Tennessee. Pick: PHI.</strong> Jalen Hurts survived Washington 24-22. The Titans went 2 of 12 on third down against the Jets. Bender 27-17. Breech 27-16. Every full card took the Eagles. The Week 2 DST mash already has Philadelphia first or second on almost every list. Start the Eagles defense. Start Hurts. Start Saquon Barkley. Sit the Titans unless you enjoy watching a first-year staff introduce itself twice.</p>

      <figure>
        <div class="photo-pair">
          {_shot("joe-burrow", "png", "Joe Burrow")}
          {_shot("baker-mayfield", "png", "Baker Mayfield")}
        </div>
        <figcaption>Burrow on the road in Houston. Mayfield at home against Cleveland. Two Sunday afternoons that already have a shape.</figcaption>
      </figure>

      <h2>Sunday late: Denver's altitude, Santa Clara's gap, and a Cardinals home opener</h2>
      <p><strong>Jacksonville at Denver. Pick: DEN.</strong> This was the split on Monday. Sporting News' ATS card had the Jaguars. Bender's SU card flipped to Denver 28-27. Breech has Denver 30-27. Sports Brackets took Denver. The Jaguars just won 34-10 and Trevor Lawrence looked like Year 2 of Liam Coen. The Broncos just lost 31-10 on Monday night and now have to host a club that already beat them last December. Home openers at altitude still count. The mash landed on Denver by a vote, 4-2 among the boards that picked a side. I am taking Denver and telling every room that streamed Jacksonville's defense last week to find a new stream. Week 2 DST already moved on.</p>
      <p><strong>Las Vegas at the Chargers. Pick: LAC.</strong> The Chargers lost in Arizona as a double-digit favorite and took ten million Circa survivor dollars with them. The Raiders beat Miami 27-13 and Michael Mayer led the club in targets while Brock Bowers waits on a meniscus. Bender 24-20. Breech 27-19. The market has Los Angeles minus 7. Jim Harbaugh is 4-0 against this opponent. Start Justin Herbert if you rostered him. Stream the Chargers defense. Add Mayer if Bowers sits another week.</p>
      <p><strong>Seattle at Arizona. Pick: SEA.</strong> Breech took the Cardinals 20-17 and said he had lost his mind. The mash kept its mind. Bender 21-18 Seattle. Four votes for the Seahawks, two for Arizona. Sam Darnold is expected to miss the trip. Drew Lock starts on the road against a club that just beat the Chargers and never trailed. Trey McBride caught nine for 95. Jacoby Brissett does not beat himself. I still have Seattle, because nine in a row in this series is a habit, and because Mike Macdonald's defense already stole a Wednesday night. Start McBride. Start Jaxon Smith-Njigba even with Lock. Stream Seattle's defense if you like the habit.</p>
      <p><strong>Washington at Dallas. Pick: DAL.</strong> The Giants just beat the Cowboys 28-20 on Sunday night. Washington just lost to Philadelphia by two. Bender 30-24 Dallas. Breech 34-24 Dallas. Sports Brackets took the Commanders. The mash went home, 4-2. Dak Prescott at home still has CeeDee Lamb and George Pickens. Jayden Daniels completed 52 percent in the opener. Start the Dallas skill names. Sit Washington's defense. Jacory Croskey-Merritt is a hold, a start only if your other backs already spent their week.</p>
      <p><strong>Miami at San Francisco. Pick: SF.</strong> The widest number on the board, 12 and a half, and the cleanest vote. Seven published sides for the 49ers, zero for the Dolphins. Bender 34-14. Breech 38-16, which is Super Bowl XIX's score, which he said out loud. Brock Purdy threw three touchdowns in Melbourne. Christian McCaffrey shared the night with Kaelon Black, who is about to cost real FAAB. Malik Willis ran for a score and still looked like a man playing behind a payroll that is larger off the roster than on it. Start Purdy. Start McCaffrey. Start the 49ers defense. Add Black even if you already roster the starter. Sit Miami unless Achane is your last running back and you enjoy hoping.</p>

      <div class="photo-row">
        {_shot("trevor-lawrence", "jpg", "Trevor Lawrence")}
        {_shot("justin-herbert", "png", "Justin Herbert")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
      </div>
      <p class="photo-cap">Lawrence in Denver. Herbert after the survivor wipe. Smith-Njigba with Lock. McCaffrey at home against Miami. The late window is where the card gets wide.</p>

      <h2>Sunday night: Indianapolis at Kansas City. Pick: KC</h2>
      {_film("fcu9F0Am9L8", "Kenneth Walker finding the edge. Monday in Kansas City already looked like this. Sunday night gets Indianapolis.")}
      <p>Kenneth Walker ran for 173 and two on Monday night. Patrick Mahomes, brace on the left knee, threw for 184 and two and ran for another. The Colts already know what a 41-point Ravens afternoon feels like. They now get Arrowhead. Bender 27-17. Breech 23-16. Four clean votes for Kansas City, zero for Indianapolis. Start Walker. Start Mahomes. Start Harrison Butker. Jonathan Taylor is still a start, because a feature back on a losing script still touches the ball. The Colts defense is a fade.</p>

      <figure>
        <div class="photo-pair">
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
          {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        </div>
        <figcaption>Walker: 173 in the debut, now a Sunday-night feature. Mahomes: a brace, a home crowd, and a club that looked like itself.</figcaption>
      </figure>

      <h2>Monday: the Giants at the Rams. Pick: LAR</h2>
      <p>Los Angeles scored seven in Melbourne and still opened as a touchdown favorite at home. Breech almost talked himself into the Giants and then printed the Rams 27-24 anyway. Bender has them 28-21. The mash is 3-1 Los Angeles among the full cards, plus the market and the power board. Myles Garrett is on injured reserve. Aaron Donald's first snap since 2023 is a Wednesday question. Jaxson Dart and Cam Skattebo already ran for 135. Matthew Stafford gets a chance to look like himself in a building that speaks his language. I am taking the Rams and telling every room that sat Puka Nacua after Australia to put him back in. Hold Kyren Williams. Hold Davante Adams. Start Wan'Dale Robinson if you added him. The Giants can keep it to a field goal. The Rams still walk out 1-1.</p>

      <figure>
        <div class="photo-pair">
          {_shot("matthew-stafford", "png", "Matthew Stafford")}
          {_shot("jaxson-dart", "jpg", "Jaxson Dart")}
        </div>
        <figcaption>Stafford after Melbourne. Dart after a Sunday-night win in Dallas. Monday night in Los Angeles is the last line on the card.</figcaption>
      </figure>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the winners in kickoff order if you came here for the list: BUF, ATL, BAL, CHI, CIN, NE, GB, TB, PHI, DEN, LAC, SEA, DAL, SF, KC, LAR. That is the mash as it stands Wednesday. Thursday can change a line. It cannot change the fact that every game already has a side.</p>
      <p>The <a href="waiver.html">Week 2 waiver board</a> still opens with Jalen Coker. Kaelon Black is the back. Tyler Shough and Devaughn Vele are the Saints tickets. Michael Mayer is the tight end if Brock Bowers sits. RotoWire spent Tuesday adding DeMario Douglas, Rashod Bateman, and Caleb Douglas. PFF spent Monday adding Jordan Love and Malik Willis. Spend the leftover FAAB on the names the tape actually moved, then come back to this page on Thursday and see if Buffalo did what eight boards said it would do.</p>
      <p>The <a href="week2-dst.html">Week 2 DST board</a> still leans San Francisco, Philadelphia, Tampa Bay, and Seattle. The <a href="week2-kickers.html">kicker board</a> still loves Brandon Aubrey and has learned to say Eddy Pineiro out loud. The <a href="weekly.html">weekly skill boards</a> rebuilt this afternoon from FantasyPros ECR, sixty-plus experts, plus RotoWire, 4for4, and the rest of the kit.</p>

      <div class="ramif">
        <h3>The sixteen, one more time</h3>
        <ul>
          <li>BUF over DET on Thursday. Short week, new building, Allen at home.</li>
          <li>ATL over CAR. The writers like Carolina. The market and the tiebreak stay in Atlanta.</li>
          <li>BAL over NO. Shough can throw. Baltimore can hit.</li>
          <li>CHI over MIN. Fifty-nine points still count on Wednesday.</li>
          <li>CIN over HOU. Burrow on the road after a track meet.</li>
          <li>NE over PIT. Four and four, and the home club keeps the nod.</li>
          <li>GB over NYJ. Love already threw for 387. The Jets already used their opener.</li>
          <li>TB over CLE. Mayfield at home against the old room.</li>
          <li>PHI over TEN. The defense boards already voted.</li>
          <li>DEN over JAX. Altitude, a home opener, and a one-score card.</li>
          <li>LAC over LV. Harbaugh's series, even after Arizona.</li>
          <li>SEA over ARI. Lock on the road. Macdonald's habit.</li>
          <li>DAL over WAS. Prescott at home after a Sunday-night loss.</li>
          <li>SF over MIA. The widest number, the cleanest vote.</li>
          <li>KC over IND. Walker already wrote the Monday chapter.</li>
          <li>LAR over NYG. Stafford gets a Monday that looks like home.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that has not happened yet. Allen pointing in a building that still smells like paint. Gibbs on the sideline after a short week that asked too much. Coker in Atlanta colors, or at least Atlanta weather, trying to prove Charlotte was a habit. Maye at home, trying to prove Seattle was a night and not a year. Purdy against a Dolphins club that is already living in a hole. Walker again, in red, under Sunday-night lights. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both before Thursday kickoff, then spend the wire on the names the opener already moved.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card, Sep 16), John Breech at CBS Sports (Sep 15), Sports Brackets, Sportsnaut, NFL Spin Zone, The Game Haus, the published FanDuel and CBS SportsLine numbers, a Week 1 winners board, and a short post-opener power card. Waiver names from RotoBaller, SI OnSI, ESPN, FantasyPros, RotoWire's Tuesday update, and PFF. Scores from the opener sit on <a href="the-recap.html">The Recap</a>. Finals we are asking this card to beat: BUF over DET; ATL over CAR; BAL over NO; CHI over MIN; CIN over HOU; NE over PIT; GB over NYJ; TB over CLE; PHI over TEN; DEN over JAX; LAC over LV; SEA over ARI; DAL over WAS; SF over MIA; KC over IND; LAR over NYG.</p>
    </article>
    """
