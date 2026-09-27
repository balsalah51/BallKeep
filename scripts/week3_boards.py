"""Week 3 DST, kicker, and matchup aggregates.

Published boards only. Unranked / unpicked is a skip.
"""
from __future__ import annotations

from special_teams import DST_TEAMS, KICKERS, _mean_rows

TEAM_NAME = {abbr: name for name, abbr in DST_TEAMS}

K_BY_TEAM = {team: name for name, team in KICKERS}
K_BY_TEAM.update({
    "IND": "Spencer Shrader",
    "LV": "Matt Gay",
    "WAS": "Drew Stevens",
    "NYG": "Dominic Zvada",
    "CAR": "Ryan Fitzgerald",
    "MIA": "Riley Patterson",
    "NO": "Daniel Carlson",
    "CLE": "Andre Szmyt",
    "ATL": "Nick Folk",
    "CHI": "Cairo Santos",
    "NE": "Andy Borregales",
    "GB": "Trey Smack",
    "SF": "Eddy Pineiro",
    "BAL": "Tyler Loop",
})

WEEK3_KICKERS = list(KICKERS) + [
    (name, team) for team, name in K_BY_TEAM.items()
    if (name, team) not in KICKERS
]


# away, home, day, TV, kickoff ET. Official slate order.
WEEK3_GAMES = [
    ("ATL", "GB", "Thu 9/24", "Prime", "8:15p"),
    ("LAC", "BUF", "Sun 9/27", "FOX", "1:00p"),
    ("CAR", "CLE", "Sun 9/27", "FOX", "1:00p"),
    ("NYJ", "DET", "Sun 9/27", "FOX", "1:00p"),
    ("HOU", "IND", "Sun 9/27", "CBS", "1:00p"),
    ("NE", "JAX", "Sun 9/27", "CBS", "1:00p"),
    ("KC", "MIA", "Sun 9/27", "CBS", "1:00p"),
    ("TEN", "NYG", "Sun 9/27", "CBS", "1:00p"),
    ("CIN", "PIT", "Sun 9/27", "CBS", "1:00p"),
    ("SEA", "WAS", "Sun 9/27", "FOX", "1:00p"),
    ("ARI", "SF", "Sun 9/27", "FOX", "4:05p"),
    ("MIN", "TB", "Sun 9/27", "FOX", "4:05p"),
    ("BAL", "DAL", "Sun 9/27", "CBS", "4:25p"),
    ("LV", "NO", "Sun 9/27", "CBS", "4:25p"),
    ("LAR", "DEN", "Sun 9/27", "NBC", "8:20p"),
    ("PHI", "CHI", "Mon 9/28", "ESPN/ABC", "8:15p"),
]

SPREADS = {
    "ATL@GB": "GB -4.5",
    "LAC@BUF": "BUF -7",
    "CAR@CLE": "CAR -2.5",
    "NYJ@DET": "DET -6.5",
    "HOU@IND": "HOU -1.5",
    "NE@JAX": "JAX -3",
    "KC@MIA": "KC -10.5",
    "TEN@NYG": "NYG -2.5",
    "CIN@PIT": "CIN -3.5",
    "SEA@WAS": "SEA -7.5",
    "ARI@SF": "SF -8.5",
    "MIN@TB": "MIN -1.5",
    "BAL@DAL": "BAL -3.5",
    "LV@NO": "NO -3",
    "LAR@DEN": "LAR -2.5",
    "PHI@CHI": "PHI -4.5",
}

# RotoBaller Week 3 DST tiers, Joey Pollizze.
# https://www.rotoballer.com/week-3-defense-def-streamers-and-starts-2026-fantasy-tiers-rankings/1946745
RB_W3_DST = {
    "SEA": 1, "KC": 2, "SF": 3, "MIN": 4, "CAR": 5, "NYG": 6, "GB": 7,
    "PHI": 8, "HOU": 9, "CIN": 10, "LAR": 11, "NO": 12, "DET": 13,
    "NE": 14, "JAX": 15, "PIT": 16, "CLE": 17, "DEN": 18, "BUF": 19,
    "IND": 20, "TB": 21, "LV": 22, "TEN": 23, "WAS": 24, "ATL": 25,
    "BAL": 26, "NYJ": 27, "CHI": 28, "ARI": 29, "DAL": 30, "MIA": 31,
    "LAC": 32,
}

# NBC Sports Week 3 DST.
# https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-3-defense-dst-rankings-and-streamers
NBC_W3_DST = {
    "SEA": 1, "KC": 2, "MIN": 3, "SF": 4, "PHI": 5, "JAX": 6, "CAR": 7,
    "NE": 8, "LAR": 9, "HOU": 10, "CIN": 11, "NO": 12, "GB": 13, "PIT": 14,
    "LV": 15, "BUF": 16, "CLE": 17, "NYG": 18, "BAL": 19, "DEN": 20,
    "CHI": 21, "ATL": 22, "DET": 23, "TB": 24, "NYJ": 25, "TEN": 26,
    "LAC": 27, "DAL": 28, "IND": 29, "ARI": 30, "WAS": 31, "MIA": 32,
}

# FantasyPros Let's Stream Defenses, Jacob Herlin, Sep 22.
# https://www.fantasypros.com/2026/09/lets-stream-defenses-week-3-2026-fantasy-football/
FP_W3_DST = {
    "SEA": 1, "CAR": 2, "GB": 3, "CIN": 4, "KC": 5, "DET": 6, "JAX": 7,
    "TEN": 8, "LV": 9, "NYG": 10, "PHI": 11, "HOU": 12, "MIN": 13, "PIT": 14,
    "CLE": 15, "SF": 16, "NO": 17, "BUF": 18, "DEN": 19, "IND": 20, "TB": 21,
    "NE": 22, "BAL": 23, "CHI": 24, "WAS": 25, "LAR": 26, "ARI": 27, "NYJ": 28,
    "DAL": 29, "LAC": 30, "ATL": 31, "MIA": 32,
}

# RotoBaller streamer column, Andy Smith, full 1-32.
# https://www.rotoballer.com/week-3-defense-streamers-best-fantasy-d-st-pickups-starts-2026/1949795
RS_W3_DST = {
    "SEA": 1, "KC": 2, "HOU": 3, "GB": 4, "PHI": 5, "SF": 6, "MIN": 7,
    "CAR": 8, "CIN": 9, "BUF": 10, "LAR": 11, "NE": 12, "TB": 13, "TEN": 14,
    "BAL": 15, "DEN": 16, "NO": 17, "NYG": 18, "DET": 19, "LV": 20, "JAX": 21,
    "IND": 22, "PIT": 23, "CLE": 24, "CHI": 25, "ATL": 26, "DAL": 27, "LAC": 28,
    "WAS": 29, "MIA": 30, "ARI": 31, "NYJ": 32,
}

# Softer implied totals first. From the RotoBaller PA column.
VEGAS_DST = {
    "SEA": 1, "KC": 2, "NYG": 3, "CAR": 4, "GB": 5, "CIN": 6, "SF": 7,
    "PHI": 8, "DET": 9, "MIN": 10, "NO": 11, "HOU": 12, "LAR": 13, "JAX": 14,
    "CLE": 15, "BUF": 16, "PIT": 17, "TB": 18, "NE": 19, "DEN": 20, "IND": 21,
    "LV": 22, "WAS": 23, "CHI": 24, "TEN": 25, "BAL": 26, "ATL": 27, "NYJ": 28,
    "DAL": 29, "ARI": 30, "MIA": 31, "LAC": 32,
}

# Week 2 form: clubs that already scored on defense or won big.
FORM_DST = {
    "CAR": 1, "SEA": 2, "SF": 3, "NE": 4, "CIN": 5, "LAR": 6, "LV": 7,
    "PHI": 8, "BUF": 9, "KC": 10, "DEN": 11, "MIN": 12,
}

# RotoBaller Week 3 kickers.
# https://www.rotoballer.com/week-3-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1946875
RB_W3_K = {
    "Brandon Aubrey": 1, "Tyler Loop": 2, "Eddy Pineiro": 3,
    "Ka'imi Fairbairn": 4, "Harrison Butker": 5, "Jason Myers": 6,
    "Evan McPherson": 7, "Cam Little": 8, "Trey Smack": 9, "Tyler Bass": 10,
    "Jake Bates": 11, "Spencer Shrader": 12, "Jason Sanders": 13,
    "Ryan Fitzgerald": 14, "Will Reichard": 15, "Jake Elliott": 16,
    "Cameron Dicker": 17, "Harrison Mevis": 18, "Daniel Carlson": 19,
    "Andy Borregales": 20, "Matt Gay": 21, "Chase McLaughlin": 22,
    "Chris Boswell": 23, "Wil Lutz": 24, "Cairo Santos": 25,
}

# SI Week 3 kicker board.
# https://www.si.com/fantasy/week-3-kicker-rankings
SI_W3_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Cam Little": 3,
    "Jason Myers": 4, "Jake Bates": 5, "Tyler Loop": 6,
    "Chase McLaughlin": 7, "Evan McPherson": 8, "Trey Smack": 9,
    "Will Reichard": 10, "Eddy Pineiro": 11, "Harrison Mevis": 12,
    "Spencer Shrader": 13, "Tyler Bass": 14, "Ryan Fitzgerald": 15,
    "Cameron Dicker": 16, "Harrison Butker": 17, "Cairo Santos": 18,
    "Chris Boswell": 19, "Wil Lutz": 20, "Andy Borregales": 21,
    "Jake Elliott": 22, "Daniel Carlson": 23, "Nick Folk": 24,
}

# Sporting News Week 3 kicker board (2026 slate).
# https://www.sportingnews.com/us/fantasy/news/fantasy-football-k-rankings-week-3-who-start-best-sleepers-top-busts/f484d5d7d6082831d6eb7c7b
SN_W3_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Evan McPherson": 3,
    "Jason Myers": 4, "Cam Little": 5, "Harrison Butker": 6,
    "Chase McLaughlin": 7, "Jake Bates": 8, "Tyler Loop": 9,
    "Trey Smack": 10, "Eddy Pineiro": 11, "Harrison Mevis": 12,
    "Tyler Bass": 13, "Spencer Shrader": 14, "Will Reichard": 15,
    "Cameron Dicker": 16, "Wil Lutz": 17, "Chris Boswell": 18,
    "Jake Elliott": 19, "Cairo Santos": 20, "Ryan Fitzgerald": 21,
    "Matt Gay": 22, "Andy Borregales": 23,
}

# FantasyPros Week 3 kicker ECR, Sep 27, 37 experts.
# https://www.fantasypros.com/nfl/rankings/k.php
FP_ECR_K = {
    "Brandon Aubrey": 1, "Eddy Pineiro": 2, "Harrison Butker": 3,
    "Tyler Loop": 4, "Ka'imi Fairbairn": 5, "Jason Myers": 6,
    "Evan McPherson": 7, "Trey Smack": 8, "Cam Little": 9,
    "Tyler Bass": 10, "Jake Bates": 11, "Harrison Mevis": 12,
    "Cameron Dicker": 13, "Daniel Carlson": 14, "Will Reichard": 15,
    "Chase McLaughlin": 16, "Jake Elliott": 17, "Chris Boswell": 18,
    "Ryan Fitzgerald": 19, "Andy Borregales": 20, "Jason Sanders": 21,
    "Spencer Shrader": 22, "Wil Lutz": 23, "Matt Gay": 24,
}


def week3_dst_maps() -> dict:
    return {
        "RotoBaller": RB_W3_DST,
        "NBC Sports": NBC_W3_DST,
        "FantasyPros stream": FP_W3_DST,
        "RotoBaller streamers": RS_W3_DST,
        "Vegas implied": VEGAS_DST,
        "Week 2 form": FORM_DST,
    }


def week3_k_maps() -> dict:
    return {
        "RotoBaller": RB_W3_K,
        "Sports Illustrated": SI_W3_K,
        "Sporting News": SN_W3_K,
        "FantasyPros ECR": FP_ECR_K,
    }


W3_DST_LONG = ("RotoBaller", "NBC Sports")
W3_K_LONG = ("FantasyPros ECR", "RotoBaller")


def week3_dst_board():
    from bk_curve import bk_value
    rows = [r for r in _mean_rows(DST_TEAMS, week3_dst_maps(), "DST", long_core=W3_DST_LONG) if r["n"] >= 3]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week3_kicker_board():
    return _mean_rows(WEEK3_KICKERS, week3_k_maps(), "K", long_core=W3_K_LONG)


def _fav(spread_map):
    """Spread string like BUF -7 -> BUF."""
    out = {}
    for key, text in spread_map.items():
        club = (text or "").split()[0]
        if club:
            out[key] = club
    return out


# Published straight-up cards. Unpicked games stay off that board.
SN_W3 = {  # Bill Bender, Sporting News, Sep 24
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR", "NYJ@DET": "DET",
    "HOU@IND": "HOU", "NE@JAX": "NE", "KC@MIA": "KC", "TEN@NYG": "NYG",
    "CIN@PIT": "CIN", "SEA@WAS": "SEA", "ARI@SF": "SF", "MIN@TB": "MIN",
    "BAL@DAL": "BAL", "LV@NO": "NO", "LAR@DEN": "DEN", "PHI@CHI": "PHI",
}
CBS_W3 = {  # Tyler Sullivan, CBS Sports, Sep 23
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR", "NYJ@DET": "DET",
    "HOU@IND": "IND", "NE@JAX": "JAX", "KC@MIA": "KC", "TEN@NYG": "TEN",
    "CIN@PIT": "CIN", "SEA@WAS": "SEA", "ARI@SF": "SF", "MIN@TB": "MIN",
    "BAL@DAL": "BAL", "LV@NO": "NO", "LAR@DEN": "LAR", "PHI@CHI": "PHI",
}
NFL_W3 = {  # NFL.com five-editor majority, Sep 24
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR", "NYJ@DET": "DET",
    "HOU@IND": "HOU", "NE@JAX": "JAX", "KC@MIA": "KC", "TEN@NYG": "NYG",
    "CIN@PIT": "CIN", "SEA@WAS": "SEA", "ARI@SF": "SF", "MIN@TB": "MIN",
    "BAL@DAL": "BAL", "LV@NO": "NO", "LAR@DEN": "LAR", "PHI@CHI": "PHI",
}
LINE_W3 = {  # SportsLine model scores published Sep 24
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR", "NYJ@DET": "DET",
    "HOU@IND": "HOU", "KC@MIA": "KC", "TEN@NYG": "NYG", "CIN@PIT": "CIN",
    "BAL@DAL": "BAL",
}
VEGAS_SU = _fav(SPREADS)
W2_WINNERS = {
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR",
    "NE@JAX": "NE", "KC@MIA": "KC", "CIN@PIT": "CIN", "SEA@WAS": "SEA",
    "ARI@SF": "SF", "MIN@TB": "MIN", "BAL@DAL": "DAL", "PHI@CHI": "PHI",
}
POWER_W3 = {
    "ATL@GB": "GB", "LAC@BUF": "BUF", "CAR@CLE": "CAR", "NYJ@DET": "DET",
    "HOU@IND": "HOU", "NE@JAX": "NE", "KC@MIA": "KC", "TEN@NYG": "NYG",
    "CIN@PIT": "CIN", "SEA@WAS": "SEA", "ARI@SF": "SF", "MIN@TB": "MIN",
    "BAL@DAL": "BAL", "LV@NO": "LV", "LAR@DEN": "LAR", "PHI@CHI": "PHI",
}


def match_maps() -> dict:
    return {
        "Sporting News": SN_W3,
        "CBS Sports": CBS_W3,
        "NFL.com": NFL_W3,
        "SportsLine model": LINE_W3,
        "Vegas favorite": VEGAS_SU,
        "Week 2 winners": W2_WINNERS,
        "Post-Week 2 power": POWER_W3,
    }


W3_DST_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-3-defense-def-streamers-and-starts-2026-fantasy-tiers-rankings/1946745", "Joey Pollizze tiers. Seahawks first at Washington."),
    ("NBC Sports", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-3-defense-dst-rankings-and-streamers", "Seahawks first. Chiefs second at Miami."),
    ("FantasyPros stream", "https://www.fantasypros.com/2026/09/lets-stream-defenses-week-3-2026-fantasy-football/", "Jacob Herlin. Seahawks, Panthers, Packers."),
    ("RotoBaller streamers", "https://www.rotoballer.com/week-3-defense-streamers-best-fantasy-d-st-pickups-starts-2026/1949795", "Andy Smith 1-32. Seahawks, Chiefs, Texans."),
    ("Vegas implied", "", "Softer implied totals get the higher stream rank."),
    ("Week 2 form", "", "Clubs that already scored on defense or won big."),
]

W3_K_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-3-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1946875", "Aubrey first. Loop and Pineiro next."),
    ("Sports Illustrated", "https://www.si.com/fantasy/week-3-kicker-rankings", "Aubrey first. Fairbairn and Little next."),
    ("Sporting News", "https://www.sportingnews.com/us/fantasy/news/fantasy-football-k-rankings-week-3-who-start-best-sleepers-top-busts/f484d5d7d6082831d6eb7c7b", "Aubrey, Fairbairn, McPherson."),
    ("FantasyPros ECR", "https://www.fantasypros.com/nfl/rankings/k.php", "Week 3 kicker consensus, 37 experts, Sep 27."),
]

MATCH_SOURCES = [
    ("Sporting News", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-3-saints-raiders-vikings/6884e7fdaa4ee34cea4b3928", "Bill Bender's full SU card. Bills, Panthers, Broncos."),
    ("CBS Sports", "https://www.cbssports.com/nfl/news/2026-nfl-week-3-picks-odds-predictions/", "Tyler Sullivan. Bills 31-20. Colts and Titans fades."),
    ("NFL.com", "https://www.nfl.com/news/nfl-picks-week-3-2026-nfl-season", "Five-editor majority. Bills, Lions, Chiefs, Seahawks."),
    ("SportsLine model", "https://www.fantasynerds.com/news/story/2026/09/24/sportsline-model-projects-week-3-nfl-game-outcomes-1632390", "10,000 sims. Bills 31-21. Lions 36-23."),
    ("Vegas favorite", "", "Current published spread favorite."),
    ("Week 2 winners", "", "The club that already won, when only one side did."),
    ("Post-Week 2 power", "", "Short 1-32 after the second Sunday. Higher club wins."),
]


# Thursday is in. Sunday and Monday stay open.
WEEK3_FINALS = {
    "ATL@GB": {"score": "35-14", "winner": "ATL", "day": "Thu Final"},
}


def week3_matchups():
    maps = match_maps()
    rows = []
    for slate, (away, home, day, tv, kick) in enumerate(WEEK3_GAMES):
        key = f"{away}@{home}"
        picks = {}
        for label, mp in maps.items():
            pick = mp.get(key)
            if pick:
                picks[label] = pick
        if not picks:
            continue
        counts = {}
        for pick in picks.values():
            counts[pick] = counts.get(pick, 0) + 1
        winner = max(counts.items(), key=lambda kv: (kv[1], kv[0] != away))[0]
        rows.append({
            "key": key,
            "away": away,
            "home": home,
            "day": day,
            "tv": tv,
            "time": kick,
            "slate": slate,
            "spread": SPREADS.get(key, ""),
            "pick": winner,
            "n": len(picks),
            "win_n": counts[winner],
            "away_n": counts.get(away, 0),
            "home_n": counts.get(home, 0),
            "picks": picks,
        })
        fin = WEEK3_FINALS.get(key)
        if fin:
            rows[-1]["final"] = fin["score"]
            rows[-1]["final_winner"] = fin["winner"]
            rows[-1]["day"] = fin["day"]
    rows.sort(key=lambda r: int(r.get("slate") or 0))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


W3_DST_FAQ = [
    ("How is Week 3 DST built?", "Super Aggregate of published Week 3 defense boards. 50% RotoBaller and NBC Sports, 50% FantasyPros, the RotoBaller streamer column, implied totals, and Week 2 form."),
    ("Is this Top Defenses?", "No. Top Defenses is rest of season. This board is only Week 3."),
]
W3_K_FAQ = [
    ("How is Week 3 Kickers built?", "Super Aggregate of RotoBaller, Sports Illustrated, Sporting News, and FantasyPros ECR."),
    ("Who leads?", "Aubrey sits first. Fairbairn and Myers follow."),
]
W3_MATCH_FAQ = [
    ("How are the win picks built?", "Published Week 3 cards: Sporting News, CBS Sports, NFL.com, the SportsLine model, the market favorite, Week 2 winners, and a short post-Week 2 power board. Unpicked games on a board are skipped."),
    ("Is this a win chance?", "Away and Home are raw vote counts. The pick is the side with more published votes."),
    ("Is this a bet slip?", "It is a mash of public picks and the market. Thursday already has a final. Sunday and Monday stay open."),
]
