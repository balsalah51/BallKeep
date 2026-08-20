"""Ball Keep desk tape of recent Superflex / 1QB packages.

Not a scrape of 200,000 leagues. Packages that moved in public dynasty chats
this month, plus asking prices from the Hot 'n' Cold board. Rank math is
scored at build time against The Board so the blurbs match the calculator.
"""
from __future__ import annotations

# Dates are ISO. Side lists are player names (as on The Board) or pick chips
# that match DYNASTY_PICKS exactly ("2027 Mid 1st", "2028 2nd", …).
DEALS = [
    {
        "date": "2026-08-20",
        "format": "sf",
        "league": "12-team Superflex · start 9",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Josh Allen"],
        "b": ["Jayden Daniels", "2027 Mid 1st", "2028 2nd"],
        "blurb": "Allen still clears Daniels plus a mid-first on our curve. The 2028 second is perfume. If you are trying to win 2026, you keep the 1.01.",
    },
    {
        "date": "2026-08-20",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "r/DynastyFF",
        "kind": "closed",
        "a": ["Drake Maye"],
        "b": ["Joe Burrow", "2027 Late 1st"],
        "blurb": "Maye for Burrow-plus-a-late-first is the age-vs-peak argument in one screenshot. The Keep prefers Maye. The 2026 start/sit prefers Burrow. Pick a window.",
    },
    {
        "date": "2026-08-19",
        "format": "sf",
        "league": "14-team Superflex · TEP",
        "source": "MFL",
        "kind": "closed",
        "a": ["Ja'Marr Chase"],
        "b": ["Puka Nacua", "2027 Early 2nd"],
        "blurb": "Chase still costs more than Puka. The second is how you talk yourself into the gap. We would still rather have the Bengal.",
    },
    {
        "date": "2026-08-19",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Jahmyr Gibbs"],
        "b": ["Bijan Robinson"],
        "blurb": "Straight up, two 24-year-old backs. Gibbs is the one KTC will not stop paying for. Bijan is the one the rest of the industry still ranks higher. This is a vibe trade, not a value trade.",
    },
    {
        "date": "2026-08-19",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Discord SF",
        "kind": "closed",
        "a": ["Jaxon Smith-Njigba"],
        "b": ["Malik Nabers", "2028 3rd"],
        "blurb": "JSN for Nabers is the WR1-or-WR1 argument with a dart attached. The Keep has JSN in the first six. Nabers is the injury-discounted version of the same sentence.",
    },
    {
        "date": "2026-08-18",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "DLF mailbag",
        "kind": "closed",
        "a": ["Justin Jefferson"],
        "b": ["CeeDee Lamb", "2027 Late 2nd"],
        "blurb": "Jefferson still gets the premium. CeeDee plus a late second is how a Cowboys manager stays in the conversation without admitting they lost the name.",
    },
    {
        "date": "2026-08-18",
        "format": "sf",
        "league": "10-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Lamar Jackson", "2027 Mid 2nd"],
        "b": ["Justin Herbert"],
        "blurb": "Herbert for Lamar-plus-a-second is a Superflex QB2 reshuffle. We would rather keep Herbert's five-year passing volume than chase Lamar's weekly ceiling.",
    },
    {
        "date": "2026-08-18",
        "format": "oneqb",
        "league": "12-team 1QB",
        "source": "Sleeper 1QB",
        "kind": "closed",
        "a": ["Bijan Robinson"],
        "b": ["Josh Allen", "2027 Late 1st"],
        "blurb": "1QB is how Allen becomes 'just a quarterback.' Bijan plus a late first for him is the format doing its job. Do not copy this into Superflex and feel clever.",
    },
    {
        "date": "2026-08-17",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sports Arena",
        "kind": "asking",
        "a": ["A.J. Brown"],
        "b": ["Luther Burden III"],
        "blurb": "The Hot/Cold asking price: Brown for Burden straight up. Contender takes the veteran. Rebuild takes the Bear. We already said this on both player pages.",
    },
    {
        "date": "2026-08-17",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sports Arena",
        "kind": "asking",
        "a": ["Christian Watson"],
        "b": ["Makai Lemon"],
        "blurb": "Lemon for Watson is the Cold-board instruction. Philly is a bad place to need year-one volume. Green Bay is a good place to need a WR2 this year.",
    },
    {
        "date": "2026-08-17",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Ashton Jeanty"],
        "b": ["Omarion Hampton", "2027 Mid 1st"],
        "blurb": "Jeanty is the 1.01 running back of the class. Hampton plus a mid-first is a lot of future. We still take the Raider if the question is 'who do I want in 2027.'",
    },
    {
        "date": "2026-08-16",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "r/DynastyFF",
        "kind": "closed",
        "a": ["Brock Bowers"],
        "b": ["Trey McBride", "2027 Early 2nd"],
        "blurb": "Tight end premium leagues will scream. In a normal Superflex, Bowers still costs McBride plus. The second is how you pretend the gap is smaller than it is.",
    },
    {
        "date": "2026-08-16",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Amon-Ra St. Brown"],
        "b": ["Drake London", "2028 3rd"],
        "blurb": "Sun God versus London is a WR2-or-WR1 argument with a throw-in. The Keep has them in the same band. The third is a handshake.",
    },
    {
        "date": "2026-08-16",
        "format": "sf",
        "league": "14-team Superflex",
        "source": "MFL",
        "kind": "closed",
        "a": ["Caleb Williams"],
        "b": ["Brock Purdy", "2027 Mid 1st"],
        "blurb": "Do not trade Maye or Caleb for Purdy because Purdy wins games. Winning games is for real football. Superflex is for five-year windows. This one at least attached a first.",
    },
    {
        "date": "2026-08-15",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "DLF",
        "kind": "closed",
        "a": ["Trevor Lawrence"],
        "b": ["Bo Nix", "2027 Late 2nd"],
        "blurb": "TLaw is on the Hot board because the second-half 2025 tape closed the gap on Mahomes in the QB8 band. Nix-plus-a-second is the 'I don't believe the tape' counter.",
    },
    {
        "date": "2026-08-15",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["De'Von Achane"],
        "b": ["Jonathan Taylor", "2028 2nd"],
        "blurb": "Achane is the explosive one. Taylor is the workhorse. The 2028 second is how a win-now manager justifies moving youth. We would need more than that second.",
    },
    {
        "date": "2026-08-15",
        "format": "oneqb",
        "league": "12-team 1QB · PPR",
        "source": "Sleeper 1QB",
        "kind": "closed",
        "a": ["Jaxon Smith-Njigba"],
        "b": ["Jahmyr Gibbs"],
        "blurb": "1QB is where JSN and Gibbs actually talk. Superflex managers should not screenshot this and send it to their QB-hungry league-mate.",
    },
    {
        "date": "2026-08-14",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Draft Sharks",
        "kind": "asking",
        "a": ["TreVeyon Henderson"],
        "b": ["2027 Late 1st"],
        "blurb": "Sports Arena's buy: Henderson for a projected late 2027 first. Youth plus the Patriots backfield. If that first is really late, we would rather have the back.",
    },
    {
        "date": "2026-08-14",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Christian McCaffrey"],
        "b": ["Breece Hall", "2027 Late 2nd"],
        "blurb": "CMC is a win-now Hot-board name (Sports Arena: PFM RB9 vs ECR RB15). Breece is on Cold. This is a contender stealing a season and donating the name.",
    },
    {
        "date": "2026-08-14",
        "format": "sf",
        "league": "10-team Superflex",
        "source": "r/DynastyFF",
        "kind": "closed",
        "a": ["Patrick Mahomes II"],
        "b": ["Jalen Hurts", "2028 Late 1st"],
        "blurb": "Mahomes is no longer the Superflex 1.01. Hurts plus a late first is how you leave the Chiefs era without looking like you panic-sold. We call it fair-ish.",
    },
    {
        "date": "2026-08-13",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Tetairoa McMillan"],
        "b": ["Emeka Egbuka", "2027 3rd"],
        "blurb": "Two 2025 first-round receivers, one third attached. Tet is the bigger body. Egbuka is the cleaner route tree. The third is a coin.",
    },
    {
        "date": "2026-08-13",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Discord SF",
        "kind": "closed",
        "a": ["Jaxson Dart"],
        "b": ["Jordan Love", "2027 Mid 2nd"],
        "blurb": "Dart is the young Superflex dart (yes). Love is the packed-in QB2. If you already have two starters, Dart is the hold. If you need this year, Love plus the second is the start.",
    },
    {
        "date": "2026-08-13",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["George Pickens"],
        "b": ["Nico Collins"],
        "blurb": "Straight-up WR2s. Pickens is the weekly headache. Nico is the one you actually want to roster on Thursday night. We would need a sweetener to move Nico.",
    },
    {
        "date": "2026-08-12",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "FantasyPros TVC",
        "kind": "closed",
        "a": ["Kyler Murray"],
        "b": ["2027 Mid 1st", "2028 2nd"],
        "blurb": "DLF's Hot note: healthy Kyler was a locked top-10 Superflex QB, currently priced like a mid-first rookie. Two picks for him is the buy the board is screaming.",
    },
    {
        "date": "2026-08-12",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Brian Thomas Jr."],
        "b": ["Garrett Wilson", "2027 Late 2nd"],
        "blurb": "BTJ is Cold because Jakobi Meyers and Parker Washington crowded the targets. Wilson plus a second is selling the name while people still type 'WR2.' That is the instruction.",
    },
    {
        "date": "2026-08-12",
        "format": "oneqb",
        "league": "12-team 1QB",
        "source": "Sleeper 1QB",
        "kind": "closed",
        "a": ["Saquon Barkley"],
        "b": ["Kyren Williams", "2027 Late 1st"],
        "blurb": "Saquon is a 2026 contest. Kyren plus a late first is a 2027 roster. 1QB managers who are not competing should not still be holding Barkley like a religion.",
    },
    {
        "date": "2026-08-11",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sports Arena",
        "kind": "asking",
        "a": ["Zay Flowers"],
        "b": ["Rashee Rice"],
        "blurb": "Flowers is Hot (new contract, 1,200 yards on a run-heavy script). Rice is Cold (Chiefs look run-leaning). Same band, opposite instructions. We take Flowers.",
    },
    {
        "date": "2026-08-11",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Colston Loveland"],
        "b": ["Tyler Warren"],
        "blurb": "Two rookie tight ends, one city each. Loveland has Caleb. Warren has the Colts volume bet. Straight up is how you admit you do not know which TE hits first.",
    },
    {
        "date": "2026-08-11",
        "format": "sf",
        "league": "14-team Superflex",
        "source": "MFL",
        "kind": "closed",
        "a": ["Jeremiyah Love"],
        "b": ["Quinshon Judkins", "2027 Early 2nd"],
        "blurb": "Love is the rookie back Superflex managers keep reaching for. Judkins plus an early second is a lot of RB. We still want the Notre Dame kid if the question is 2028.",
    },
    {
        "date": "2026-08-10",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Tee Higgins"],
        "b": ["DeVonta Smith", "2028 3rd"],
        "blurb": "Higgins versus Smitty is two WR2s with different quarterbacks. The third is a courtesy. We would rather have the one who is not sharing a building with Chase — wait, that is Smith. Take Smith.",
    },
    {
        "date": "2026-08-10",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "r/DynastyFF",
        "kind": "closed",
        "a": ["Ladd McConkey"],
        "b": ["Chris Olave"],
        "blurb": "Ladd is the cleaner 2026 bet. Olave is the name. Straight up, the desk takes the Charger and does not apologize.",
    },
    {
        "date": "2026-08-10",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Dak Prescott"],
        "b": ["Baker Mayfield", "2027 3rd"],
        "blurb": "Two QB2s in Superflex. Dak is the contract. Baker is the one who keeps finishing as a QB1. The third is how Dallas managers save face.",
    },
    {
        "date": "2026-08-09",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Fantasy Footballers",
        "kind": "asking",
        "a": ["Davante Adams"],
        "b": ["Jaylen Waddle"],
        "blurb": "Adams is Cold: 33, coming off a 14-TD outlier. Waddle is the younger name. If a contender still pays WR2 money for Adams, cash it for Waddle and a nap.",
    },
    {
        "date": "2026-08-09",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Marvin Harrison Jr."],
        "b": ["Rome Odunze", "2027 Late 2nd"],
        "blurb": "MHJ is the former 1.01 who no longer prices like one. Odunze plus a second is the 'I still believe in the Cardinal' tax. We would rather have the second and the Bear.",
    },
    {
        "date": "2026-08-08",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Draft Sharks",
        "kind": "closed",
        "a": ["Jordan Mason"],
        "b": ["D'Andre Swift", "2028 3rd"],
        "blurb": "Mason is Hot: cheap potential starter in Minnesota. Swift is a name. The third is a shrug. Buy Mason before a spike week, which is the whole point of a Hot board.",
    },
    {
        "date": "2026-08-08",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Harold Fannin Jr."],
        "b": ["Tucker Kraft"],
        "blurb": "Two tight ends the desk likes. Fannin is the FBS-leading rookie on a TE-maven staff. Kraft is the 25-year-old who looked top-4 before the ACL. Straight up is a coin we would flip toward Kraft's tape.",
    },
    {
        "date": "2026-08-07",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["James Cook III"],
        "b": ["Kenneth Walker III", "2027 Late 2nd"],
        "blurb": "Cook is climbing boards. KW3 is the other back in the same sentence. The late second is how Seattle managers stay in it. We would still want Cook.",
    },
    {
        "date": "2026-08-07",
        "format": "oneqb",
        "league": "12-team 1QB",
        "source": "Sleeper 1QB",
        "kind": "closed",
        "a": ["Puka Nacua"],
        "b": ["Caleb Williams", "2028 2nd"],
        "blurb": "1QB is where a WR1 beats a young quarterback plus a second. Copy this into Superflex and you have donated a franchise.",
    },
    {
        "date": "2026-08-06",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "r/DynastyFF",
        "kind": "closed",
        "a": ["C.J. Stroud"],
        "b": ["Jared Goff", "2027 Early 2nd"],
        "blurb": "Stroud is the hold. Goff is the 2025 start. The early second is how a contender tries to buy a season. We would not sell the Texans kid for that.",
    },
    {
        "date": "2026-08-06",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Bucky Irving"],
        "b": ["Cam Skattebo", "2028 3rd"],
        "blurb": "Two young backs, one third. Bucky has the job. Skattebo has the landing-spot conversation. We take the Buc.",
    },
    {
        "date": "2026-08-05",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "FantasyPros",
        "kind": "asking",
        "a": ["Ricky Pearsall"],
        "b": ["2027 Late 1st"],
        "blurb": "Pearsall is Cold: out until about next September, age 27 on return. A late first is the sell. If someone is still paying mid-first, take it twice.",
    },
    {
        "date": "2026-08-05",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Josh Jacobs"],
        "b": ["Javonte Williams"],
        "blurb": "Jacobs is the veteran volume. Javonte is the hope. Straight up, the desk takes the Packer and lets someone else write the comeback story.",
    },
    {
        "date": "2026-08-04",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "Sleeper SF",
        "kind": "closed",
        "a": ["Fernando Mendoza"],
        "b": ["Carnell Tate", "2027 3rd"],
        "blurb": "Rookie quarterback versus rookie receiver plus a third. Superflex takes the passer. Every time. The third is how WR managers sleep.",
    },
    {
        "date": "2026-08-04",
        "format": "sf",
        "league": "12-team Superflex",
        "source": "DLF",
        "kind": "closed",
        "a": ["DJ Moore"],
        "b": ["Terry McLaurin", "2028 3rd"],
        "blurb": "Moore is Cold: 29, new team in Buffalo, 60-790 last year. McLaurin is Scary Terry still doing Scary Terry things. Sell the name, keep the one who is still a WR2.",
    },
]


def enrich_deals(board, bk_value, pick_rows, norm_name):
    """Score each deal against The Board / pick chips. Drop nothing; warn on misses."""
    by_key = {r["key"]: r for r in board}
    pick_map = {p["name"]: p for p in pick_rows}
    out = []
    missing = []
    for i, raw in enumerate(DEALS, 1):
        qb_mult = 0.38 if raw["format"] == "oneqb" else 1.0

        def resolve(token):
            if token in pick_map:
                p = pick_map[token]
                return {
                    "name": p["name"],
                    "pos": "PICK",
                    "team": "",
                    "value": int(p["value"]),
                    "kind": "pick",
                    "rank": p.get("rank"),
                }
            row = by_key.get(norm_name(token))
            if not row:
                missing.append(token)
                return {
                    "name": token,
                    "pos": "",
                    "team": "",
                    "value": 0,
                    "kind": "missing",
                    "rank": None,
                }
            mult = qb_mult if row.get("pos") == "QB" else 1.0
            val = row.get("value") if qb_mult == 1.0 else bk_value(row.get("bk") or 0, mult)
            return {
                "name": row["name"],
                "pos": row.get("pos") or "",
                "team": row.get("team") or "",
                "value": int(val or 0),
                "kind": "player",
                "rank": row.get("bk"),
            }

        a = [resolve(x) for x in raw["a"]]
        b = [resolve(x) for x in raw["b"]]
        ta = sum(x["value"] for x in a)
        tb = sum(x["value"] for x in b)
        diff = ta - tb
        bigger = max(ta, tb, 1)
        pct = abs(diff) / bigger
        if ta and tb and pct > 0.08:
            label = "Side A Wins" if diff > 0 else "Side B Wins"
        else:
            label = "Fair Trade"
        names = [x["name"] for x in a + b]
        iso = raw["date"]
        pretty = _pretty_date(iso)
        out.append({
            "id": f"deal-{i}",
            "date": pretty,
            "date_iso": iso,
            "format": "Superflex" if raw["format"] == "sf" else "1QB",
            "format_id": raw["format"],
            "league": raw["league"],
            "source": raw["source"],
            "kind": raw["kind"],
            "a": a,
            "b": b,
            "total_a": ta,
            "total_b": tb,
            "diff": diff,
            "label": label,
            "blurb": raw["blurb"],
            "names": names,
            "hay": " ".join(names).lower(),
        })
    if missing:
        uniq = sorted(set(missing))
        print("recent-trades missing names:", ", ".join(uniq))
    return out


def _pretty_date(iso: str) -> str:
    y, m, d = iso.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(m) - 1]} {int(d)}, {y}"
