"""Week 5 DST, kicker, and matchup aggregates.

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

WEEK5_KICKERS = list(KICKERS) + [
    (name, team) for team, name in K_BY_TEAM.items()
    if (name, team) not in KICKERS
]


# away, home, day, TV, kickoff ET. Official slate. KC and CAR on bye.
WEEK5_GAMES = [
    ("TB", "DAL", "Thu 10/8", "Prime", "8:15p"),
    ("PHI", "JAX", "Sun 10/11", "NFLN", "9:30a"),
    ("CIN", "MIA", "Sun 10/11", "FOX", "1:00p"),
    ("LV", "NE", "Sun 10/11", "CBS", "1:00p"),
    ("MIN", "NO", "Sun 10/11", "FOX", "1:00p"),
    ("CLE", "NYJ", "Sun 10/11", "CBS", "1:00p"),
    ("IND", "PIT", "Sun 10/11", "CBS", "1:00p"),
    ("HOU", "TEN", "Sun 10/11", "CBS", "1:00p"),
    ("NYG", "WAS", "Sun 10/11", "FOX", "1:00p"),
    ("DEN", "LAC", "Sun 10/11", "CBS", "4:05p"),
    ("DET", "ARI", "Sun 10/11", "FOX", "4:25p"),
    ("CHI", "GB", "Sun 10/11", "FOX", "4:25p"),
    ("SF", "SEA", "Sun 10/11", "FOX", "4:25p"),
    ("BAL", "ATL", "Sun 10/11", "NBC", "8:20p"),
    ("BUF", "LAR", "Mon 10/12", "ESPN", "8:15p"),
]

SPREADS = {
    "TB@DAL": "DAL -9.5",
    "PHI@JAX": "JAX -4.5",
    "CIN@MIA": "CIN -7.5",
    "LV@NE": "NE -3.5",
    "MIN@NO": "MIN -1.5",
    "CLE@NYJ": "NYJ -1.5",
    "IND@PIT": "PIT -1.5",
    "HOU@TEN": "HOU -6.5",
    "NYG@WAS": "WAS -3.5",
    "DEN@LAC": "DEN -3.5",
    "DET@ARI": "DET -4.5",
    "CHI@GB": "CHI -2.5",
    "SF@SEA": "SEA -3",
    "BAL@ATL": "BAL -3.5",
    "BUF@LAR": "LAR -2.5",
}

# RotoBaller Week 5 DST tiers, Joey Pollizze.
# https://www.rotoballer.com/week-5-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1958775
RB_W5_DST = {
    "HOU": 1, "CIN": 2, "DEN": 3, "MIN": 4, "DAL": 5, "CLE": 6, "JAX": 7,
    "PIT": 8, "CHI": 9, "NYJ": 10, "SEA": 11, "BAL": 12, "NE": 13,
    "WAS": 14, "IND": 15, "LAC": 16, "GB": 17, "NYG": 18, "LV": 19,
    "PHI": 20, "ATL": 21, "NO": 22, "MIA": 23, "TEN": 24, "BUF": 25,
    "SF": 26, "LAR": 27, "DET": 28, "TB": 29, "ARI": 30,
}

# Pro Football Network Week 5 DST, Katz.
# https://www.profootballnetwork.com/fantasy-football/early-defense-rankings-week-5-2026-katz/
PFN_W5_DST = {
    "HOU": 1, "DEN": 2, "CIN": 3, "MIN": 4, "JAX": 5, "DAL": 6, "NE": 7,
    "NYJ": 8, "CLE": 9, "BAL": 10, "PIT": 11, "SEA": 12, "CHI": 13,
    "LAR": 14, "PHI": 15, "NYG": 16, "SF": 17, "DET": 18, "GB": 19,
    "BUF": 20, "NO": 21, "TEN": 22, "WAS": 23, "ATL": 24, "LAC": 25,
    "LV": 26, "TB": 27, "IND": 28, "ARI": 29, "MIA": 30,
}

# FantasyPros weekly DST, Pat Fitzmaurice, Oct 5.
# https://www.fantasypros.com/nfl/fantasy-football-rankings/weekly-dst.php
FP_W5_DST = {
    "HOU": 1, "MIN": 2, "PIT": 3, "DEN": 4, "DAL": 5, "CIN": 6, "NE": 7,
    "WAS": 8, "JAX": 9, "SEA": 10, "NO": 11, "BAL": 12,
}

# NBC Sports Getting Defensive, Eric Samulski, Oct 6.
# https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-5-defense-dst-rankings-and-streamers
NBC_W5_DST = {
    "JAX": 1, "MIN": 2, "CHI": 3, "CIN": 4, "HOU": 5, "DEN": 6, "PIT": 7,
    "NYJ": 8, "DAL": 9, "SEA": 10, "NE": 11, "LV": 12, "CLE": 13,
    "WAS": 14, "BAL": 15, "IND": 16, "LAC": 17, "TEN": 18, "NYG": 19,
    "ATL": 20, "NO": 21, "LAR": 22, "SF": 23, "MIA": 24, "GB": 25,
    "PHI": 26, "DET": 27, "TB": 28, "BUF": 29, "ARI": 30, "CAR": 31, "KC": 32,
}

# Softer implied totals first. RotoBaller PA column, Oct 6.
VEGAS_DST = {
    "HOU": 1, "CIN": 2, "JAX": 3, "DAL": 4, "CLE": 5, "NYJ": 6, "DEN": 7,
    "WAS": 8, "MIN": 9, "NE": 10, "PIT": 11, "BAL": 12, "CHI": 13, "NO": 14,
    "SEA": 15, "LAC": 16, "IND": 17, "GB": 18, "NYG": 19, "TEN": 20,
    "PHI": 21, "ATL": 22, "LV": 23, "MIA": 24, "DET": 25, "SF": 26,
    "LAR": 27, "BUF": 28, "TB": 29, "ARI": 30,
}

# Week 4 form: clubs that already won big or scored on defense.
FORM_DST = {
    "CHI": 1, "IND": 2, "ATL": 3, "SF": 4, "NYG": 5, "MIN": 6, "CLE": 7,
    "SEA": 8, "NE": 9, "JAX": 10, "KC": 11, "GB": 12, "CAR": 13, "DAL": 14,
    "LAR": 15, "BAL": 16,
}

# RotoBaller Week 5 kickers, Nick Mariano.
# https://www.rotoballer.com/week-5-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1958720
RB_W5_K = {
    "Brandon Aubrey": 1, "Spencer Shrader": 2, "Evan McPherson": 3,
    "Ka'imi Fairbairn": 4, "Will Reichard": 5, "Tyler Loop": 6,
    "Cam Little": 7, "Jake Bates": 8, "Eddy Pineiro": 9,
    "Jason Myers": 10, "Trey Smack": 11, "Tyler Bass": 12,
    "Harrison Mevis": 13, "Chad Ryland": 14, "Matt Gay": 15,
    "Daniel Carlson": 16, "Chris Boswell": 17, "Cairo Santos": 18,
    "Drew Stevens": 19, "Nick Folk": 20, "Dominic Zvada": 21,
    "Chase McLaughlin": 22, "Cameron Dicker": 23, "Andy Borregales": 24,
    "Wil Lutz": 25, "Jake Elliott": 26, "Andre Szmyt": 27,
    "Jason Sanders": 28, "Joey Slye": 29, "Riley Patterson": 30,
}

# Sports Illustrated Week 5 kicker board.
# https://www.si.com/fantasy/week-5-kicker-rankings
SI_W5_K = {
    "Brandon Aubrey": 1, "Evan McPherson": 2, "Will Reichard": 3,
    "Spencer Shrader": 4, "Ka'imi Fairbairn": 5, "Tyler Loop": 6,
    "Jake Bates": 7, "Dominic Zvada": 8, "Cam Little": 9,
    "Chad Ryland": 10, "Chris Boswell": 11, "Jason Myers": 12,
    "Cameron Dicker": 13, "Tyler Bass": 14, "Jason Sanders": 15,
    "Harrison Mevis": 16, "Cairo Santos": 17, "Nick Folk": 18,
    "Wil Lutz": 19, "Andre Szmyt": 20, "Trey Smack": 21,
    "Eddy Pineiro": 22, "Daniel Carlson": 23, "Matt Gay": 24,
    "Drew Stevens": 25, "Chase McLaughlin": 26, "Jake Elliott": 27,
    "Andy Borregales": 28, "Riley Patterson": 29, "Joey Slye": 30,
}

# Pro Football Network Week 5 kickers, Katz.
# https://www.profootballnetwork.com/fantasy-football/early-kicker-rankings-week-5-2026-katz/
PFN_W5_K = {
    "Brandon Aubrey": 1, "Evan McPherson": 2, "Will Reichard": 3,
    "Cam Little": 4, "Ka'imi Fairbairn": 5, "Tyler Loop": 6,
    "Trey Smack": 7, "Jake Bates": 8, "Tyler Bass": 9,
    "Andy Borregales": 10, "Cameron Dicker": 11, "Jason Myers": 12,
    "Harrison Mevis": 13, "Jake Elliott": 15, "Eddy Pineiro": 16,
    "Matt Gay": 17, "Andre Szmyt": 18, "Spencer Shrader": 19,
    "Chase McLaughlin": 20, "Wil Lutz": 21, "Nick Folk": 22,
    "Cairo Santos": 23, "Chris Boswell": 24, "Daniel Carlson": 25,
    "Dominic Zvada": 26, "Chad Ryland": 27, "Joey Slye": 29,
    "Drew Stevens": 30,
}

# FantasyPros Week 5 kicker ECR, Oct 7, 27 experts.
# https://www.fantasypros.com/nfl/rankings/k.php
FP_ECR_K = {
    "Brandon Aubrey": 1, "Evan McPherson": 2, "Will Reichard": 3,
    "Ka'imi Fairbairn": 4, "Spencer Shrader": 5, "Jake Bates": 6,
    "Cam Little": 7, "Jason Myers": 8, "Tyler Loop": 9,
    "Eddy Pineiro": 10, "Chris Boswell": 11, "Tyler Bass": 12,
    "Cairo Santos": 13, "Harrison Mevis": 14, "Matt Gay": 15,
    "Daniel Carlson": 16, "Chad Ryland": 17, "Trey Smack": 18,
    "Andy Borregales": 19, "Wil Lutz": 20, "Chase McLaughlin": 21,
    "Nick Folk": 22, "Jason Sanders": 23, "Dominic Zvada": 24,
    "Jake Elliott": 25, "Drew Stevens": 26, "Cameron Dicker": 27,
    "Andre Szmyt": 28, "Joey Slye": 29, "Riley Patterson": 30,
}


def week5_dst_maps() -> dict:
    return {
        "RotoBaller": RB_W5_DST,
        "Pro Football Network": PFN_W5_DST,
        "FantasyPros weekly": FP_W5_DST,
        "NBC Sports": NBC_W5_DST,
        "Vegas implied": VEGAS_DST,
        "Week 4 form": FORM_DST,
    }


def week5_k_maps() -> dict:
    return {
        "RotoBaller": RB_W5_K,
        "Sports Illustrated": SI_W5_K,
        "Pro Football Network": PFN_W5_K,
        "FantasyPros ECR": FP_ECR_K,
    }


W5_DST_LONG = ("RotoBaller", "Pro Football Network")
W5_K_LONG = ("FantasyPros ECR", "RotoBaller")


def week5_dst_board():
    from bk_curve import bk_value
    rows = [r for r in _mean_rows(DST_TEAMS, week5_dst_maps(), "DST", long_core=W5_DST_LONG) if r["n"] >= 3]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week5_kicker_board():
    return _mean_rows(WEEK5_KICKERS, week5_k_maps(), "K", long_core=W5_K_LONG)


def _fav(spread_map):
    """Spread string like BUF -7 -> BUF."""
    out = {}
    for key, text in spread_map.items():
        club = (text or "").split()[0]
        if club:
            out[key] = club
    return out


# Published straight-up cards. Unpicked games stay off that board.
SN_W5 = {  # Bill Bender, Sporting News
    "TB@DAL": "DAL", "PHI@JAX": "JAX", "CHI@GB": "CHI", "HOU@TEN": "HOU",
    "CIN@MIA": "CIN", "LV@NE": "NE", "MIN@NO": "NO", "CLE@NYJ": "CLE",
    "IND@PIT": "PIT", "NYG@WAS": "NYG", "DEN@LAC": "DEN", "DET@ARI": "DET",
    "SF@SEA": "SF", "BAL@ATL": "BAL", "BUF@LAR": "LAR",
}
BREECH_W5 = {  # John Breech, CBS Sports, Oct 6
    "TB@DAL": "DAL", "PHI@JAX": "JAX", "CHI@GB": "CHI", "HOU@TEN": "HOU",
    "CIN@MIA": "CIN", "LV@NE": "NE", "MIN@NO": "MIN", "CLE@NYJ": "CLE",
    "IND@PIT": "IND", "NYG@WAS": "NYG", "DEN@LAC": "DEN", "DET@ARI": "DET",
    "SF@SEA": "SF", "BAL@ATL": "ATL", "BUF@LAR": "LAR",
}
IYER_W5 = {  # Vinnie Iyer, Sporting News ATS card with SU winners
    "TB@DAL": "DAL", "PHI@JAX": "JAX", "LV@NE": "NE", "CLE@NYJ": "NYJ",
    "SF@SEA": "SF", "BUF@LAR": "BUF",
}
LINE_W5 = {  # SportsLine model notes published Oct 6
    "MIN@NO": "MIN", "CIN@MIA": "CIN",
}
VEGAS_SU = _fav(SPREADS)
W4_WINNERS = {
    "TB@DAL": "DAL", "PHI@JAX": "JAX", "CIN@MIA": "CIN", "LV@NE": "NE",
    "MIN@NO": "MIN", "CLE@NYJ": "CLE", "IND@PIT": "IND", "NYG@WAS": "NYG",
    "DEN@LAC": "DEN", "DET@ARI": "DET", "CHI@GB": "CHI", "SF@SEA": "SF",
    "BUF@LAR": "LAR",
}
POWER_W5 = {
    "TB@DAL": "DAL", "PHI@JAX": "JAX", "CIN@MIA": "CIN", "LV@NE": "LV",
    "MIN@NO": "MIN", "CLE@NYJ": "CLE", "IND@PIT": "PIT", "HOU@TEN": "HOU",
    "NYG@WAS": "NYG", "DEN@LAC": "DEN", "DET@ARI": "DET", "CHI@GB": "CHI",
    "SF@SEA": "SF", "BAL@ATL": "BAL", "BUF@LAR": "BUF",
}


def match_maps() -> dict:
    return {
        "Sporting News": SN_W5,
        "CBS Breech": BREECH_W5,
        "Sporting News ATS": IYER_W5,
        "SportsLine model": LINE_W5,
        "Vegas favorite": VEGAS_SU,
        "Week 4 winners": W4_WINNERS,
        "Post-Week 4 power": POWER_W5,
    }


W5_DST_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-5-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1958775", "Joey Pollizze tiers. Texans first at Tennessee."),
    ("Pro Football Network", "https://www.profootballnetwork.com/fantasy-football/early-defense-rankings-week-5-2026-katz/", "Katz 1-30. Texans, Broncos, Bengals."),
    ("FantasyPros weekly", "https://www.fantasypros.com/nfl/fantasy-football-rankings/weekly-dst.php", "Pat Fitzmaurice. Texans, Vikings, Steelers."),
    ("NBC Sports", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-week-5-defense-dst-rankings-and-streamers", "Eric Samulski. Jaguars and Vikings first."),
    ("Vegas implied", "", "Softer implied totals get the higher stream rank."),
    ("Week 4 form", "", "Clubs that already won big or scored on defense."),
]

W5_K_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-5-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1958720", "Aubrey first. Shrader and McPherson next."),
    ("Sports Illustrated", "https://www.si.com/fantasy/week-5-kicker-rankings", "Aubrey, McPherson, Reichard."),
    ("Pro Football Network", "https://www.profootballnetwork.com/fantasy-football/early-kicker-rankings-week-5-2026-katz/", "Katz. Aubrey, McPherson, Reichard."),
    ("FantasyPros ECR", "https://www.fantasypros.com/nfl/rankings/k.php", "Week 5 kicker consensus, 27 experts, Oct 7."),
]

MATCH_SOURCES = [
    ("Sporting News", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-5/04787d3ef5247c02e1b96a88", "Bill Bender's full SU card. Cowboys, Bears, Rams."),
    ("CBS Breech", "https://www.cbssports.com/nfl/news/nfl-week-5-picks-score-predictions-ravens-bills-49ers/", "John Breech. 49ers on the road. Falcons on Sunday night."),
    ("Sporting News ATS", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-against-spread-week-5/eca9ea6e41412f089384daf3", "Vinnie Iyer. Bills on Monday. 49ers in Seattle."),
    ("SportsLine model", "https://www.cbssports.com/betting/news/week-5-2026-nfl-odds-picks-predictions/", "10,000 sims. Vikings cover. Bengals cover."),
    ("Vegas favorite", "", "Current published spread favorite."),
    ("Week 4 winners", "", "The club that already won, when only one side did."),
    ("Post-Week 4 power", "", "Short 1-32 after the fourth Sunday. Higher club wins."),
]


# Thursday has not kicked. Sunday and Monday stay open.
WEEK5_FINALS = {}


def week5_matchups():
    maps = match_maps()
    rows = []
    for slate, (away, home, day, tv, kick) in enumerate(WEEK5_GAMES):
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
        fin = WEEK5_FINALS.get(key)
        if fin:
            rows[-1]["final"] = fin["score"]
            rows[-1]["final_winner"] = fin["winner"]
            rows[-1]["day"] = fin["day"]
    rows.sort(key=lambda r: int(r.get("slate") or 0))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


W5_DST_FAQ = [
    ("How is Week 5 DST built?", "Super Aggregate of published Week 5 defense boards. 50% RotoBaller and Pro Football Network, 50% FantasyPros, NBC Sports, implied totals, and Week 4 form."),
    ("Is this Top Defenses?", "Top Defenses is rest of season. This board is only Week 5."),
]
W5_K_FAQ = [
    ("How is Week 5 Kickers built?", "Super Aggregate of RotoBaller, Sports Illustrated, Pro Football Network, and FantasyPros ECR."),
    ("Who leads?", "Aubrey sits first. McPherson and Fairbairn follow."),
]
W5_MATCH_FAQ = [
    ("How are the win picks built?", "Published Week 5 cards: Sporting News, John Breech at CBS Sports, the Sporting News ATS card, the SportsLine model, the market favorite, Week 4 winners, and a short post-Week 4 power board. Unpicked games on a board are skipped."),
    ("Is this a win chance?", "Away and Home are raw vote counts. The pick is the side with more published votes."),
    ("Is this a bet slip?", "It is a mash of public picks and the market. Thursday has not kicked. Sunday and Monday stay open. Kansas City and Carolina are on bye."),
]
