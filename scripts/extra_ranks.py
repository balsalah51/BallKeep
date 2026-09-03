"""Additional ranking sources loaded from data/ranks/.

Published boards only. Short lists still count: unranked names are skipped
in the mean, not treated as 999.
"""
from __future__ import annotations

import json
from pathlib import Path

RANK_DIR = Path(__file__).resolve().parents[1] / "data" / "ranks"


def load_names(stem: str) -> list[str]:
    path = RANK_DIR / f"{stem}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        return [name for name, _rk in sorted(data.items(), key=lambda kv: int(kv[1]))]
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return [row["name"] for row in data if row.get("name")]
    return [n for n in data if isinstance(n, str) and n.strip()]


def load_rank_map(stem: str) -> dict[str, int]:
    path = RANK_DIR / f"{stem}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        return {str(k): int(v) for k, v in data.items()}
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return {row["name"]: i for i, row in enumerate(data, 1) if row.get("name")}
    return {n: i for i, n in enumerate(data, 1) if isinstance(n, str) and n.strip()}


# ESPN Karabell Superflex PPR, updated Aug 31, 2026
# https://www.espn.com/fantasy/football/story/_/id/47539664
ESPN_KARABELL_SF = load_names("karabell-sf")

# ESPN Karabell Flex (no QB) - extra PPR redraft source, Aug 31 2026
ESPN_KARABELL_FLEX = load_names("karabell-flex")

# Draft Sharks Dynasty Superflex public top 25, Sep 3 2026
# https://www.draftsharks.com/dynasty-rankings/superflex
DRAFT_SHARKS_SF = load_names("ds-sf")

# Mike Clay ESPN dynasty top 240, Aug 31 2026
# https://www.espn.com/fantasy/football/story/_/id/15698900
MIKE_CLAY_DYNASTY = load_names("clay-dynasty")

# RotoWire Superflex, Aug 14 2026. Names mapped from the published team/pos board
# plus named ranks in the buy-low table. No newer public list after Aug 27.
# https://www.rotowire.com/football/article/2026-dynasty-superflex-rankings-buy-low-values-adp-127901
ROTOWIRE_SF = [
    "Josh Allen", "Drake Maye", "Ja'Marr Chase", "Jahmyr Gibbs", "Bijan Robinson",
    "Puka Nacua", "Lamar Jackson", "Jaxon Smith-Njigba", "Amon-Ra St. Brown", "Patrick Mahomes",
    "Jayden Daniels", "Joe Burrow", "Justin Jefferson", "Malik Nabers", "Caleb Williams",
    "Drake London", "Justin Herbert", "Trevor Lawrence", "CeeDee Lamb", "Ashton Jeanty",
    "De'Von Achane", "Jalen Hurts", "Bo Nix", "Jeremiyah Love", "Jaxson Dart",
    "Brock Bowers", "Tetairoa McMillan", "Nico Collins", "Trey McBride", "Omarion Hampton",
    "Brock Purdy", "Dak Prescott", "George Pickens", "Colston Loveland", "Emeka Egbuka",
    "Jordan Love", "Luther Burden", "Fernando Mendoza", "Jonathan Taylor", "Zay Flowers",
    "James Cook", "DeVonta Smith", "Ladd McConkey", "Chris Olave", "Carnell Tate",
    "Jordyn Tyson", "Christian McCaffrey", "Jared Goff", "Cam Ward", "Kenneth Walker",
]


def as_ranks(names):
    return {n: i for i, n in enumerate(names, 1)}
