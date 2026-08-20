#!/usr/bin/env python3
"""Pull the public ranking boards Ball Keep aggregates and write data/ranks/.

Football: PFN Superflex table, FantasyPros Superflex ECR / PPR / rookies,
KeepTradeCut Superflex, Dynasty Nerds Superflex JSON-LD.
Baseball: FantasyPros keeper/dynasty ECR.

Unranked names stay skipped in the mean — this script only stores names a
board actually published.
"""
from __future__ import annotations

from html import unescape
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RANK_DIR = ROOT / "data" / "ranks"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

URLS = {
    "pfn": "https://www.profootballnetwork.com/dynasty-fantasy-football-rankings/",
    "fp_sf": "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php",
    "fp_ppr": "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php",
    "fp_rook": "https://www.fantasypros.com/nfl/rankings/dynasty-rookies-superflex.php",
    "fp_bb": "https://www.fantasypros.com/mlb/rankings/dynasty-overall.php",
    "ktc": "https://keeptradecut.com/dynasty-rankings",
    "dn": "https://www.dynastynerds.com/dynasty-rankings/superflex/",
}


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
                return json.loads(text[i : j + 1])
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


def ktc_names(html: str) -> list[str]:
    arr = extract_js_assign(html, "playersArray") or []
    scored = []
    for p in arr:
        sf = p.get("superflexValues") or {}
        rank = sf.get("rank")
        if not rank:
            continue
        scored.append((int(rank), p.get("playerName") or ""))
    scored.sort()
    names = unique_names([n for _r, n in scored])
    print(f"  KeepTradeCut Superflex n={len(names)} top={names[:5]}")
    return names


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
        age = prev.get("age") or 24
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


def main() -> int:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    pages = {}
    for key, url in URLS.items():
        print(f"fetch {key}")
        try:
            pages[key] = fetch(url)
        except Exception as exc:
            print(f"  skip {key}: {type(exc).__name__}: {exc}")

    if "fp_sf" in pages:
        dump_names("fp-dynasty-sf", fp_names(pages["fp_sf"]))
    if "fp_ppr" in pages:
        dump_names("fp-ppr", fp_names(pages["fp_ppr"]))
    if "fp_rook" in pages:
        dump_names("fp-rookies", fp_names(pages["fp_rook"]))
    if "fp_bb" in pages:
        dump_names("fp-bb-dynasty", fp_names(pages["fp_bb"]))
    if "ktc" in pages:
        dump_names("ktc-sf", ktc_names(pages["ktc"]))
    if "dn" in pages:
        dump_names("dn-sf", dn_names(pages["dn"]))
    if "pfn" in pages:
        write_pfn_txt(parse_pfn(pages["pfn"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
