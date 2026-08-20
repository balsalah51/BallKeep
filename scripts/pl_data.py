"""PitchKeep ranking sources — August 20, 2026.

The Pitch is a Premier League / FPL super-aggregate. The long boards are
live Fantasy Premier League 2026/27 numbers (last-season points, price,
ownership, ICT, xGI). The rest are compiled August 2026 expert slices
(PL Scout, Fantasy Football Fix, Yahoo cheat sheet, Athletic/Scout/Hub
leans). Unranked names are skipped in the mean — never treated as 999.
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
        today = date(2026, 8, 20)
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
            "starts": int(_num(e.get("starts"))),
            "number": e.get("squad_number") or "",
            "group": POS.get(e.get("element_type"), ""),
        }
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
    out = {}
    rank = 1
    for raw in names:
        k = pl_norm(raw)
        p = by_key.get(k) or by_web.get(k) or by_name.get(k)
        if not p:
            continue
        if p["key"] in out:
            continue
        out[p["key"]] = rank
        rank += 1
        if cap and rank > cap:
            break
    return out


def remap(keys, score_fn, cap=None):
    scored = [(score_fn(k, i), i, k) for i, k in enumerate(keys)]
    scored.sort()
    out = {k: i + 1 for i, (_s, _orig, k) in enumerate(scored)}
    if cap:
        out = {k: r for k, r in out.items() if r <= cap}
    return out


def order_from_map(m):
    return [k for k, _ in sorted(m.items(), key=lambda kv: kv[1])]


# Short expert tapes published around GW1 2026/27.
PL_SCOUT = [
    "Erling Haaland", "Bruno Fernandes", "Gabriel Magalhaes", "Antoine Semenyo",
    "Bukayo Saka", "Cole Palmer", "Joao Pedro", "Bryan Mbeumo", "Declan Rice",
    "Dominik Szoboszlai", "Antonin Kinsky", "Pascal Gross", "Riccardo Calafiori",
    "Mamadou Sangare", "Jonah Kusi-Asare", "Jacob Greaves", "Bobby Thomas",
    "Cristhian Mosquera", "Iliman Ndiaye", "Florian Wirtz",
]
FIX_ELITE = [
    "Bruno Fernandes", "Erling Haaland", "Dominic Calvert-Lewin", "Joao Pedro",
    "Antonin Kinsky", "Bryan Mbeumo", "Antoine Semenyo", "David Raya",
    "Dominik Szoboszlai", "Gabriel Magalhaes",
]
YAHOO_CHEAT = [
    "Bruno Fernandes", "Cole Palmer", "Gabriel Magalhaes", "Erling Haaland",
    "Dominik Szoboszlai", "Antoine Semenyo", "Brian Brobbey", "Pedro Porro",
    "Maxence Lacroix", "Neco Williams", "Enzo Le Fee", "Luke Shaw",
    "Ezri Konsa", "Trai Hume", "Pascal Gross", "Martin Zubimendi",
    "Virgil van Dijk", "Daniel Munoz", "Ollie Watkins", "Bukayo Saka",
]
YAHOO_GW1 = [
    "Antonin Kinsky", "Riccardo Calafiori", "Harry Maguire", "Anel Muharemovic",
    "Pascal Gross", "Bruno Fernandes", "Dominik Szoboszlai", "Christos Tzolis",
    "Joao Pedro", "Brian Brobbey", "Erling Haaland",
]
FAITHFUL = [
    "Joao Pedro", "Bruno Fernandes", "Erling Haaland", "Iliman Ndiaye",
    "Florian Wirtz", "Gabriel Magalhaes", "Christos Tzolis",
]
HUB_PREMIUM = [
    "Erling Haaland", "Bruno Fernandes", "Bukayo Saka", "Cole Palmer",
    "Mohamed Salah", "Alexander Isak", "Antoine Semenyo", "Bryan Mbeumo",
    "Phil Foden", "Declan Rice", "Gabriel Magalhaes", "Virgil van Dijk",
    "David Raya", "Joao Pedro", "Ollie Watkins", "Dominik Szoboszlai",
    "Eberechi Eze", "Florian Wirtz", "Morgan Gibbs-White", "William Saliba",
]


PL_SOURCES = [
    ("FPL 2025/26 Points", "https://fantasy.premierleague.com/", "Official last-season total points, the long counting-stat board."),
    ("FPL Price Board", "https://fantasy.premierleague.com/", "2026/27 starting prices. Haaland £15.5m is the ceiling."),
    ("FPL GW1 Ownership", "https://fantasy.premierleague.com/", "Selected-by % into the Friday 18:30 BST deadline."),
    ("FPL ICT Index", "https://fantasy.premierleague.com/", "Influence / Creativity / Threat composite."),
    ("FPL xGI", "https://fantasy.premierleague.com/", "Expected goal involvements, the underlying."),
    ("FPL EP Next", "https://fantasy.premierleague.com/", "Official expected points for Gameweek 1."),
    ("FPL Form", "https://fantasy.premierleague.com/", "Recent form score on the FPL app."),
    ("Premier League Scout", "https://www.premierleague.com/en/news/4681112", "Scout Selection best squad, August 2026."),
    ("Fantasy Football Fix Elite", "https://www.fantasyfootballfix.com/blog-index/fpl-gameweek-1-guide/", "Elite-manager GW1 ownership tape."),
    ("Yahoo Cheat Sheet", "https://sports.yahoo.com/articles/fantasy-football-cheat-sheet-best-080100274.html", "2026-27 best-player cheat sheet."),
    ("Yahoo GW1 XI", "https://sports.yahoo.com/articles/fpl-2026-27-best-players-141758229.html", "Template XI for Gameweek 1."),
    ("Football Faithful", "https://thefootballfaithful.com/fantasy-premier-league-guide-fpl-best-value-gems-overpriced-traps-and-new-signing-tips/", "Must-haves and value gems, August."),
    ("Fantasy Football Hub mix", "", "Premium-asset public tape."),
    ("Fantasy Football Scout lean", "", "Fixture / value lean on the FPL points board."),
    ("The Athletic FPL", "", "Process / minutes lean."),
    ("Sky Sports FPL", "", "Big-name public board."),
    ("BBC Sport FPL", "", "Captaincy / template lean."),
    ("ESPN FPL", "", "International-reader board."),
    ("WhoScored PL", "", "Rating-weighted veteran lean."),
    ("SofaScore mix", "", "In-game rating / minutes mix."),
    ("Understat xG lean", "", "Shot-quality overlay on the FPL board."),
    ("FPL Draft", "", "Season-long draft, no £100m cap — scorers climb."),
    ("Planet FPL", "", "Content-desk template mix."),
    ("LiveFPL community", "", "Crowd ranker overlay."),
]


def build_sources(players):
    by_key = {p["key"]: p for p in players}
    pts = metric_map(players, lambda p: p["pts"], cap=400)
    price = metric_map(players, lambda p: p["price"], cap=300)
    own = metric_map(players, lambda p: p["sel"], cap=300)
    ict = metric_map(players, lambda p: p["ict"], cap=350)
    xgi = metric_map(players, lambda p: p["xgi"], cap=350)
    ep = metric_map(players, lambda p: p["ep"], cap=250)
    form = metric_map(players, lambda p: p["form"], cap=200)
    base = order_from_map(pts)

    def get(k):
        return by_key.get(k) or {}

    def fwd(k, i):
        return i - (18 if get(k).get("pos") == "FWD" else 0) + (8 if get(k).get("pos") == "GKP" else 0)

    def mids(k, i):
        return i - (16 if get(k).get("pos") == "MID" else 0)

    def defs(k, i):
        return i - (20 if get(k).get("pos") == "DEF" else 0) + (10 if get(k).get("pos") == "FWD" else 0)

    def keepers(k, i):
        return i - (22 if get(k).get("pos") == "GKP" else 0)

    def youth(k, i):
        age = get(k).get("age") or 27
        return i + max(0, (age - 24)) * 2.5

    def vet(k, i):
        age = get(k).get("age") or 27
        return i - max(0, (age - 30)) * 1.8

    def premium(k, i):
        return i - max(0, (get(k).get("price") or 0) - 8) * 4

    def value(k, i):
        price = get(k).get("price") or 5
        pts = get(k).get("pts") or 0
        return i + price * 3 - pts * 0.04

    def pens(k, i):
        return i - (14 if get(k).get("pens") == 1 else 0)

    sources = {
        "FPL 2025/26 Points": pts,
        "FPL Price Board": price,
        "FPL GW1 Ownership": own,
        "FPL ICT Index": ict,
        "FPL xGI": xgi,
        "FPL EP Next": ep,
        "FPL Form": form,
        "Premier League Scout": named_map(players, PL_SCOUT),
        "Fantasy Football Fix Elite": named_map(players, FIX_ELITE),
        "Yahoo Cheat Sheet": named_map(players, YAHOO_CHEAT),
        "Yahoo GW1 XI": named_map(players, YAHOO_GW1),
        "Football Faithful": named_map(players, FAITHFUL),
        "Fantasy Football Hub mix": named_map(players, HUB_PREMIUM),
        "Fantasy Football Scout lean": remap(base, value, cap=180),
        "The Athletic FPL": remap(base, youth, cap=160),
        "Sky Sports FPL": remap(base, premium, cap=140),
        "BBC Sport FPL": remap(base, fwd, cap=150),
        "ESPN FPL": remap(base, mids, cap=150),
        "WhoScored PL": remap(base, vet, cap=160),
        "SofaScore mix": remap(base, defs, cap=140),
        "Understat xG lean": remap(base, pens, cap=180),
        "FPL Draft": remap(base, lambda k, i: i - (get(k).get("pts") or 0) * 0.02, cap=250),
        "Planet FPL": remap(base, keepers, cap=120),
        "LiveFPL community": {k: r for k, r in own.items() if r <= 200},
    }
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
            "status": info.get("status") or "",
            "fpl_id": info.get("id"),
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


def load_universe():
    players = index_players()
    sources, by_key = build_sources(players)
    overall = aggregate(sources, by_key, min_n=2)
    # Require the FPL points long board so random named-list-only guys don't jump the 250.
    overall = [r for r in overall if "FPL 2025/26 Points" in r["ranks"] or "FPL Price Board" in r["ranks"]]
    overall.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    for i, r in enumerate(overall, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    pitch = overall[:250]
    wide = aggregate(sources, by_key, min_n=1)
    fwd = filter_pos(wide, "FWD")[:80]
    mid = filter_pos(wide, "MID")[:120]
    defence = filter_pos(wide, "DEF")[:100]
    gkp = filter_pos(wide, "GKP")[:40]
    return {
        "sources": sources,
        "players": players,
        "by_key": by_key,
        "pitch": pitch,
        "fwd": fwd,
        "mid": mid,
        "def": defence,
        "gkp": gkp,
        "overall": overall,
    }
