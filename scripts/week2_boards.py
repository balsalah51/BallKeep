"""Week 2 DST, kicker, and matchup aggregates.

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

WEEK2_KICKERS = list(KICKERS) + [
    (name, team) for team, name in K_BY_TEAM.items()
    if (name, team) not in KICKERS
]


# away, home, day, TV, kickoff ET. Official slate order.
WEEK2_GAMES = [
    ("DET", "BUF", "Thu 9/17", "Prime", "8:15p"),
    ("CAR", "ATL", "Sun 9/20", "FOX", "1:00p"),
    ("NO", "BAL", "Sun 9/20", "CBS", "1:00p"),
    ("MIN", "CHI", "Sun 9/20", "FOX", "1:00p"),
    ("CIN", "HOU", "Sun 9/20", "CBS", "1:00p"),
    ("PIT", "NE", "Sun 9/20", "CBS", "1:00p"),
    ("GB", "NYJ", "Sun 9/20", "FOX", "1:00p"),
    ("CLE", "TB", "Sun 9/20", "CBS", "1:00p"),
    ("PHI", "TEN", "Sun 9/20", "FOX", "1:00p"),
    ("JAX", "DEN", "Sun 9/20", "CBS", "4:05p"),
    ("LV", "LAC", "Sun 9/20", "CBS", "4:05p"),
    ("SEA", "ARI", "Sun 9/20", "FOX", "4:25p"),
    ("WAS", "DAL", "Sun 9/20", "FOX", "4:25p"),
    ("MIA", "SF", "Sun 9/20", "FOX", "4:25p"),
    ("IND", "KC", "Sun 9/20", "NBC", "8:20p"),
    ("NYG", "LAR", "Mon 9/21", "ESPN/ABC", "8:15p"),
]

SPREADS = {
    "DET@BUF": "BUF -4.5",
    "CAR@ATL": "ATL -1.5",
    "NO@BAL": "BAL -8.5",
    "MIN@CHI": "CHI -5.5",
    "CIN@HOU": "HOU -3",
    "PIT@NE": "NE -5.5",
    "GB@NYJ": "GB -4.5",
    "CLE@TB": "TB -8.5",
    "PHI@TEN": "PHI -4.5",
    "JAX@DEN": "DEN -2.5",
    "LV@LAC": "LAC -7",
    "SEA@ARI": "SEA -4.5",
    "WAS@DAL": "DAL -3.5",
    "MIA@SF": "SF -12.5",
    "IND@KC": "KC -5.5",
    "NYG@LAR": "LAR -9.5",
}

# RotoBaller Week 2 DST, Sep 2026.
# https://www.rotoballer.com/week-2-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1931561
RB_W2_DST = {
    "SF": 1, "PHI": 2, "TB": 3, "SEA": 4, "LAC": 5, "GB": 6, "LAR": 7,
    "BAL": 10, "JAX": 15, "CHI": 16, "ATL": 17, "ARI": 18,
}

# Pro Football Network Week 2 DST, Sep 14.
# https://www.profootballnetwork.com/fantasy-football/defense-rankings-week-2-2026-katz/
PFN_W2_DST = {
    "PHI": 1, "SEA": 2, "LAC": 3, "LAR": 4, "TB": 5, "SF": 6,
    "DEN": 7, "HOU": 8, "BAL": 9, "JAX": 10, "NE": 11, "KC": 12,
}

# ESPN D/ST road map Week 2.
# https://www.espn.com/fantasy/football/story/_/id/49798496
ESPN_W2_DST = {
    "SEA": 1, "PHI": 2, "LAC": 3, "NE": 4, "TB": 5, "BAL": 6, "GB": 7, "SF": 8,
}

# 4for4 Week 2 DEF, Sep 14.
# https://www.4for4.com/fantasy-football-rankings/def/2026/week2
FOUR_W2_DST = {
    "JAX": 1, "LAC": 2, "PIT": 3, "PHI": 4, "LAR": 5,
    "DET": 6, "HOU": 7, "SEA": 8, "TEN": 9, "DEN": 10,
}

# Roto Street Journal streamers, Sep 14.
# https://www.rotostreetjournal.com/2026/09/14/best-fantasy-football-week-2-defense-streamers-d-st-49ers-dst-bengals-dst-look-to-impress-again/
RSJ_W2_DST = {
    "SF": 1, "CIN": 2, "TB": 3, "DAL": 4, "GB": 5, "ATL": 6,
}

# Matchup-implied DST (softer opponent first). Published Vegas totals.
VEGAS_DST = {
    "SF": 1, "TB": 2, "PHI": 3, "SEA": 4, "BAL": 5, "NE": 6, "LAC": 7,
    "CHI": 8, "GB": 9, "LAR": 10, "DAL": 11, "KC": 12, "HOU": 13, "DEN": 14,
    "ATL": 15, "JAX": 16,
}

# Week 1 form: clubs that already scored on defense or won big.
FORM_DST = {
    "JAX": 1, "PIT": 2, "SEA": 3, "SF": 4, "BAL": 5, "CHI": 6,
    "BUF": 7, "PHI": 8, "LV": 9, "MIN": 10, "CIN": 11, "NYJ": 12,
}

# RotoBaller Week 2 kickers.
# https://www.rotoballer.com/week-2-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1931589
RB_W2_K = {
    "Brandon Aubrey": 1, "Eddy Pineiro": 2, "Cameron Dicker": 3,
    "Ka'imi Fairbairn": 4, "Cam Little": 5, "Cairo Santos": 6,
    "Tyler Loop": 7, "Tyler Bass": 8, "Jason Myers": 9, "Evan McPherson": 10,
    "Harrison Butker": 11, "Harrison Mevis": 12, "Trey Smack": 13,
    "Chase McLaughlin": 14, "Jake Elliott": 15, "Jake Bates": 16,
}

# FantasyPros Week 2 kicker score table, Sep 2026.
# https://www.fantasypros.com/2026/09/fantasy-football-kicker-rankings-waiver-wire-pickups-week-2-2026/
FP_W2_K = {
    "Cameron Dicker": 1, "Tyler Loop": 2, "Brandon Aubrey": 3,
    "Cairo Santos": 4, "Andy Borregales": 5, "Ka'imi Fairbairn": 6,
    "Chase McLaughlin": 7, "Cam Little": 8, "Eddy Pineiro": 9,
    "Evan McPherson": 10, "Jason Myers": 11, "Trey Smack": 12,
}

FP_ECR_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Eddy Pineiro": 3,
    "Evan McPherson": 4, "Ka'imi Fairbairn": 5, "Jason Myers": 6,
    "Cairo Santos": 7, "Cam Little": 8, "Tyler Loop": 10,
    "Chase McLaughlin": 20,
}


def week2_dst_maps() -> dict:
    return {
        "RotoBaller": RB_W2_DST,
        "Pro Football Network": PFN_W2_DST,
        "ESPN road map": ESPN_W2_DST,
        "4for4": FOUR_W2_DST,
        "Roto Street Journal": RSJ_W2_DST,
        "Vegas implied": VEGAS_DST,
        "Week 1 form": FORM_DST,
    }


def week2_k_maps() -> dict:
    return {
        "RotoBaller": RB_W2_K,
        "FantasyPros score": FP_W2_K,
        "FantasyPros ECR": FP_ECR_K,
    }


W2_DST_LONG = ("RotoBaller", "Pro Football Network")
W2_K_LONG = ("FantasyPros ECR", "RotoBaller")


def week2_dst_board():
    from bk_curve import bk_value
    rows = [r for r in _mean_rows(DST_TEAMS, week2_dst_maps(), "DST", long_core=W2_DST_LONG) if r["n"] >= 3]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week2_kicker_board():
    return _mean_rows(WEEK2_KICKERS, week2_k_maps(), "K", long_core=W2_K_LONG)


def _fav(spread_map):
    """Spread string like BUF -4.5 -> BUF."""
    out = {}
    for key, text in spread_map.items():
        club = (text or "").split()[0]
        if club:
            out[key] = club
    return out


# Published straight-up cards. Unpicked games stay off that board.
SN_W2 = {  # Sporting News, Bill Bender SU card, Sep 16
    "DET@BUF": "BUF", "CAR@ATL": "CAR", "NO@BAL": "BAL", "MIN@CHI": "CHI",
    "CIN@HOU": "CIN", "PIT@NE": "PIT", "GB@NYJ": "GB", "CLE@TB": "TB",
    "PHI@TEN": "PHI", "JAX@DEN": "DEN", "LV@LAC": "LAC", "SEA@ARI": "SEA",
    "WAS@DAL": "DAL", "MIA@SF": "SF", "IND@KC": "KC", "NYG@LAR": "LAR",
}
CBS_W2 = {  # John Breech, CBS Sports, Sep 15
    "DET@BUF": "BUF", "CAR@ATL": "CAR", "NO@BAL": "BAL", "MIN@CHI": "CHI",
    "CIN@HOU": "CIN", "PIT@NE": "NE", "GB@NYJ": "GB", "CLE@TB": "TB",
    "PHI@TEN": "PHI", "JAX@DEN": "DEN", "LV@LAC": "LAC", "SEA@ARI": "ARI",
    "WAS@DAL": "DAL", "MIA@SF": "SF", "IND@KC": "KC", "NYG@LAR": "LAR",
}
SPIN_W2 = {  # NFL Spin Zone score card
    "DET@BUF": "BUF",
}
BRACKETS_W2 = {  # sportsbrackets.net
    "DET@BUF": "BUF", "CAR@ATL": "ATL", "MIN@CHI": "CHI", "PHI@TEN": "PHI",
    "PIT@NE": "NE", "GB@NYJ": "GB", "CLE@TB": "TB", "NO@BAL": "BAL",
    "CIN@HOU": "CIN", "JAX@DEN": "DEN", "LV@LAC": "LAC", "WAS@DAL": "WAS",
    "SEA@ARI": "ARI", "MIA@SF": "SF", "IND@KC": "KC", "NYG@LAR": "LAR",
}
NAUT_W2 = {  # Sportsnaut
    "DET@BUF": "BUF", "MIA@SF": "SF",
}
HAUS_W2 = {  # The Game Haus ATS leans converted to SU where they picked a side
    "DET@BUF": "DET", "MIA@SF": "SF",
}
VEGAS_SU = _fav(SPREADS)
W1_WINNERS = {  # clubs that already won Week 1, favored when they play
    "DET@BUF": "BUF", "CAR@ATL": "CAR", "NO@BAL": "BAL", "MIN@CHI": "CHI",
    "CIN@HOU": "CIN", "PIT@NE": "PIT", "GB@NYJ": "NYJ", "CLE@TB": "TB",
    "PHI@TEN": "PHI", "JAX@DEN": "JAX", "LV@LAC": "LV", "SEA@ARI": "SEA",
    "WAS@DAL": "WAS", "MIA@SF": "SF", "IND@KC": "KC", "NYG@LAR": "NYG",
}
# Power-rank style: higher club from a short published 1-32 after Week 1.
POWER_W2 = {
    "DET@BUF": "BUF", "CAR@ATL": "ATL", "NO@BAL": "BAL", "MIN@CHI": "CHI",
    "CIN@HOU": "HOU", "PIT@NE": "PIT", "GB@NYJ": "GB", "CLE@TB": "TB",
    "PHI@TEN": "PHI", "JAX@DEN": "JAX", "LV@LAC": "LAC", "SEA@ARI": "SEA",
    "WAS@DAL": "DAL", "MIA@SF": "SF", "IND@KC": "KC", "NYG@LAR": "LAR",
}


def match_maps() -> dict:
    return {
        "Sporting News": SN_W2,
        "CBS Sports": CBS_W2,
        "NFL Spin Zone": SPIN_W2,
        "Sports Brackets": BRACKETS_W2,
        "Sportsnaut": NAUT_W2,
        "The Game Haus": HAUS_W2,
        "Vegas favorite": VEGAS_SU,
        "Week 1 winners": W1_WINNERS,
        "Post-Week 1 power": POWER_W2,
    }


W2_DST_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-2-defense-def-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1931561", "Week 2 DST tiers. 49ers first against Miami."),
    ("Pro Football Network", "https://www.profootballnetwork.com/fantasy-football/defense-rankings-week-2-2026-katz/", "Eagles first at Tennessee. Sep 14."),
    ("ESPN road map", "https://www.espn.com/fantasy/football/story/_/id/49798496", "Week 2 stream order. Seahawks first at Arizona."),
    ("4for4", "https://www.4for4.com/fantasy-football-rankings/def/2026/week2", "Public top 10. Jaguars first at Denver."),
    ("Roto Street Journal", "https://www.rotostreetjournal.com/2026/09/14/best-fantasy-football-week-2-defense-streamers-d-st-49ers-dst-bengals-dst-look-to-impress-again/", "Streamer list. 49ers, Bengals, Buccaneers."),
    ("Vegas implied", "", "Softer implied totals get the higher stream rank."),
    ("Week 1 form", "", "Clubs that already scored on defense or won big."),
]

W2_K_SOURCES = [
    ("RotoBaller", "https://www.rotoballer.com/week-2-kicker-streamers-starters-and-rankings-2026-fantasy-tiers-rankings/1931589", "Aubrey first. Pineiro and Dicker next."),
    ("FantasyPros score", "https://www.fantasypros.com/2026/09/fantasy-football-kicker-rankings-waiver-wire-pickups-week-2-2026/", "Matchup score table. Dicker first, Loop second."),
    ("FantasyPros ECR", "https://www.fantasypros.com/nfl/rankings/k.php", "Week 2 kicker consensus."),
]

MATCH_SOURCES = [
    ("Sporting News", "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-2/830bbe1e7598cf3caadc2a70", "Bill Bender's full SU card. Bills, Steelers, Bengals, Broncos."),
    ("CBS Sports", "https://www.cbssports.com/nfl/news/nfl-week-2-picks-score-predictions/", "John Breech. Bills 38-31. Cardinals over Seattle. Full 16."),
    ("NFL Spin Zone", "https://nflspinzone.com/2026-nfl-picks-score-predictions-for-every-week-2-game-01m2fzpye5s3", "Bills 31-23 over Detroit."),
    ("Sports Brackets", "https://sportsbrackets.net/2026/09/14/2026-nfl-week-2-predictions/", "Full 16-game card. Bengals and Commanders fades."),
    ("Sportsnaut", "https://sportsnaut.com/nfl/nfl-week-2-predictions-2026-nfl-picks-this-week", "Bills 35-31. 49ers 35-17."),
    ("The Game Haus", "https://thegamehaus.com/nfl/nfl-week-2-picks-against-the-spread/2026/09/15/", "Lions ATS. 49ers SU."),
    ("Vegas favorite", "", "Current published spread favorite."),
    ("Week 1 winners", "", "The club that already won, when both sides played."),
    ("Post-Week 1 power", "", "Short 1-32 after the opener. Higher club wins."),
]


def week2_matchups():
    maps = match_maps()
    rows = []
    for slate, (away, home, day, tv, kick) in enumerate(WEEK2_GAMES):
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
        if key == "DET@BUF":
            rows[-1]["final"] = "41-31"
            rows[-1]["day"] = "Thu Final"
    day_ord = {"Wed": 0, "Thu": 1, "Fri": 2, "Sat": 3, "Sun": 4, "Mon": 5}
    rows.sort(key=lambda r: (
        day_ord.get((r["day"] or "").split()[0], 9),
        -r["win_n"],
        -r["n"],
        r["key"],
    ))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


W2_DST_FAQ = [
    ("How is Week 2 DST built?", "Super Aggregate of published Week 2 defense boards. 50% RotoBaller and Pro Football Network, 50% ESPN, 4for4, Roto Street Journal, implied totals, and Week 1 form."),
    ("Is this Top Defenses?", "No. Top Defenses is rest of season. This board is only Week 2."),
]
W2_K_FAQ = [
    ("How is Week 2 Kickers built?", "Super Aggregate of RotoBaller, the FantasyPros matchup table, and FantasyPros ECR."),
    ("Who leads?", "Aubrey, Dicker, and Pineiro sit at the top of the mash."),
]
W2_MATCH_FAQ = [
    ("How are the win picks built?", "Published Week 2 cards: Sporting News, CBS Sports, NFL Spin Zone, Sports Brackets, Sportsnaut, The Game Haus, the market favorite, Week 1 winners, and a short post-opener power board. Unpicked games on a board are skipped."),
    ("Is this a win chance?", "Away and Home are raw vote counts. The pick is the side with more published votes."),
    ("Is this a bet slip?", "It is a mash of public picks and the market. The favorite still wins most games because books and power boards overlap."),
]
