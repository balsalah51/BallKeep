"""Week 7 slate from the official NFL schedule.

No invented picks or finals. Published mash boards are not on this rebuild.
"""
from __future__ import annotations

from special_teams import DST_TEAMS

TEAM_NAME = {abbr: name for name, abbr in DST_TEAMS}
NAME_TO_ABBR = {name: abbr for name, abbr in DST_TEAMS}

# Official Week 7 slate. Byes: BUF, JAX, LAC, WAS.
WEEK7_GAMES = [
    ("NE", "CHI", "Thu 10/22", "AMZ", "8:15p"),
    ("PIT", "NO", "Sun 10/25", "NFLN", "9:30a"),
    ("SF", "ATL", "Sun 10/25", "FOX", "1:00p"),
    ("CIN", "BAL", "Sun 10/25", "CBS", "1:00p"),
    ("TB", "CAR", "Sun 10/25", "FOX", "1:00p"),
    ("NYG", "HOU", "Sun 10/25", "FOX", "1:00p"),
    ("IND", "MIN", "Sun 10/25", "CBS", "1:00p"),
    ("MIA", "NYJ", "Sun 10/25", "CBS", "1:00p"),
    ("CLE", "TEN", "Sun 10/25", "CBS", "1:00p"),
    ("DEN", "ARI", "Sun 10/25", "CBS", "4:05p"),
    ("GB", "DET", "Sun 10/25", "FOX", "4:25p"),
    ("LAR", "LV", "Sun 10/25", "FOX", "4:25p"),
    ("KC", "SEA", "Sun 10/25", "NBC", "8:20p"),
    ("DAL", "PHI", "Mon 10/26", "ESPN", "8:15p"),
]


def week7_matchups():
    rows = []
    for i, (away, home, day, tv, kick) in enumerate(WEEK7_GAMES, 1):
        rows.append({
            "bk": i,
            "key": f"{away}@{home}",
            "away": away,
            "home": home,
            "day": day,
            "tv": tv,
            "time": kick,
            "slate": i - 1,
            "spread": "",
            "pick": "",
            "n": 0,
            "win_n": 0,
            "away_n": 0,
            "home_n": 0,
            "picks": {},
        })
    return rows


def predictions_teaser():
    return """
    <a class="opening-teaser" href="week7-matchups.html">
      <img src="img/players/drake-maye.jpg" alt="Drake Maye" width="160" height="160" />
      <div>
        <p class="k">Week 7 · Sunday, Oct 25</p>
        <h2>Fourteen games. Thursday already played. No invented picks.</h2>
        <p>The official slate is on the board. Mash picks land when the published cards are in. Buffalo, Jacksonville, the Chargers, and Washington are on bye.</p>
      </div>
    </a>
    """


W7_DST_FAQ = [
    ("Where is Week 7 DST?", "Published Week 7 defense boards are not on this rebuild. Season-long D lives on The D. The finished Week 6 stream sits next door."),
]
W7_K_FAQ = [
    ("Where is Week 7 Kickers?", "Published Week 7 kicker boards are not on this rebuild. Season-long K lives on Top Kickers. The finished Week 6 stream sits next door."),
]
W7_MATCH_FAQ = [
    ("How are these games listed?", "The official Week 7 NFL slate. Thursday was New England at Chicago. Sunday includes Paris. Monday is Dallas at Philadelphia."),
    ("Where are the mash picks?", "They land when the published cards are in. This rebuild does not invent a pick or a final."),
    ("Who is on bye?", "Buffalo, Jacksonville, the Chargers, and Washington."),
]
W7_DST_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 7 slate. No weekly DST mash on this rebuild."),
]
W7_K_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 7 slate. No weekly kicker mash on this rebuild."),
]
W7_MATCH_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 7 slate, Oct 22-26. No published pick mash on this rebuild."),
]
