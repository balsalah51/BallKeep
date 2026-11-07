"""Week 8 slate from the official NFL schedule.

No invented picks or finals. Published mash boards are not on this rebuild.
"""
from __future__ import annotations

from special_teams import DST_TEAMS

TEAM_NAME = {abbr: name for name, abbr in DST_TEAMS}
NAME_TO_ABBR = {name: abbr for name, abbr in DST_TEAMS}

# Official Week 8 slate. Byes: HOU, NO, NYG, SF.
WEEK8_GAMES = [
    ("CAR", "GB", "Thu 10/29", "AMZ", "8:15p"),
    ("BAL", "BUF", "Sun 11/1", "CBS", "1:00p"),
    ("TEN", "CIN", "Sun 11/1", "CBS", "1:00p"),
    ("ARI", "DAL", "Sun 11/1", "FOX", "1:00p"),
    ("MIN", "DET", "Sun 11/1", "FOX", "1:00p"),
    ("IND", "JAX", "Sun 11/1", "CBS", "1:00p"),
    ("LV", "NYJ", "Sun 11/1", "FOX", "1:00p"),
    ("CLE", "PIT", "Sun 11/1", "CBS", "1:00p"),
    ("ATL", "TB", "Sun 11/1", "FOX", "1:00p"),
    ("LAC", "LAR", "Sun 11/1", "FOX", "4:05p"),
    ("KC", "DEN", "Sun 11/1", "CBS", "4:25p"),
    ("NE", "MIA", "Sun 11/1", "CBS", "4:25p"),
    ("PHI", "WAS", "Sun 11/1", "NBC", "8:20p"),
    ("CHI", "SEA", "Mon 11/2", "ESPN", "8:15p"),
]


def week8_matchups():
    rows = []
    for i, (away, home, day, tv, kick) in enumerate(WEEK8_GAMES, 1):
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
    from nfl_week import week_href
    href = week_href("matchups", 8)
    return f"""
    <a class="opening-teaser" href="{href}">
      <picture><source type="image/webp" srcset="img/players/drake-maye.webp" />
      <img src="img/players/drake-maye.jpg" alt="Drake Maye" width="160" height="160" loading="lazy" /></picture>
      <div>
        <p class="k">Week 8 · Thursday, Oct 29</p>
        <h2>Fourteen games. Philadelphia-Washington Sunday night. No invented picks.</h2>
        <p>The official slate is on the board. Thursday was Carolina at Green Bay. Houston, New Orleans, the Giants, and San Francisco are on bye.</p>
      </div>
    </a>
    """


W8_DST_FAQ = [
    ("Where is Week 8 DST?", "Published Week 8 defense boards are not on this rebuild. Season-long D lives on The D. The finished Week 7 stream sits next door."),
]
W8_K_FAQ = [
    ("Where is Week 8 Kickers?", "Published Week 8 kicker boards are not on this rebuild. Season-long K lives on Top Kickers. The finished Week 7 stream sits next door."),
]
W8_MATCH_FAQ = [
    ("How are these games listed?", "The official Week 8 NFL slate. Thursday was Carolina at Green Bay. Sunday night is Philadelphia at Washington. Monday is Chicago at Seattle."),
    ("Where are the mash picks?", "They land when the published cards are in. This rebuild does not invent a pick or a final."),
    ("Who is on bye?", "Houston, New Orleans, the Giants, and San Francisco."),
]
W8_DST_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 8 slate. No weekly DST mash on this rebuild."),
]
W8_K_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 8 slate. No weekly kicker mash on this rebuild."),
]
W8_MATCH_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 8 slate, Oct 29-Nov 2. No published pick mash on this rebuild."),
]
