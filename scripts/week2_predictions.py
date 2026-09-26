"""Week 2 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Sixteen games, a new Highmark, and a card that already has a memory."
DEK = (
    "Monday wrote the last score. The Rams hung 28-6 in Inglewood. "
    "The mash finished eleven and five. Carolina hung 34 in Atlanta. "
    "Kansas City needed overtime. Stafford threw four."
)
PUBLISHED = "2026-09-16T14:00:00Z"
MODIFIED = "2026-09-22T18:00:00Z"
OG_IMAGE = "img/players/josh-allen.png"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week2-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=MODIFIED,
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
        <p class="k">Week 2 · Tuesday, Sep 22</p>
        <h2>Bills over Lions. Monday paid eleven.</h2>
        <p>Rams 28-6. Carolina 34-3. San Francisco 35-13. Kansas City in overtime. The mash closed 11-5.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 2 · Sixteen receipts · Tuesday, September 22, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Wednesday. Monday final added Tuesday morning.</p>

      <div class="score-row recap-scores">
        <div class="score-card is-final"><p class="when">Thu · Final</p><p class="result">BUF 41, DET 31</p><p class="meta">Allen 5 TD · Cook 134 rush</p></div>
        <div class="score-card is-final"><p class="when">Sun · FOX</p><p class="result">SF 35, MIA 13</p><p class="meta">Purdy 20 of 22 · CMC 100th TD</p></div>
        <div class="score-card is-final"><p class="when">Sun · NBC</p><p class="result">KC 33, IND 30 OT</p><p class="meta">Mahomes 382 · Walker 117 · Butker 40</p></div>
        <div class="score-card is-final"><p class="when">Mon · ESPN</p><p class="result">LAR 28, NYG 6</p><p class="meta">Stafford 4 TD · Adams 8-195-2</p></div>
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
      <p class="photo-cap">Allen, Gibbs, Purdy, Hurts, Mahomes, Williams, Maye, McCaffrey. Thursday, Sunday, and Monday all have a number now.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet, and a prediction page that also prints the argument starts to feel like a room you can sit in on a Wednesday. The mash above already voted. What follows is the walk through sixteen games in kickoff order, using the published cards from Sporting News, CBS Sports, Sports Brackets, Sportsnaut, the market, and the tape we just watched, with a side on every game and the winners copied at the bottom of the table for anyone who wants the list without the sentences.</p>

      {_film("2kwY6ve5E88", "Josh Allen tape. Four scores in the opener, and Thursday night in the new Highmark asks for another chapter.")}

      <h2>Thursday: Detroit at Buffalo. Pick: BUF</h2>
      <p>The new Highmark Stadium gets its first regular-season night, and the league handed it the two clubs that just scored 67 points between them. Buffalo beat Houston 36-31. Detroit survived New Orleans 31-30 in overtime. Bill Bender at Sporting News has the Bills 28-26. John Breech at CBS Sports has them 38-31. NFL Spin Zone printed 31-23. Sportsnaut printed 35-31. The Game Haus leaned Detroit against the number and still left the favorite on the moneyline. The mash is loud about Buffalo. Seven of the eight boards that bothered to pick this game took the home side. I am taking the home side with them.</p>
      <p>Jahmyr Gibbs already has his first chapter, 156 yards of it, and now he has to spend it on a short week after an overtime, which is a brutal way to open Thursday Night Football. Josh Allen accounted for four scores against a Texans defense that was supposed to be the grown-up in the room, and Tyler Shough threw for 410 on that same Detroit secondary, so a Saints backup finding that much grass is the hint that Allen will find more. The Lions can still hang 27. The Bills hang 30 and walk out of their own new building with a 2-0 start.</p>
      <p>Saturday morning now has the receipt. Buffalo 41, Detroit 31. Josh Allen accounted for five scores. James Cook ran for 134. The mash took the home side on Wednesday and the home side cashed on Thursday night in a building that still smelled like paint. The Lions hung 31 and walked out 1-1. Buffalo is 2-0, and the rest of the card is still Sunday and Monday.</p>
      <p>Fantasy rooms already know the start list, Allen and Gibbs and Amon-Ra St. Brown and James Cook, and Buffalo's defense is a stream for points after turnovers only in the rooms that already rostered it. Detroit's defense just watched Shough throw fifty-six times, which is a sit even before the short week.</p>

      <figure>
        <div class="photo-pair">
          {_shot("josh-allen", "png", "Josh Allen")}
          {_shot("jahmyr-gibbs", "jpg", "Jahmyr Gibbs")}
        </div>
        <figcaption>Allen at home on a short week. Gibbs on the road after overtime. The mash has already chosen a building.</figcaption>
      </figure>

      <h2>Sunday at one: eight games, eight names</h2>
      <p><strong>Carolina at Atlanta. Pick: ATL.</strong> The mash splits. Sporting News and CBS both printed the Panthers, 23-20 and 24-17. The market still has Atlanta minus a point and a half. Week 1 winners like Carolina because Carolina already scored 37. Post-opener power likes Atlanta. Ties go home on this board, and the home club is Atlanta, which is also where Bijan Robinson just piled 173 total yards and where Tua Tagovailoa's oblique is still a Wednesday question. Jalen Coker caught eight for 138 and two scores in Charlotte. He will cost real FAAB even if the mash fades his club. I am taking the Falcons by a field goal and telling every room to spend the wire on Coker anyway.</p>
      <p>Sunday receipt: Carolina 34, Atlanta 3. Bryce Young threw for 287 and three, two of them to Darren Waller. Devin Lloyd ran one of his two interceptions back. Cooper Rush threw for 86 with two picks and then sat. Bijan Robinson was held to 72 on the ground. The writers had this one. The mash took the building and the building lost by 31.</p>
      <p><strong>New Orleans at Baltimore. Pick: BAL.</strong> Lamar Jackson's club hung 41 on Indianapolis and Derrick Henry ran for 144 and three, while Tyler Shough just threw for 410 in Detroit and now has to do it in Baltimore, which is a colder ask. Bender has the Ravens 29-22. Breech has them 34-23. Every full card we mashed took Baltimore. The Ravens defense is the stream for points after turnovers, Shough is the Superflex stream in rooms that lost Sam Darnold, and one-quarterback rooms that still have a cleaner Sunday name can leave Shough on the bench.</p>
      <p>Sunday receipt: New Orleans 24, Baltimore 17. Shough threw for 252 and a score, then sneaked it on fourth down with 1:28 left. Chris Olave had 86 and a touchdown. Every full card we mashed took Baltimore. The Saints took the building.</p>
      <p><strong>Minnesota at Chicago. Pick: CHI.</strong> Chicago hung 59 in Charlotte, Caleb Williams threw for two and ran for two, D'Andre Swift ran for 124 and three, and Kyle Monangai added 100. Minnesota, with Carson Wentz likely starting for Kyler Murray, just beat Green Bay 39-22 and now has to visit a building that just set a Week 1 scoring record. Bender has the Bears 30-23. Breech has them 20-17, which is the nervous version of the same sentence. The mash is clean on Chicago, and Williams and Swift and Cairo Santos are the names you start while Chicago's defense has to be treated like a matchup because Minnesota already remembered how to finish.</p>
      <p>Sunday receipt: Minnesota 9, Chicago 3, in the rain, Isaiah Rodgers recovering a fumble and blocking a late kick while Caleb Williams left with a right hamstring and the 59 points from the opener stayed in Charlotte.</p>

      <div class="photo-row">
        {_shot("bijan-robinson", "jpg", "Bijan Robinson")}
        {_shot("jalen-coker", "jpg", "Jalen Coker")}
        {_shot("lamar-jackson", "png", "Lamar Jackson")}
        {_shot("caleb-williams", "jpg", "Caleb Williams")}
      </div>
      <p class="photo-cap">Robinson in Atlanta. Coker on the wire. Jackson at home. Williams after 59. The one o'clock window already has a weather report.</p>

      <p><strong>Cincinnati at Houston. Pick: CIN.</strong> This is the one the market and the writers split on last week and then watched the Bengals win a track meet, 33-27, in Tampa. Bender has Cincinnati 30-28. Breech has Cincinnati 23-20. Sports Brackets took the Bengals too. The Texans just hung 31 on Buffalo and still lost, which is the kind of afternoon that makes a room believe in C.J. Stroud and then ask the same room to fade him at home. I am taking Burrow on the road. Ja'Marr Chase had two catches for twelve in the opener. That line is a buy, and this is the week the buy comes due.</p>
      <p>Sunday receipt: Cincinnati 20, Houston 6. Burrow found Chase twice. The buy came due, and the mash cashed it.</p>
      <p><strong>Pittsburgh at New England. Pick: NE.</strong> Four boards on each side. Bender likes the Steelers 21-19. Breech likes the Patriots 27-20. The market has New England minus 5.5, which is a sentence that would have sounded like fan fiction in July and now has a 13-10 Seattle loss sitting behind it. Drake Maye threw three fourth-quarter interceptions and said those mistakes were unacceptable, and Aaron Rodgers and T.J. Watt just beat Atlanta 20-13. Ties go home, the home club is New England, and the home club still has Maye's arm even after Wednesday's mess, so rooms that rostered him start him and rooms that like Watt traveling can stream New England's defense.</p>
      <p>Sunday receipt: New England 20, Pittsburgh 3. TreVeyon Henderson ran 39 yards for a score in his season debut. Eli Ponder took a fumble the other way. Maye still threw a bad ball into the third quarter, and the defense still made the afternoon look finished.</p>
      <p><strong>Green Bay at the Jets. Pick: GB.</strong> Jordan Love threw for 387 and two, then watched a 22-point fourth quarter evaporate in Minnesota, while the Jets looked like a club that could tackle against Tennessee. Bender has the Packers 28-21. Breech has them 26-23. The market has Green Bay minus 4.5. PFF put Love on the Week 2 waiver list because forty-two percent of ESPN rooms still have him sitting there, which is a fact that should embarrass those rooms. Love and Breece Hall are the Sunday names, and the Jets defense is a fade against a quarterback who just proved he can still throw it fifty times.</p>
      <p>Sunday receipt: Green Bay 20, New York 17, in overtime. The mash took the Packers and the Packers walked out with a field goal in the extra session.</p>
      <p><strong>Cleveland at Tampa Bay. Pick: TB.</strong> Baker Mayfield against the club that traded him is the revenge script every column already wrote, and the mash agrees with the script. Bender 31-21. Breech 34-16. Four clean votes for Tampa, zero for Cleveland. The Browns just lost 34-10 in Jacksonville and Deshaun Watson took five sacks, while the Buccaneers gave up four turnovers and still look like a club that can score at home, which makes Mayfield and Chase McLaughlin and Tampa Bay's defense the cheapest three-piece on the stream this week.</p>
      <p>Sunday receipt: Cleveland 23, Tampa Bay 19, after a lightning delay that lasted two hours and twelve minutes. Watson threw two scores, one of them 55 yards to Denzel Boston. Mayfield's last throw on fourth down sailed past Emeka Egbuka. The revenge script stayed in the columns.</p>
      <p><strong>Philadelphia at Tennessee. Pick: PHI.</strong> Jalen Hurts survived Washington 24-22 and the Titans went 2 of 12 on third down against the Jets. Bender 27-17. Breech 27-16. Every full card took the Eagles, and the Week 2 DST mash already has Philadelphia first or second on almost every list, so the Eagles defense and Hurts and Saquon Barkley are the Sunday names and the Titans are a sit unless a person enjoys watching a first-year staff introduce itself twice.</p>
      <p>Sunday receipt: Philadelphia 24, Tennessee 20. Hurts found Darius Cooper from three yards with nine seconds left. DeVonta Smith caught ten for 117. The turf measured 157 degrees and the mash still cashed.</p>

      <figure>
        <div class="photo-pair">
          {_shot("joe-burrow", "png", "Joe Burrow")}
          {_shot("baker-mayfield", "png", "Baker Mayfield")}
        </div>
        <figcaption>Burrow on the road in Houston. Mayfield at home against Cleveland. Two Sunday afternoons that already have a shape.</figcaption>
      </figure>

      <h2>Sunday late: Denver's altitude, Santa Clara's gap, and a Cardinals home opener</h2>
      <p><strong>Jacksonville at Denver. Pick: DEN.</strong> This was the split on Monday. Sporting News' ATS card had the Jaguars. Bender's SU card flipped to Denver 28-27. Breech has Denver 30-27. Sports Brackets took Denver. The Jaguars just won 34-10 and Trevor Lawrence looked like Year 2 of Liam Coen. The Broncos just lost 31-10 on Monday night and now have to host a club that already beat them last December. Home openers at altitude still count. The mash landed on Denver by a vote, 4-2 among the boards that picked a side. I am taking Denver and telling every room that streamed Jacksonville's defense last week to find a new stream. Week 2 DST already moved on.</p>
      <p>Sunday receipt: Denver 20, Jacksonville 13. Jaylen Waddle caught eight for 138. Jonah Coleman punched a 3-yard score after J.K. Dobbins left with a hamstring. Jacksonville's nine-game regular-season streak ended at altitude, and the mash had the home side.</p>
      <p><strong>Las Vegas at the Chargers. Pick: LAC.</strong> The Chargers lost in Arizona as a double-digit favorite and took ten million Circa survivor dollars with them. The Raiders beat Miami 27-13 and Michael Mayer led the club in targets while Brock Bowers waits on a meniscus. Bender 24-20. Breech 27-19. The market has Los Angeles minus 7. Jim Harbaugh is 4-0 against this opponent, so rooms that rostered Justin Herbert start him, the Chargers defense is the stream, and Mayer is the add while Bowers sits another week.</p>
      <p>Sunday receipt: Las Vegas 26, Los Angeles 14. Kirk Cousins found Cody White twice. The series habit broke, and the mash took the Chargers into a hole.</p>
      <p><strong>Seattle at Arizona. Pick: SEA.</strong> Breech took the Cardinals 20-17 and said he had lost his mind. The mash kept its mind. Bender 21-18 Seattle. Four votes for the Seahawks, two for Arizona. Sam Darnold is expected to miss the trip, and Drew Lock starts on the road against a club that just beat the Chargers and never trailed. Trey McBride caught nine for 95 and Jacoby Brissett does not beat himself. I still have Seattle, because nine in a row in this series is a habit and because Mike Macdonald's defense already stole a Wednesday night, which makes McBride and Jaxon Smith-Njigba the Sunday names even with Lock and makes Seattle's defense a stream for anyone who likes the habit.</p>
      <p>Sunday receipt: Seattle 31, Arizona 7. Drew Lock threw three scores on the road. The habit held, and Breech can keep the sentence about losing his mind.</p>
      <p><strong>Washington at Dallas. Pick: DAL.</strong> The Giants just beat the Cowboys 28-20 on Sunday night and Washington just lost to Philadelphia by two. Bender 30-24 Dallas. Breech 34-24 Dallas. Sports Brackets took the Commanders. The mash went home, 4-2. Dak Prescott at home still has CeeDee Lamb and George Pickens, and Jayden Daniels completed 52 percent in the opener, so the Dallas skill names are the Sunday starts, Washington's defense is a sit, and Jacory Croskey-Merritt is a hold who becomes a start only when the other backs have already spent their week.</p>
      <p>Sunday receipt: Dallas 37, Washington 20. The home side did what the mash asked, and the Dallas skill names got a full afternoon.</p>
      <p><strong>Miami at San Francisco. Pick: SF.</strong> The widest number on the board, 12 and a half, and the cleanest vote. Seven published sides for the 49ers, zero for the Dolphins. Bender 34-14. Breech 38-16, which is Super Bowl XIX's score, which he said out loud. Brock Purdy threw three touchdowns in Melbourne and Christian McCaffrey shared the night with Kaelon Black, who is about to cost real FAAB, while Malik Willis ran for a score and still looked like a man playing behind a payroll that is larger off the roster than on it. Purdy and McCaffrey and the 49ers defense are the Sunday names, Black is the add even in rooms that already roster the starter, and Miami is a sit unless Achane is the last running back a person has and hoping is the plan.</p>
      <p>Sunday receipt: San Francisco 35, Miami 13. Purdy went 20 of 22 for 287, two throw scores and a run score. McCaffrey became the fourth-fastest player in the Super Bowl era to 100 career touchdowns. The widest number on the card was also the cleanest vote, and it cashed by 22.</p>

      <div class="photo-row">
        {_shot("trevor-lawrence", "jpg", "Trevor Lawrence")}
        {_shot("justin-herbert", "png", "Justin Herbert")}
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("christian-mccaffrey", "png", "Christian McCaffrey")}
      </div>
      <p class="photo-cap">Lawrence in Denver. Herbert after the survivor wipe. Smith-Njigba with Lock. McCaffrey at home against Miami. The late window is where the card gets wide.</p>

      <h2>Sunday night: Indianapolis at Kansas City. Pick: KC</h2>
      {_film("fcu9F0Am9L8", "Kenneth Walker finding the edge. Monday in Kansas City already looked like this. Sunday night gets Indianapolis.")}
      <p>Kenneth Walker ran for 173 and two on Monday night, and Patrick Mahomes, brace on the left knee, threw for 184 and two and ran for another. The Colts already know what a 41-point Ravens afternoon feels like, and they now get Arrowhead. Bender 27-17. Breech 23-16. Four clean votes for Kansas City, zero for Indianapolis. Walker and Mahomes and Harrison Butker are the Sunday names, Jonathan Taylor is still a start because a feature back on a losing script still touches the ball, and the Colts defense is a fade.</p>
      <p>Sunday receipt: Kansas City 33, Indianapolis 30, in overtime. Mahomes threw for 382 and three. Walker ran for 117 and caught six for 61, including the 22-yarder that set up Harrison Butker's 40-yard kick as time expired. Travis Kelce caught nine for 101 and a score. Jonathan Taylor scored twice and still left 0-2. The mash took Kansas City and Kansas City needed every minute.</p>

      <figure>
        <div class="photo-pair">
          {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
          {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        </div>
        <figcaption>Walker: 173 in the debut, now a Sunday-night feature. Mahomes: a brace, a home crowd, and a club that looked like itself.</figcaption>
      </figure>

      <h2>Monday: the Giants at the Rams. Pick: LAR</h2>
      <p>Los Angeles scored seven in Melbourne and still opened as a touchdown favorite at home. Breech almost talked himself into the Giants and then printed the Rams 27-24 anyway. Bender has them 28-21. The mash is 3-1 Los Angeles among the full cards, plus the market and the power board. Myles Garrett is on injured reserve, Aaron Donald's first snap since 2023 is a Wednesday question, and Jaxson Dart and Cam Skattebo already ran for 135. Matthew Stafford gets a chance to look like himself in a building that speaks his language. I am taking the Rams, and rooms that sat Puka Nacua after Australia should put him back in while Kyren Williams and Davante Adams stay held and Wan'Dale Robinson is a start in the rooms that added him. The Giants can keep it to a field goal. The Rams still walk out 1-1.</p>
      <p>Monday receipt: Los Angeles 28, New York 6. Stafford went 22 of 31 for 327 and four scores, two of them to Davante Adams, one to Kyren Williams, one to Terrance Ferguson. Adams caught eight for 195. Dart left with a left knee on the first series. Jameis Winston threw 11 of 27. Puka Nacua was inactive. The mash took the home side on Wednesday and the home side cashed by 22. Both clubs are 1-1.</p>

      <figure>
        <div class="photo-pair">
          {_shot("matthew-stafford", "png", "Matthew Stafford")}
          {_shot("jaxson-dart", "jpg", "Jaxson Dart")}
        </div>
        <figcaption>Stafford after Melbourne, then four scores on Monday. Dart after a Sunday-night win in Dallas, then a left knee on the first series.</figcaption>
      </figure>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the published picks in kickoff order if you came here for the list: BUF, ATL, BAL, CHI, CIN, NE, GB, TB, PHI, DEN, LAC, SEA, DAL, SF, KC, LAR. Thursday paid. Sunday paid ten and missed five. Monday paid. The mash closed 11-5.</p>
      <p>The <a href="waiver.html">Week 2 waiver board</a> still opens with Jalen Coker, and Coker just played 76 percent of the snaps in a 34-3 win. Kaelon Black is the back. Tyler Shough just beat Baltimore. Michael Mayer is the tight end if Brock Bowers sits. Spend the leftover FAAB on the names Sunday actually moved.</p>
      <p>The <a href="week2-dst.html">Week 2 DST board</a> leaned San Francisco, Philadelphia, Tampa Bay, and Seattle. San Francisco, Philadelphia, and Seattle cashed. Tampa Bay left the points on the grass. The <a href="week2-kickers.html">kicker board</a> still loves Brandon Aubrey. The <a href="weekly.html">weekly skill boards</a> rebuilt this morning from FantasyPros ECR dated September 22, plus RotoWire, 4for4, and the rest of the kit.</p>

      <div class="ramif">
        <h3>The sixteen, one more time</h3>
        <ul>
          <li>BUF over DET. Final 41-31. Paid.</li>
          <li>ATL over CAR. Final CAR 34-3. Missed.</li>
          <li>BAL over NO. Final NO 24-17. Missed.</li>
          <li>CHI over MIN. Final MIN 9-3. Missed.</li>
          <li>CIN over HOU. Final 20-6. Paid.</li>
          <li>NE over PIT. Final 20-3. Paid.</li>
          <li>GB over NYJ. Final 20-17 OT. Paid.</li>
          <li>TB over CLE. Final CLE 23-19. Missed.</li>
          <li>PHI over TEN. Final 24-20. Paid.</li>
          <li>DEN over JAX. Final 20-13. Paid.</li>
          <li>LAC over LV. Final LV 26-14. Missed.</li>
          <li>SEA over ARI. Final 31-7. Paid.</li>
          <li>DAL over WAS. Final 37-20. Paid.</li>
          <li>SF over MIA. Final 35-13. Paid.</li>
          <li>KC over IND. Final 33-30 OT. Paid.</li>
          <li>LAR over NYG. Final 28-6. Paid.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that now has sixteen receipts. Allen pointing in a building that still smelled like paint, and that picture has a 41 next to it. Young in Atlanta, 287 and three, with Waller twice. Purdy almost perfect in Santa Clara. Lock throwing three on the road. Mahomes and Walker asking Butker to finish an overtime. Maye winning ugly at home. Williams leaving Chicago in the rain. Stafford finding Adams twice on a Monday that finally looked like a favorite. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both, then spend the wire on the names the card actually moved.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card, Sep 16), John Breech at CBS Sports (Sep 15), Sports Brackets, Sportsnaut, NFL Spin Zone, The Game Haus, the published FanDuel and CBS SportsLine numbers, a Week 1 winners board, and a short post-opener power card. Thursday, Sunday, and Monday finals from the published boxes. Mash on the finished card: 11-5. Waiver names from RotoBaller, SI OnSI, ESPN, FantasyPros, RotoWire, and PFF. Scores from the opener sit on <a href="the-recap.html">The Recap</a>. The full Week 2 tape sits on <a href="week2-tape.html">The Second Sunday</a>.</p>
    </article>
    """
