"""Week 6 predictions essay: a pick for every game, written in kickoff order."""
from __future__ import annotations

from seo import article_jsonld

HEADLINE = "Lutz walked into overtime with the whole building already tired of turnovers, and Sunday still has thirteen games and four empty chairs."
DEK = (
    "Broncos 17-14. Wilson 52. Smith-Njigba 134. The mash took Seattle. "
    "Cincinnati, Detroit, Miami, and Minnesota sit. "
    "Sunday and Monday are still open."
)
PUBLISHED = "2026-10-17T21:30:00Z"
MODIFIED = "2026-10-17T21:30:00Z"
OG_IMAGE = "img/players/jaxon-smith-njigba.jpg"

PREDICTION_LD = [
    article_jsonld(
        HEADLINE,
        "https://ballkeep.com/week6-matchups.html",
        DEK,
        published=PUBLISHED,
        modified=MODIFIED,
        image=OG_IMAGE,
        brand="Ball Keep",
        section="Week 6",
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
    <a class="opening-teaser recap-teaser" href="week6-matchups.html">
      <img src="{OG_IMAGE}" alt="Jaxon Smith-Njigba" width="160" height="160" />
      <div>
        <p class="k">Week 6 · Saturday, Oct 17</p>
        <h2>Broncos 17-14. Sunday is still open.</h2>
        <p>Denver 17-14 in overtime. The mash took Seattle. Thirteen games left. Four clubs sit.</p>
      </div>
    </a>
    """


def predictions_article_html():
    return f"""
    <article class="opening recap">
      <p class="opening-kicker">Week 6 · Thursday is in · Saturday, October 17, 2026</p>
      <h2 class="pred-hed">{HEADLINE}</h2>
      <p class="dek">{DEK}</p>
      <p class="byline">Ball Keep · Filed Saturday. Denver final Thursday. Sunday card still live. Four clubs on bye.</p>

      <div class="score-row recap-scores">
        <div class="score-card is-final"><p class="when">Thu · Final</p><p class="result">DEN 17, SEA 14</p><p class="meta">OT · Lutz · Wilson 52 · JSN 134</p></div>
        <div class="score-card"><p class="when">Sun · NFLN</p><p class="result">HOU at JAX</p><p class="meta">London · Stroud after 26-3</p></div>
        <div class="score-card"><p class="when">Sun · NBC</p><p class="result">DAL at GB</p><p class="meta">Love after 367 · Lamb a quad</p></div>
        <div class="score-card"><p class="when">Mon · ESPN</p><p class="result">WAS at SF</p><p class="meta">Purdy 5-0 · Daniels after a tie</p></div>
      </div>

      <div class="photo-row" aria-label="Faces from the Week 6 card">
        {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
        {_shot("brock-purdy", "jpg", "Brock Purdy")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("drake-maye", "jpg", "Drake Maye")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
        {_shot("jordan-love", "png", "Jordan Love")}
      </div>
      <p class="photo-cap">Smith-Njigba after 134 on a night Seattle lost. Purdy still unbeaten. Allen in Las Vegas. Mahomes off a bye. Maye after 374. Walker at home against Herbert. Nacua against Arizona. Love on Sunday night.</p>

      <p class="lede">A prediction page that only prints a table starts to feel like a filing cabinet, and a prediction page that also prints the argument starts to feel like a room you can sit in on a Saturday while London is already packing and four clubs have already gone quiet. The mash above already voted. Thursday already wrote one receipt, and it wrote it in a building the mash had as a two-and-a-half-point dog. What follows is the walk through fourteen games in kickoff order, using the published cards from Bill Bender at Sporting News, Tyler Sullivan at CBS Sports, John Breech at CBS Sports, the CBS Sports expert table, the market, and the tape we just watched, with a side on every game and the winners copied at the bottom of the table for anyone who wants the list without the sentences.</p>

      <h2>Thursday: Seattle at Denver. Pick: SEA. Final: DEN 17-14</h2>
      <p>Five of seven. Bender printed 23-21 and still laid the two and a half. Sullivan printed Seattle. Breech printed Seattle. The whole CBS table printed Seattle. The market had Seattle minus 2.5 in a building that had already beaten two clubs at home and allowed 20 a night while doing it, which is a habit the mash decided was not enough. I took Seattle with them on Thursday because a short week still had Jaxon Smith-Njigba on it, and a habit that long usually gets one more night before it pays.</p>
      <p>Saturday morning now has the receipt. Denver 17, Seattle 14, overtime. Wil Lutz hit the kick after Sam Darnold spent the night throwing the ball into trouble, 278 yards that never turned into a lead that held. Emanuel Wilson ran 52. Smith-Njigba caught 134 and still walked out of Mile High with a loss. Seattle had seven turnovers in the two losses Bender already counted, and Thursday made it a third. The mash took the road favorite. The building won by three in extra time. Both clubs sit in the middle of the NFC West argument, and the rest of the card is still Sunday and Monday.</p>
      <p>Fantasy rooms already know what to do with a night like that. Start Smith-Njigba next week even if the Keep price already moved. Stream Denver if you still have a hole and you already spent Thursday watching Nix take a punch and survive it. Sit Seattle's defense unless you like a unit that just spent a short week giving the ball away. The waiver board has already moved on to Bernard and Pierce and Marks, and Sunday still has thirteen games left to move it again.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jaxon-smith-njigba", "jpg", "Jaxon Smith-Njigba")}
          {_shot("drake-maye", "jpg", "Drake Maye")}
        </div>
        <figcaption>Smith-Njigba after 134 in a loss. Maye after 374 and four, with the Jets visiting Foxborough.</figcaption>
      </figure>

      <h2>Sunday morning in London: Houston at Jacksonville. Pick: JAX</h2>
      <p>Four of six. Bender took the Texans 22-19 because Stroud is 3-2 as a starter against this club and London already gave Jacksonville a 19-17 over Philadelphia. Sullivan took the Jaguars. Breech took Houston. The CBS table landed on Jacksonville. The market is Jacksonville minus 2.5 in a soccer stadium that just watched Trevor Lawrence steal a morning. Woody Marks took 15 carries and four catches after David Montgomery left with a groin, which is why Marks sits on the Week 6 waiver mash. Start Lawrence if Superflex still has a hole. Stream Jacksonville's defense, which sits inside the top ten after a month that has not allowed more than 20 in three straight. Sit Houston's skill names unless Nico Collins is already in the lineup and you have no other receiver. The Texans just hung 26-3 on Tennessee, and a morning in London is a brutal place to ask a 1-4 club to do it twice.</p>

      <h2>Sunday at one: seven games, seven names</h2>
      <p><strong>Chicago at Atlanta. Pick: CHI.</strong> Five of six. Bender 26-20. Sullivan took the Bears. Prisco and Breech took the Falcons because Penix can still light up a secondary that just got shredded in Green Bay. Bijan Robinson already has 580 rushing yards, which is a league lead that used to belong to a different sentence, and Caleb Williams is on a groin that makes the line tenuous. I am taking Chicago with the mash because five cards did, and I am telling every room that drafted Robinson like a ceiling to start him anyway. Sit both defenses. Nick Folk is a stream only if the kicker board already ran out of Shrader and Aubrey.</p>
      <p><strong>Baltimore at Cleveland. Pick: BAL.</strong> Seven of seven. Bender 28-17. Every CBS card. The market is three. Lamar Jackson is a hamstring sentence again, and Tyler Huntley would get the start against a Browns line that just watched Deshaun Watson take eight sacks. Derrick Henry still has the chair. Quinshon Judkins wore a walking boot after the Jets. Start Henry. Stream Baltimore's defense, which sits fifth on the Week 6 DST mash after a night that allowed 17 offensive points in Atlanta. Sit Cleveland unless you already paid for a Browns name and the report upgrades him in the morning.</p>
      <p><strong>Tennessee at Indianapolis. Pick: IND.</strong> Six of six, seven on the number, the other blowout on the early window. Bender 30-19. The Titans have scored 11.6 a night. Cam Ward has thrown an interception in three straight. Spencer Shrader sits first on the kicker mash. Stream Indianapolis, which sits third on the DST mash at four percent rostered because rooms still remember the bad nights and have not priced a Cam Ward afternoon. Sit Tennessee. Jonathan Taylor is a start because the chair is the chair.</p>
      <p><strong>New York Jets at New England. Pick: NE.</strong> Six of six. Bender 24-14. Drake Maye just threw for 374 and four against Las Vegas, which is a sentence that used to belong to a cold list and now belongs to a buy if a room still has him as the six-interception chair. Geno Smith has taken at least three sacks in four straight. Start Maye. Stream New England's defense, which sits second on the mash. Sit the Jets unless Braelon Allen is the last running back a person has and hoping is the plan.</p>
      <p><strong>New Orleans at the Giants. Pick: NYG.</strong> Five of six. Bender 24-21. Breech took the Giants. The Saints are a minus-six turnover club with Tyler Shough on a hand. Jameis Winston has thrown three scores in each of the last two, which is why Boone put him fourth on the Week 6 waiver mash. Start Nabers. Start Winston in Superflex if you added him. Sit both defenses unless you streamed New York for the Shough matchup and already spent the FAAB. Kendre Miller is on the wire because Kamara's back is a sentence again.</p>
      <p><strong>Carolina at Philadelphia. Pick: CAR.</strong> Seven of seven, the loudest number on the early window besides Buffalo and Kansas City. Bender 22-20. Sullivan 23-21. Breech. The whole CBS table except Prisco. Jalen Hurts is a blood clot sentence. Saquon Barkley is a hamstring. Tank Bigsby is on IR. Will Shipley is a plantar fascia. Dameon Pierce took 11 carries in London and sits second on the waiver mash. Bryce Young is coming off a bye with a 90.3 passer rating. Start Young. Start Pierce if the claim cleared. Sit Philadelphia's defense, which has spent two weeks allowing 300 passing yards. Carolina laying three on the road in Lincoln Financial is a sentence this league has been waiting to write.</p>
      <p><strong>Pittsburgh at Tampa Bay. Pick: PIT.</strong> Four of six. Bender 26-16. Sullivan and Breech took the Buccaneers because the run defense is 72.6 a night and Baker Mayfield might get the thumb back. Jalon Daniels is still the name under center until the report says otherwise. Aaron Rodgers has 28 fantasy points in each of the last three. Start Rodgers in Superflex. Stream Pittsburgh, which sits first on the RotoBaller DST board and fourth on the mash. Germie Bernard ran 94 percent of the routes and caught 6 for 80, which is why Boone put him first on the wire. Sit Tampa Bay unless Bucky Irving is already in the lineup after 165.</p>

      <div class="photo-row">
        {_shot("patrick-mahomes", "png", "Patrick Mahomes")}
        {_shot("kenneth-walker", "jpg", "Kenneth Walker")}
        {_shot("josh-allen", "png", "Josh Allen")}
        {_shot("puka-nacua", "jpg", "Puka Nacua")}
      </div>
      <p class="photo-cap">Mahomes off a bye against a 0-5 club. Walker in the feature. Allen in Las Vegas. Nacua against a Cardinals defense that has allowed 37 a night.</p>

      <h2>Sunday late: Inglewood, Kansas City, and Las Vegas</h2>
      <p><strong>Arizona at the Rams. Pick: LAR.</strong> Six of six, 12.5 on the number, the widest spread on the card. Bender 34-24 and still gave Arizona a late cover. Matthew Stafford has Puka Nacua and Davante Adams. Jacoby Brissett has thrown four interceptions in two weeks. Start Stafford, Nacua, and Kyren Williams. Sit Arizona unless Trey McBride is already in the lineup, because McBride still gets the targets even when the building is loud. Harrison Mevis is a streamer on Boone's kicker list. The mash did not care about the cover. The mash took the Rams to win.</p>
      <p><strong>Los Angeles Chargers at Kansas City. Pick: KC.</strong> Seven of seven. Bender 25-19. The Chargers have 13 turnovers and a 0-5. Kenneth Walker already has the feature. Patrick Mahomes is 4-0 with two turnovers as a club. Start Mahomes and Walker and Travis Kelce. Stream Kansas City, which sits first on the Week 6 DST mash against a line that ranks 30th in pass-block win rate. Sit the Chargers. Justin Herbert is a sit unless Superflex already lost a chair and the wire is empty.</p>
      <p><strong>Buffalo at Las Vegas. Pick: BUF.</strong> Seven of seven. Bender 30-22. Josh Allen after 37-34 in overtime on Monday. Kirk Cousins has a 62.5 percent number in the last two losses. Start Allen and James Cook. Sit Las Vegas unless Brock Bowers is already in the lineup, because Bowers is still the years even when the week is a Bills afternoon. Keon Coleman is on the waiver mash after the Monday score.</p>

      <figure>
        <div class="photo-pair">
          {_shot("jordan-love", "png", "Jordan Love")}
          {_shot("brock-purdy", "jpg", "Brock Purdy")}
        </div>
        <figcaption>Love after 367 against Chicago, with Dallas visiting. Purdy 5-0, with Washington on Monday.</figcaption>
      </figure>

      <h2>Sunday night: Dallas at Green Bay. Pick: GB</h2>
      <p>Five of seven. Bender 28-20. Sullivan and Breech took Dallas. Jordan Love just threw for 367 in a 31-7. CeeDee Lamb played 56.7 percent of the snaps with a quad. Dak Prescott still has the chair. Start Love. Start Lamb if the report upgrades him, and sit him if it does not. Stream neither defense unless you already paid for Green Bay and you like a Cowboys run defense that allows 168 a night. Trey Smack sits inside the top ten on the kicker mash. The number is Green Bay minus 1.5 and the votes landed there after a week of watching Dallas lose to Jalon Daniels.</p>

      <h2>Monday: Washington at San Francisco. Pick: SF</h2>
      <p>Seven of seven. Bender 34-20. The 49ers are 5-0. Brock Purdy has eight throwing scores and zero interceptions in three home games. Christian McCaffrey is still the back. Jayden Daniels is back from the elbow and just tied the Giants 27-27. Start Purdy and McCaffrey. Stream San Francisco at home if you need a defense that just had five sacks, four takeaways, and a score in Seattle. Sit Washington unless you already paid Keep money for Daniels and you start the years. Eddy Pineiro sits inside the top five on the kicker mash because Washington has been a kicking gift.</p>

      <h2>What the rooms should do with the card</h2>
      <p>Copy the published picks in kickoff order if you came here for the list: SEA, JAX, CHI, BAL, IND, NE, NYG, CAR, PIT, LAR, KC, BUF, GB, SF. Thursday already missed. Sunday and Monday are still live. The mash is a vote, and the vote is 0-1 on the night. Cincinnati, Detroit, Miami, and Minnesota sit.</p>
      <p>The <a href="waiver.html">Week 6 waiver board</a> opens with the names rooms can still claim after five Sundays: Bernard, Pierce, Bourne, Strange, Marks. Barkley is a hamstring. Montgomery is a groin. Shipley is a plantar fascia. Pittman is on IR. Spend the leftover FAAB on the names Sunday actually moves.</p>
      <p>The <a href="week6-dst.html">Week 6 DST board</a> leans Kansas City, New England, and Indianapolis. Kansas City gets Herbert at 0-5. New England gets Geno Smith at home. Indianapolis gets Ward at 0-5. The <a href="week6-kickers.html">kicker board</a> has learned to say Spencer Shrader out loud and still loves Brandon Aubrey. The <a href="weekly.html">weekly skill boards</a> rebuilt this evening from FantasyPros ECR dated October 17, plus RotoWire, 4for4, and the rest of the kit. Robinson opens the backs. Nacua opens the receivers. Bowers sits first among the tight ends.</p>

      <div class="ramif">
        <h3>The fourteen, one more time</h3>
        <ul>
          <li>SEA over DEN. Thursday. Final: DEN 17-14.</li>
          <li>JAX over HOU. Sunday morning, in London.</li>
          <li>CHI over ATL. Sunday.</li>
          <li>BAL over CLE. Sunday.</li>
          <li>IND over TEN. Sunday.</li>
          <li>NE over NYJ. Sunday.</li>
          <li>NYG over NO. Sunday.</li>
          <li>CAR over PHI. Sunday.</li>
          <li>PIT over TB. Sunday.</li>
          <li>LAR over ARI. Sunday.</li>
          <li>KC over LAC. Sunday.</li>
          <li>BUF over LV. Sunday.</li>
          <li>GB over DAL. Sunday night.</li>
          <li>SF over WAS. Monday.</li>
        </ul>
      </div>

      <h2>A last look, because a card this long deserves one</h2>
      <p>I keep a private list of images from a week that already has one receipt and thirteen arguments. Lutz after the overtime kick. Smith-Njigba after 134 in a loss. Maye after 374, waiting on the Jets. Walker in a Chiefs feature against a 0-5 club. Young packing for a building that just lost its quarterback to a clot. Purdy still unbeaten, with Monday still on the calendar. Those pictures are why this page is crowded. The table at the top is the vote. The essay is the argument. Spend both, then spend the wire on Bernard and Pierce before the room remembers the names.</p>
      <p class="sources">Picks drawn from Bill Bender at Sporting News (full SU card), Tyler Sullivan at CBS Sports, John Breech at CBS Sports, the CBS Sports straight-up expert table, the published FanDuel and DraftKings numbers, a Week 5 winners board, and a short post-Week 5 power card. Thursday is in, Denver 17-14. Waiver names from Justin Boone, FantasyPros, NFL.com, and FFToday. Week 5 scores sit on <a href="week5-matchups.html">Week 5 Predictions</a>.</p>
    </article>
    """
