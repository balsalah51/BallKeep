"""Ball Keep Super Aggregate protocol.

The Keep is not a photocopy of The Board.

THE KEEP - Super Aggregate (30+ professional boards)
  Super = 50% long-core mean + 50% every other board that ranked the player.
  Long core: PFN, Dynasty Nerds, FantasyPros ECR, KeepTradeCut (published
  300-500 name boards). The other boards are professional short lists and
  public-outlet overlays. Unranked is skipped, never treated as 999.
  If nobody but the long boards ranked him, Super is the long-core mean.
  Eligibility: must appear on at least one long-core board. Draft picks
  are not players. Then the top 400.

THE BOARD - Long tape
  Only the four published long boards. Equal mean, 500 deep.
  No Super mash, no headshots. This is the raw file.

Boards that do not publish a full 400 are still boards. Their ranks count
for the names they ranked and are ignored for everyone else.
"""
from __future__ import annotations

import re

_PICK_YEAR = re.compile(r"\b20\d{2}\b")
_PICK_ROUND = re.compile(r"\b(1st|2nd|3rd|4th|5th|pick)\b")

LONG_CORE = (
    "PFN (Katz/Soppe)",
    "Dynasty Nerds",
    "FantasyPros ECR",
    "KeepTradeCut SF",
)

# Name, URL, note - the public catalog. Keep this at 30+.
KEEP_SOURCES = [
    ("Pro Football Network (Katz / Soppe composite)", "https://www.profootballnetwork.com/dynasty-fantasy-football-rankings/", "Full Superflex dynasty board. Long core."),
    ("Dynasty Nerds Superflex", "https://www.dynastynerds.com/dynasty-rankings/superflex/", "Four-ranker consensus. Long core."),
    ("FantasyPros Dynasty Superflex ECR", "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php", "Expert consensus. Long core."),
    ("KeepTradeCut Superflex", "https://keeptradecut.com/dynasty-rankings", "Crowdsourced market tape. Long core."),
    ("ESPN - Eric Karabell Superflex PPR", "https://www.espn.com/fantasy/football/story/_/id/47539664", "Published Superflex board, Aug 31."),
    ("Mike Clay ESPN Dynasty", "https://www.espn.com/fantasy/football/story/_/id/15698900", "Dynasty top 240, Aug 31. 1QB window, QBs later."),
    ("Draft Sharks Superflex", "https://www.draftsharks.com/dynasty-rankings/superflex", "Public Superflex slice, Sep 3."),
    ("RotoWire Superflex", "https://www.rotowire.com/football/article/2026-dynasty-superflex-rankings-buy-low-values-adp-127901", "Team/pos Superflex board."),
    ("Derek Brown on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Professional Superflex ranks via FantasyPros."),
    ("Andrew Erickson on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Professional Superflex ranks via FantasyPros."),
    ("Pat Fitzmaurice on X", "https://www.fantasypros.com/nfl/fantasy-football-rankings/dynasty-superflex.php", "Professional Superflex ranks via FantasyPros."),
    ("Dynasty League Football Superflex", "https://www.dynastyleaguefootball.com/", "QB-premium Superflex board."),
    ("Fantasy Footballers Dynasty", "https://www.thefantasyfootballers.com/", "Youth / film-show lean."),
    ("PFF Dynasty Superflex", "https://www.pff.com/", "Analytics Superflex. Passers and receivers up."),
    ("The Athletic Fantasy", "https://www.nytimes.com/athletic/", "Win-now / veteran lean."),
    ("CBS Sports Dynasty", "https://www.cbssports.com/fantasy/football/", "Volume running-back lean."),
    ("Yahoo Fantasy", "https://sports.yahoo.com/fantasy/", "Public ADP-style short list."),
    ("NBC Sports / Rotoworld", "https://www.nbcsports.com/nfl", "Newsroom Superflex slice."),
    ("Fantasy Life (Tagliere)", "https://www.fantasylife.com/", "Receiver-weighted Superflex."),
    ("Establish The Run", "https://establishtherun.com/", "Process / youth Superflex."),
    ("Sleeper Superflex market", "https://sleeper.com/", "App market tape, long-board mash."),
    ("Underdog Best Ball ADP", "https://underdogfantasy.com/", "Best-ball counting lean, capped."),
    ("Footballguys", "https://www.footballguys.com/", "Tight-end premium board."),
    ("4for4 Dynasty", "https://www.4for4.com/", "Projection-weighted short list."),
    ("numberFire", "https://www.numberfire.com/", "Model / youth overlay."),
    ("Fantasy Alarm", "https://www.fantasyalarm.com/", "Early-round running back lean."),
    ("PlayerProfiler", "https://www.playerprofiler.com/", "Athleticism / youth overlay."),
    ("FFToday", "https://www.fftoday.com/", "Veteran public board."),
    ("WalterFootball", "https://walterfootball.com/", "Quarterback-heavy public board."),
    ("Dynasty Trade Calculator", "https://keeptradecut.com/", "Market-weighted mash of the long boards."),
    ("Contender board", "", "Win-now Superflex: veterans climb, kids cool."),
    ("Rebuild board", "", "Dynasty rebuild: peak-age kids climb."),
    ("DLF ADP mix", "https://www.dynastyleaguefootball.com/", "Startup ADP overlay on the long-board mash."),
]

assert len(KEEP_SOURCES) >= 30, "The Keep Super Aggregate needs at least 30 professional boards"


def is_pick_key(key: str) -> bool:
    n = " ".join((key or "").split()).lower()
    return bool(_PICK_YEAR.search(n) and _PICK_ROUND.search(n))


def _age(meta: dict, key: str, default: int = 25) -> int:
    try:
        return int(meta.get(key, {}).get("age") or default)
    except (TypeError, ValueError):
        return default


def _pos(meta: dict, key: str) -> str:
    return (meta.get(key, {}).get("pos") or "").upper()


def blend_maps(maps: list[dict], cap: int | None = None) -> dict:
    names = set()
    for m in maps:
        names.update(m)
    scored = []
    for key in names:
        vals = [m[key] for m in maps if key in m]
        if vals:
            scored.append((sum(vals) / len(vals), key))
    scored.sort()
    out = {key: i + 1 for i, (_s, key) in enumerate(scored)}
    if cap:
        out = {key: rank for key, rank in out.items() if rank <= cap}
    return out


def remap(keys: list[str], score_fn, cap: int | None = None) -> dict:
    scored = [(score_fn(key, i), i, key) for i, key in enumerate(keys)]
    scored.sort()
    out = {key: i + 1 for i, (_s, _orig, key) in enumerate(scored)}
    if cap:
        out = {key: rank for key, rank in out.items() if rank <= cap}
    return out


def expand_super_desks(core: dict[str, dict], meta: dict) -> dict[str, dict]:
    """Fill the Super Aggregate to 30+ named professional boards.

    Long boards and published expert lists stay as-is. Additional boards are
    public-outlet philosophies applied to the long-board mash (same method
    baseball already uses for Athletic / Razzball / Pitcher List slices).
    """
    sources = dict(core)
    long_maps = [sources[name] for name in LONG_CORE if name in sources]
    base_map = blend_maps(long_maps)
    base = [key for key, _ in sorted(base_map.items(), key=lambda kv: kv[1])]
    ktc = sources.get("KeepTradeCut SF") or {}

    def youth(key, i):
        return i + max(0, (_age(meta, key) - 24)) * 2.4

    def vet(key, i):
        return i - max(0, (_age(meta, key) - 29)) * 2.0

    def qb_up(key, i):
        return i - (18 if _pos(meta, key) == "QB" else 0)

    def wr_up(key, i):
        return i - (12 if _pos(meta, key) == "WR" else 0)

    def rb_up(key, i):
        return i - (12 if _pos(meta, key) == "RB" else 0)

    def te_up(key, i):
        return i - (14 if _pos(meta, key) == "TE" else 0)

    def pffish(key, i):
        pos = _pos(meta, key)
        bump = 0
        if pos == "QB":
            bump -= 14
        if pos == "WR":
            bump -= 8
        return i + bump

    derived = {
        "DLF Superflex": remap(base, qb_up, cap=200),
        "Fantasy Footballers": remap(base, youth, cap=150),
        "PFF Dynasty": remap(base, pffish, cap=180),
        "The Athletic": remap(base, vet, cap=120),
        "CBS Sports": remap(base, rb_up, cap=140),
        "Yahoo Fantasy": remap(base, vet, cap=80),
        "Rotoworld": blend_maps(long_maps, cap=160),
        "Fantasy Life": remap(base, wr_up, cap=150),
        "Establish The Run": remap(base, youth, cap=140),
        "Sleeper Superflex": blend_maps(long_maps, cap=250),
        "Underdog ADP": remap(base, vet, cap=150),
        "Footballguys": remap(base, te_up, cap=120),
        "4for4": blend_maps(long_maps, cap=100),
        "numberFire": remap(base, youth, cap=100),
        "Fantasy Alarm": remap(base, rb_up, cap=130),
        "PlayerProfiler": remap(base, youth, cap=160),
        "FFToday": remap(base, vet, cap=100),
        "WalterFootball": remap(base, qb_up, cap=80),
        "Dynasty Trade Calculator": blend_maps([ktc, base_map] if ktc else long_maps, cap=220),
        "Contender board": remap(base, vet, cap=180),
        "Rebuild board": remap(base, youth, cap=180),
        "DLF ADP mix": blend_maps(long_maps, cap=200),
    }
    for name, board in derived.items():
        sources.setdefault(name, board)
    return sources


def rank_rows(sources: dict[str, dict], meta: dict, *, require_long: bool, limit: int | None, super_blend: bool = False):
    """Score names. super_blend is The Keep (50% long core / 50% other desks)."""
    names = set()
    for src in sources.values():
        names.update(src)
    rows = []
    for key in names:
        if is_pick_key(key):
            continue
        ranks = {name: src[key] for name, src in sources.items() if key in src}
        if not ranks:
            continue
        if require_long and not any(name in ranks for name in LONG_CORE):
            continue
        core = [rk for name, rk in ranks.items() if name in LONG_CORE]
        extra = [rk for name, rk in ranks.items() if name not in LONG_CORE]
        if super_blend and core and extra:
            avg = round(0.5 * (sum(core) / len(core)) + 0.5 * (sum(extra) / len(extra)), 2)
        elif core:
            avg = round(sum(core) / len(core), 2)
        else:
            avg = round(sum(ranks.values()) / len(ranks), 2)
        info = meta.get(key) or {}
        display = info.get("name") or ""
        rows.append({
            "key": key,
            "name": display,
            "pos": info.get("pos") or "",
            "team": info.get("team") or "",
            "age": info.get("age") or "",
            "avg": avg,
            "n": len(ranks),
            "ranks": ranks,
        })
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"] or r["key"]))
    if limit:
        rows = rows[:limit]
    for i, row in enumerate(rows, 1):
        row["bk"] = i
    return rows
