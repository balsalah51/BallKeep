"""Week 1 2026 DST, kicker, and matchup aggregates.

Published boards and pick sheets only. Unranked / unpicked is a skip,
never treated as 999.
"""
from __future__ import annotations

import json
from pathlib import Path

from bk_curve import bk_value
from special_teams import DST_TEAMS, KICKERS, _mean_rows

RANK_DIR = Path(__file__).resolve().parents[1] / "data" / "ranks"

TEAM_ALIAS = {
    "JAC": "JAX", "WSH": "WAS", "LA": "LAR", "LAR": "LAR", "LVR": "LV",
    "GBP": "GB", "KCC": "KC", "NOS": "NO", "SFO": "SF", "NEP": "NE",
    "TAM": "TB", "GNB": "GB", "NWE": "NE", "NOR": "NO",
}

K_BY_TEAM = {team: name for name, team in KICKERS}
K_BY_TEAM.update({
    "IND": "Spencer Shrader",
    "LV": "Matt Gay",
    "WAS": "Matt Gay",
    "NYG": "Graham Gano",
    "CAR": "Ryan Fitzgerald",
    "MIA": "Jason Sanders",
})

WEEK1_KICKERS = list(KICKERS) + [
    ("Spencer Shrader", "IND"),
    ("Matt Gay", "LV"),
    ("Daniel Carlson", "LV"),
    ("Riley Patterson", "CLE"),
    ("Jason Sanders", "MIA"),
    ("Drew Stevens", "WAS"),
    ("Andre Szmyt", "CLE"),
    ("Dominic Zvada", "NYG"),
]


def _team(code: str) -> str:
    return TEAM_ALIAS.get((code or "").upper(), (code or "").upper())


def _load_fp_weekly(stem: str, kind: str) -> dict:
    path = RANK_DIR / f"{stem}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    out = {}
    for row in data.get("players") or []:
        rk = int(row.get("rank") or 0)
        if not rk:
            continue
        if kind == "DST":
            code = _team(row.get("team") or "")
            if code:
                out[code] = rk
        else:
            name = row.get("name") or ""
            if name:
                out[name] = rk
    return out


# ESPN weekly D/ST, Sep 4 2026. Eight named rankers.
# https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273
ESPN_DST_RANKERS = ["Bowen", "Clay", "Cockcroft", "Dopp", "Karabell", "Loza", "Moody", "Yates"]
ESPN_DST_ROWS = [
    ("JAX", [1, 1, 1, 1, 2, 1, 1, 1]),
    ("PIT", [2, 2, 2, 2, 1, 2, 8, 2]),
    ("LAC", [4, 3, 3, 3, 3, 3, 5, 3]),
    ("SEA", [5, 5, 5, 5, 6, 5, 4, 4]),
    ("DET", [3, 4, 4, 4, 5, 4, 14, 5]),
    ("BAL", [6, 6, 6, 6, 4, 6, 12, 10]),
    ("PHI", [7, 9, 7, 9, 7, 9, 7, 8]),
    ("TEN", [8, 7, 9, 7, 8, 7, 11, 7]),
    ("LAR", [11, 10, 8, 10, 10, 10, 2, 11]),
    ("NYJ", [10, 8, 11, 8, 9, 8, 10, 9]),
    ("DEN", [9, 11, 10, 11, 12, 11, 3, 12]),
    ("HOU", [14, 15, 14, 15, 11, 15, 6, 6]),
    ("CHI", [12, 12, 12, 12, 13, 12, 13, 14]),
    ("GB", [16, 13, 13, 13, 14, 13, 15, 17]),
    ("KC", [18, 14, 16, 14, 15, 14, 20, 13]),
    ("DAL", [13, 16, 15, 16, 16, 16, 18, 15]),
    ("LV", [15, 18, 17, 18, 18, 18, 17, 19]),
    ("CLE", [19, 17, 18, 17, 17, 17, 19, None]),
    ("MIN", [None, None, None, None, None, None, 9, 18]),
    ("NE", [17, 19, 19, 19, 19, 19, None, None]),
]


def _espn_maps(rows, labels):
    maps = {lab: {} for lab in labels}
    for key, ranks in rows:
        for lab, rk in zip(labels, ranks):
            if rk:
                maps[lab][key] = rk
    return maps


# Draft Sharks Week 1 DEF, Sep 2. Rank column + consensus projection column.
# https://www.draftsharks.com/weekly-rankings/1/def
DS_W1_DST = {
    "JAX": 1, "LAC": 2, "NYJ": 3, "TEN": 4, "SEA": 5, "DEN": 6, "CHI": 7, "DET": 8,
    "HOU": 9, "PHI": 10, "NE": 11, "MIA": 12, "BAL": 13, "DAL": 14, "TB": 15, "LV": 16,
    "LAR": 17, "PIT": 18, "BUF": 19, "GB": 20, "MIN": 21, "CLE": 22, "IND": 23, "SF": 24,
    "KC": 25,
}
DS_W1_DST_CONS = {
    "JAX": 1, "SEA": 2, "LAC": 3, "PIT": 4, "DET": 5, "TEN": 6, "LAR": 7, "PHI": 8,
    "LV": 9, "BAL": 10, "NYJ": 11, "MIN": 12, "DEN": 13, "HOU": 14, "NE": 15, "GB": 16,
    "DAL": 17, "MIA": 18, "CHI": 19, "BUF": 20, "TB": 21, "SF": 22, "IND": 23, "CLE": 24,
    "KC": 25,
}

# 4for4 Week 1 DEF, Sep 3. Public top 10.
# https://www.4for4.com/fantasy-football-rankings/def/2026/week1
FOUR_W1_DST = {
    "JAX": 1, "LAC": 2, "DET": 3, "SEA": 4, "TEN": 5,
    "LV": 6, "DEN": 7, "PIT": 8, "LAR": 9, "KC": 10,
}

# FantasyPros Week 1 DST projections, Sep 3.
# https://www.fantasypros.com/nfl/projections/dst.php?week=1
FP_PROJ_DST = {
    "JAX": 1, "LAC": 2, "TEN": 3, "PIT": 4, "LV": 5,
    "SEA": 6, "NYJ": 7, "DET": 8, "DEN": 9, "PHI": 10,
}

# RotoWire streaming D/ST Week 1 rankings.
# https://www.rotowire.com/football/article/streaming-defenses-dst-picks-for-week-1-132259
RW_W1_DST = {
    "JAX": 1, "PIT": 2, "LAC": 3, "PHI": 4, "SEA": 5,
    "TEN": 6, "NYJ": 7, "LV": 8, "DET": 9, "LAR": 10,
    "BAL": 11, "HOU": 12, "BUF": 13, "CHI": 14, "MIN": 15,
    "KC": 16, "DEN": 17, "DAL": 18, "ATL": 19, "CAR": 20,
}

# ESPN D/ST road map Week 1, Sep 2026. Short published order.
# https://www.espn.com/fantasy/football/story/_/id/49798496
ESPN_ROAD_DST = {
    "PIT": 1, "JAX": 2, "LAC": 3, "BAL": 4, "DET": 5, "NYJ": 6, "CHI": 7, "TEN": 8,
}

# RotoBaller Week 1 DST, published 2026.
# https://www.rotoballer.com/updated-week-1-fantasy-football-team-defense-def-rankings-2026/1911982
RB_W1_DST = {
    "JAX": 1, "LAC": 2, "HOU": 3, "DEN": 4, "BAL": 5,
    "SEA": 6, "CHI": 7, "TEN": 8, "PIT": 9, "PHI": 10,
    "GB": 11, "MIN": 12, "BUF": 13, "LV": 14, "DET": 15, "LAR": 16,
}

# ESPN weekly kickers, Sep 4 2026. Eight named rankers.
# https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233
ESPN_K_ROWS = [
    ("Brandon Aubrey", [1, 2, 1, 2, 1, 2, 1, 1]),
    ("Cameron Dicker", [2, 1, 2, 1, 2, 1, 2, 2]),
    ("Ka'imi Fairbairn", [3, 3, 3, 3, 3, 3, 3, 3]),
    ("Jason Myers", [6, 5, 4, 5, 6, 5, 7, 4]),
    ("Chris Boswell", [5, 6, 7, 6, 4, 6, 11, 5]),
    ("Cam Little", [8, 7, 5, 7, 7, 7, 4, 6]),
    ("Harrison Mevis", [4, 4, 6, 4, 5, 4, 19, 7]),
    ("Jake Bates", [7, 8, 10, 8, 8, 8, 6, 8]),
    ("Eddy Pineiro", [9, 9, 9, 9, 10, 9, 12, 9]),
    ("Evan McPherson", [11, 11, 15, 11, 12, 11, 10, 12]),
    ("Tyler Loop", [10, 13, 13, 13, 9, 13, 5, None]),
    ("Will Reichard", [15, 14, 8, 14, 13, 14, 9, 10]),
    ("Jake Elliott", [12, 10, 20, 10, 11, 10, 15, 11]),
    ("Harrison Butker", [13, 12, 11, 12, 14, 12, 14, 13]),
    ("Chase McLaughlin", [16, 15, 12, 15, 15, 15, 8, 14]),
    ("Cairo Santos", [14, 16, 14, 16, 16, 16, 13, 15]),
    ("Trey Smack", [18, 17, 19, 17, 18, 17, 17, 16]),
    ("Spencer Shrader", [19, 18, 16, 18, 19, 18, None, 17]),
    ("Matt Gay", [17, 19, None, 19, 20, 19, None, 18]),
    ("Wil Lutz", [None, None, None, None, 17, None, 18, None]),
]

# FantasyPros Week 1 kicker article, Andrew Swanson, Sep 2.
# https://www.fantasypros.com/2026/09/fantasy-football-kicker-rankings-start-sit-advice-week-1-2026/
SWANSON_K = {
    "Cameron Dicker": 1, "Jason Myers": 2, "Tyler Loop": 3, "Ka'imi Fairbairn": 4,
    "Brandon Aubrey": 5, "Cam Little": 6, "Andy Borregales": 7, "Jake Bates": 8,
    "Chris Boswell": 9, "Trey Smack": 10, "Wil Lutz": 11, "Cairo Santos": 12,
    "Chase McLaughlin": 13, "Harrison Mevis": 18,
}

# FantasyPros Week 1 K projections, Sep 2.
# https://www.fantasypros.com/nfl/projections/k.php
FP_PROJ_K = {
    "Cameron Dicker": 1, "Brandon Aubrey": 2, "Jake Bates": 3, "Harrison Mevis": 4,
    "Jason Myers": 5, "Ka'imi Fairbairn": 6, "Cam Little": 7, "Tyler Loop": 8,
    "Evan McPherson": 9, "Spencer Shrader": 10,
}

# Draft Sharks Week 1 K, Sep 2. Team slots mapped to the named kicker.
# https://www.draftsharks.com/weekly-rankings/k
DS_W1_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Cam Little": 4,
    "Jason Myers": 5, "Jake Bates": 6, "Harrison Mevis": 7, "Tyler Loop": 8,
    "Eddy Pineiro": 9, "Cairo Santos": 10,
}

# 4for4 Week 1 K, public top 10.
# https://www.4for4.com/fantasy-football-rankings/k/2026/week1
FOUR_W1_K = {
    "Cameron Dicker": 1, "Jake Bates": 2, "Evan McPherson": 3, "Harrison Mevis": 4,
    "Cam Little": 5, "Tyler Loop": 6, "Ka'imi Fairbairn": 7, "Brandon Aubrey": 8,
    "Jake Elliott": 9, "Cairo Santos": 10,
}

# RotoBaller Week 1 K, published 2026.
# https://www.rotoballer.com/week-1-fantasy-football-kicker-k-updated-rankings-2026/1922819
RB_W1_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Cam Little": 4,
    "Jake Bates": 5, "Tyler Loop": 6, "Evan McPherson": 7, "Chase McLaughlin": 8,
    "Jason Myers": 9, "Harrison Mevis": 10, "Cairo Santos": 11, "Eddy Pineiro": 12,
    "Spencer Shrader": 13, "Trey Smack": 14, "Will Reichard": 15, "Daniel Carlson": 16,
    "Wil Lutz": 17, "Chris Boswell": 18, "Jake Elliott": 19, "Tyler Bass": 20,
    "Harrison Butker": 21, "Andy Borregales": 22, "Riley Patterson": 23, "Joey Slye": 24,
    "Matt Gay": 25, "Ryan Fitzgerald": 26, "Nick Folk": 27, "Drew Stevens": 28,
    "Jason Sanders": 29, "Chad Ryland": 30,
}

# CBS Sports weekly K, Sep 5 2026. Named expert columns on the public board.
# https://www.cbssports.com/fantasy/football/rankings/standard/K/
CBS_JAMEY_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Jason Myers": 3, "Cam Little": 4,
    "Cameron Dicker": 5, "Eddy Pineiro": 6, "Harrison Butker": 7, "Evan McPherson": 8,
    "Tyler Loop": 9, "Andy Borregales": 10, "Harrison Mevis": 11, "Chase McLaughlin": 12,
    "Cairo Santos": 13, "Will Reichard": 14, "Wil Lutz": 15, "Jake Bates": 16,
    "Chris Boswell": 17, "Jake Elliott": 18, "Tyler Bass": 19, "Trey Smack": 20,
    "Dominic Zvada": 21, "Spencer Shrader": 22, "Daniel Carlson": 23, "Chad Ryland": 24,
    "Drew Stevens": 25, "Ryan Fitzgerald": 26, "Matt Gay": 27, "Nick Folk": 28,
    "Blake Grupe": 29, "Joey Slye": 30, "Andre Szmyt": 31, "Riley Patterson": 32,
}
CBS_DAVE_K = {
    "Ka'imi Fairbairn": 1, "Brandon Aubrey": 2, "Jason Myers": 3, "Cameron Dicker": 4,
    "Evan McPherson": 5, "Cam Little": 6, "Eddy Pineiro": 7, "Jake Bates": 8,
    "Will Reichard": 9, "Chase McLaughlin": 10, "Harrison Mevis": 11, "Andy Borregales": 12,
    "Spencer Shrader": 13, "Matt Gay": 14, "Cairo Santos": 15, "Tyler Loop": 16,
    "Chris Boswell": 17, "Harrison Butker": 18, "Wil Lutz": 19, "Tyler Bass": 20,
    "Chad Ryland": 21, "Trey Smack": 22, "Ryan Fitzgerald": 23, "Joey Slye": 24,
    "Dominic Zvada": 25, "Jake Elliott": 26, "Nick Folk": 27, "Riley Patterson": 28,
    "Drew Stevens": 29, "Blake Grupe": 30, "Andre Szmyt": 31, "Daniel Carlson": 32,
}


def week1_dst_maps():
    maps = _espn_maps(ESPN_DST_ROWS, ESPN_DST_RANKERS)
    maps["Draft Sharks"] = DS_W1_DST
    maps["Draft Sharks consensus"] = DS_W1_DST_CONS
    maps["4for4"] = FOUR_W1_DST
    maps["FantasyPros ECR"] = _load_fp_weekly("week1-fp_dst", "DST") or {
        "JAX": 1, "LAC": 2, "HOU": 3, "LAR": 4, "PHI": 5, "DEN": 6, "SEA": 7,
    }
    maps["FantasyPros projections"] = FP_PROJ_DST
    maps["RotoWire"] = RW_W1_DST
    maps["ESPN road map"] = ESPN_ROAD_DST
    maps["RotoBaller"] = RB_W1_DST
    return maps


W1_DST_SOURCES = [
    ("Matt Bowen DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4. Jaguars first."),
    ("Mike Clay DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4. Jaguars first."),
    ("Tristan H. Cockcroft DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4."),
    ("Daniel Dopp DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4."),
    ("Eric Karabell DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4. Steelers first."),
    ("Liz Loza DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4."),
    ("Eric Moody DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4. Rams second."),
    ("Field Yates DST", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273", "ESPN weekly ranker, Sep 4."),
    ("Draft Sharks Week 1 DEF", "https://www.draftsharks.com/weekly-rankings/1/def", "DS projection rank, Sep 2. Jacksonville first."),
    ("Draft Sharks consensus DEF", "https://www.draftsharks.com/weekly-rankings/1/def", "Consensus projection column, Sep 2. Jacksonville first."),
    ("4for4 Week 1 DEF", "https://www.4for4.com/fantasy-football-rankings/def/2026/week1", "Public top 10, Sep 3. Jaguars first."),
    ("FantasyPros Week 1 DST ECR", "https://www.fantasypros.com/nfl/rankings/dst.php", "Weekly expert consensus, Sep 4. Jaguars first."),
    ("FantasyPros Week 1 DST projections", "https://www.fantasypros.com/nfl/projections/dst.php?week=1", "Consensus projections, Sep 3. Jaguars first."),
    ("RotoWire Week 1 DST", "https://www.rotowire.com/football/article/streaming-defenses-dst-picks-for-week-1-132259", "Streaming board. Jaguars first, Steelers second."),
    ("ESPN D/ST road map", "https://www.espn.com/fantasy/football/story/_/id/49798496", "Week 1 streamer order. Steelers first. Short list."),
    ("RotoBaller Week 1 DST", "https://www.rotoballer.com/updated-week-1-fantasy-football-team-defense-def-rankings-2026/1911982", "Week 1 team defense board. Jaguars first."),
]


def week1_k_maps():
    maps = _espn_maps(ESPN_K_ROWS, ESPN_DST_RANKERS)
    maps["FantasyPros ECR"] = _load_fp_weekly("week1-fp_k", "K")
    maps["FantasyPros projections"] = FP_PROJ_K
    maps["Andrew Swanson"] = SWANSON_K
    maps["Draft Sharks"] = DS_W1_K
    maps["4for4"] = FOUR_W1_K
    maps["RotoBaller"] = RB_W1_K
    maps["CBS Jamey Eisenberg"] = CBS_JAMEY_K
    maps["CBS Dave Richard"] = CBS_DAVE_K
    return maps


W1_K_SOURCES = [
    ("Matt Bowen K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4. Aubrey first."),
    ("Mike Clay K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4. Dicker first."),
    ("Tristan H. Cockcroft K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4."),
    ("Daniel Dopp K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4. Dicker first."),
    ("Eric Karabell K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4."),
    ("Liz Loza K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4. Dicker first."),
    ("Eric Moody K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4."),
    ("Field Yates K", "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233", "ESPN weekly ranker, Sep 4."),
    ("FantasyPros Week 1 K ECR", "https://www.fantasypros.com/nfl/rankings/k.php", "Weekly expert consensus, Sep 5. Aubrey first."),
    ("FantasyPros Week 1 K projections", "https://www.fantasypros.com/nfl/projections/k.php", "Consensus projections, Sep 2. Dicker first."),
    ("Andrew Swanson K", "https://www.fantasypros.com/2026/09/fantasy-football-kicker-rankings-start-sit-advice-week-1-2026/", "FantasyPros Week 1 start/sit, Sep 2. Dicker first."),
    ("Draft Sharks Week 1 K", "https://www.draftsharks.com/weekly-rankings/k", "Weekly board, Sep 2. Dallas / Aubrey first."),
    ("4for4 Week 1 K", "https://www.4for4.com/fantasy-football-rankings/k/2026/week1", "Public top 10. Dicker first."),
    ("RotoBaller Week 1 K", "https://www.rotoballer.com/week-1-fantasy-football-kicker-k-updated-rankings-2026/1922819", "Week 1 kicker board. Aubrey first."),
    ("CBS Jamey Eisenberg K", "https://www.cbssports.com/fantasy/football/rankings/standard/K/jamey-eisenberg/", "Weekly K column, Sep 5. Aubrey first, Myers third."),
    ("CBS Dave Richard K", "https://www.cbssports.com/fantasy/football/rankings/standard/K/dave-richard/", "Weekly K column, Sep 5. Fairbairn first, Aubrey second."),
]


def week1_dst_board():
    return _mean_rows(DST_TEAMS, week1_dst_maps(), "DST")


def week1_kicker_board():
    return _mean_rows(WEEK1_KICKERS, week1_k_maps(), "K")


# Week 1 games: away, home. Neutral Melbourne is SF vs LAR.
WEEK1_GAMES = [
    ("NE", "SEA", "Wed 9/9", "NBC"),
    ("SF", "LAR", "Thu 9/10", "Netflix"),
    ("CHI", "CAR", "Sun 9/13", "FOX"),
    ("TB", "CIN", "Sun 9/13", "FOX"),
    ("NO", "DET", "Sun 9/13", "FOX"),
    ("BUF", "HOU", "Sun 9/13", "CBS"),
    ("BAL", "IND", "Sun 9/13", "CBS"),
    ("CLE", "JAX", "Sun 9/13", "CBS"),
    ("ATL", "PIT", "Sun 9/13", "CBS"),
    ("NYJ", "TEN", "Sun 9/13", "CBS"),
    ("ARI", "LAC", "Sun 9/13", "CBS"),
    ("MIA", "LV", "Sun 9/13", "CBS"),
    ("GB", "MIN", "Sun 9/13", "FOX"),
    ("WAS", "PHI", "Sun 9/13", "FOX"),
    ("DAL", "NYG", "Sun 9/13", "NBC"),
    ("DEN", "KC", "Mon 9/14", "ABC/ESPN"),
]

# Current consensus spreads from CBS SportsLine, early Sep 2026.
VEGAS = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "CHI@CAR": "CHI", "TB@CIN": "CIN",
    "NO@DET": "DET", "BUF@HOU": "BUF", "BAL@IND": "BAL", "CLE@JAX": "JAX",
    "ATL@PIT": "PIT", "NYJ@TEN": "TEN", "ARI@LAC": "LAC", "MIA@LV": "LV",
    "GB@MIN": "MIN", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "KC",
}
SPREADS = {
    "NE@SEA": "SEA -3.5", "SF@LAR": "LAR -3.5", "CHI@CAR": "CHI -2.5", "TB@CIN": "CIN -3.5",
    "NO@DET": "DET -7", "BUF@HOU": "BUF -1.5", "BAL@IND": "BAL -3.5", "CLE@JAX": "JAX -7.5",
    "ATL@PIT": "PIT -3", "NYJ@TEN": "TEN -1.5", "ARI@LAC": "LAC -10.5", "MIA@LV": "LV -3.5",
    "GB@MIN": "MIN -1.5", "WAS@PHI": "PHI -4.5", "DAL@NYG": "DAL -2.5", "DEN@KC": "KC -2.5",
}

# CBS Sports straight-up expert grid, Week 1 2026.
# https://www.cbssports.com/nfl/picks/experts/straight-up/1/
CBS_DUBIN = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "ATL@PIT": "PIT", "BAL@IND": "BAL",
    "BUF@HOU": "HOU", "CHI@CAR": "CHI", "CLE@JAX": "JAX", "NO@DET": "DET",
    "NYJ@TEN": "TEN", "TB@CIN": "CIN", "ARI@LAC": "LAC", "GB@MIN": "GB",
    "MIA@LV": "LV", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "DEN",
}
CBS_WILSON = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "ATL@PIT": "PIT", "BAL@IND": "BAL",
    "BUF@HOU": "BUF", "CHI@CAR": "CHI", "CLE@JAX": "JAX", "NO@DET": "DET",
    "NYJ@TEN": "TEN", "TB@CIN": "CIN", "ARI@LAC": "LAC", "GB@MIN": "MIN",
    "MIA@LV": "LV", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "KC",
}
CBS_BREECH = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "ATL@PIT": "PIT", "BAL@IND": "BAL",
    "BUF@HOU": "HOU", "CHI@CAR": "CHI", "CLE@JAX": "JAX", "NO@DET": "DET",
    "NYJ@TEN": "TEN", "TB@CIN": "CIN", "ARI@LAC": "LAC", "GB@MIN": "GB",
    "MIA@LV": "LV", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "DEN",
}
CBS_SULLIVAN = {
    "NE@SEA": "SEA", "SF@LAR": "SF", "ATL@PIT": "PIT", "BAL@IND": "BAL",
    "BUF@HOU": "HOU", "CHI@CAR": "CHI", "CLE@JAX": "JAX", "NO@DET": "DET",
    "NYJ@TEN": "NYJ", "TB@CIN": "CIN", "ARI@LAC": "ARI", "GB@MIN": "MIN",
    "MIA@LV": "LV", "WAS@PHI": "PHI", "DAL@NYG": "NYG", "DEN@KC": "DEN",
}

# BUSR Week 1 score predictions, Sep 1 2026.
# https://www.busr.ag/news/nfl/nfl-picks-predictions-for-week-1-games
BUSR = {
    "NE@SEA": "SEA", "SF@LAR": "SF", "CHI@CAR": "CHI", "TB@CIN": "CIN",
    "BAL@IND": "BAL", "CLE@JAX": "JAX", "ATL@PIT": "PIT", "NYJ@TEN": "NYJ",
    "NO@DET": "DET", "BUF@HOU": "BUF", "ARI@LAC": "LAC", "GB@MIN": "GB",
    "MIA@LV": "MIA", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "KC",
}

# Action Network published moneylines, Sep 5 2026. Favorite is the pick.
AN_CONSENSUS = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "NYJ@TEN": "TEN", "TB@CIN": "CIN",
    "CLE@JAX": "JAX", "ATL@PIT": "PIT", "CHI@CAR": "CHI", "NO@DET": "DET",
    "BAL@IND": "BAL", "BUF@HOU": "BUF", "MIA@LV": "LV", "ARI@LAC": "LAC",
    "WAS@PHI": "PHI", "GB@MIN": "MIN", "DAL@NYG": "DAL", "DEN@KC": "KC",
}
AN_OPEN = dict(AN_CONSENSUS, **{"GB@MIN": "GB"})
AN_DK = dict(AN_CONSENSUS)
AN_CAESARS = dict(AN_CONSENSUS)
AN_FD = dict(AN_CONSENSUS)
AN_BETRIVERS = dict(AN_CONSENSUS)
AN_MGM = dict(AN_CONSENSUS, **{"GB@MIN": "GB"})


def _from_power(order: list[str]) -> dict:
    rank = {abbr: i for i, abbr in enumerate(order, 1)}
    out = {}
    for away, home, _day, _tv in WEEK1_GAMES:
        key = f"{away}@{home}"
        ra, rh = rank.get(away), rank.get(home)
        if ra is None or rh is None:
            continue
        if ra == rh:
            continue
        out[key] = away if ra < rh else home
    return out


# ESPN preseason power ranks, Sep 2026 (final cuts).
# https://www.espn.com/nfl/story/_/id/49754534
ESPN_PR = _from_power([
    "LAR", "SEA", "BUF", "DEN", "PHI", "NE", "GB", "BAL", "SF", "HOU",
    "DET", "CHI", "KC", "LAC", "DAL", "CIN", "JAX", "TB", "IND", "WAS",
    "PIT", "MIN", "CAR", "NYG", "NO", "ATL", "LV", "TEN", "NYJ", "ARI",
    "CLE", "MIA",
])

# Sportsnaut after-preseason power ranks, 2026.
# https://sportsnaut.com/nfl/2026-nfl-power-rankings-after-preseason
SPORTSNAUT_PR = _from_power([
    "LAR", "SEA", "HOU", "BAL", "PHI", "BUF", "DEN", "NE", "DET", "GB",
    "LAC", "DAL", "SF", "JAX", "CIN", "CHI", "KC", "TB", "MIN", "PIT",
    "NO", "NYG", "IND", "CAR", "LV", "WAS", "TEN", "ATL", "ARI", "NYJ",
    "MIA", "CLE",
])

# Windy City Gridiron Week 1 power ranks, 2026.
# https://www.windycitygridiron.com/chicago-bears-power-rankings/121936/nfl-week-1-power-rankings-biggest-question-each-team-bears-rams-seahawks-ravens
WCG_PR = _from_power([
    "SEA", "LAR", "DEN", "BUF", "NE", "SF", "BAL", "HOU", "CHI", "KC",
    "DET", "PHI", "JAX", "GB", "LAC", "CAR", "DAL", "CIN", "PIT", "IND",
    "TB", "MIN", "WAS", "NYG", "NO", "ATL", "LV", "TEN", "CLE", "ARI",
    "MIA", "NYJ",
])

# CBS opening DraftKings line, May 15 2026 (moneyline favorite).
# https://www.cbssports.com/nfl/news/early-odds-picks-for-every-week-1-nfl-matchup/
CBS_OPENING = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "NO@DET": "DET", "BUF@HOU": "BUF",
    "BAL@IND": "BAL", "CHI@CAR": "CHI", "TB@CIN": "CIN", "ATL@PIT": "PIT",
    "NYJ@TEN": "TEN", "CLE@JAX": "JAX", "WAS@PHI": "PHI", "ARI@LAC": "LAC",
    "MIA@LV": "LV", "GB@MIN": "GB", "DAL@NYG": "DAL", "DEN@KC": "KC",
}

# Eric Cohen / SportsLine published SU lean: Texans over Bills. Other games skipped.
# https://www.sportsline.com/insiders/nfl-week-1-score-predictions-expert-reveals-game-picks-for-the-2026-opening-week/
COHEN = {"BUF@HOU": "HOU"}

# OddsTrader published ML leans, Sep 3. Short list.
# https://www.oddstrader.com/betting/nfl-week-1-picks-best-value-underdog-bets-for-opening-week/
ODDSTRADER = {"SF@LAR": "SF", "NO@DET": "NO"}

# CBS Tyler Sullivan May ATS article, SU only where he picked a side to win
# (favorite minus). Dogs he liked ATS are skipped.
# https://www.cbssports.com/nfl/news/early-odds-picks-for-every-week-1-nfl-matchup/
SULLIVAN_MAY = {
    "NE@SEA": "SEA", "NO@DET": "DET", "BUF@HOU": "BUF", "BAL@IND": "BAL",
    "TB@CIN": "CIN", "NYJ@TEN": "TEN", "CLE@JAX": "JAX", "ARI@LAC": "LAC",
    "MIA@LV": "LV", "DAL@NYG": "DAL",
}

# SportsLine model public leans: Jaguars and Eagles cover, which is a SU win
# at those numbers. Other games skipped.
# https://www.cbssports.com/betting/news/week-1-nfl-2026-odds-lines-spreads-best-bets-predictions-picks/
SPORTSLINE_MODEL = {"CLE@JAX": "JAX", "WAS@PHI": "PHI"}

# Sharp Football Analysis training-camp 1-32.
# https://www.sharpfootballanalysis.com/analysis/nfl-power-rankings/
SHARP_PR = _from_power([
    "LAR", "BUF", "SEA", "GB", "LAC", "DEN", "HOU", "BAL", "PHI", "NE",
    "CIN", "SF", "KC", "DET", "JAX", "DAL", "CHI", "TB", "MIN", "PIT",
    "IND", "CAR", "WAS", "NYG", "NO", "TEN", "NYJ", "ATL", "LV", "ARI",
    "CLE", "MIA",
])

# NFL Spin Zone via Yardbarker, Sep 1 after roster cuts.
# https://www.yardbarker.com/nfl/articles/nfl_power_rankings_updated_league_rankings_after_roster_cuts/s1_17819_44246353
YARDBARKER_PR = _from_power([
    "LAR", "SEA", "DEN", "BUF", "HOU", "NE", "CHI", "GB", "PHI", "DET",
    "BAL", "JAX", "LAC", "SF", "DAL", "IND", "KC", "CIN", "TB", "PIT",
    "NYG", "CAR", "NO", "MIN", "WAS", "ATL", "NYJ", "TEN", "LV", "ARI",
    "MIA", "CLE",
])

# CBS Sports roster rankings, Jordan Dajani and Tyler Sullivan, Aug 25.
# https://www.cbssports.com/nfl/news/2026-nfl-roster-rankings-rams-seahawks/
# https://www.cbssports.com/nfl/news/2026-nfl-roster-rankings-32-17/
CBS_ROSTER_PR = _from_power([
    "LAR", "SEA", "PHI", "DEN", "BAL", "NE", "BUF", "HOU", "DET", "SF",
    "KC", "CIN", "DAL", "JAX", "LAC", "GB", "CHI", "MIN", "PIT", "TB",
    "IND", "WAS", "NYG", "CAR", "NO", "NYJ", "LV", "TEN", "ATL", "CLE",
    "ARI", "MIA",
])

# TeamRankings predictive model, Sep 5. Higher rating wins.
# https://www.teamrankings.com/nfl/ranking/predictive-by-other/
TR_PRED = _from_power([
    "LAR", "SEA", "BUF", "BAL", "HOU", "LAC", "KC", "DET", "GB", "DEN",
    "PHI", "SF", "NE", "CIN", "CHI", "DAL", "JAX", "TB", "MIN", "PIT",
    "WAS", "IND", "NYG", "NO", "CAR", "ATL", "LV", "TEN", "CLE", "NYJ",
    "ARI", "MIA",
])

# FOX Sports DraftKings sheet, Sep 3. Moneyline favorite.
# https://www.foxsports.com/stories/nfl/2026-nfl-odds-week-1-lines-spreads-all-16-games
FOX_DK = {
    "NE@SEA": "SEA", "SF@LAR": "LAR", "CHI@CAR": "CHI", "TB@CIN": "CIN",
    "NO@DET": "DET", "BUF@HOU": "BUF", "BAL@IND": "BAL", "CLE@JAX": "JAX",
    "ATL@PIT": "PIT", "NYJ@TEN": "TEN", "ARI@LAC": "LAC", "MIA@LV": "LV",
    "GB@MIN": "MIN", "WAS@PHI": "PHI", "DAL@NYG": "DAL", "DEN@KC": "KC",
}


def match_maps():
    return {
        "CBS Jared Dubin": CBS_DUBIN,
        "CBS Ryan Wilson": CBS_WILSON,
        "CBS John Breech": CBS_BREECH,
        "CBS Tyler Sullivan": CBS_SULLIVAN,
        "BUSR": BUSR,
        "Vegas consensus": VEGAS,
        "Action Consensus ML": AN_CONSENSUS,
        "Open ML": AN_OPEN,
        "DraftKings NJ ML": AN_DK,
        "Caesars NV ML": AN_CAESARS,
        "FanDuel NJ ML": AN_FD,
        "BetRivers NJ ML": AN_BETRIVERS,
        "BetMGM NJ ML": AN_MGM,
        "ESPN power ranks": ESPN_PR,
        "Sportsnaut power ranks": SPORTSNAUT_PR,
        "Windy City Gridiron": WCG_PR,
        "CBS opening DK line": CBS_OPENING,
        "Eric Cohen / SportsLine": COHEN,
        "OddsTrader": ODDSTRADER,
        "Tyler Sullivan May": SULLIVAN_MAY,
        "SportsLine model": SPORTSLINE_MODEL,
        "Sharp Football": SHARP_PR,
        "NFL Spin Zone": YARDBARKER_PR,
        "CBS roster ranks": CBS_ROSTER_PR,
        "TeamRankings predictive": TR_PRED,
        "FOX Sports DK": FOX_DK,
    }


MATCH_SOURCES = [
    ("CBS Jared Dubin", "https://www.cbssports.com/nfl/picks/experts/straight-up/1/", "Straight-up Week 1 grid, Sep 5. Texans and Packers fades."),
    ("CBS Ryan Wilson", "https://www.cbssports.com/nfl/picks/experts/straight-up/1/", "Straight-up Week 1 grid, Sep 5. Closest to the market."),
    ("CBS John Breech", "https://www.cbssports.com/nfl/picks/experts/straight-up/1/", "Straight-up Week 1 grid, Sep 5. Texans and Packers."),
    ("CBS Tyler Sullivan", "https://www.cbssports.com/nfl/picks/experts/straight-up/1/", "Straight-up Week 1 grid, Sep 5. 49ers, Jets, Cardinals, Giants, Broncos."),
    ("BUSR", "https://www.busr.ag/news/nfl/nfl-picks-predictions-for-week-1-games", "Score predictions, Sep 1. 49ers, Jets, Packers, Dolphins."),
    ("Vegas consensus", "https://www.cbssports.com/betting/news/week-1-nfl-2026-odds-lines-spreads-best-bets-predictions-picks/", "Current CBS SportsLine market favorite, early Sep."),
    ("Action Consensus ML", "https://www.actionnetwork.com/nfl/picks", "Published moneyline favorite, Sep 5."),
    ("Open ML", "https://www.actionnetwork.com/nfl/picks", "Open sportsbook moneyline favorite. Packers over Minnesota."),
    ("DraftKings NJ ML", "https://www.actionnetwork.com/nfl/picks", "DraftKings NJ moneyline favorite, Sep 5."),
    ("Caesars NV ML", "https://www.actionnetwork.com/nfl/picks", "Caesars NV moneyline favorite, Sep 5."),
    ("FanDuel NJ ML", "https://www.actionnetwork.com/nfl/picks", "FanDuel NJ moneyline favorite, Sep 5."),
    ("BetRivers NJ ML", "https://www.actionnetwork.com/nfl/picks", "BetRivers NJ moneyline favorite, Sep 5."),
    ("BetMGM NJ ML", "https://www.actionnetwork.com/nfl/picks", "BetMGM NJ moneyline favorite. Packers over Minnesota."),
    ("ESPN power ranks", "https://www.espn.com/nfl/story/_/id/49754534", "Preseason 1-32 after final cuts. Higher club wins."),
    ("Sportsnaut power ranks", "https://sportsnaut.com/nfl/2026-nfl-power-rankings-after-preseason", "After-preseason 1-32. Higher club wins."),
    ("Windy City Gridiron", "https://www.windycitygridiron.com/chicago-bears-power-rankings/121936/nfl-week-1-power-rankings-biggest-question-each-team-bears-rams-seahawks-ravens", "Week 1 1-32. Seattle first. Higher club wins."),
    ("CBS opening DK line", "https://www.cbssports.com/nfl/news/early-odds-picks-for-every-week-1-nfl-matchup/", "May 15 DraftKings openers. Packers were the favorite."),
    ("Eric Cohen / SportsLine", "https://www.sportsline.com/insiders/nfl-week-1-score-predictions-expert-reveals-game-picks-for-the-2026-opening-week/", "Published Texans over Bills. Other games skipped."),
    ("OddsTrader", "https://www.oddstrader.com/betting/nfl-week-1-picks-best-value-underdog-bets-for-opening-week/", "Published 49ers and Saints ML leans, Sep 3. Other games skipped."),
    ("Tyler Sullivan May", "https://www.cbssports.com/nfl/news/early-odds-picks-for-every-week-1-nfl-matchup/", "May 15 SU leans where he picked a favorite to win. Dog ATS plays skipped."),
    ("SportsLine model", "https://www.cbssports.com/betting/news/week-1-nfl-2026-odds-lines-spreads-best-bets-predictions-picks/", "Public model leans: Jaguars and Eagles cover. Other games skipped."),
    ("Sharp Football", "https://www.sharpfootballanalysis.com/analysis/nfl-power-rankings/", "Training-camp 1-32. Bills second. Higher club wins."),
    ("NFL Spin Zone", "https://www.yardbarker.com/nfl/articles/nfl_power_rankings_updated_league_rankings_after_roster_cuts/s1_17819_44246353", "After cuts, Sep 1. Denver third. Higher club wins."),
    ("CBS roster ranks", "https://www.cbssports.com/nfl/news/2026-nfl-roster-rankings-rams-seahawks/", "Dajani and Sullivan on-paper 1-32, Aug 25. Eagles third."),
    ("TeamRankings predictive", "https://www.teamrankings.com/nfl/ranking/predictive-by-other/", "Model 1-32, Sep 5. Rams, Seattle, Buffalo. Higher club wins."),
    ("FOX Sports DK", "https://www.foxsports.com/stories/nfl/2026-nfl-odds-week-1-lines-spreads-all-16-games", "DraftKings favorites printed Sep 3."),
]

assert len(W1_DST_SOURCES) >= 16
assert len(W1_K_SOURCES) >= 16
assert len(MATCH_SOURCES) == 26


def week1_matchups():
    maps = match_maps()
    rows = []
    for away, home, day, tv in WEEK1_GAMES:
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
        n = len(picks)
        win_n = counts[winner]
        rows.append({
            "key": key,
            "away": away,
            "home": home,
            "day": day,
            "tv": tv,
            "spread": SPREADS.get(key, ""),
            "pick": winner,
            "n": n,
            "win_n": win_n,
            "win_pct": round(100.0 * win_n / n, 1),
            "away_n": counts.get(away, 0),
            "home_n": counts.get(home, 0),
            "picks": picks,
        })
    rows.sort(key=lambda r: (-r["win_pct"], -r["n"], r["day"], r["key"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows
