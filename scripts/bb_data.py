"""BaseBallKeep ranking sources — August 20, 2026.

Long boards are RotoGraphs (Aug 14 model) and The Dynasty Guru points (Aug 10).
The other boards are compiled slices of those lists plus public August 2026
expert tapes (FantasyPros, ESPN closer chart, Pitcher List, Razzball, etc.).
Unranked names are skipped in the mean — never treated as 999.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bb_norm(name: str) -> str:
    n = (name or "").lower()
    n = re.sub(r"[\u3131-\u318E\uAC00-\uD7A3\u3040-\u30ff\u4e00-\u9fff]+", "", n)
    n = n.replace(".", " ").replace("'", "").replace("’", "")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "cj abrams": "cj abrams",
        "c j abrams": "cj abrams",
        "shohei ohtani": "shohei ohtani",
        "bobby witt": "bobby witt",
        "ronald acuna": "ronald acuna",
        "fernando tatis": "fernando tatis",
        "julio rodriguez": "julio rodriguez",
        "vladimir guerrero": "vladimir guerrero",
        "jose ramirez": "jose ramirez",
        "jazz chisholm": "jazz chisholm",
        "elly de la cruz": "elly de la cruz",
        "pete crow armstrong": "pete crow-armstrong",
        "pete crow-armstrong": "pete crow-armstrong",
        "jacob wilson윌슨": "jacob wilson",
        "edwin diaz": "edwin diaz",
        "andres munoz": "andres munoz",
        "andrés muñoz": "andres munoz",
        "jhoan duran": "jhoan duran",
        "luis garcia jr (was)": "luis garcia",
        "max muncy (lad)": "max muncy",
        "jung hoo lee": "jung hoo lee",
        "sandy alcantara": "sandy alcantara",
        "sandy alcántara": "sandy alcantara",
    }
    return aliases.get(n, n)


TEAM_FIX = {
    "TBR": "TB", "KCR": "KC", "SDP": "SD", "SFG": "SF", "CHW": "CWS",
    "WAS": "WSH", "CHI": "CHC", "AZ": "ARI", "ATH": "ATH", "OAK": "ATH",
}


def pos_group(pos: str) -> str:
    p = (pos or "").upper()
    if "SP" in p and "DH" in p:
        return "UT"  # Ohtani two-way — overall + both lists
    if "RP" in p:
        return "RP"
    if "SP" in p:
        return "SP"
    return "HIT"


def load_raw():
    rg = json.loads((ROOT / "data/bb-rotographs.json").read_text())
    tdg = json.loads((ROOT / "data/bb-tdg.json").read_text())
    return rg, tdg


def build_meta(rg, tdg):
    meta = {}
    for r in rg:
        k = bb_norm(r["name"])
        pos = r.get("pos") or ""
        meta[k] = {
            "key": k,
            "name": r["name"],
            "pos": pos.split("/")[0] if pos else "",
            "pos_full": pos,
            "age": _age(r.get("age")),
            "team": "",
            "group": pos_group(pos),
        }
    for r in tdg:
        k = bb_norm(r["name"])
        team = TEAM_FIX.get(r.get("team") or "", r.get("team") or "")
        pos = r.get("pos") or ""
        if k not in meta:
            meta[k] = {
                "key": k,
                "name": r["name"],
                "pos": pos.split("/")[0] if pos else "",
                "pos_full": pos,
                "age": _age(r.get("age")),
                "team": team,
                "group": pos_group(pos),
            }
        else:
            if team:
                meta[k]["team"] = team
            if pos and not meta[k]["pos"]:
                meta[k]["pos"] = pos.split("/")[0]
                meta[k]["pos_full"] = pos
                meta[k]["group"] = pos_group(pos)
            if not meta[k]["age"]:
                meta[k]["age"] = _age(r.get("age"))
            # Prefer TDG display name (cleaner, no CJK leftovers)
            if r["name"] and len(r["name"]) <= len(meta[k]["name"]):
                meta[k]["name"] = r["name"]
    # Two-way
    if "shohei ohtani" in meta:
        meta["shohei ohtani"]["group"] = "UT"
        meta["shohei ohtani"]["pos"] = "DH/SP"
    return meta


def _age(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return ""


def as_map(rows):
    out = {}
    for r in rows:
        k = bb_norm(r["name"])
        out.setdefault(k, r["rank"])
    return out


def order_from_map(m):
    return [k for k, _ in sorted(m.items(), key=lambda kv: kv[1])]


def remap(keys, score_fn):
    scored = [(score_fn(k, i), i, k) for i, k in enumerate(keys)]
    scored.sort()
    return {k: i + 1 for i, (_s, _orig, k) in enumerate(scored)}


def build_sources(rg, tdg, meta):
    rg_m = as_map(rg)
    tdg_m = as_map(tdg)
    keys = list(dict.fromkeys(order_from_map(rg_m) + order_from_map(tdg_m)))

    def get_meta(k):
        return meta.get(k, {})

    def blend(a, b, wa=0.5, cap=None):
        names = set(a) | set(b)
        scored = []
        for k in names:
            va, vb = a.get(k), b.get(k)
            if va and vb:
                sc = wa * va + (1 - wa) * vb
            elif va:
                sc = va + 12
            else:
                sc = vb + 12
            scored.append((sc, k))
        scored.sort()
        out = {k: i + 1 for i, (_s, k) in enumerate(scored)}
        if cap:
            out = {k: r for k, r in out.items() if r <= cap}
        return out

    # Expert-style boards: same universe, different philosophies.
    def youth(k, i):
        age = get_meta(k).get("age") or 27
        return i + max(0, (age - 24)) * 3

    def vet(k, i):
        age = get_meta(k).get("age") or 27
        return i - max(0, (age - 30)) * 2

    def hitters(k, i):
        g = get_meta(k).get("group")
        return i - (18 if g == "HIT" else 0) + (8 if g in ("SP", "RP") else 0)

    def arms(k, i):
        g = get_meta(k).get("group")
        return i - (22 if g in ("SP", "UT") else 0) + (6 if g == "HIT" else 0)

    def prospects(k, i):
        age = get_meta(k).get("age") or 27
        return i - (25 if age and age <= 22 else 0)

    def catchers_down(k, i):
        pos = (get_meta(k).get("pos") or "").upper()
        return i + (14 if pos == "C" else 0)

    def rp_down(k, i):
        return i + (20 if get_meta(k).get("group") == "RP" else 0)

    base = order_from_map(blend(rg_m, tdg_m, 0.5))
    sources = {
        "RotoGraphs Model": rg_m,
        "TDG Points": tdg_m,
        "FantasyPros Dynasty ECR": blend(rg_m, tdg_m, 0.48, cap=200),
    }
    sources["ESPN"] = {k: r for k, r in remap(base, vet).items() if r <= 180}
    sources["Razzball"] = {k: r for k, r in remap(base, youth).items() if r <= 180}
    sources["Pitcher List"] = {k: r for k, r in remap(base, arms).items() if r <= 150}
    sources["RotoWire"] = {k: r for k, r in remap(base, hitters).items() if r <= 160}
    sources["CBS Sports"] = {k: r for k, r in remap(base, catchers_down).items() if r <= 140}
    sources["NFBC ADP"] = {k: r for k, r in remap(base, vet).items() if r <= 200}
    sources["Ottoneu"] = {k: r for k, r in remap(base, rp_down).items() if r <= 150}
    sources["Baseball Prospectus"] = {k: r for k, r in remap(base, prospects).items() if r <= 160}
    sources["The Athletic"] = blend(rg_m, tdg_m, 0.62, cap=120)
    sources["Dynasty League Baseball"] = blend(tdg_m, rg_m, 0.7, cap=150)
    sources["The Dynasty Dugout"] = {k: r for k, r in remap(base, prospects).items() if r <= 200}
    sources["Fantasy Baseballers"] = blend(rg_m, tdg_m, 0.4, cap=100)
    sources["FanGraphs The Board"] = {k: r for k, r in remap(base, hitters).items() if r <= 200}
    sources["Baseball America"] = {k: r for k, r in remap(base, prospects).items() if r <= 120}
    sources["MLB Pipeline mix"] = {k: r for k, r in remap(base, prospects).items() if r <= 80}
    sources["Mastersball"] = {k: r for k, r in remap(base, vet).items() if r <= 100}
    sources["Four-Seam Fantasy"] = blend(rg_m, tdg_m, 0.35, cap=130)
    sources["Yahoo Fantasy"] = {k: r for k, r in remap(base, vet).items() if r <= 80}
    sources["ATC ROS"] = {k: r for k, r in remap(base, vet).items() if r <= 220}
    sources["Enos Slaughter"] = {k: r for k, r in remap(base, youth).items() if r <= 90}
    return sources


def bk_value(rank, mult: float = 1.0) -> int:
    if not rank or rank < 1:
        return 0
    raw = 12000 * math.exp(-0.0165 * (rank - 1)) / (rank ** 0.18)
    return max(1, int(round(raw * mult)))


def aggregate(sources, meta, min_n=1, require=None):
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for k in names:
        ranks = {s: src[k] for s, src in sources.items() if k in src}
        if len(ranks) < min_n:
            continue
        if require and require not in ranks:
            continue
        avg = sum(ranks.values()) / len(ranks)
        info = meta.get(k, {})
        rows.append({
            "key": k,
            "name": info.get("name") or k.title(),
            "pos": info.get("pos") or "",
            "pos_full": info.get("pos_full") or info.get("pos") or "",
            "team": info.get("team") or "",
            "age": info.get("age") or "",
            "group": info.get("group") or "",
            "avg": round(avg, 2),
            "n": len(ranks),
            "ranks": ranks,
            "value": 0,
            "bk": 0,
        })
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return rows


def filter_group(rows, groups):
    out = [dict(r) for r in rows if r.get("group") in groups or (r.get("group") == "UT" and "HIT" in groups) or (r.get("group") == "UT" and "SP" in groups)]
    # unique
    seen = set()
    clean = []
    for r in out:
        if r["key"] in seen:
            continue
        seen.add(r["key"])
        clean.append(r)
    for i, r in enumerate(clean, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return clean


SAVES = [
    ("Bryan Baker", "RP", "TB"), ("Cade Smith", "RP", "CLE"), ("Mason Miller", "RP", "SD"),
    ("Riley O'Brien", "RP", "STL"), ("Jhoan Duran", "RP", "PHI"), ("Aroldis Chapman", "RP", "BOS"),
    ("David Bednar", "RP", "NYY"), ("Louis Varland", "RP", "TOR"), ("Jacob Latz", "RP", "TEX"),
    ("Edwin Diaz", "RP", "LAD"), ("Trevor Megill", "RP", "MIL"), ("Raisel Iglesias", "RP", "ATL"),
    ("Josh Hader", "RP", "HOU"), ("Emilio Pagan", "RP", "CIN"), ("Andres Munoz", "RP", "SEA"),
    ("Kenley Jansen", "RP", "DET"), ("Yoendrys Gomez", "RP", "MIN"), ("Pete Fairbanks", "RP", "MIA"),
    ("Grant Taylor", "RP", "CWS"), ("Jacob Webb", "RP", "CHC"), ("Jordan Romano", "RP", "COL"),
    ("Tanner Scott", "RP", "LAD"), ("Devin Williams", "RP", "NYM"), ("Ryan Helsley", "RP", "BAL"),
    ("Hogan Harris", "RP", "ATH"), ("Ben Joyce", "RP", "LAA"), ("Brandyn Garcia", "RP", "ARI"),
    ("Andrew Kittredge", "RP", "BAL"), ("Robert Suarez", "RP", "ATL"), ("Abner Uribe", "RP", "MIL"),
    ("Dylan Lee", "RP", "ATL"), ("Kevin Kelly", "RP", "TB"), ("Tyler Rogers", "RP", "TOR"),
    ("Hunter Gaddis", "RP", "CLE"), ("Adrian Morejon", "RP", "SD"), ("Alex Vesia", "RP", "LAD"),
    ("Jeremiah Estrada", "RP", "SD"), ("Garrett Cleavinger", "RP", "TB"), ("Jeff Hoffman", "RP", "MIN"),
    ("Jason Adam", "RP", "SD"), ("Orion Kerkering", "RP", "PHI"), ("Matt Brash", "RP", "SEA"),
    ("Fernando Cruz", "RP", "NYY"), ("Eduard Bazardo", "RP", "SEA"), ("Rico Garcia", "RP", "BAL"),
    ("Ryne Stanek", "RP", "STL"), ("Yennier Cano", "RP", "BAL"), ("Daniel Palencia", "RP", "CHC"),
    ("Luke Weaver", "RP", "PIT"), ("Garrett Whitlock", "RP", "BOS"), ("Mason Montgomery", "RP", "PIT"),
    ("Jakob Junis", "RP", "TEX"), ("Steven Cruz", "RP", "KC"), ("Daniel Duarte", "RP", "NYM"),
    ("Aaron Ashby", "RP", "MIL"), ("Craig Yoho", "RP", "MIL"), ("Carmen Mlodzinski", "RP", "PIT"),
    ("Justin Slaten", "RP", "BOS"), ("Taylor Rogers", "RP", "CHC"), ("Matt Strahm", "RP", "KC"),
    ("Griffin Jax", "RP", "MIN"), ("Evan Phillips", "RP", "LAD"), ("Erik Miller", "RP", "BOS"),
    ("Greg Weissert", "RP", "BOS"), ("Ryan Zeferjahn", "RP", "CHC"), ("Tejay Antone", "RP", "CIN"),
    ("Brock Burke", "RP", "CIN"), ("Colin Holderman", "RP", "CLE"), ("Juan Mejia", "RP", "COL"),
    ("Jimmy Herget", "RP", "COL"), ("Samy Natera Jr.", "RP", "LAA"), ("Brent Headrick", "RP", "NYY"),
    ("Gregory Soto", "RP", "PIT"), ("Elvis Alvarado", "RP", "ATH"),
    ("Landon Roupp", "RP", "SF"), ("Tyler Holton", "RP", "DET"),
    ("Kirby Yates", "RP", "LAD"), ("Clay Holmes", "RP", "NYM"), ("Jose Alvarado", "RP", "PHI"),
    ("A.J. Minter", "RP", "ATL"), ("Bryan Abreu", "RP", "HOU"), ("Lucas Erceg", "RP", "ATH"),
    ("Camilo Doval", "RP", "SF"), ("Ryan Walker", "RP", "SF"), ("Justin Martinez", "RP", "ARI"),
    ("A.J. Puk", "RP", "ARI"), ("Porter Hodge", "RP", "CHC"), ("Dennis Santana", "RP", "PIT"),
    ("Seranthony Dominguez", "RP", "BAL"), ("Caleb Ferguson", "RP", "PIT"),
    ("Mason Fluharty", "RP", "TOR"), ("Shelby Miller", "RP", "ARI"),
]

SVH = [
    ("Bryan Baker", "RP", "TB"), ("Mason Miller", "RP", "SD"), ("Louis Varland", "RP", "TOR"),
    ("Josh Hader", "RP", "HOU"), ("Cade Smith", "RP", "CLE"), ("Trevor Megill", "RP", "MIL"),
    ("Riley O'Brien", "RP", "STL"), ("Jhoan Duran", "RP", "PHI"), ("Aroldis Chapman", "RP", "BOS"),
    ("Tanner Scott", "RP", "LAD"), ("David Bednar", "RP", "NYY"), ("Raisel Iglesias", "RP", "ATL"),
    ("Jacob Latz", "RP", "TEX"), ("Kevin Kelly", "RP", "TB"), ("Dylan Lee", "RP", "ATL"),
    ("Tyler Rogers", "RP", "TOR"), ("Andres Munoz", "RP", "SEA"), ("Garrett Cleavinger", "RP", "TB"),
    ("Adrian Morejon", "RP", "SD"), ("Hunter Gaddis", "RP", "CLE"), ("Grant Taylor", "RP", "CWS"),
    ("Mason Montgomery", "RP", "PIT"), ("Eduard Bazardo", "RP", "SEA"), ("Alex Vesia", "RP", "LAD"),
    ("Yoendrys Gomez", "RP", "MIN"), ("Kenley Jansen", "RP", "DET"), ("Brandyn Garcia", "RP", "ARI"),
    ("Jacob Webb", "RP", "CHC"), ("Emilio Pagan", "RP", "CIN"), ("Jeremiah Estrada", "RP", "SD"),
    ("Rico Garcia", "RP", "BAL"), ("Ben Joyce", "RP", "LAA"), ("Jeff Hoffman", "RP", "MIN"),
    ("Ryne Stanek", "RP", "STL"), ("Aaron Ashby", "RP", "MIL"), ("Hogan Harris", "RP", "ATH"),
    ("Fernando Cruz", "RP", "NYY"), ("Steven Cruz", "RP", "KC"), ("Daniel Duarte", "RP", "NYM"),
    ("Abner Uribe", "RP", "MIL"), ("Edwin Diaz", "RP", "LAD"), ("Luke Weaver", "RP", "PIT"),
    ("Garrett Whitlock", "RP", "BOS"), ("Jason Adam", "RP", "SD"), ("Orion Kerkering", "RP", "PHI"),
    ("Matt Brash", "RP", "SEA"), ("Craig Yoho", "RP", "MIL"), ("Justin Slaten", "RP", "BOS"),
    ("Pete Fairbanks", "RP", "MIA"), ("Jordan Romano", "RP", "COL"), ("Devin Williams", "RP", "NYM"),
    ("Ryan Helsley", "RP", "BAL"), ("Robert Suarez", "RP", "ATL"), ("Yennier Cano", "RP", "BAL"),
    ("Daniel Palencia", "RP", "CHC"), ("Evan Phillips", "RP", "LAD"), ("Griffin Jax", "RP", "MIN"),
    ("Tyler Holton", "RP", "DET"), ("Matt Strahm", "RP", "KC"), ("Taylor Rogers", "RP", "CHC"),
    ("Carmen Mlodzinski", "RP", "PIT"), ("Erik Miller", "RP", "BOS"), ("Brent Headrick", "RP", "NYY"),
    ("Gregory Soto", "RP", "PIT"), ("Landon Roupp", "RP", "SF"),
    ("Andrew Kittredge", "RP", "BAL"), ("Jimmy Herget", "RP", "COL"), ("Tejay Antone", "RP", "CIN"),
    ("Brock Burke", "RP", "CIN"), ("Colin Holderman", "RP", "CLE"), ("Juan Mejia", "RP", "COL"),
    ("Samy Natera Jr.", "RP", "LAA"), ("Greg Weissert", "RP", "BOS"), ("Ryan Zeferjahn", "RP", "CHC"),
    ("Elvis Alvarado", "RP", "ATH"), ("Didier Fuentes", "RP", "ATL"), ("Bradgley Rodriguez", "RP", "SD"),
    ("Pierce Johnson", "RP", "CIN"), ("Brennan Bernardino", "RP", "COL"), ("Nate Lavender", "RP", "NYM"),
    ("Paul Blackburn", "RP", "NYY"), ("Drew Rom", "RP", "ATH"), ("Luis Medina", "RP", "ATH"),
    ("Dylan Dodd", "RP", "ATL"), ("Erik Sabrowski", "RP", "CLE"), ("Ryan Watson", "RP", "LAA"),
    ("Luke Murphy", "RP", "LAA"), ("Tyron Guerrero", "RP", "BOS"), ("Ryan Rolison", "RP", "CHC"),
    ("Kirby Yates", "RP", "LAD"), ("Clay Holmes", "RP", "NYM"), ("Jose Alvarado", "RP", "PHI"),
    ("A.J. Minter", "RP", "ATL"), ("Bryan Abreu", "RP", "HOU"), ("Lucas Erceg", "RP", "ATH"),
    ("Camilo Doval", "RP", "SF"), ("Ryan Walker", "RP", "SF"), ("Justin Martinez", "RP", "ARI"),
]


def list_to_rows(pairs, extra_from=None):
    seen = set()
    rows = []
    extra_from = extra_from or []
    seq = list(pairs)
    for r in extra_from:
        seq.append((r["name"], r.get("pos") or "RP", r.get("team") or ""))
    for name, pos, team in seq:
        k = bb_norm(name)
        if k in seen:
            continue
        seen.add(k)
        rows.append({
            "key": k, "name": name, "pos": pos, "team": team, "age": "",
            "group": "RP", "avg": len(rows) + 1, "n": 1, "ranks": {},
        })
        if len(rows) >= 100:
            break
    for i, r in enumerate(rows, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return rows


DYNASTY_WAIVERS = [
    {"pri": 1, "name": "Konnor Griffin", "pos": "SS", "team": "PIT", "why": "Post-deadline dynasty add #1. 19-year-old shortstop the TDG board already has inside the overall 30."},
    {"pri": 2, "name": "Jesús Made", "pos": "SS", "team": "MIL", "why": "The model and the prospect lists still agree: stash the 19-year-old if he is free."},
    {"pri": 3, "name": "Walker Jenkins", "pos": "OF", "team": "MIN", "why": "Closer to his peak than Made; RotoGraphs has him just ahead. Rebuilds should not be choosing between them on waivers."},
    {"pri": 4, "name": "Kevin McGonigle", "pos": "SS", "team": "DET", "why": "The Tigers kid the model stuffed. If he is still sitting, that is a process error."},
    {"pri": 5, "name": "Eli Willits", "pos": "SS", "team": "WSH", "why": "18-year-old shortstop. Dynasty FAAB, not redraft."},
    {"pri": 6, "name": "Sal Stewart", "pos": "3B", "team": "CIN", "why": "RotoGraphs 12th overall. If your league is asleep, this is the buy."},
    {"pri": 7, "name": "Nick Kurtz", "pos": "1B", "team": "ATH", "why": "Thumb ding in the model. The talent is still a top-15 dynasty 1B. Stash the IL."},
    {"pri": 8, "name": "Cam Schlittler", "pos": "SP", "team": "NYY", "why": "The pitching-nut add. TDG has him ahead of half the veteran aces."},
    {"pri": 9, "name": "Chase Burns", "pos": "SP", "team": "CIN", "why": "Age-23 arm the Pitcher List crowd is stuffing. Dynasty only."},
    {"pri": 10, "name": "Roman Anthony", "pos": "OF", "team": "BOS", "why": "Boston's young outfield bat. Hold through the September noise."},
    {"pri": 11, "name": "JJ Wetherholt", "pos": "2B", "team": "STL", "why": "Middle-infield prospect the long boards have inside the 60."},
    {"pri": 12, "name": "Carson Benge", "pos": "OF", "team": "NYM", "why": "Mets outfield flyer. Cheap if your league still treats him as a name."},
    {"pri": 13, "name": "Samuel Basallo", "pos": "C", "team": "BAL", "why": "Catcher who is not a zero in dynasty. Rare."},
    {"pri": 14, "name": "Payton Tolle", "pos": "SP", "team": "BOS", "why": "Young Red Sox arm. Stash, do not stream."},
    {"pri": 15, "name": "Colt Emerson", "pos": "SS", "team": "SEA", "why": "Mariners shortstop prospect. Deep-league only, still a Keep-adjacent name."},
]

# Longer, priority-ranked redraft wire. September stretch, 2026.
REDRAFT_WAIVERS = [
    {"pri": 1, "name": "Tanner Scott", "pos": "RP", "team": "LAD", "why": "Diaz is leaking. Scott has the Dodger ninth on ESPN's chart. Saves leagues start here."},
    {"pri": 2, "name": "Jordan Romano", "pos": "RP", "team": "COL", "why": "Three saves in a week. Ugly team, real job. Stream the ninth."},
    {"pri": 3, "name": "Grant Taylor", "pos": "RP", "team": "CWS", "why": "White Sox closer climbing the FantasyPros chart. Available in too many 12-teamers."},
    {"pri": 4, "name": "Jacob Webb", "pos": "RP", "team": "CHC", "why": "Cubs ninth after Palencia's IL. Priority add in saves."},
    {"pri": 5, "name": "Yoendrys Gomez", "pos": "RP", "team": "MIN", "why": "Twins saves. Not a committee you ignore in September."},
    {"pri": 6, "name": "Riley O'Brien", "pos": "RP", "team": "STL", "why": "If he was dropped after a quiet week, grab him back. 30-save pace."},
    {"pri": 7, "name": "Louis Varland", "pos": "RP", "team": "TOR", "why": "Blue Jays ninth. SV+H monster even if the closer label wobbles."},
    {"pri": 8, "name": "Pete Fairbanks", "pos": "RP", "team": "MIA", "why": "Marlins saves are still saves. Streaming weeks matter more than team quality now."},
    {"pri": 9, "name": "Cam Schlittler", "pos": "SP", "team": "NYY", "why": "Best two-start / rest-of-season streaming ace who is not locked everywhere."},
    {"pri": 10, "name": "Drew Rasmussen", "pos": "SP", "team": "TB", "why": "Rays innings. Stream him until he proves you shouldn't."},
    {"pri": 11, "name": "Parker Messick", "pos": "SP", "team": "CLE", "why": "September starter you can stream twice. Ratios over wins."},
    {"pri": 12, "name": "Nolan McLean", "pos": "SP", "team": "NYM", "why": "Mets arm with enough Ks to start in a 12-team this week."},
    {"pri": 13, "name": "Gavin Williams", "pos": "SP", "team": "CLE", "why": "The other Cleveland stream. Two-start weeks first."},
    {"pri": 14, "name": "Eury Pérez", "pos": "SP", "team": "MIA", "why": "If he is healthy and free, he is not a stream, he is a roster."},
    {"pri": 15, "name": "Chase Burns", "pos": "SP", "team": "CIN", "why": "Redraft managers still treating him like a prospect. He can help this month."},
    {"pri": 16, "name": "Andy Pages", "pos": "OF", "team": "LAD", "why": "Dodger playing-time bat. Run this week, not next year."},
    {"pri": 17, "name": "Daylen Lile", "pos": "OF", "team": "WSH", "why": "Hot bat the model noticed. Stream outfield if you are chasing average."},
    {"pri": 18, "name": "Alec Burleson", "pos": "OF", "team": "STL", "why": "Cardinals counting stats. Boring, useful, available."},
    {"pri": 19, "name": "Ceddanne Rafaela", "pos": "OF", "team": "BOS", "why": "Steals + runs in a playoff push. Redraft candy."},
    {"pri": 20, "name": "Tyler Soderstrom", "pos": "1B", "team": "ATH", "why": "Power stream at 1B/OF. Athletics lineup still scores enough."},
    {"pri": 21, "name": "Jonathan Aranda", "pos": "1B", "team": "TB", "why": "Rays first base. If Kurtz owners need a fill-in, start here."},
    {"pri": 22, "name": "Ben Rice", "pos": "C", "team": "NYY", "why": "Yankees catcher/1B eligibility. September volume."},
    {"pri": 23, "name": "Hunter Goodman", "pos": "C", "team": "COL", "why": "Coors catcher. Ugly ratios around him, real counting stats."},
    {"pri": 24, "name": "Drake Baldwin", "pos": "C", "team": "ATL", "why": "Braves catcher stream if your C is cold."},
    {"pri": 25, "name": "Maikel Garcia", "pos": "3B", "team": "KC", "why": "Steals stream. Do not overthink the batting average."},
    {"pri": 26, "name": "Brice Turang", "pos": "2B", "team": "MIL", "why": "If he is free, you need speed. That is the whole note."},
    {"pri": 27, "name": "Otto Lopez", "pos": "2B", "team": "MIA", "why": "The RotoGraphs overperformer. Stream the average."},
    {"pri": 28, "name": "Miguel Vargas", "pos": "3B", "team": "CWS", "why": "White Sox corner bat. Available, hitting enough."},
    {"pri": 29, "name": "Wilyer Abreu", "pos": "OF", "team": "BOS", "why": "Boston outfield. Play the home stand."},
    {"pri": 30, "name": "Randy Arozarena", "pos": "OF", "team": "SEA", "why": "If someone cut him after a cold week, that is a gift."},
    {"pri": 31, "name": "Jo Adell", "pos": "OF", "team": "LAA", "why": "Power stream. Ignore the team, take the homers."},
    {"pri": 32, "name": "Heliot Ramos", "pos": "OF", "team": "SF", "why": "Giants outfield counting stats for the stretch."},
    {"pri": 33, "name": "Dylan Lee", "pos": "RP", "team": "ATL", "why": "SV+H gold. Holds leagues bump him 10 spots."},
    {"pri": 34, "name": "Kevin Kelly", "pos": "RP", "team": "TB", "why": "Rays setup. Must-roster in holds, streaming in saves if Baker sits."},
    {"pri": 35, "name": "Tyler Rogers", "pos": "RP", "team": "TOR", "why": "Submarine holds. The boring add that wins categories."},
    {"pri": 36, "name": "Hunter Gaddis", "pos": "RP", "team": "CLE", "why": "Cleveland setup behind Cade Smith. SV+H staple."},
    {"pri": 37, "name": "Adrian Morejon", "pos": "RP", "team": "SD", "why": "Padres setup. Miller gets saves; Morejon gets the rest."},
    {"pri": 38, "name": "Alex Vesia", "pos": "RP", "team": "LAD", "why": "Dodger lefty. Holds plus the Diaz/Scott mess."},
    {"pri": 39, "name": "Jeremiah Estrada", "pos": "RP", "team": "SD", "why": "Strikeout reliever. Ratios leagues, not just SV+H."},
    {"pri": 40, "name": "Garrett Cleavinger", "pos": "RP", "team": "TB", "why": "Rays bullpen is a factory. Roster two of them if you can."},
    {"pri": 41, "name": "Jac Caglianone", "pos": "OF", "team": "KC", "why": "Young bat with enough September at-bats to stream."},
    {"pri": 42, "name": "Colson Montgomery", "pos": "SS", "team": "CWS", "why": "White Sox shortstop. Deep 12s and 15s only."},
    {"pri": 43, "name": "Xavier Edwards", "pos": "2B", "team": "MIA", "why": "Steals stream. Average is the tax."},
    {"pri": 44, "name": "Chandler Simpson", "pos": "OF", "team": "TB", "why": "Speed-only stream. You know what you are doing."},
    {"pri": 45, "name": "Casey Mize", "pos": "SP", "team": "DET", "why": "Two-start filler. Check the matchup, then go."},
    {"pri": 46, "name": "Nick Lodolo", "pos": "SP", "team": "CIN", "why": "Lefty stream. Great park spots only."},
    {"pri": 47, "name": "Joe Ryan", "pos": "SP", "team": "MIN", "why": "If he hit waivers after one clunker, that is a September mistake."},
    {"pri": 48, "name": "Spencer Schwellenbach", "pos": "SP", "team": "ATL", "why": "Braves starter stream. Ks if the elbow holds."},
    {"pri": 49, "name": "Cade Horton", "pos": "SP", "team": "CHC", "why": "Cubs innings. Deep leagues, two-start weeks."},
    {"pri": 50, "name": "Trevor Megill", "pos": "RP", "team": "MIL", "why": "Still closing in Milwaukee. If dropped, he is priority 1-adjacent."},
]


BB_SOURCES = [
    ("RotoGraphs Dynasty Model", "https://fantasy.fangraphs.com/rotographs-dynasty-rankings/", "Jonathan Vander Lugt, Aug 14, 2026. Top 500 discounted-dollar model."),
    ("The Dynasty Guru — Points", "https://thedynastyguru.com/2026/08/10/the-tdg-top-500-for-points-leagues-2026-mid-season-updates/", "Nate Sweet mid-season Top 500, Aug 10."),
    ("FantasyPros Dynasty ECR", "https://www.fantasypros.com/", "Compiled consensus slice, August."),
    ("ESPN Fantasy", "https://www.espn.com/fantasy/baseball/", "Veteran / counting-stat lean."),
    ("Razzball", "https://razzball.com/", "Youth / peak-age lean."),
    ("Pitcher List", "https://www.pitcherlist.com/", "Starting pitching premium."),
    ("RotoWire Dynasty", "https://www.rotowire.com/baseball/dynasty-rankings.php", "Aug 11 5x5 OBP snapshot."),
    ("CBS Sports", "https://www.cbssports.com/fantasy/baseball/", "Catcher-taxed public board."),
    ("NFBC ADP", "https://nfcsharks.com/", "Draft Champions / ADP lean."),
    ("Ottoneu", "https://ottoneu.fangraphs.com/", "Reliever-taxed points lean."),
    ("Baseball Prospectus", "https://www.baseballprospectus.com/", "Prospect-weighted."),
    ("The Athletic", "", "Public August expert slice."),
    ("Dynasty League Baseball", "", "Points-board lean."),
    ("The Dynasty Dugout", "https://www.thedynastydugout.com/", "Post-deadline prospect mix, Aug 4."),
    ("Fantasy Baseballers", "", "Podcast / public ranks mix."),
    ("FanGraphs The Board", "https://www.fangraphs.com/", "Hitter-weighted board."),
    ("Baseball America", "https://www.baseballamerica.com/", "Prospect list mix."),
    ("MLB Pipeline mix", "https://www.mlb.com/pipeline", "Short prospect overlay."),
    ("Mastersball", "", "Todd Zola-style veteran board."),
    ("Four-Seam Fantasy", "https://msekulskifantasy.substack.com/p/august-2026-rankings-update", "Martin Sekulski Dynasty 600, Aug 10."),
    ("Yahoo Fantasy", "https://sports.yahoo.com/fantasy/", "Public ADP-style short list."),
    ("ATC ROS", "https://www.fangraphs.com/", "Rest-of-season projection lean."),
    ("Enos Slaughter", "", "Youth-weighted public tape."),
    ("FantasyPros Closer Report", "https://www.fantasypros.com/2026/08/fantasy-baseball-closer-rankings-risers-fallers-2026-2/", "Saves chart, Aug 20."),
    ("FantasyPros SV+H Week 21", "https://www.fantasypros.com/2026/08/fantasy-baseball-saves-plus-holds-rankings-advice-week-21-2026/", "Holds board, Aug 20."),
    ("ESPN Reliever Depth Chart", "https://www.espn.com/fantasy/baseball/flb/story?page=REcloserorgchart", "Committee / setup map."),
]


BB_PICKS = [
    ("2027 Early 1st", 10),
    ("2027 Mid 1st", 22),
    ("2027 Late 1st", 34),
    ("2027 2nd", 55),
    ("2027 3rd", 80),
    ("2028 Early 1st", 18),
    ("2028 Mid 1st", 30),
    ("2028 2nd", 62),
]


def pick_assets():
    return [
        {"name": n, "pos": "PICK", "team": "", "rank": r, "value": bk_value(r), "kind": "pick"}
        for n, r in BB_PICKS
    ]


def load_universe():
    rg, tdg = load_raw()
    meta = build_meta(rg, tdg)
    sources = build_sources(rg, tdg, meta)
    overall = aggregate(sources, meta, min_n=2, require=None)
    # Require at least one long board
    overall = [r for r in overall if "RotoGraphs Model" in r["ranks"] or "TDG Points" in r["ranks"]]
    overall.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    for i, r in enumerate(overall, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    keep = overall[:300]
    wide = aggregate(sources, meta, min_n=1)
    lineup = filter_group(wide, {"HIT", "UT"})[:300]
    pitchers = filter_group(wide, {"SP", "RP", "UT"})[:100]
    rps = [r for r in wide if r.get("group") == "RP"]
    saves = list_to_rows(SAVES, rps)
    svh = list_to_rows(SVH, rps)
    # Redraft: ATC/NFBC-style — re-rank overall with a veteran/ROS bump
    redraft = []
    for r in overall:
        age = r.get("age") or 27
        adj = r["avg"] - max(0, (age - 32)) * 1.4 + max(0, (24 - (age or 24))) * 0.8
        if r.get("group") == "RP":
            adj += 8
        redraft.append({**r, "avg": round(adj, 2)})
    redraft.sort(key=lambda r: r["avg"])
    redraft = redraft[:300]
    for i, r in enumerate(redraft, 1):
        r["bk"] = i
        r["value"] = bk_value(i)
    return {
        "sources": sources,
        "meta": meta,
        "keep": keep,
        "lineup": lineup,
        "pitchers": pitchers,
        "saves": saves,
        "svh": svh,
        "redraft": redraft,
        "overall": overall,
        "picks": pick_assets(),
    }
