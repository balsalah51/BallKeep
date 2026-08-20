#!/usr/bin/env python3
"""Build the BallKeep static site from scraped ranking and schedule sources."""
from __future__ import annotations

import html
import json
import math
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 20, 2026"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extra_ranks import (  # noqa: E402
    DRAFT_SHARKS_SF,
    ESPN_KARABELL_FLEX,
    ESPN_KARABELL_SF,
    ROTOWIRE_SF,
    as_ranks,
)
from player_copy import get_copy  # noqa: E402
from recent_trades import enrich_deals  # noqa: E402
from build_bb import write_baseball_site  # noqa: E402
from build_pl import write_pitch_site  # noqa: E402


def esc(s):
    return html.escape(str(s), quote=True)


def norm_name(name: str) -> str:
    n = name.lower()
    n = n.replace(".", " ")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = n.replace("'", "").replace("’", "")
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "patrick mahomes ii": "patrick mahomes",
        "james cook iii": "james cook",
        "kenneth walker iii": "kenneth walker",
        "luther burden iii": "luther burden",
        "brian thomas jr": "brian thomas",
        "omar cooper jr": "omar cooper",
        "marvin harrison jr": "marvin harrison",
        "michael pittman jr": "michael pittman",
        "kyle pitts sr": "kyle pitts",
        "chris godwin jr": "chris godwin",
        "travis etienne jr": "travis etienne",
        "dandre swift": "dandre swift",
        "d'andre swift": "dandre swift",
        "devon achane": "devon achane",
        "de'von achane": "devon achane",
        "amon ra st brown": "amon-ra st brown",
        "amon-ra st. brown": "amon-ra st brown",
        "ja marr chase": "jamarr chase",
        "jamarr chase": "jamarr chase",
        "nicholas singleton": "nick singleton",
        "nick singleton": "nick singleton",
        "harold fannin jr": "harold fannin",
        "deebo samuel sr": "deebo samuel",
        "aaron jones sr": "aaron jones",
    }
    return aliases.get(n, n)


TEAMS = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS",
}
TEAM_BY_ABBR = {v: k for k, v in TEAMS.items()}


def parse_pfn(path: Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(QB|RB|WR|TE)\s*\|\s*([A-Z]{2,3})\s*\|\s*(\d+)\s*\|",
            line,
        )
        if not m:
            continue
        rows.append({
            "rank": int(m.group(1)),
            "name": m.group(2).strip(),
            "pos": m.group(3),
            "team": m.group(4).replace("GBP", "GB").replace("KCC", "KC").replace("NOS", "NO").replace("SFO", "SF").replace("LVR", "LV").replace("NEP", "NE"),
            "age": int(m.group(5)),
        })
    # keep first occurrence (best overall rank)
    seen = set()
    out = []
    for r in rows:
        k = norm_name(r["name"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def parse_nfl_schedule(path: Path):
    games = []
    week = None
    day = ""
    for line in path.read_text(errors="replace").splitlines():
        wm = re.match(r"WEEK\s+(\d+)", line.strip(), re.I)
        if wm:
            week = int(wm.group(1))
            continue
        dm = re.match(
            r"(Wednesday|Thursday|Friday|Saturday|Sunday|Monday|Date TBD),?\s*(.*)",
            line.strip(),
        )
        if dm and week:
            day = line.strip()
            continue
        gm = re.match(r"\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if not gm or week is None:
            continue
        matchup = gm.group(1).strip()
        time = gm.group(2).strip()
        tv = gm.group(3).strip().rstrip("*")
        if matchup in ("Matchup", "TBD") or "---" in matchup:
            continue
        loc = ""
        mm = re.match(r"(.+?)\s+(at|vs)\s+(.+?)(?:\s+\((.+)\))?$", matchup)
        if not mm:
            continue
        left, prep, right, loc = mm.group(1).strip(), mm.group(2), mm.group(3).strip(), mm.group(4) or ""
        if left not in TEAMS or right not in TEAMS:
            continue
        away, home = (left, right) if prep == "at" else (left, right)
        games.append({
            "week": week, "day": day, "away": away, "home": home,
            "prep": prep, "time": time, "tv": tv, "note": loc,
        })
    # de-dupe (file repeats week 7)
    uniq = []
    seen = set()
    for g in games:
        key = (g["week"], g["away"], g["home"], g["time"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(g)
    return uniq


# --- additional scraped source ranks (name -> rank) ---
FANTASYPROS_SF = {
    "Drake Maye": 1, "Josh Allen": 2, "Ja'Marr Chase": 3, "Jaxon Smith-Njigba": 4,
    "Bijan Robinson": 5, "Jayden Daniels": 6, "Jahmyr Gibbs": 7, "Puka Nacua": 8,
    "Jalen Hurts": 9, "Lamar Jackson": 10, "Justin Herbert": 11, "Ashton Jeanty": 12,
}
FP_EXPERTS = {
    "Derek Brown (X)": {
        "Josh Allen": 1, "Drake Maye": 2, "Jalen Hurts": 3, "Ja'Marr Chase": 4,
        "Jaxon Smith-Njigba": 5, "Jahmyr Gibbs": 6, "Bijan Robinson": 7, "Puka Nacua": 8,
        "Ashton Jeanty": 11, "Jayden Daniels": 23, "Justin Herbert": 26, "Lamar Jackson": 27,
    },
    "Andrew Erickson (X)": {
        "Drake Maye": 1, "Jayden Daniels": 2, "Josh Allen": 3, "Lamar Jackson": 4,
        "Justin Herbert": 5, "Ja'Marr Chase": 8, "Jaxon Smith-Njigba": 9, "Bijan Robinson": 10,
        "Jalen Hurts": 14, "Jahmyr Gibbs": 16, "Puka Nacua": 18, "Ashton Jeanty": 22,
    },
    "Pat Fitzmaurice (X)": {
        "Drake Maye": 1, "Josh Allen": 2, "Jayden Daniels": 3, "Ja'Marr Chase": 5,
        "Lamar Jackson": 6, "Bijan Robinson": 7, "Jahmyr Gibbs": 8, "Puka Nacua": 9,
        "Jaxon Smith-Njigba": 10, "Justin Herbert": 12, "Ashton Jeanty": 13, "Jalen Hurts": 19,
    },
}
DYNASTY_NERDS = {
    "Josh Allen": 1, "Bijan Robinson": 2, "Drake Maye": 3, "Ja'Marr Chase": 4,
    "Jahmyr Gibbs": 5, "Jaxon Smith-Njigba": 6, "Puka Nacua": 7, "Caleb Williams": 8,
    "Jayden Daniels": 9, "Ashton Jeanty": 10, "Brock Bowers": 11, "Justin Jefferson": 12,
    "De'Von Achane": 13, "CeeDee Lamb": 14, "Amon-Ra St. Brown": 15, "Malik Nabers": 16,
    "Joe Burrow": 17, "Jeremiyah Love": 18, "Lamar Jackson": 19, "Patrick Mahomes": 20,
    "Omarion Hampton": 21, "Justin Herbert": 22, "Trey McBride": 23, "Jaxson Dart": 24,
    "Drake London": 25, "Jalen Hurts": 26, "Tetairoa McMillan": 27, "Trevor Lawrence": 28,
    "Emeka Egbuka": 29, "Jonathan Taylor": 30, "James Cook": 31, "Garrett Wilson": 32,
    "George Pickens": 33, "Brock Purdy": 34, "Bo Nix": 35, "Carnell Tate": 36,
    "Colston Loveland": 37, "Breece Hall": 38, "Ladd McConkey": 39, "Jordan Love": 40,
    "Tyler Warren": 41, "Nico Collins": 42, "Kenneth Walker": 43, "Quinshon Judkins": 44,
    "Chris Olave": 45, "TreVeyon Henderson": 46, "Fernando Mendoza": 47, "Rome Odunze": 48,
    "Marvin Harrison": 49, "Dak Prescott": 50, "Christian McCaffrey": 51, "Brian Thomas": 52,
    "Zay Flowers": 53, "Jordyn Tyson": 54, "Luther Burden": 55, "Makai Lemon": 56,
    "Baker Mayfield": 57, "Chase Brown": 58, "Saquon Barkley": 59, "A.J. Brown": 60,
    "Tee Higgins": 61, "Jared Goff": 62, "Rashee Rice": 63, "Javonte Williams": 64,
    "DeVonta Smith": 65, "Cam Skattebo": 66, "Jaylen Waddle": 67, "Kyren Williams": 68,
    "Cam Ward": 69, "Jadarian Price": 70, "Bucky Irving": 71, "KC Concepcion": 72,
    "Kyle Pitts": 73, "Tucker Kraft": 74, "Jameson Williams": 75, "Harold Fannin": 76,
    "Josh Jacobs": 77, "Travis Etienne": 78, "Sam Darnold": 79, "C.J. Stroud": 80,
    "Kyler Murray": 81, "Christian Watson": 82, "Sam LaPorta": 83, "Bhayshul Tuten": 84,
    "DJ Moore": 85, "Jordan Addison": 86, "Tyler Shough": 87, "Malik Willis": 88,
    "Daniel Jones": 89, "Alec Pierce": 90, "D'Andre Swift": 91, "Omar Cooper": 92,
    "Denzel Boston": 93, "Michael Wilson": 94, "Terry McLaurin": 95, "Ty Simpson": 96,
    "Parker Washington": 97, "Matthew Stafford": 98, "Derrick Henry": 99, "Kenyon Sadiq": 100,
}
KTC_SF = {
    "Jahmyr Gibbs": 1, "Ja'Marr Chase": 2, "Bijan Robinson": 3, "Josh Allen": 4,
    "Jaxon Smith-Njigba": 5, "Drake Maye": 6, "Puka Nacua": 7, "Brock Bowers": 8,
    "Amon-Ra St. Brown": 9, "Caleb Williams": 10, "Lamar Jackson": 11, "Ashton Jeanty": 12,
    "Jeremiyah Love": 13, "Justin Jefferson": 14, "Malik Nabers": 15, "Joe Burrow": 16,
    "Jayden Daniels": 17, "Trey McBride": 18, "CeeDee Lamb": 19, "De'Von Achane": 20,
    "Omarion Hampton": 22, "Justin Herbert": 23, "Drake London": 24, "Jonathan Taylor": 25,
    "Jalen Hurts": 26, "Tetairoa McMillan": 27, "Emeka Egbuka": 28, "Colston Loveland": 29,
    "Patrick Mahomes": 30, "Bo Nix": 31, "George Pickens": 32, "Tyler Warren": 33,
    "Jaxson Dart": 36, "Carnell Tate": 37, "Nico Collins": 38, "Chris Olave": 39,
    "Brock Purdy": 40, "Chase Brown": 41, "Kenneth Walker": 42, "Rome Odunze": 43,
    "Garrett Wilson": 44, "Luther Burden": 47, "Ladd McConkey": 48, "A.J. Brown": 49,
    "Fernando Mendoza": 50,
}
YATES_PPR = [
    ("Bijan Robinson", "RB", "ATL"), ("Jahmyr Gibbs", "RB", "DET"), ("Christian McCaffrey", "RB", "SF"),
    ("Ja'Marr Chase", "WR", "CIN"), ("Puka Nacua", "WR", "LAR"), ("Jaxon Smith-Njigba", "WR", "SEA"),
    ("Jonathan Taylor", "RB", "IND"), ("De'Von Achane", "RB", "MIA"), ("Amon-Ra St. Brown", "WR", "DET"),
    ("James Cook", "RB", "BUF"), ("Derrick Henry", "RB", "BAL"), ("Justin Jefferson", "WR", "MIN"),
    ("CeeDee Lamb", "WR", "DAL"), ("Chase Brown", "RB", "CIN"), ("Kenneth Walker", "RB", "KC"),
    ("Trey McBride", "TE", "ARI"), ("Drake London", "WR", "ATL"), ("Brock Bowers", "TE", "LV"),
    ("Rashee Rice", "WR", "KC"), ("Josh Jacobs", "RB", "GB"), ("Jeremiyah Love", "RB", "ARI"),
    ("Saquon Barkley", "RB", "PHI"), ("Ashton Jeanty", "RB", "LV"), ("Omarion Hampton", "RB", "LAC"),
    ("Malik Nabers", "WR", "NYG"), ("A.J. Brown", "WR", "NE"), ("Chris Olave", "WR", "NO"),
    ("Josh Allen", "QB", "BUF"), ("George Pickens", "WR", "DAL"), ("Javonte Williams", "RB", "DAL"),
    ("Breece Hall", "RB", "NYJ"), ("Kyren Williams", "RB", "LAR"), ("Emeka Egbuka", "WR", "TB"),
    ("Garrett Wilson", "WR", "NYJ"), ("Colston Loveland", "TE", "CHI"), ("Lamar Jackson", "QB", "BAL"),
    ("Travis Etienne", "RB", "NO"), ("Cam Skattebo", "RB", "NYG"), ("Nico Collins", "WR", "HOU"),
    ("Jayden Daniels", "QB", "WAS"), ("Zay Flowers", "WR", "BAL"), ("Tetairoa McMillan", "WR", "CAR"),
    ("DeVonta Smith", "WR", "PHI"), ("Jaylen Waddle", "WR", "DEN"), ("Quinshon Judkins", "RB", "CLE"),
    ("Tyler Warren", "TE", "IND"), ("D'Andre Swift", "RB", "CHI"), ("Drake Maye", "QB", "NE"),
    ("Bucky Irving", "RB", "TB"), ("Davante Adams", "WR", "LAR"), ("Ladd McConkey", "WR", "LAC"),
    ("Jalen Hurts", "QB", "PHI"), ("Harold Fannin", "TE", "CLE"), ("Bhayshul Tuten", "RB", "JAX"),
    ("Chuba Hubbard", "RB", "CAR"), ("Jadarian Price", "RB", "SEA"), ("Tee Higgins", "WR", "CIN"),
    ("Kyle Pitts", "TE", "ATL"), ("Justin Herbert", "QB", "LAC"), ("Terry McLaurin", "WR", "WAS"),
    ("Carnell Tate", "WR", "TEN"), ("David Montgomery", "RB", "HOU"), ("Tony Pollard", "RB", "TEN"),
    ("George Kittle", "TE", "SF"), ("Rhamondre Stevenson", "RB", "NE"), ("TreVeyon Henderson", "RB", "NE"),
    ("Rome Odunze", "WR", "CHI"), ("DK Metcalf", "WR", "PIT"), ("Kenneth Gainwell", "RB", "TB"),
    ("Jaxson Dart", "QB", "NYG"), ("Jaylen Warren", "RB", "PIT"), ("DJ Moore", "WR", "BUF"),
    ("Joe Burrow", "QB", "CIN"), ("Marvin Harrison", "WR", "ARI"), ("Trevor Lawrence", "QB", "JAX"),
    ("Christian Watson", "WR", "GB"), ("Luther Burden", "WR", "CHI"), ("Jameson Williams", "WR", "DET"),
    ("Wan'Dale Robinson", "WR", "TEN"), ("Stefon Diggs", "WR", "WAS"), ("Rachaad White", "RB", "WAS"),
    ("Sam LaPorta", "TE", "DET"), ("Aaron Jones", "RB", "MIN"), ("Michael Wilson", "WR", "ARI"),
    ("Mike Evans", "WR", "SF"), ("Courtland Sutton", "WR", "DEN"), ("Michael Pittman", "WR", "PIT"),
    ("Tucker Kraft", "TE", "GB"), ("Dak Prescott", "QB", "DAL"), ("Patrick Mahomes", "QB", "KC"),
    ("Jakobi Meyers", "WR", "JAX"), ("Jake Ferguson", "TE", "DAL"), ("Chris Godwin", "WR", "TB"),
    ("Dallas Goedert", "TE", "PHI"), ("Kyle Monangai", "RB", "CHI"), ("Brock Purdy", "QB", "SF"),
    ("Matthew Stafford", "QB", "LAR"), ("Bo Nix", "QB", "DEN"), ("Travis Kelce", "TE", "KC"),
    ("J.K. Dobbins", "RB", "DEN"),
]
FP_PPR = {"Ja'Marr Chase": 1, "Jahmyr Gibbs": 2, "Puka Nacua": 3, "Bijan Robinson": 4, "Jaxon Smith-Njigba": 5}

ROOKIES = [
    {"name": "Jeremiyah Love", "pos": "RB", "team": "ARI", "dd": 1, "fp": 1, "pff": 1, "value": "Locked 1.01 · elite RB1 capital"},
    {"name": "Fernando Mendoza", "pos": "QB", "team": "LV", "dd": 2, "fp": 2, "pff": 2, "value": "Clear 1.02 in Superflex · sit-behind-Cousins year-one risk"},
    {"name": "Carnell Tate", "pos": "WR", "team": "TEN", "dd": 3, "fp": 3, "pff": 3, "value": "Safest WR · Day-1 starter with Ward"},
    {"name": "Jordyn Tyson", "pos": "WR", "team": "NO", "dd": 4, "fp": 5, "pff": 5, "value": "Early/mid 1st · Saints volume bet"},
    {"name": "Makai Lemon", "pos": "WR", "team": "PHI", "dd": 5, "fp": 6, "pff": 6, "value": "Mid 1st · crowded Philly room, talent is real"},
    {"name": "Jadarian Price", "pos": "RB", "team": "SEA", "dd": 6, "fp": 4, "pff": 4, "value": "Riser after draft · projected Seattle volume"},
    {"name": "KC Concepcion", "pos": "WR", "team": "CLE", "dd": 7, "fp": 8, "pff": None, "value": "Mid/late 1st · Jeanty-adjacent profile in comments"},
    {"name": "Ty Simpson", "pos": "QB", "team": "LAR", "dd": 11, "fp": 7, "pff": None, "value": "SF-only first · McVay development path"},
    {"name": "Kenyon Sadiq", "pos": "TE", "team": "NYJ", "dd": 8, "fp": 9, "pff": None, "value": "Late 1st TE1 of the class"},
    {"name": "Eli Stowers", "pos": "TE", "team": "PHI", "dd": 9, "fp": 11, "pff": None, "value": "Late 1st / early 2nd TE"},
    {"name": "Omar Cooper", "pos": "WR", "team": "NYJ", "dd": 10, "fp": 10, "pff": None, "value": "Turn-of-1st WR flyer"},
    {"name": "Jonah Coleman", "pos": "RB", "team": "DEN", "dd": 14, "fp": 10, "pff": None, "value": "Early 2nd · Denver committee"},
    {"name": "Denzel Boston", "pos": "WR", "team": "CLE", "dd": 12, "fp": 12, "pff": None, "value": "Early/mid 2nd"},
    {"name": "Antonio Williams", "pos": "WR", "team": "WAS", "dd": 13, "fp": None, "pff": None, "value": "Mid 2nd"},
    {"name": "Nick Singleton", "pos": "RB", "team": "TEN", "dd": 18, "fp": None, "pff": None, "value": "Mid 2nd committee back"},
    {"name": "Germie Bernard", "pos": "WR", "team": "PIT", "dd": 15, "fp": None, "pff": None, "value": "Mid 2nd"},
    {"name": "Chris Bell", "pos": "WR", "team": "MIA", "dd": 16, "fp": None, "pff": None, "value": "Mid/late 2nd"},
    {"name": "De'Zhaun Stribling", "pos": "WR", "team": "SF", "dd": 17, "fp": None, "pff": None, "value": "Late 2nd"},
    {"name": "Carson Beck", "pos": "QB", "team": "ARI", "dd": None, "fp": 19, "pff": None, "value": "Volatile SF 2nd/3rd · high STD DEV"},
    {"name": "Kaytron Allen", "pos": "RB", "team": "WAS", "dd": None, "fp": None, "pff": None, "value": "Day 3 / 3rd-round dart"},
]

HOT = [
    {"name": "Kyler Murray", "pos": "QB", "team": "MIN", "why": "DLF (Aug 16): healthy years were locked top-10 SF QBs; currently priced like a mid-1st rookie pick.", "src": "Dynasty League Football"},
    {"name": "Christian Watson", "pos": "WR", "team": "GB", "why": "Sports Arena + Draft Sharks: WR21 in FPPG Weeks 8–18 last year on a 68% route share; Doubs/Wicks gone.", "src": "Sports Arena, Draft Sharks"},
    {"name": "A.J. Brown", "pos": "WR", "team": "NE", "why": "Sports Arena: PFM WR14 vs FantasyPros ECR WR20. Buy for Luther Burden straight up.", "src": "Sports Arena / PFM"},
    {"name": "Trevor Lawrence", "pos": "QB", "team": "JAX", "why": "FantasyPros TVC + YouTube: closed the gap on Mahomes in the QB8-9 band after a 26 FPPG second half.", "src": "FantasyPros, Fantasy Footballers"},
    {"name": "Jordan Mason", "pos": "RB", "team": "MIN", "why": "Draft Sharks: cheap potential starter in a new Minnesota scheme; buy before a spike week.", "src": "Draft Sharks"},
    {"name": "Tucker Kraft", "pos": "TE", "team": "GB", "why": "FantasyPros: positive ACL reports; 25-year-old TE who looked top-4 before the injury.", "src": "FantasyPros"},
    {"name": "Zay Flowers", "pos": "WR", "team": "BAL", "why": "FantasyPros: new contract + 1,200 yards on a historically run-heavy Ravens offense; new OC hope.", "src": "FantasyPros"},
    {"name": "Harold Fannin Jr.", "pos": "TE", "team": "CLE", "why": "FantasyPros: FBS-leading receiving TE who popped as a rookie; new HC is a TE maven.", "src": "FantasyPros"},
    {"name": "TreVeyon Henderson", "pos": "RB", "team": "NE", "why": "Sports Arena: buy for a projected late 2027 1st. Youth + Patriots backfield.", "src": "Sports Arena"},
    {"name": "Christian McCaffrey", "pos": "RB", "team": "SF", "why": "Sports Arena for contenders only: PFM RB9 vs ECR RB15. Win-now buy, not a rebuild hold.", "src": "Sports Arena"},
]
COLD = [
    {"name": "Brian Thomas Jr.", "pos": "WR", "team": "JAX", "why": "DLF + Sports Arena: Jakobi Meyers + Parker Washington crowding targets. ADP still treats him like a high WR2.", "src": "DLF, Sports Arena"},
    {"name": "Breece Hall", "pos": "RB", "team": "NYJ", "why": "Sports Arena: sell if you can still get true top-10 RB value; efficiency/target share have slipped.", "src": "Sports Arena"},
    {"name": "Makai Lemon", "pos": "WR", "team": "PHI", "why": "Sports Arena: sell the rookie premium for Christian Watson. Philly room is packed.", "src": "Sports Arena"},
    {"name": "Luther Burden III", "pos": "WR", "team": "CHI", "why": "Sports Arena: ECR has him WR19; if that's the ask, move him for A.J. Brown.", "src": "Sports Arena"},
    {"name": "Davante Adams", "pos": "WR", "team": "LAR", "why": "Fantasy Footballers (YouTube): 33-year-old coming off a 14-TD outlier. Cash to a contender.", "src": "Fantasy Footballers"},
    {"name": "DJ Moore", "pos": "WR", "team": "BUF", "why": "Fantasy Footballers: 29, new team, 60-790 line last year. Sell the name.", "src": "Fantasy Footballers"},
    {"name": "Ricky Pearsall", "pos": "WR", "team": "SF", "why": "FantasyPros live update: out until ~next September, age 27 on return. Clear sell for win-now clubs.", "src": "FantasyPros"},
    {"name": "RJ Harvey", "pos": "RB", "team": "DEN", "why": "Draft Sharks: Broncos brought J.K. Dobbins back; not a locked lead back.", "src": "Draft Sharks"},
    {"name": "Rashee Rice", "pos": "WR", "team": "KC", "why": "Draft Sharks: Chiefs look run-leaning; sell while redraft boards still pay WR10-ish.", "src": "Draft Sharks"},
    {"name": "Jonathon Brooks", "pos": "RB", "team": "CAR", "why": "FantasyPros: two ACLs in 13 months, still unproven, market near RB26.", "src": "FantasyPros"},
]


def meta_map(pfn_rows):
    m = {}
    for r in pfn_rows:
        m[norm_name(r["name"])] = r
    return m


def bk_value(rank, qb_mult: float = 1.0) -> int:
    """Turn a 1-indexed list rank into Ball Keep trade value.

    Rank 1 is 12,000. Value falls on an exponential curve with a mild
    rank-power so the cliff from 1.01 to 1.02 is real, a late first sits
    near 28% of the 1.01, and rank 100 still has a tradable number.
    """
    if not rank or rank < 1:
        return 0
    raw = 12000 * math.exp(-0.0165 * (rank - 1)) / (rank ** 0.18)
    return max(1, int(round(raw * qb_mult)))


def fmt_val(n: int) -> str:
    return f"{int(n):,}"


def attach_values(rows, qb_mult_for_qb: float = 1.0):
    for r in rows:
        mult = qb_mult_for_qb if r.get("pos") == "QB" else 1.0
        r["value"] = bk_value(r.get("bk") or 0, mult)
    return rows


# Future firsts priced as equivalent ranks on the Superflex curve.
DYNASTY_PICKS = [
    ("2027 Early 1st", 8),
    ("2027 Mid 1st", 18),
    ("2027 Late 1st", 28),
    ("2027 Early 2nd", 36),
    ("2027 Mid 2nd", 44),
    ("2027 Late 2nd", 52),
    ("2027 3rd", 68),
    ("2028 Early 1st", 16),
    ("2028 Mid 1st", 26),
    ("2028 Late 1st", 36),
    ("2028 2nd", 54),
    ("2028 3rd", 80),
]


def pick_assets(qb_mult_for_qb: float = 1.0):
    out = []
    for name, rank in DYNASTY_PICKS:
        # Picks are not quarterbacks; always use the raw curve.
        out.append({
            "id": name.lower().replace(" ", "-"),
            "name": name,
            "pos": "PICK",
            "team": "",
            "rank": rank,
            "value": bk_value(rank, 1.0),
            "href": "",
        })
    return out


def aggregate(pfn_rows):
    sources = {
        "PFN (Katz/Soppe)": {norm_name(r["name"]): r["rank"] for r in pfn_rows},
        "Dynasty Nerds": {norm_name(n): r for n, r in DYNASTY_NERDS.items()},
        "FantasyPros ECR": {norm_name(n): r for n, r in FANTASYPROS_SF.items()},
        "KeepTradeCut SF": {norm_name(n): r for n, r in KTC_SF.items()},
        "ESPN (Karabell)": {norm_name(n): r for n, r in as_ranks(ESPN_KARABELL_SF).items()},
        "Draft Sharks": {norm_name(n): r for n, r in as_ranks(DRAFT_SHARKS_SF).items()},
        "RotoWire": {norm_name(n): r for n, r in as_ranks(ROTOWIRE_SF).items()},
    }
    for expert, board in FP_EXPERTS.items():
        sources[expert] = {norm_name(n): r for n, r in board.items()}
    meta = meta_map(pfn_rows)
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for key in names:
        ranks = {s: src[key] for s, src in sources.items() if key in src}
        if not ranks:
            continue
        avg = sum(ranks.values()) / len(ranks)
        # require at least one long board
        if "PFN (Katz/Soppe)" not in ranks and "Dynasty Nerds" not in ranks:
            continue
        info = meta.get(key, {})
        display = info.get("name")
        if not display:
            bank = (
                list(DYNASTY_NERDS)
                + list(KTC_SF)
                + list(FANTASYPROS_SF)
                + ESPN_KARABELL_SF
                + DRAFT_SHARKS_SF
                + ROTOWIRE_SF
            )
            for n in bank:
                if norm_name(n) == key:
                    display = n
                    break
        rows.append({
            "key": key,
            "name": display or key.title(),
            "pos": info.get("pos") or "",
            "team": info.get("team") or "",
            "age": info.get("age") or "",
            "avg": round(avg, 2),
            "n": len(ranks),
            "ranks": ranks,
        })
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    attach_values(rows)
    return rows, sources


def redraft_lists():
    karabell = as_ranks(ESPN_KARABELL_FLEX)
    ppr = []
    for i, (name, pos, team) in enumerate(YATES_PPR, 1):
        fp = FP_PPR.get(name)
        kb = karabell.get(name)
        nums = [float(i)]
        if fp:
            nums.append(float(fp))
        if kb:
            nums.append(float(kb))
        avg = sum(nums) / len(nums)
        ppr.append({
            "bk": 0,
            "name": name,
            "pos": pos,
            "team": team,
            "yates": i,
            "fp": fp or "—",
            "karabell": kb or "—",
            "n": len(nums),
            "avg": round(avg, 2),
        })
    ppr.sort(key=lambda r: r["avg"])
    for i, r in enumerate(ppr[:100], 1):
        r["bk"] = i
    attach_values(ppr[:100])
    # Standard: bump RB, slight WR/TE tax vs PPR
    std = []
    for r in ppr:
        adj = r["avg"]
        if r["pos"] == "RB":
            adj -= 4.5
        elif r["pos"] == "WR":
            adj += 3.0
        elif r["pos"] == "TE":
            adj += 2.0
        elif r["pos"] == "QB":
            adj += 0.5
        std.append({**r, "avg": round(adj, 2)})
    std.sort(key=lambda r: r["avg"])
    out = []
    for i, r in enumerate(std[:100], 1):
        out.append({**r, "bk": i})
    attach_values(out)
    return ppr[:100], out


NAV = [
    ("index.html", "Home"),
    ("the-keep.html", "The Keep"),
    ("trade.html", "Trade"),
    ("recent-trades.html", "Deals"),
    ("redraft-ppr.html", "Redraft PPR"),
    ("redraft-standard.html", "Redraft STD"),
    ("rookies-2026.html", "2026 Rookies"),
    ("hot-n-cold.html", "Hot 'n' Cold"),
    ("board.html", "The Board"),
    ("players/index.html", "Players"),
    ("nfl-schedule.html", "NFL"),
    ("mlb-schedule.html", "MLB"),
    ("discord.html", "Discord"),
]

PLAYER_PAGES = {}  # key -> slug


def slugify(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", norm_name(name))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def nav_href(target: str, depth: int) -> str:
    if depth == 0:
        return target
    if target.startswith("players/"):
        return target[len("players/") :]
    return "../" + target


def asset(path: str, depth: int) -> str:
    return ("../" * depth) + path


def player_url(name: str, depth: int = 0) -> str | None:
    slug = PLAYER_PAGES.get(norm_name(name))
    if not slug:
        return None
    return f"{slug}.html" if depth else f"players/{slug}.html"


def player_anchor(name: str, depth: int = 0) -> str:
    href = player_url(name, depth)
    if not href:
        return f"<strong>{esc(name)}</strong>"
    return f'<a class="player-link" href="{esc(href)}"><strong>{esc(name)}</strong></a>'


def wordmark():
    return '<span class="word-ball">BALL</span> <span class="word-keep">KEEP</span>'


def sources_panel(items):
    lis = []
    for name, url, note in items:
        if url:
            lis.append(f'<li><a href="{esc(url)}">{esc(name)}</a> — {esc(note)}</li>')
        else:
            lis.append(f"<li><strong>{esc(name)}</strong> — {esc(note)}</li>")
    return (
        '<section class="sources-box panel">'
        '<p class="kicker">Sources</p>'
        "<h3>Boards in This Aggregate</h3>"
        f"<ol>{''.join(lis)}</ol>"
        '<p class="note">Unranked names are skipped in the mean — never treated as 999. '
        "Short expert lists still move the names they actually ranked.</p>"
        "</section>"
    )


KEEP_SOURCES = [
    ("Pro Football Network (Katz / Soppe composite)", "https://www.profootballnetwork.com/dynasty-fantasy-football-rankings/", "Full Superflex dynasty board."),
    ("Dynasty Nerds Superflex", "https://www.dynastynerds.com/dynasty-rankings/superflex/", "Consensus of four rankers, weekly."),
    ("FantasyPros Dynasty Superflex ECR", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Published top 12, Aug 19."),
    ("KeepTradeCut Superflex", "https://keeptradecut.com/dynasty-rankings", "Crowdsourced market tape."),
    ("Derek Brown on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Aug 17 Superflex ranks via FantasyPros."),
    ("Andrew Erickson on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "July 29 Superflex ranks via FantasyPros."),
    ("Pat Fitzmaurice on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Aug 19 Superflex ranks via FantasyPros."),
    ("ESPN — Eric Karabell Superflex PPR", "https://www.espn.com/fantasy/football/story/_/id/47539664", "Updated Aug 17, 200 names."),
    ("Draft Sharks Superflex", "https://www.draftsharks.com/dynasty-rankings/superflex", "Aug 12 public top 25."),
    ("RotoWire Superflex", "https://www.rotowire.com/football/article/2026-dynasty-superflex-rankings-buy-low-values-adp-127901", "Aug 14 top 50 (team/pos board + named ranks)."),
]
PPR_SOURCES = [
    ("Field Yates, ESPN", "https://www.espn.com/fantasy/football/", "2026 full-PPR redraft board, updated Aug 17."),
    ("FantasyPros Redraft ECR", "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php", "Published top overlay, Aug 20."),
    ("ESPN — Eric Karabell Flex (no QB)", "https://www.espn.com/fantasy/football/story/_/id/47539664", "PPR skill-player board, Aug 17."),
]
ROOKIE_SOURCES = [
    ("Dynasty Dealer Superflex rookie board", "", "13-analyst team board, July 30."),
    ("FantasyPros Superflex Rookie ECR", "https://www.fantasypros.com/nfl/rankings/dynasty-rookies-superflex.php", "August consensus."),
    ("PFF Superflex Rookie Column", "https://www.pff.com/", "Love / Mendoza / Tate locked 1–2–3."),
]


def page(title, path, body, extra_js="", depth=0):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == path else ""
        links.append(f'<a href="{nav_href(href, depth)}"{cur}>{esc(label)}</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{esc(title)} — Ball Keep</title>
  <meta name="description" content="Ball Keep dynasty and redraft rankings, trade calculators, schedules, and market notes." />
  <link rel="stylesheet" href="{asset("css/site.css", depth)}" />
  <link rel="icon" href="{asset("img/logo.jpg", depth)}" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{nav_href("index.html", depth)}">
        <img src="{asset("img/logo.jpg", depth)}" alt="Ball Keep circular logo" />
        <div>
          <h1>{wordmark()}</h1>
          <p>Dynasty · Redraft · Ball</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {body}
    <footer>
      © {date.today().year} Ball Keep · ballkeep.com · Rankings aggregated {UPDATED}. Sources listed at the bottom of each board. Not affiliated with the NFL, MLB, or Premier League.
      <div><a class="sport-switch bb" href="{nav_href('bb/index.html', depth)}">BaseBallKeep</a>
      <a class="sport-switch pl" href="{nav_href('pl/index.html', depth)}">PitchKeep</a></div>
    </footer>
  </div>
  {extra_js}
</body>
</html>
"""


def rank_table(rows, extra_headers=None, extra_cells=None, depth=0):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    head = "".join(f"<th>{esc(h)}</th>" for h in ["BK", "Player", "Pos", "Team"] + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        body.append(
            f'<tr data-pos="{esc(pos)}">'
            f'<td class="rk">{r.get("bk","")}</td>'
            f"<td>{player_anchor(r['name'], depth)}</td>"
            f'<td><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f"<td>{esc(r.get('team',''))}</td>"
            f"{extra_cells(r)}"
            "</tr>"
        )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def write(path, html_doc):
    dest = ROOT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_doc)


def collect_profiles(keep, board, ppr, std):
    """Union of The Keep top 300, redraft top 50, rookies, and Hot/Cold."""
    players = OrderedDict()

    def add(name, pos, team, list_name, rank=None, extra=None, ranks=None, avg=None, n=None, age=None):
        k = norm_name(name)
        if k not in players:
            players[k] = {
                "key": k,
                "slug": slugify(name),
                "name": name,
                "pos": pos or "",
                "team": team or "",
                "age": age or "",
                "lists": {},
                "notes": [],
                "ranks": {},
                "keep_avg": avg,
                "keep_n": n,
            }
        p = players[k]
        if pos and not p["pos"]:
            p["pos"] = pos
        if team and not p["team"]:
            p["team"] = team
        if age and not p["age"]:
            p["age"] = age
        if ranks:
            p["ranks"] = ranks
        if avg is not None:
            p["keep_avg"] = avg
        if n is not None:
            p["keep_n"] = n
        p["lists"][list_name] = rank
        if extra:
            p["notes"].append(extra)

    for r in keep[:300]:
        add(r["name"], r["pos"], r["team"], "The Keep", r["bk"],
            f"The Keep #{r['bk']} · average {r['avg']} across {r['n']} Superflex boards",
            ranks=r["ranks"], avg=r["avg"], n=r["n"], age=r.get("age"))
    for r in board[:300]:
        add(r["name"], r["pos"], r["team"], "The Board", r["bk"],
            f"The Board #{r['bk']} on the long proprietary aggregate")
    for r in ppr[:50]:
        extra = f"Redraft PPR #{r['bk']} (Yates {r['yates']}" + (f", FantasyPros {r['fp']}" if r["fp"] != "—" else "") + ")"
        add(r["name"], r["pos"], r["team"], "Redraft PPR", r["bk"], extra)
    for r in std[:50]:
        add(r["name"], r["pos"], r["team"], "Redraft Standard", r["bk"],
            f"Redraft Standard #{r['bk']}")
    for i, r in enumerate(ROOKIES, 1):
        add(r["name"], r["pos"], r["team"], "2026 Rookies", i, r["value"])
    for i, r in enumerate(HOT, 1):
        add(r["name"], r["pos"], r["team"], "Hot", i, f"Hot #{i}: {r['why']} — {r['src']}")
    for i, r in enumerate(COLD, 1):
        add(r["name"], r["pos"], r["team"], "Cold", i, f"Cold #{i}: {r['why']} — {r['src']}")

    PLAYER_PAGES.clear()
    for k, p in players.items():
        PLAYER_PAGES[k] = p["slug"]
    return list(players.values())


def auto_plus_minus(p):
    plus, minus = [], []
    lists = p["lists"]
    if "The Keep" in lists and lists["The Keep"] <= 15:
        plus.append(f"Superflex first-rounder on The Keep (#{lists['The Keep']}).")
    if "The Keep" in lists and lists["The Keep"] >= 150:
        minus.append(f"Keep #{lists['The Keep']} — still on the 300, but the long-term case is thinner than the names above.")
    if "Hot" in lists:
        plus.append(next((n for n in p["notes"] if n.startswith("Hot")), "On the BK Hot board as a buy."))
    if "Cold" in lists:
        minus.append(next((n for n in p["notes"] if n.startswith("Cold")), "On the BK Cold board as a sell."))
    if "2026 Rookies" in lists and lists["2026 Rookies"] <= 5:
        plus.append(next((n for n in p["notes"] if n in [x["value"] for x in ROOKIES]), "Top-five name in the 2026 rookie class."))
    if len(lists) >= 4:
        plus.append("Shows up on four-plus Ball Keep lists — not a one-board meme.")
    if "The Keep" not in lists and ("Redraft PPR" in lists or "Redraft Standard" in lists):
        minus.append("A 2026 redraft name more than a 2029 Keep name — missing The Keep top 300.")
    if p.get("age") not in ("", None):
        try:
            age = int(p["age"])
            if p["pos"] == "RB" and age >= 27:
                minus.append(f"Age {age} at running back is a dynasty tax even when 2026 looks huge.")
            if p["pos"] == "WR" and age >= 30:
                minus.append(f"Age {age} at receiver is why win-now boards love him and The Keep is colder.")
            if p["pos"] == "QB" and age >= 30:
                minus.append(f"Age {age} at quarterback: still a starter, no longer a five-year 1.01 without a discount.")
            if age <= 24 and p["pos"] in ("QB", "WR", "TE", "RB"):
                plus.append(f"Age {age} — still on the right side of the dynasty curve.")
        except (TypeError, ValueError):
            pass
    ranks = p.get("ranks") or {}
    if ranks:
        vals = list(ranks.values())
        if max(vals) - min(vals) >= 15:
            spread = ", ".join(f"{s} {v}" for s, v in sorted(ranks.items(), key=lambda kv: kv[1])[:4])
            minus.append(f"Expert spread is wide ({spread}…). You are betting with one camp, not a unanimous tape.")
        if len(ranks) >= 6:
            plus.append(f"Ranked on {len(ranks)} Superflex sources — not a one-list darling.")
    return plus, minus


def render_player_pages(profiles):
    media = {}
    media_path = ROOT / "data" / "player_media.json"
    if media_path.exists():
        media = json.loads(media_path.read_text())
    out_dir = ROOT / "players"
    out_dir.mkdir(parents=True, exist_ok=True)

    cards = []
    missing_copy = []
    for p in profiles:
        copy = get_copy(p["key"])
        if not copy.get("grafs"):
            missing_copy.append(p["name"])
        med = media.get(p["key"], {})
        img = med.get("image") or ""
        yt = med.get("youtube_id") or ""
        yt_title = med.get("youtube_title") or "Highlight"
        college = med.get("college") or ""
        is_rook = bool(med.get("is_rookie")) or "2026 Rookies" in p["lists"]

        auto_p, auto_m = auto_plus_minus(p)
        plus = list(dict.fromkeys((copy.get("plus") or []) + auto_p))
        minus = list(dict.fromkeys((copy.get("minus") or []) + auto_m))
        # Keep unique-ish, cap
        plus = plus[:6]
        minus = minus[:6]

        chips = []
        for label, key in (
            ("The Keep", "The Keep"),
            ("Board", "The Board"),
            ("PPR", "Redraft PPR"),
            ("STD", "Redraft Standard"),
            ("Rookie", "2026 Rookies"),
            ("Hot", "Hot"),
            ("Cold", "Cold"),
        ):
            if key in p["lists"]:
                cls = " hot" if key == "Hot" else " cold" if key == "Cold" else ""
                chips.append(f'<span class="chip{cls}">{esc(label)} #{p["lists"][key]}</span>')
        if p.get("age"):
            chips.append(f'<span class="chip">Age {esc(p["age"])}</span>')
        if college and is_rook:
            chips.append(f'<span class="chip">{esc(college)}</span>')

        photo = ""
        if img:
            photo = f'<img src="{asset(img, 1)}" alt="{esc(p["name"])} headshot" />'
        else:
            photo = f'<img src="{asset("img/logo.jpg", 1)}" alt="" />'

        rank_bits = ""
        if p.get("ranks"):
            bits = "".join(
                f"<div><small>{esc(s)}</small> {v}</div>"
                for s, v in sorted(p["ranks"].items(), key=lambda kv: kv[1])
            )
            rank_bits = f'<div class="note" style="margin-top:10px"><strong>Superflex boards</strong>{bits}</div>'

        plus_li = "".join(f"<li>{esc(x)}</li>" for x in plus) or "<li>See the boards this player appears on.</li>"
        minus_li = "".join(f"<li>{esc(x)}</li>" for x in minus) or "<li>No loud sell notes on our tape — the rank is the comment.</li>"
        grafs = copy.get("grafs") or [
            f"{p['name']} is on the Ball Keep desk because The Keep, a redraft board, the rookie sheet, or Hot/Cold has him. The plus/minus above aggregates those list comments.",
            "Refresh this page with The Keep. Film and ranks move; the format split between Superflex dynasty and 1QB redraft does not.",
        ]
        analysis = "".join(f"<p>{esc(g)}</p>" for g in grafs)

        video = ""
        if yt:
            kind = "college" if is_rook else "2025 season"
            video = f"""
    <p class="kicker" style="margin-top:22px">Tape · {esc(kind)}</p>
    <h3>{esc(yt_title)}</h3>
    <p class="note">Best available public clip of a 2025 {"college" if is_rook else "NFL"} play. Not affiliated with the NFL, NCAA, or the posting channel.</p>
    <div class="video-wrap">
      <iframe src="https://www.youtube-nocookie.com/embed/{esc(yt)}" title="{esc(yt_title)}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen loading="lazy"></iframe>
    </div>"""

        same_pos = [x for x in profiles if x["pos"] == p["pos"] and x["key"] != p["key"]][:6]
        related = ""
        if same_pos:
            related = (
                '<p class="kicker" style="margin-top:22px">Same Position on This Hub</p><p>'
                + " · ".join(player_anchor(x["name"], 1) for x in same_pos)
                + "</p>"
            )

        body = f"""
    <p class="kicker">Player File · {esc(p["pos"])} {esc(p["team"])}</p>
    <div class="player-hero">
      {photo}
      <div>
        <h2>{esc(p["name"])}</h2>
        <p class="note">{esc(p["pos"])} · {esc(p["team"])}{" · " + esc(str(p["age"])) if p.get("age") else ""}{" · " + esc(college) if college and is_rook else ""}</p>
        <div class="chips">{''.join(chips)}</div>
        {rank_bits}
      </div>
    </div>
    <div class="plusminus">
      <div class="pm plus"><h3>Plus</h3><ul>{plus_li}</ul></div>
      <div class="pm minus"><h3>Minus</h3><ul>{minus_li}</ul></div>
    </div>
    <section class="panel analysis">
      <p class="kicker">Ball Keep Take</p>
      {analysis}
    </section>
    {video}
    {related}
    <p class="note" style="margin-top:18px"><a href="index.html">All player pages</a> · <a href="../the-keep.html">The Keep</a> · <a href="../recent-trades.html?q={esc(p["name"])}">Recent deals</a> · <a href="../hot-n-cold.html">Hot 'n' Cold</a></p>
    """
        write(f"players/{p['slug']}.html", page(p["name"], f"players/{p['slug']}.html", body, depth=1))

        thumb = asset(img, 1) if img else asset("img/logo.jpg", 1)
        cards.append(
            f'<a class="tile player-card" href="{p["slug"]}.html" data-pos="{esc(p.get("pos") or "")}">'
            f'<img src="{thumb}" alt="" />'
            f'<h3>{esc(p["name"])}</h3>'
            f'<p class="note">{esc(p["pos"])} {esc(p["team"])}</p></a>'
        )

    hub = f"""
    <p class="kicker">Depth Chart · {UPDATED}</p>
    <h2>Player Pages</h2>
    <p class="note">Every name in The Keep top 300, plus redraft top 50, the 2026 rookie sheet, and Hot 'n' Cold. Each file aggregates list comments into plus/minus, adds a few paragraphs on the Superflex vs Redraft split, and embeds a 2025 NFL play when we have the tape — or college tape for 2026 draftees.</p>
    <p class="note">Position</p>
    <div class="filters" id="hub-pos"><button type="button" class="active" data-pos="all">All</button>
      <button type="button" data-pos="QB">QB</button>
      <button type="button" data-pos="RB">RB</button>
      <button type="button" data-pos="WR">WR</button>
      <button type="button" data-pos="TE">TE</button>
    </div>
    <div class="player-grid">{''.join(cards)}</div>
    """
    hub_js = """<script>
    const box = document.getElementById('hub-pos');
    if (box) box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const p = b.dataset.pos;
      document.querySelectorAll('.player-grid .player-card').forEach(card => {
        card.style.display = (p === 'all' || card.dataset.pos === p) ? '' : 'none';
      });
    });
    </script>"""
    write("players/index.html", page("Players", "players/index.html", hub, hub_js, depth=1))

    urls = ["https://ballkeep.com/players/"] + [
        f"https://ballkeep.com/players/{p['slug']}.html" for p in profiles
    ]
    if missing_copy:
        print("missing copy", len(missing_copy), "(generic plus/minus used)")
    return urls


def as_trade_players(rows, qb_mult_for_qb=1.0):
    out = []
    for r in rows:
        mult = qb_mult_for_qb if r.get("pos") == "QB" else 1.0
        href = player_url(r["name"], 0) or ""
        out.append({
            "id": slugify(r["name"]),
            "name": r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "rank": r["bk"],
            "value": bk_value(r["bk"], mult),
            "href": href,
        })
    return out


def trade_mode_page(mode, payload):
    picks_note = (
        "Future firsts and seconds are priced as equivalent ranks on the same curve."
        if payload.get("picks")
        else "Redraft has no future picks — only the names on this board."
    )
    body = f"""
    <p class="kicker">Trade Calculator · {esc(payload["label"])}</p>
    <h2>{esc(payload["label"])}</h2>
    <p class="note">{esc(payload["blurb"])} {picks_note} Fair means the sides are within 8%.</p>
    <p class="filters">
      <a href="trade.html">All Calculators</a>
      <a href="trade-superflex.html"{' class="active"' if mode == "sf" else ""}>Superflex Dynasty</a>
      <a href="trade-1qb.html"{' class="active"' if mode == "oneqb" else ""}>1QB Dynasty</a>
      <a href="trade-ppr.html"{' class="active"' if mode == "ppr" else ""}>Redraft PPR</a>
      <a href="trade-standard.html"{' class="active"' if mode == "std" else ""}>Redraft Standard</a>
    </p>
    <div id="trade-app" class="trade-app"></div>
    """
    blob = json.dumps(payload, ensure_ascii=False)
    extra = f"<script>window.BK_TRADE = {blob};</script>\n<script src=\"js/trade.js\"></script>"
    write(payload["file"], page(payload["label"], payload["file"], body, extra))


def write_trade_pages(board, ppr, std):
    modes = {
        "sf": {
            "id": "sf",
            "file": "trade-superflex.html",
            "label": "Superflex Dynasty",
            "blurb": "Uses The Board ranks (same order as The Keep). Rank 1 is 12,000 BK Value. Quarterbacks keep full Superflex price.",
            "players": as_trade_players(board),
            "picks": pick_assets(),
        },
        "oneqb": {
            "id": "oneqb",
            "file": "trade-1qb.html",
            "label": "1QB Dynasty",
            "blurb": "Same Ball Keep ranks as Superflex, but quarterbacks are taxed to 38% of that value because there is no second QB slot.",
            "players": as_trade_players(board, 0.38),
            "picks": pick_assets(),
        },
        "ppr": {
            "id": "ppr",
            "file": "trade-ppr.html",
            "label": "Redraft PPR",
            "blurb": "Uses the Redraft PPR board rank. Same curve, one-year contest, no dynasty pick chips.",
            "players": as_trade_players(ppr),
            "picks": [],
        },
        "std": {
            "id": "std",
            "file": "trade-standard.html",
            "label": "Redraft Standard",
            "blurb": "Uses the Redraft Standard board rank after the PPR-to-Standard positional taxes.",
            "players": as_trade_players(std),
            "picks": [],
        },
    }
    (ROOT / "data/trade-values.json").write_text(json.dumps({
        "updated": UPDATED,
        "algorithm": "value = round(12000 * exp(-0.0165 * (rank-1)) / rank**0.18). 1QB multiplies QB value by 0.38. Picks map to equivalent ranks on that curve.",
        "modes": modes,
    }, indent=2, default=str))
    for key, payload in modes.items():
        trade_mode_page(key, payload)

    tiles = [
        ("trade-superflex.html", "Superflex Dynasty", "The Keep / The Board ranks. QBs are first-round assets."),
        ("trade-1qb.html", "1QB Dynasty", "Same ranks, quarterbacks taxed to 38% of Superflex value."),
        ("trade-ppr.html", "Redraft PPR", "One-year PPR board. No future picks."),
        ("trade-standard.html", "Redraft Standard", "One-year Standard board after the catch-tax."),
        ("recent-trades.html", "Recent Deals", "Type a player. Pull every package on the desk tape."),
    ]
    hub = f"""
    <p class="kicker">Trade Calculators</p>
    <h2>Four Calculators, One Curve</h2>
    <p class="note">Every name on a Ball Keep list has a rank. That rank becomes <strong>BK Value</strong>: rank 1 is 12,000, and the number falls on a decaying curve so the drop from 1 to 2 is larger than 50 to 51. A late first (~rank 28) is about 28% of the 1.01. Trade math is just adding those numbers on two sides.</p>
    <p class="note">Use Superflex for two-QB leagues, 1QB when a passer is just another starter, and the redraft calculators when the deal is for this season only.</p>
    <div class="grid" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    """
    write("trade.html", page("Trade Calculators", "trade.html", hub))


def write_recent_trades_page(deals):
    payload = json.dumps(deals, ensure_ascii=False)
    nicks = {
        "jsn": "jaxon smith-njigba",
        "jj": "justin jefferson",
        "cmc": "christian mccaffrey",
        "chase": "jamarr chase",
        "sun god": "amon-ra st brown",
        "arsb": "amon-ra st brown",
        "st brown": "amon-ra st brown",
        "btj": "brian thomas",
        "tlaw": "trevor lawrence",
        "bijan": "bijan robinson",
        "gibbs": "jahmyr gibbs",
        "puka": "puka nacua",
        "maye": "drake maye",
        "allen": "josh allen",
        "jeanty": "ashton jeanty",
        "mhj": "marvin harrison",
        "marv": "marvin harrison",
        "ceedee": "ceedee lamb",
        "cd": "ceedee lamb",
        "ajb": "a j brown",
        "bowers": "brock bowers",
        "saquon": "saquon barkley",
        "lamar": "lamar jackson",
        "mahomes": "patrick mahomes",
        "kyler": "kyler murray",
        "ladd": "ladd mcconkey",
        "tet": "tetairoa mcmillan",
        "breece": "breece hall",
        "cmcaffrey": "christian mccaffrey",
    }
    chips = [
        "Josh Allen", "Drake Maye", "Ja'Marr Chase", "Jaxon Smith-Njigba",
        "Jahmyr Gibbs", "Ashton Jeanty", "Brock Bowers", "Christian McCaffrey",
        "A.J. Brown", "Brian Thomas Jr.", "Kyler Murray",
    ]
    chip_html = "".join(
        f'<button type="button" class="deal-chip" data-q="{esc(n)}">{esc(n)}</button>'
        for n in chips
    )
    body = f"""
    <p class="kicker">Desk Tape · {UPDATED}</p>
    <h2>Recent Deals</h2>
    <p class="note">Type a player. We pull every package on the tape that names him — Superflex, 1QB, asking prices from Hot 'n' Cold, and the deals Sleeper chats actually closed this month. Not a scrape of 200,000 leagues. A powder-blue log with BK Value on both sides so you can see if the room was drunk.</p>
    <div class="trade-search deals-search">
      <label for="deal-q">Player</label>
      <input id="deal-q" type="search" placeholder="JSN, CMC, Sun God, Jeanty…" autocomplete="off" />
      <p class="note" id="deal-status" style="margin:10px 0 0"></p>
      <div class="filters" style="margin-top:12px">
        <button type="button" class="active" data-fmt="all">All formats</button>
        <button type="button" data-fmt="sf">Superflex</button>
        <button type="button" data-fmt="oneqb">1QB</button>
        <button type="button" data-kind="all" class="active">Closed + asking</button>
        <button type="button" data-kind="closed">Closed</button>
        <button type="button" data-kind="asking">Asking price</button>
      </div>
      <p class="note" style="margin-top:8px">Jump</p>
      <div class="filters">{chip_html}</div>
    </div>
    <div id="deal-list"></div>
    """
    extra = f"""<script>
    const DEALS = {payload};
    const NICKS = {json.dumps(nicks)};
    function norm(s) {{
      let n = (s || '').toLowerCase().replace(/[.'’]/g, ' ').replace(/\\b(jr|sr|iii|ii|iv)\\b/g, ' ');
      n = n.replace(/\\s+/g, ' ').trim();
      return NICKS[n] || n;
    }}
    function fmt(n) {{ return (n || 0).toLocaleString(); }}
    function sideHtml(items, q) {{
      return items.map(x => {{
        const hit = q && norm(x.name).includes(q);
        const meta = x.kind === 'pick' ? 'Pick' : ((x.pos || '') + ' ' + (x.team || '')).trim();
        return '<li class="' + (hit ? 'deal-hit' : '') + '"><strong>' + x.name + '</strong>' +
          (meta ? '<small>' + meta + '</small>' : '') +
          '<span class="val">' + fmt(x.value) + '</span></li>';
      }}).join('');
    }}
    let fmtFilter = 'all', kindFilter = 'all';
    function render() {{
      const raw = document.getElementById('deal-q').value;
      const q = norm(raw);
      const rows = DEALS.filter(d => {{
        const okF = fmtFilter === 'all' || d.format_id === fmtFilter;
        const okK = kindFilter === 'all' || d.kind === kindFilter;
        if (!okF || !okK) return false;
        if (!q) return true;
        return d.names.some(n => norm(n).includes(q) || q.includes(norm(n)));
      }});
      const status = document.getElementById('deal-status');
      if (q) {{
        status.textContent = rows.length
          ? rows.length + ' deal' + (rows.length === 1 ? '' : 's') + ' involving ' + raw.trim() + '.'
          : 'Nobody on the tape named ' + raw.trim() + '. Try Chase, Maye, Jeanty, JSN.';
      }} else {{
        status.textContent = rows.length + ' packages on the tape. Newest first.';
      }}
      const root = document.getElementById('deal-list');
      if (!rows.length) {{
        root.innerHTML = '<div class="panel"><p class="note">Empty drawer. Clear the search or pick a chip.</p></div>';
        return;
      }}
      root.innerHTML = rows.map(d => {{
        const cls = d.label === 'Fair Trade' ? 'fair' : (d.label.indexOf('A') >= 0 ? 'a' : 'b');
        const tag = d.kind === 'asking' ? 'Asking price' : 'Closed';
        return '<article class="deal ' + cls + '">' +
          '<header><p class="kicker" style="margin:0">' + d.date + ' · ' + d.format + ' · ' + tag + '</p>' +
          '<h3>' + d.label + '</h3>' +
          '<p class="note">' + d.league + ' · ' + d.source + '</p></header>' +
          '<div class="deal-grid">' +
            '<div class="deal-side"><h4>Side A · ' + fmt(d.total_a) + '</h4><ul>' + sideHtml(d.a, q) + '</ul></div>' +
            '<p class="deal-vs">vs</p>' +
            '<div class="deal-side"><h4>Side B · ' + fmt(d.total_b) + '</h4><ul>' + sideHtml(d.b, q) + '</ul></div>' +
          '</div>' +
          '<p class="deal-blurb">' + d.blurb + '</p>' +
          '<p class="note"><a href="trade-superflex.html">Run it on the calculator</a></p>' +
        '</article>';
      }}).join('');
    }}
    document.getElementById('deal-q').addEventListener('input', render);
    document.querySelectorAll('.deals-search [data-fmt]').forEach(b => b.addEventListener('click', () => {{
      document.querySelectorAll('.deals-search [data-fmt]').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); fmtFilter = b.dataset.fmt; render();
    }}));
    document.querySelectorAll('.deals-search [data-kind]').forEach(b => b.addEventListener('click', () => {{
      document.querySelectorAll('.deals-search [data-kind]').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); kindFilter = b.dataset.kind; render();
    }}));
    document.querySelectorAll('.deal-chip').forEach(b => b.addEventListener('click', () => {{
      document.getElementById('deal-q').value = b.dataset.q; render();
    }}));
    const params = new URLSearchParams(location.search);
    if (params.get('q')) document.getElementById('deal-q').value = params.get('q');
    render();
    </script>"""
    write("recent-trades.html", page("Recent Deals", "recent-trades.html", body, extra))


def main():
    pfn = parse_pfn(ROOT / "data/pfn-dynasty.txt")
    nfl = parse_nfl_schedule(ROOT / "data/nfl-schedule.txt")
    board, sources = aggregate(pfn)
    keep = board[:300]
    ppr, std = redraft_lists()
    profiles = collect_profiles(keep, board, ppr, std)
    (ROOT / "data" / "player_roster.json").write_text(json.dumps(profiles, indent=2))

    (ROOT / "data/the-keep.json").write_text(json.dumps({
        "updated": UPDATED,
        "sources": list(sources),
        "players": keep,
    }, indent=2))
    (ROOT / "data/board.json").write_text(json.dumps(board, indent=2))

    write_trade_pages(board, ppr, std)
    deals = enrich_deals(board, bk_value, pick_assets(), norm_name)
    write_recent_trades_page(deals)

    # HOME
    tiles = [
        ("the-keep.html", "The Keep", "Daily Superflex dynasty top 300. Our keystone board."),
        ("trade.html", "Trade Calculators", "Four calculators. Rank becomes BK Value. Add two sides."),
        ("recent-trades.html", "Recent Deals", "Type a name. See the Superflex packages he actually moved in."),
        ("redraft-ppr.html", "Redraft PPR", "2026 startup board for full-PPR redraft."),
        ("redraft-standard.html", "Redraft Standard", "Same season, no reception point. Different order."),
        ("rookies-2026.html", "2026 Rookies", "Drafted class consensus ranks and Superflex values."),
        ("hot-n-cold.html", "BK Hot 'n' Cold", "Buys and sells scraped from dynasty desks and film shows."),
        ("board.html", "The Board", "The long proprietary aggregate — every ranked name we pulled."),
        ("players/index.html", "Player Pages", "Keep top 300: plus/minus, tape, and a 2025 or college clip."),
        ("nfl-schedule.html", "NFL Schedules", "2026 week-by-week slate and all 32 team pages."),
        ("mlb-schedule.html", "MLB Schedules", "September stretch run, filterable by club."),
        ("discord.html", "Discord", "The circular mark plus a bot that searches ranks, runs the calculator, drops tape, and can publish the whole site into a server."),
        ("bb/index.html", "BaseBallKeep", "Navy diamond desk. Keep 300, Lineup, Pitchers, bullpen, redraft."),
        ("pl/index.html", "PitchKeep", "Premier League purple. The Pitch top 250, FPL files, tape."),
    ]
    home_body = f"""
    <section class="hero" style="background-image:url('img/hero.jpg')">
      <div class="hero-card">
        <p class="kicker" style="color:#ffd4db">Updated {UPDATED}</p>
        <h2>{wordmark()}</h2>
        <p>A powder-blue desk for dynasty and redraft. Football first. Baseball in season. Premier League next door. One board, many experts, no fluff.</p>
      </div>
    </section>
    <section class="panel">
      <p class="kicker">What This Site Is</p>
      <h2>Keep the guys who still matter in 2029.</h2>
      <p class="note"><strong>Fantasy Football</strong> is a one-year contest: you draft, you stream, you chase weekly points. <strong>Dynasty Football</strong> is a roster you keep. Young quarterbacks, incoming rookies, and contract years all change the price. Superflex (a second QB slot) makes passers first-round assets instead of round-eight afterthoughts.</p>
      <p class="note"><strong>Fantasy Baseball</strong> is the same split. Redraft/roto is this summer's counting stats. <strong>Dynasty Baseball</strong> prices the next five years — peak age, service time, and whether a 22-year-old shortstop is still a shortstop in 2030. ESPN's current dynasty formula weights 2027–2030 at 80% of value.</p>
      <p class="note">Ball Keep aggregates public expert boards (FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN Karabell, Draft Sharks, RotoWire, plus X ranks from Brown / Erickson / Fitzmaurice) into one number, then turns that rank into BK Value for the trade calculators. We do not pretend a podcast hot take is a 300-player sheet. Sources sit at the bottom of each board. Baseball lives in <a href="bb/index.html">BaseBallKeep</a>. The Premier League lives in <a href="pl/index.html">PitchKeep</a> — purple, pitch green, and The Pitch top 250.</p>
    </section>
    <div class="grid-3" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    """
    write("index.html", page("Home", "index.html", home_body))

    # THE KEEP
    def keep_extra(r):
        return f'<td>{r["avg"]}</td><td>{r["n"]}</td><td class="val">{fmt_val(r["value"])}</td>'
    keep_body = f"""
    <p class="kicker">Keystone · Superflex Dynasty</p>
    <h2>The Keep</h2>
    <p class="note">Top 300 for Superflex dynasty leagues, rebuilt {UPDATED}. Ball Keep rank is the average of every source that ranked the player. BK Value is that rank on a decaying curve (12,000 at 1.01). Filter by position. Per-source ranks live in the source list at the bottom so the board stays readable.</p>
    <p class="note">Position</p>
    <div class="filters" id="keep-pos"><button type="button" class="active" data-pos="all">All</button>
      <button type="button" data-pos="QB">QB</button>
      <button type="button" data-pos="RB">RB</button>
      <button type="button" data-pos="WR">WR</button>
      <button type="button" data-pos="TE">TE</button>
    </div>
    <div class="panel">{rank_table(keep, ["Avg", "# Boards", "BK Value"], keep_extra)}</div>
    {sources_panel(KEEP_SOURCES)}
    """
    keep_js = """<script>
    const box = document.getElementById('keep-pos');
    box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const p = b.dataset.pos;
      document.querySelectorAll('tbody tr').forEach(tr => {
        tr.style.display = (p === 'all' || tr.dataset.pos === p) ? '' : 'none';
      });
    });
    </script>"""
    write("the-keep.html", page("The Keep", "the-keep.html", keep_body, keep_js))

    # REDRAFT
    def ppr_extra(r):
        return f'<td>{r["yates"]}</td><td>{r["fp"]}</td><td>{r["karabell"]}</td><td class="val">{fmt_val(r["value"])}</td>'
    ppr_body = f"""
    <p class="kicker">2026 Redraft · PPR</p>
    <h2>Redraft PPR</h2>
    <p class="note">Full-PPR, 1QB. Consensus of Field Yates (ESPN, Aug 17), FantasyPros Expert Consensus where published, and Eric Karabell's Flex board (Aug 17). Kickers and DST from Yates are omitted so this stays a skill-player draft sheet. BK Value uses this list's rank on the same curve as dynasty.</p>
    <div class="panel">{rank_table(ppr, ["Yates", "FP ECR", "Karabell", "BK Value"], ppr_extra)}</div>
    {sources_panel(PPR_SOURCES)}
    """
    write("redraft-ppr.html", page("Redraft PPR", "redraft-ppr.html", ppr_body))

    std_body = f"""
    <p class="kicker">2026 Redraft · Standard</p>
    <h2>Redraft Standard</h2>
    <p class="note">Standard (no extra point per catch) is a different sport than PPR. We start from the PPR consensus above, then apply Ball Keep positional taxes used across major STD vs PPR deltas: running backs −4.5 ranks, receivers +3, tight ends +2, quarterbacks +0.5. Result: Bijan / Gibbs / CMC / Henry / Taylor climb; Chase / Puka / JSN still go early but not as automatic 1.01s.</p>
    <div class="panel">{rank_table(std, ["Adj. Score", "BK Value"], lambda r: f'<td>{r["avg"]}</td><td class="val">{fmt_val(r["value"])}</td>')}</div>
    {sources_panel(PPR_SOURCES + [("Ball Keep Standard Tax", "", "RB −4.5 ranks, WR +3, TE +2, QB +0.5 applied to the PPR consensus.")])}
    """
    write("redraft-standard.html", page("Redraft Standard", "redraft-standard.html", std_body))

    # ROOKIES
    rook_rows = []
    for r in ROOKIES:
        nums = [x for x in (r["dd"], r["fp"], r["pff"]) if x]
        avg = round(sum(nums) / len(nums), 2) if nums else 99.0
        rook_rows.append({**r, "bk": 0, "avg": avg, "dd": r["dd"] or "—", "fp": r["fp"] or "—", "pff": r["pff"] or "—", "blurb": r["value"]})
    rook_rows.sort(key=lambda r: r["avg"])
    for i, r in enumerate(rook_rows, 1):
        r["bk"] = i
    attach_values(rook_rows)
    rook_body = f"""
    <p class="kicker">2026 NFL Draft Class</p>
    <h2>Notable Drafted Rookies</h2>
    <p class="note">Superflex rookie consensus from Dynasty Dealer (13-analyst team board, July 30), FantasyPros Superflex Rookie ECR (August), and PFF's Superflex rookie column (Love / Mendoza / Tate locked 1-2-3). BK Value uses this rookie-board rank on the same curve as The Keep. The note is startup / rookie-draft language, not salary-cap dollars.</p>
    <div class="panel">{rank_table(rook_rows, ["Avg", "Dealer", "FP", "PFF", "BK Value", "Note"], lambda r: f'<td>{r["avg"]}</td><td>{r["dd"]}</td><td>{r["fp"]}</td><td>{r["pff"]}</td><td class="val">{fmt_val(r["value"])}</td><td class="note">{esc(r["blurb"])}</td>')}</div>
    {sources_panel(ROOKIE_SOURCES)}
    """
    write("rookies-2026.html", page("2026 Rookies", "rookies-2026.html", rook_body))

    # HOT COLD
    def hc_cards(items, cls):
        out = []
        for i, x in enumerate(items, 1):
            out.append(
                f'<article class="tile {cls}"><span class="badge">{i}</span> '
                f'<h3>{player_anchor(x["name"])} <span class="pos {esc(x["pos"])}">{esc(x["pos"])}</span> {esc(x["team"])}</h3>'
                f'<p>{esc(x["why"])}</p><p class="note">Source: {esc(x["src"])}</p></article>'
            )
        return "".join(out)
    hc_body = f"""
    <p class="kicker">Market Tape · {UPDATED}</p>
    <h2>BK Hot 'n' Cold</h2>
    <p class="note">Rising names to Buy and aging / overpriced names to Sell, pulled from DLF trending notes (Aug 16), Sports Arena trade targets (Aug 11), Draft Sharks (Aug 14), FantasyPros Trade Value Chart show (August), and the Fantasy Footballers dynasty trade episode on YouTube.</p>
    <div class="grid">
      <div>
        <h3 style="color:var(--red)">Hot — Buy</h3>
        {hc_cards(HOT, "hot")}
      </div>
      <div>
        <h3 style="color:#1d4f8a">Cold — Sell</h3>
        {hc_cards(COLD, "cold")}
      </div>
    </div>
    {sources_panel([
        ("Dynasty League Football", "", "Trending notes, Aug 16."),
        ("Sports Arena", "", "Trade targets, Aug 11."),
        ("Draft Sharks", "https://www.draftsharks.com/dynasty-rankings/superflex", "Aug 14 market notes."),
        ("FantasyPros Trade Value Chart", "https://www.fantasypros.com/", "August show."),
        ("Fantasy Footballers", "", "Dynasty trade episode on YouTube."),
    ])}
    """
    write("hot-n-cold.html", page("Hot 'n' Cold", "hot-n-cold.html", hc_body))

    # LONG BOARD
    def board_extra(r):
        return f'<td>{r["avg"]}</td><td>{r["n"]}</td><td class="val">{fmt_val(r["value"])}</td>'
    board_body = f"""
    <p class="kicker">Proprietary Aggregate</p>
    <h2>The Board</h2>
    <p class="note">Every player we could pin to at least one full Superflex dynasty board, ordered by Ball Keep average. This is the long file we will refresh with The Keep. Methodology: simple mean of published ranks; unranked sources are skipped (not treated as 999). That slightly favors household names who appear on short expert lists — which is the point of a consensus tape, not a recency-weighted model. Individual source columns used to live in this table; they now live in the source list below.</p>
    <div class="panel">{rank_table(board, ["Avg", "# Boards", "BK Value"], board_extra)}</div>
    {sources_panel(KEEP_SOURCES)}
    """
    write("board.html", page("The Board", "board.html", board_body))

    # NFL schedule
    weeks = sorted({g["week"] for g in nfl})
    nfl_js_games = json.dumps(nfl)
    week_btns = "".join(f'<button type="button" data-week="{w}">W{w}</button>' for w in weeks)
    team_btns = "".join(
        f'<button type="button" data-team="{esc(abbr)}">{esc(abbr)}</button>'
        for abbr in sorted(TEAM_BY_ABBR)
    )
    nfl_body = f"""
    <p class="kicker">2026 NFL Regular Season</p>
    <h2>NFL Schedule</h2>
    <p class="note">Full slate from NFL Football Operations (released May 14). Kickoff is Wednesday, Sept. 9 in Seattle. Filter by week or club for the individual team schedule. International sites: Melbourne, Rio, London, Paris, Madrid, Munich, Mexico City.</p>
    <p class="note">Weeks</p>
    <div class="filters" id="weeks"><button type="button" class="active" data-week="all">All</button>{week_btns}</div>
    <p class="note">Teams</p>
    <div class="filters" id="teams"><button type="button" class="active" data-team="all">All clubs</button>{team_btns}</div>
    <div class="panel" id="games"></div>
    """
    nfl_js = f"""<script>
    const GAMES = {nfl_js_games};
    const ABBR = {json.dumps(TEAMS)};
    let week = 'all', team = 'all';
    function render() {{
      const rows = GAMES.filter(g => {{
        const wa = ABBR[g.away], wh = ABBR[g.home];
        const okW = week === 'all' || String(g.week) === String(week);
        const okT = team === 'all' || wa === team || wh === team;
        return okW && okT;
      }});
      const body = rows.map(g => {{
        const loc = g.note ? ` (${{g.note}})` : '';
        const line = g.prep === 'at' ? `${{g.away}} at ${{g.home}}` : `${{g.away}} vs ${{g.home}}`;
        return `<tr><td>W${{g.week}}</td><td>${{g.day}}</td><td><strong>${{line}}</strong>${{loc}}</td><td>${{g.time}} ET</td><td>${{g.tv}}</td></tr>`;
      }}).join('');
      document.getElementById('games').innerHTML = `<table><thead><tr><th>Wk</th><th>Day</th><th>Matchup</th><th>Time</th><th>TV</th></tr></thead><tbody>${{body}}</tbody></table>`;
    }}
    function bind(id, key, setter) {{
      document.getElementById(id).addEventListener('click', e => {{
        const b = e.target.closest('button'); if (!b) return;
        document.querySelectorAll('#' + id + ' button').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        setter(b.dataset[key]);
        render();
      }});
    }}
    bind('weeks', 'week', v => week = v);
    bind('teams', 'team', v => team = v);
    render();
    </script>"""
    write("nfl-schedule.html", page("NFL Schedule", "nfl-schedule.html", nfl_body, nfl_js))

    # MLB September
    mlb_games = []
    mlb_html = ROOT / "data/mlb-september.html"
    if mlb_html.exists():
        day = ""
        blob = mlb_html.read_text(errors="replace")
        for token in re.finditer(
            r'<h4 class="amazon passion toptop">([^<]+)</h4>|<span class="right devil">([^<]+)</span>\s*<img[^>]+>\s*<span class="small">([A-Z]{2,3})</span>\s*<span[^>]*>@</span>\s*<img[^>]+>\s*<span class="small">([A-Z]{2,3})</span>',
            blob,
        ):
            if token.group(1):
                day = token.group(1).strip()
            elif day:
                mlb_games.append({
                    "day": day,
                    "time": token.group(2).strip(),
                    "away": token.group(3),
                    "home": token.group(4),
                })
    mlb_abbrs = sorted({g["away"] for g in mlb_games} | {g["home"] for g in mlb_games})
    mlb_btns = "".join(f'<button type="button" data-team="{esc(a)}">{esc(a)}</button>' for a in mlb_abbrs)
    mlb_body = f"""
    <p class="kicker">MLB · Stretch Run</p>
    <h2>Baseball Schedules</h2>
    <p class="note">Today is Aug. 20, 2026 — the regular season wraps Sunday, Sept. 27. Below is the full September slate (Fantasy Nerds / league schedule). Filter by club for that team's remaining games. For the live daily tick, use ESPN's MLB scoreboard. Dynasty baseball prices 2027–2031 heavier than this month's box score; redraft baseball is only this month.</p>
    <div class="filters" id="mlb-teams"><button type="button" class="active" data-team="all">All clubs</button>{mlb_btns}</div>
    <div class="panel" id="mlb-games"></div>
    """
    mlb_js = f"""<script>
    const MLB = {json.dumps(mlb_games)};
    let team = 'all';
    function render() {{
      const rows = MLB.filter(g => team === 'all' || g.away === team || g.home === team)
        .map(g => `<tr><td>${{g.day}}</td><td><strong>${{g.away}} @ ${{g.home}}</strong></td><td>${{g.time}}</td></tr>`).join('');
      document.getElementById('mlb-games').innerHTML = `<table><thead><tr><th>Date</th><th>Matchup</th><th>Time</th></tr></thead><tbody>${{rows}}</tbody></table>`;
    }}
    document.getElementById('mlb-teams').addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      document.querySelectorAll('#mlb-teams button').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); team = b.dataset.team; render();
    }});
    render();
    </script>"""
    write("mlb-schedule.html", page("MLB Schedule", "mlb-schedule.html", mlb_body, mlb_js))

    # Discord
    disc = """
    <div class="panel discord-hero">
      <img src="img/discord.jpg" alt="Ball Keep circular Discord logo" />
      <p class="kicker">Community</p>
      <h2>Ball Keep on Discord</h2>
      <p class="note">Red primary. White BK. Black ring. The bot is the desk in the server: every Keep rank, every player file, every highlight, and the trade calculator — searchable in Discord the same way they are on the site.</p>
      <a class="cta" href="https://github.com/balsalah51/BallKeep/tree/main/bot">Run the Ball Keep bot</a>
    </div>
    <section class="panel" style="margin-top:16px">
      <p class="kicker">Slash Commands</p>
      <h2>Talk to the desk.</h2>
      <p class="note"><code>/player Josh Allen</code> pulls The Keep rank, BK Value, plus/minus, the 2025 clip, and the player page. <code>/trade</code> is the Superflex / 1QB / PPR / Standard calculator. <code>/deals JSN</code> pulls every recent package on the desk tape. <code>/bbplayer Ohtani</code> is the same file on the baseball desk. <code>/plplayer Haaland</code> is the PitchKeep file — The Pitch rank, picture, long take, 2025/26 tape. <code>/video</code> drops the tape. <code>/quiz</code> hides a Keep rank behind a spoiler. <code>/publish</code> writes the whole site into Discord channels so native search works.</p>
      <div class="grid" style="margin-top:14px">
        <article class="tile"><h3>/player</h3><p>Full file: ranks, value, plus/minus, tape, link.</p></article>
        <article class="tile"><h3>/trade</h3><p>Two sides. Same BK Value curve as the site.</p></article>
        <article class="tile"><h3>/deals</h3><p>Type a name. Every recent package on the desk tape.</p></article>
        <article class="tile"><h3>/video</h3><p>2025 NFL or college highlight from the player page.</p></article>
        <article class="tile"><h3>/keep-or-cut</h3><p>Theatrical buy/sell with Hot 'n' Cold and The Keep.</p></article>
        <article class="tile"><h3>/top + /pos</h3><p>Leaderboards, or just the QBs / RBs / WRs / TEs.</p></article>
        <article class="tile"><h3>/quiz + /hottake</h3><p>Guess a Keep rank. Draw a random buy or sell.</p></article>
        <article class="tile"><h3>/start + /picks</h3><p>Redraft start/sit, plus every future-pick value.</p></article>
        <article class="tile"><h3>/bbplayer</h3><p>BaseBallKeep file: Keep 300, Lineup, Pitchers, redraft.</p></article>
        <article class="tile"><h3>/bbkeep + /bbwire</h3><p>Diamond boards and the longer redraft waiver list.</p></article>
        <article class="tile"><h3>/plplayer</h3><p>PitchKeep file: The Pitch 250, FPL line, long take, tape.</p></article>
        <article class="tile"><h3>/pitch + /pltrade</h3><p>Premier League boards and the PitchKeep calculator.</p></article>
      </div>
    </section>
    """
    write("discord.html", page("Discord", "discord.html", disc))

    player_urls = render_player_pages(profiles)
    sitemap = [
        "https://ballkeep.com/",
        "https://ballkeep.com/the-keep.html",
        "https://ballkeep.com/trade.html",
        "https://ballkeep.com/recent-trades.html",
        "https://ballkeep.com/trade-superflex.html",
        "https://ballkeep.com/trade-1qb.html",
        "https://ballkeep.com/trade-ppr.html",
        "https://ballkeep.com/trade-standard.html",
        "https://ballkeep.com/redraft-ppr.html",
        "https://ballkeep.com/redraft-standard.html",
        "https://ballkeep.com/rookies-2026.html",
        "https://ballkeep.com/hot-n-cold.html",
        "https://ballkeep.com/board.html",
        "https://ballkeep.com/nfl-schedule.html",
        "https://ballkeep.com/mlb-schedule.html",
        "https://ballkeep.com/discord.html",
    ] + player_urls
    bb = write_baseball_site()
    sitemap.extend(bb.get("urls") or [])
    pl = write_pitch_site()
    sitemap.extend(pl.get("urls") or [])
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap)
        + "</urlset>\n"
    )

    cat = write_discord_catalog(keep, board, ppr, std, rook_rows, profiles, nfl, mlb_games, deals, bb, pl)
    print(
        f"Keep {len(keep)} Board {len(board)} NFL games {len(nfl)} MLB {len(mlb_games)} "
        f"Players {len(profiles)} BB Keep {bb['n_keep']} Pitch {pl['n_pitch']} Catalog {cat.name}"
    )


def slim_row(r, extra=()):
    out = {
        "name": r.get("name"),
        "pos": r.get("pos") or "",
        "team": r.get("team") or "",
        "bk": r.get("bk"),
        "avg": r.get("avg"),
        "n": r.get("n"),
        "value": r.get("value"),
    }
    for k in extra:
        if k in r:
            out[k] = r[k]
    return out


def write_discord_catalog(keep, board, ppr, std, rook_rows, profiles, nfl, mlb_games, deals=None, bb=None, pl=None):
    """One JSON pack the Discord bot reads instead of scraping HTML."""
    media = {}
    media_path = ROOT / "data/player_media.json"
    if media_path.exists():
        media = json.loads(media_path.read_text())
    files = []
    for p in profiles:
        copy = get_copy(p["key"])
        med = media.get(p["key"], {})
        files.append({
            "key": p["key"],
            "slug": p["slug"],
            "name": p["name"],
            "pos": p.get("pos") or "",
            "team": p.get("team") or "",
            "age": p.get("age") or "",
            "lists": p.get("lists") or {},
            "notes": p.get("notes") or [],
            "ranks": p.get("ranks") or {},
            "keep_avg": p.get("keep_avg"),
            "keep_n": p.get("keep_n"),
            "plus": copy.get("plus") or [],
            "minus": copy.get("minus") or [],
            "grafs": copy.get("grafs") or [],
            "image": med.get("image") or "",
            "youtube_id": med.get("youtube_id") or "",
            "youtube_title": med.get("youtube_title") or "",
            "youtube_channel": med.get("youtube_channel") or "",
            "college": med.get("college") or "",
            "is_rookie": bool(med.get("is_rookie")),
            "sport": "football",
            "url": f"https://ballkeep.com/players/{p['slug']}.html",
        })
    catalog = {
        "updated": UPDATED,
        "site": "https://ballkeep.com",
        "algorithm": "value = round(12000 * exp(-0.0165 * (rank-1)) / rank**0.18). 1QB multiplies QB value by 0.38.",
        "sources": [name for name, _url, _note in KEEP_SOURCES],
        "keep": [slim_row(r, ("ranks", "age")) for r in keep],
        "board": [slim_row(r) for r in board],
        "ppr": [slim_row(r, ("yates", "fp", "karabell")) for r in ppr],
        "standard": [slim_row(r) for r in std],
        "rookies": [slim_row(r, ("dd", "fp", "pff", "blurb")) for r in rook_rows],
        "hot": HOT,
        "cold": COLD,
        "picks": pick_assets(),
        "deals": deals or [],
        "players": files,
        "nfl": [
            {**g, "away_abbr": TEAMS.get(g["away"], ""), "home_abbr": TEAMS.get(g["home"], "")}
            for g in nfl
        ],
        "mlb": mlb_games,
    }
    bb = bb or {}
    catalog["bb_keep"] = [slim_row(r, ("age", "group")) for r in bb.get("keep") or []]
    catalog["bb_lineup"] = [slim_row(r, ("age", "group")) for r in bb.get("lineup") or []]
    catalog["bb_pitchers"] = [slim_row(r, ("age", "group")) for r in bb.get("pitchers") or []]
    catalog["bb_saves"] = [slim_row(r) for r in bb.get("saves") or []]
    catalog["bb_svh"] = [slim_row(r) for r in bb.get("svh") or []]
    catalog["bb_redraft"] = [slim_row(r, ("age", "group")) for r in bb.get("redraft") or []]
    catalog["bb_picks"] = bb.get("picks") or []
    catalog["bb_players"] = bb.get("files") or []
    catalog["bb_waivers_dynasty"] = bb.get("dynasty_waivers") or []
    catalog["bb_waivers_redraft"] = bb.get("redraft_waivers") or []
    catalog["bb_sources"] = bb.get("source_names") or []
    pl = pl or {}
    catalog["pl_pitch"] = [slim_row(r, ("age", "group", "price", "sel", "pts")) for r in pl.get("pitch") or []]
    catalog["pl_fwd"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("fwd") or []]
    catalog["pl_mid"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("mid") or []]
    catalog["pl_def"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("def") or []]
    catalog["pl_gkp"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("gkp") or []]
    catalog["pl_players"] = pl.get("files") or []
    catalog["pl_sources"] = pl.get("source_names") or []
    dest = ROOT / "data/discord-catalog.json"
    dest.write_text(json.dumps(catalog, indent=2, default=str))
    return dest


if __name__ == "__main__":
    main()
