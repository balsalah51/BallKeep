"""PitchKeep ranking sources — August 21, 2026.

The Pitch is a Sleeper BPL 2025 points board. Default Sleeper soccer
scoring (support.sleeper.com/en/articles/9702800-scoring-system) applied
to 2025/26 Premier League counting stats from the official FPL dump.

The Premier is the third PitchKeep list: 50% Sleeper BPL 2025 rank,
50% consensus of every other board (official FPL metrics plus 25
published 2026/27 pro lists). Unranked names are skipped — never 999.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fold(s: str) -> str:
    n = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in n if not unicodedata.combining(c))


def pl_norm(name: str) -> str:
    n = fold(name or "").lower()
    n = n.replace(".", " ").replace("'", "").replace("’", "").replace("-", " ")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "b fernandes": "bruno fernandes",
        "bruno borges fernandes": "bruno fernandes",
        "bruno": "bruno fernandes",
        "erling haaland": "erling haaland",
        "haaland": "erling haaland",
        "gabriel dos santos magalhaes": "gabriel magalhaes",
        "gabriel magalhaes": "gabriel magalhaes",
        "gabriel": "gabriel magalhaes",
        "joao pedro junqueira de jesus": "joao pedro",
        "joao pedro": "joao pedro",
        "virgil van dijk": "virgil van dijk",
        "virgil": "virgil van dijk",
        "vvd": "virgil van dijk",
        "bukayo saka": "bukayo saka",
        "cole palmer": "cole palmer",
        "bryan mbeumo": "bryan mbeumo",
        "dominik szoboszlai": "dominik szoboszlai",
        "szobo": "dominik szoboszlai",
        "pascal grosz": "pascal gross",
        "pascal gross": "pascal gross",
        "groß": "pascal gross",
        "antonin kinsky": "antonin kinsky",
        "kinsky": "antonin kinsky",
        "david raya martin": "david raya",
        "david raya": "david raya",
        "raya": "david raya",
        "pedro porro sauceda": "pedro porro",
        "pedro porro": "pedro porro",
        "florian wirtz": "florian wirtz",
        "alexander isak": "alexander isak",
        "isak": "alexander isak",
        "phil foden": "phil foden",
        "eberechi eze": "eberechi eze",
        "antoine semenyo": "antoine semenyo",
        "riccardo calafiori": "riccardo calafiori",
        "declan rice": "declan rice",
        "rice": "declan rice",
        "morgan gibbs white": "morgan gibbs-white",
        "morgan gibbs-white": "morgan gibbs-white",
        "ollie watkins": "ollie watkins",
        "dominic calvert lewin": "dominic calvert-lewin",
        "dominic calvert-lewin": "dominic calvert-lewin",
        "ilimane ndiaye": "iliman ndiaye",
        "iliman ndiaye": "iliman ndiaye",
        "brian brobbey": "brian brobbey",
        "martin zubimendi ibanez": "martin zubimendi",
        "martin zubimendi": "martin zubimendi",
        "william saliba": "william saliba",
        "marc guehi": "marc guehi",
        "igorthiago nascimento rodrigues": "igor thiago",
        "odegaard": "ødegaard",
        "martin odegaard": "ødegaard",
        "martin ødegaard": "ødegaard",
        "bruno g": "bruno g",
        "bruno guimaraes": "bruno g",
        "bruno guimaraes rodriguez moura": "bruno g",
        "alisson": "a becker",
        "alisson becker": "a becker",
        "a becker": "a becker",
        "rodri": "rodrigo",
        "rodrigo rodri": "rodrigo",
        "n jackson": "n jackson",
        "nicolas jackson": "n jackson",
        "alexis mac allister": "mac allister",
        "mac allister": "mac allister",
        "moises caicedo": "caicedo",
        "moises caicedo corozo": "caicedo",
        "caicedo": "caicedo",
        "matheus nunes": "matheus n",
        "matheus n": "matheus n",
        "david raya martin": "david raya",
        "marcos senesi baron": "senesi",
        "marcos senesi": "senesi",
        "micky van de ven": "van de ven",
        "van de ven": "van de ven",
        "emiliano martinez": "martinez",
        "emiliano martinez romero": "martinez",
        "estevao": "estevao",
        "estevao goncalves": "estevao",
        "florentino": "florentino",
        "evanilson": "evanilson",
        "rayan vitor": "rayan",
        "jeremy doku": "jeremy doku",
        "jeremie doku": "jeremy doku",
        "ezri konsa": "konsa",
        "ezri konsa ngoyo": "konsa",
        "daniel munoz": "munoz",
        "daniel munoz mejia": "munoz",
        "ben white": "white",
        "benjamin white": "white",
        "kaoru mitoma": "mitoma",
        "mitoma kaoru": "mitoma",
        "diego gomez": "gomez",
        "diego gomez amarilla": "gomez",
        "vitaliy mykolenko": "mykolenko",
        "vitalii mykolenko": "mykolenko",
        "emiliano buendia": "buendia",
        "emiliano buendia stati": "buendia",
        "djordje petrovic": "petrovic",
        "dorde petrovic": "petrovic",
        "oliver mcburnie": "mcburnie",
        "oli mcburnie": "mcburnie",
        "yeremy pino": "yeremy",
        "yeremy pino santos": "yeremy",
        "yehor yarmolyuk": "yarmoliuk",
        "yehor yarmoliuk": "yarmoliuk",
        "valentino livramento": "livramento",
        "tino livramento": "livramento",
        "florentino luis": "florentino",
        "christian norgaard": "nørgaard",
        "jorgen strand larsen": "strand larsen",
        "strand larsen": "strand larsen",
        "gabriel martinelli": "martinelli",
        "jamie gittens": "gittens",
        "jamie bynoe gittens": "gittens",
        "wataru endo": "endo",
        "endo wataru": "endo",
        "rodrigo muniz": "muniz",
        "ao tanaka": "tanaka",
        "tanaka ao": "tanaka",
        "mikel merino": "merino",
        "juanlu": "sanchez",
        "juanlu sanchez": "sanchez",
    }
    return aliases.get(n, n)


def bk_value(rank, mult=1.0):
    if not rank or rank <= 0:
        return 0
    return int(round(12000 * math.exp(-0.0165 * (rank - 1)) / (rank ** 0.18) * mult))


def display_name(e):
    first = (e.get("first_name") or "").strip()
    second = (e.get("second_name") or "").strip()
    web = (e.get("web_name") or "").strip()
    particles = {"van", "von", "de", "del", "di", "da", "dos", "la", "le", "bin", "al", "ter"}
    parts = [p for p in second.split() if p]
    given = first.split()[0] if first else ""
    last = parts[-1] if parts else web
    tokens = (first + " " + second).split()
    # Virgil van Dijk — keep the particle surname intact.
    if len(parts) == 2 and parts[0].lower() in particles:
        return f"{first} {second}".strip()
    # FPL already prints the public name: João Pedro, Pedro Porro.
    if web and " " in web:
        return web
    if web and "-" in web and given and given.lower() not in web.lower():
        return f"{given} {web}".strip()
    # B.Fernandes / G.Jesus
    if web and "." in web:
        return f"{given} {last}".strip()
    # Igor Thiago Nascimento Rodrigues → Igor Thiago
    if len(tokens) >= 4 and len(first.split()) >= 2:
        return first
    # Gabriel dos Santos Magalhães → Gabriel Magalhães
    if len(tokens) >= 4:
        return f"{given} {last}".strip()
    # Pedro Lomba Neto → Pedro Neto
    if len(tokens) == 3 and web and last and web.lower() == last.lower():
        return f"{given} {last}".strip()
    if web and given and last and web.lower() == last.lower():
        return f"{given} {web}".strip()
    return (f"{first} {second}".strip() or web)


POS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
PITCH_N = 400
FWD_N = 100
MID_N = 150
DEF_N = 120
GKP_N = 50


def sleeper_bpl_points(p) -> float:
    """Default Sleeper soccer scoring on 2025/26 counting stats.

    Goals/assists/CS/GA/cards/saves/PK from the published Sleeper table.
    Tackles map to tackles won (1). FPL clearances+blocks+interceptions
    are blended at 0.4 to stand in for clearances (0.25), blocks (1),
    and interceptions (1) without double-counting. Shots on target and
    key passes are not in the FPL dump, so they are omitted rather than
    invented.
    """
    pos = p.get("pos") or "MID"
    g = int(p.get("gls") or 0)
    a = int(p.get("ast") or 0)
    cs = int(p.get("cs") or 0)
    gc = int(p.get("gc") or 0)
    yc = int(p.get("yc") or 0)
    rc = int(p.get("rc") or 0)
    saves = int(p.get("saves") or 0)
    og = int(p.get("og") or 0)
    ps = int(p.get("pk_save") or 0)
    pm = int(p.get("pk_miss") or 0)
    tack = int(p.get("tackles") or 0)
    cbi = int(p.get("cbi") or 0)
    gp = 10 if pos in ("DEF", "GKP") else 9
    ap = 7 if pos in ("DEF", "GKP") else 6
    csp = {"FWD": 0, "MID": 1, "DEF": 6, "GKP": 8}.get(pos, 1)
    gap = -2 if pos in ("DEF", "GKP") else 0
    return round(
        g * gp
        + a * ap
        + cs * csp
        + saves * 2
        + ps * 8
        + yc * -2
        + rc * -7
        + og * -5
        + pm * -4
        + gc * gap
        + tack * 1
        + cbi * 0.4,
        1,
    )


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _age(birth):
    if not birth:
        return ""
    try:
        y, m, d = [int(x) for x in str(birth)[:10].split("-")]
        today = date(2026, 8, 21)
        age = today.year - y - ((today.month, today.day) < (m, d))
        return age
    except Exception:
        return ""


def load_raw():
    return json.loads((ROOT / "data/pl-fpl.json").read_text())


def index_players(raw=None):
    raw = raw or load_raw()
    teams = {t["id"]: t for t in raw["teams"]}
    out = []
    seen = set()
    for e in raw["elements"]:
        full = display_name(e)
        legal = f"{e.get('first_name') or ''} {e.get('second_name') or ''}".strip()
        web = e.get("web_name") or full
        team = teams.get(e.get("team") or 0) or {}
        key = pl_norm(web) or pl_norm(full) or pl_norm(legal)
        if key in seen:
            key = f"{key} {pl_norm(team.get('short_name') or '')}".strip()
        seen.add(key)
        rec = {
            "key": key,
            "id": e.get("id"),
            "name": full or web,
            "full_name": legal or full or web,
            "web_name": web,
            "pos": POS.get(e.get("element_type"), ""),
            "team": team.get("short_name") or "",
            "team_name": team.get("name") or "",
            "age": _age(e.get("birth_date")),
            "birth": e.get("birth_date") or "",
            "price": round(_num(e.get("now_cost")) / 10.0, 1),
            "sel": _num(e.get("selected_by_percent")),
            "pts": int(_num(e.get("total_points"))),
            "minutes": int(_num(e.get("minutes"))),
            "gls": int(_num(e.get("goals_scored"))),
            "ast": int(_num(e.get("assists"))),
            "cs": int(_num(e.get("clean_sheets"))),
            "saves": int(_num(e.get("saves"))),
            "bonus": int(_num(e.get("bonus"))),
            "ict": _num(e.get("ict_index")),
            "xg": _num(e.get("expected_goals")),
            "xa": _num(e.get("expected_assists")),
            "xgi": _num(e.get("expected_goal_involvements")),
            "form": _num(e.get("form")),
            "ppg": _num(e.get("points_per_game")),
            "ep": _num(e.get("ep_next")),
            "photo": e.get("photo") or "",
            "code": e.get("code") or (str(e.get("photo") or "").replace(".jpg", "")),
            "news": e.get("news") or "",
            "status": e.get("status") or "a",
            "chance": e.get("chance_of_playing_this_round"),
            "pens": e.get("penalties_order"),
            "corners": e.get("corners_and_indirect_freekicks_order"),
            "dfk": e.get("direct_freekicks_order"),
            "starts": int(_num(e.get("starts"))),
            "number": e.get("squad_number") or "",
            "group": POS.get(e.get("element_type"), ""),
            "yc": int(_num(e.get("yellow_cards"))),
            "rc": int(_num(e.get("red_cards"))),
            "bps": int(_num(e.get("bps"))),
            "sel_rank": e.get("selected_rank"),
            "influence": _num(e.get("influence")),
            "creativity": _num(e.get("creativity")),
            "threat": _num(e.get("threat")),
            "gc": int(_num(e.get("goals_conceded"))),
            "og": int(_num(e.get("own_goals"))),
            "pk_save": int(_num(e.get("penalties_saved"))),
            "pk_miss": int(_num(e.get("penalties_missed"))),
            "tackles": int(_num(e.get("tackles"))),
            "cbi": int(_num(e.get("clearances_blocks_interceptions"))),
        }
        rec["sleeper_pts"] = sleeper_bpl_points(rec)
        out.append(rec)
    return out


def metric_map(players, getter, reverse=True, cap=None, min_minutes=0):
    scored = []
    for p in players:
        if min_minutes and p.get("minutes", 0) < min_minutes and getter(p) == p.get("pts"):
            pass
        val = getter(p)
        scored.append((val, p["key"]))
    scored.sort(key=lambda kv: kv[0], reverse=reverse)
    out = {}
    for i, (_v, k) in enumerate(scored, 1):
        if cap and i > cap:
            break
        out[k] = i
    return out


def named_map(players, names, cap=None):
    by_key = {p["key"]: p for p in players}
    by_web = {pl_norm(p["web_name"]): p for p in players}
    by_name = {pl_norm(p["name"]): p for p in players}
    by_full = {pl_norm(p["full_name"]): p for p in players}
    out = {}
    rank = 1
    for raw in names:
        k = pl_norm(raw)
        p = by_key.get(k) or by_web.get(k) or by_name.get(k) or by_full.get(k)
        if not p:
            continue
        if p["key"] in out:
            continue
        out[p["key"]] = rank
        rank += 1
        if cap and rank > cap:
            break
    return out


def load_expert_lists():
    path = ROOT / "data/pl-expert-lists.json"
    if not path.exists():
        return {}
    blob = json.loads(path.read_text())
    return blob.get("lists") or {}


def remap(keys, score_fn, cap=None):
    scored = [(score_fn(k, i), i, k) for i, k in enumerate(keys)]
    scored.sort()
    out = {k: i + 1 for i, (_s, _orig, k) in enumerate(scored)}
    if cap:
        out = {k: r for k, r in out.items() if r <= cap}
    return out


def order_from_map(m):
    return [k for k, _ in sorted(m.items(), key=lambda kv: kv[1])]


EXPERT_META = [
    ("RotoWire FPL 400", "https://www.rotowire.com/soccer/article/fantasy-premier-league-fpl-rankings-top-400-for-2026-27-season-124261", "Season-long official-game top 400, Aug 21."),
    ("RotoWire Fantrax / Sleeper 400", "https://www.rotowire.com/soccer/article/fantrax-sleeper-premier-league-rankings-top-400-for-the-202627-season-123920", "Draft-scoring Fantrax and Sleeper top 400, Aug 21."),
    ("RotoWire GW1", "https://www.rotowire.com/soccer/article/fpl-gameweek-1-best-players-captain-picks-2026-27-rankings-127487", "Gameweek 1 projected board."),
    ("RotoWire Premiums", "https://www.rotowire.com/soccer/article/fantasy-premier-league-fpl-rankings-top-400-for-2026-27-season-124261", "Elite assets the FPL 400 is built around."),
    ("RotoWire Value", "https://www.rotowire.com/soccer/article/fantasy-premier-league-fpl-rankings-top-400-for-2026-27-season-124261", "Points-per-million enablers."),
    ("RotoWire DEFCON", "https://www.rotowire.com/soccer/article/fantasy-premier-league-fpl-rankings-top-400-for-2026-27-season-124261", "Defensive-contribution specialists."),
    ("RotoWire Bounce-backs", "https://www.rotowire.com/soccer/article/fantrax-sleeper-premier-league-rankings-top-400-for-the-202627-season-123920", "Lost-season names the draft room fades."),
    ("RotoWire Draft values", "https://www.rotowire.com/soccer/article/fantrax-sleeper-premier-league-rankings-top-400-for-the-202627-season-123920", "Early-ADP steals."),
    ("RotoWire GW1 captains", "https://www.rotowire.com/soccer/article/fpl-gameweek-1-best-players-captain-picks-2026-27-rankings-127487", "Opening-week armband tape."),
    ("The Athletic PL 50", "https://www.nytimes.com/athletic/7518505/2026/08/19/premier-league-best-players-ranking/", "Phil Hay and Tim Spiers, August 2026."),
    ("ESPN PL 50", "https://www.espn.com/soccer/story/_/id/49610912/premier-league-top-50-ranking-best-players-2026-27-season-liverpool-arsenal-man-united", "ESPN Premier League Top 50, 2026-27."),
    ("The Independent Watchlist", "https://www.the-independent.com/sport/football/fpl-fantasy-premier-league-tips-player-rankings-b3032618.html", "44-name 2026/27 FPL watchlist."),
    ("Premier League Scout Selection", "https://www.premierleague.com/en/news/4681112", "Official Scout best squad for GW1."),
    ("Premier League Scout Must-Haves", "https://www.premierleague.com/en/news/4681709", "Four names The Scout says you need."),
    ("Premier League Scout Club Picks", "https://www.premierleague.com/en/news/4688438", "Best FPL pick from each of the 20 clubs."),
    ("Premier League Scout Key Prices", "https://www.premierleague.com/en/news/4680821", "Fifteen key 2026/27 price tags."),
    ("Fantasy Football Fix Elite", "https://www.fantasyfootballfix.com/blog-index/fpl-gameweek-1-guide/", "Elite-manager GW1 board."),
    ("Fantasy Football Fix GW1", "https://www.fantasyfootballfix.com/blog-index/fpl-gw1-top-5-players-2026-27/", "Five key GW1 picks."),
    ("Fantasy Football Fix Captains", "https://www.fantasyfootballfix.com/blog-index/fpl-gameweek-1-captaincy-2026/", "GW1 captain three."),
    ("Yahoo Cheat Sheet", "https://sports.yahoo.com/articles/fantasy-football-cheat-sheet-best-080100274.html", "2026-27 best-player cheat sheet."),
    ("Yahoo GW1 XI", "https://sports.yahoo.com/articles/fpl-2026-27-best-players-141758229.html", "Template XI for Gameweek 1."),
    ("Football Faithful", "https://thefootballfaithful.com/fantasy-premier-league-guide-fpl-best-value-gems-overpriced-traps-and-new-signing-tips/", "Must-haves and value gems, August."),
    ("Football Faithful Premiums", "https://thefootballfaithful.com/the-five-most-expensive-players-in-fpl-2026-27/", "Five priciest 2026/27 assets."),
    ("Fantasy Football Hub", "", "Premium-asset public tape."),
    ("BBC Sport FPL", "https://www.bbc.co.uk/sport/football/articles/cn0np755k4wo", "BBC 2026-27 FPL questions board."),
]

FPL_METRIC_SOURCES = [
    ("Sleeper BPL 2025", "https://support.sleeper.com/en/articles/9702800-scoring-system", "Default Sleeper soccer scoring on 2025/26 Premier League counting stats. This is The Pitch, and half of The Premier."),
    ("FPL 2025/26 Points", "https://fantasy.premierleague.com/", "Official last-season total points."),
    ("FPL Price Board", "https://fantasy.premierleague.com/", "2026/27 starting prices."),
    ("FPL ICT Index", "https://fantasy.premierleague.com/", "Influence / Creativity / Threat composite."),
    ("FPL xGI", "https://fantasy.premierleague.com/", "Expected goal involvements."),
    ("FPL EP Next", "https://fantasy.premierleague.com/", "Official expected points for Gameweek 1."),
    ("FPL Form", "https://fantasy.premierleague.com/", "Recent form score on the FPL app."),
    ("FPL Ownership", "https://fantasy.premierleague.com/", "Official selected-by percent, the public board."),
]

PL_SOURCES = FPL_METRIC_SOURCES + EXPERT_META


def build_sources(players):
    by_key = {p["key"]: p for p in players}
    sources = {
        "Sleeper BPL 2025": metric_map(players, lambda p: p.get("sleeper_pts") or 0, cap=500),
        "FPL 2025/26 Points": metric_map(players, lambda p: p["pts"], cap=400),
        "FPL Price Board": metric_map(players, lambda p: p["price"], cap=300),
        "FPL ICT Index": metric_map(players, lambda p: p["ict"], cap=350),
        "FPL xGI": metric_map(players, lambda p: p["xgi"], cap=350),
        "FPL EP Next": metric_map(players, lambda p: p["ep"], cap=250),
        "FPL Form": metric_map(players, lambda p: p["form"], cap=200),
        "FPL Ownership": metric_map(players, lambda p: p.get("sel") or 0, cap=250),
    }
    for name, names in load_expert_lists().items():
        sources[name] = named_map(players, names)
    return sources, by_key


def aggregate(sources, by_key, min_n=2):
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for k in names:
        ranks = {s: src[k] for s, src in sources.items() if k in src}
        if len(ranks) < min_n:
            continue
        avg = sum(ranks.values()) / len(ranks)
        info = by_key.get(k, {})
        rows.append({
            "key": k,
            "name": info.get("name") or k.title(),
            "full_name": info.get("full_name") or info.get("name") or k.title(),
            "web_name": info.get("web_name") or "",
            "pos": info.get("pos") or "",
            "team": info.get("team") or "",
            "team_name": info.get("team_name") or "",
            "age": info.get("age") or "",
            "group": info.get("pos") or "",
            "avg": round(avg, 2),
            "n": len(ranks),
            "ranks": ranks,
            "price": info.get("price"),
            "sel": info.get("sel"),
            "pts": info.get("pts"),
            "ict": info.get("ict"),
            "xgi": info.get("xgi"),
            "gls": info.get("gls"),
            "ast": info.get("ast"),
            "minutes": info.get("minutes"),
            "cs": info.get("cs"),
            "saves": info.get("saves"),
            "form": info.get("form"),
            "ep": info.get("ep"),
            "news": info.get("news") or "",
            "photo": info.get("photo") or "",
            "code": info.get("code") or "",
            "number": info.get("number") or "",
            "birth": info.get("birth") or "",
            "pens": info.get("pens"),
            "corners": info.get("corners"),
            "dfk": info.get("dfk"),
            "status": info.get("status") or "",
            "chance": info.get("chance"),
            "bonus": info.get("bonus"),
            "xg": info.get("xg"),
            "xa": info.get("xa"),
            "ppg": info.get("ppg"),
            "starts": info.get("starts"),
            "yc": info.get("yc"),
            "rc": info.get("rc"),
            "bps": info.get("bps"),
            "sel_rank": info.get("sel_rank"),
            "influence": info.get("influence"),
            "creativity": info.get("creativity"),
            "threat": info.get("threat"),
            "gc": info.get("gc"),
            "fpl_id": info.get("id"),
            "sleeper_pts": info.get("sleeper_pts") or 0,
            "tackles": info.get("tackles") or 0,
            "cbi": info.get("cbi") or 0,
            "og": info.get("og") or 0,
            "pk_save": info.get("pk_save") or 0,
            "pk_miss": info.get("pk_miss") or 0,
            "value": 0,
            "bk": 0,
        })
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return rows


def filter_pos(rows, pos):
    out = [dict(r) for r in rows if r.get("pos") == pos]
    for i, r in enumerate(out, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return out


PREMIER_SKIP = {
    "Sleeper BPL 2025",
    "FPL 2025/26 Points",
    "FPL ICT Index",
    "FPL xGI",
    "FPL Form",
}
PREMIER_OFFICIAL = {"FPL Price Board", "FPL EP Next", "FPL Ownership"}
# This-year official boards still vote: price, EP-next, ownership.


def build_premier(rows, cap=PITCH_N):
    """2026/27 board: mean of published pro lists.

    Last-season Sleeper and FPL counting stats stay on The Pitch. A name needs
    two published desks before those ranks can lift him. Unranked sources are skipped.
    """
    expert_names = set(load_expert_lists())
    scored = []
    for r in rows:
        ranks = dict(r.get("ranks") or {})
        sleeper = ranks.get("Sleeper BPL 2025") or r.get("sleeper_rank")
        expert = [v for k, v in ranks.items() if k in expert_names]
        official = [v for k, v in ranks.items() if k in PREMIER_OFFICIAL]
        if len(expert) >= 2:
            votes = expert
            tier = 0
        elif expert:
            votes = expert + [90]
            tier = 1
        elif official:
            votes = official
            tier = 2
        elif sleeper:
            votes = [float(sleeper) + 80]
            tier = 3
        else:
            continue
        consensus = sum(votes) / len(votes)
        rec = dict(r)
        rec["sleeper_rank"] = int(sleeper) if sleeper else ""
        rec["consensus"] = round(consensus, 2)
        rec["premier_score"] = round(consensus, 2)
        rec["n_consensus"] = len(expert)
        rec["tier"] = tier
        scored.append(rec)
    scored.sort(key=lambda r: (r["tier"], r["premier_score"], r.get("sleeper_rank") or 999, r["name"]))
    premier = []
    for i, r in enumerate(scored[:cap], 1):
        rec = dict(r)
        rec["bk"] = i
        rec["premier"] = i
        rec["value"] = bk_value(i)
        premier.append(rec)
    return premier


def load_universe():
    players = index_players()
    sources, by_key = build_sources(players)
    agg_rows = {r["key"]: r for r in aggregate(sources, by_key, min_n=1)}
    scored = [
        p for p in players
        if (p.get("sleeper_pts") or 0) > 0 or (p.get("minutes") or 0) > 0
    ]
    scored.sort(key=lambda p: (-(p.get("sleeper_pts") or 0), -(p.get("pts") or 0), p["name"]))
    rows = []
    for i, p in enumerate(scored, 1):
        extra = agg_rows.get(p["key"]) or {}
        rec = dict(extra) if extra else dict(p)
        rec.update({
            "key": p["key"],
            "name": p.get("name"),
            "full_name": p.get("full_name") or p.get("name"),
            "web_name": p.get("web_name") or "",
            "pos": p.get("pos") or "",
            "team": p.get("team") or "",
            "team_name": p.get("team_name") or "",
            "age": p.get("age") or "",
            "group": p.get("pos") or "",
            "sleeper_pts": p.get("sleeper_pts") or 0,
            "sleeper_rank": i,
            "pts": p.get("pts") or 0,
            "gls": p.get("gls") or 0,
            "ast": p.get("ast") or 0,
            "minutes": p.get("minutes") or 0,
            "price": p.get("price"),
            "sel": p.get("sel"),
            "tackles": p.get("tackles") or 0,
            "cbi": p.get("cbi") or 0,
        })
        ranks = dict(extra.get("ranks") or {})
        ranks["Sleeper BPL 2025"] = i
        rec["ranks"] = ranks
        rec["n"] = len(ranks)
        rec["avg"] = round(sum(ranks.values()) / len(ranks), 2) if ranks else float(i)
        rec["bk"] = i
        rec["value"] = bk_value(i)
        rows.append(rec)
    pitch = [dict(r) for r in rows[:PITCH_N]]
    for i, r in enumerate(pitch, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    premier = build_premier(rows, cap=PITCH_N)
    prem_map = {r["key"]: r["bk"] for r in premier}
    for r in pitch:
        r["premier"] = prem_map.get(r["key"])
    for r in rows:
        r["premier"] = prem_map.get(r["key"])
    fwd = filter_pos(rows, "FWD")[:FWD_N]
    mid = filter_pos(rows, "MID")[:MID_N]
    defence = filter_pos(rows, "DEF")[:DEF_N]
    gkp = filter_pos(rows, "GKP")[:GKP_N]
    dest = ROOT / "data" / "ranks" / "sleeper-bpl-2025.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(
        [{"rank": r["sleeper_rank"], "name": r["name"], "pos": r["pos"], "team": r["team"],
          "sleeper_pts": r["sleeper_pts"], "fpl_pts": r.get("pts")} for r in rows[:PITCH_N]],
        indent=2,
    ) + "\n")
    return {
        "sources": sources,
        "players": players,
        "by_key": by_key,
        "pitch": pitch,
        "premier": premier,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
        "overall": rows,
    }
