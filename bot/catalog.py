"""Ball Keep desk data: load the site catalog and answer ranking / trade questions."""
from __future__ import annotations

import json
import re
import sys
from functools import cached_property
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bk_curve import FORMULA, bk_value  # noqa: E402

CATALOG_PATH = ROOT / "data" / "discord-catalog.json"

NICKNAMES = {
    "jsn": "jaxon smith-njigba",
    "jj": "justin jefferson",
    "jefferson": "justin jefferson",
    "bijan": "bijan robinson",
    "cmc": "christian mccaffrey",
    "mccaffrey": "christian mccaffrey",
    "jt": "jonathan taylor",
    "puka": "puka nacua",
    "chase": "jamarr chase",
    "jamarr": "jamarr chase",
    "sun god": "amon-ra st brown",
    "st brown": "amon-ra st brown",
    "arsb": "amon-ra st brown",
    "ceedee": "ceedee lamb",
    "cd": "ceedee lamb",
    "cd lamb": "ceedee lamb",
    "mahomes": "patrick mahomes",
    "lamar": "lamar jackson",
    "hurts": "jalen hurts",
    "herbert": "justin herbert",
    "maye": "drake maye",
    "allen": "josh allen",
    "bowers": "brock bowers",
    "london": "drake london",
    "nabers": "malik nabers",
    "jeanty": "ashton jeanty",
    "gibbs": "jahmyr gibbs",
    "achane": "devon achane",
    "hampton": "omarion hampton",
    "tet": "tetairoa mcmillan",
    "egbuka": "emeka egbuka",
    "ladd": "ladd mcconkey",
    "btj": "brian thomas",
    "ajb": "a j brown",
    "aj brown": "a j brown",
    "saquon": "saquon barkley",
    "dak": "dak prescott",
    "burrow": "joe burrow",
    "purdy": "brock purdy",
    "nix": "bo nix",
    "dart": "jaxson dart",
    "love": "jeremiyah love",
    "j love": "jordan love",
    "jordan love": "jordan love",
    "tlaw": "trevor lawrence",
    "mcbride": "trey mcbride",
    "kyler": "kyler murray",
    "nico": "nico collins",
    "olave": "chris olave",
    "puka nacua": "puka nacua",
    "mhj": "marvin harrison",
    "marv": "marvin harrison",
    "breece": "breece hall",
    "kyren": "kyren williams",
    "bucky": "bucky irving",
    "bhayshul": "bhayshul tuten",
    "cam ward": "cam ward",
    "shedeur": "shedeur sanders",
    "gunderson": "colston loveland",
    "loveland": "colston loveland",
    "golden": "matthew golden",
    "tyler warren": "tyler warren",
    "kw3": "kenneth walker",
    "devonta": "devonta smith",
    "smitty": "devonta smith",
    "dk": "dk metcalf",
    "metcalf": "dk metcalf",
    "tee": "tee higgins",
    "gwilson": "garrett wilson",
    "scary terry": "terry mclaurin",
    "mclaurin": "terry mclaurin",
    "kelce": "travis kelce",
    "kittle": "george kittle",
    "hock": "tj hockenson",
    "hockenson": "tj hockenson",
    "laporta": "sam laporta",
    "goff": "jared goff",
    "stafford": "matthew stafford",
    "stroud": "cj stroud",
    "cj": "cj stroud",
    "daniels": "jayden daniels",
    "jd5": "jayden daniels",
    "caleb": "caleb williams",
    "fields": "justin fields",
    "tua": "tua tagovailoa",
    "geno": "geno smith",
    "baker": "baker mayfield",
    "darnold": "sam darnold",
    "jjm": "jj mccarthy",
    "mccarthy": "jj mccarthy",
    "penix": "michael penix",
    "nix bo": "bo nix",
    "rice": "rashee rice",
    "flowers": "zay flowers",
    "kraft": "tucker kraft",
    "fannin": "harold fannin",
    "mason": "jordan mason",
    "ohtani": "shohei ohtani",
    "shohei": "shohei ohtani",
    "judge": "aaron judge",
    "soto": "juan soto",
    "witt": "bobby witt",
    "elly": "elly de la cruz",
    "edlc": "elly de la cruz",
    "pca": "pete crow-armstrong",
    "skenes": "paul skenes",
    "caminero": "junior caminero",
    "yordan": "yordan alvarez",
    "acuna": "ronald acuna",
    "tatis": "fernando tatis",
    "julio": "julio rodriguez",
    "vlad": "vladimir guerrero",
    "jazz": "jazz chisholm",
    "gunnar": "gunnar henderson",
    "corbin": "corbin carroll",
    "mookie": "mookie betts",
    "trout": "mike trout",
    "devers": "rafael devers",
    "hader": "josh hader",
    "diaz": "edwin diaz",
    "haaland": "erling haaland",
    "bruno": "bruno fernandes",
    "saka": "bukayo saka",
    "palmer": "cole palmer",
    "semenyo": "antoine semenyo",
    "mbeumo": "bryan mbeumo",
    "szobo": "dominik szoboszlai",
    "joao pedro": "joao pedro",
    "wirtz": "florian wirtz",
    "isak": "alexander isak",
    "vvd": "virgil van dijk",
    "raya": "david raya",
    "foden": "phil foden",
    "salah": "mohamed salah",
    "eze": "eberechi eze",
    "kinsky": "antonin kinsky",
    "calafiori": "riccardo calafiori",
    "porro": "pedro porro",
    "saliba": "william saliba",
    "guehi": "marc guehi",
    "watkins": "ollie watkins",
    "szoboszlai": "dominik szoboszlai",
    "thiago": "igor thiago",
}

MLB_ALIASES = {
    "yankees": "NYY", "yanks": "NYY", "nyy": "NYY", "new york yankees": "NYY",
    "mets": "NYM", "nym": "NYM",
    "red sox": "BOS", "boston": "BOS", "bos": "BOS",
    "white sox": "CWS", "cws": "CWS", "chw": "CWS",
    "cubs": "CHC", "chc": "CHC",
    "dodgers": "LAD", "lad": "LAD", "la dodgers": "LAD",
    "angels": "ANA", "laa": "ANA", "ana": "ANA",
    "giants": "SF", "sfg": "SF", "sf": "SF",
    "athletics": "ATH", "as": "ATH", "oak": "ATH", "ath": "ATH",
    "padres": "SD", "sdp": "SD", "sd": "SD",
    "mariners": "SEA", "sea": "SEA",
    "rangers": "TEX", "tex": "TEX",
    "astros": "HOU", "hou": "HOU",
    "braves": "ATL", "atl": "ATL",
    "phillies": "PHI", "phils": "PHI", "phi": "PHI",
    "nationals": "WSH", "nats": "WSH", "wsh": "WSH", "was": "WSH",
    "marlins": "MIA", "mia": "MIA",
    "rays": "TB", "tampa": "TB", "tbr": "TB",
    "orioles": "BAL", "bal": "BAL",
    "blue jays": "TOR", "jays": "TOR", "tor": "TOR",
    "guardians": "CLE", "cleveland": "CLE", "cle": "CLE",
    "tigers": "DET", "det": "DET",
    "twins": "MIN", "min": "MIN",
    "royals": "KC", "kcr": "KC",
    "cardinals": "STL", "cards": "STL", "stl": "STL",
    "brewers": "MIL", "brew crew": "MIL", "mil": "MIL",
    "cubbies": "CHC",
    "pirates": "PIT", "bucs": "PIT", "pit": "PIT",
    "reds": "CIN", "cin": "CIN",
    "rockies": "COL", "col": "COL",
    "dbacks": "ARI", "d-backs": "ARI", "diamondbacks": "ARI", "ari": "ARI",
}

NFL_ALIASES = {
    "GBP": "GB", "KCC": "KC", "JAC": "JAX", "WSH": "WAS", "NWE": "NE",
    "NOR": "NO", "SFO": "SF", "TAM": "TB", "GNB": "GB", "LAR": "LAR",
    "LAC": "LAC", "NYP": "NYJ", "NYG": "NYG", "BILLS": "BUF", "PATS": "NE",
    "PATRIOTS": "NE", "COWBOYS": "DAL", "CHIEFS": "KC", "EAGLES": "PHI",
    "NINERS": "SF", "49ERS": "SF", "PACKERS": "GB", "VIKINGS": "MIN",
    "LIONS": "DET", "BEARS": "CHI", "FALCONS": "ATL", "SAINTS": "NO",
    "BUCS": "TB", "BUCCANEERS": "TB", "DOLPHINS": "MIA", "JETS": "NYJ",
    "GIANTS": "NYG", "COMMANDERS": "WAS", "RAVENS": "BAL", "STEELERS": "PIT",
    "BENGALS": "CIN", "BROWNS": "CLE", "TITANS": "TEN", "COLTS": "IND",
    "JAGUARS": "JAX", "JAGS": "JAX", "TEXANS": "HOU", "BRONCOS": "DEN",
    "RAIDERS": "LV", "CHARGERS": "LAC", "RAMS": "LAR", "CARDINALS": "ARI",
    "SEAHAWKS": "SEA", "PANTHERS": "CAR",
}


def compact(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", (s or "").lower())
    s = re.sub(r"\b20(\d{2})\b", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def norm(name: str) -> str:
    n = (name or "").lower()
    n = n.replace(".", " ")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = n.replace("'", "").replace("’", "")
    n = re.sub(r"\s+", " ", n).strip()
    return NICKNAMES.get(n, n)


class Catalog:
    def __init__(self, path: Path | None = None):
        self.path = path or CATALOG_PATH
        self.raw = json.loads(self.path.read_text())

    @property
    def updated(self) -> str:
        return self.raw.get("updated", "")

    @property
    def site(self) -> str:
        return self.raw.get("site", "https://ballkeep.com")

    @cached_property
    def players(self) -> list[dict]:
        return self.raw.get("players") or []

    @cached_property
    def by_key(self) -> dict[str, dict]:
        return {p["key"]: p for p in self.players}

    def list_for(self, board: str) -> list[dict]:
        key = {
            "keep": "keep",
            "the keep": "keep",
            "sf": "keep",
            "superflex": "keep",
            "board": "board",
            "the board": "board",
            "ppr": "ppr",
            "redraft": "ppr",
            "redraft ppr": "ppr",
            "sf redraft": "sf_redraft",
            "superflex redraft": "sf_redraft",
            "redraft superflex": "sf_redraft",
            "sf_redraft": "sf_redraft",
            "std": "standard",
            "standard": "standard",
            "classic": "classic",
            "the classic": "classic",
            "half ppr": "classic",
            "0.5 ppr": "classic",
            "half-ppr": "classic",
            "dst": "dst",
            "defense": "dst",
            "defenses": "dst",
            "the d": "dst",
            "top defenses": "dst",
            "kickers": "kickers",
            "kicker": "kickers",
            "k": "kickers",
            "top kickers": "kickers",
            "fence": "fence",
            "the fence": "fence",
            "idp": "fence",
            "dynasty idp": "fence",
            "mixed": "fence",
            "superflex idp": "fence",
            "rookies": "rookies",
            "rookie": "rookies",
            "bbkeep": "bb_keep",
            "bb keep": "bb_keep",
            "bb_keep": "bb_keep",
            "lineup": "bb_lineup",
            "the lineup": "bb_lineup",
            "bb_lineup": "bb_lineup",
            "pitchers": "bb_pitchers",
            "bb_pitchers": "bb_pitchers",
            "saves": "bb_saves",
            "bb_saves": "bb_saves",
            "bullpen": "bb_saves",
            "svh": "bb_svh",
            "bb_svh": "bb_svh",
            "holds": "bb_svh",
            "bbredraft": "bb_redraft",
            "bb_redraft": "bb_redraft",
            "bb redraft": "bb_redraft",
            "farm": "bb_farm",
            "the farm": "bb_farm",
            "bb_farm": "bb_farm",
            "prospects": "bb_farm",
            "bb farm": "bb_farm",
            "pitch": "pl_pitch",
            "the pitch": "pl_pitch",
            "pl_pitch": "pl_pitch",
            "plpitch": "pl_pitch",
            "premier": "pl_premier",
            "the premier": "pl_premier",
            "pl_premier": "pl_premier",
            "plpremier": "pl_premier",
            "plfwd": "pl_fwd",
            "attack": "pl_fwd",
            "pl_fwd": "pl_fwd",
            "plmid": "pl_mid",
            "midfield": "pl_mid",
            "pl_mid": "pl_mid",
            "pldef": "pl_def",
            "defence": "pl_def",
            "pl_def": "pl_def",
            "plgkp": "pl_gkp",
            "keepers": "pl_gkp",
            "pl_gkp": "pl_gkp",
            "bkkeep": "bk_keep",
            "bk keep": "bk_keep",
            "bk_keep": "bk_keep",
            "basketkeep": "bk_keep",
            "bkboard": "bk_board",
            "bk board": "bk_board",
            "bk_board": "bk_board",
            "bkguards": "bk_guards",
            "bk_guards": "bk_guards",
            "bkwings": "bk_wings",
            "bk_wings": "bk_wings",
            "bkbigs": "bk_bigs",
            "bk_bigs": "bk_bigs",
        }.get((board or "keep").lower(), "keep")
        return self.raw.get(key) or []

    def find(self, query: str, limit: int = 8, sport: str | None = None) -> list[dict]:
        q = norm(query)
        if not q:
            return []
        scored = []
        football = list(self.players or self.raw.get("board") or [])
        baseball = list(self.raw.get("bb_players") or self.raw.get("bb_keep") or [])
        soccer = list(self.raw.get("pl_players") or self.raw.get("pl_pitch") or [])
        basketball = list(self.raw.get("bk_players") or self.raw.get("bk_keep") or [])
        if sport == "baseball":
            pool = baseball
        elif sport == "football":
            pool = football
        elif sport in ("soccer", "premier", "pl", "fpl"):
            pool = soccer
        elif sport in ("basketball", "nba", "bk"):
            pool = basketball
        else:
            pool = football + baseball + soccer + basketball
        for p in pool:
            key = p.get("key") or norm(p.get("name", ""))
            name = norm(p.get("name", ""))
            full = norm(p.get("full_name") or "")
            hay = f"{name} {full} {p.get('pos','')} {p.get('team','')} {p.get('slug','')}"
            if q == key or q == name or (full and q == full):
                scored.append((0, p))
            elif name.startswith(q) or key.startswith(q) or (full and full.startswith(q)):
                scored.append((1, p))
            elif q in name or q in key or (full and q in full):
                scored.append((2, p))
            elif all(tok in hay for tok in q.split()):
                scored.append((3, p))
        scored.sort(key=lambda x: (
            x[0],
            (x[1].get("lists") or {}).get("The Keep")
            or (x[1].get("lists") or {}).get("BB Keep")
            or (x[1].get("lists") or {}).get("The Pitch")
            or (x[1].get("lists") or {}).get("The Keep")
            or x[1].get("keep")
            or x[1].get("bk")
            or 999,
            x[1].get("name", ""),
        ))
        seen = set()
        out = []
        for _s, p in scored:
            k = (p.get("sport") or "football") + ":" + (norm(p.get("name", "")) or p.get("key") or "")
            if k in seen:
                continue
            seen.add(k)
            out.append(p)
            if len(out) >= limit:
                break
        if len(out) < limit and sport != "baseball":
            for board_key in ("keep", "board", "ppr", "standard", "classic", "dst", "kickers", "rookies"):
                for r in self.raw.get(board_key) or []:
                    name = norm(r.get("name", ""))
                    if not name:
                        continue
                    if q == name or name.startswith(q) or q in name:
                        tag = "football:" + name
                        if tag in seen:
                            continue
                        seen.add(tag)
                        out.append(r)
                        if len(out) >= limit:
                            return out
        if len(out) < limit and sport != "football":
            for board_key in ("bb_keep", "bb_lineup", "bb_pitchers", "bb_redraft", "bb_farm"):
                for r in self.raw.get(board_key) or []:
                    name = norm(r.get("name", ""))
                    if not name:
                        continue
                    if q == name or name.startswith(q) or q in name:
                        tag = "baseball:" + name
                        if tag in seen:
                            continue
                        seen.add(tag)
                        row = dict(r)
                        row.setdefault("sport", "baseball")
                        out.append(row)
                        if len(out) >= limit:
                            return out
        if sport in (None, "soccer", "premier", "pl", "fpl"):
            for board_key in ("pl_premier", "pl_pitch", "pl_fwd", "pl_mid", "pl_def", "pl_gkp"):
                for r in self.raw.get(board_key) or []:
                    name = norm(r.get("name", ""))
                    if not name:
                        continue
                    if q == name or name.startswith(q) or q in name:
                        tag = "soccer:" + name
                        if tag in seen:
                            continue
                        seen.add(tag)
                        row = dict(r)
                        row.setdefault("sport", "soccer")
                        out.append(row)
                        if len(out) >= limit:
                            return out
        if sport in (None, "basketball", "nba", "bk"):
            for board_key in ("bk_keep", "bk_board", "bk_guards", "bk_wings", "bk_bigs"):
                for r in self.raw.get(board_key) or []:
                    name = norm(r.get("name", ""))
                    if not name:
                        continue
                    if q == name or name.startswith(q) or q in name:
                        tag = "basketball:" + name
                        if tag in seen:
                            continue
                        seen.add(tag)
                        row = dict(r)
                        row.setdefault("sport", "basketball")
                        out.append(row)
                        if len(out) >= limit:
                            return out
        return out

    def one(self, query: str, sport: str | None = None) -> dict | None:
        hits = self.find(query, limit=1, sport=sport)
        return hits[0] if hits else None

    def board_row(self, name: str, board: str = "keep") -> dict | None:
        q = norm(name)
        for r in self.list_for(board):
            if norm(r.get("name", "")) == q or q in norm(r.get("name", "")):
                return r
        return None

    def resolve_asset(self, token: str, mode: str = "sf") -> dict | None:
        t = (token or "").strip()
        if not t:
            return None
        nt = norm(t)
        want = compact(t)
        bb_modes = {
            "bbkeep": "bb_keep",
            "bblineup": "bb_lineup",
            "bbpitchers": "bb_pitchers",
            "bbredraft": "bb_redraft",
            "bbsaves": "bb_saves",
            "bbsvh": "bb_svh",
        }
        pl_mode_keys = {
            "plpitch", "pitch250", "thepitch", "plpremier", "premier400", "thepremier",
            "plfwd", "plmid", "pldef", "plgkp",
        }
        bk_modes = {
            "bkkeep": "bk_keep",
            "bkboard": "bk_board",
            "bkguards": "bk_guards",
            "bkwings": "bk_wings",
            "bkbigs": "bk_bigs",
        }
        if mode in bb_modes:
            pick_pool = self.raw.get("bb_picks")
        elif mode in pl_mode_keys:
            pick_pool = []
        elif mode in bk_modes:
            pick_pool = self.raw.get("bk_picks")
        else:
            pick_pool = self.raw.get("picks")
        exact_pick = None
        fuzzy_pick = None
        for p in pick_pool or []:
            pn = compact(p["name"])
            if want == pn or nt == norm(p["name"]):
                exact_pick = {**p, "kind": "pick"}
                break
            if want and (want in pn or pn in want) and len(want) >= 6:
                fuzzy_pick = fuzzy_pick or {**p, "kind": "pick"}
        pl_modes = {
            "plpitch": "pl_pitch",
            "pitch250": "pl_pitch",
            "thepitch": "pl_pitch",
            "plpremier": "pl_premier",
            "premier400": "pl_premier",
            "thepremier": "pl_premier",
            "plfwd": "pl_fwd",
            "plmid": "pl_mid",
            "pldef": "pl_def",
            "plgkp": "pl_gkp",
        }
        if exact_pick:
            return exact_pick
        if fuzzy_pick:
            return fuzzy_pick
        if mode in bb_modes:
            row = self.board_row(t, mode)
            if not row:
                return None
            return {
                "name": row.get("name"),
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "rank": row.get("bk"),
                "value": int(row.get("value") or bk_value(row.get("bk") or 0)),
                "kind": "player",
                "url": "",
                "slug": "",
            }
        if mode in pl_modes:
            row = self.board_row(t, mode) or self.one(t, sport="soccer")
            if not row:
                return None
            return {
                "name": row.get("name"),
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "rank": row.get("bk"),
                "value": int(row.get("value") or bk_value(row.get("bk") or 0)),
                "kind": "player",
                "url": row.get("url") or "",
                "slug": row.get("slug") or "",
            }
        if mode in bk_modes:
            row = self.board_row(t, mode) or self.one(t, sport="basketball")
            if not row:
                return None
            return {
                "name": row.get("name"),
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "rank": row.get("bk"),
                "value": int(row.get("value") or bk_value(row.get("bk") or 0)),
                "kind": "player",
                "url": row.get("url") or f"https://ballkeep.com/bk/players/{row.get('slug') or ''}.html",
                "slug": row.get("slug") or "",
            }
        player = self.one(t, sport="football")
        if player and player.get("sport") == "baseball":
            player = None
        if not player:
            # long-board-only name
            row = self.board_row(t, "board")
            if not row:
                return None
            player = row
        rank = None
        value = None
        if mode in ("sf", "superflex", "keep"):
            rank = (player.get("lists") or {}).get("The Keep") or player.get("bk")
            if rank is None:
                brow = self.board_row(player.get("name", ""), "board")
                rank = brow.get("bk") if brow else None
            value = bk_value(rank or 0, 1.0)
        elif mode in ("oneqb", "1qb"):
            rank = (player.get("lists") or {}).get("The Keep") or player.get("bk")
            if rank is None:
                brow = self.board_row(player.get("name", ""), "board")
                rank = brow.get("bk") if brow else None
            mult = 0.38 if (player.get("pos") == "QB") else 1.0
            value = bk_value(rank or 0, mult)
        elif mode in ("ppr",):
            row = self.board_row(player.get("name", ""), "ppr")
            rank = row.get("bk") if row else None
            value = bk_value(rank or 0)
        elif mode in ("classic", "halfppr", "half-ppr"):
            row = self.board_row(player.get("name", ""), "classic")
            rank = row.get("bk") if row else None
            value = bk_value(rank or 0)
        elif mode in ("std", "standard"):
            row = self.board_row(player.get("name", ""), "standard")
            rank = row.get("bk") if row else None
            value = bk_value(rank or 0)
        else:
            rank = player.get("bk")
            value = player.get("value") or bk_value(rank or 0)
        return {
            "name": player.get("name"),
            "pos": player.get("pos") or "",
            "team": player.get("team") or "",
            "rank": rank,
            "value": int(value or 0),
            "kind": "player",
            "url": player.get("url") or "",
            "slug": player.get("slug") or "",
        }

    def parse_side(self, blob: str, mode: str) -> tuple[list[dict], list[str]]:
        bits = [b.strip() for b in re.split(r"[,/+]| and ", blob or "") if b.strip()]
        found, missing = [], []
        for b in bits:
            asset = self.resolve_asset(b, mode)
            if asset:
                found.append(asset)
            else:
                missing.append(b)
        return found, missing

    def trade(self, mode: str, side_a: str, side_b: str) -> dict:
        a, miss_a = self.parse_side(side_a, mode)
        b, miss_b = self.parse_side(side_b, mode)
        ta = sum(x["value"] for x in a)
        tb = sum(x["value"] for x in b)
        diff = ta - tb
        bigger = max(ta, tb, 1)
        pct = abs(diff) / bigger
        if ta and tb and pct > 0.08:
            winner = "Side A" if diff > 0 else "Side B"
            label = f"{winner} Wins"
        else:
            label = "Fair Trade"
        return {
            "mode": mode,
            "a": a,
            "b": b,
            "missing": miss_a + miss_b,
            "total_a": ta,
            "total_b": tb,
            "diff": diff,
            "label": label,
        }

    def nfl_abbr(self, team: str) -> str:
        t = (team or "").upper().strip()
        return NFL_ALIASES.get(t, t)

    def mlb_abbr(self, team: str) -> str:
        raw = (team or "").strip()
        return MLB_ALIASES.get(raw.lower(), raw.upper())

    def team_players(self, team: str, board: str = "keep") -> list[dict]:
        t = self.nfl_abbr(team)
        return [r for r in self.list_for(board) if (r.get("team") or "").upper() == t]

    def pos_top(self, pos: str, board: str = "keep", limit: int = 12) -> list[dict]:
        p = (pos or "").upper().strip()
        aliases = {"QUARTERBACK": "QB", "RUNNING BACK": "RB", "WIDE RECEIVER": "WR", "TIGHT END": "TE", "PICK": "PICK"}
        p = aliases.get(p, p)
        return [r for r in self.list_for(board) if (r.get("pos") or "").upper() == p][:limit]

    def nfl_games(self, team: str | None = None, week: int | None = None) -> list[dict]:
        rows = list(self.raw.get("nfl") or [])
        if week:
            rows = [g for g in rows if g.get("week") == week]
        team_u = self.nfl_abbr(team) if team else ""
        if team_u:
            rows = [
                g for g in rows
                if team_u in {
                    (g.get("away_abbr") or "").upper(),
                    (g.get("home_abbr") or "").upper(),
                }
                or team_u in (g.get("away") or "").upper()
                or team_u in (g.get("home") or "").upper()
            ]
        return rows

    def mlb_games(self, team: str) -> list[dict]:
        t = self.mlb_abbr(team)
        return [
            g for g in self.raw.get("mlb") or []
            if t in {(g.get("away") or "").upper(), (g.get("home") or "").upper()}
        ]

    def deals_for(self, query: str = "") -> list[dict]:
        rows = list(self.raw.get("deals") or [])
        q = norm(query)
        if not q:
            return rows
        hits = []
        for d in rows:
            names = [norm(n) for n in d.get("names") or []]
            if any(q == n or q in n or n.startswith(q) for n in names):
                hits.append(d)
        return hits

    def youtube(self, player: dict) -> str | None:
        yid = player.get("youtube_id")
        if not yid:
            key = player.get("key") or norm(player.get("name", ""))
            p = self.by_key.get(key)
            yid = (p or {}).get("youtube_id")
        if not yid:
            want = player.get("key") or norm(player.get("name", ""))
            for row in list(self.raw.get("pl_players") or []) + list(self.raw.get("bb_players") or []):
                if (row.get("key") or "") == want or norm(row.get("name", "")) == want:
                    yid = row.get("youtube_id")
                    break
        return f"https://www.youtube.com/watch?v={yid}" if yid else None


def load() -> Catalog:
    return Catalog()
