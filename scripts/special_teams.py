"""2026 redraft DST and kicker Super Aggregates.

DST season board (The D): Mega Aggregate of published season projections.
  50% FantasyPros + ESPN long core, 50% RotoWire (via Sleeper).

DST ROS board: Super Aggregate of rest-of-season ranking boards.
  50% FantasyPros ROS ECR, 50% every other ROS board that ranked the club.

Kickers stay on the published draft-season expert mash.
Published boards only. Unranked names are skipped, never treated as 999.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_curve import bk_value  # noqa: E402
from aggregate_protocol import super_avg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RANK_DIR = ROOT / "data" / "ranks"

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

TEAM_NAME = {abbr: name for name, abbr in DST_TEAMS}


def _load_rank(name: str) -> dict:
    path = RANK_DIR / f"{name}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _rank_map_from_players(payload: dict, *, by: str = "rank") -> dict:
    out = {}
    for row in payload.get("players") or []:
        team = (row.get("team") or "").upper()
        if team == "JAC":
            team = "JAX"
        if not team:
            continue
        if by == "fpts":
            fpts = row.get("fpts")
            if fpts is None:
                continue
            out[team] = float(fpts)
        else:
            rk = row.get("rank")
            if not rk:
                continue
            out[team] = int(rk)
    if by == "fpts":
        ordered = sorted(out.items(), key=lambda kv: (-kv[1], kv[0]))
        return {team: i for i, (team, _) in enumerate(ordered, 1)}
    return out


def _proj_map(payload: dict) -> dict:
    out = {}
    for row in payload.get("players") or []:
        team = (row.get("team") or "").upper()
        if team == "JAC":
            team = "JAX"
        fpts = row.get("fpts")
        if not team or fpts is None:
            continue
        out[team] = float(fpts)
    return out


def _mean_rows(universe, maps, pos, long_core=(), proj_by_team=None):
    rows = []
    for name, team in universe:
        shown = {}
        for label, mp in maps.items():
            rk = mp.get(team) if pos == "DST" else mp.get(name)
            if rk:
                shown[label] = int(rk)
        if not shown:
            continue
        avg = super_avg(shown, long_core) if long_core else round(sum(shown.values()) / len(shown), 2)
        row = {
            "name": name,
            "pos": pos,
            "team": team,
            "n": len(shown),
            "avg": avg,
            "ranks": shown,
        }
        if proj_by_team and team in proj_by_team:
            row["proj"] = round(proj_by_team[team], 1)
        rows.append(row)
    rows.sort(key=lambda r: (r["avg"], r["name"]))
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def season_proj_maps() -> dict:
    """Team -> rank maps from season projection boards."""
    return {
        "FantasyPros": _rank_map_from_players(_load_rank("dst-fp-season-proj"), by="fpts"),
        "ESPN": _rank_map_from_players(_load_rank("dst-espn-season-proj"), by="fpts"),
        "RotoWire": _rank_map_from_players(_load_rank("dst-rw-season-proj"), by="fpts"),
    }


def season_proj_points() -> dict:
    """Mean projected season points across boards that published the club."""
    sources = [
        _proj_map(_load_rank("dst-fp-season-proj")),
        _proj_map(_load_rank("dst-espn-season-proj")),
        _proj_map(_load_rank("dst-rw-season-proj")),
    ]
    teams = set()
    for src in sources:
        teams.update(src)
    out = {}
    for team in teams:
        vals = [src[team] for src in sources if team in src]
        if vals:
            out[team] = sum(vals) / len(vals)
    return out


DST_SEASON_LONG = ("FantasyPros", "ESPN")

DST_SOURCES = [
    (
        "FantasyPros season projections",
        "https://www.fantasypros.com/nfl/projections/dst.php?week=draft",
        "Consensus 2026 season DST points. Free top of the board; unranked clubs skipped.",
    ),
    (
        "ESPN season projections",
        "https://fantasy.espn.com/football/players/projections",
        "ESPN default-league season D/ST points for all 32 clubs.",
    ),
    (
        "RotoWire season projections",
        "https://www.rotowire.com/football/",
        "Season D/ST points via Sleeper. All 32 clubs.",
    ),
]


def dst_board():
    """Season projections Mega Aggregate for The D."""
    maps = season_proj_maps()
    maps = {k: v for k, v in maps.items() if v}
    if not maps:
        return []
    return _mean_rows(
        DST_TEAMS,
        maps,
        "DST",
        long_core=tuple(name for name in DST_SEASON_LONG if name in maps),
        proj_by_team=season_proj_points(),
    )


def ros_dst_maps() -> dict:
    maps = {
        "FantasyPros ROS ECR": _rank_map_from_players(_load_rank("dst-fp-ros-ecr")),
    }
    experts = _load_rank("dst-fp-ros-experts").get("boards") or {}
    for label, rows in experts.items():
        mp = {}
        for row in rows:
            team = (row.get("team") or "").upper()
            if team == "JAC":
                team = "JAX"
            rk = row.get("rank")
            if team and rk:
                mp[team] = int(rk)
        if mp:
            maps[label] = mp
    espn = _rank_map_from_players(_load_rank("dst-espn-ros-proj"), by="fpts")
    if espn:
        maps["ESPN ROS"] = espn
    fsp = _rank_map_from_players(_load_rank("dst-fantasysp-ros"), by="fpts")
    if fsp:
        maps["FantasySP ROS"] = fsp
    return maps


def ros_dst_points() -> dict:
    """Remaining projected points when a ROS feed publishes them."""
    buckets = [
        _proj_map(_load_rank("dst-fp-ros-ecr")),
        _proj_map(_load_rank("dst-espn-ros-proj")),
        _proj_map(_load_rank("dst-fantasysp-ros")),
    ]
    teams = set()
    for src in buckets:
        teams.update(src)
    out = {}
    for team in teams:
        vals = [src[team] for src in buckets if team in src]
        if vals:
            out[team] = sum(vals) / len(vals)
    return out


DST_ROS_LONG = ("FantasyPros ROS ECR",)

DST_ROS_SOURCES = [
    (
        "FantasyPros ROS DST ECR",
        "https://www.fantasypros.com/nfl/rankings/ros-dst.php",
        "Rest-of-season expert consensus. All 32 clubs.",
    ),
    (
        "Pat Fitzmaurice ROS DST",
        "https://www.fantasypros.com/nfl/rankings/pat-fitzmaurice.php?position=DST&type=ros",
        "FantasyPros expert ROS board.",
    ),
    (
        "Ryan Linkletter ROS DST",
        "https://www.fantasypros.com/nfl/rankings/ryanlinkletter.php?position=DST&type=ros",
        "Blitz Sports Media ROS board via FantasyPros.",
    ),
    (
        "Aaron St Denis ROS DST",
        "https://www.fantasypros.com/nfl/rankings/aaron-st-denis.php?position=DST&type=ros",
        "Fantasy Sports Advice Network ROS board via FantasyPros.",
    ),
    (
        "ESPN ROS projections",
        "https://fantasy.espn.com/football/players/projections",
        "ESPN remaining-season D/ST points for all 32 clubs.",
    ),
    (
        "FantasySP ROS DST",
        "https://www.fantasysp.com/rest-of-season/nfl/DST",
        "Remaining projected points. Free top of the board; unranked clubs skipped.",
    ),
]


def ros_dst_board():
    """Rest-of-season DST Super Aggregate."""
    maps = {k: v for k, v in ros_dst_maps().items() if v}
    if not maps:
        return []
    return _mean_rows(
        DST_TEAMS,
        maps,
        "DST",
        long_core=tuple(name for name in DST_ROS_LONG if name in maps),
        proj_by_team=ros_dst_points(),
    )


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
DS_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Cam Little": 4,
    "Eddy Pineiro": 5, "Cairo Santos": 6, "Evan McPherson": 7, "Jason Myers": 8,
    "Jake Bates": 9, "Harrison Mevis": 10, "Trey Smack": 11, "Will Reichard": 12,
    "Wil Lutz": 13, "Harrison Butker": 14, "Tyler Loop": 15, "Andy Borregales": 16,
    "Chris Boswell": 17, "Chase McLaughlin": 18, "Tyler Bass": 19, "Jake Elliott": 20,
    "Charlie Smyth": 23, "Blake Grupe": 25,
}
# RotoWire Jerry Donabedian, Aug 27. Skip 15 (Carlson vs Smyth). Grupe not Shrader.
RW_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Jason Myers": 4,
    "Cam Little": 5, "Will Reichard": 6, "Jake Bates": 7, "Harrison Mevis": 8,
    "Tyler Loop": 9, "Harrison Butker": 10, "Chris Boswell": 11, "Chase McLaughlin": 12,
    "Wil Lutz": 13, "Eddy Pineiro": 14, "Cairo Santos": 16, "Nick Folk": 17,
    "Evan McPherson": 18, "Trey Smack": 19, "Blake Grupe": 20,
}
# Field Yates overall PPR, refreshed Sep 5. Kicker slice only.
YATES_K = {
    "Brandon Aubrey": 1, "Cameron Dicker": 2, "Ka'imi Fairbairn": 3, "Eddy Pineiro": 4,
    "Chris Boswell": 5, "Harrison Butker": 6, "Jason Myers": 7, "Will Reichard": 8,
    "Cam Little": 9, "Harrison Mevis": 10,
}

K_SOURCES = [
    ("FantasyPros Kicker ECR", "https://www.fantasypros.com/2026/08/fantasy-football-draft-rankings-tiers-kickers-2026-little-bates-aubrey/", "Expert consensus, Aug 2026. Aubrey locked first."),
    ("Derek Brown K", "https://www.fantasypros.com/nfl/fantasy-football-rankings/k.php", "FantasyPros expert, Aug 13."),
    ("Pat Fitzmaurice K", "https://www.fantasypros.com/nfl/fantasy-football-rankings/k.php", "FantasyPros expert, Aug 26. Little over Myers, Mevis inside the 6."),
    ("Draft Sharks K", "https://www.draftsharks.com/rankings/pk", "Updated Aug 31. Trey Smack (GB) inside the 12. Unnamed slots skipped."),
    ("RotoWire K", "https://www.rotowire.com/football/article/2026-fantasy-football-rankings-kickers-85924", "Jerry Donabedian, Aug 27. Skip the Carlson/Smyth slot."),
    ("Field Yates K", "https://www.espn.com/fantasy/football/story/_/id/48711830", "PPR overall slice, Sep 5. Aubrey first, Dicker second."),
]

K_LONG = ("fp", "ds", "rw")


def kicker_board():
    return _mean_rows(KICKERS, {
        "fp": FP_K,
        "brown": BROWN_K,
        "fitz": FITZ_K,
        "ds": DS_K,
        "rw": RW_K,
        "yates": YATES_K,
    }, "K", long_core=K_LONG)
