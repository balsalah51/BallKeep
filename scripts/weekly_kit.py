"""Week N skill boards, ADP, waivers, injuries, SOS, and usage.

Published lists only. Unranked on a board is a skip, never 999.
Skill boards use Super Aggregate: 50% FantasyPros ECR, 50% every other
desk that ranked the name.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from bk_curve import bk_value
from scrape_weekly import current_week
from special_teams import DST_TEAMS, dst_board
from aggregate_protocol import super_avg

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / "data" / "weekly"

TEAM_FROM_NAME = {name: abbr for name, abbr in DST_TEAMS}
TEAM_TO_NAME = {abbr: name for name, abbr in DST_TEAMS}

ALIASES = {
    "aj brown": "a j brown",
    "a.j. brown": "a j brown",
    "ja marr chase": "jamarr chase",
    "jamarr chase": "jamarr chase",
    "amon ra st brown": "amon-ra st brown",
    "amon-ra st. brown": "amon-ra st brown",
    "brian thomas jr": "brian thomas",
    "marvin harrison jr": "marvin harrison",
    "kenneth walker iii": "kenneth walker",
    "james cook iii": "james cook",
    "travis etienne jr": "travis etienne",
    "michael pittman jr": "michael pittman",
    "chig okonkwo": "chigoziem okonkwo",
}


def _norm(name: str) -> str:
    n = unicodedata.normalize("NFKD", name or "")
    n = "".join(c for c in n if not unicodedata.combining(c)).lower()
    n = n.replace(".", " ").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return ALIASES.get(n, n)


def _load(stem: str):
    path = WEEKLY / f"{stem}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def meta() -> dict:
    data = _load("meta") or {}
    data.setdefault("week", current_week())
    data.setdefault("season", 2026)
    return data


def week_num() -> int:
    return int(meta().get("week") or 1)


def _rank_map(stem: str, pos: str | None = None, rerank: bool = False) -> dict:
    data = _load(stem)
    out = {}
    for row in data.get("players") or []:
        if pos and (row.get("pos") or "").upper() != pos:
            continue
        name = row.get("name") or ""
        rk = int(row.get("rank") or 0)
        if name and rk:
            out[_norm(name)] = rk
    if rerank and out:
        items = sorted(out.items(), key=lambda kv: (kv[1], kv[0]))
        out = {k: i for i, (k, _) in enumerate(items, 1)}
    return out


def _info_bank() -> dict:
    """name-key -> pos, team, opp, owned, fpts, adp, injury."""
    bank = {}

    def touch(name, **kw):
        if not name:
            return
        k = _norm(name)
        cur = bank.setdefault(k, {"name": name, "key": k})
        for key, val in kw.items():
            if val in (None, "", []):
                continue
            if key not in cur or cur[key] in (None, ""):
                cur[key] = val
        if name and len(name) > len(cur.get("name") or ""):
            cur["name"] = name

    for pos in ("qb", "rb", "wr", "te", "flex"):
        for row in (_load(f"fp-ecr-{pos}").get("players") or []):
            touch(
                row.get("name"),
                pos=row.get("pos"),
                team=row.get("team"),
                opp=row.get("opp") or row.get("opp_id"),
                owned=row.get("owned"),
            )
    for row in (_load("rw-proj").get("players") or []):
        touch(row.get("name"), pos=row.get("pos"), team=row.get("team"), opp=row.get("opp"), fpts=row.get("fpts"), adp=row.get("adp"))
    for pos in ("qb", "rb", "wr", "te"):
        for row in (_load(f"fp-proj-{pos}").get("players") or []):
            touch(row.get("name"), team=row.get("team"), fpts_fp=row.get("fpts"), pos=pos.upper())
        for row in (_load(f"four-{pos}").get("players") or []):
            touch(row.get("name"), team=row.get("team"), opp=row.get("opp"), sos=row.get("sos"), pos=pos.upper())
    for row in (_load("espn-adp").get("players") or []):
        touch(row.get("name"), pos=row.get("pos"), team=row.get("team"), espn_adp=row.get("adp"), espn_ppr=row.get("espn_ppr"), pct_owned=row.get("pct_owned"), injury=row.get("injury"))
    for row in (_load("injuries").get("players") or []):
        touch(row.get("name"), pos=row.get("pos"), team=TEAM_FROM_NAME.get(row.get("team_name") or ""), injury=row.get("status"), note=row.get("note"))
    return bank


WEEKLY_LONG = ("FantasyPros ECR",)


def weekly_maps(pos: str) -> dict:
    pos = pos.upper()
    maps = {
        "FantasyPros ECR": _rank_map(f"fp-ecr-{pos.lower()}"),
        "RotoWire projections": _rank_map("rw-proj", pos=pos, rerank=True),
        "FantasyPros projections": _rank_map(f"fp-proj-{pos.lower()}"),
        "4for4": _rank_map(f"four-{pos.lower()}"),
    }
    return {k: v for k, v in maps.items() if v}


def weekly_sources(pos: str) -> list:
    week = week_num()
    pos = pos.lower()
    return [
        ("FantasyPros ECR", f"https://www.fantasypros.com/nfl/rankings/{pos}.php", f"Week {week} expert consensus. Unranked is a skip."),
        ("RotoWire projections", "https://www.rotowire.com/football/", f"Week {week} PPR points via Sleeper. Ranked by projected points."),
        ("FantasyPros projections", f"https://www.fantasypros.com/nfl/projections/{pos}.php?week={week}", "Public projection table. Partial board."),
        ("4for4", f"https://www.4for4.com/fantasy-football-rankings/{pos}/2026/week{week}", "Public top of the weekly board. Partial board."),
    ]


def _mash(maps: dict, bank: dict, pos: str | None = None, cap: int | None = None, long_core=None) -> list:
    keys = set()
    for mp in maps.values():
        keys.update(mp)
    rows = []
    for k in keys:
        info = bank.get(k) or {"name": k, "key": k}
        if pos and (info.get("pos") or "").upper() not in {pos, ""}:
            # keep if any board filed them at this pos
            if not any(k in mp for mp in maps.values()):
                continue
        shown = {}
        for src, mp in maps.items():
            rk = mp.get(k)
            if rk:
                shown[src] = rk
        if not shown:
            continue
        rows.append({
            **info,
            "key": k,
            "pos": (info.get("pos") or pos or "").upper(),
            "n": len(shown),
            "avg": super_avg(shown, long_core if long_core is not None else WEEKLY_LONG),
            "ranks": shown,
        })
    rows.sort(key=lambda r: (r["avg"], r["name"]))
    if cap:
        rows = rows[:cap]
    out = []
    for i, r in enumerate(rows, 1):
        fpts = r.get("fpts") or r.get("fpts_fp")
        out.append({**r, "bk": i, "value": bk_value(i), "fpts": fpts})
    return out


def weekly_board(pos: str, cap: int | None = None) -> list:
    pos = pos.upper()
    return _mash(weekly_maps(pos), _info_bank(), pos=pos, cap=cap)


def weekly_flex(cap: int = 150) -> list:
    maps = {
        "FantasyPros Flex ECR": _rank_map("fp-ecr-flex"),
        "RotoWire projections": {
            k: i
            for i, (k, _) in enumerate(
                sorted(
                    (
                        (_norm(r["name"]), r["fpts"])
                        for r in (_load("rw-proj").get("players") or [])
                        if r.get("pos") in {"RB", "WR", "TE"} and r.get("fpts")
                    ),
                    key=lambda kv: -kv[1],
                ),
                1,
            )
        },
    }
    return _mash(maps, _info_bank(), cap=cap, long_core=("FantasyPros Flex ECR",))


WEEKLY_FLEX_SOURCES = [
    ("FantasyPros Flex ECR", "https://www.fantasypros.com/nfl/rankings/ppr-flex.php", "Week N PPR flex consensus. Unranked is a skip."),
    ("RotoWire projections", "https://www.rotowire.com/football/", "RB/WR/TE ranked by Week N PPR points."),
]


def adp_rows(board_rows: list) -> list:
    """The Board rank vs ESPN ADP and RotoWire/Sleeper ADP."""
    bank = _info_bank()
    board = {_norm(r["name"]): r for r in board_rows}
    keys = set(board) | {_norm(r["name"]) for r in (_load("espn-adp").get("players") or []) if r.get("adp")}
    rows = []
    for k in keys:
        info = bank.get(k) or {}
        br = board.get(k)
        espn = info.get("espn_adp")
        sleeper_adp = info.get("adp")
        if not br and espn is None:
            continue
        if (info.get("pos") or "") not in {"QB", "RB", "WR", "TE", ""}:
            continue
        board_rk = br["bk"] if br else None
        delta = None
        if board_rk and espn:
            delta = round(float(espn) - float(board_rk), 2)
        rows.append({
            "name": (br or info).get("name") or k,
            "pos": (br or info).get("pos") or "",
            "team": (br or info).get("team") or "",
            "board": board_rk,
            "espn_adp": round(float(espn), 2) if espn else None,
            "ud_adp": round(float(sleeper_adp), 2) if sleeper_adp else None,
            "delta": delta,
            "n": (1 if board_rk else 0) + (1 if espn else 0),
            "avg": board_rk or espn or 999,
        })
    rows.sort(key=lambda r: (r["board"] is None, r["board"] or 999, r["name"]))
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(r["board"] or i)})
    return out


ADP_SOURCES = [
    ("The Board", "https://ballkeep.com/board.html", "Ball Keep redraft PPR Super Aggregate. Fifteen boards."),
    ("ESPN ADP", "https://fantasy.espn.com/", "Public ESPN average draft position, 2026 PPR."),
    ("Underdog / Sleeper ADP", "https://sleeper.com/", "adp_dd_ppr on the RotoWire projection feed."),
]


def waiver_board(cap: int = 60) -> list:
    """Week N adds: weekly rankers who are not locked roster locks."""
    mixed = []
    for pos in ("QB", "RB", "WR", "TE"):
        for r in weekly_board(pos):
            owned = r.get("owned")
            pct = r.get("pct_owned")
            adp = r.get("espn_adp")
            if owned is not None and float(owned) >= 70:
                continue
            if pct is not None and float(pct) >= 70:
                continue
            if adp is not None and float(adp) <= 50:
                continue
            mixed.append(r)
    mixed.sort(key=lambda r: (r["avg"], r["name"]))
    out = []
    seen = set()
    for r in mixed:
        if r["key"] in seen:
            continue
        seen.add(r["key"])
        out.append(r)
    for i, r in enumerate(out, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return out[:cap]


WAIVER_SOURCES = [
    ("Weekly skill mash", "https://ballkeep.com/weekly.html", "Same Week N boards, names that are not roster locks."),
    ("ESPN ownership / ADP", "https://fantasy.espn.com/", "Cuts players already drafted in most rooms."),
    ("FantasyPros roster percent", "https://www.fantasypros.com/", "owned-average on the weekly ECR dump."),
]


def _week1_waiver_payload() -> dict:
    path = WEEKLY / "week1_waiver_sources.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def week1_waiver_maps() -> dict:
    """Published pre-Week 1 waiver ranks. Kickers and DST stay off."""
    skip = {"DST", "K", "DEF", "D/ST"}
    maps = {}
    for src in (_week1_waiver_payload().get("sources") or []):
        mp = {}
        for row in src.get("players") or []:
            pos = (row.get("pos") or "").upper()
            if pos in skip:
                continue
            name = row.get("name") or ""
            rk = int(row.get("rank") or 0)
            if name and rk:
                mp[_norm(name)] = rk
        if mp:
            maps[src["name"]] = mp
    return maps


def week1_waiver_board(cap: int = 60) -> list:
    """Pre-Week 1 consensus adds from published waiver lists."""
    payload = _week1_waiver_payload()
    maps = week1_waiver_maps()
    bank = dict(_info_bank())
    for src in (payload.get("sources") or []):
        for row in src.get("players") or []:
            name = row.get("name") or ""
            if not name:
                continue
            k = _norm(name)
            cur = dict(bank.get(k) or {"name": name, "key": k})
            if not cur.get("name"):
                cur["name"] = name
            if row.get("pos") and not cur.get("pos"):
                cur["pos"] = row["pos"]
            if row.get("team") and not cur.get("team"):
                cur["team"] = row["team"]
            if name and len(name) > len(cur.get("name") or ""):
                cur["name"] = name
            bank[k] = cur
    rows = [r for r in _mash(maps, bank, long_core=("FantasyPros WW ECR",)) if r["n"] >= 2]
    out = []
    for i, r in enumerate(rows[:cap], 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


def week1_waiver_sources() -> list:
    out = []
    for src in (_week1_waiver_payload().get("sources") or []):
        out.append((src["name"], src.get("url") or "", src.get("note") or ""))
    return out


WEEK1_WAIVER_SOURCES = week1_waiver_sources()


def injury_rows() -> list:
    bank = _info_bank()
    skill = {"QB", "RB", "WR", "TE", "K", "FB"}
    rows = []
    for row in (_load("injuries").get("players") or []):
        pos = (row.get("pos") or "").upper()
        if pos and pos not in skill:
            continue
        info = bank.get(_norm(row.get("name") or "")) or {}
        rows.append({
            "name": row.get("name"),
            "pos": pos or info.get("pos") or "",
            "team": info.get("team") or TEAM_FROM_NAME.get(row.get("team_name") or "") or "",
            "status": row.get("status") or "",
            "note": row.get("note") or "",
        })
    order = {"Out": 0, "Doubtful": 1, "Questionable": 2, "Injured Reserve": 3}
    rows.sort(key=lambda r: (order.get(r["status"], 9), r["pos"], r["name"]))
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i), "n": 1, "avg": i})
    return out


INJURY_SOURCES = [
    ("ESPN injury report", "https://www.espn.com/nfl/injuries", "Official designations scraped from the ESPN club tables."),
]


def depth_rows() -> list:
    data = _load("depth-charts")
    teams = data.get("teams") or []
    out = []
    for t in teams:
        abbr = t.get("team") or ""
        slots = t.get("slots") or {}
        out.append({
            "team": abbr,
            "name": TEAM_TO_NAME.get(abbr, abbr),
            "qb": ", ".join(x["name"] for x in (slots.get("QB") or [])[:3]),
            "rb": ", ".join(x["name"] for x in (slots.get("RB") or [])[:4]),
            "wr": ", ".join(x["name"] for x in (slots.get("WR") or [])[:4]),
            "te": ", ".join(x["name"] for x in (slots.get("TE") or [])[:3]),
            "slots": slots,
        })
    out.sort(key=lambda r: r["name"])
    return out


DEPTH_SOURCES = [
    ("Sleeper depth charts", "https://sleeper.com/", "depth_chart_order on the 2026 Sleeper player file."),
]


def usage_for(name: str) -> dict | None:
    data = _load("usage-2025")
    players = data.get("players") or {}
    if name in players:
        return players[name]
    key = _norm(name)
    for raw, row in players.items():
        if _norm(raw) == key:
            return row
    return None


def usage_index() -> dict:
    data = _load("usage-2025")
    out = {}
    for raw, row in (data.get("players") or {}).items():
        out[_norm(raw)] = row
    return out


def sos_rows(nfl_games: list, week: int | None = None) -> list:
    """Remaining schedule vs our season DST board. Higher avg = easier (weaker fantasy DST)."""
    week = week or week_num()
    dst = {r["team"]: r["bk"] for r in dst_board()}
    remaining = {}
    this_week = {}
    for g in nfl_games:
        wk = g.get("week")
        away, home = g.get("away"), g.get("home")
        a, h = TEAM_FROM_NAME.get(away), TEAM_FROM_NAME.get(home)
        if not a or not h:
            continue
        if wk == week:
            this_week[a] = (h, "at")
            this_week[h] = (a, "vs")
        if wk is None or wk < week:
            continue
        remaining.setdefault(a, []).append(dst.get(h) or 16)
        remaining.setdefault(h, []).append(dst.get(a) or 16)
    rows = []
    for name, abbr in DST_TEAMS:
        nums = remaining.get(abbr) or []
        if not nums:
            continue
        avg = round(sum(nums) / len(nums), 2)
        opp, prep = this_week.get(abbr, ("", ""))
        rows.append({
            "name": name,
            "team": abbr,
            "pos": "DST",
            "avg": avg,
            "n": len(nums),
            "opp": TEAM_TO_NAME.get(opp, opp),
            "opp_abbr": opp,
            "prep": prep,
            "opp_dst": dst.get(opp),
        })
    rows.sort(key=lambda r: (-r["avg"], r["name"]))
    out = []
    for i, r in enumerate(rows, 1):
        out.append({**r, "bk": i, "value": bk_value(i)})
    return out


SOS_SOURCES = [
    ("Season DST board", "https://ballkeep.com/defenses.html", "Remaining opponents scored by our nine-board DST Super Aggregate. Higher average means easier leftover clubs."),
    ("2026 NFL schedule", "https://ballkeep.com/nfl-schedule.html", "Weeks still in front of each club."),
]


def start_sit_players() -> list:
    """Compact payload for the Week N comparer."""
    seen = {}
    for pos in ("QB", "RB", "WR", "TE"):
        for r in weekly_board(pos):
            seen[_norm(r["name"])] = {
                "name": r["name"],
                "pos": r.get("pos") or pos,
                "team": r.get("team") or "",
                "week_rk": r["bk"],
                "avg": r["avg"],
                "n": r["n"],
                "fpts": r.get("fpts"),
                "opp": r.get("opp") or "",
                "injury": r.get("injury") or r.get("status") or "",
                "owned": r.get("owned"),
            }
    return sorted(seen.values(), key=lambda r: (r["pos"], r["week_rk"], r["name"]))


def weekly_check_bits(nfl_games: list) -> dict:
    week = week_num()
    qb = weekly_board("QB")
    rb = weekly_board("RB")
    wr = weekly_board("WR")
    te = weekly_board("TE")
    waivers = week1_waiver_board()
    inj = [r for r in injury_rows() if r["status"] in {"Out", "Doubtful", "Questionable"}][:12]
    sos = sos_rows(nfl_games, week)
    return {
        "week": week,
        "starts": {
            "QB": qb[:5],
            "RB": rb[:5],
            "WR": wr[:5],
            "TE": te[:5],
        },
        "waivers": waivers[:10],
        "injuries": inj,
        "easiest": sos[:5],
        "hardest": list(reversed(sos[-5:])) if sos else [],
    }
