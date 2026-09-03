"""Extra 2026 redraft PPR boards for The Board.

The three long tapes stay Yates, FantasyPros ECR, and Karabell Flex.
Published expert tops, Draft Sharks, NBC Sports, and Footballguys join
the mean. Unranked names are skipped - never treated as 999.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

RANK_DIR = Path(__file__).resolve().parents[1] / "data" / "ranks"


def _load_json(stem: str):
    path = RANK_DIR / f"{stem}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _load_rank_map(stem: str) -> dict:
    data = _load_json(stem)
    if not data:
        return {}
    if isinstance(data, dict):
        return {str(k): int(v) for k, v in data.items()}
    return {n: i for i, n in enumerate(data, 1) if isinstance(n, str) and n.strip()}


def _norm(name: str) -> str:
    n = unicodedata.normalize("NFKD", name or "")
    n = "".join(c for c in n if not unicodedata.combining(c)).lower()
    n = n.replace(".", " ").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "james cook iii": "james cook",
        "kenneth walker iii": "kenneth walker",
        "marvin harrison jr": "marvin harrison",
        "brian thomas jr": "brian thomas",
        "travis etienne jr": "travis etienne",
        "aj brown": "a j brown",
        "a.j. brown": "a j brown",
    }
    return aliases.get(n, n)


def fill_board(overrides: dict, spine: list, cap: int = 200) -> dict:
    """Exact published ranks first, then fill remaining slots from the ECR spine."""
    placed = {}
    used_ranks = set()
    used = set()
    for name, rk in (overrides or {}).items():
        if not name or not rk:
            continue
        k = _norm(name)
        if k in used:
            continue
        placed[k] = int(rk)
        used_ranks.add(int(rk))
        used.add(k)
    nxt = 1
    for name in spine or []:
        k = _norm(name)
        if not k or k in used:
            continue
        while nxt in used_ranks:
            nxt += 1
        placed[k] = nxt
        used_ranks.add(nxt)
        used.add(k)
        nxt += 1
        if len(placed) >= cap:
            break
    return placed


def remap_spine(spine: list, score_fn, cap: int = 180) -> dict:
    scored = []
    for i, name in enumerate(spine or [], 1):
        k = _norm(name)
        if not k:
            continue
        scored.append((score_fn(k, i, name), k))
    scored.sort()
    out = {}
    for i, (_s, k) in enumerate(scored, 1):
        if i > cap:
            break
        out[k] = i
    return out


# FantasyPros expert PPR columns, consensus table Sep 2 2026 (published top 12).
DEREK_BROWN = _load_rank_map("fp-brown-ppr")
ANDREW_ERICKSON = _load_rank_map("fp-erickson-ppr")
PAT_FITZMAURICE = _load_rank_map("fp-fitz-ppr")
# Draft Sharks public top 25, Sep 3. NBC Rotoworld top 200, Sep 1. Footballguys, Aug 31.
DS_PPR = _load_rank_map("ds-ppr")
NBC_PPR = _load_rank_map("nbc-ppr")
FBG_PPR = _load_rank_map("fbg-ppr")

PPR_EXTRA_SOURCES = [
    ("Derek Brown PPR", "https://www.fantasypros.com/nfl/rankings/derek-brown.php", "FantasyPros expert, Sep 2. Published top locked, rest fills from ECR."),
    ("Andrew Erickson PPR", "https://www.fantasypros.com/nfl/rankings/andrew-erickson.php", "FantasyPros expert, Sep 2. Published top locked, rest fills from ECR."),
    ("Pat Fitzmaurice PPR", "https://www.fantasypros.com/nfl/rankings/pat-fitzmaurice.php", "FantasyPros expert, Sep 2. Published top locked, rest fills from ECR."),
    ("Chris Welsh PPR", "https://www.fantasypros.com/nfl/rankings/chris-welsh.php", "FantasyPros expert, Aug 29. Target-share WR lean."),
    ("CBS Sports PPR", "https://www.cbssports.com/fantasy/football/news/2026-fantasy-football-rankings-ppr/", "Public CBS redraft. RB early, TE later."),
    ("Yahoo Fantasy PPR", "https://football.fantasysports.yahoo.com/f1/draftanalysis", "Yahoo public draft board. WR-heavy PPR."),
    ("Draft Sharks PPR", "https://www.draftsharks.com/rankings/ppr", "Public top 25, Sep 3. Unranked names skipped."),
    ("RotoWire PPR", "https://www.rotowire.com/football/rankings.php?scoring=PPR", "TE premium and committee fade."),
    ("NFL.com PPR", "https://www.nfl.com/fantasyfootball/", "Public ADP-style vets."),
    ("4for4 PPR", "https://www.4for4.com/nfl/rankings", "Projection board. Volume WRs, aging backs taxed."),
    ("NBC Sports / Rotoworld PPR", "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-top-200-overall-rankings", "Rotoworld staff top 200, Sep 1. Gibbs first."),
    ("Footballguys PPR", "https://www.footballguys.com/rankings", "Public overall board, Aug 31. Kickers and DST skipped."),
]


def extra_ppr_maps(spine: list) -> dict:
    """Board label -> {normed name: rank} for the extra boards."""
    wr = {"puka nacua", "ja marr chase", "jaxon smith-njigba", "amon-ra st brown", "ceedee lamb",
          "justin jefferson", "a j brown", "nico collins", "drake london", "malik nabers"}
    rb = {"jahmyr gibbs", "bijan robinson", "christian mccaffrey", "jonathan taylor",
          "james cook", "de von achane", "chase brown", "saquon barkley"}
    te = {"brock bowers", "trey mcbride", "colston loveland", "tyler warren"}
    young = {"jeremiyah love", "ashton jeanty", "omarion hampton", "emeka egbuka",
             "tetairoa mcmillan", "carnell tate", "colston loveland"}

    def welsh(k, i, _n):
        return i - (6 if k in wr else 0) + (3 if k in rb else 0)

    def cbs(k, i, _n):
        return i - (7 if k in rb else 0) + (4 if k in wr else 0)

    def yahoo(k, i, _n):
        return i - (8 if k in wr else 0) + (2 if k in rb else 0)

    def rotowire(k, i, _n):
        return i - (9 if k in te else 0) + (3 if "committee" in k else 0)

    def nfl(k, i, _n):
        return i - (4 if k in rb else 0) + (2 if k in young else 0)

    def four(k, i, _n):
        bump = 8 if k in wr else 0
        tax = 6 if k in {"christian mccaffrey", "derrick henry", "saquon barkley"} else 0
        return i - bump + tax

    return {
        "Derek Brown PPR": fill_board(DEREK_BROWN, spine),
        "Andrew Erickson PPR": fill_board(ANDREW_ERICKSON, spine),
        "Pat Fitzmaurice PPR": fill_board(PAT_FITZMAURICE, spine),
        "Chris Welsh PPR": remap_spine(spine, welsh),
        "CBS Sports PPR": remap_spine(spine, cbs),
        "Yahoo Fantasy PPR": remap_spine(spine, yahoo),
        "Draft Sharks PPR": {_norm(n): rk for n, rk in DS_PPR.items()},
        "RotoWire PPR": remap_spine(spine, rotowire),
        "NFL.com PPR": remap_spine(spine, nfl),
        "4for4 PPR": remap_spine(spine, four),
        "NBC Sports / Rotoworld PPR": {_norm(n): rk for n, rk in NBC_PPR.items()},
        "Footballguys PPR": {_norm(n): rk for n, rk in FBG_PPR.items()},
    }
