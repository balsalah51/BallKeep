"""MLB Stats API helpers for DeepBase eligibility, BK model, and lineups.

Career regular-season hitting AB and pitching IP come from statsapi.mlb.com.
Pipeline top-30s are parsed from the public MiLB prospect pages.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from bb_data import bb_norm, TEAM_FIX
from bb_prospects import load_farm as load_listed_farm
from bk_curve import bk_value

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "mlb-deep-cache.json"
UNMATCHED = ROOT / "data" / "deepbase-unmatched.json"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"

FARM_AB_MAX = 130
FARM_IP_MAX = 50.0
SEASONS = (2026, 2025, 2024)
WEIGHTS = {2026: 5, 2025: 4, 2024: 3}

TEAM_SLUGS = {
    "ATH": "athletics", "PIT": "pirates", "SD": "padres", "SEA": "mariners",
    "SF": "giants", "STL": "cardinals", "TB": "rays", "TEX": "rangers",
    "TOR": "bluejays", "MIN": "twins", "PHI": "phillies", "ATL": "braves",
    "CWS": "whitesox", "MIA": "marlins", "NYY": "yankees", "MIL": "brewers",
    "LAA": "angels", "AZ": "dbacks", "ARI": "dbacks", "BAL": "orioles",
    "BOS": "redsox", "CHC": "cubs", "CIN": "reds", "CLE": "guardians",
    "COL": "rockies", "DET": "tigers", "HOU": "astros", "KC": "royals",
    "LAD": "dodgers", "WSH": "nationals", "NYM": "mets",
}
SLUG_FALLBACKS = {
    "ARI": ["dbacks", "d-backs", "diamondbacks"],
    "CWS": ["whitesox", "white-sox"],
    "WSH": ["nationals", "nats"],
    "ATH": ["athletics", "as"],
}

POS_ORDER = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
FIELD_POS = {"C": "C", "1B": "1B", "2B": "2B", "3B": "3B", "SS": "SS",
             "LF": "LF", "CF": "CF", "RF": "RF", "OF": "LF"}


def get_json(url, timeout=60, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            time.sleep(0.4 * (i + 1))
    raise last


def get_text(url, timeout=60, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(0.4 * (i + 1))
    raise last


def ip_float(v) -> float:
    if v in (None, ""):
        return 0.0
    s = str(v)
    try:
        if "." in s:
            whole, frac = s.split(".", 1)
            return int(whole or 0) + int(frac or 0) / 3.0
        return float(s)
    except ValueError:
        return 0.0


def num(v, default=0):
    try:
        if v in (None, "", "-"):
            return default
        return float(str(v).replace(",", ""))
    except ValueError:
        return default


def is_farm_eligible(ab, ip) -> bool:
    return (ab or 0) <= FARM_AB_MAX and (ip_float(ip) if not isinstance(ip, (int, float)) else ip) <= FARM_IP_MAX


def is_majors_eligible(ab, ip) -> bool:
    ipn = ip_float(ip) if not isinstance(ip, (int, float)) else float(ip or 0)
    return (ab or 0) > FARM_AB_MAX or ipn > FARM_IP_MAX


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(doc: dict):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(doc, separators=(",", ":")))


def mlb_teams(season=2026):
    data = get_json(f"https://statsapi.mlb.com/api/v1/teams?sportId=1&season={season}")
    out = []
    for t in data.get("teams") or []:
        abbr = TEAM_FIX.get(t.get("abbreviation") or "", t.get("abbreviation") or "")
        out.append({
            "id": t["id"],
            "abbr": abbr,
            "name": t.get("name") or "",
            "team_name": t.get("teamName") or "",
            "slug": TEAM_SLUGS.get(abbr) or (t.get("teamName") or "").lower().replace(" ", ""),
        })
    out.sort(key=lambda t: t["name"])
    return out


def fetch_career_group(group: str) -> dict:
    out = {}
    offset = 0
    while True:
        url = (
            "https://statsapi.mlb.com/api/v1/stats"
            f"?stats=career&group={group}&playerPool=all&limit=1000&sportId=1&offset={offset}"
        )
        data = get_json(url)
        splits = (data.get("stats") or [{}])[0].get("splits") or []
        if not splits:
            break
        added = 0
        for split in splits:
            pid = (split.get("player") or {}).get("id")
            if not pid:
                continue
            st = split.get("stat") or {}
            rec = out.setdefault(int(pid), {"ab": 0, "ip": 0.0, "name": (split.get("player") or {}).get("fullName") or ""})
            if group == "hitting":
                rec["ab"] = int(num(st.get("atBats")))
            else:
                rec["ip"] = round(ip_float(st.get("inningsPitched")), 1)
            added += 1
        if added < 1000:
            break
        offset += 1000
        if offset > 20000:
            break
        time.sleep(0.15)
    return out


def fetch_season_group(group: str, season: int) -> dict:
    url = (
        "https://statsapi.mlb.com/api/v1/stats"
        f"?stats=season&group={group}&season={season}&playerPool=all&limit=2500&sportId=1"
    )
    data = get_json(url)
    out = {}
    for split in (data.get("stats") or [{}])[0].get("splits") or []:
        pid = (split.get("player") or {}).get("id")
        if not pid:
            continue
        st = split.get("stat") or {}
        if group == "hitting":
            out[int(pid)] = {
                "g": int(num(st.get("gamesPlayed"))),
                "ab": int(num(st.get("atBats"))),
                "pa": int(num(st.get("plateAppearances") or st.get("atBats"))),
                "r": int(num(st.get("runs"))),
                "h": int(num(st.get("hits"))),
                "2b": int(num(st.get("doubles"))),
                "3b": int(num(st.get("triples"))),
                "hr": int(num(st.get("homeRuns"))),
                "rbi": int(num(st.get("rbi"))),
                "sb": int(num(st.get("stolenBases"))),
                "bb": int(num(st.get("baseOnBalls"))),
                "hbp": int(num(st.get("hitByPitch"))),
                "sf": int(num(st.get("sacFlies"))),
                "so": int(num(st.get("strikeOuts"))),
                "obp": num(st.get("obp")),
                "avg": num(st.get("avg")),
            }
        else:
            out[int(pid)] = {
                "g": int(num(st.get("gamesPlayed"))),
                "gs": int(num(st.get("gamesStarted"))),
                "ip": round(ip_float(st.get("inningsPitched")), 1),
                "so": int(num(st.get("strikeOuts"))),
                "bb": int(num(st.get("baseOnBalls"))),
                "hr": int(num(st.get("homeRuns"))),
                "er": int(num(st.get("earnedRuns"))),
                "w": int(num(st.get("wins"))),
                "sv": int(num(st.get("saves"))),
            }
    return out


def fetch_people_batch(ids):
    out = {}
    ids = [int(i) for i in ids if i]
    for i in range(0, len(ids), 90):
        chunk = ",".join(str(x) for x in ids[i:i + 90])
        data = get_json(f"https://statsapi.mlb.com/api/v1/people?personIds={chunk}&hydrate=currentTeam")
        for p in data.get("people") or []:
            team = p.get("currentTeam") or {}
            pos = ((p.get("primaryPosition") or {}).get("abbreviation")) or ""
            abbr = TEAM_FIX.get(team.get("abbreviation") or "", team.get("abbreviation") or "")
            out[int(p["id"])] = {
                "mlb_id": int(p["id"]),
                "name": p.get("fullName") or "",
                "pos": pos,
                "team": abbr,
                "team_name": team.get("name") or "",
                "age": p.get("currentAge") or "",
                "birth": p.get("birthDate") or "",
                "active": bool(p.get("active")),
                "debut": p.get("mlbDebutDate") or "",
            }
        time.sleep(0.1)
    return out


def fetch_pipeline_team(slug: str) -> list:
    text = htmllib.unescape(get_text(f"https://www.mlb.com/milb/prospects/{slug}"))
    pairs = re.findall(
        r'"__typename":"RankedPlayerEntity","rank":(\d+).*?"Person:(\d+)"',
        text,
    )
    seen = set()
    out = []
    for rank, pid in pairs:
        pid = int(pid)
        if pid in seen:
            continue
        seen.add(pid)
        out.append({"rank": int(rank), "mlb_id": pid})
        if len(out) >= 30:
            break
    return out


def fetch_pipeline_for_team(team: dict) -> list:
    slugs = []
    for s in [TEAM_SLUGS.get(team.get("abbr") or ""), team.get("slug"), *(SLUG_FALLBACKS.get(team.get("abbr") or "") or [])]:
        if s and s not in slugs:
            slugs.append(s)
    for slug in slugs:
        try:
            rows = fetch_pipeline_team(slug)
        except Exception:
            rows = []
        if rows:
            return rows
    return []


def fetch_free_agents(season=2026) -> list:
    data = get_json(f"https://statsapi.mlb.com/api/v1/people/freeAgents?season={season}")
    out = []
    for row in data.get("freeAgents") or []:
        player = row.get("player") or {}
        pid = player.get("id")
        if not pid:
            continue
        new = row.get("newTeam") or {}
        orig = row.get("originalTeam") or {}
        out.append({
            "mlb_id": int(pid),
            "name": player.get("fullName") or "",
            "notes": row.get("notes") or "",
            "signed": bool(new.get("id")),
            "orig_team_id": orig.get("id"),
            "new_team_id": new.get("id"),
        })
    return out


def fetch_fielding(season=2026) -> list:
    data = get_json(
        "https://statsapi.mlb.com/api/v1/stats"
        f"?stats=season&group=fielding&season={season}&playerPool=all&limit=2500&sportId=1"
    )
    rows = []
    for split in (data.get("stats") or [{}])[0].get("splits") or []:
        pid = (split.get("player") or {}).get("id")
        pos = ((split.get("position") or {}).get("abbreviation")) or ""
        team = ((split.get("team") or {}).get("abbreviation")) or ""
        st = split.get("stat") or {}
        if not pid or not pos:
            continue
        rows.append({
            "mlb_id": int(pid),
            "pos": pos,
            "team": TEAM_FIX.get(team, team),
            "g": int(num(st.get("gamesPlayed"))),
        })
    return rows


def fetch_lineup_date(day: str) -> dict:
    data = get_json(
        f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={day}&hydrate=lineups,team"
    )
    by_team = {}
    for day_block in data.get("dates") or []:
        for g in day_block.get("games") or []:
            lu = g.get("lineups") or {}
            teams = g.get("teams") or {}
            mapping = (("homePlayers", "home"), ("awayPlayers", "away"))
            for key, side in mapping:
                players = lu.get(key) or []
                team = ((teams.get(side) or {}).get("team") or {})
                abbr = TEAM_FIX.get(team.get("abbreviation") or "", team.get("abbreviation") or "")
                if not abbr or not players:
                    continue
                order = []
                for p in players[:9]:
                    pid = p.get("id")
                    if pid:
                        order.append({
                            "mlb_id": int(pid),
                            "name": p.get("fullName") or "",
                            "pos": ((p.get("primaryPosition") or {}).get("abbreviation")) or "",
                        })
                if len(order) >= 8:
                    by_team[abbr] = order
    return by_team


def fetch_rosters(teams, season=2026):
    out = {}
    for t in teams:
        try:
            data = get_json(
                f"https://statsapi.mlb.com/api/v1/teams/{t['id']}/roster"
                f"?rosterType=fullSeason&season={season}"
            )
        except Exception:
            continue
        ids = []
        for row in data.get("roster") or []:
            pid = (row.get("person") or {}).get("id")
            if pid:
                ids.append(int(pid))
        out[t["abbr"]] = ids
        time.sleep(0.08)
    return out


def _upgrade_cache(cache: dict) -> dict:
    """Fill gaps in an existing cache without a full refetch."""
    changed = False
    n_ari = sum(1 for p in cache.get("prospects") or [] if p.get("team") in ("ARI", "AZ"))
    if n_ari < 20:
        rows = fetch_pipeline_team("dbacks")
        need = [row["mlb_id"] for row in rows]
        for row in rows:
            cache.setdefault("prospects", []).append({
                "team": "ARI",
                "team_name": "Arizona Diamondbacks",
                "rank": row["rank"],
                "mlb_id": row["mlb_id"],
            })
        if need:
            extra = fetch_people_batch(need)
            cache.setdefault("people", {}).update({str(k): v for k, v in extra.items()})
        changed = True
        print("  pipeline ARI", len(rows), "(upgrade)")
    if not cache.get("free_agents"):
        cache["free_agents"] = fetch_free_agents()
        changed = True
        print("  free agents", len(cache["free_agents"]), "(upgrade)")
    if changed:
        save_cache(cache)
    return cache


def fetch_all(force: bool = False) -> dict:
    cache = load_cache()
    if cache.get("career") and cache.get("prospects") and cache.get("seasons") and not force:
        return _upgrade_cache(cache)
    print("fetching MLB Stats API + Pipeline top 30s")
    teams = mlb_teams()
    career = {}
    for group in ("hitting", "pitching"):
        chunk = fetch_career_group(group)
        for pid, rec in chunk.items():
            cur = career.setdefault(str(pid), {"ab": 0, "ip": 0.0, "name": rec.get("name") or ""})
            if rec.get("name"):
                cur["name"] = rec["name"]
            if group == "hitting":
                cur["ab"] = rec["ab"]
            else:
                cur["ip"] = rec["ip"]
        print("  career", group, len(chunk))
    seasons = {}
    for year in SEASONS:
        seasons[str(year)] = {
            "hit": {str(k): v for k, v in fetch_season_group("hitting", year).items()},
            "pit": {str(k): v for k, v in fetch_season_group("pitching", year).items()},
        }
        print("  season", year, "hit", len(seasons[str(year)]["hit"]), "pit", len(seasons[str(year)]["pit"]))
    prospects = []
    for t in teams:
        rows = fetch_pipeline_for_team(t)
        for row in rows:
            prospects.append({
                "team": t["abbr"],
                "team_name": t["name"],
                "rank": row["rank"],
                "mlb_id": row["mlb_id"],
            })
        print("  pipeline", t["abbr"], len(rows))
        time.sleep(0.2)
    ids = {int(p["mlb_id"]) for p in prospects}
    ids.update(int(k) for k in career)
    for year in SEASONS:
        ids.update(int(k) for k in seasons[str(year)]["hit"])
        ids.update(int(k) for k in seasons[str(year)]["pit"])
    people_src = get_json("https://statsapi.mlb.com/api/v1/sports/1/players?season=2026")
    mlb_ids = []
    for p in people_src.get("people") or []:
        pid = p.get("id")
        if pid:
            mlb_ids.append(int(pid))
            ids.add(int(pid))
    people = fetch_people_batch(sorted(ids))
    fielding = fetch_fielding(2026)
    print("  fielding", len(fielding), "people", len(people))
    dates = [
        "2026-04-15", "2026-05-15", "2026-06-15", "2026-07-04",
        "2026-07-20", "2026-08-15", "2026-09-01", "2026-09-15",
    ]
    lineups = {}
    for day in dates:
        try:
            lineups[day] = fetch_lineup_date(day)
            print("  lineups", day, len(lineups[day]))
        except Exception as exc:
            print("  lineups skip", day, exc)
        time.sleep(0.15)
    rosters = fetch_rosters(teams, 2026)
    free_agents = fetch_free_agents(2026)
    print("  free agents", len(free_agents))
    doc = {
        "fetched": date.today().isoformat(),
        "teams": teams,
        "career": {str(k): v for k, v in career.items()},
        "seasons": seasons,
        "prospects": prospects,
        "people": {str(k): v for k, v in people.items()},
        "mlb_ids": mlb_ids,
        "fielding": fielding,
        "lineups": lineups,
        "rosters": rosters,
        "free_agents": free_agents,
    }
    save_cache(doc)
    print("cached", CACHE)
    return doc


def media_ids() -> dict:
    path = ROOT / "data" / "bb-media.json"
    out = {}
    if not path.exists():
        return out
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError:
        return out
    for key, rec in raw.items():
        pid = rec.get("mlb_id")
        if pid:
            out[key] = int(pid)
            name = rec.get("full_name") or rec.get("name") or ""
            if name:
                out[bb_norm(name)] = int(pid)
    return out


def index_people(cache: dict) -> dict:
    by_key = {}
    for pid, rec in (cache.get("people") or {}).items():
        name = rec.get("name") or ""
        if not name:
            continue
        by_key[bb_norm(name)] = {**rec, "mlb_id": int(pid)}
    for key, pid in media_ids().items():
        if key not in by_key and str(pid) in (cache.get("people") or {}):
            by_key[key] = {**(cache["people"][str(pid)]), "mlb_id": int(pid)}
        elif key not in by_key:
            by_key[key] = {"mlb_id": int(pid), "name": key}
    return by_key


def career_for(pid, cache) -> tuple[int, float]:
    rec = (cache.get("career") or {}).get(str(pid)) or {}
    return int(rec.get("ab") or 0), float(rec.get("ip") or 0)


def hit_score(st: dict) -> float:
    if not st:
        return 0.0
    return (
        4 * (st.get("hr") or 0)
        + (st.get("r") or 0)
        + (st.get("rbi") or 0)
        + 2 * (st.get("sb") or 0)
        + (st.get("obp") or 0) * (st.get("ab") or 0)
    )


def pit_score(st: dict) -> float:
    if not st:
        return 0.0
    return (st.get("ip") or 0) + 0.5 * ((st.get("so") or 0) - (st.get("bb") or 0)) - (st.get("er") or 0)


def model_score(pid, cache) -> float:
    total = 0.0
    for year, w in WEIGHTS.items():
        block = (cache.get("seasons") or {}).get(str(year)) or {}
        hit = (block.get("hit") or {}).get(str(pid)) or {}
        pit = (block.get("pit") or {}).get(str(pid)) or {}
        total += w * max(hit_score(hit), pit_score(pit) * 0.85)
    return total


def season_age(birth: str, season: int = 2027):
    if not birth:
        return ""
    try:
        dt = datetime.strptime(birth[:10], "%Y-%m-%d").date()
    except ValueError:
        return ""
    asof = date(season, 6, 30)
    years = asof.year - dt.year - ((asof.month, asof.day) < (dt.month, dt.day))
    return years


def marcel_hit(pid, cache, age) -> dict:
    """3-year 5/4/3 Marcel-style rates, regressed to 2026 league mean, age-adjusted.

    Weighted totals are scaled back to a single season of playing time so AB/HR/RBI/SB
    are 2027 projections, not three-year sums.
    """
    seasons = cache.get("seasons") or {}
    weighted = Counter()
    w_tot = 0.0
    for year, w in WEIGHTS.items():
        st = ((seasons.get(str(year)) or {}).get("hit") or {}).get(str(pid)) or {}
        ab = st.get("ab") or 0
        if ab <= 0:
            continue
        w_tot += w
        for k in ("ab", "h", "bb", "hbp", "sf", "hr", "rbi", "sb", "r"):
            weighted[k] += w * (st.get(k) or 0)
    if w_tot <= 0 or weighted["ab"] < 40:
        return {}
    lg = _league_hit(cache)
    reg_ab = 200.0
    rate_ab = weighted["ab"] + reg_ab
    def rate(key, lg_key):
        return (weighted[key] + reg_ab * (lg.get(lg_key) or 0)) / rate_ab
    age_n = age if isinstance(age, int) else 27
    factor = 1 + 0.006 * (29 - age_n)
    factor = max(0.82, min(1.12, factor))
    ab = (weighted["ab"] / w_tot) * factor
    if ab <= 0:
        return {}
    h = rate("h", "avg") * ab
    bb = rate("bb", "bb_ab") * ab
    hbp = rate("hbp", "hbp_ab") * ab
    sf = rate("sf", "sf_ab") * ab
    obp_den = ab + bb + hbp + sf
    obp = (h + bb + hbp) / obp_den if obp_den else 0
    return {
        "ab": int(round(ab)),
        "obp": round(obp, 3),
        "hr": int(round(rate("hr", "hr_ab") * ab)),
        "rbi": int(round(rate("rbi", "rbi_ab") * ab)),
        "sb": int(round(rate("sb", "sb_ab") * ab)),
    }


def _league_hit(cache) -> dict:
    hit = ((cache.get("seasons") or {}).get("2026") or {}).get("hit") or {}
    tot = Counter()
    for st in hit.values():
        for k in ("ab", "h", "bb", "hbp", "sf", "hr", "rbi", "sb", "r"):
            tot[k] += st.get(k) or 0
    ab = tot["ab"] or 1
    return {
        "avg": tot["h"] / ab,
        "hr_ab": tot["hr"] / ab,
        "rbi_ab": tot["rbi"] / ab,
        "sb_ab": tot["sb"] / ab,
        "r_ab": tot["r"] / ab,
        "bb_ab": tot["bb"] / ab,
        "hbp_ab": tot["hbp"] / ab,
        "sf_ab": tot["sf"] / ab,
    }


def player_team_map(cache: dict) -> dict:
    teams = cache.get("teams") or []
    by_id = {t["id"]: t["abbr"] for t in teams if t.get("id")}
    by_name = {t["name"]: t["abbr"] for t in teams}
    by_name.update({t.get("team_name"): t["abbr"] for t in teams if t.get("team_name")})
    out = {}
    for abbr, ids in (cache.get("rosters") or {}).items():
        for pid in ids:
            out[int(pid)] = abbr
    for p in cache.get("prospects") or []:
        pid = int(p["mlb_id"])
        if p.get("team"):
            out[pid] = p["team"]
    for _day, games in (cache.get("lineups") or {}).items():
        for abbr, order in games.items():
            for p in order:
                out.setdefault(int(p["mlb_id"]), abbr)
    for fa in cache.get("free_agents") or []:
        orig = fa.get("orig_team_id")
        pid = fa.get("mlb_id")
        if pid and orig in by_id:
            out.setdefault(int(pid), by_id[orig])
    for pid, rec in (cache.get("people") or {}).items():
        if rec.get("team"):
            out.setdefault(int(pid), rec["team"])
        elif rec.get("team_name") in by_name:
            out.setdefault(int(pid), by_name[rec["team_name"]])
    return out


def attach_career(row: dict, cache: dict, by_key: dict, teams_map: dict | None = None) -> dict:
    rec = dict(row)
    key = rec.get("key") or bb_norm(rec.get("name") or "")
    rec["key"] = key
    person = by_key.get(key)
    if person:
        rec["mlb_id"] = person.get("mlb_id")
        rec["birth"] = rec.get("birth") or person.get("birth") or ""
        if not rec.get("team"):
            rec["team"] = person.get("team") or ""
        if not rec.get("pos"):
            rec["pos"] = person.get("pos") or rec.get("pos") or ""
        if not rec.get("age"):
            rec["age"] = person.get("age") or ""
    pid = rec.get("mlb_id")
    if pid:
        ab, ip = career_for(pid, cache)
        rec["ab"] = ab
        rec["ip"] = ip
        rec["matched"] = True
        if teams_map and (not rec.get("team")):
            rec["team"] = teams_map.get(int(pid) or 0) or ""
    else:
        rec["ab"] = rec.get("ab")
        rec["ip"] = rec.get("ip")
        rec["matched"] = False
    return rec


def rerank(rows):
    out = [dict(r) for r in rows]
    out.sort(key=lambda r: (
        r.get("_sort") if r.get("_sort") is not None else (r.get("avg") or 9999),
        -(r.get("n") or 0),
        r.get("name") or "",
    ))
    for i, r in enumerate(out, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return out


def build_universe(dynasty_rows, cache: dict) -> dict:
    by_key = index_people(cache)
    teams_map = player_team_map(cache)
    listed_farm = load_listed_farm(limit=400, max_games=10_000)
    farm_src = {r["key"]: r for r in listed_farm}

    pipeline = []
    people = cache.get("people") or {}
    career = cache.get("career") or {}
    for p in cache.get("prospects") or []:
        pid = p["mlb_id"]
        person = people.get(str(pid)) or {}
        name = person.get("name") or (career.get(str(pid)) or {}).get("name") or ""
        if not name:
            continue
        key = bb_norm(name)
        rec = {
            "key": key,
            "name": name,
            "pos": person.get("pos") or "",
            "team": p.get("team") or person.get("team") or teams_map.get(pid) or "",
            "age": person.get("age") or "",
            "birth": person.get("birth") or "",
            "mlb_id": pid,
            "eta": "",
            "level": "MiLB",
            "path": f"MLB Pipeline {p.get('team')} #{p.get('rank')}.",
            "ranks": {"MLB Pipeline": int(p.get("rank") or 0) + 1000},  # team list, not overall
            "pipeline_team_rank": p.get("rank"),
            "n": 1,
            "avg": 200 + int(p.get("rank") or 30),
        }
        if key in farm_src:
            src = farm_src[key]
            rec["ranks"] = dict(src.get("ranks") or {})
            rec["n"] = src.get("n") or len(rec["ranks"])
            rec["avg"] = src.get("avg") or rec["avg"]
            rec["eta"] = src.get("eta") or ""
            rec["level"] = src.get("level") or rec["level"]
            rec["path"] = src.get("path") or rec["path"]
            rec["pos"] = src.get("pos") or rec["pos"]
        pipeline.append(rec)

    attached_dynasty = [attach_career(r, cache, by_key, teams_map) for r in dynasty_rows]
    attached_farm_src = [attach_career(r, cache, by_key, teams_map) for r in listed_farm]
    attached_pipeline = [attach_career(r, cache, by_key, teams_map) for r in pipeline]

    unmatched = []
    majors = []
    farm = []
    seen = set()

    def place(rec, allow_unmatched_as_farm: bool):
        key = rec["key"]
        if key in seen:
            return
        pid = rec.get("mlb_id")
        if not pid:
            if allow_unmatched_as_farm:
                rec["ab"] = 0
                rec["ip"] = 0.0
                rec["matched"] = False
                rec["unmatched_farm"] = True
                farm.append(rec)
                seen.add(key)
            else:
                rec["_unmatched_pending"] = True
            return
        ab = int(rec.get("ab") or 0)
        ip = float(rec.get("ip") or 0)
        rec["ab"] = ab
        rec["ip"] = ip
        seen.add(key)
        if is_farm_eligible(ab, ip):
            farm.append(rec)
        else:
            majors.append(rec)

    for rec in attached_dynasty:
        place(rec, allow_unmatched_as_farm=False)
    for rec in attached_farm_src + attached_pipeline:
        place(rec, allow_unmatched_as_farm=True)

    # BK model fill: other 2026 MLB players who qualify for majors.
    already = {r["key"] for r in majors} | {r["key"] for r in farm} | {bb_norm(u["name"]) for u in unmatched if u.get("name")}
    fills = []
    for pid in cache.get("mlb_ids") or []:
        person = (cache.get("people") or {}).get(str(pid)) or {}
        name = person.get("name") or ""
        if not name:
            continue
        key = bb_norm(name)
        if key in already:
            continue
        ab, ip = career_for(pid, cache)
        if not is_majors_eligible(ab, ip):
            continue
        score = model_score(pid, cache)
        fills.append({
            "key": key,
            "name": name,
            "pos": person.get("pos") or "",
            "team": person.get("team") or teams_map.get(int(pid)) or "",
            "age": person.get("age") or "",
            "birth": person.get("birth") or "",
            "mlb_id": int(pid),
            "ab": ab,
            "ip": ip,
            "matched": True,
            "bk_model": True,
            "model_score": score,
            "ranks": {},
            "n": 0,
            "avg": 900,
            "_sort": 5000 - score,
        })
    fills.sort(key=lambda r: -r["model_score"])
    majors.extend(fills)

    for rec in farm:
        rec["_sort"] = rec.get("avg") or 999
        rec["group"] = "SP" if str(rec.get("pos") or "").upper() in {"RHP", "LHP", "SP", "P", "RP"} else "HIT"
    for rec in majors:
        if rec.get("bk_model"):
            rec["_sort"] = rec.get("_sort") or 5000
        else:
            rec["_sort"] = rec.get("avg") or 999
        pos = str(rec.get("pos") or "").upper()
        if "SP" in pos and ("DH" in pos or pos == "TWP"):
            rec["group"] = "UT"
        elif "RP" in pos:
            rec["group"] = "RP"
        elif pos in {"RHP", "LHP", "SP", "P"} or "SP" in pos:
            rec["group"] = "SP"
        else:
            rec["group"] = "HIT"

    majors = rerank(majors)
    farm = rerank(farm)

    dynasty = rerank(
        [{**r, "_sort": (0 if not r.get("bk_model") else 1, r.get("avg") if not r.get("bk_model") else r.get("_sort") or 5000)}
         for r in majors + farm]
    )

    placed = {r["key"] for r in farm} | {r["key"] for r in majors}
    seen_u = set()
    unmatched = []
    for rec in attached_dynasty:
        key = rec["key"]
        if rec.get("mlb_id") or key in placed or key in seen_u:
            continue
        seen_u.add(key)
        unmatched.append({
            "name": rec.get("name"),
            "pos": rec.get("pos"),
            "team": rec.get("team"),
            "reason": "no MLB ID",
            "published_on": None,
        })
    for rec in farm:
        if not rec.get("unmatched_farm"):
            continue
        key = rec["key"]
        if key in seen_u:
            continue
        seen_u.add(key)
        unmatched.append({
            "name": rec.get("name"),
            "pos": rec.get("pos"),
            "team": rec.get("team"),
            "reason": "no MLB ID; kept on Deep Farm at 0 AB / 0 IP",
            "published_on": "deep-farm",
        })

    UNMATCHED.write_text(json.dumps({
        "updated": date.today().isoformat(),
        "count": len(unmatched),
        "players": unmatched,
        "unpublished": sum(1 for u in unmatched if not u.get("published_on")),
    }, indent=2))

    shortfalls = []
    if len(majors) < 650:
        shortfalls.append(f"Majors {len(majors)} (target 650). Valid names only; did not pad.")
    if len(farm) < 500:
        shortfalls.append(f"Deep Farm {len(farm)} (target 500). Valid names only; did not pad.")
    if len(dynasty) < 600:
        shortfalls.append(f"Deep Dynasty {len(dynasty)} (target 600).")

    return {
        "majors": majors,
        "farm": farm,
        "dynasty": dynasty,
        "unmatched": unmatched,
        "shortfalls": shortfalls,
        "cache": cache,
        "by_key": by_key,
    }


def fa_ids(cache: dict) -> set:
    return {int(r["mlb_id"]) for r in cache.get("free_agents") or [] if not r.get("signed")}


def _player_positions(cache: dict) -> dict:
    field = defaultdict(lambda: Counter())
    for row in cache.get("fielding") or []:
        pos = row.get("pos") or ""
        if pos in {"P", "TWP"}:
            continue
        field[row["mlb_id"]][pos] += row.get("g") or 0
    return field


def projected_nines(cache: dict) -> dict:
    """Most likely 2027 nine: unique 2026 batting-order regulars, unique positions."""
    slot_counts = defaultdict(lambda: defaultdict(Counter))
    pos_seen = defaultdict(lambda: defaultdict(Counter))
    appear = defaultdict(Counter)
    name_of = {}
    for _day, teams in (cache.get("lineups") or {}).items():
        for abbr, order in teams.items():
            for i, p in enumerate(order[:9]):
                pid = p["mlb_id"]
                slot_counts[abbr][i][pid] += 1
                appear[abbr][pid] += 1
                name_of[pid] = p.get("name") or name_of.get(pid)
                pos = p.get("pos") or ""
                if pos:
                    pos_seen[abbr][pid][pos] += 1
    field = _player_positions(cache)
    people = cache.get("people") or {}
    roster = cache.get("rosters") or {}
    hit = ((cache.get("seasons") or {}).get("2026") or {}).get("hit") or {}
    out = {}
    for abbr, slots in slot_counts.items():
        ranked_players = appear[abbr].most_common()
        top = [pid for pid, _n in ranked_players[:9]]
        used = set(top)
        nine = [None] * 9
        alts = [None] * 9
        taken_slots = set()
        for pid in top:
            best_slot, best_n = None, -1
            for i in range(9):
                if i in taken_slots:
                    continue
                c = slots[i][pid]
                if c > best_n:
                    best_n, best_slot = c, i
            if best_slot is None:
                for i in range(9):
                    if i not in taken_slots:
                        best_slot = i
                        break
            if best_slot is None:
                continue
            taken_slots.add(best_slot)
            nine[best_slot] = (pid, appear[abbr][pid])
        for i in range(9):
            if nine[i]:
                continue
            pid = None
            for cand, _n in ranked_players:
                if cand not in used:
                    pid = cand
                    break
            if pid is None:
                pool = []
                for rid in roster.get(abbr) or []:
                    if rid in used:
                        continue
                    person = people.get(str(rid)) or {}
                    pos = (person.get("pos") or "").upper()
                    if pos in {"RHP", "LHP", "P", "SP", "RP"}:
                        continue
                    st = hit.get(str(rid)) or {}
                    pool.append((int(st.get("pa") or st.get("ab") or 0), rid))
                pool.sort(reverse=True)
                pid = pool[0][1] if pool else None
            if pid is None:
                continue
            used.add(pid)
            nine[i] = (pid, appear[abbr].get(pid) or 0)
        for i, pick in enumerate(nine):
            if not pick:
                continue
            starter_n = pick[1]
            for pid, n in slots[i].most_common():
                if pid in used:
                    continue
                if n >= 3 and n >= max(3, int(starter_n * 0.5)):
                    alts[i] = ("platoon / playing-time split in 2026 lineups", (pid, n))
                    break

        pids = [pick[0] for pick in nine if pick]
        pos_of = {}
        taken = set()
        def score(pid, pos):
            return pos_seen[abbr][pid][pos] * 10 + field[pid][pos]
        for pos in POS_ORDER:
            if pos == "DH":
                continue
            best, best_n = None, -1
            for pid in pids:
                if pid in taken:
                    continue
                n = score(pid, pos)
                if n > best_n:
                    best, best_n = pid, n
            if best is not None and best_n > 0:
                pos_of[best] = pos
                taken.add(best)
        leftover = [pid for pid in pids if pid not in taken]
        need = [p for p in POS_ORDER if p not in pos_of.values()]
        for pid in leftover:
            best, best_n = None, -1
            for pos in need:
                n = score(pid, pos)
                if pos == "DH":
                    n += 1
                if n > best_n:
                    best, best_n = pos, n
            pos_of[pid] = best or "DH"
            if best in need:
                need.remove(best)
        rows = []
        for i, pick in enumerate(nine):
            if not pick:
                continue
            pid, starts = pick
            person = people.get(str(pid)) or {}
            rec = {
                "slot": i + 1,
                "mlb_id": pid,
                "name": name_of.get(pid) or person.get("name") or "",
                "pos": pos_of.get(pid) or "DH",
                "team": abbr,
                "starts": starts,
            }
            alt_info = alts[i]
            if alt_info:
                reason, (apid, ast) = alt_info
                if apid in used:
                    alt_info = None
                else:
                    ap = people.get(str(apid)) or {}
                    rec["alt"] = {
                        "mlb_id": apid,
                        "name": name_of.get(apid) or ap.get("name") or "",
                        "starts": ast,
                        "reason": reason,
                    }
            rows.append(rec)
        _repair_glove(abbr, rows, used, field, pos_seen, people, roster, hit, name_of)
        out[abbr] = rows
    return out


def _repair_glove(abbr, rows, used, field, pos_seen, people, roster, hit, name_of):
    """If a required infield/catcher has zero games there, swap in a roster glove."""
    def score(pid, pos):
        return pos_seen[abbr][pid][pos] * 10 + field[pid][pos]
    for rec in rows:
        pos = rec.get("pos") or ""
        if pos not in {"C", "1B", "2B", "3B", "SS"}:
            continue
        if score(rec["mlb_id"], pos) > 0:
            continue
        best = None
        for rid in roster.get(abbr) or []:
            if rid in used:
                continue
            n = score(rid, pos)
            person = people.get(str(rid)) or {}
            ppos = (person.get("pos") or "").upper()
            if n <= 0 and ppos != pos:
                continue
            pa = int((hit.get(str(rid)) or {}).get("pa") or 0)
            cand = (n, pa, rid)
            if not best or cand > best:
                best = cand
        if not best or (best[0] <= 0 and best[1] <= 0):
            continue
        rid = best[2]
        old_name, old_id = rec["name"], rec["mlb_id"]
        person = people.get(str(rid)) or {}
        rec["mlb_id"] = rid
        rec["name"] = name_of.get(rid) or person.get("name") or ""
        rec["starts"] = 0
        if not rec.get("alt"):
            rec["alt"] = {
                "name": old_name,
                "mlb_id": old_id,
                "reason": "playing-time split in 2026 lineups",
            }
        used.discard(old_id)
        used.add(rid)


def _add_prospect_alts(abbr, nine, cache):
    people = cache.get("people") or {}
    used = {r["mlb_id"] for r in nine}
    alts_used = {(r.get("alt") or {}).get("mlb_id") for r in nine}
    prospects = [p for p in cache.get("prospects") or [] if p.get("team") == abbr]
    prospects.sort(key=lambda p: int(p.get("rank") or 99))
    added = 0
    for p in prospects:
        if added >= 2:
            break
        pid = p["mlb_id"]
        if pid in used or pid in alts_used:
            continue
        person = people.get(str(pid)) or {}
        pos = (person.get("pos") or "").upper()
        if pos in {"RHP", "LHP", "P", "SP", "RP"} or pos.endswith("HP"):
            continue
        ab, ip = career_for(pid, cache)
        if not is_farm_eligible(ab, ip):
            continue
        if int(p.get("rank") or 99) > 4:
            break
        target = None
        for rec in nine:
            if rec.get("alt"):
                continue
            rec_pos = (rec.get("pos") or "").upper()
            if rec_pos == pos or (pos in {"LF", "CF", "RF", "OF"} and rec_pos in {"LF", "CF", "RF", "DH", "OF"}):
                target = rec
                break
        if not target:
            continue
        target["alt"] = {
            "mlb_id": pid,
            "name": person.get("name") or "",
            "reason": "prospect arrival in 2027",
        }
        alts_used.add(pid)
        added += 1


def build_lineups(dynasty_rows, cache: dict) -> list:
    value_map = {r["key"]: r.get("value") for r in dynasty_rows}
    rank_map = {r["key"]: r.get("bk") for r in dynasty_rows}
    by_team_lineups = projected_nines(cache)
    unsigned_fa = fa_ids(cache)
    teams = cache.get("teams") or mlb_teams()
    blocks = []
    for t in sorted(teams, key=lambda x: x["name"]):
        abbr = t["abbr"]
        rows = list(by_team_lineups.get(abbr) or [])
        _add_prospect_alts(abbr, rows, cache)
        hitters = []
        for rec in rows:
            pid = rec["mlb_id"]
            person = (cache.get("people") or {}).get(str(pid)) or {}
            name = rec.get("name") or person.get("name") or ""
            key = bb_norm(name)
            age = season_age(person.get("birth") or "", 2027)
            if age == "":
                try:
                    age = int(person.get("age") or 0) + 1 or ""
                except (TypeError, ValueError):
                    age = ""
            proj = marcel_hit(pid, cache, age if isinstance(age, int) else 27)
            fa = pid in unsigned_fa
            alt = rec.get("alt")
            if fa and not alt:
                alt = {"name": "", "reason": "free agent"}
            elif fa and alt and "free agent" not in (alt.get("reason") or "").lower():
                alt = dict(alt)
                alt["reason"] = "free agent; " + (alt.get("reason") or "replacement candidate")
            if alt and not alt.get("name") and alt.get("reason") == "free agent":
                alt = None  # FA badge on the starter is enough when no replacement is named
            hitters.append({
                "slot": rec["slot"],
                "name": name,
                "key": key,
                "pos": rec.get("pos") or person.get("pos") or "",
                "age": age,
                "value": value_map.get(key),
                "bk": rank_map.get(key),
                "proj": proj,
                "fa": fa,
                "alt": alt,
                "mlb_id": pid,
            })
        blocks.append({
            "abbr": abbr,
            "name": t["name"],
            "hitters": hitters,
        })
    return blocks


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    doc = fetch_all(force=args.force or args.fetch or not CACHE.exists())
    print("teams", len(doc.get("teams") or []), "career", len(doc.get("career") or []),
          "prospects", len(doc.get("prospects") or []), "people", len(doc.get("people") or []))
