"""Week 9 slate from the official NFL schedule.

No invented picks or finals. Published mash boards are not on this rebuild.
"""
from __future__ import annotations

from special_teams import DST_TEAMS

TEAM_NAME = {abbr: name for name, abbr in DST_TEAMS}
NAME_TO_ABBR = {name: abbr for name, abbr in DST_TEAMS}

# Official Week 9 slate. Byes: PIT, TEN.
WEEK9_GAMES = [
    ("JAX", "BAL", "Thu 11/5", "AMZ", "8:15p"),
    ("CIN", "ATL", "Sun 11/8", "NFLN", "9:30a"),
    ("DEN", "CAR", "Sun 11/8", "CBS", "1:00p"),
    ("DAL", "IND", "Sun 11/8", "FOX", "1:00p"),
    ("NYJ", "KC", "Sun 11/8", "CBS", "1:00p"),
    ("DET", "MIA", "Sun 11/8", "FOX", "1:00p"),
    ("CLE", "NO", "Sun 11/8", "CBS", "1:00p"),
    ("NYG", "PHI", "Sun 11/8", "FOX", "1:00p"),
    ("LAR", "WAS", "Sun 11/8", "FOX", "1:00p"),
    ("HOU", "LAC", "Sun 11/8", "CBS", "4:05p"),
    ("LV", "SF", "Sun 11/8", "CBS", "4:05p"),
    ("GB", "NE", "Sun 11/8", "FOX", "4:25p"),
    ("ARI", "SEA", "Sun 11/8", "FOX", "4:25p"),
    ("TB", "CHI", "Sun 11/8", "NBC", "8:20p"),
    ("BUF", "MIN", "Mon 11/9", "ESPN", "8:15p"),
]


def week9_matchups():
    rows = []
    for i, (away, home, day, tv, kick) in enumerate(WEEK9_GAMES, 1):
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
    href = week_href("matchups", 9)
    return f"""
    <a class="opening-teaser" href="{href}">
      <picture><source type="image/webp" srcset="img/players/drake-maye.webp" />
      <img src="img/players/drake-maye.jpg" alt="Drake Maye" width="160" height="160" loading="lazy" /></picture>
      <div>
        <p class="k">Week 9 · Thursday, Nov 5</p>
        <h2>Fifteen games. Cincinnati-Atlanta in Madrid. No invented picks.</h2>
        <p>The official slate is on the board. Thursday was Jacksonville at Baltimore. Pittsburgh and Tennessee are on bye.</p>
      </div>
    </a>
    """


W9_DST_FAQ = [
    ("Where is Week 9 DST?", "Published Week 9 defense boards are not on this rebuild. Season-long D lives on The D. The finished Week 8 stream sits next door."),
]
W9_K_FAQ = [
    ("Where is Week 9 Kickers?", "Published Week 9 kicker boards are not on this rebuild. Season-long K lives on Top Kickers. The finished Week 8 stream sits next door."),
]
W9_MATCH_FAQ = [
    ("How are these games listed?", "The official Week 9 NFL slate. Thursday was Jacksonville at Baltimore. Sunday features Cincinnati vs. Atlanta in Madrid. Monday is Buffalo at Minnesota."),
    ("Where are the mash picks?", "They land when the published cards are in. This rebuild does not invent a pick or a final."),
    ("Who is on bye?", "Pittsburgh and Tennessee."),
]
W9_DST_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 9 slate. No weekly DST mash on this rebuild."),
]
W9_K_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 9 slate. No weekly kicker mash on this rebuild."),
]
W9_MATCH_SOURCES = [
    ("NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Official Week 9 slate, Nov 5-9. No published pick mash on this rebuild."),
]
