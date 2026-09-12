"""My Team: BK Value picture of a Sleeper league you load yourself."""
from __future__ import annotations

import json
from pathlib import Path

from bk_curve import ALGORITHM, QB_1QB_MULT, bk_value
from seo import also_on_desk, breadcrumbs, breadcrumb_jsonld

ROOT = Path(__file__).resolve().parents[1]
DEMO_TEAMS = (
    "Cedar", "Harbor", "Summit", "Prairie", "Quarry",
    "Beacon", "Hollow", "Ridge", "Forge", "Delta",
)


def pick_band(worst_index: int, n: int) -> str:
    """worst_index 0 is the weakest record. Returns Early, Mid, or Late."""
    if n <= 0:
        return "Mid"
    third = n / 3.0
    if worst_index < third:
        return "Early"
    if worst_index < 2 * third:
        return "Mid"
    return "Late"


def pick_label(season, round_n: int, band: str) -> str:
    year = str(season)
    if round_n >= 3:
        return f"{year} 3rd"
    if round_n == 2:
        try:
            if int(year) >= 2028:
                return f"{year} 2nd"
        except ValueError:
            pass
        return f"{year} {band} 2nd"
    return f"{year} {band} 1st"


def _row_pack(name, pos, team, slug, image, sleeper_id, keep=0, board=0, sf=0, oneqb=0, ppr=0, classic=0):
    return {
        "name": name,
        "pos": pos or "",
        "team": team or "",
        "slug": slug or "",
        "image": image or "",
        "sleeper_id": str(sleeper_id or ""),
        "keep": keep or 0,
        "board": board or 0,
        "sf": sf or 0,
        "oneqb": oneqb or 0,
        "ppr": ppr or 0,
        "classic": classic or 0,
    }


def write_league_lookup(keep, board, ppr, classic, std, waiver, media, updated=""):
    from build_site import DYNASTY_PICKS, norm_name, slugify

    by_key = {}

    def bump(name, pos, team, **fields):
        key = norm_name(name)
        if not key:
            return
        row = by_key.get(key)
        if not row:
            med = media.get(key) or {}
            row = _row_pack(
                name, pos, team,
                med.get("slug") or slugify(name),
                med.get("image") or "",
                med.get("sleeper_id") or "",
            )
            by_key[key] = row
        else:
            if pos and not row["pos"]:
                row["pos"] = pos
            if team and not row["team"]:
                row["team"] = team
        for k, v in fields.items():
            if v:
                row[k] = v

    for r in keep or []:
        rk = r.get("bk") or 0
        pos = r.get("pos") or ""
        sf = r.get("value") or bk_value(rk)
        one = bk_value(rk, QB_1QB_MULT if pos == "QB" else 1.0)
        bump(r.get("name"), pos, r.get("team"), keep=rk, sf=sf, oneqb=one)
    for r in board or []:
        bump(r.get("name"), r.get("pos"), r.get("team"), board=r.get("bk") or 0)
    for r in ppr or []:
        bump(r.get("name"), r.get("pos"), r.get("team"), board=r.get("bk") or 0, ppr=r.get("value") or 0)
    for r in classic or []:
        bump(r.get("name"), r.get("pos"), r.get("team"), classic=r.get("value") or 0)
    for key, med in (media or {}).items():
        if key not in by_key:
            bump(med.get("name") or key, med.get("pos"), med.get("team"))

    by_sleeper = {p["sleeper_id"]: p for p in by_key.values() if p.get("sleeper_id")}
    by_name = {k: p for k, p in by_key.items()}

    picks = []
    for name, rank in DYNASTY_PICKS:
        picks.append({
            "name": name,
            "rank": rank,
            "value": bk_value(rank),
        })

    waivers = []
    for r in (waiver or [])[:40]:
        key = norm_name(r.get("name"))
        pack = by_name.get(key) or {}
        waivers.append({
            "name": r.get("name"),
            "pos": r.get("pos") or pack.get("pos") or "",
            "team": r.get("team") or pack.get("team") or "",
            "slug": pack.get("slug") or "",
            "image": pack.get("image") or "",
            "value": r.get("value") or pack.get("sf") or 0,
        })

    demo = _demo_league(keep, by_name)
    payload = {
        "updated": updated,
        "algorithm": ALGORITHM,
        "bySleeper": by_sleeper,
        "byName": by_name,
        "picks": picks,
        "waiver": waivers,
        "demo": demo,
    }
    path = ROOT / "data/league-lookup.json"
    path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))
    return payload


def _demo_league(keep, by_name):
    from build_site import norm_name

    names = [r["name"] for r in (keep or [])[:120]]
    teams = []
    for i, label in enumerate(DEMO_TEAMS):
        teams.append({
            "id": i + 1,
            "name": label,
            "owner": label,
            "wins": 10 - i if i < 8 else i - 7,
            "losses": i if i < 8 else 17 - i,
            "players": [],
        })
    direction = 1
    seat = 0
    for name in names:
        teams[seat]["players"].append(name)
        seat += direction
        if seat >= len(teams):
            direction = -1
            seat = len(teams) - 1
        elif seat < 0:
            direction = 1
            seat = 0
    for t in teams:
        t["sleeper_ids"] = []
        for name in t["players"]:
            pack = by_name.get(norm_name(name)) or {}
            if pack.get("sleeper_id"):
                t["sleeper_ids"].append(pack["sleeper_id"])
    return {
        "name": "Ball Keep Sample Superflex",
        "season": "2026",
        "kind": "dynasty",
        "scoring": "PPR",
        "superflex": True,
        "teams": teams,
    }


def league_body():
    return """
    <p class="kicker mine-kicker">Yours · Sleeper</p>
    <h1>My Team</h1>
    <p class="note">Put in your Sleeper league ID. Every matched name gets a Keep or Board BK Value. Unranked names are a skip. Dynasty rooms can turn future picks on or off. This browser keeps the IDs you load so they are here next time.</p>
    <form class="league-form" id="league-form" action="league.html" method="get">
      <div class="league-fields" data-pane="sleeper">
        <label for="sleeper-id">Sleeper league ID</label>
        <div class="league-row">
          <input id="sleeper-id" name="sleeper" type="text" inputmode="numeric" autocomplete="off" placeholder="18-digit league ID" />
          <button type="submit" class="cta" data-load="sleeper">Load my team</button>
          <button type="button" class="cta alt" data-demo="1">Sample league</button>
        </div>
        <div id="saved-leagues" class="saved-leagues" hidden></div>
        <p class="note">Find the ID in the Sleeper URL or in league settings. Saved IDs stay on this device. Forget one or forget all from the list.</p>
      </div>
    </form>
    <div id="league-app" class="league-app" hidden></div>
    """


def write_league_page(b, keep, board, ppr, classic, std, waiver, media):
    from build_site import UPDATED

    write_league_lookup(keep, board, ppr, classic, std, waiver, media, UPDATED)
    extra = also_on_desk(b.FB_ALSO.get("league.html") or [])
    body = league_body() + extra
    js = '<script src="js/league.js?v=4" defer></script>'
    b.write(
        "league.html",
        b.page(
            "My Team",
            "league.html",
            body,
            extra_js=js,
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("My Team", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("My Team", "https://ballkeep.com/league.html"),
                ]),
            ],
            body_class="mine-page",
        ),
    )
