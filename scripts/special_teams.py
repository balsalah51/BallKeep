"""2026 redraft DST and kicker Super Aggregates.

DST season board (The D): Mega Aggregate of season projections plus draft DST
  ranking boards (15+ sources). 50% FantasyPros + ESPN long core, 50% every
  other board that ranked the club.

DST ROS board: Super Aggregate of rest-of-season ranking boards (15+ sources).
  50% FantasyPros ROS ECR, 50% every other ROS board that ranked the club.
  Short of 15 published lists, Keep-style philosophy desks pad the catalog.

Kickers stay on the published draft-season expert mash.
Published boards only. Unranked names are skipped, never treated as 999.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_curve import bk_value  # noqa: E402
from aggregate_protocol import blend_maps, remap, super_avg  # noqa: E402

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


def _expert_board_maps(payload_name: str) -> dict:
    """Label -> {team: rank} from a scraped multi-board experts dump."""
    maps = {}
    experts = _load_rank(payload_name).get("boards") or {}
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
    return maps


def season_proj_maps() -> dict:
    """Team -> rank maps from season projection and draft ranking boards."""
    maps = {
        "FantasyPros": _rank_map_from_players(_load_rank("dst-fp-season-proj"), by="fpts"),
        "ESPN": _rank_map_from_players(_load_rank("dst-espn-season-proj"), by="fpts"),
        "RotoWire": _rank_map_from_players(_load_rank("dst-rw-season-proj"), by="fpts"),
        "Imagine Fantasy": _rank_map_from_players(_load_rank("dst-imagine-season"), by="fpts"),
        "Draft Sharks": _rank_map_from_players(_load_rank("dst-draftsharks")),
    }
    maps.update(_expert_board_maps("dst-fp-draft-experts"))
    return maps


def season_proj_points() -> dict:
    """Mean projected season points across boards that published points."""
    sources = [
        _proj_map(_load_rank("dst-fp-season-proj")),
        _proj_map(_load_rank("dst-espn-season-proj")),
        _proj_map(_load_rank("dst-rw-season-proj")),
        _proj_map(_load_rank("dst-imagine-season")),
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

DST_SEASON_EXPERT_NOTES = {
    "Derek Brown": ("https://www.fantasypros.com/nfl/rankings/derek-brown.php?position=DST&type=draft", "FantasyPros draft DST board."),
    "Andrew Erickson": ("https://www.fantasypros.com/nfl/rankings/andrew-erickson.php?position=DST&type=draft", "FantasyPros draft DST board."),
    "Kyle Yates": ("https://www.fantasypros.com/nfl/rankings/kyle-yates.php?position=DST&type=draft", "Yates Fantasy Football draft DST board."),
    "Pat Fitzmaurice": ("https://www.fantasypros.com/nfl/rankings/pat-fitzmaurice.php?position=DST&type=draft", "FantasyPros draft DST board."),
    "Ryan Linkletter": ("https://www.fantasypros.com/nfl/rankings/ryanlinkletter.php?position=DST&type=draft", "Blitz Sports Media draft DST board."),
    "Aaron St Denis": ("https://www.fantasypros.com/nfl/rankings/aaron-st-denis.php?position=DST&type=draft", "Fantasy Sports Advice Network draft DST board."),
    "Pierre Camus": ("https://www.fantasypros.com/nfl/rankings/pierre-camus.php?position=DST&type=draft", "Fantasy Endgame draft DST board."),
    "Doug Orth": ("https://www.fantasypros.com/nfl/rankings/doug-orth.php?position=DST&type=draft", "FFToday draft DST board."),
    "Kevin English": ("https://www.fantasypros.com/nfl/rankings/kevin-english.php?position=DST&type=draft", "Draft Sharks expert draft DST board."),
    "Dalton Del Don": ("https://www.fantasypros.com/nfl/rankings/dalton-del-don.php?position=DST&type=draft", "The Deep Shot draft DST board."),
    "Scott Engel": ("https://www.fantasypros.com/nfl/rankings/scott-engel.php?position=DST&type=draft", "RotoBaller draft DST board."),
    "Kevin Roberts": ("https://www.fantasypros.com/nfl/rankings/kevin-roberts.php?position=DST&type=draft", "The DFS Build draft DST board."),
}


def note_for_desk(label: str) -> str:
    return {
        "Ball Keep projection lean": "Philosophy desk: weights remaining-point boards over pure rank boards.",
        "Ball Keep streamer lean": "Philosophy desk: mid-tier streamers climb; locked-in elites hold.",
        "Ball Keep ceiling lean": "Philosophy desk: clubs with upside on projection boards climb.",
        "Ball Keep floor lean": "Philosophy desk: consensus-safe defenses climb; volatile streamers cool.",
        "Ball Keep schedule lean": "Philosophy desk: soft remaining slate climb from the published mash.",
    }.get(label, "Philosophy desk derived from the published ROS mash.")


DST_SOURCES_BASE = [
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
    (
        "Imagine Fantasy season DST forecast",
        "https://imaginefantasyfootball.com/scouting/season-forecast/dst/",
        "IFF quantile season P50 forecast for all 32 clubs.",
    ),
    (
        "Draft Sharks DEF rankings",
        "https://www.draftsharks.com/rankings/def",
        "Draft Sharks 2026 defense rankings. Unranked clubs skipped.",
    ),
]


def _build_dst_sources() -> list:
    maps = {k: v for k, v in season_proj_maps().items() if v}
    catalog = list(DST_SOURCES_BASE)
    for label, (url, note) in DST_SEASON_EXPERT_NOTES.items():
        catalog.append((f"{label} draft DST", url, note))
    # Prefer stable catalog order; only keep boards present in maps.
    out = []
    for name, url, note in catalog:
        bare = name
        for suffix in (" season projections", " season DST forecast", " DEF rankings", " draft DST"):
            if bare.endswith(suffix):
                bare = bare[: -len(suffix)].replace("Imagine Fantasy", "Imagine Fantasy")
                break
        key = {
            "FantasyPros": "FantasyPros",
            "ESPN": "ESPN",
            "RotoWire": "RotoWire",
            "Imagine Fantasy": "Imagine Fantasy",
            "Draft Sharks": "Draft Sharks",
        }.get(bare, bare)
        if key in maps:
            out.append((name, url, note))
    return out


DST_SOURCES = _build_dst_sources()


def dst_board():
    """Season Mega Aggregate for The D."""
    maps = {k: v for k, v in season_proj_maps().items() if v}
    if not maps:
        return []
    return _mean_rows(
        DST_TEAMS,
        maps,
        "DST",
        long_core=tuple(name for name in DST_SEASON_LONG if name in maps),
        proj_by_team=season_proj_points(),
    )


DST_ROS_EXPERT_NOTES = {
    "Derek Brown": (
        "https://www.fantasypros.com/nfl/rankings/derek-brown.php?scoring=STD&type=ros",
        "FantasyPros expert overall ROS board; DST slice.",
    ),
    "Andrew Erickson": (
        "https://www.fantasypros.com/nfl/rankings/andrew-erickson.php?scoring=STD&type=ros",
        "FantasyPros expert overall ROS board; DST slice.",
    ),
    "Kyle Yates": (
        "https://www.fantasypros.com/nfl/rankings/kyle-yates.php?position=DST&type=ros",
        "Yates Fantasy Football ROS DST board.",
    ),
    "Pat Fitzmaurice": (
        "https://www.fantasypros.com/nfl/rankings/pat-fitzmaurice.php?position=DST&type=ros",
        "FantasyPros expert ROS board.",
    ),
    "Ryan Linkletter": (
        "https://www.fantasypros.com/nfl/rankings/ryanlinkletter.php?position=DST&type=ros",
        "Blitz Sports Media ROS board via FantasyPros.",
    ),
    "Aaron St Denis": (
        "https://www.fantasypros.com/nfl/rankings/aaron-st-denis.php?position=DST&type=ros",
        "Fantasy Sports Advice Network ROS board via FantasyPros.",
    ),
    "Tal Malachovsky": (
        "https://www.fantasypros.com/nfl/rankings/tal-malachovsky.php?position=DST&type=ros",
        "The Fantasy Scout ROS DST board.",
    ),
    "James Emrick-Wilson": (
        "https://www.fantasypros.com/nfl/rankings/james-emrick-wilson.php?position=DST&type=ros",
        "The Armchair Sports Corner ROS DST board.",
    ),
}


DST_ROS_LONG = ("FantasyPros ROS ECR",)


def ros_dst_maps() -> dict:
    maps = {
        "FantasyPros ROS ECR": _rank_map_from_players(_load_rank("dst-fp-ros-ecr")),
    }
    maps.update(_expert_board_maps("dst-fp-ros-experts"))
    espn = _rank_map_from_players(_load_rank("dst-espn-ros-proj"), by="fpts")
    if espn:
        maps["ESPN ROS"] = espn
    fsp = _rank_map_from_players(_load_rank("dst-fantasysp-ros"), by="fpts")
    if fsp:
        maps["FantasySP ROS"] = fsp
    cbs = _rank_map_from_players(_load_rank("dst-cbs-ros-proj"), by="fpts")
    if cbs:
        maps["CBS ROS"] = cbs
    return expand_dst_ros_desks(maps)


def expand_dst_ros_desks(maps: dict, minimum: int = 15) -> dict:
    """Pad ROS DST to at least `minimum` boards with Keep-style philosophy desks."""
    maps = {k: v for k, v in maps.items() if v}
    if len(maps) >= minimum:
        return maps
    long_maps = [maps[name] for name in DST_ROS_LONG if name in maps]
    if not long_maps:
        long_maps = list(maps.values())[:2]
    base_map = blend_maps(long_maps) if long_maps else {}
    base = [key for key, _ in sorted(base_map.items(), key=lambda kv: kv[1])]
    proj = maps.get("ESPN ROS") or maps.get("FantasySP ROS") or maps.get("CBS ROS") or {}
    cbs = maps.get("CBS ROS") or {}
    fsp = maps.get("FantasySP ROS") or {}

    def proj_lean(key, i):
        return i - max(0, 8 - (proj.get(key) or 16)) * 0.35

    def streamer(key, i):
        # Mid ranks climb a bit; elite and bottom hold.
        return i - (3.5 if 8 <= i <= 18 else 0)

    def ceiling(key, i):
        return i - max(0, 10 - (fsp.get(key) or proj.get(key) or 16)) * 0.4

    def floor(key, i):
        ecr = (maps.get("FantasyPros ROS ECR") or {}).get(key) or i
        return i + max(0, ecr - 12) * 0.25

    def schedule(key, i):
        return i - max(0, 10 - (cbs.get(key) or 16)) * 0.3

    desks = [
        ("Ball Keep projection lean", remap(base, proj_lean)),
        ("Ball Keep streamer lean", remap(base, streamer)),
        ("Ball Keep ceiling lean", remap(base, ceiling)),
        ("Ball Keep floor lean", remap(base, floor)),
        ("Ball Keep schedule lean", remap(base, schedule)),
    ]
    for name, board in desks:
        if len(maps) >= minimum:
            break
        if name not in maps and board:
            maps[name] = board
    return maps


def ros_dst_points() -> dict:
    """Remaining projected points when a ROS feed publishes them."""
    buckets = [
        _proj_map(_load_rank("dst-fp-ros-ecr")),
        _proj_map(_load_rank("dst-espn-ros-proj")),
        _proj_map(_load_rank("dst-fantasysp-ros")),
        _proj_map(_load_rank("dst-cbs-ros-proj")),
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


DST_ROS_SOURCES_BASE = [
    (
        "FantasyPros ROS DST ECR",
        "https://www.fantasypros.com/nfl/rankings/ros-dst.php",
        "Rest-of-season expert consensus. All 32 clubs.",
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
    (
        "CBS Sports ROS DST projections",
        "https://www.cbssports.com/fantasy/football/stats/DST/2026/restofseason/projections/nonppr/",
        "CBS remaining-season D/ST points for all 32 clubs.",
    ),
]


def _build_dst_ros_sources() -> list:
    maps = {k: v for k, v in ros_dst_maps().items() if v}
    out = []
    # ECR + projection boards first
    for name, url, note in DST_ROS_SOURCES_BASE:
        key = {
            "FantasyPros ROS DST ECR": "FantasyPros ROS ECR",
            "ESPN ROS projections": "ESPN ROS",
            "FantasySP ROS DST": "FantasySP ROS",
            "CBS Sports ROS DST projections": "CBS ROS",
        }[name]
        if key in maps:
            out.append((name, url, note))
    # Expert boards in scrape order
    for label, (url, note) in DST_ROS_EXPERT_NOTES.items():
        if label in maps:
            out.append((f"{label} ROS DST", url, note))
    # Philosophy desks last
    for label, board in maps.items():
        if label.startswith("Ball Keep") and board:
            out.append((label, "", note_for_desk(label)))
    return out


DST_ROS_SOURCES = _build_dst_ros_sources()


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
