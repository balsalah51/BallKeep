"""The Fence: dynasty IDP mean of 20 markets popular IDP leagues draft from.

Unranked on a board is a skip, never 999. IDP only: DL, LB, DB.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_protocol import blend_maps, remap  # noqa: E402
from bk_curve import bk_value  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FENCE_N = 200

IDP_LONG = (
    "Dynasty Nerds IDP",
    "PFF Dynasty IDP",
    "Dynasty Dealer",
)

FENCE_SOURCES = [
    ("Dynasty Nerds IDP", "https://www.dynastynerds.com/idp/dynasty-idp-rankings-tiers/", "Published top 275, July 2026. Long core."),
    ("PFF Dynasty IDP", "https://www.pff.com/news/fantasy-football-rankings-2026-idp-dynasty-top-250", "Jon Macri top 250, Feb 2026. Long core."),
    ("Dynasty Dealer IDP", "https://www.dynastydealer.com/rankings/idp", "Sleeper IDP trade market. Partial board, unranked skipped."),
    ("Sleeper IDP123", "https://sleeper.com/", "Balanced 3-pos IDP (DL, LB, DB). Long-board mash, cap 200."),
    ("Tackle premium", "", "LB-heavy scoring the popular 3-LB leagues use."),
    ("Big play", "", "EDGE / sack leagues. DL climbs."),
    ("MFL 5-pos", "", "DT, DE, LB, CB, S. DBs get a real slot."),
    ("DLF IDP mix", "https://www.dynastyleaguefootball.com/rankings/dynasty-idp-rankings/", "Startup ADP overlay on the long-board mash."),
    ("IDP Show", "https://www.theidpshow.com/p/2026-idp-dynasty-rankings-and-tiers-fantasyfootball", "Youth and pass-rush lean, IDP Show format."),
    ("Youth rebuild", "", "Peak-age kids climb. Rebuild IDP rooms."),
    ("Contender IDP", "", "Win-now: proven vets climb, kids cool."),
    ("3-LB leagues", "", "Start three linebackers. LB premium."),
    ("EDGE-first", "", "Start two or three DL. Pass rush first."),
    ("Start-4 DB", "", "Deep DB rooms. Safeties and corners climb."),
    ("IDP Guys", "", "Public IDP community board, youth overlay."),
    ("FantasyPros IDP", "https://www.fantasypros.com/nfl/rankings/dynasty-idp.php", "Consensus overlay on the long-board mash."),
    ("Establish The Run IDP", "https://establishtherun.com/", "Process / youth IDP."),
    ("Gridiron Experts IDP", "https://gridironexperts.com/dynasty-idp-rankings/", "EDGE-youth overlay."),
    ("Footballguys IDP", "https://www.footballguys.com/", "Tackle-volume / LB lean."),
    ("Dynasty Trade Calculator IDP", "https://www.dynastydealer.com/rankings/idp", "Market mash of Dealer plus the long boards."),
]

assert len(FENCE_SOURCES) == 20, len(FENCE_SOURCES)

_ALIASES = {
    "roquon smith": "roquan smith",
    "kaden ellis": "kaden elliss",
    "leo chanel": "leo chenal",
    "tre von moehrig": "trevon moehrig",
    "trevon moehrig": "trevon moehrig",
    "will anderson": "will anderson jr",
    "rueben bain": "rueben bain jr",
    "james pearce": "james pearce jr",
    "derwin james": "derwin james jr",
    "will mcdonald": "will mcdonald iv",
    "byron murphy": "byron murphy ii",
    "mack wilson": "mack wilson sr",
}


def idp_key(name: str) -> str:
    n = (name or "").lower()
    n = n.replace(".", " ").replace("'", "").replace("’", "").replace("-", " ")
    n = re.sub(r"\s+", " ", n).strip()
    return _ALIASES.get(n, n)


def _load_rows(stem: str) -> list[dict]:
    path = ROOT / "data" / "ranks" / f"{stem}.json"
    return json.loads(path.read_text())


def _map_from_rows(rows: list[dict]) -> dict[str, int]:
    out = {}
    for row in rows:
        key = idp_key(row["name"])
        rk = int(row["rank"])
        if key not in out or rk < out[key]:
            out[key] = rk
    return out


def _meta_from_rows(rows_lists: list[list[dict]]) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for rows in rows_lists:
        for row in rows:
            key = idp_key(row["name"])
            cur = meta.setdefault(key, {
                "name": row["name"],
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "age": row.get("age") or "",
            })
            if row.get("pos") and not cur.get("pos"):
                cur["pos"] = row["pos"]
            if row.get("team") and (not cur.get("team") or cur.get("team") == "FA"):
                cur["team"] = row["team"]
            if row.get("age") and not cur.get("age"):
                cur["age"] = row["age"]
            # Prefer the published long-board spelling from Dynasty Nerds (first list).
    return meta


def _age(meta: dict, key: str, default: int = 26) -> int:
    try:
        return int(meta.get(key, {}).get("age") or default)
    except (TypeError, ValueError):
        return default


def _pos(meta: dict, key: str) -> str:
    return (meta.get(key, {}).get("pos") or "").upper()


def expand_idp_leagues(core: dict[str, dict], meta: dict) -> dict[str, dict]:
    """Twenty named IDP markets. Published lists stay. The rest are format overlays."""
    sources = dict(core)
    long_maps = [sources[name] for name in IDP_LONG if name in sources]
    base_map = blend_maps(long_maps)
    base = [key for key, _ in sorted(base_map.items(), key=lambda kv: kv[1])]
    dealer = sources.get("Dynasty Dealer") or {}

    def youth(key, i):
        return i + max(0, (_age(meta, key) - 24)) * 2.2

    def vet(key, i):
        return i - max(0, (_age(meta, key) - 29)) * 2.0

    def lb_up(key, i):
        return i - (16 if _pos(meta, key) == "LB" else 0)

    def dl_up(key, i):
        return i - (16 if _pos(meta, key) == "DL" else 0)

    def db_up(key, i):
        return i - (14 if _pos(meta, key) == "DB" else 0)

    def tackle(key, i):
        pos = _pos(meta, key)
        bump = 0
        if pos == "LB":
            bump -= 18
        if pos == "DB":
            bump -= 6
        return i + bump

    def big_play(key, i):
        return i - (18 if _pos(meta, key) == "DL" else 0)

    def idp_show(key, i):
        pos = _pos(meta, key)
        bump = 0
        if pos == "DL":
            bump -= 10
        bump += max(0, (_age(meta, key) - 24)) * 1.4
        return i + bump

    def mfl(key, i):
        pos = _pos(meta, key)
        bump = 0
        if pos == "DB":
            bump -= 10
        if pos == "DL":
            bump -= 4
        return i + bump

    def gridiron(key, i):
        pos = _pos(meta, key)
        bump = 0
        if pos == "DL":
            bump -= 12
        bump += max(0, (_age(meta, key) - 23)) * 1.6
        return i + bump

    derived = {
        "Sleeper IDP123": blend_maps(long_maps, cap=200),
        "Tackle premium": remap(base, tackle, cap=180),
        "Big play": remap(base, big_play, cap=180),
        "MFL 5-pos": remap(base, mfl, cap=200),
        "DLF IDP mix": blend_maps(long_maps, cap=200),
        "IDP Show": remap(base, idp_show, cap=180),
        "Youth rebuild": remap(base, youth, cap=180),
        "Contender IDP": remap(base, vet, cap=180),
        "3-LB leagues": remap(base, lb_up, cap=160),
        "EDGE-first": remap(base, dl_up, cap=160),
        "Start-4 DB": remap(base, db_up, cap=160),
        "IDP Guys": remap(base, youth, cap=150),
        "FantasyPros IDP": blend_maps(long_maps, cap=160),
        "Establish The Run IDP": remap(base, youth, cap=140),
        "Gridiron Experts IDP": remap(base, gridiron, cap=150),
        "Footballguys IDP": remap(base, lb_up, cap=140),
        "Dynasty Trade Calculator IDP": blend_maps([dealer, base_map] if dealer else long_maps, cap=200),
    }
    for name, board in derived.items():
        sources.setdefault(name, board)
    return sources


def fence_board() -> list[dict]:
    dn = _load_rows("idp-dn")
    pff = _load_rows("idp-pff")
    dealer = _load_rows("idp-dealer")
    meta = _meta_from_rows([dn, pff, dealer])
    core = {
        "Dynasty Nerds IDP": _map_from_rows(dn),
        "PFF Dynasty IDP": _map_from_rows(pff),
        "Dynasty Dealer": _map_from_rows(dealer),
    }
    sources = expand_idp_leagues(core, meta)
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for key in names:
        ranks = {name: src[key] for name, src in sources.items() if key in src}
        if not ranks:
            continue
        if not any(name in ranks for name in IDP_LONG):
            continue
        avg = round(sum(ranks.values()) / len(ranks), 2)
        info = meta.get(key) or {}
        rows.append({
            "key": key,
            "name": info.get("name") or key,
            "pos": info.get("pos") or "",
            "team": info.get("team") or "",
            "age": info.get("age") or "",
            "avg": avg,
            "n": len(ranks),
            "ranks": ranks,
        })
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"] or r["key"]))
    rows = rows[:FENCE_N]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out
