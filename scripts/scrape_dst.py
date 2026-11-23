#!/usr/bin/env python3
"""Scrape season DST projections/rankings and rest-of-season DST rankings.

Season Mega Aggregate (The D):
  FantasyPros / ESPN / RotoWire season points, Imagine Fantasy P50 forecast,
  Draft Sharks DEF rankings, and FantasyPros draft DST expert boards.

Rest-of-season Super Aggregate (ROS Defenses):
  FantasyPros ROS ECR, free expert ROS boards (DST page or overall STD slice),
  ESPN remaining points, FantasySP remaining points, CBS ROS projections.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RANK_DIR = ROOT / "data" / "ranks"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

ESPN_TEAM = {
    1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN",
    8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV", 14: "LAR",
    15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ", 21: "PHI",
    22: "ARI", 23: "PIT", 24: "LAC", 25: "SF", 26: "SEA", 27: "TB", 28: "WAS",
    29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU",
}

NAME_TO_TEAM = {
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

# Draft / season-long DST expert boards (FantasyPros type=draft).
DRAFT_EXPERTS = [
    ("Derek Brown", "derek-brown"),
    ("Andrew Erickson", "andrew-erickson"),
    ("Kyle Yates", "kyle-yates"),
    ("Pat Fitzmaurice", "pat-fitzmaurice"),
    ("Ryan Linkletter", "ryanlinkletter"),
    ("Aaron St Denis", "aaron-st-denis"),
    ("Pierre Camus", "pierre-camus"),
    ("Doug Orth", "doug-orth"),
    ("Kevin English", "kevin-english"),
    ("Dalton Del Don", "dalton-del-don"),
    ("Scott Engel", "scott-engel"),
    ("Kevin Roberts", "kevin-roberts"),
]

# Rest-of-season expert boards. mode=dst uses the DST ROS page;
# mode=overall pulls DST ranks from the overall STD ROS page when DST is paywalled.
ROS_EXPERTS = [
    ("Derek Brown", "derek-brown", "overall"),
    ("Andrew Erickson", "andrew-erickson", "overall"),
    ("Kyle Yates", "kyle-yates", "dst"),
    ("Pat Fitzmaurice", "pat-fitzmaurice", "dst"),
    ("Ryan Linkletter", "ryanlinkletter", "dst"),
    ("Aaron St Denis", "aaron-st-denis", "dst"),
    ("Tal Malachovsky", "tal-malachovsky", "dst"),
    ("James Emrick-Wilson", "james-emrick-wilson", "dst"),
]


def fetch(url: str, headers: dict | None = None, timeout: int = 40) -> str:
    req = Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_json(url: str, headers: dict | None = None, timeout: int = 40):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    with urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def dump(name: str, payload: dict) -> None:
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    path = RANK_DIR / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    if payload.get("boards"):
        n = sum(len(v) for v in payload["boards"].values())
        label = f"{len(payload['boards'])} boards / {n} ranks"
    else:
        n = len(payload.get("players") or payload.get("teams") or [])
        label = str(n)
    print(f"  wrote {path.name} n={label}")


def _team(code: str) -> str:
    c = (code or "").upper().strip()
    return {"JAC": "JAX", "LA": "LAR", "WSH": "WAS", "WAS": "WAS"}.get(c, c)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


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


def extract_fp_proj_rows(html: str) -> list[dict]:
    m = re.search(r'"rows":\s*(\[)', html)
    if not m:
        return []
    i = m.start() + len('"rows":')
    while i < len(html) and html[i] in " \n\t":
        i += 1
    if i >= len(html) or html[i] != "[":
        return []
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for j in range(i, len(html)):
        c = html[j]
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
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                try:
                    rows = json.loads(html[i : j + 1])
                except json.JSONDecodeError:
                    return []
                break
    else:
        return []
    out = []
    for row in rows:
        player = row.get("player") or {}
        short = (player.get("shortName") or "").replace(" DST", "").strip()
        team = _team(short)
        try:
            fpts = float(row.get("fpts"))
        except (TypeError, ValueError):
            continue
        if not team:
            continue
        out.append({
            "name": player.get("name") or team,
            "team": team,
            "fpts": round(fpts, 2),
        })
    out.sort(key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out


def scrape_fp_season_proj() -> dict:
    url = "https://www.fantasypros.com/nfl/projections/dst.php?week=draft"
    print(f"fetch FP season DST proj {url}")
    html = fetch(url)
    rows = extract_fp_proj_rows(html)
    updated = ""
    for m in re.finditer(r"[Cc]onsensus last updated ([^\"<]+)", html):
        updated = m.group(1).strip()
        break
    if not updated:
        m = re.search(r'"subtitle":"([^"]*updated[^"]*)"', html, re.I)
        if m and "Sign up" not in m.group(1):
            updated = m.group(1).strip()
    print(f"  FP season proj n={len(rows)} updated={updated}")
    return {
        "source": "FantasyPros season projections",
        "url": url,
        "updated": updated,
        "scraped": _now(),
        "players": rows,
    }


def scrape_espn_season_proj() -> dict:
    url = (
        "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/"
        "segments/0/leaguedefaults/3?view=kona_player_info"
    )
    filt = json.dumps({
        "players": {
            "filterSlotIds": {"value": [16]},
            "limit": 50,
            "sortPercOwned": {"sortAsc": False, "sortPriority": 1},
        }
    })
    print("fetch ESPN season DST proj")
    data = fetch_json(url, headers={"X-Fantasy-Filter": filt, "Accept": "application/json"})
    rows = []
    ros_rows = []
    for wrap in data.get("players") or []:
        player = wrap.get("player") or {}
        team = ESPN_TEAM.get(player.get("proTeamId") or 0)
        if not team:
            continue
        season = None
        remaining = None
        for st in player.get("stats") or []:
            if st.get("seasonId") != 2026 or st.get("scoringPeriodId") != 0:
                continue
            if st.get("statSourceId") != 1:
                continue
            split = st.get("statSplitTypeId")
            total = st.get("appliedTotal")
            if total is None:
                continue
            if split == 2:
                season = float(total)
            elif split == 0:
                remaining = float(total)
        if season is not None and season > 0:
            rows.append({
                "name": player.get("fullName") or team,
                "team": team,
                "fpts": round(season, 2),
            })
        if remaining is not None and remaining > 0:
            ros_rows.append({
                "name": player.get("fullName") or team,
                "team": team,
                "fpts": round(remaining, 2),
            })
    rows.sort(key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    ros_rows.sort(key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(ros_rows, 1):
        r["rank"] = i
    print(f"  ESPN season proj n={len(rows)} ros n={len(ros_rows)}")
    dump("dst-espn-ros-proj", {
        "source": "ESPN rest-of-season DST projections",
        "url": "https://fantasy.espn.com/football/players/projections",
        "scraped": _now(),
        "players": ros_rows,
    })
    return {
        "source": "ESPN season projections",
        "url": "https://fantasy.espn.com/football/players/projections",
        "scraped": _now(),
        "players": rows,
    }


def scrape_rw_season_proj() -> dict:
    url = "https://api.sleeper.app/projections/nfl/2026?season_type=regular"
    print("fetch RotoWire/Sleeper season DST proj")
    data = fetch_json(url)
    rows = []
    for row in data or []:
        player = row.get("player") or {}
        if player.get("position") != "DEF" or row.get("game_id") != "season":
            continue
        team = _team(player.get("team") or row.get("team") or "")
        stats = row.get("stats") or {}
        fpts = stats.get("pts_std")
        if not team or fpts is None:
            continue
        name = f"{player.get('first_name') or ''} {player.get('last_name') or ''}".strip() or team
        rows.append({"name": name, "team": team, "fpts": round(float(fpts), 2)})
    rows.sort(key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(f"  RotoWire season proj n={len(rows)}")
    return {
        "source": "RotoWire season projections via Sleeper",
        "url": "https://www.rotowire.com/football/",
        "scraped": _now(),
        "players": rows,
    }


def scrape_imagine_season() -> dict:
    url = "https://imaginefantasyfootball.com/scouting/season-forecast/dst/"
    print(f"fetch Imagine Fantasy season DST {url}")
    html = fetch(url)
    text = unescape(re.sub(r"<script[\s\S]*?</script>", "", html))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    rows = []
    for name, team in NAME_TO_TEAM.items():
        m = re.search(
            re.escape(name) + r" D/ST.*?(\d+)\s+P50\s+(\d+)\s+FLR\s+(\d+)\s+CEIL",
            text,
        )
        if not m:
            continue
        rows.append({
            "name": name,
            "team": team,
            "fpts": float(m.group(1)),
            "flr": int(m.group(2)),
            "ceil": int(m.group(3)),
        })
    rows.sort(key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(f"  Imagine season n={len(rows)} top={[r['team'] for r in rows[:3]]}")
    return {
        "source": "Imagine Fantasy season DST forecast",
        "url": url,
        "scraped": _now(),
        "players": rows,
    }


def scrape_draftsharks_dst() -> dict:
    url = "https://www.draftsharks.com/rankings/def"
    print(f"fetch Draft Sharks DEF {url}")
    html = fetch(url)
    rows = []
    for m in re.finditer(
        r'"name":"((?:Arizona|Atlanta|Baltimore|Buffalo|Carolina|Chicago|Cincinnati|'
        r"Cleveland|Dallas|Denver|Detroit|Green Bay|Houston|Indianapolis|Jacksonville|"
        r"Kansas City|Las Vegas|Los Angeles|Miami|Minnesota|New England|New Orleans|"
        r"New York|Philadelphia|Pittsburgh|San Francisco|Seattle|Tampa Bay|Tennessee|"
        r'Washington)[^"]*)".*?ranked #(\d+) overall in our 2026 Fantasy Football Defense Rankings',
        html,
    ):
        name = m.group(1)
        team = NAME_TO_TEAM.get(name)
        if not team:
            # Chargers / Rams / Jets / Giants short forms
            for full, abbr in NAME_TO_TEAM.items():
                if name in full or full.startswith(name):
                    team = abbr
                    name = full
                    break
        if not team:
            continue
        rows.append({"name": name, "team": team, "rank": int(m.group(2))})
    # Dedupe keep best (lowest) rank
    best = {}
    for r in rows:
        prev = best.get(r["team"])
        if prev is None or r["rank"] < prev["rank"]:
            best[r["team"]] = r
    rows = sorted(best.values(), key=lambda r: r["rank"])
    print(f"  Draft Sharks n={len(rows)} top={[r['team'] for r in rows[:3]]}")
    return {
        "source": "Draft Sharks DEF rankings",
        "url": url,
        "scraped": _now(),
        "players": rows,
    }


def scrape_fp_draft_experts() -> dict:
    boards = {}
    for label, slug in DRAFT_EXPERTS:
        url = f"https://www.fantasypros.com/nfl/rankings/{slug}.php?position=DST&type=draft"
        print(f"fetch FP draft expert {label}")
        try:
            html = fetch(url)
        except (HTTPError, URLError) as exc:
            print(f"  skip {label}: {type(exc).__name__}: {exc}")
            continue
        title = (re.search(r"<title>([^<]+)", html) or [None, ""])[1]
        if "Draft" not in title and "draft" not in title.lower():
            # Fitzmaurice default draft page sometimes omits Draft in title
            if label != "Pat Fitzmaurice":
                print(f"  skip {label}: not a draft board ({title[:60]})")
                continue
        rows = parse_expert_dst_table(html)
        if len(rows) < 12:
            print(f"  skip {label}: thin board n={len(rows)}")
            continue
        boards[label] = rows
        print(f"  {label} n={len(rows)} top={[r['team'] for r in rows[:3]]}")
    return {
        "source": "FantasyPros draft DST expert boards",
        "scraped": _now(),
        "boards": boards,
    }


def scrape_fp_ros_ecr() -> dict:
    url = "https://www.fantasypros.com/nfl/rankings/ros-dst.php"
    print(f"fetch FP ROS DST ECR {url}")
    html = fetch(url)
    ecr = extract_js_assign(html, "ecrData") or {}
    players = []
    for p in ecr.get("players") or []:
        rk = int(p.get("rank_ecr") or 0)
        if not rk:
            continue
        team = _team(p.get("player_team_id") or "")
        fpts = p.get("r2p_pts")
        try:
            fpts = float(fpts) if fpts not in (None, "") else None
        except (TypeError, ValueError):
            fpts = None
        players.append({
            "name": p.get("player_name") or "",
            "team": team,
            "rank": rk,
            "ave": p.get("rank_ave"),
            "fpts": fpts,
        })
    print(
        f"  FP ROS ECR n={len(players)} experts={ecr.get('total_experts')} "
        f"updated={ecr.get('last_updated')}"
    )
    return {
        "source": "FantasyPros ROS DST ECR",
        "url": url,
        "updated": ecr.get("last_updated"),
        "experts": ecr.get("total_experts"),
        "scraped": _now(),
        "players": players,
    }


def parse_expert_dst_table(html: str) -> list[dict]:
    rows = []
    for m in re.finditer(r"<tr[^>]*>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>(.*?)</td>", html, re.S):
        rk = int(m.group(1))
        name = unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        name = re.sub(r"\s+", " ", name)
        name = re.sub(r"\s+[A-Z]{2,3}$", "", name).replace(" DST", "").strip()
        team = NAME_TO_TEAM.get(name)
        if not team:
            continue
        rows.append({"name": name, "team": team, "rank": rk})
    rows.sort(key=lambda r: r["rank"])
    return rows


def parse_overall_dst_ranks(html: str) -> list[dict]:
    """Pull DST ranks embedded in an overall STD ROS expert page."""
    rows = []
    for name, team in NAME_TO_TEAM.items():
        m = re.search(re.escape(name) + r".{0,300}?DST(\d+)", html, re.S)
        if not m:
            continue
        rows.append({"name": name, "team": team, "rank": int(m.group(1))})
    rows.sort(key=lambda r: r["rank"])
    return rows


def scrape_fp_ros_experts() -> dict:
    boards = {}
    for label, slug, mode in ROS_EXPERTS:
        if mode == "dst":
            url = f"https://www.fantasypros.com/nfl/rankings/{slug}.php?position=DST&type=ros"
        else:
            url = f"https://www.fantasypros.com/nfl/rankings/{slug}.php?scoring=STD&type=ros"
        print(f"fetch FP ROS expert {label} ({mode})")
        try:
            html = fetch(url)
        except (HTTPError, URLError) as exc:
            print(f"  skip {label}: {type(exc).__name__}: {exc}")
            continue
        title = (re.search(r"<title>([^<]+)", html) or [None, ""])[1]
        if "Rest of Season" not in title and "ROS" not in title:
            print(f"  skip {label}: not an ROS board ({title[:60]})")
            continue
        if mode == "dst":
            rows = parse_expert_dst_table(html)
            if len(rows) < 16:
                # Fall back to overall STD page
                url2 = f"https://www.fantasypros.com/nfl/rankings/{slug}.php?scoring=STD&type=ros"
                try:
                    html2 = fetch(url2)
                except (HTTPError, URLError):
                    html2 = ""
                rows = parse_overall_dst_ranks(html2) if html2 else []
        else:
            rows = parse_overall_dst_ranks(html)
            if len(rows) < 12:
                rows = parse_expert_dst_table(html)
        if len(rows) < 12:
            print(f"  skip {label}: thin board n={len(rows)}")
            continue
        boards[label] = rows
        print(f"  {label} n={len(rows)} top={[r['team'] for r in rows[:3]]}")
    return {
        "source": "FantasyPros ROS expert boards",
        "scraped": _now(),
        "boards": boards,
    }


def scrape_fantasysp_ros() -> dict:
    url = "https://www.fantasysp.com/rest-of-season/nfl/DST"
    print(f"fetch FantasySP ROS DST {url}")
    html = fetch(url)
    rows = []
    for m in re.finditer(
        r"<td>\s*(\d+)\.\s*<a[^>]*>.*?DST</a>\s*<span[^>]*>\s*([A-Z]{2,3})\s*DST</span>"
        r".*?</td>\s*<td>\s*([\d.]+)\s*</td>\s*<td>\s*([\d.]+)\s*</td>\s*<td>\s*([\d.]+)\s*</td>"
        r"\s*<td>\s*([\d.]+)\s*</td>\s*<td>\s*([\d.]+)\s*</td>\s*<td>\s*([\d.]+)\s*</td>",
        html,
        re.S,
    ):
        team = _team(m.group(2))
        fpts = float(m.group(8))
        rows.append({"team": team, "rank": int(m.group(1)), "fpts": fpts})
    rows.sort(key=lambda r: (-r["fpts"], r["rank"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(f"  FantasySP ROS n={len(rows)}")
    return {
        "source": "FantasySP ROS DST projections",
        "url": url,
        "updated": "Nov 23, 2026",
        "scraped": _now(),
        "players": rows,
    }


def scrape_cbs_ros_proj() -> dict:
    url = "https://www.cbssports.com/fantasy/football/stats/DST/2026/restofseason/projections/nonppr/"
    print(f"fetch CBS ROS DST proj {url}")
    html = fetch(url)
    seen = {}
    for m in re.finditer(
        r'/nfl/teams/([A-Z]{2,3})/[^"]*" class="">([^<]+)</a>.*?</tr>',
        html,
        re.S,
    ):
        team = _team(m.group(1))
        nums = [
            float(x)
            for x in re.findall(r"TableBase-bodyTd--number[^>]*>\s*([\d.]+)", m.group(0))
        ]
        if len(nums) < 2:
            continue
        # Last number is FPTS/G; second-to-last is remaining FPTS total.
        fpts = nums[-2]
        if team in seen:
            continue
        seen[team] = {
            "name": NAME_TO_TEAM.get(team) or m.group(2),
            "team": team,
            "fpts": round(fpts, 2),
        }
    rows = sorted(seen.values(), key=lambda r: (-r["fpts"], r["team"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(f"  CBS ROS n={len(rows)} top={[r['team'] for r in rows[:3]]}")
    return {
        "source": "CBS Sports ROS DST projections",
        "url": url,
        "scraped": _now(),
        "players": rows,
    }


def main() -> int:
    try:
        dump("dst-fp-season-proj", scrape_fp_season_proj())
        dump("dst-espn-season-proj", scrape_espn_season_proj())
        dump("dst-rw-season-proj", scrape_rw_season_proj())
        dump("dst-imagine-season", scrape_imagine_season())
        dump("dst-draftsharks", scrape_draftsharks_dst())
        dump("dst-fp-draft-experts", scrape_fp_draft_experts())
        dump("dst-fp-ros-ecr", scrape_fp_ros_ecr())
        dump("dst-fp-ros-experts", scrape_fp_ros_experts())
        dump("dst-fantasysp-ros", scrape_fantasysp_ros())
        dump("dst-cbs-ros-proj", scrape_cbs_ros_proj())
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        print("fatal", type(exc).__name__, exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
