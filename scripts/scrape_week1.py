#!/usr/bin/env python3
"""Fetch Week 1 DST, kicker, and pick-em pages. Write data/ranks/week1-*.json."""
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
    "fp_dst": "https://www.fantasypros.com/nfl/rankings/dst.php",
    "fp_k": "https://www.fantasypros.com/nfl/rankings/k.php",
    "fp_dst_proj": "https://www.fantasypros.com/nfl/projections/dst.php?week=1",
    "fp_k_proj": "https://www.fantasypros.com/nfl/projections/k.php",
    "ds_dst": "https://www.draftsharks.com/weekly-rankings/1/def",
    "ds_k": "https://www.draftsharks.com/weekly-rankings/1/k/ppr",
    "four_dst": "https://www.4for4.com/fantasy-football-rankings/def/2026/week1",
    "four_k": "https://www.4for4.com/fantasy-football-rankings/k/2026/week1",
    "rb_dst": "https://www.rotoballer.com/updated-week-1-fantasy-football-team-defense-def-rankings-2026/1911982",
    "rb_k": "https://www.rotoballer.com/week-1-fantasy-football-kicker-k-updated-rankings-2026/1922819",
    "rw_dst": "https://www.rotowire.com/football/article/streaming-defenses-dst-picks-for-week-1-132259",
    "espn_dst": "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804273/nfl-fantasy-football-rankings-2026-dst-defense",
    "espn_k": "https://www.espn.com/fantasy/football/story/_/page/FFWeeklyPlayerRank26-49804233/nfl-fantasy-football-rankings-2026-k-kicker",
    "espn_picks": "https://www.espn.com/nfl/picks/_/week/1/year/2026/seasontype/2",
    "espn_picks2": "https://www.espn.com/nfl/picks/_/week/1/seasontype/2",
    "cbs_picks": "https://www.cbssports.com/nfl/picks/experts/straight-up/1/",
    "busr": "https://www.busr.ag/news/nfl/nfl-picks-predictions-for-week-1-games",
    "covers": "https://www.covers.com/nfl/picks",
    "oddsshark": "https://www.oddsshark.com/nfl/computer-picks",
    "teamrankings": "https://www.teamrankings.com/nfl/picks",
    "fox_picks": "https://www.foxsports.com/stories/nfl/nfl-picks-predictions-week-1-2026",
    "usa_picks": "https://www.usatoday.com/story/sports/nfl/2026/09/nfl-week-1-picks-predictions/",
    "sn_picks": "https://www.sportingnews.com/us/nfl/news/nfl-picks-predictions-week-1-2026",
    "action": "https://www.actionnetwork.com/nfl/picks",
    "pickwatch": "https://www.pickwatch.com/nfl",
    "azcentral": "https://www.azcentral.com/story/sports/nfl/2026/09/03/nfl-week-1-odds-spreads-predictions/",
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


def dump(name: str, data) -> None:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    dest = RANK_DIR / f"{name}.json"
    dest.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  wrote {dest}")


def fp_ecr(html: str, label: str):
    data = extract_js_assign(html, "ecrData") or {}
    players = data.get("players") or []
    ordered = sorted(players, key=lambda p: int(p.get("rank_ecr") or 10**9))
    names = []
    for p in ordered:
        names.append({
            "name": p.get("player_name") or "",
            "team": p.get("player_team_id") or "",
            "rank": int(p.get("rank_ecr") or 0),
        })
    print(f"  {label} ECR n={len(names)} updated={data.get('last_updated')} top={[p['name'] for p in names[:5]]}")
    return {"updated": data.get("last_updated"), "type": data.get("ranking_type_name"), "players": names}


def main() -> int:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    for key, url in URLS.items():
        print(f"fetch {key} {url}")
        try:
            html = fetch(url)
        except Exception as exc:
            print(f"  skip {key}: {type(exc).__name__}: {exc}")
            continue
        snippet = RANK_DIR / f"week1-raw-{key}.html"
        snippet.write_text(html)
        print(f"  saved {snippet} ({len(html)} bytes)")
        if key in ("fp_dst", "fp_k"):
            dump(f"week1-{key}", fp_ecr(html, key))
        # keep raw HTML for the rest; parsers in week1_boards read published maps
    return 0


if __name__ == "__main__":
    sys.exit(main())
