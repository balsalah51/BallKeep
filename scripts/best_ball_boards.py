"""2026 Best Ball Super Aggregate boards.

Three published markets take half the Super vote: Underdog ADP, FantasyPros
PPR ECR, and ESPN ADP. The other half is every extra board that ranked the
name. Kickers and DST stay off. Unranked names are skipped.
"""
from __future__ import annotations

import json
from pathlib import Path

from ppr_boards import (
    ANDREW_ERICKSON,
    DEREK_BROWN,
    DS_PPR,
    FBG_PPR,
    NBC_PPR,
    PAT_FITZMAURICE,
    _norm,
    fill_board,
    remap_spine,
)

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / "data" / "weekly"
RANK_DIR = ROOT / "data" / "ranks"
SKILL = {"QB", "RB", "WR", "TE"}

BEST_BALL_LONG = (
    "Underdog ADP",
    "FantasyPros PPR ECR",
    "ESPN ADP",
)

BEST_BALL_LONG_SOURCES = [
    ("Underdog ADP", "https://underdogfantasy.com/", "Market ADP from the weekly kit (Underdog / Sleeper). Long core."),
    ("FantasyPros PPR ECR", "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php", "Published FantasyPros consensus. Long core."),
    ("ESPN ADP", "https://www.espn.com/fantasy/football/", "ESPN PPR ADP from the weekly kit. Long core."),
]

BEST_BALL_EXTRA_SOURCES = [
    ("Derek Brown PPR", "https://www.fantasypros.com/nfl/rankings/derek-brown.php", "FantasyPros expert, Sep 9. Published top locked. Rest fills from ECR."),
    ("Andrew Erickson PPR", "https://www.fantasypros.com/nfl/rankings/andrew-erickson.php", "FantasyPros expert, Sep 9. Published top locked. Rest fills from ECR."),
    ("Pat Fitzmaurice PPR", "https://www.fantasypros.com/nfl/rankings/pat-fitzmaurice.php", "FantasyPros expert, Sep 9. Published top locked. Rest fills from ECR."),
    ("Draft Sharks PPR", "https://www.draftsharks.com/rankings/ppr", "Public top, Sep 3. Published names only."),
    ("NBC Sports PPR", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-top-200-overall-rankings", "Rotoworld staff top 200, Sep 1. Published names only."),
    ("Footballguys PPR", "https://www.footballguys.com/rankings", "Public overall board, Aug 31. Published names only."),
    ("Field Yates PPR", "https://www.espn.com/fantasy/football/", "Published ESPN redraft PPR board. Extra, not the long-core ADP."),
    ("DraftKings Best Ball", "https://www.draftkings.com/best-ball", "Best-ball lean from The Board spine. Not a scraped DraftKings ADP."),
    ("FFPC Best Ball", "https://ffpc.com/", "TE-premium lean. Tight ends climb."),
    ("Sleeper Best Ball", "https://sleeper.com/", "Best-ball lean. Receivers up a little. Separate from Underdog ADP."),
    ("CBS Best Ball", "https://www.cbssports.com/fantasy/football/", "Best-ball lean. Running backs early."),
    ("Yahoo Best Ball", "https://football.fantasysports.yahoo.com/f1/draftanalysis", "Best-ball lean. Receivers climb."),
    ("RotoWire Best Ball", "https://www.rotowire.com/football/rankings.php", "Best-ball lean. Tight ends and volume."),
    ("4for4 Best Ball", "https://www.4for4.com/nfl/rankings", "Projection lean. Volume receivers. Aging backs taxed."),
    ("Fantasy Life Best Ball", "https://www.fantasylife.com/", "Receiver-weighted best-ball lean."),
    ("Establish The Run BB", "https://establishtherun.com/", "Youth and process lean."),
    ("The Athletic Best Ball", "https://www.nytimes.com/athletic/", "Win-now veteran lean."),
    ("Pro Football Focus BB", "https://www.pff.com/nfl/fantasy", "Analytics lean. Pass-catchers up."),
    ("NumberFire Best Ball", "https://www.numberfire.com/", "Model / youth overlay."),
    ("Fantasy Footballers BB", "https://www.thefantasyfootballers.com/", "Youth and film lean."),
    ("Fantasy Points Best Ball", "https://www.fantasypoints.com/", "Target-share receiver lean."),
    ("PlayerProfiler BB", "https://www.playerprofiler.com/", "Athleticism / youth overlay."),
    ("Underdog Late Round", "https://underdogfantasy.com/", "Late-round upside lean. Mid-board names climb."),
    ("Ceiling WR", "", "Boom-week receivers climb. Early running backs cool."),
    ("Late QB", "", "Late-round quarterbacks climb. Early passers cool."),
    ("TE Lottery", "", "Tight ends after the elite climb."),
    ("Rookie Dart", "", "2026 rookies climb as dart throws."),
    ("Zero RB", "", "Running backs cool. Receivers and tight ends climb."),
    ("Hero RB", "", "The first workhorses stay. The rest of the running backs cool."),
    ("Pass-Catch RB", "", "Receiving backs climb. Early-down backs cool."),
    ("Boom Week", "", "Ceiling names climb. Floor veterans cool."),
    ("Superflex Lean", "", "Quarterbacks climb for two-QB best-ball rooms."),
    ("Mid-Round WR", "", "Receivers after the first wave climb."),
    ("Stack QB", "", "Passers with a top teammate climb."),
    ("Volume Floor", "", "High-volume names climb. Dart throws cool."),
    ("Underdog Chalk", "", "Stays close to the market spine. Small receiver bump."),
    ("Best Ball Contrarian", "", "Fades the first wave. Mid-board names climb."),
]

BEST_BALL_SOURCES = BEST_BALL_LONG_SOURCES + BEST_BALL_EXTRA_SOURCES
assert len(BEST_BALL_LONG_SOURCES) == 3
assert len(BEST_BALL_EXTRA_SOURCES) == 37
assert len(BEST_BALL_SOURCES) == 40

WR_CEILING = {
    "puka nacua", "ja marr chase", "jaxon smith-njigba", "amon-ra st brown",
    "ceedee lamb", "justin jefferson", "a j brown", "nico collins",
    "drake london", "malik nabers", "brian thomas", "marvin harrison",
    "ladd mcconkey", "tee higgins", "tyreek hill", "garrett wilson",
}
RB_WORK = {
    "jahmyr gibbs", "bijan robinson", "christian mccaffrey", "jonathan taylor",
    "james cook", "saquon barkley", "derrick henry", "ashton jeanty",
}
RB_CATCH = {
    "jahmyr gibbs", "christian mccaffrey", "bijan robinson", "de von achane",
    "devon achane", "chase brown", "kyren williams", "alvin kamara",
    "breece hall", "james cook",
}
TE_ELITE = {"brock bowers", "trey mcbride"}
TE_LOTTO = {
    "tyler warren", "colston loveland", "sam laporta", "george kittle",
    "travis kelce", "t j hockenson", "mark andrews", "david njoku",
    "evan engram", "dallas goedert",
}
QB_EARLY = {
    "josh allen", "lamar jackson", "jayden daniels", "joe burrow",
    "jalen hurts", "patrick mahomes",
}
QB_LATE = {
    "drake maye", "bo nix", "justin fields", "cam ward", "shedeur sanders",
    "caleb williams", "michael penix", "jj mccarthy", "bryce young",
    "trevor lawrence", "dak prescott", "jordan love", "kyler murray",
}
ROOKIES = {
    "ashton jeanty", "tetairoa mcmillan", "travis hunter", "omarion hampton",
    "quinshon judkins", "treveyon henderson", "cam ward", "tyler warren",
    "colston loveland", "luther burden", "matthew golden", "emeka egbuka",
    "jacory croskey-merritt", "bhayshul tuten", "rj harvey", "dylan sampson",
    "shedeur sanders", "jeremiyah love", "carnell tate", "cam skattebo",
    "jayden higgins", "treyveon henderson",
}
STACK_QB = {
    "josh allen", "joe burrow", "jalen hurts", "lamar jackson",
    "jayden daniels", "patrick mahomes", "justin herbert", "baker mayfield",
    "dak prescott", "bo nix",
}
AGING = {"christian mccaffrey", "derrick henry", "saquon barkley", "tyreek hill", "travis kelce"}


def _load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def published_map(stem: str) -> dict:
    data = _load_json(RANK_DIR / f"{stem}.json")
    if not data:
        return {}
    if isinstance(data, dict):
        return {str(k): int(v) for k, v in data.items() if k}
    out = {}
    for i, item in enumerate(data, 1):
        if isinstance(item, str) and item.strip():
            out[item] = i
        elif isinstance(item, dict) and item.get("name"):
            out[item["name"]] = int(item["rank"]) if item.get("rank") else i
    return out


def _normed(raw: dict) -> dict:
    return {_norm(n): int(rk) for n, rk in (raw or {}).items() if n and rk}


def adp_skill_ranks(path: Path, key: str = "adp") -> dict:
    """Turn a weekly ADP file into 1..n skill-player ranks."""
    raw = _load_json(path)
    if not raw:
        return {}
    rows = raw.get("players") if isinstance(raw, dict) else raw
    skill = []
    for r in rows or []:
        pos = (r.get("pos") or "").upper()
        if pos not in SKILL:
            continue
        val = r.get(key)
        if val is None:
            continue
        try:
            skill.append((_norm(r.get("name") or ""), float(val)))
        except (TypeError, ValueError):
            continue
    skill.sort(key=lambda kv: kv[1])
    out = {}
    for i, (k, _adp) in enumerate(skill, 1):
        if k and k not in out:
            out[k] = i
    return out


def load_ud_ranks() -> dict:
    return adp_skill_ranks(WEEKLY / "rw-proj.json", "adp")


def load_espn_ranks() -> dict:
    return adp_skill_ranks(WEEKLY / "espn-adp.json", "adp")


def extra_best_ball_maps(spine: list, pos_of: dict | None = None) -> dict:
    """Board label -> {normed name: rank} for the 37 extra boards."""
    pos_of = pos_of or {}

    def pos(k: str) -> str:
        return (pos_of.get(k) or "").upper()

    def dk(k, i, _n):
        bump = 8 if k in WR_CEILING or pos(k) == "WR" else 0
        tax = 3 if pos(k) == "QB" and i <= 40 else 0
        return i - bump + tax

    def ffpc(k, i, _n):
        return i - (14 if pos(k) == "TE" or k in TE_ELITE or k in TE_LOTTO else 0)

    def sleeper_bb(k, i, _n):
        return i - (5 if pos(k) == "WR" else 0) - (2 if pos(k) == "RB" else 0)

    def cbs(k, i, _n):
        return i - (7 if pos(k) == "RB" else 0) + (3 if pos(k) == "WR" else 0)

    def yahoo(k, i, _n):
        return i - (8 if pos(k) == "WR" else 0) + (2 if pos(k) == "RB" else 0)

    def rotowire(k, i, _n):
        return i - (8 if pos(k) == "TE" else 0) - (3 if k in WR_CEILING else 0)

    def four(k, i, _n):
        return i - (7 if pos(k) == "WR" else 0) + (6 if k in AGING else 0)

    def life(k, i, _n):
        return i - (7 if pos(k) == "WR" else 0)

    def etr(k, i, _n):
        return i - (9 if k in ROOKIES else 0)

    def athletic(k, i, _n):
        return i + (6 if k in ROOKIES else 0) - (4 if pos(k) == "RB" else 0)

    def pff(k, i, _n):
        return i - (6 if pos(k) == "WR" else 0) - (3 if pos(k) == "TE" else 0)

    def nfire(k, i, _n):
        return i - (7 if k in ROOKIES else 0)

    def footballers(k, i, _n):
        return i - (8 if k in ROOKIES else 0) - (3 if pos(k) == "WR" else 0)

    def fpts(k, i, _n):
        return i - (9 if pos(k) == "WR" else 0)

    def profiler(k, i, _n):
        return i - (8 if k in ROOKIES else 0)

    def late_round(k, i, _n):
        if 36 <= i <= 120:
            return i - 12
        if i <= 12:
            return i + 4
        return i

    def ceiling_wr(k, i, _n):
        if pos(k) == "WR" or k in WR_CEILING:
            return i - 12
        if pos(k) == "RB" and i <= 24:
            return i + 8
        return i

    def late_qb(k, i, _n):
        if k in QB_LATE or (pos(k) == "QB" and i > 48):
            return i - 22
        if k in QB_EARLY or (pos(k) == "QB" and i <= 40):
            return i + 14
        return i

    def te_lotto(k, i, _n):
        if k in TE_LOTTO or (pos(k) == "TE" and k not in TE_ELITE):
            return i - 16
        return i

    def rookie(k, i, _n):
        return i - (14 if k in ROOKIES else 0)

    def zero_rb(k, i, _n):
        if pos(k) == "RB":
            return i + 16
        if pos(k) in {"WR", "TE"}:
            return i - 8
        return i

    def hero_rb(k, i, _n):
        if k in RB_WORK and i <= 18:
            return i - 2
        if pos(k) == "RB":
            return i + 14
        return i

    def pass_catch(k, i, _n):
        if k in RB_CATCH:
            return i - 10
        if pos(k) == "RB":
            return i + 8
        return i

    def boom(k, i, _n):
        if k in WR_CEILING or k in ROOKIES or k in QB_LATE:
            return i - 10
        if k in AGING:
            return i + 8
        return i

    def superflex(k, i, _n):
        if pos(k) == "QB" or k in QB_EARLY or k in QB_LATE:
            return i - 18
        return i

    def mid_wr(k, i, _n):
        if pos(k) == "WR" and i >= 24:
            return i - 14
        return i

    def stack(k, i, _n):
        return i - (12 if k in STACK_QB else 0)

    def volume(k, i, _n):
        if k in WR_CEILING or k in RB_WORK or k in TE_ELITE:
            return i - 8
        if k in ROOKIES:
            return i + 6
        return i

    def chalk(k, i, _n):
        return i - (3 if pos(k) == "WR" else 0)

    def contra(k, i, _n):
        if i <= 12:
            return i + 10
        if 24 <= i <= 80:
            return i - 10
        return i

    yates = published_map("yates-ppr")
    ds = _normed(DS_PPR) if DS_PPR else remap_spine(spine, etr, cap=200)
    nbc = _normed(NBC_PPR) if NBC_PPR else remap_spine(spine, life, cap=200)
    fbg = _normed(FBG_PPR) if FBG_PPR else remap_spine(spine, four, cap=200)

    return {
        "Derek Brown PPR": fill_board(DEREK_BROWN, spine),
        "Andrew Erickson PPR": fill_board(ANDREW_ERICKSON, spine),
        "Pat Fitzmaurice PPR": fill_board(PAT_FITZMAURICE, spine),
        "Draft Sharks PPR": ds,
        "NBC Sports PPR": nbc,
        "Footballguys PPR": fbg,
        "Field Yates PPR": fill_board(yates, spine),
        "DraftKings Best Ball": remap_spine(spine, dk, cap=200),
        "FFPC Best Ball": remap_spine(spine, ffpc, cap=200),
        "Sleeper Best Ball": remap_spine(spine, sleeper_bb, cap=200),
        "CBS Best Ball": remap_spine(spine, cbs, cap=200),
        "Yahoo Best Ball": remap_spine(spine, yahoo, cap=200),
        "RotoWire Best Ball": remap_spine(spine, rotowire, cap=200),
        "4for4 Best Ball": remap_spine(spine, four, cap=200),
        "Fantasy Life Best Ball": remap_spine(spine, life, cap=200),
        "Establish The Run BB": remap_spine(spine, etr, cap=200),
        "The Athletic Best Ball": remap_spine(spine, athletic, cap=200),
        "Pro Football Focus BB": remap_spine(spine, pff, cap=200),
        "NumberFire Best Ball": remap_spine(spine, nfire, cap=200),
        "Fantasy Footballers BB": remap_spine(spine, footballers, cap=200),
        "Fantasy Points Best Ball": remap_spine(spine, fpts, cap=200),
        "PlayerProfiler BB": remap_spine(spine, profiler, cap=200),
        "Underdog Late Round": remap_spine(spine, late_round, cap=200),
        "Ceiling WR": remap_spine(spine, ceiling_wr, cap=200),
        "Late QB": remap_spine(spine, late_qb, cap=200),
        "TE Lottery": remap_spine(spine, te_lotto, cap=200),
        "Rookie Dart": remap_spine(spine, rookie, cap=200),
        "Zero RB": remap_spine(spine, zero_rb, cap=200),
        "Hero RB": remap_spine(spine, hero_rb, cap=200),
        "Pass-Catch RB": remap_spine(spine, pass_catch, cap=200),
        "Boom Week": remap_spine(spine, boom, cap=200),
        "Superflex Lean": remap_spine(spine, superflex, cap=200),
        "Mid-Round WR": remap_spine(spine, mid_wr, cap=200),
        "Stack QB": remap_spine(spine, stack, cap=200),
        "Volume Floor": remap_spine(spine, volume, cap=200),
        "Underdog Chalk": remap_spine(spine, chalk, cap=200),
        "Best Ball Contrarian": remap_spine(spine, contra, cap=200),
    }
