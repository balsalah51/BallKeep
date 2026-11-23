#!/usr/bin/env python3
"""Pull the public ranking boards Ball Keep aggregates and write data/ranks/.

Football: PFN Superflex table, FantasyPros Superflex ECR / PPR / rookies,
KeepTradeCut Superflex, Dynasty Nerds Superflex JSON-LD, plus article
boards (Karabell, Yates, Clay, NBC, Draft Sharks, Footballguys).
Baseball: FantasyPros keeper/dynasty ECR.

Unranked names stay skipped in the mean - this script only stores names a
board actually published.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RANK_DIR = ROOT / "data" / "ranks"
META_WEEKLY = ROOT / "data" / "weekly" / "meta.json"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

URLS = {
    "pfn": "https://www.profootballnetwork.com/dynasty-fantasy-football-rankings/",
    "fp_sf": "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php",
    # Rest-of-season PPR (in-season). Draft cheatsheets stop updating after Week 1.
    "fp_ppr": "https://www.fantasypros.com/nfl/rankings/ros-ppr-overall.php",
    "fp_rook": "https://www.fantasypros.com/nfl/rankings/dynasty-rookies-superflex.php",
    "fp_bb": "https://www.fantasypros.com/mlb/rankings/dynasty-overall.php",
    "fp_nba": "https://www.fantasypros.com/nba/rankings/dynasty-overall.php",
    "ktc": "https://keeptradecut.com/dynasty-rankings",
    "dn": "https://www.dynastynerds.com/dynasty-rankings/superflex/",
    "karabell": "https://www.espn.com/fantasy/football/story/_/id/47539664",
    "yates": "https://www.espn.com/fantasy/football/story/_/id/48711830",
    "clay": "https://www.espn.com/fantasy/football/story/_/id/15698900",
    "nbc": "https://www.nbcsports.com/fantasy/football/news/2026-fantasy-football-top-200-overall-rankings",
    "ds_sf": "https://www.draftsharks.com/dynasty-rankings/superflex",
    "ds_ppr": "https://www.draftsharks.com/rankings/ppr",
    "fbg": "https://www.footballguys.com/rankings",
    "fp_sf_experts": "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php",
    "fp_ppr_experts": "https://www.fantasypros.com/nfl/fantasy-football-rankings/ppr-overall.php",
}

# Boards older than this are skipped at aggregate time (see build_site.aggregate).
MAX_AGE_DAYS = 10


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json"})
    with urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_js_assign(text: str, var: str):
    m = re.search(rf"var {re.escape(var)}\s*=\s*", text)
    if not m:
        return None
    i = m.end()
    while i < len(text) and text[i] in " \n\r\t":
        i += 1
    if i >= len(text) or text[i] not in "{[":
        return None
    opener = text[i]
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for j in range(i, len(text)):
        c = text[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
            continue
        if c in ('"', "'"):
            in_str = True
            quote = c
            continue
        if c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[i : j + 1])
                except json.JSONDecodeError:
                    return None
    return None


def extract_json_script(html: str, elem_id: str):
    m = re.search(
        rf'<script[^>]*\bid=["\']{re.escape(elem_id)}["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def unique_names(names: list[str]) -> list[str]:
    out = []
    seen = set()
    for n in names:
        n = (n or "").strip()
        if not n:
            continue
        key = re.sub(r"\s+", " ", n)
        if key.lower() in seen:
            continue
        seen.add(key.lower())
        out.append(key)
    return out


def fp_names(html: str) -> list[str]:
    data = extract_js_assign(html, "ecrData") or {}
    players = data.get("players") or []
    ordered = sorted(players, key=lambda p: int(p.get("rank_ecr") or 10**9))
    names = unique_names([p.get("player_name") or "" for p in ordered])
    print(f"  FantasyPros {data.get('ranking_type_name')} {data.get('scoring')} "
          f"updated {data.get('last_updated')} n={len(names)} "
          f"top={names[:5]}")
    return names


def ktc_rows(html: str) -> list[dict]:
    arr = extract_json_script(html, "ktc-players") or extract_js_assign(html, "playersArray") or []
    scored = []
    for p in arr:
        sf = p.get("superflexValues") or {}
        rank = sf.get("rank")
        if not rank:
            continue
        age = p.get("age")
        try:
            age_i = int(age)
        except (TypeError, ValueError):
            age_i = ""
        scored.append((int(rank), {
            "name": p.get("playerName") or "",
            "pos": p.get("position") or "",
            "team": p.get("team") or "",
            "age": age_i,
        }))
    scored.sort()
    rows = []
    seen = set()
    for _rank, row in scored:
        name = (row.get("name") or "").strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        rows.append(row)
    print(f"  KeepTradeCut Superflex n={len(rows)} top={[r['name'] for r in rows[:5]]}")
    return rows


def ktc_names(html: str) -> list[str]:
    return [r["name"] for r in ktc_rows(html) if r.get("name")]


def dn_names(html: str) -> list[str]:
    items = re.findall(
        r'\{"@type":"ListItem","position":(\d+),"name":"([^"]+)"\}',
        html,
    )
    items.sort(key=lambda kv: int(kv[0]))
    names = unique_names([n for _p, n in items])
    print(f"  Dynasty Nerds Superflex n={len(names)} top={names[:5]}")
    return names


def parse_pfn(html: str) -> list[dict]:
    rows = []
    seen = set()
    body = html
    if "<tbody>" in html:
        body = html.split("<tbody>", 1)[1]
    for chunk in body.split("<tr>")[1:]:
        rank_m = re.search(r'<div class="ta-l">(\d+)</div>', chunk)
        name_m = re.search(r'data-filter="([^"]+)"', chunk)
        pos_m = re.search(r'data-filter="(QB|RB|WR|TE)"', chunk)
        team_m = re.search(r"onTeamLinkClick\('([A-Z]{2,3})'\)", chunk)
        if not team_m:
            team_m = re.search(r"<span>([A-Z]{2,3})</span>", chunk)
        if not (rank_m and name_m and pos_m):
            continue
        name = unescape(name_m.group(1)).strip()
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        team = (team_m.group(1) if team_m else "").replace("GBP", "GB").replace("KCC", "KC")
        team = team.replace("NOS", "NO").replace("SFO", "SF").replace("LVR", "LV").replace("NEP", "NE")
        rows.append({
            "rank": int(rank_m.group(1)),
            "name": name,
            "pos": pos_m.group(1),
            "team": team,
        })
    rows.sort(key=lambda r: r["rank"])
    print(f"  PFN Superflex n={len(rows)} top={[r['name'] for r in rows[:5]]}")
    return rows


def old_pfn_meta() -> dict:
    meta = {}
    path = ROOT / "data" / "pfn-dynasty.txt"
    if not path.exists():
        return meta
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(QB|RB|WR|TE)\s*\|\s*([A-Z]{2,3})\s*\|\s*(\d+)\s*\|",
            line,
        )
        if not m:
            continue
        meta[m.group(2).strip().lower()] = {
            "team": m.group(4),
            "age": int(m.group(5)),
            "pos": m.group(3),
        }
    return meta


def write_pfn_txt(rows: list[dict]) -> None:
    old = old_pfn_meta()
    lines = [
        "Superflex Non-PPR Dynasty Rankings 2026",
        "",
        "Refreshed from Pro Football Network public board.",
        "",
        "| Overall ▲ | Player | Position | Team | Age | Pos. Rank | Katz | Soppe |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        prev = old.get(r["name"].lower(), {})
        team = r["team"] or prev.get("team") or "FA"
        age = prev.get("age") or ""
        pos_rank = ""
        lines.append(
            f"| {r['rank']} | {r['name']} | {r['pos']} | {team} | {age} | {pos_rank} |  |  |"
        )
    dest = ROOT / "data" / "pfn-dynasty.txt"
    dest.write_text("\n".join(lines) + "\n")
    print(f"  wrote {dest} ({len(rows)} rows)")


def dump_names(name: str, names: list[str]) -> None:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    dest = RANK_DIR / f"{name}.json"
    dest.write_text(json.dumps(names, indent=2) + "\n")
    print(f"  wrote {dest} ({len(names)})")


def dump_map(name: str, ranks: dict[str, int]) -> None:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    dest = RANK_DIR / f"{name}.json"
    dest.write_text(json.dumps(ranks, indent=2) + "\n")
    print(f"  wrote {dest} ({len(ranks)})")


def _strip_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html)
    html = re.sub(r"<[^>]+>", "\n", html)
    return re.sub(r"\s+", " ", unescape(html).replace("\xa0", " "))


_SUFFIX = re.compile(r"\s+(Jr\.?|Sr\.?|III|II|IV)$", re.I)
_NAME_ALIASES = {
    "D.J. Moore": "DJ Moore",
    "Patrick Mahomes II": "Patrick Mahomes",
    "Tetairoa Mcmillan": "Tetairoa McMillan",
    "Chigoziem Okonkwo": "Chig Okonkwo",
    "Oronde Gadsden II": "Oronde Gadsden",
    "A.J. Barner": "AJ Barner",
    "Tre Harris": "Tre' Harris",
}


def clean_name(name: str) -> str:
    n = unescape(name or "").replace("’", "'").replace("‘", "'")
    n = re.sub(r"\s+", " ", n).strip()
    n = _SUFFIX.sub("", n).strip()
    return _NAME_ALIASES.get(n, n)


def unique_clean(names: list[str]) -> list[str]:
    return unique_names([clean_name(n) for n in names])


def parse_karabell(html: str) -> tuple[list[str], list[str]]:
    text = _strip_html(html)
    idx = text.find("Flex (RB, WR, TE only)")
    pat = re.compile(r"(\d+)\.\s+([A-Za-z][^,]{1,50}?),\s+([^()]+?)\s+\((QB|RB|WR|TE)\d*\)")

    def board(chunk: str, last: int) -> list[str]:
        rows = pat.findall(chunk)
        start = 0
        for i, (rk, _n, _t, _p) in enumerate(rows):
            if int(rk) == 1:
                start = i
        seen = set()
        out = []
        for rk, name, _t, _p in rows[start:]:
            rk = int(rk)
            if rk in seen or rk > last:
                continue
            seen.add(rk)
            out.append((rk, clean_name(name)))
        out.sort()
        return [n for _r, n in out]

    sf = board(text[:idx] if idx > 0 else text, 200)
    flex = board(text[idx:] if idx > 0 else "", 163)
    print(f"  Karabell SF n={len(sf)} Flex n={len(flex)} top={sf[:5]}")
    return sf, flex


def parse_yates(html: str) -> tuple[list[dict], list[str], list[str]]:
    text = _strip_html(html)
    pat = re.compile(
        r"(\d+)\.\s+([A-Za-z][A-Za-z' .\-]{1,45}?),\s*([A-Z]{2,4})\s*\((QB|RB|WR|TE|K|DST)\d*\)"
    )
    rows = pat.findall(text)
    start = 0
    for i, (rk, *_rest) in enumerate(rows):
        if int(rk) == 1:
            start = i
    skill, kickers, dst = [], [], []
    seen = set()
    team_map = {"WSH": "WAS", "JAC": "JAX"}
    for _rk, name, team, pos in rows[start:]:
        name = clean_name(name.replace(" DST", ""))
        team = team_map.get(team, team)
        key = (name.lower(), pos)
        if key in seen:
            continue
        seen.add(key)
        if pos in ("QB", "RB", "WR", "TE"):
            skill.append({"name": name, "pos": pos, "team": team})
        elif pos == "K":
            kickers.append(name)
        elif pos == "DST":
            dst.append(team)
    print(f"  Yates skill n={len(skill)} K n={len(kickers)} DST n={len(dst)}")
    return skill, kickers, dst


def parse_clay(html: str) -> list[str]:
    text = _strip_html(html)
    parts = re.split(r"Overall top 240", text, flags=re.I)
    chunk = parts[-1]
    chunk = re.split(r"Top 80 rookies|Rookie top 80", chunk, flags=re.I)[0]
    pat = re.compile(r"(\d+)\.\s+([A-Za-z][A-Za-z' .\-]{1,40}?),\s*([A-Z]{2,3})\s*--\s*(QB|RB|WR|TE)\d*")
    seen = {}
    for m in pat.finditer(chunk):
        rk = int(m.group(1))
        if rk not in seen:
            seen[rk] = clean_name(m.group(2))
    names = [seen[i] for i in range(1, 241) if i in seen]
    print(f"  Clay dynasty n={len(names)} top={names[:5]}")
    return names


def parse_nbc(html: str) -> list[str]:
    rows = []
    for m in re.finditer(
        r"<tr[^>]*>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>\s*([^<]+)</td>\s*<td[^>]*>\s*([A-Z]{2,3})\s*</td>\s*<td[^>]*>\s*(QB|RB|WR|TE)",
        html,
    ):
        rows.append((int(m.group(1)), clean_name(m.group(2))))
    rows.sort()
    names = unique_clean([n for _r, n in rows])
    print(f"  NBC PPR n={len(names)} top={names[:5]}")
    return names


def parse_draftsharks(html: str) -> list[str]:
    names = unique_clean(re.findall(r'data-player-name="([^"]+)"', html))
    print(f"  Draft Sharks n={len(names)} top={names[:5]}")
    return names


_NFL_TEAMS = {
    "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills",
    "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns",
    "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers",
    "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs",
    "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
    "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants",
    "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers",
    "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Commanders",
}
_KICKERS = {
    "Brandon Aubrey", "Ka'imi Fairbairn", "Cameron Dicker", "Jason Myers", "Cam Little",
    "Eddy Pineiro", "Tyler Loop", "Evan McPherson", "Jake Bates", "Cairo Santos",
    "Andy Borregales", "Harrison Mevis", "Chase McLaughlin", "Chris Boswell",
    "Harrison Butker", "Will Reichard", "Wil Lutz", "Charlie Smyth", "Jake Elliott",
    "Blake Grupe", "Tyler Bass", "Chad Ryland", "Joey Slye", "Nick Folk", "Trey Smack",
    "Daniel Carlson", "Drew Stevens",
}


def parse_fbg(html: str) -> list[str]:
    rows = []
    for m in re.finditer(r'data-playername="([^"]+)"id="table_row_[^"]+"data-rank="(\d+)"', html):
        name = clean_name(unescape(m.group(1)))
        if name in _NFL_TEAMS or name in _KICKERS:
            continue
        rows.append((int(m.group(2)), name))
    rows.sort()
    names = unique_clean([n for _r, n in rows])
    print(f"  Footballguys skill n={len(names)} top={names[:5]}")
    return names


def parse_fp_expert_cols(html: str, labels: list[str]) -> dict[str, dict[str, int]]:
    boards = {e: {} for e in labels}
    for m in re.finditer(
        r'fp-player-name="([^"]+)"[\s\S]{0,800}?</td>\s*((?:<td>\s*\d+\s*</td>\s*)+)',
        html,
    ):
        name = clean_name(unescape(m.group(1)))
        ranks = [int(x) for x in re.findall(r"<td>\s*(\d+)\s*</td>", m.group(2))]
        for i, label in enumerate(labels):
            if i < len(ranks):
                boards[label][name] = ranks[i]
    for label, board in boards.items():
        top = sorted(board.items(), key=lambda kv: kv[1])[:5]
        print(f"  {label} n={len(board)} top={top}")
    return boards


def _fp_updated(html: str) -> str:
    data = extract_js_assign(html, "ecrData") or {}
    return str(data.get("last_updated") or "")


def _stamp_weekly_meta(scraped: str) -> None:
    META_WEEKLY.parent.mkdir(parents=True, exist_ok=True)
    meta = {}
    if META_WEEKLY.exists():
        try:
            meta = json.loads(META_WEEKLY.read_text())
        except json.JSONDecodeError:
            meta = {}
    meta["scraped"] = scraped
    meta.setdefault("season", 2026)
    meta.setdefault("kickoff", "2026-09-10")
    meta.setdefault("note", "Rank refresh stamps scraped so The Keep / Board rebuilds are fresh.")
    META_WEEKLY.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  stamped {META_WEEKLY} scraped={scraped}")


def write_scrape_meta(sources: dict, scraped: str) -> None:
    """Record which football boards landed and how old their publisher stamp is."""
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    dest = RANK_DIR / "scrape-meta.json"
    doc = {
        "scraped": scraped,
        "max_age_days": MAX_AGE_DAYS,
        "sources": sources,
    }
    dest.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"  wrote {dest}")


def main() -> int:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    scraped = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    pages = {}
    landed: dict[str, dict] = {}
    for key, url in URLS.items():
        print(f"fetch {key}")
        try:
            pages[key] = fetch(url)
        except Exception as exc:
            print(f"  skip {key}: {type(exc).__name__}: {exc}")

    def mark(stem: str, ok: bool, **extra):
        landed[stem] = {"ok": ok, "scraped": scraped if ok else None, **extra}

    if "fp_sf" in pages:
        updated = _fp_updated(pages["fp_sf"])
        names = fp_names(pages["fp_sf"])
        dump_names("fp-dynasty-sf", names)
        mark("fp-dynasty-sf", bool(names), publisher_updated=updated)
    if "fp_ppr" in pages:
        updated = _fp_updated(pages["fp_ppr"])
        names = fp_names(pages["fp_ppr"])
        dump_names("fp-ppr", names)
        mark("fp-ppr", bool(names), publisher_updated=updated, kind="ros")
    if "fp_rook" in pages:
        updated = _fp_updated(pages["fp_rook"])
        names = fp_names(pages["fp_rook"])
        dump_names("fp-rookies", names)
        mark("fp-rookies", bool(names), publisher_updated=updated)
    if "fp_bb" in pages:
        dump_names("fp-bb-dynasty", fp_names(pages["fp_bb"]))
    if "fp_nba" in pages:
        dump_names("fp-nba-dynasty", fp_names(pages["fp_nba"]))
    if "ktc" in pages:
        try:
            rows = ktc_rows(pages["ktc"])
            if rows:
                dump_names("ktc-sf", rows)
                mark("ktc-sf", True)
            else:
                print("  keep existing KTC tape (parser got 0 rows)")
                mark("ktc-sf", False, reason="empty parse")
        except Exception as exc:
            print(f"  keep existing KTC tape: {type(exc).__name__}: {exc}")
            mark("ktc-sf", False, reason=str(exc))
    if "dn" in pages:
        names = dn_names(pages["dn"])
        dump_names("dn-sf", names)
        mark("dn-sf", bool(names))
    if "pfn" in pages:
        pfn_rows = parse_pfn(pages["pfn"])
        if pfn_rows:
            write_pfn_txt(pfn_rows)
            mark("pfn", True, n=len(pfn_rows))
        else:
            # Interactive PFN board is a JS shell now. Do not reuse a months-old
            # tape in a fresh Super Aggregate — mark it unavailable.
            print("  PFN tape unavailable (parser got 0 rows); excluding from fresh aggregate")
            mark("pfn", False, reason="empty parse / js shell")
    else:
        mark("pfn", False, reason="fetch failed")
    if "karabell" in pages:
        sf, flex = parse_karabell(pages["karabell"])
        if len(sf) >= 150:
            dump_names("karabell-sf", sf)
            mark("karabell-sf", True, n=len(sf))
        if len(flex) >= 120:
            dump_names("karabell-flex", flex)
            mark("karabell-flex", True, n=len(flex))
    if "yates" in pages:
        skill, kickers, dst = parse_yates(pages["yates"])
        if len(skill) >= 100:
            dest = RANK_DIR / "yates-ppr.json"
            dest.write_text(json.dumps(skill, indent=2) + "\n")
            print(f"  wrote {dest} ({len(skill)})")
            mark("yates-ppr", True, n=len(skill))
        if kickers:
            dump_names("yates-k", kickers)
        if dst:
            dump_names("yates-dst", dst)
    if "clay" in pages:
        clay = parse_clay(pages["clay"])
        if len(clay) >= 200:
            dump_names("clay-dynasty", clay)
            mark("clay-dynasty", True, n=len(clay))
    if "nbc" in pages:
        nbc = parse_nbc(pages["nbc"])
        if len(nbc) >= 150:
            dump_names("nbc-ppr", nbc)
            mark("nbc-ppr", True, n=len(nbc))
    if "ds_sf" in pages:
        names = parse_draftsharks(pages["ds_sf"])
        if names:
            dump_names("ds-sf", names)
            mark("ds-sf", True, n=len(names))
    if "ds_ppr" in pages:
        names = parse_draftsharks(pages["ds_ppr"])
        if names:
            dump_names("ds-ppr", names)
            mark("ds-ppr", True, n=len(names))
    if "fbg" in pages:
        names = parse_fbg(pages["fbg"])
        if len(names) >= 150:
            dump_names("fbg-ppr", names)
            mark("fbg-ppr", True, n=len(names))
        else:
            print(f"  Footballguys too short ({len(names)}); leaving prior tape unmarked")
            mark("fbg-ppr", False, reason=f"short parse n={len(names)}")
    experts = ("Derek Brown", "Andrew Erickson", "Pat Fitzmaurice")
    stems = {"Derek Brown": "fp-brown", "Andrew Erickson": "fp-erickson", "Pat Fitzmaurice": "fp-fitz"}
    if "fp_sf_experts" in pages:
        boards = parse_fp_expert_cols(pages["fp_sf_experts"], list(experts))
        for label, board in boards.items():
            if board:
                dump_map(f"{stems[label]}-sf", board)
                mark(f"{stems[label]}-sf", True, n=len(board))
    if "fp_ppr_experts" in pages:
        boards = parse_fp_expert_cols(pages["fp_ppr_experts"], list(experts))
        for label, board in boards.items():
            if board:
                dump_map(f"{stems[label]}-ppr", board)
                mark(f"{stems[label]}-ppr", True, n=len(board))
    # August RotoWire fallback is older than MAX_AGE_DAYS — never mark it fresh.
    mark("rotowire-sf", False, reason="no public list newer than August 2026")
    try:
        from scrape_dst import main as scrape_dst_main
        print("DST season projections + ROS rankings")
        if scrape_dst_main() == 0:
            mark("dst-season-proj", True)
            mark("dst-ros", True)
        else:
            mark("dst-season-proj", False, reason="scrape_dst failed")
            mark("dst-ros", False, reason="scrape_dst failed")
    except Exception as exc:
        print(f"  DST scrape skipped: {type(exc).__name__}: {exc}")
        mark("dst-season-proj", False, reason=str(exc))
        mark("dst-ros", False, reason=str(exc))
    write_scrape_meta(landed, scraped)
    _stamp_weekly_meta(scraped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
