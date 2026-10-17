"""Week 6 DST, kicker, and matchup aggregates.

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
    "TEN": "Joey Slye",
    "ARI": "Chad Ryland",
    "LAR": "Harrison Mevis",
})

WEEK6_KICKERS = list(KICKERS) + [
    (name, team) for team, name in K_BY_TEAM.items()
    if (name, team) not in KICKERS
]


# away, home, day, TV, kickoff ET. Official slate order.
WEEK6_GAMES = [
    ("SEA", "DEN", "Thu 10/15", "Prime", "8:15p"),
    ("HOU", "JAX", "Sun 10/18", "NFLN", "9:30a"),
    ("CHI", "ATL", "Sun 10/18", "FOX", "1:00p"),
    ("BAL", "CLE", "Sun 10/18", "FOX", "1:00p"),
    ("TEN", "IND", "Sun 10/18", "FOX", "1:00p"),
    ("NYJ", "NE", "Sun 10/18", "CBS", "1:00p"),
    ("NO", "NYG", "Sun 10/18", "FOX", "1:00p"),
    ("CAR", "PHI", "Sun 10/18", "CBS", "1:00p"),
    ("PIT", "TB", "Sun 10/18", "CBS", "1:00p"),
    ("ARI", "LAR", "Sun 10/18", "FOX", "4:05p"),
    ("LAC", "KC", "Sun 10/18", "CBS", "4:25p"),
    ("BUF", "LV", "Sun 10/18", "CBS", "4:25p"),
    ("DAL", "GB", "Sun 10/18", "NBC", "8:20p"),
    ("WAS", "SF", "Mon 10/19", "ESPN", "8:15p"),
]

SPREADS = {
    "SEA@DEN": "SEA -2.5",
    "HOU@JAX": "JAX -2.5",
    "CHI@ATL": "CHI -1.5",
    "BAL@CLE": "BAL -3",
    "TEN@IND": "IND -7",
    "NYJ@NE": "NE -7.5",
    "NO@NYG": "NO -1.5",
    "CAR@PHI": "CAR -3",
    "PIT@TB": "PIT -2.5",
    "ARI@LAR": "LAR -12.5",
    "LAC@KC": "KC -7.5",
    "BUF@LV": "BUF -5.5",
    "DAL@GB": "GB -1.5",
    "WAS@SF": "SF -7.5",
}

# RotoBaller Week 6 DST tiers, Joey Pollizze.
# https://www.rotoballer.com/week-6-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1964600
RB_W6_DST = {
    "PIT": 1, "SEA": 2, "KC": 3, "NE": 4, "IND": 5, "LAR": 6, "BAL": 7,
    "JAX": 8, "HOU": 9, "SF": 10, "PHI": 11, "DEN": 12, "CLE": 13,
    "TB": 14, "CHI": 15, "NO": 16, "CAR": 17, "BUF": 18, "NYG": 19,
    "DAL": 20, "NYJ": 21, "LAC": 22, "ATL": 23, "TEN": 24, "GB": 25,
    "WAS": 26, "LV": 27, "ARI": 28,
}

# FantasyPros Week 6 D/ST, Oct 15.
# https://www.fantasypros.com/2026/10/fantasy-football-rankings-start-sit-advice-d-st-week-6-2026/
FP_W6_DST = {
    "BAL": 1, "NE": 2, "KC": 3, "IND": 4, "PIT": 5, "NO": 6, "JAX": 7,
    "DEN": 8, "NYG": 9, "LAR": 10, "PHI": 11, "NYJ": 12, "HOU": 13,
    "SF": 14, "CAR": 15, "SEA": 16, "TEN": 17, "CLE": 18, "TB": 19,
    "BUF": 20, "ATL": 21, "GB": 22, "LAC": 23, "CHI": 24, "LV": 25,
    "DAL": 26, "WAS": 27, "ARI": 28,
}

# NBC Sports Week 6 DST, published ranks that named a side.
# https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-6-defense-dst-rankings-and-streamers
NBC_W6_DST = {
    "KC": 1, "SEA": 2, "JAX": 5, "PIT": 6, "BAL": 7,
}

# Justin Boone D/ST streamers, Yahoo Sports, Oct 12.
# https://sports.yahoo.com/fantasy/article/fantasy-football-waiver-wire-justin-boones-top-defenses-to-stream-for-week-6-181723479.html
BOONE_W6_DST = {
    "KC": 1, "IND": 2, "SF": 3, "NO": 4, "NYG": 5, "NE": 6, "BAL": 7,
}

# Softer implied totals first. From the RotoBaller PA column.
VEGAS_DST = {
    "KC": 1, "NE": 2, "PIT": 3, "IND": 4, "BAL": 5, "SEA": 6, "LAR": 7,
    "JAX": 8, "PHI": 9, "CAR": 10, "SF": 11, "TB": 12, "DEN": 13, "NO": 14,
    "HOU": 15, "CHI": 16, "CLE": 17, "BUF": 18, "NYG": 19, "NYJ": 20,
    "LAC": 21, "TEN": 22, "GB": 23, "ATL": 24, "DAL": 25, "WAS": 26,
    "LV": 27, "ARI": 28,
}

# Week 5 form: clubs that already won big or scored on defense.
FORM_DST = {
    "HOU": 1, "NE": 2, "GB": 3, "DET": 4, "PIT": 5, "TB": 6, "MIN": 7,
    "DEN": 8, "CIN": 9, "NYJ": 10, "SF": 11, "BAL": 12, "BUF": 13, "JAX": 14,
}

# RotoBaller Week 6 kickers, Nick Mariano.
# https://www.rotoballer.com/week-6-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1964514
RB_W6_K = {
    "Spencer Shrader": 1, "Brandon Aubrey": 2, "Ka'imi Fairbairn": 3,
    "Tyler Loop": 4, "Cam Little": 5, "Jason Myers": 6, "Eddy Pineiro": 7,
    "Harrison Butker": 8, "Trey Smack": 9, "Tyler Bass": 10, "Matt Gay": 11,
    "Harrison Mevis": 12, "Cairo Santos": 13, "Chris Boswell": 14,
    "Ryan Fitzgerald": 15, "Daniel Carlson": 16, "Drew Stevens": 17,
    "Dominic Zvada": 18, "Nick Folk": 19, "Andy Borregales": 20,
    "Jake Elliott": 21, "Chad Ryland": 22, "Wil Lutz": 23,
    "Chase McLaughlin": 24, "Andre Szmyt": 25, "Joey Slye": 26,
    "Cameron Dicker": 27, "Jason Sanders": 28,
}

# FantasyPros Week 6 kicker ECR, Oct 17, 29 names.
# https://www.fantasypros.com/nfl/rankings/k.php?week=6
FP_ECR_K = {
    "Spencer Shrader": 1, "Brandon Aubrey": 2, "Eddy Pineiro": 3,
    "Cam Little": 4, "Tyler Loop": 5, "Harrison Butker": 6,
    "Ka'imi Fairbairn": 7, "Tyler Bass": 8, "Cairo Santos": 9,
    "Jason Myers": 10, "Chris Boswell": 11, "Matt Gay": 12,
    "Dominic Zvada": 13, "Trey Smack": 14, "Andy Borregales": 15,
    "Blake Grupe": 16, "Nick Folk": 17, "Ryan Fitzgerald": 18,
    "Daniel Carlson": 19, "Chase McLaughlin": 20, "Drew Stevens": 21,
    "Chad Ryland": 22, "Jake Elliott": 23, "Wil Lutz": 24,
    "Andre Szmyt": 25, "Cameron Dicker": 26, "Jason Sanders": 27,
    "Joey Slye": 28, "Harrison Mevis": 29,
}

# PFN Week 6 kicker consensus, Katz and Soppe.
# https://www.profootballnetwork.com/fantasy-hq/weekly-kicker-rankings
PFN_W6_K = {
    "Brandon Aubrey": 1, "Cam Little": 2, "Tyler Loop": 3, "Tyler Bass": 4,
    "Jason Myers": 5, "Harrison Butker": 6, "Ka'imi Fairbairn": 7,
    "Trey Smack": 8,
}

# Justin Boone kicker streamers, Yahoo Sports, Oct 12.
# https://sports.yahoo.com/fantasy/article/fantasy-football-waiver-wire-justin-boones-top-kickers-to-stream-for-week-6-182119733.html
BOONE_W6_K = {
    "Harrison Mevis": 1, "Eddy Pineiro": 2, "Dominic Zvada": 3,
    "Chris Boswell": 4, "Harrison Butker": 5, "Blake Grupe": 6,
}


def week6_dst_maps() -> dict:
    return {
        "RotoBaller": RB_W6_DST,
        "FantasyPros weekly": FP_W6_DST,
        "NBC Sports": NBC_W6_DST,
        "Yahoo Boone": BOONE_W6_DST,
        "Vegas implied": VEGAS_DST,
        "Week 5 form": FORM_DST,
    }


def week6_k_maps() -> dict:
    return {
        "RotoBaller": RB_W6_K,
        "FantasyPros ECR": FP_ECR_K,
        "Pro Football Network": PFN_W6_K,
        "Yahoo Boone": BOONE_W6_K,
    }


W6_DST_LONG = ("RotoBaller", "FantasyPros weekly")
W6_K_LONG = ("FantasyPros ECR", "RotoBaller")


def week6_dst_board():
    from bk_curve import bk_value
    rows = [r for r in _mean_rows(DST_TEAMS, week6_dst_maps(), "DST", long_core=W6_DST_LONG) if r["n"] >= 3]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week6_kicker_board():
    return _mean_rows(WEEK6_KICKERS, week6_k_maps(), "K", long_core=W6_K_LONG)


def _fav(spread_map):
    """Spread string like BUF -7 -> BUF."""
    out = {}
    for key, text in spread_map.items():
        club = (text or "").split()[0]
        if club:
            out[key] = club
    return out


# Published straight-up cards. Unpicked games stay off that board.
SN_W6 = {  # Bill Bender, Sporting News
    "SEA@DEN": "SEA", "HOU@JAX": "HOU", "CHI@ATL": "CHI", "BAL@CLE": "BAL",
    "TEN@IND": "IND", "NYJ@NE": "NE", "NO@NYG": "NYG", "CAR@PHI": "CAR",
    "PIT@TB": "PIT", "ARI@LAR": "LAR", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "GB", "WAS@SF": "SF",
}
CBS_W6 = {  # Tyler Sullivan, CBS Sports expert table
    "SEA@DEN": "SEA", "HOU@JAX": "JAX", "CHI@ATL": "CHI", "BAL@CLE": "BAL",
    "TEN@IND": "IND", "NYJ@NE": "NE", "NO@NYG": "NYG", "CAR@PHI": "CAR",
    "PIT@TB": "TB", "ARI@LAR": "LAR", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "DAL", "WAS@SF": "SF",
}
BREECH_W6 = {  # John Breech, CBS Sports expert table
    "SEA@DEN": "SEA", "HOU@JAX": "HOU", "CHI@ATL": "ATL", "BAL@CLE": "BAL",
    "TEN@IND": "IND", "NYJ@NE": "NE", "NO@NYG": "NYG", "CAR@PHI": "CAR",
    "PIT@TB": "TB", "ARI@LAR": "LAR", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "DAL", "WAS@SF": "SF",
}
CBS_TABLE = {  # Majority of the CBS Sports straight-up expert table
    "SEA@DEN": "SEA", "HOU@JAX": "JAX", "CHI@ATL": "CHI", "BAL@CLE": "BAL",
    "TEN@IND": "IND", "NYJ@NE": "NE", "NO@NYG": "NYG", "CAR@PHI": "CAR",
    "PIT@TB": "PIT", "ARI@LAR": "LAR", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "GB", "WAS@SF": "SF",
}
VEGAS_SU = _fav(SPREADS)
W5_WINNERS = {
    "SEA@DEN": "DEN", "BAL@CLE": "BAL", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "GB", "WAS@SF": "SF", "CAR@PHI": "CAR",
}
POWER_W6 = {
    "SEA@DEN": "DEN", "HOU@JAX": "JAX", "CHI@ATL": "CHI", "BAL@CLE": "BAL",
    "TEN@IND": "IND", "NYJ@NE": "NE", "NO@NYG": "NYG", "CAR@PHI": "CAR",
    "PIT@TB": "PIT", "ARI@LAR": "LAR", "LAC@KC": "KC", "BUF@LV": "BUF",
    "DAL@GB": "GB", "WAS@SF": "SF",
}


def match_maps() -> dict:
    return {
        "Sporting News": SN_W6,
        "CBS Sports": CBS_W6,
        "CBS Breech": BREECH_W6,
        "CBS experts": CBS_TABLE,
        "Vegas favorite": VEGAS_SU,
        "Week 5 winners": W5_WINNERS,
        "Post-Week 5 power": POWER_W6,
    }


W6_DST_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-6-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1964600", "Joey Pollizze tiers. Steelers first at Tampa Bay."),
    ("FantasyPros weekly", "https://www.fantasypros.com/2026/10/fantasy-football-rankings-start-sit-advice-d-st-week-6-2026/", "Pat Fitzmaurice. Ravens, Patriots, Chiefs."),
    ("NBC Sports", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-6-defense-dst-rankings-and-streamers", "Kansas City first against the Chargers."),
    ("Yahoo Boone", "https://sports.yahoo.com/fantasy/article/fantasy-football-waiver-wire-justin-boones-top-defenses-to-stream-for-week-6-181723479.html", "Boone streamers. Chiefs, Colts, 49ers."),
    ("Vegas implied", "", "Softer implied totals get the higher stream rank."),
    ("Week 5 form", "", "Clubs that already won big or scored on defense."),
]

W6_K_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-6-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1964514", "Shrader first. Aubrey and Fairbairn next."),
    ("FantasyPros ECR", "https://www.fantasypros.com/nfl/rankings/k.php?week=6", "Week 6 kicker consensus, Oct 17."),
    ("Pro Football Network", "https://www.profootballnetwork.com/fantasy-hq/weekly-kicker-rankings", "Katz and Soppe. Aubrey, Little, Loop."),
    ("Yahoo Boone", "https://sports.yahoo.com/fantasy/article/fantasy-football-waiver-wire-justin-boones-top-kickers-to-stream-for-week-6-182119733.html", "Mevis, Pineiro, Zvada among the streamers."),
]

MATCH_SOURCES = [
    ("Sporting News", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-6/96ca7b5b371e7b64cd933e96", "Bill Bender's full SU card. Seahawks on Thursday. Panthers in Philadelphia."),
    ("CBS Sports", "https://www.cbssports.com/nfl/news/pick-six-seahawks-broncos-predictions-nfl-week-6-picks/", "Tyler Sullivan. Panthers 23-21. Packers on Sunday night."),
    ("CBS Breech", "https://www.cbssports.com/nfl/picks/experts/straight-up/6/", "John Breech. Texans in London. Buccaneers at home."),
    ("CBS experts", "https://www.cbssports.com/nfl/picks/experts/straight-up/6/", "Majority of the CBS Sports straight-up table."),
    ("Vegas favorite", "", "Current published spread favorite."),
    ("Week 5 winners", "", "The club that already won, when only one side did."),
    ("Post-Week 5 power", "", "Short 1-32 after the fifth Sunday. Higher club wins."),
]


# Thursday is in. Sunday and Monday stay open.
WEEK6_FINALS = {
    "SEA@DEN": {"score": "17-14", "winner": "DEN", "day": "Thu Final"},
}


def week6_matchups():
    maps = match_maps()
    rows = []
    for slate, (away, home, day, tv, kick) in enumerate(WEEK6_GAMES):
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
        fin = WEEK6_FINALS.get(key)
        if fin:
            rows[-1]["final"] = fin["score"]
            rows[-1]["final_winner"] = fin["winner"]
            rows[-1]["day"] = fin["day"]
    rows.sort(key=lambda r: int(r.get("slate") or 0))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


W6_DST_FAQ = [
    ("How is Week 6 DST built?", "Super Aggregate of published Week 6 defense boards. 50% RotoBaller and FantasyPros, 50% NBC Sports, Yahoo Boone, implied totals, and Week 5 form."),
    ("Is this Top Defenses?", "Top Defenses is rest of season. This board is only Week 6."),
]
W6_K_FAQ = [
    ("How is Week 6 Kickers built?", "Super Aggregate of FantasyPros ECR, RotoBaller, Pro Football Network, and Yahoo Boone."),
    ("Who leads?", "Shrader and Aubrey sit first. Loop and Little follow."),
]
W6_MATCH_FAQ = [
    ("How are the win picks built?", "Published Week 6 cards: Sporting News, two CBS Sports cards, the CBS Sports expert table, the market favorite, Week 5 winners, and a short post-Week 5 power board. Unpicked games on a board are skipped."),
    ("Is this a win chance?", "Away and Home are raw vote counts. The pick is the side with more published votes."),
    ("Is this a bet slip?", "It is a mash of public picks and the market. Thursday already has a final. Sunday and Monday stay open. Cincinnati, Detroit, Miami, and Minnesota are on bye."),
]
