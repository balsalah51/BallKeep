"""9-cat plus/minus for BasketKeep player files.

Plus = categories the player is good or elite in.
Minus = categories that leak. Never the old 'price / someone knows the rank' line.
"""
from __future__ import annotations

# 2 elite, 1 helps, -1 thin, -2 drain. Omitted cats are average.
# pts reb ast stl blk tpm fg ft to
IDENTS = {
    "victor wembanyama": dict(pts=1, reb=1, blk=2, tpm=1, ft=1, to=-1),
    "cooper flagg": dict(pts=1, reb=1, stl=1, blk=1, tpm=0, ft=0, ast=0),
    "shai gilgeous-alexander": dict(pts=2, ft=2, stl=1, fg=1, reb=0, blk=-1),
    "luka doncic": dict(pts=2, reb=1, ast=2, tpm=1, to=-2, fg=-1, ft=1),
    "anthony edwards": dict(pts=2, tpm=1, stl=1, ft=1, reb=0, ast=0, to=-1),
    "paolo banchero": dict(pts=2, reb=1, ast=1, ft=-1, tpm=0, blk=0, to=-1),
    "cade cunningham": dict(pts=1, ast=2, reb=1, tpm=1, to=-2, fg=0, stl=1),
    "amen thompson": dict(reb=1, ast=1, stl=2, blk=1, tpm=-2, ft=-1, pts=1),
    "chet holmgren": dict(blk=2, tpm=1, reb=1, fg=1, ft=1, pts=1, ast=-1),
    "franz wagner": dict(pts=1, ast=1, stl=1, tpm=1, reb=0, blk=0, ft=1),
    "nikola jokic": dict(pts=2, reb=2, ast=2, fg=2, ft=1, stl=1, tpm=1, to=-1, blk=0),
    "giannis antetokounmpo": dict(pts=2, reb=2, ast=1, fg=2, stl=1, blk=1, ft=-2, tpm=-2, to=-1),
    "jalen williams": dict(pts=1, ast=1, stl=1, tpm=1, reb=1, blk=0, fg=1),
    "anthony black": dict(ast=1, stl=1, reb=1, tpm=-1, ft=-1, pts=0, blk=0),
    "stephon castle": dict(ast=1, stl=1, reb=1, tpm=-1, ft=0, pts=1, to=-1),
    "tyrese maxey": dict(pts=2, tpm=2, ft=1, ast=1, reb=-1, blk=-1, stl=1),
    "ausar thompson": dict(stl=2, reb=1, blk=1, tpm=-2, ft=-1, pts=0, ast=0),
    "scoot henderson": dict(pts=1, ast=1, stl=1, tpm=-1, ft=-1, to=-1, reb=0),
    "jalen brunson": dict(pts=2, ast=1, tpm=1, ft=2, reb=-1, blk=-1, stl=0),
    "ace bailey": dict(pts=1, tpm=1, reb=0, ast=-1, stl=0, blk=0),
    "dylan harper": dict(ast=1, pts=1, stl=1, tpm=-1, reb=0, to=-1),
    "reed sheppard": dict(tpm=2, stl=1, ast=1, reb=-1, blk=0, pts=0, fg=0),
    "alexandre sarr": dict(blk=2, reb=1, tpm=1, pts=0, ast=-1, ft=-1, fg=-1),
    "donovan clingan": dict(blk=2, reb=2, fg=1, tpm=-2, ft=-2, ast=-1, pts=0),
    "jalen duren": dict(reb=2, fg=2, blk=1, tpm=-2, ft=-1, ast=0, pts=1),
    "alperen sengun": dict(pts=1, reb=2, ast=2, fg=1, blk=0, tpm=-1, ft=-1, to=-1),
    "scottie barnes": dict(reb=1, ast=1, stl=1, blk=1, tpm=0, pts=1, ft=0),
    "jaren jackson": dict(blk=2, tpm=1, pts=1, stl=1, reb=0, fg=-1, ft=1, to=-1),
    "evan mobley": dict(reb=1, blk=2, ast=1, fg=1, tpm=0, pts=1, ft=0),
    "lamelo ball": dict(pts=1, ast=2, tpm=2, reb=1, stl=1, to=-2, fg=-1, ft=0),
    "trae young": dict(pts=2, ast=2, tpm=2, ft=2, reb=-2, blk=-2, to=-2, fg=-1),
    "bam adebayo": dict(reb=2, ast=1, stl=1, blk=1, fg=1, tpm=-1, ft=0, pts=1),
    "karl-anthony towns": dict(pts=2, reb=2, tpm=1, ft=1, blk=0, ast=0, to=-1, fg=0),
    "ja morant": dict(pts=2, ast=2, stl=1, reb=0, tpm=-1, ft=-1, to=-2, blk=-1),
    "domantas sabonis": dict(reb=2, ast=2, pts=1, fg=2, tpm=-2, ft=-1, blk=-1, to=-1),
    "deaaron fox": dict(pts=2, ast=1, stl=2, tpm=1, reb=-1, blk=-1, ft=-1),
    "tyrese haliburton": dict(ast=2, tpm=2, stl=1, ft=1, pts=1, reb=-1, to=1, blk=-1),
    "jalen johnson": dict(pts=1, reb=2, ast=1, stl=1, tpm=0, blk=0, ft=0),
    "brandon miller": dict(pts=1, tpm=2, stl=1, reb=0, ast=0, ft=1, to=-1),
    "darius garland": dict(pts=1, ast=2, tpm=2, ft=1, reb=-2, blk=-2, stl=1, to=-1),
    "bilal coulibaly": dict(stl=1, blk=1, reb=1, tpm=0, pts=0, ast=-1, ft=-1),
    "josh giddey": dict(reb=2, ast=2, pts=1, tpm=0, stl=1, fg=-1, ft=-1, to=-1),
    "bennedict mathurin": dict(pts=1, tpm=1, ft=1, reb=0, ast=-1, stl=0, to=-1),
    "keyonte george": dict(pts=1, ast=1, tpm=1, reb=-1, blk=-1, to=-1, ft=0),
    "gradey dick": dict(tpm=2, pts=1, ft=1, reb=-1, ast=-1, blk=-1, stl=0),
    "cam whitmore": dict(pts=1, tpm=1, stl=1, reb=0, ast=-1, ft=-1, fg=-1),
    "matas buzelis": dict(blk=1, tpm=1, reb=1, pts=0, ast=-1, ft=0),
    "jaime jaquez": dict(reb=1, stl=1, pts=1, tpm=-1, ft=-1, ast=0, blk=0),
    "taylor hendricks": dict(tpm=1, blk=1, reb=1, pts=0, ast=-1, stl=1),
    "dereck lively": dict(blk=2, reb=1, fg=2, tpm=-2, ft=-1, ast=0, pts=0),
    "zach edey": dict(reb=2, blk=1, pts=1, tpm=-2, ft=-1, ast=-1, fg=1),
    "jalen suggs": dict(stl=2, tpm=1, blk=1, pts=1, reb=0, to=-1, ft=0),
    "desmond bane": dict(pts=1, tpm=2, ast=1, ft=1, reb=0, blk=-1, stl=1),
    "mikal bridges": dict(tpm=1, stl=1, pts=1, fg=1, reb=0, ast=0, blk=0),
    "og anunoby": dict(stl=2, tpm=1, blk=1, pts=1, reb=0, ast=-1, ft=0),
    "jaylen brown": dict(pts=2, tpm=1, stl=1, reb=1, ast=0, ft=-1, to=-1, fg=0),
    "jayson tatum": dict(pts=2, reb=1, ast=1, tpm=2, stl=1, ft=1, to=-1, blk=0),
    "dyson daniels": dict(stl=2, reb=1, ast=1, tpm=-1, pts=0, ft=-1, blk=0),
    "tari eason": dict(stl=2, reb=1, blk=1, tpm=0, pts=0, ast=-1, to=-1),
    "toumani camara": dict(stl=1, reb=1, tpm=1, blk=0, pts=0, ast=-1, ft=0),
    "keegan murray": dict(tpm=2, reb=1, blk=1, pts=1, ast=-1, stl=0, ft=1),
    "trey murphy": dict(tpm=2, stl=1, blk=1, pts=1, reb=0, ast=-1, ft=1),
    "norman powell": dict(pts=1, tpm=2, ft=1, reb=-1, ast=-1, blk=-1, stl=0),
    "herbert jones": dict(stl=2, blk=1, tpm=1, pts=-1, ast=0, reb=0, ft=0),
    "dillon brooks": dict(tpm=1, stl=1, pts=1, reb=0, ast=-1, ft=0, to=0),
    "austin reaves": dict(pts=1, ast=1, tpm=1, ft=2, reb=0, blk=-1, stl=0),
    "cj mccollum": dict(pts=1, tpm=2, ast=1, reb=-1, blk=-1, stl=0, ft=1),
    "anfernee simons": dict(pts=1, tpm=2, ast=1, reb=-1, blk=-1, stl=0, ft=1),
    "tyler herro": dict(pts=2, tpm=2, ast=1, ft=1, reb=0, blk=-1, stl=0),
    "donovan mitchell": dict(pts=2, tpm=2, stl=1, ft=1, ast=1, reb=-1, blk=-1, to=-1),
    "anthony davis": dict(pts=2, reb=2, blk=2, stl=1, fg=1, tpm=-1, ft=0, ast=0),
    "kawhi leonard": dict(pts=2, stl=2, tpm=1, fg=1, ft=1, reb=1, ast=0, blk=0),
    "devin booker": dict(pts=2, ast=1, tpm=1, ft=2, reb=-1, blk=-1, stl=0, to=-1),
    "paul george": dict(pts=1, tpm=2, stl=1, reb=1, ast=0, ft=1, blk=0),
    "lebron james": dict(pts=2, ast=2, reb=1, stl=1, tpm=0, ft=-1, blk=0, to=-1),
    "stephen curry": dict(pts=2, tpm=2, ast=1, ft=2, stl=1, reb=-1, blk=-1, to=-1),
    "zion williamson": dict(pts=2, reb=1, ast=1, fg=2, stl=1, tpm=-2, ft=-2, to=-1, blk=0),
    "kevin durant": dict(pts=2, tpm=1, ft=2, fg=1, reb=0, ast=0, blk=1, stl=0),
    "lauri markkanen": dict(pts=2, reb=1, tpm=2, ft=1, ast=-1, stl=0, blk=0),
    "james harden": dict(pts=1, ast=2, tpm=2, ft=2, stl=1, reb=1, fg=-1, to=-2, blk=-1),
    "kyrie irving": dict(pts=2, ast=1, tpm=2, fg=1, ft=1, reb=-1, blk=-1, stl=1),
    "pascal siakam": dict(pts=2, reb=1, ast=1, stl=1, fg=1, tpm=0, ft=0, blk=0),
    "rj barrett": dict(pts=1, reb=1, ast=1, tpm=0, ft=-1, stl=0, blk=0),
    "zach lavine": dict(pts=2, tpm=2, ft=1, reb=0, ast=0, stl=0, blk=-1),
    "brandon ingram": dict(pts=2, ast=1, reb=1, tpm=1, ft=1, stl=0, blk=0),
    "jimmy butler": dict(pts=1, ast=1, stl=2, ft=2, reb=1, tpm=-1, blk=0),
    "immanuel quickley": dict(pts=1, ast=1, tpm=2, stl=1, reb=-1, blk=-1, ft=1),
    "demar derozan": dict(pts=2, ft=2, ast=1, tpm=-2, reb=0, stl=1, blk=-1),
    "walker kessler": dict(blk=2, reb=2, fg=2, tpm=-2, ft=-2, ast=-1, pts=0),
    "ivica zubac": dict(reb=2, pts=1, fg=2, blk=1, tpm=-2, ft=-1, ast=0),
    "jakob poeltl": dict(reb=2, fg=2, blk=1, ast=1, tpm=-2, ft=-2, pts=0),
    "nic claxton": dict(blk=2, reb=1, fg=2, ast=1, tpm=-2, ft=-2, pts=0),
    "jarrett allen": dict(reb=2, fg=2, blk=1, pts=1, tpm=-2, ft=-1, ast=0),
    "myles turner": dict(blk=2, tpm=2, pts=1, reb=0, ast=-1, ft=1, stl=0),
    "jaden mcdaniels": dict(stl=1, blk=1, tpm=1, pts=0, ast=-1, reb=1, ft=0),
    "naz reid": dict(pts=1, tpm=2, reb=1, blk=1, ast=0, ft=0, stl=0),
    "julius randle": dict(pts=1, reb=2, ast=1, tpm=1, ft=-1, to=-1, blk=0),
    "cam thomas": dict(pts=2, tpm=1, ft=1, reb=-1, ast=0, blk=-1, stl=0),
    "brook lopez": dict(blk=2, tpm=2, pts=1, reb=0, ast=-1, stl=0, ft=1),
    "rudy gobert": dict(reb=2, blk=2, fg=2, tpm=-2, ft=-2, ast=-1, pts=0),
    "donte divincenzo": dict(tpm=2, stl=1, reb=1, pts=0, ast=0, blk=0, ft=1),
    "mitchell robinson": dict(reb=2, blk=2, fg=2, tpm=-2, ft=-2, ast=-1, pts=-1),
    "josh hart": dict(reb=2, ast=1, stl=1, tpm=1, pts=0, blk=-1, ft=0),
    "payton pritchard": dict(tpm=2, pts=1, ast=1, reb=-1, blk=-1, stl=0, ft=1),
    "derrick white": dict(tpm=2, stl=1, blk=2, ast=1, pts=1, reb=0, ft=1),
    "kristaps porzingis": dict(pts=1, blk=2, tpm=2, reb=1, ft=1, ast=-1, stl=0),
    "jrue holiday": dict(ast=1, stl=1, tpm=1, pts=0, reb=0, blk=0, ft=1),
    "onyeka okongwu": dict(reb=1, blk=1, fg=1, tpm=0, ft=-1, ast=0, pts=1),
    "yves missi": dict(blk=2, reb=1, fg=1, tpm=-2, ft=-1, ast=-1, pts=0),
    "coby white": dict(pts=1, tpm=2, ast=1, reb=-1, blk=-1, stl=0, ft=1),
    "ayo dosunmu": dict(pts=1, ast=1, tpm=1, stl=1, reb=0, blk=0, ft=1),
    "joel embiid": dict(pts=2, reb=1, blk=1, ft=1, ast=1, tpm=0, to=-1, fg=0),
    "kel el ware": dict(blk=2, reb=1, tpm=0, pts=0, ast=-1, ft=-1),
    "kel'el ware": dict(blk=2, reb=1, tpm=0, pts=0, ast=-1, ft=-1),
    "jared mccain": dict(tpm=2, pts=1, ast=0, reb=-1, blk=-1, stl=0, ft=1),
    "isaiah collier": dict(ast=1, pts=1, stl=1, tpm=-1, ft=-1, to=-1, reb=0),
    "cason wallace": dict(stl=2, tpm=1, reb=0, ast=0, pts=0, blk=0, ft=1),
    "keon ellis": dict(stl=2, tpm=2, pts=0, reb=-1, ast=-1, blk=1),
    "andrew nembhard": dict(ast=1, stl=1, tpm=1, pts=1, reb=0, blk=-1, ft=1),
    "goga bitadze": dict(blk=2, reb=1, fg=1, tpm=-1, ft=-1, ast=0, pts=0),
    "santi aldama": dict(tpm=1, reb=1, blk=1, pts=1, ast=0, stl=0, ft=1),
    "isaiah joe": dict(tpm=2, ft=1, pts=0, reb=-1, ast=-1, blk=-1, stl=0),
    "jabari smith": dict(tpm=1, reb=1, blk=1, pts=1, ast=-1, stl=0, ft=1),
    "luguentz dort": dict(tpm=1, stl=1, pts=0, reb=0, ast=-1, ft=0, blk=0),
    "malik monk": dict(pts=1, tpm=1, ast=1, reb=-1, blk=-1, stl=0, ft=1),
    "grayson allen": dict(tpm=2, stl=1, ft=1, pts=1, reb=-1, ast=0, blk=-1),
    "christian braun": dict(pts=1, reb=1, stl=1, tpm=0, ast=0, blk=0, ft=1),
    "miles mcbride": dict(tpm=1, stl=1, pts=0, reb=-1, ast=0, blk=-1, ft=1),
    "isaiah hartenstein": dict(reb=2, ast=1, blk=1, fg=1, tpm=-2, ft=-1, pts=0),
    "daniel gafford": dict(blk=2, reb=1, fg=2, tpm=-2, ft=-1, ast=-1, pts=0),
    "bobby portis": dict(pts=1, reb=2, tpm=1, ast=-1, stl=0, blk=0, ft=1),
    "clint capela": dict(reb=2, blk=1, fg=2, tpm=-2, ft=-2, ast=-1, pts=0),
    "dejounte murray": dict(pts=1, ast=2, stl=2, reb=1, tpm=0, ft=0, to=-1),
    "draymond green": dict(ast=2, reb=1, stl=1, blk=1, pts=-1, tpm=0, to=-1, ft=-1),
    "khris middleton": dict(pts=1, ast=1, tpm=1, reb=0, stl=1, ft=1, blk=-1),
    "jamal murray": dict(pts=2, ast=1, tpm=2, ft=1, reb=0, blk=-1, stl=1, to=-1),
    "michael porter": dict(pts=1, reb=1, tpm=2, ast=-1, stl=0, blk=0, ft=1),
    "aaron gordon": dict(pts=1, reb=1, tpm=1, stl=1, ast=0, blk=0, ft=0),
}

PLUS_LINE = {
    ("pts", 2): "Elite scoring. This is a 25-plus nights player in points leagues too.",
    ("pts", 1): "Helps in points. You are not punting the scoring column.",
    ("reb", 2): "Elite rebounds. The glass is a weekly lock.",
    ("reb", 1): "Helps on the glass. Boards show up even when the shot is quiet.",
    ("ast", 2): "Elite assists. He is a hub — category rooms pay this.",
    ("ast", 1): "Helps in assists. Enough dimes to keep the column honest.",
    ("stl", 2): "Elite steals. This is a 2-steal floor most weeks.",
    ("stl", 1): "Helps in steals. The defensive events are real.",
    ("blk", 2): "Elite blocks. First-round stock in any 9-cat room.",
    ("blk", 1): "Helps in blocks. The rim protection is not empty.",
    ("tpm", 2): "Elite threes. Volume from deep is the extra category.",
    ("tpm", 1): "Helps in threes. Enough makes to keep the column green.",
    ("fg", 2): "Elite field-goal %. Dunks and paint finishes juice the sheet.",
    ("fg", 1): "Helps field-goal %. Efficient enough that you are not punting FG.",
    ("ft", 2): "Elite free-throw %. High volume, high make rate.",
    ("ft", 1): "Helps free-throw %. The line is not a leak.",
    ("to", 1): "Clean with the ball. Turnovers are not the leak.",
    ("to", 2): "Very clean handle. You can pair him with a high-usage mess.",
}

MINUS_LINE = {
    ("pts", -1): "Points run light. You need scoring from the other four.",
    ("pts", -2): "Points are a hole. Cats-only profile — empty scoring nights happen.",
    ("reb", -1): "Rebounds are thin. Guard/wing who does not crash.",
    ("reb", -2): "Rebounds are empty. You are punting the glass if you start him.",
    ("ast", -1): "Assists are light. Not a creator. Need dimes elsewhere.",
    ("ast", -2): "Assists are a hole. Zero-dime nights will show.",
    ("stl", -1): "Steals are quiet. The defensive events have to come from someone else.",
    ("stl", -2): "Steals are empty. No stocks on that end.",
    ("blk", -1): "Blocks are rare. Not a rim protector.",
    ("blk", -2): "Blocks are a hole. Guard-sized on that column.",
    ("tpm", -1): "Threes are thin. The shot is not a category you can count.",
    ("tpm", -2): "Threes are empty. Zero-make nights in a 9-cat week hurt.",
    ("fg", -1): "Field-goal % leaks. Midrange volume and low 3s will ding you.",
    ("fg", -2): "Field-goal % is a drain. You need efficient bigs next to him.",
    ("ft", -1): "Free-throw % is a leak. Paint finishes that miss the line.",
    ("ft", -2): "Free-throw % is a drain. Brick-layer volume will sink a week.",
    ("to", -1): "Turnovers run high. Pair him with safe handles.",
    ("to", -2): "Turnovers are a drain. High usage, high giveaways every night.",
}

POS_PLUS = {
    "PG": [("ast", 1), ("tpm", 1), ("stl", 1)],
    "SG": [("pts", 1), ("tpm", 1), ("stl", 1)],
    "SF": [("pts", 1), ("stl", 1), ("tpm", 1)],
    "PF": [("reb", 1), ("blk", 1), ("pts", 1)],
    "C": [("reb", 1), ("blk", 1), ("fg", 1)],
}

POS_MINUS = {
    "PG": [("reb", -1), ("blk", -2), ("to", -1)],
    "SG": [("reb", -1), ("blk", -2), ("ast", 0)],
    "SF": [("ast", -1), ("blk", 0), ("ft", 0)],
    "PF": [("ast", -1), ("ft", -1), ("tpm", 0)],
    "C": [("tpm", -1), ("ft", -1), ("ast", -1)],
}


def _scores(row: dict) -> dict:
    key = (row.get("key") or "").strip().lower()
    pos = (row.get("pos") or "SF").split("/")[0].strip().upper()
    out = {}
    for cat, sc in POS_PLUS.get(pos, POS_PLUS["SF"]):
        out[cat] = sc
    for cat, sc in POS_MINUS.get(pos, POS_MINUS["SF"]):
        if sc:
            out[cat] = sc
    ident = IDENTS.get(key)
    if ident:
        out.update(ident)
    return out


def _board_lines(row: dict) -> tuple[list[str], list[str]]:
    ranks = row.get("ranks") or {}
    cat_rk = ranks.get("Basketball Monster Cats") or ranks.get("BBall-Index")
    pts_rk = ranks.get("Hashtag Points") or ranks.get("Razzball")
    plus, minus = [], []
    if cat_rk and pts_rk:
        if cat_rk + 18 <= pts_rk:
            plus.append(f"Category boards have him #{cat_rk} vs points #{pts_rk} — stocks and percentages travel.")
        elif pts_rk + 18 <= cat_rk:
            minus.append(f"Points boards have him #{pts_rk} vs cats #{cat_rk} — scoring is the line, empty cats are the tax.")
    return plus, minus


def plus_minus(row: dict) -> tuple[list[str], list[str]]:
    scores = _scores(row)
    plus, minus = [], []
    for cat, sc in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0])):
        if sc >= 1:
            line = PLUS_LINE.get((cat, 2 if sc >= 2 else 1))
            if line:
                plus.append(line)
        elif sc <= -1:
            line = MINUS_LINE.get((cat, -2 if sc <= -2 else -1))
            if line:
                minus.append(line)
    extra_p, extra_m = _board_lines(row)
    plus.extend(extra_p)
    minus.extend(extra_m)

    age = row.get("age")
    try:
        age_n = int(age) if age not in (None, "") else None
    except (TypeError, ValueError):
        age_n = None
    if age_n is not None and age_n >= 34:
        minus.append("Age 34+ — minutes and games played are the hidden category.")
    if age_n is not None and age_n <= 21 and row.get("bk", 99) > 30:
        plus.append("Age still on your side. The counting stats can grow into the rank.")

    plus = list(dict.fromkeys(plus))[:4]
    minus = list(dict.fromkeys(minus))[:4]
    if not plus:
        pos = row.get("pos") or "wing"
        plus.append(f"{pos} counting stats are why he is on The Keep at all.")
    if not minus:
        minus.append("No loud category drain on the sheet — the risk is minutes, not a dead column.")
    return plus, minus
