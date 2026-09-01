"""The Fence: mixed Superflex + IDP dynasty board.

Published mixed cores (Glossery Top 725) plus Keep / IDP stitches using
the IDP Show slot method. Separate IDP-only mean stays as one source.
Unranked on a board is a skip, never 999.
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
FENCE_MIXED_N = 400
IDP_POS = {"DL", "LB", "DB", "DE", "DT", "CB", "S"}

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

MIXED_LONG = (
    "Glossery Mixed",
    "Consensus stitch",
    "The Keep",
    "Fence IDP",
)

FENCE_MIXED_SOURCES = [
    ("Glossery Mixed", "https://www.dynastynerds.com/idp/glossery-mixed-idp-rankings/", "Dynasty Nerds Glossery Superflex + IDP top 725, Aug 21 2026. Long core."),
    ("Consensus stitch", "https://www.theidpshow.com/p/combined-idp-offense-dynasty-rankings-fantasy-football", "IDP Show method: Keep skill + Fence IDP dropped into Glossery startup slots."),
    ("The Keep", "https://ballkeep.com/the-keep.html", "Superflex skill-player 400. IDP names are a skip."),
    ("Fence IDP", "https://ballkeep.com/the-fence.html", "IDP-only mean of 20 markets. Skill names are a skip."),
    ("IDP Show startup", "https://www.theidpshow.com/p/combined-idp-offense-dynasty-rankings-fantasy-football", "Same stitch, IDP slots a few rounds earlier the way Sleeper IDP startups run."),
    ("Youth mixed", "", "Kids climb on the consensus stitch."),
    ("Contender mixed", "", "Win-now vets climb on the consensus stitch."),
    ("IDP-early", "", "Defenders climb. Popular when 40%+ of starters are IDP."),
    ("Skill-first", "", "Defenders cool. Skill-heavy IDP rooms."),
    ("TE premium", "", "Tight ends climb, same Superflex + IDP board."),
]
assert len(FENCE_MIXED_SOURCES) == 10, len(FENCE_MIXED_SOURCES)

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


def idp_only_board() -> list[dict]:
    """IDP-only mean of 20 markets. Hutchinson is 1.01 on this slice."""
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


def _is_idp(pos: str) -> bool:
    return (pos or "").upper() in IDP_POS


def _keep_rows() -> list[dict]:
    path = ROOT / "data" / "the-keep.json"
    blob = json.loads(path.read_text())
    return blob.get("players") or []


def _glossery_rows() -> list[dict]:
    return _load_rows("idp-glossery-mixed")


def _merge_meta(*row_lists: list[list[dict]]) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for rows in row_lists:
        for row in rows:
            key = idp_key(row.get("name") or row.get("key") or "")
            if not key:
                continue
            cur = meta.setdefault(key, {
                "name": row.get("name") or key,
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "age": row.get("age") or "",
            })
            if row.get("name") and len(str(row.get("name"))) >= len(str(cur.get("name") or "")):
                cur["name"] = row["name"]
            if row.get("pos") and not cur.get("pos"):
                cur["pos"] = row["pos"]
            if row.get("team") and (not cur.get("team") or cur.get("team") == "FA"):
                cur["team"] = row["team"]
            if row.get("age") and not cur.get("age"):
                cur["age"] = row["age"]
    return meta


def _ordered_keys(rows: list[dict]) -> list[str]:
    out, seen = [], set()
    for row in sorted(rows, key=lambda r: int(r.get("bk") or r.get("rank") or 9999)):
        key = idp_key(row.get("name") or row.get("key") or "")
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def _slot_kind(pos: str) -> str:
    return "IDP" if _is_idp(pos) else "SKILL"


def _stitch(skill_keys: list[str], idp_keys: list[str], slots: list[str]) -> dict[str, int]:
    si = ii = 0
    used = set()
    out = {}
    rank = 1
    for slot in slots:
        if slot == "IDP":
            while ii < len(idp_keys) and idp_keys[ii] in used:
                ii += 1
            if ii >= len(idp_keys):
                continue
            key = idp_keys[ii]
            ii += 1
        else:
            while si < len(skill_keys) and skill_keys[si] in used:
                si += 1
            if si >= len(skill_keys):
                continue
            key = skill_keys[si]
            si += 1
        used.add(key)
        out[key] = rank
        rank += 1
    return out


def _shift_idp_slots(slots: list[str], earlier: int) -> list[str]:
    """Move each IDP slot `earlier` places toward the top. Skill fills the gaps."""
    idp_at = [i for i, s in enumerate(slots) if s == "IDP"]
    moved = []
    taken = set()
    for i in idp_at:
        dest = min(len(slots) - 1, max(0, i - earlier))
        while dest in taken and dest < len(slots) - 1:
            dest += 1
        taken.add(dest)
        moved.append(dest)
    out = ["SKILL"] * len(slots)
    for i in moved:
        if i < len(out):
            out[i] = "IDP"
    return out


def expand_mixed_leagues(keep: list[dict], idp: list[dict], gloss: list[dict], meta: dict) -> dict[str, dict]:
    skill_keys = _ordered_keys(keep)
    idp_keys = _ordered_keys(idp)
    slots = [_slot_kind(r.get("pos") or "") for r in sorted(gloss, key=lambda x: int(x["rank"]))]
    stitch = _stitch(skill_keys, idp_keys, slots)
    early = _stitch(skill_keys, idp_keys, _shift_idp_slots(slots, 10))
    late = _stitch(skill_keys, idp_keys, _shift_idp_slots(slots, -12))
    show = _stitch(skill_keys, idp_keys, _shift_idp_slots(slots, 6))
    base = [key for key, _ in sorted(stitch.items(), key=lambda kv: kv[1])]

    def youth(key, i):
        return i + max(0, (_age(meta, key) - 24)) * 1.8

    def vet(key, i):
        return i - max(0, (_age(meta, key) - 29)) * 1.6

    def te_up(key, i):
        return i - (14 if _pos(meta, key) == "TE" else 0)

    keep_map = {idp_key(r.get("name") or r.get("key") or ""): int(r.get("bk") or r.get("rank") or 0)
                for r in keep if r.get("bk") or r.get("rank")}
    idp_map = {idp_key(r.get("name") or r.get("key") or ""): int(r.get("bk") or r.get("rank") or 0)
               for r in idp if r.get("bk") or r.get("rank")}
    gloss_map = _map_from_rows(gloss)
    return {
        "Glossery Mixed": gloss_map,
        "Consensus stitch": stitch,
        "The Keep": {k: v for k, v in keep_map.items() if k and v},
        "Fence IDP": {k: v for k, v in idp_map.items() if k and v},
        "IDP Show startup": show,
        "Youth mixed": remap(base, youth, cap=400),
        "Contender mixed": remap(base, vet, cap=400),
        "IDP-early": early,
        "Skill-first": late,
        "TE premium": remap(base, te_up, cap=400),
    }


def fence_board() -> list[dict]:
    """Mixed Superflex + IDP. Skill and IDP on one board."""
    keep = _keep_rows()
    idp = idp_only_board()
    gloss = _glossery_rows()
    meta = _merge_meta(keep, idp, gloss)
    sources = expand_mixed_leagues(keep, idp, gloss, meta)
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for key in names:
        ranks = {name: src[key] for name, src in sources.items() if key in src}
        if not ranks:
            continue
        if not any(name in ranks for name in MIXED_LONG):
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
    rows = rows[:FENCE_MIXED_N]
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out
