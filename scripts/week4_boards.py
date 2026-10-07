"""Week 4 DST, kicker, and matchup aggregates.

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
})

WEEK4_KICKERS = list(KICKERS) + [
    (name, team) for team, name in K_BY_TEAM.items()
    if (name, team) not in KICKERS
]


# away, home, day, TV, kickoff ET. Official slate order.
WEEK4_GAMES = [
    ("PIT", "CLE", "Thu 10/1", "Prime", "8:15p"),
    ("IND", "WAS", "Sun 10/4", "NFLN", "9:30a"),
    ("TEN", "BAL", "Sun 10/4", "CBS", "1:00p"),
    ("NE", "BUF", "Sun 10/4", "CBS", "1:00p"),
    ("NYJ", "CHI", "Sun 10/4", "FOX", "1:00p"),
    ("JAX", "CIN", "Sun 10/4", "CBS", "1:00p"),
    ("DAL", "HOU", "Sun 10/4", "FOX", "1:00p"),
    ("ARI", "NYG", "Sun 10/4", "CBS", "1:00p"),
    ("LAR", "PHI", "Sun 10/4", "FOX", "1:00p"),
    ("GB", "TB", "Sun 10/4", "FOX", "1:00p"),
    ("MIA", "MIN", "Sun 10/4", "FOX", "4:05p"),
    ("KC", "LV", "Sun 10/4", "CBS", "4:25p"),
    ("LAC", "SEA", "Sun 10/4", "CBS", "4:25p"),
    ("DEN", "SF", "Sun 10/4", "CBS", "4:25p"),
    ("DET", "CAR", "Sun 10/4", "NBC", "8:20p"),
    ("ATL", "NO", "Mon 10/5", "ESPN", "8:15p"),
]

SPREADS = {
    "PIT@CLE": "PIT -2.5",
    "IND@WAS": "IND -3.5",
    "TEN@BAL": "BAL -11.5",
    "NE@BUF": "BUF -6.5",
    "NYJ@CHI": "CHI -3.5",
    "JAX@CIN": "CIN -2.5",
    "DAL@HOU": "HOU -2.5",
    "ARI@NYG": "ARI -1",
    "LAR@PHI": "LAR -3",
    "GB@TB": "GB -4",
    "MIA@MIN": "MIN -10.5",
    "KC@LV": "KC -4.5",
    "LAC@SEA": "SEA -7",
    "DEN@SF": "SF -2.5",
    "DET@CAR": "DET -3.5",
    "ATL@NO": "NO -2.5",
}

# RotoBaller Week 4 DST tiers, Joey Pollizze.
# https://www.rotoballer.com/week-4-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1952910
RB_W4_DST = {
    "MIN": 1, "BAL": 2, "PIT": 3, "SEA": 4, "GB": 5, "CLE": 6, "KC": 7,
    "BUF": 8, "CHI": 9, "SF": 10, "DEN": 11, "LAR": 12, "HOU": 13,
    "NYG": 14, "NYJ": 15, "ARI": 16, "IND": 17, "TB": 18, "DAL": 19,
    "NO": 20, "DET": 21, "PHI": 22, "MIA": 23, "WAS": 24, "ATL": 25,
    "LAC": 26, "CIN": 27, "JAX": 28, "NE": 29, "LV": 30, "CAR": 31,
    "TEN": 32,
}

# Pro Football Network Week 4 DST, Katz.
# https://www.profootballnetwork.com/fantasy-football/early-defense-rankings-week-4-2026-katz/
PFN_W4_DST = {
    "MIN": 1, "SEA": 2, "BAL": 3, "BUF": 4, "PIT": 5, "KC": 6, "NYJ": 7,
    "JAX": 8, "DEN": 9, "HOU": 10, "LAR": 11, "PHI": 12, "GB": 13, "NYG": 14,
    "SF": 15, "CLE": 16, "DAL": 17, "DET": 18, "CHI": 19, "ATL": 20,
    "ARI": 21, "NE": 22, "LAC": 23, "TB": 24, "NO": 25, "IND": 26,
    "CIN": 27, "LV": 28, "WAS": 29, "CAR": 30,
}

# FantasyPros Let's Stream Defenses, Jacob Herlin, Sep 29.
# https://www.fantasypros.com/2026/09/lets-stream-defenses-week-4-2026-fantasy-football/
FP_W4_DST = {
    "MIN": 1, "BAL": 2, "GB": 3, "SEA": 4, "BUF": 5, "PIT": 6, "CHI": 7,
    "ARI": 8, "CLE": 9, "DET": 10, "NO": 11, "HOU": 12, "ATL": 13, "TB": 14,
    "IND": 15, "WAS": 16, "KC": 17, "CIN": 18, "LAR": 19, "LAC": 20,
    "NYJ": 21, "PHI": 22, "JAX": 23, "DEN": 24, "LV": 25, "SF": 26,
    "NYG": 27, "DAL": 28, "MIA": 29, "NE": 30, "TEN": 31, "CAR": 32,
}

# Sporting News Week 4 DST.
# https://www.sportingnews.com/us/fantasy/news/fantasy-football-dst-rankings-week-4-who-start-best-sleepers-top-busts/283969583a4b1876565b5ddb
SN_W4_DST = {
    "MIN": 1, "PIT": 2, "BAL": 3, "SEA": 4, "KC": 5, "CLE": 6, "BUF": 7,
    "GB": 8, "WAS": 9, "CHI": 10, "LAR": 11, "NYG": 12, "TB": 13, "ARI": 14,
    "SF": 15, "NYJ": 16, "ATL": 17, "HOU": 18, "JAX": 19, "DAL": 20,
}

# NBC Sports Getting Defensive, Gary Davenport, Sep 29. Streamer column order.
# https://www.nbcsports.com/fantasy/football/news/getting-defensive-week-4-fantasy-plays-led-by-vikings-seahawks-top-streaming-defenses
NBC_W4_DST = {
    "MIN": 1, "SEA": 2, "PIT": 3, "CLE": 4, "KC": 5, "BAL": 6, "BUF": 7,
    "CHI": 8, "GB": 9, "NO": 10, "DEN": 11, "JAX": 12,
}

# Softer implied totals first. From the RotoBaller PA column.
VEGAS_DST = {
    "MIN": 1, "BAL": 2, "PIT": 3, "GB": 4, "SEA": 5, "CHI": 6, "CLE": 7,
    "BUF": 8, "ARI": 9, "TB": 10, "KC": 11, "SF": 12, "IND": 13, "LAR": 14,
    "HOU": 15, "NYG": 16, "NO": 17, "NYJ": 18, "DET": 19, "PHI": 20,
    "MIA": 21, "CIN": 22, "DEN": 23, "WAS": 24, "DAL": 25, "LAC": 26,
    "ATL": 27, "LV": 28, "CAR": 29, "JAX": 30, "NE": 31, "TEN": 32,
}

# Week 3 form: clubs that already won big or scored on defense.
FORM_DST = {
    "CHI": 1, "JAX": 2, "MIN": 3, "KC": 4, "DEN": 5, "CLE": 6, "PIT": 7,
    "WAS": 8, "LV": 9, "BAL": 10, "ATL": 11, "BUF": 12, "DET": 13, "SF": 14,
    "NYG": 15,
}

# RotoBaller Week 4 kickers, Nick Mariano.
# https://www.rotoballer.com/week-4-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1953073
RB_W4_K = {
    "Brandon Aubrey": 1, "Tyler Loop": 2, "Evan McPherson": 3,
    "Spencer Shrader": 4, "Harrison Butker": 5, "Eddy Pineiro": 6,
    "Ka'imi Fairbairn": 7, "Cam Little": 8, "Jason Myers": 9,
    "Will Reichard": 10, "Ryan Fitzgerald": 11, "Trey Smack": 12,
    "Tyler Bass": 13, "Jake Bates": 14, "Harrison Mevis": 15,
    "Daniel Carlson": 16, "Chris Boswell": 17, "Chad Ryland": 18,
    "Matt Gay": 19, "Nick Folk": 20, "Cairo Santos": 21,
    "Jason Sanders": 22, "Cameron Dicker": 23, "Chase McLaughlin": 24,
    "Jake Elliott": 25, "Drew Stevens": 26, "Andy Borregales": 27,
    "Wil Lutz": 28, "Dominic Zvada": 29, "Joey Slye": 30,
    "Andre Szmyt": 31, "Riley Patterson": 32,
}

# Sporting News Week 4 kicker board.
# https://www.sportingnews.com/us/fantasy/news/fantasy-football-k-rankings-week-4-who-start-best-sleepers-top-busts/5b1ad9359719da3afa34525e
SN_W4_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Jason Myers": 3,
    "Tyler Loop": 4, "Spencer Shrader": 5, "Eddy Pineiro": 6,
    "Will Reichard": 7, "Daniel Carlson": 8, "Harrison Butker": 9,
    "Cam Little": 10, "Jake Bates": 11, "Evan McPherson": 12,
    "Chris Boswell": 13, "Chase McLaughlin": 14, "Ryan Fitzgerald": 15,
    "Tyler Bass": 16, "Dominic Zvada": 17, "Cairo Santos": 18,
    "Harrison Mevis": 19, "Cameron Dicker": 20,
}

# Sportzeen Week 4 kicker board, Sep 29.
# https://sportzeen.com/week-4-fantasy-football-kicker-rankings/
SZ_W4_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Evan McPherson": 3,
    "Jason Myers": 4, "Will Reichard": 5, "Tyler Loop": 6,
    "Spencer Shrader": 7, "Harrison Butker": 8, "Trey Smack": 9,
    "Cam Little": 10, "Chris Boswell": 11, "Ryan Fitzgerald": 12,
    "Jake Bates": 13, "Drew Stevens": 14, "Nick Folk": 15,
    "Daniel Carlson": 16, "Chad Ryland": 17, "Cairo Santos": 18,
    "Eddy Pineiro": 19, "Dominic Zvada": 20, "Chase McLaughlin": 21,
    "Tyler Bass": 22, "Matt Gay": 23, "Jason Sanders": 24,
    "Jake Elliott": 25, "Wil Lutz": 26, "Harrison Mevis": 27,
    "Cameron Dicker": 28, "Andy Borregales": 29, "Andre Szmyt": 30,
    "Joey Slye": 31, "Riley Patterson": 32,
}

# FantasyPros Week 4 kicker ECR, Oct 1, 11 experts.
# https://www.fantasypros.com/nfl/rankings/k.php
FP_ECR_K = {
    "Brandon Aubrey": 1, "Evan McPherson": 2, "Tyler Loop": 3,
    "Ka'imi Fairbairn": 4, "Harrison Butker": 5, "Will Reichard": 6,
    "Eddy Pineiro": 7, "Jason Myers": 8, "Spencer Shrader": 9,
    "Cam Little": 10, "Jake Bates": 11, "Chris Boswell": 12,
    "Tyler Bass": 13, "Ryan Fitzgerald": 14, "Matt Gay": 15,
    "Daniel Carlson": 16, "Harrison Mevis": 17, "Trey Smack": 18,
    "Nick Folk": 19, "Cairo Santos": 20, "Chad Ryland": 21,
    "Jason Sanders": 22, "Wil Lutz": 23, "Chase McLaughlin": 24,
    "Jake Elliott": 25, "Cameron Dicker": 26, "Andy Borregales": 27,
    "Drew Stevens": 28, "Dominic Zvada": 29, "Andre Szmyt": 30,
    "Joey Slye": 31, "Riley Patterson": 32,
}


def week4_dst_maps() -> dict:
    return {
        "RotoBaller": RB_W4_DST,
        "Pro Football Network": PFN_W4_DST,
        "FantasyPros stream": FP_W4_DST,
        "Sporting News": SN_W4_DST,
        "NBC Sports": NBC_W4_DST,
        "Vegas implied": VEGAS_DST,
        "Week 3 form": FORM_DST,
    }


def week4_k_maps() -> dict:
    return {
        "RotoBaller": RB_W4_K,
        "Sporting News": SN_W4_K,
        "Sportzeen": SZ_W4_K,
        "FantasyPros ECR": FP_ECR_K,
    }


W4_DST_LONG = ("RotoBaller", "Pro Football Network")
W4_K_LONG = ("FantasyPros ECR", "RotoBaller")


def week4_dst_board():
    from bk_curve import bk_value
    rows = [r for r in _mean_rows(DST_TEAMS, week4_dst_maps(), "DST", long_core=W4_DST_LONG) if r["n"] >= 3]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week4_kicker_board():
    return _mean_rows(WEEK4_KICKERS, week4_k_maps(), "K", long_core=W4_K_LONG)


def _fav(spread_map):
    """Spread string like BUF -7 -> BUF."""
    out = {}
    for key, text in spread_map.items():
        club = (text or "").split()[0]
        if club:
            out[key] = club
    return out


# Published straight-up cards. Unpicked games stay off that board.
SN_W4 = {  # Bill Bender, Sporting News
    "PIT@CLE": "PIT", "IND@WAS": "IND", "NE@BUF": "BUF", "NYJ@CHI": "CHI",
    "JAX@CIN": "CIN", "ARI@NYG": "ARI", "LAR@PHI": "LAR", "GB@TB": "GB",
    "TEN@BAL": "BAL", "DAL@HOU": "DAL", "MIA@MIN": "MIN", "KC@LV": "KC",
    "DEN@SF": "SF", "LAC@SEA": "SEA", "DET@CAR": "DET", "ATL@NO": "NO",
}
CBS_W4 = {  # Tyler Sullivan, CBS Sports, Sep 30
    "PIT@CLE": "PIT", "IND@WAS": "IND", "ARI@NYG": "ARI", "JAX@CIN": "CIN",
    "NE@BUF": "BUF", "NYJ@CHI": "CHI", "TEN@BAL": "BAL", "DAL@HOU": "DAL",
    "MIA@MIN": "MIN", "DEN@SF": "DEN", "KC@LV": "KC", "LAC@SEA": "SEA",
    "LAR@PHI": "LAR", "GB@TB": "GB", "DET@CAR": "DET", "ATL@NO": "ATL",
}
BREECH_W4 = {  # John Breech, CBS Sports, Sep 29
    "PIT@CLE": "CLE", "IND@WAS": "IND", "JAX@CIN": "CIN", "NE@BUF": "BUF",
    "NYJ@CHI": "NYJ", "ARI@NYG": "ARI", "LAR@PHI": "LAR", "GB@TB": "GB",
    "DAL@HOU": "HOU", "MIA@MIN": "MIN", "KC@LV": "KC", "DEN@SF": "SF",
    "LAC@SEA": "SEA", "DET@CAR": "DET", "ATL@NO": "ATL", "TEN@BAL": "BAL",
}
FS_W4 = {  # Cody Williams, FanSided, Sep 29
    "PIT@CLE": "CLE", "IND@WAS": "IND", "TEN@BAL": "BAL", "NYJ@CHI": "CHI",
    "GB@TB": "GB", "JAX@CIN": "JAX", "NE@BUF": "BUF", "ARI@NYG": "ARI",
    "DAL@HOU": "DAL", "LAR@PHI": "LAR", "MIA@MIN": "MIN", "LAC@SEA": "SEA",
    "DEN@SF": "SF", "KC@LV": "KC", "DET@CAR": "DET", "ATL@NO": "NO",
}
LINE_W4 = {  # SportsLine model notes published Sep 30
    "ARI@NYG": "NYG", "LAC@SEA": "SEA", "JAX@CIN": "CIN",
    "NE@BUF": "BUF", "TEN@BAL": "BAL", "MIA@MIN": "MIN",
    "KC@LV": "KC", "LAR@PHI": "LAR", "GB@TB": "GB",
}
VEGAS_SU = _fav(SPREADS)
W3_WINNERS = {
    "TEN@BAL": "BAL", "NE@BUF": "BUF", "NYJ@CHI": "CHI", "JAX@CIN": "JAX",
    "ARI@NYG": "NYG", "MIA@MIN": "MIN", "DET@CAR": "DET", "ATL@NO": "ATL",
}
POWER_W4 = {
    "PIT@CLE": "PIT", "IND@WAS": "IND", "TEN@BAL": "BAL", "NE@BUF": "BUF",
    "NYJ@CHI": "CHI", "JAX@CIN": "JAX", "DAL@HOU": "DAL", "ARI@NYG": "NYG",
    "LAR@PHI": "LAR", "GB@TB": "GB", "MIA@MIN": "MIN", "KC@LV": "KC",
    "LAC@SEA": "SEA", "DEN@SF": "SF", "DET@CAR": "DET", "ATL@NO": "ATL",
}


def match_maps() -> dict:
    return {
        "Sporting News": SN_W4,
        "CBS Sports": CBS_W4,
        "CBS Breech": BREECH_W4,
        "FanSided": FS_W4,
        "SportsLine model": LINE_W4,
        "Vegas favorite": VEGAS_SU,
        "Week 3 winners": W3_WINNERS,
        "Post-Week 3 power": POWER_W4,
    }


W4_DST_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-4-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1952910", "Joey Pollizze tiers. Vikings first at Miami."),
    ("Pro Football Network", "https://www.profootballnetwork.com/fantasy-football/early-defense-rankings-week-4-2026-katz/", "Katz 1-30. Vikings, Seahawks, Ravens."),
    ("FantasyPros stream", "https://www.fantasypros.com/2026/09/lets-stream-defenses-week-4-2026-fantasy-football/", "Jacob Herlin. Vikings, Ravens, Packers."),
    ("Sporting News", "https://www.sportingnews.com/us/fantasy/news/fantasy-football-dst-rankings-week-4-who-start-best-sleepers-top-busts/283969583a4b1876565b5ddb", "Vikings, Steelers, Ravens."),
    ("NBC Sports", "https://www.nbcsports.com/fantasy/football/news/getting-defensive-week-4-fantasy-plays-led-by-vikings-seahawks-top-streaming-defenses", "Gary Davenport streamer column. Vikings and Seahawks first."),
    ("Vegas implied", "", "Softer implied totals get the higher stream rank."),
    ("Week 3 form", "", "Clubs that already won big or scored on defense."),
]

W4_K_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-4-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1953073", "Aubrey first. Loop and McPherson next."),
    ("Sporting News", "https://www.sportingnews.com/us/fantasy/news/fantasy-football-k-rankings-week-4-who-start-best-sleepers-top-busts/5b1ad9359719da3afa34525e", "Aubrey, Fairbairn, Myers."),
    ("Sportzeen", "https://sportzeen.com/week-4-fantasy-football-kicker-rankings/", "Charles, Sep 29. Aubrey, Fairbairn, McPherson."),
    ("FantasyPros ECR", "https://www.fantasypros.com/nfl/rankings/k.php", "Week 4 kicker consensus, 11 experts, Oct 1."),
]

MATCH_SOURCES = [
    ("Sporting News", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-4/d770d8401c10e9e74b6e687b", "Bill Bender's full SU card. Steelers, Bills, Chiefs."),
    ("CBS Sports", "https://www.cbssports.com/nfl/news/nfl-week-4-picks-odds-packers-road-teams/", "Tyler Sullivan. Steelers 21-17. Broncos and Falcons fades."),
    ("CBS Breech", "https://www.cbssports.com/nfl/news/nfl-week-4-picks-and-score-predictions-breech/", "John Breech. Browns on Thursday. Texans get one."),
    ("FanSided", "https://fansided.com/nfl/nfl-week-4-picks-and-predictions-straight-up-and-ats-bills-bury-patriots-chiefs-and-lions-roll", "Cody Williams. Browns, Jaguars, Saints."),
    ("SportsLine model", "https://www.cbssports.com/betting/news/week-4-2026-nfl-odds-picks-predictions/", "10,000 sims. Giants cover. Seahawks cover. Bengals over."),
    ("Vegas favorite", "", "Current published spread favorite."),
    ("Week 3 winners", "", "The club that already won, when only one side did."),
    ("Post-Week 3 power", "", "Short 1-32 after the third Sunday. Higher club wins."),
]


# Finished Week 4 card. Every final is in.
WEEK4_FINALS = {
    "PIT@CLE": {"score": "27-24", "winner": "CLE", "day": "Thu Final"},
    "IND@WAS": {"score": "30-13", "winner": "IND", "day": "Sun Final"},
    "TEN@BAL": {"score": "24-18", "winner": "BAL", "day": "Sun Final"},
    "NE@BUF": {"score": "29-26", "winner": "NE", "day": "Sun Final"},
    "NYJ@CHI": {"score": "23-12", "winner": "CHI", "day": "Sun Final"},
    "JAX@CIN": {"score": "22-17", "winner": "JAX", "day": "Sun Final"},
    "DAL@HOU": {"score": "34-30", "winner": "DAL", "day": "Sun Final"},
    "ARI@NYG": {"score": "36-24", "winner": "NYG", "day": "Sun Final"},
    "LAR@PHI": {"score": "24-20", "winner": "LAR", "day": "Sun Final"},
    "GB@TB": {"score": "17-14", "winner": "GB", "day": "Sun Final"},
    "MIA@MIN": {"score": "15-10", "winner": "MIN", "day": "Sun Final"},
    "KC@LV": {"score": "30-27", "winner": "KC", "day": "Sun Final"},
    "LAC@SEA": {"score": "30-23", "winner": "SEA", "day": "Sun Final"},
    "DEN@SF": {"score": "24-14", "winner": "SF", "day": "Sun Final"},
    "DET@CAR": {"score": "32-26", "winner": "CAR", "day": "Sun Final"},
    "ATL@NO": {"score": "45-24", "winner": "ATL", "day": "Mon Final"},
}


def week4_matchups():
    maps = match_maps()
    rows = []
    for slate, (away, home, day, tv, kick) in enumerate(WEEK4_GAMES):
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
        fin = WEEK4_FINALS.get(key)
        if fin:
            rows[-1]["final"] = fin["score"]
            rows[-1]["final_winner"] = fin["winner"]
            rows[-1]["day"] = fin["day"]
    rows.sort(key=lambda r: int(r.get("slate") or 0))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


W4_DST_FAQ = [
    ("How is Week 4 DST built?", "Super Aggregate of published Week 4 defense boards. 50% RotoBaller and Pro Football Network, 50% FantasyPros, Sporting News, NBC Sports, implied totals, and Week 3 form."),
    ("Is this Top Defenses?", "No. Top Defenses is rest of season. This board is only Week 4."),
]
W4_K_FAQ = [
    ("How is Week 4 Kickers built?", "Super Aggregate of RotoBaller, Sporting News, Sportzeen, and FantasyPros ECR."),
    ("Who leads?", "Aubrey sits first. Loop and Fairbairn follow."),
]
W4_MATCH_FAQ = [
    ("How are the win picks built?", "Published Week 4 cards: Sporting News, two CBS Sports cards, FanSided, the SportsLine model, the market favorite, Week 3 winners, and a short post-Week 3 power board. Unpicked games on a board are skipped."),
    ("Is this a win chance?", "Away and Home are raw vote counts. The pick is the side with more published votes."),
    ("Is this a bet slip?", "It is a mash of public picks and the market. The finished Week 4 card is in. Live picks live on Week 5 Predictions."),
]
