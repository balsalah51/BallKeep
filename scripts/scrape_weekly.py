#!/usr/bin/env python3
"""Fetch weekly skill ranks, projections, ADP, injuries, usage, and depth charts.

Writes JSON under data/weekly/. Raw HTML is not committed.
Monday and Tuesday GitHub Action re-runs this, then rebuilds the site.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "weekly"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

# 2026 regular season Week 1 kickoff (Thu).
KICKOFF = date(2026, 9, 10)

POS = ("qb", "rb", "wr", "te")
TEAM_ALIAS = {
    "JAC": "JAX", "WSH": "WAS", "LA": "LAR", "LVR": "LV", "GBP": "GB",
    "KCC": "KC", "NOS": "NO", "SFO": "SF", "NEP": "NE", "TAM": "TB",
    "GNB": "GB", "NWE": "NE", "NOR": "NO", "WAS": "WAS",
}

ESPN_TEAM = {
    1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN",
    8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV", 14: "LAR",
    15: "MIA", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ",
    21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC", 25: "SF", 26: "SEA",
    27: "TB", 28: "WAS", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU",
}


def current_week(today: date | None = None) -> int:
    today = today or date.today()
    if today < KICKOFF:
        return 1
    week = 1 + ((today - KICKOFF).days + 3) // 7
    return min(18, max(1, week))


def _team(code: str) -> str:
    return TEAM_ALIAS.get((code or "").upper(), (code or "").upper())


def fetch(url: str, headers: dict | None = None, timeout: int = 40) -> str:
    h = {"User-Agent": UA, "Accept": "text/html,application/json"}
    if headers:
        h.update(headers)
    req = Request(url, headers=h)
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_json(url: str, headers: dict | None = None):
    text = fetch(url, headers=headers)
    return json.loads(text)


def dump(name: str, data) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.json"
    dest.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  wrote {dest.name}")


def extract_js_assign(text: str, var: str):
    m = re.search(rf"(?:var|let|const)\s+{re.escape(var)}\s*=\s*", text)
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


def fp_ecr(html: str, label: str) -> dict:
    data = extract_js_assign(html, "ecrData") or {}
    players = []
    for p in data.get("players") or []:
        rk = int(p.get("rank_ecr") or 0)
        if not rk:
            continue
        players.append({
            "name": p.get("player_name") or "",
            "team": _team(p.get("player_team_id") or ""),
            "pos": p.get("player_position_id") or "",
            "rank": rk,
            "ave": p.get("rank_ave"),
            "min": p.get("rank_min"),
            "max": p.get("rank_max"),
            "owned": p.get("player_owned_avg"),
            "opp": p.get("player_opponent") or "",
            "opp_id": _team(p.get("player_opponent_id") or ""),
            "bye": p.get("player_bye_week"),
            "pos_rank": p.get("pos_rank") or "",
        })
    print(f"  {label} ECR n={len(players)} week={data.get('week')} experts={data.get('total_experts')} updated={data.get('last_updated')}")
    return {
        "updated": data.get("last_updated"),
        "week": data.get("week"),
        "year": data.get("year"),
        "experts": data.get("total_experts"),
        "players": players,
    }


def parse_proj_table(html: str) -> list:
    rows = []
    for m in re.finditer(
        r'<tr[^>]*class="[^"]*mpb-player[^"]*"[^>]*>\s*<td[^>]*>.*?'
        r'fp-player-name="([^"]+)"[^>]*>.*?</a>\s*([A-Z]{2,3})?.*?</td>'
        r'(.*?)</tr>',
        html,
        re.S,
    ):
        name = unescape(m.group(1))
        team = _team(m.group(2) or "")
        cells = re.findall(r"<td[^>]*>(.*?)</td>", m.group(0), re.S)
        nums = []
        for cell in cells[1:]:
            txt = unescape(re.sub(r"<[^>]+>", "", cell)).replace(",", "").strip()
            try:
                nums.append(float(txt))
            except ValueError:
                nums.append(None)
        fpts = None
        for n in reversed(nums):
            if n is not None:
                fpts = n
                break
        if not name or fpts is None:
            continue
        rows.append({"name": name, "team": team, "fpts": fpts})
    rows.sort(key=lambda r: (-r["fpts"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def scrape_fp_weekly(week: int) -> None:
    for pos in POS:
        url = f"https://www.fantasypros.com/nfl/rankings/{pos}.php"
        print(f"fetch fp ecr {pos} {url}")
        try:
            html = fetch(url)
            dump(f"fp-ecr-{pos}", fp_ecr(html, pos.upper()))
        except Exception as exc:
            print(f"  skip {pos}: {type(exc).__name__}: {exc}")
    url = "https://www.fantasypros.com/nfl/rankings/ppr-flex.php"
    print(f"fetch fp ecr flex {url}")
    try:
        dump("fp-ecr-flex", fp_ecr(fetch(url), "FLEX"))
    except Exception as exc:
        print(f"  skip flex: {type(exc).__name__}: {exc}")

    for pos in POS:
        url = f"https://www.fantasypros.com/nfl/projections/{pos}.php?week={week}"
        print(f"fetch fp proj {pos} {url}")
        try:
            rows = parse_proj_table(fetch(url))
            print(f"  {pos} proj n={len(rows)} top={[r['name'] for r in rows[:3]]}")
            dump(f"fp-proj-{pos}", {"week": week, "players": rows})
        except Exception as exc:
            print(f"  skip proj {pos}: {type(exc).__name__}: {exc}")


def scrape_fourfor4(week: int) -> None:
    for pos in POS:
        url = f"https://www.4for4.com/fantasy-football-rankings/{pos}/2026/week{week}"
        print(f"fetch 4for4 {pos} {url}")
        try:
            html = fetch(url)
        except Exception as exc:
            print(f"  skip: {type(exc).__name__}: {exc}")
            continue
        rows = []
        for m in re.finditer(
            r'<td[^>]*data-order="(\d+)"[^>]*>\s*\d+\s*</td>\s*'
            r'<td[^>]*>.*?<a href="/player/[^"]+">([^<]+)</a>.*?</td>\s*'
            r'<td[^>]*>([A-Z]{2,3})</td>\s*'
            r'<td[^>]*>([^<]*)</td>\s*'
            r'<td[^>]*data-order="(\d+)"',
            html,
            re.S,
        ):
            name = unescape(m.group(2)).strip()
            rk = int(m.group(1))
            if name and rk:
                rows.append({
                    "name": name,
                    "rank": rk,
                    "team": _team(m.group(3)),
                    "opp": unescape(m.group(4)).strip(),
                    "sos": int(m.group(5)),
                })
        # de-dupe keeping first rank
        seen = set()
        uniq = []
        for r in rows:
            k = r["name"].lower()
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        uniq.sort(key=lambda r: r["rank"])
        print(f"  4for4 {pos} n={len(uniq)} top={[r['name'] for r in uniq[:3]]}")
        dump(f"four-{pos}", {"week": week, "players": uniq})


def scrape_fp_stats() -> None:
    """2025 season counting stats. Targets live here; snaps come from Sleeper."""
    for pos in POS:
        url = f"https://www.fantasypros.com/nfl/stats/{pos}.php?year=2025"
        print(f"fetch fp stats {pos} {url}")
        try:
            html = fetch(url)
        except Exception as exc:
            print(f"  skip: {type(exc).__name__}: {exc}")
            continue
        header_row = None
        players = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
            heads = [unescape(re.sub(r"<[^>]+>", "", h)).strip().upper() for h in re.findall(r"<th[^>]*>(.*?)</th>", tr, re.S)]
            if heads and "PLAYER" in heads:
                header_row = heads
                continue
            name_m = re.search(r'fp-player-name="([^"]+)"', tr)
            if not name_m or not header_row:
                continue
            team_m = re.search(r"</a>\s*\(([A-Z]{2,3})\)", tr)
            cells = [unescape(re.sub(r"<[^>]+>", "", c)).replace(",", "").strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            rec = {"name": unescape(name_m.group(1)), "team": _team(team_m.group(1) if team_m else "")}
            # cells align to header after rank
            labels = header_row
            if labels and labels[0] == "RANK":
                # first td is rank
                for lab, val in zip(labels, cells):
                    rec[lab.lower().replace(" ", "_").replace("%", "pct").replace("/", "_")] = val
            players.append(rec)
        print(f"  stats {pos} n={len(players)}")
        dump(f"fp-stats-{pos}", {"season": 2025, "players": players})


def _usage_from_sleeper(players, stats) -> dict:
    out = {}
    for pid, p in (players or {}).items():
        if not isinstance(p, dict):
            continue
        pos = p.get("position") or ""
        if pos not in {"QB", "RB", "WR", "TE"}:
            continue
        name = p.get("full_name") or ""
        if not name:
            continue
        st = (stats or {}).get(pid) or {}
        if not st:
            continue
        if not (st.get("off_snp") or st.get("rec_tgt") or st.get("rush_att") or st.get("pass_att")):
            continue
        off = st.get("off_snp")
        tm = st.get("tm_off_snp")
        snap_pct = round(100.0 * off / tm, 1) if off and tm else None
        out[name] = {
            "name": name,
            "pos": pos,
            "team": _team(p.get("team") or ""),
            "gp": st.get("gp"),
            "off_snp": off,
            "tm_off_snp": tm,
            "snap_pct": snap_pct,
            "rec_tgt": st.get("rec_tgt"),
            "rec": st.get("rec"),
            "rec_yd": st.get("rec_yd"),
            "rec_td": st.get("rec_td"),
            "rush_att": st.get("rush_att"),
            "rush_yd": st.get("rush_yd"),
            "rush_td": st.get("rush_td"),
            "pass_att": st.get("pass_att"),
            "pass_yd": st.get("pass_yd"),
            "pass_td": st.get("pass_td"),
            "pts_ppr": st.get("pts_ppr"),
        }
    return out


def scrape_sleeper_usage(week: int) -> None:
    print("fetch sleeper players, 2025 and 2026 stats, week projections")
    try:
        players = fetch_json("https://api.sleeper.app/v1/players/nfl")
        stats_2025 = fetch_json("https://api.sleeper.app/v1/stats/nfl/regular/2025")
        stats_2026 = fetch_json("https://api.sleeper.app/v1/stats/nfl/regular/2026")
        projs = fetch_json(f"https://api.sleeper.app/projections/nfl/2026/{week}?season_type=regular")
    except Exception as exc:
        print(f"  skip sleeper: {type(exc).__name__}: {exc}")
        return
    depth = {}
    for pid, p in (players or {}).items():
        if not isinstance(p, dict):
            continue
        pos = p.get("position") or ""
        if pos not in {"QB", "RB", "WR", "TE"}:
            continue
        name = p.get("full_name") or ""
        team = _team(p.get("team") or "")
        if not name:
            continue
        order = p.get("depth_chart_order")
        if team and order:
            depth.setdefault(team, {}).setdefault(pos, []).append({
                "name": name, "order": int(order), "slot": p.get("depth_chart_position") or pos,
            })
    for team, slots in depth.items():
        for pos, rows in slots.items():
            rows.sort(key=lambda r: r["order"])
    out_2025 = _usage_from_sleeper(players, stats_2025)
    out_2026 = _usage_from_sleeper(players, stats_2026)
    print(f"  sleeper usage 2025 n={len(out_2025)} 2026 n={len(out_2026)} depth teams={len(depth)}")
    dump("usage-2025", {"season": 2025, "players": out_2025})
    dump("usage-2026", {"season": 2026, "players": out_2026})
    dump("depth-charts", {"season": 2026, "teams": [
        {"team": team, "slots": slots} for team, slots in sorted(depth.items())
    ]})

    proj_rows = []
    for row in projs or []:
        st = row.get("stats") or {}
        pts = st.get("pts_ppr")
        if pts is None:
            continue
        pl = row.get("player") or {}
        name = (pl.get("full_name") or f"{pl.get('first_name') or ''} {pl.get('last_name') or ''}").strip()
        pos = pl.get("position") or ""
        if not name or pos not in {"QB", "RB", "WR", "TE"}:
            continue
        proj_rows.append({
            "name": name,
            "pos": pos,
            "team": _team(row.get("team") or pl.get("team") or ""),
            "opp": _team(row.get("opponent") or ""),
            "fpts": round(float(pts), 2),
            "adp": st.get("adp_dd_ppr") or st.get("adp_ppr"),
        })
    # one row per name (first / only company)
    seen = set()
    uniq = []
    for r in sorted(proj_rows, key=lambda x: (-x["fpts"], x["name"])):
        k = r["name"].lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    for i, r in enumerate(uniq, 1):
        r["rank"] = i
    print(f"  sleeper/rotowire proj n={len(uniq)} top={[r['name'] for r in uniq[:3]]}")
    dump("rw-proj", {"week": week, "source": "RotoWire via Sleeper", "players": uniq})


def scrape_espn_adp() -> None:
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/players?scoringPeriodId=0&view=kona_player_info"
    filt = json.dumps({
        "players": {
            "limit": 400,
            "sortDraftRanks": {"sortPriority": 1, "sortAsc": True, "value": "PPR"},
        }
    })
    print("fetch espn adp")
    try:
        data = json.loads(fetch(url, {"X-Fantasy-Filter": filt, "Accept": "application/json"}))
    except Exception as exc:
        print(f"  skip espn adp: {type(exc).__name__}: {exc}")
        return
    rows = []
    for p in data or []:
        name = p.get("fullName") or ""
        if not name:
            continue
        own = p.get("ownership") or {}
        ranks = p.get("draftRanksByRankType") or {}
        ppr = (ranks.get("PPR") or {}).get("rank")
        adp = own.get("averageDraftPosition")
        if not adp and not ppr:
            continue
        pos_id = p.get("defaultPositionId")
        pos = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}.get(pos_id, "")
        if pos not in {"QB", "RB", "WR", "TE"}:
            continue
        rows.append({
            "name": name,
            "pos": pos,
            "team": ESPN_TEAM.get(p.get("proTeamId") or 0, ""),
            "adp": adp,
            "espn_ppr": ppr,
            "pct_owned": own.get("percentOwned"),
            "injury": p.get("injuryStatus") or "",
        })
    rows.sort(key=lambda r: (r["adp"] is None, r["adp"] if r["adp"] is not None else 999, r["name"]))
    print(f"  espn adp n={len(rows)} top={[r['name'] for r in rows[:3]]}")
    dump("espn-adp", {"season": 2026, "players": rows})


def scrape_espn_injuries() -> None:
    print("fetch espn injuries")
    try:
        html = fetch("https://www.espn.com/nfl/injuries")
    except Exception as exc:
        print(f"  skip: {type(exc).__name__}: {exc}")
        return
    rows = []
    team = ""
    for block in re.split(r'<div class="Table__Title">', html)[1:]:
        tm = re.search(r"^([^<]+)", block)
        if tm:
            team = unescape(tm.group(1)).strip()
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
            name_m = re.search(r"<a[^>]*>([^<]+)</a>", tr)
            pos_m = re.search(r'class="col-pos[^"]*"[^>]*>([^<]+)', tr)
            stat_m = re.search(r'TextStatus[^>]*>([^<]+)', tr)
            desc_m = re.search(r'class="col-desc[^"]*"[^>]*>(.*?)</td>', tr, re.S)
            if not name_m or not stat_m:
                continue
            desc = unescape(re.sub(r"<[^>]+>", "", desc_m.group(1))).strip() if desc_m else ""
            rows.append({
                "name": unescape(name_m.group(1)).strip(),
                "pos": unescape(pos_m.group(1)).strip() if pos_m else "",
                "team_name": team,
                "status": unescape(stat_m.group(1)).strip(),
                "note": desc[:280],
            })
    print(f"  injuries n={len(rows)}")
    dump("injuries", {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "players": rows})


def write_meta(week: int) -> None:
    dump("meta", {
        "season": 2026,
        "week": week,
        "kickoff": KICKOFF.isoformat(),
        "scraped": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "note": "Monday and Tuesday refresh. Unranked on a board is a skip.",
    })


def main() -> int:
    week = current_week()
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        week = int(sys.argv[1])
    print(f"weekly scrape week={week}")
    write_meta(week)
    scrape_fp_weekly(week)
    scrape_fourfor4(week)
    scrape_fp_stats()
    scrape_sleeper_usage(week)
    scrape_espn_adp()
    scrape_espn_injuries()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        print("fatal", type(exc).__name__, exc)
        raise SystemExit(1)
