"""2026 redraft DST and kicker aggregates.

Published boards only. Unranked names are skipped, never treated as 999.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_curve import bk_value  # noqa: E402


# Full team names match the football schedule board. FantasyPros writes JAC; we use JAX.
DST_TEAMS = [
    ("Arizona Cardinals", "ARI"), ("Atlanta Falcons", "ATL"), ("Baltimore Ravens", "BAL"),
    ("Buffalo Bills", "BUF"), ("Carolina Panthers", "CAR"), ("Chicago Bears", "CHI"),
    ("Cincinnati Bengals", "CIN"), ("Cleveland Browns", "CLE"), ("Dallas Cowboys", "DAL"),
    ("Denver Broncos", "DEN"), ("Detroit Lions", "DET"), ("Green Bay Packers", "GB"),
    ("Houston Texans", "HOU"), ("Indianapolis Colts", "IND"), ("Jacksonville Jaguars", "JAX"),
    ("Kansas City Chiefs", "KC"), ("Las Vegas Raiders", "LV"), ("Los Angeles Chargers", "LAC"),
    ("Los Angeles Rams", "LAR"), ("Miami Dolphins", "MIA"), ("Minnesota Vikings", "MIN"),
    ("New England Patriots", "NE"), ("New Orleans Saints", "NO"), ("New York Giants", "NYG"),
    ("New York Jets", "NYJ"), ("Philadelphia Eagles", "PHI"), ("Pittsburgh Steelers", "PIT"),
    ("San Francisco 49ers", "SF"), ("Seattle Seahawks", "SEA"), ("Tampa Bay Buccaneers", "TB"),
    ("Tennessee Titans", "TEN"), ("Washington Commanders", "WAS"),
]

# FantasyPros DST ECR, Aug 2026 draft article (32 clubs).
FP_DST = {
    "HOU": 1, "DEN": 2, "LAR": 3, "SEA": 4, "PHI": 5, "NE": 6, "PIT": 7, "MIN": 8,
    "JAX": 9, "LAC": 10, "BAL": 11, "KC": 12, "GB": 13, "DET": 14, "BUF": 15, "CLE": 16,
    "NO": 17, "IND": 18, "SF": 19, "ATL": 20, "CHI": 21, "DAL": 22, "NYG": 23, "TB": 24,
    "CAR": 25, "TEN": 26, "CIN": 27, "WAS": 28, "MIA": 29, "LV": 30, "NYJ": 31, "ARI": 32,
}
# FantasyPros experts, Aug 12-27. Top 12 published; rest skipped.
BROWN_DST = {
    "HOU": 1, "LAR": 2, "DEN": 3, "SEA": 4, "PHI": 5, "PIT": 6, "JAX": 9, "NE": 11,
    "BAL": 12, "MIN": 16, "DET": 17, "LAC": 19,
}
ERICKSON_DST = {
    "HOU": 1, "SEA": 2, "LAR": 3, "LAC": 4, "PHI": 5, "DEN": 6, "BAL": 7, "DET": 8,
    "MIN": 9, "JAX": 11, "PIT": 12, "NE": 15,
}
FITZ_DST = {
    "SEA": 1, "HOU": 2, "DEN": 3, "LAR": 4, "PHI": 5, "MIN": 6, "JAX": 7, "NE": 8,
    "LAC": 9, "PIT": 11, "DET": 13, "BAL": 16,
}
# NBC Sports tiered DST, Aug 19.
NBC_DST = {
    "SEA": 1, "DEN": 2, "HOU": 3, "LAC": 4, "LAR": 5, "MIN": 6, "JAX": 7, "NE": 8,
    "PHI": 9, "BAL": 10, "PIT": 11, "BUF": 12, "DET": 13, "CLE": 14, "NO": 15, "KC": 16,
    "GB": 17, "ATL": 18, "TB": 19, "SF": 20, "CHI": 21, "IND": 22, "NYG": 23, "MIA": 24,
    "LV": 25, "CAR": 26, "TEN": 27, "DAL": 28, "CIN": 29, "NYJ": 30, "WAS": 31, "ARI": 32,
}
# STACKED 2026 DST, updated Aug 31. Full 32. https://www.stackedfantasy.com/nfl/draft-guide/dst
STACKED_DST = {
    "HOU": 1, "DEN": 2, "LAR": 3, "SEA": 4, "PHI": 5, "NE": 6, "JAX": 7, "PIT": 8,
    "BAL": 9, "LAC": 10, "MIN": 11, "GB": 12, "KC": 13, "CLE": 14, "DET": 15, "BUF": 16,
    "SF": 17, "NO": 18, "DAL": 19, "IND": 20, "ATL": 21, "CAR": 22, "CHI": 23, "CIN": 24,
    "NYG": 25, "TB": 26, "TEN": 27, "MIA": 28, "WAS": 29, "NYJ": 30, "ARI": 31, "LV": 32,
}
# Draft Sharks 2026 DST. Partial board: skip unranked. https://www.draftsharks.com/rankings/def
DS_DST = {
    "HOU": 1, "DEN": 2, "SEA": 3, "GB": 4, "BAL": 5, "PIT": 6, "MIN": 7, "NE": 8,
    "PHI": 9, "LAR": 10, "DET": 11, "NYG": 12, "LAC": 13, "JAX": 14, "CHI": 15, "BUF": 16,
    "CLE": 17, "IND": 21, "NO": 23,
}
# CBS via 4for4, top 10 published Aug 30. https://www.4for4.com/fantasy-football-rankings/cbs/def/2026
CBS_DST = {
    "LAR": 1, "HOU": 2, "SEA": 3, "DEN": 4, "PIT": 5,
    "JAX": 6, "MIN": 7, "NE": 8, "BAL": 9, "PHI": 10,
}

DST_SOURCES = [
    ("FantasyPros DST ECR", "https://www.fantasypros.com/2026/08/fantasy-football-draft-rankings-targets-defenses-d-st-picks/", "Expert consensus, Aug 2026. All 32 clubs."),
    ("NBC Sports DST", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-tiered-defense-dst-rankings-and-strategy", "Matthew Harris tiers, Aug 19. Seattle first, Houston third."),
    ("Derek Brown DST", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dst.php", "FantasyPros expert, Aug 12. Houston and the Rams up."),
    ("Andrew Erickson DST", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dst.php", "FantasyPros expert, Aug 27. Chargers inside the 5."),
    ("Pat Fitzmaurice DST", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dst.php", "FantasyPros expert, July 1. Seattle first."),
    ("STACKED DST", "https://www.stackedfantasy.com/nfl/draft-guide/dst", "Full 32, updated Aug 31. Houston first."),
    ("Draft Sharks DST", "https://www.draftsharks.com/rankings/def", "Partial board, Aug 31. Unranked clubs skipped."),
    ("CBS DST", "https://www.4for4.com/fantasy-football-rankings/cbs/def/2026", "Top 10 published Aug 30 via 4for4. Rams first."),
]

KICKERS = [
    ("Brandon Aubrey", "DAL"), ("Ka'imi Fairbairn", "HOU"), ("Cameron Dicker", "LAC"),
    ("Jason Myers", "SEA"), ("Cam Little", "JAX"), ("Eddy Pineiro", "SF"),
    ("Tyler Loop", "BAL"), ("Evan McPherson", "CIN"), ("Jake Bates", "DET"),
    ("Cairo Santos", "CHI"), ("Andy Borregales", "NE"), ("Harrison Mevis", "LAR"),
    ("Chase McLaughlin", "TB"), ("Chris Boswell", "PIT"), ("Harrison Butker", "KC"),
    ("Will Reichard", "MIN"), ("Wil Lutz", "DEN"), ("Charlie Smyth", "NO"),
    ("Jake Elliott", "PHI"), ("Blake Grupe", "IND"), ("Tyler Bass", "BUF"),
    ("Chad Ryland", "ARI"), ("Joey Slye", "TEN"), ("Nick Folk", "ATL"),
    ("Trey Smack", "GB"),
]

# FantasyPros kicker ECR, Aug 2026 draft article.
FP_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Cameron Dicker": 3, "Jason Myers": 4,
    "Cam Little": 5, "Eddy Pineiro": 6, "Tyler Loop": 7, "Evan McPherson": 8,
    "Jake Bates": 9, "Cairo Santos": 10, "Andy Borregales": 11, "Harrison Mevis": 12,
    "Chase McLaughlin": 13, "Chris Boswell": 14, "Harrison Butker": 15, "Will Reichard": 16,
    "Wil Lutz": 17, "Charlie Smyth": 18, "Jake Elliott": 19, "Blake Grupe": 20,
    "Tyler Bass": 21, "Chad Ryland": 22, "Joey Slye": 23, "Nick Folk": 24,
}
BROWN_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Cameron Dicker": 3, "Jason Myers": 4,
    "Cam Little": 5, "Evan McPherson": 6, "Eddy Pineiro": 7, "Chase McLaughlin": 9,
    "Andy Borregales": 10, "Tyler Loop": 11, "Cairo Santos": 12, "Harrison Mevis": 13,
}
FITZ_K = {
    "Brandon Aubrey": 1, "Ka'imi Fairbairn": 2, "Cameron Dicker": 3, "Cam Little": 4,
    "Jason Myers": 5, "Harrison Mevis": 6, "Tyler Loop": 7, "Eddy Pineiro": 8,
    "Chase McLaughlin": 9, "Cairo Santos": 10, "Andy Borregales": 11, "Evan McPherson": 12,
}
# Draft Sharks 2026 K, updated Aug 31. Skip unnamed NYG/CAR/WAS slots.
# https://www.draftsharks.com/rankings/pk
DS_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Cam Little": 4,
    "Eddy Pineiro": 5, "Cairo Santos": 6, "Evan McPherson": 7, "Jason Myers": 8,
    "Jake Bates": 9, "Harrison Mevis": 10, "Trey Smack": 11, "Will Reichard": 12,
    "Wil Lutz": 13, "Harrison Butker": 14, "Tyler Loop": 15, "Andy Borregales": 16,
    "Chris Boswell": 17, "Chase McLaughlin": 18, "Tyler Bass": 19, "Jake Elliott": 20,
    "Charlie Smyth": 23, "Blake Grupe": 25,
}
# RotoWire Jerry Donabedian, Aug 27. Skip 15 (Carlson vs Smyth). Grupe not Shrader.
# https://www.rotowire.com/football/article/2026-fantasy-football-rankings-kickers-85924
RW_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Jason Myers": 4,
    "Cam Little": 5, "Will Reichard": 6, "Jake Bates": 7, "Harrison Mevis": 8,
    "Tyler Loop": 9, "Harrison Butker": 10, "Chris Boswell": 11, "Chase McLaughlin": 12,
    "Wil Lutz": 13, "Eddy Pineiro": 14, "Cairo Santos": 16, "Nick Folk": 17,
    "Evan McPherson": 18, "Trey Smack": 19, "Blake Grupe": 20,
}

K_SOURCES = [
    ("FantasyPros Kicker ECR", "https://www.fantasypros.com/2026/08/fantasy-football-draft-rankings-tiers-kickers-2026-little-bates-aubrey/", "Expert consensus, Aug 2026. Aubrey locked first."),
    ("Derek Brown K", "https://www.fantasypros.com/nfl/fantasy-football-rankings/k.php", "FantasyPros expert, Aug 13."),
    ("Pat Fitzmaurice K", "https://www.fantasypros.com/nfl/fantasy-football-rankings/k.php", "FantasyPros expert, Aug 26. Little over Myers, Mevis inside the 6."),
    ("Draft Sharks K", "https://www.draftsharks.com/rankings/pk", "Updated Aug 31. Trey Smack (GB) inside the 12. Unnamed slots skipped."),
    ("RotoWire K", "https://www.rotowire.com/football/article/2026-fantasy-football-rankings-kickers-85924", "Jerry Donabedian, Aug 27. Skip the Carlson/Smyth slot."),
]


def _mean_rows(universe, maps, pos):
    rows = []
    for name, team in universe:
        nums = []
        shown = {}
        for label, mp in maps.items():
            rk = mp.get(team) if pos == "DST" else mp.get(name)
            if rk:
                nums.append(float(rk))
                shown[label] = int(rk)
        if not nums:
            continue
        rows.append({
            "name": name,
            "pos": pos,
            "team": team,
            "n": len(nums),
            "avg": round(sum(nums) / len(nums), 2),
            "ranks": shown,
        })
    rows.sort(key=lambda r: (r["avg"], r["name"]))
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def dst_board():
    return _mean_rows(DST_TEAMS, {
        "fp": FP_DST,
        "nbc": NBC_DST,
        "brown": BROWN_DST,
        "erickson": ERICKSON_DST,
        "fitz": FITZ_DST,
        "stacked": STACKED_DST,
        "ds": DS_DST,
        "cbs": CBS_DST,
    }, "DST")


def kicker_board():
    return _mean_rows(KICKERS, {
        "fp": FP_K,
        "brown": BROWN_K,
        "fitz": FITZ_K,
        "ds": DS_K,
        "rw": RW_K,
    }, "K")
