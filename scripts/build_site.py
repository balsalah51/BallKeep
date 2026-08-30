#!/usr/bin/env python3
"""Build the BallKeep static site from scraped ranking and schedule sources."""
from __future__ import annotations

import html
import json
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "August 28, 2026"
LASTMOD = "2026-08-28"
KEEP_N = 400
BOARD_N = 500
PPR_N = 200
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_curve import ALGORITHM, bk_value  # noqa: E402
from extra_ranks import (  # noqa: E402
    DRAFT_SHARKS_SF,
    ESPN_KARABELL_FLEX,
    ESPN_KARABELL_SF,
    ROTOWIRE_SF,
    as_ranks,
)
from ppr_boards import PPR_EXTRA_SOURCES, extra_ppr_maps, _norm as ppr_norm  # noqa: E402
from aggregate_protocol import (  # noqa: E402
    KEEP_SOURCES,
    LONG_CORE,
    expand_super_desks,
    rank_rows,
)
from seo import (  # noqa: E402
    abs_img,
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
    canon,
    card_alt,
    clip,
    draft_check_js,
    face_alt,
    faq_html,
    faq_jsonld,
    footer_nav,
    head_tags,
    legal_links,
    news_sitemap_xml,
    person_jsonld,
    rank_list_jsonld,
    rank_search_bar,
    rank_search_key,
    rank_spread_graph,
    related_players_html,
    related_stories_html,
    robots_txt,
    rss_xml,
    sitemap_xml,
    sports_footer,
    sports_top,
    strip_em,
    value_bars,
    video_jsonld,
    website_jsonld,
)
from news_algo import CATEGORY_LABEL, load_news_stories, news_when  # noqa: E402
from x_tape import cards_html as x_cards  # noqa: E402
from player_copy import get_copy  # noqa: E402
from recent_trades import enrich_deals  # noqa: E402
from build_bb import write_baseball_site  # noqa: E402
from build_bk import write_basket_site  # noqa: E402
from build_pl import write_pitch_site  # noqa: E402


def esc(s):
    return html.escape(str(s), quote=True)


def pos_filter(box_id):
    """QB / RB / WR / TE chips. Works with applyRankFilter on ranking tables."""
    chips = (
        f'<div class="filters" id="{box_id}">'
        '<button type="button" class="active" data-pos="all">All</button>'
        '<button type="button" data-pos="QB">QB</button>'
        '<button type="button" data-pos="RB">RB</button>'
        '<button type="button" data-pos="WR">WR</button>'
        '<button type="button" data-pos="TE">TE</button>'
        "</div>"
    )
    js = f"""<script>
    const box = document.getElementById({box_id!r});
    if (box) box.addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      if (window.applyRankFilter) applyRankFilter();
    }});
    </script>"""
    return chips, js


def desk_block(kind, kicker, heading, note, tiles, extra=""):
    cards = "".join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h, t, p in tiles)
    cols = "grid" if len(tiles) <= 2 else "grid-3"
    return (
        f'<section class="desk-block {kind}">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f"<h2>{esc(heading)}</h2>"
        f'<p class="note">{note}</p>'
        f'<div class="{cols}">{cards}</div>'
        f"{extra}"
        "</section>"
    )


def norm_name(name: str) -> str:
    n = name.lower()
    n = n.replace(".", " ")
    n = re.sub(r"\b(jr|sr|iii|ii|iv)\b", "", n)
    n = n.replace("'", "").replace("’", "")
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "patrick mahomes ii": "patrick mahomes",
        "james cook iii": "james cook",
        "kenneth walker iii": "kenneth walker",
        "luther burden iii": "luther burden",
        "brian thomas jr": "brian thomas",
        "omar cooper jr": "omar cooper",
        "marvin harrison jr": "marvin harrison",
        "michael pittman jr": "michael pittman",
        "kyle pitts sr": "kyle pitts",
        "chris godwin jr": "chris godwin",
        "travis etienne jr": "travis etienne",
        "dandre swift": "dandre swift",
        "d'andre swift": "dandre swift",
        "devon achane": "devon achane",
        "de'von achane": "devon achane",
        "amon ra st brown": "amon-ra st brown",
        "amon-ra st. brown": "amon-ra st brown",
        "ja marr chase": "jamarr chase",
        "jamarr chase": "jamarr chase",
        "nicholas singleton": "nick singleton",
        "nick singleton": "nick singleton",
        "harold fannin jr": "harold fannin",
        "deebo samuel sr": "deebo samuel",
        "aaron jones sr": "aaron jones",
    }
    return aliases.get(n, n)


TEAMS = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS",
}
TEAM_BY_ABBR = {v: k for k, v in TEAMS.items()}


def load_rank_names(stem: str) -> dict:
    """Ordered public board dumped by scripts/refresh_ranks.py (name -> rank)."""
    path = ROOT / "data" / "ranks" / f"{stem}.json"
    if not path.exists():
        return {}
    names = json.loads(path.read_text())
    out = {}
    for i, name in enumerate(names, 1):
        if isinstance(name, str) and name.strip():
            out[name] = i
    return out


def parse_pfn(path: Path):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(QB|RB|WR|TE)\s*\|\s*([A-Z]{2,3})\s*\|\s*(\d+)\s*\|",
            line,
        )
        if not m:
            continue
        rows.append({
            "rank": int(m.group(1)),
            "name": html.unescape(m.group(2).strip()),
            "pos": m.group(3),
            "team": m.group(4).replace("GBP", "GB").replace("KCC", "KC").replace("NOS", "NO").replace("SFO", "SF").replace("LVR", "LV").replace("NEP", "NE"),
            "age": int(m.group(5)),
        })
    # keep first occurrence (best overall rank)
    seen = set()
    out = []
    for r in rows:
        k = norm_name(r["name"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def parse_nfl_schedule(path: Path):
    games = []
    week = None
    day = ""
    for line in path.read_text(errors="replace").splitlines():
        wm = re.match(r"WEEK\s+(\d+)", line.strip(), re.I)
        if wm:
            week = int(wm.group(1))
            continue
        dm = re.match(
            r"(Wednesday|Thursday|Friday|Saturday|Sunday|Monday|Date TBD),?\s*(.*)",
            line.strip(),
        )
        if dm and week:
            day = line.strip()
            continue
        gm = re.match(r"\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if not gm or week is None:
            continue
        matchup = gm.group(1).strip()
        time = gm.group(2).strip()
        tv = gm.group(3).strip().rstrip("*")
        if matchup in ("Matchup", "TBD") or "---" in matchup:
            continue
        loc = ""
        mm = re.match(r"(.+?)\s+(at|vs)\s+(.+?)(?:\s+\((.+)\))?$", matchup)
        if not mm:
            continue
        left, prep, right, loc = mm.group(1).strip(), mm.group(2), mm.group(3).strip(), mm.group(4) or ""
        if left not in TEAMS or right not in TEAMS:
            continue
        away, home = (left, right) if prep == "at" else (left, right)
        games.append({
            "week": week, "day": day, "away": away, "home": home,
            "prep": prep, "time": time, "tv": tv, "note": loc,
        })
    # de-dupe (file repeats week 7)
    uniq = []
    seen = set()
    for g in games:
        key = (g["week"], g["away"], g["home"], g["time"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(g)
    return uniq


# --- additional scraped source ranks (name -> rank) ---
FANTASYPROS_SF = {
    "Drake Maye": 1, "Josh Allen": 2, "Ja'Marr Chase": 3, "Jaxon Smith-Njigba": 4,
    "Bijan Robinson": 5, "Jayden Daniels": 6, "Jahmyr Gibbs": 7, "Puka Nacua": 8,
    "Jalen Hurts": 9, "Lamar Jackson": 10, "Justin Herbert": 11, "Ashton Jeanty": 12,
}
FP_EXPERTS = {
    "Derek Brown (X)": {
        "Josh Allen": 1, "Drake Maye": 2, "Jalen Hurts": 3, "Ja'Marr Chase": 4,
        "Jaxon Smith-Njigba": 5, "Jahmyr Gibbs": 6, "Bijan Robinson": 7, "Puka Nacua": 8,
        "Ashton Jeanty": 11, "Jayden Daniels": 23, "Justin Herbert": 26, "Lamar Jackson": 27,
    },
    "Andrew Erickson (X)": {
        "Drake Maye": 1, "Jayden Daniels": 2, "Josh Allen": 3, "Lamar Jackson": 4,
        "Justin Herbert": 5, "Ja'Marr Chase": 8, "Jaxon Smith-Njigba": 9, "Bijan Robinson": 10,
        "Jalen Hurts": 14, "Jahmyr Gibbs": 16, "Puka Nacua": 18, "Ashton Jeanty": 22,
    },
    "Pat Fitzmaurice (X)": {
        "Drake Maye": 1, "Josh Allen": 2, "Jayden Daniels": 3, "Ja'Marr Chase": 5,
        "Lamar Jackson": 6, "Bijan Robinson": 7, "Jahmyr Gibbs": 8, "Puka Nacua": 9,
        "Jaxon Smith-Njigba": 10, "Justin Herbert": 12, "Ashton Jeanty": 13, "Jalen Hurts": 19,
    },
}
DYNASTY_NERDS = {
    "Josh Allen": 1, "Bijan Robinson": 2, "Drake Maye": 3, "Ja'Marr Chase": 4,
    "Jahmyr Gibbs": 5, "Jaxon Smith-Njigba": 6, "Puka Nacua": 7, "Caleb Williams": 8,
    "Jayden Daniels": 9, "Ashton Jeanty": 10, "Brock Bowers": 11, "Justin Jefferson": 12,
    "De'Von Achane": 13, "CeeDee Lamb": 14, "Amon-Ra St. Brown": 15, "Malik Nabers": 16,
    "Joe Burrow": 17, "Jeremiyah Love": 18, "Lamar Jackson": 19, "Patrick Mahomes": 20,
    "Omarion Hampton": 21, "Justin Herbert": 22, "Trey McBride": 23, "Jaxson Dart": 24,
    "Drake London": 25, "Jalen Hurts": 26, "Tetairoa McMillan": 27, "Trevor Lawrence": 28,
    "Emeka Egbuka": 29, "Jonathan Taylor": 30, "James Cook": 31, "Garrett Wilson": 32,
    "George Pickens": 33, "Brock Purdy": 34, "Bo Nix": 35, "Carnell Tate": 36,
    "Colston Loveland": 37, "Breece Hall": 38, "Ladd McConkey": 39, "Jordan Love": 40,
    "Tyler Warren": 41, "Nico Collins": 42, "Kenneth Walker": 43, "Quinshon Judkins": 44,
    "Chris Olave": 45, "TreVeyon Henderson": 46, "Fernando Mendoza": 47, "Rome Odunze": 48,
    "Marvin Harrison": 49, "Dak Prescott": 50, "Christian McCaffrey": 51, "Brian Thomas": 52,
    "Zay Flowers": 53, "Jordyn Tyson": 54, "Luther Burden": 55, "Makai Lemon": 56,
    "Baker Mayfield": 57, "Chase Brown": 58, "Saquon Barkley": 59, "A.J. Brown": 60,
    "Tee Higgins": 61, "Jared Goff": 62, "Rashee Rice": 63, "Javonte Williams": 64,
    "DeVonta Smith": 65, "Cam Skattebo": 66, "Jaylen Waddle": 67, "Kyren Williams": 68,
    "Cam Ward": 69, "Jadarian Price": 70, "Bucky Irving": 71, "KC Concepcion": 72,
    "Kyle Pitts": 73, "Tucker Kraft": 74, "Jameson Williams": 75, "Harold Fannin": 76,
    "Josh Jacobs": 77, "Travis Etienne": 78, "Sam Darnold": 79, "C.J. Stroud": 80,
    "Kyler Murray": 81, "Christian Watson": 82, "Sam LaPorta": 83, "Bhayshul Tuten": 84,
    "DJ Moore": 85, "Jordan Addison": 86, "Tyler Shough": 87, "Malik Willis": 88,
    "Daniel Jones": 89, "Alec Pierce": 90, "D'Andre Swift": 91, "Omar Cooper": 92,
    "Denzel Boston": 93, "Michael Wilson": 94, "Terry McLaurin": 95, "Ty Simpson": 96,
    "Parker Washington": 97, "Matthew Stafford": 98, "Derrick Henry": 99, "Kenyon Sadiq": 100,
}
KTC_SF = {
    "Jahmyr Gibbs": 1, "Ja'Marr Chase": 2, "Bijan Robinson": 3, "Josh Allen": 4,
    "Jaxon Smith-Njigba": 5, "Drake Maye": 6, "Puka Nacua": 7, "Brock Bowers": 8,
    "Amon-Ra St. Brown": 9, "Caleb Williams": 10, "Lamar Jackson": 11, "Ashton Jeanty": 12,
    "Jeremiyah Love": 13, "Justin Jefferson": 14, "Malik Nabers": 15, "Joe Burrow": 16,
    "Jayden Daniels": 17, "Trey McBride": 18, "CeeDee Lamb": 19, "De'Von Achane": 20,
    "Omarion Hampton": 22, "Justin Herbert": 23, "Drake London": 24, "Jonathan Taylor": 25,
    "Jalen Hurts": 26, "Tetairoa McMillan": 27, "Emeka Egbuka": 28, "Colston Loveland": 29,
    "Patrick Mahomes": 30, "Bo Nix": 31, "George Pickens": 32, "Tyler Warren": 33,
    "Jaxson Dart": 36, "Carnell Tate": 37, "Nico Collins": 38, "Chris Olave": 39,
    "Brock Purdy": 40, "Chase Brown": 41, "Kenneth Walker": 42, "Rome Odunze": 43,
    "Garrett Wilson": 44, "Luther Burden": 47, "Ladd McConkey": 48, "A.J. Brown": 49,
    "Fernando Mendoza": 50,
}
YATES_PPR = [
    ("Bijan Robinson", "RB", "ATL"), ("Jahmyr Gibbs", "RB", "DET"), ("Christian McCaffrey", "RB", "SF"),
    ("Ja'Marr Chase", "WR", "CIN"), ("Puka Nacua", "WR", "LAR"), ("Jaxon Smith-Njigba", "WR", "SEA"),
    ("Jonathan Taylor", "RB", "IND"), ("De'Von Achane", "RB", "MIA"), ("Amon-Ra St. Brown", "WR", "DET"),
    ("James Cook", "RB", "BUF"), ("Derrick Henry", "RB", "BAL"), ("Justin Jefferson", "WR", "MIN"),
    ("CeeDee Lamb", "WR", "DAL"), ("Chase Brown", "RB", "CIN"), ("Kenneth Walker", "RB", "KC"),
    ("Trey McBride", "TE", "ARI"), ("Drake London", "WR", "ATL"), ("Brock Bowers", "TE", "LV"),
    ("Rashee Rice", "WR", "KC"), ("Josh Jacobs", "RB", "GB"), ("Jeremiyah Love", "RB", "ARI"),
    ("Saquon Barkley", "RB", "PHI"), ("Ashton Jeanty", "RB", "LV"), ("Omarion Hampton", "RB", "LAC"),
    ("Malik Nabers", "WR", "NYG"), ("A.J. Brown", "WR", "NE"), ("Chris Olave", "WR", "NO"),
    ("Josh Allen", "QB", "BUF"), ("George Pickens", "WR", "DAL"), ("Javonte Williams", "RB", "DAL"),
    ("Breece Hall", "RB", "NYJ"), ("Kyren Williams", "RB", "LAR"), ("Emeka Egbuka", "WR", "TB"),
    ("Garrett Wilson", "WR", "NYJ"), ("Colston Loveland", "TE", "CHI"), ("Lamar Jackson", "QB", "BAL"),
    ("Travis Etienne", "RB", "NO"), ("Cam Skattebo", "RB", "NYG"), ("Nico Collins", "WR", "HOU"),
    ("Jayden Daniels", "QB", "WAS"), ("Zay Flowers", "WR", "BAL"), ("Tetairoa McMillan", "WR", "CAR"),
    ("DeVonta Smith", "WR", "PHI"), ("Jaylen Waddle", "WR", "DEN"), ("Quinshon Judkins", "RB", "CLE"),
    ("Tyler Warren", "TE", "IND"), ("D'Andre Swift", "RB", "CHI"), ("Drake Maye", "QB", "NE"),
    ("Bucky Irving", "RB", "TB"), ("Davante Adams", "WR", "LAR"), ("Ladd McConkey", "WR", "LAC"),
    ("Jalen Hurts", "QB", "PHI"), ("Harold Fannin", "TE", "CLE"), ("Bhayshul Tuten", "RB", "JAX"),
    ("Chuba Hubbard", "RB", "CAR"), ("Jadarian Price", "RB", "SEA"), ("Tee Higgins", "WR", "CIN"),
    ("Kyle Pitts", "TE", "ATL"), ("Justin Herbert", "QB", "LAC"), ("Terry McLaurin", "WR", "WAS"),
    ("Carnell Tate", "WR", "TEN"), ("David Montgomery", "RB", "HOU"), ("Tony Pollard", "RB", "TEN"),
    ("George Kittle", "TE", "SF"), ("Rhamondre Stevenson", "RB", "NE"), ("TreVeyon Henderson", "RB", "NE"),
    ("Rome Odunze", "WR", "CHI"), ("DK Metcalf", "WR", "PIT"), ("Kenneth Gainwell", "RB", "TB"),
    ("Jaxson Dart", "QB", "NYG"), ("Jaylen Warren", "RB", "PIT"), ("DJ Moore", "WR", "BUF"),
    ("Joe Burrow", "QB", "CIN"), ("Marvin Harrison", "WR", "ARI"), ("Trevor Lawrence", "QB", "JAX"),
    ("Christian Watson", "WR", "GB"), ("Luther Burden", "WR", "CHI"), ("Jameson Williams", "WR", "DET"),
    ("Wan'Dale Robinson", "WR", "TEN"), ("Stefon Diggs", "WR", "WAS"), ("Rachaad White", "RB", "WAS"),
    ("Sam LaPorta", "TE", "DET"), ("Aaron Jones", "RB", "MIN"), ("Michael Wilson", "WR", "ARI"),
    ("Mike Evans", "WR", "SF"), ("Courtland Sutton", "WR", "DEN"), ("Michael Pittman", "WR", "PIT"),
    ("Tucker Kraft", "TE", "GB"), ("Dak Prescott", "QB", "DAL"), ("Patrick Mahomes", "QB", "KC"),
    ("Jakobi Meyers", "WR", "JAX"), ("Jake Ferguson", "TE", "DAL"), ("Chris Godwin", "WR", "TB"),
    ("Dallas Goedert", "TE", "PHI"), ("Kyle Monangai", "RB", "CHI"), ("Brock Purdy", "QB", "SF"),
    ("Matthew Stafford", "QB", "LAR"), ("Bo Nix", "QB", "DEN"), ("Travis Kelce", "TE", "KC"),
    ("J.K. Dobbins", "RB", "DEN"),
]
FP_PPR = {"Ja'Marr Chase": 1, "Jahmyr Gibbs": 2, "Puka Nacua": 3, "Bijan Robinson": 4, "Jaxon Smith-Njigba": 5}

ROOKIES = [
    {"name": "Jeremiyah Love", "pos": "RB", "team": "ARI", "dd": 1, "fp": 1, "pff": 1, "value": "Locked 1.01 · elite RB1 capital"},
    {"name": "Fernando Mendoza", "pos": "QB", "team": "LV", "dd": 2, "fp": 2, "pff": 2, "value": "Clear 1.02 in Superflex · sit-behind-Cousins year-one risk"},
    {"name": "Carnell Tate", "pos": "WR", "team": "TEN", "dd": 3, "fp": 3, "pff": 3, "value": "Safest WR · Day-1 starter with Ward"},
    {"name": "Jordyn Tyson", "pos": "WR", "team": "NO", "dd": 4, "fp": 5, "pff": 5, "value": "Early/mid 1st · Saints volume bet"},
    {"name": "Makai Lemon", "pos": "WR", "team": "PHI", "dd": 5, "fp": 6, "pff": 6, "value": "Mid 1st · crowded Philly room, talent is real"},
    {"name": "Jadarian Price", "pos": "RB", "team": "SEA", "dd": 6, "fp": 4, "pff": 4, "value": "Riser after draft · projected Seattle volume"},
    {"name": "KC Concepcion", "pos": "WR", "team": "CLE", "dd": 7, "fp": 8, "pff": None, "value": "Mid/late 1st · Jeanty-adjacent profile in comments"},
    {"name": "Ty Simpson", "pos": "QB", "team": "LAR", "dd": 11, "fp": 7, "pff": None, "value": "SF-only first · McVay development path"},
    {"name": "Kenyon Sadiq", "pos": "TE", "team": "NYJ", "dd": 8, "fp": 9, "pff": None, "value": "Late 1st TE1 of the class"},
    {"name": "Eli Stowers", "pos": "TE", "team": "PHI", "dd": 9, "fp": 11, "pff": None, "value": "Late 1st / early 2nd TE"},
    {"name": "Omar Cooper", "pos": "WR", "team": "NYJ", "dd": 10, "fp": 10, "pff": None, "value": "Turn-of-1st WR flyer"},
    {"name": "Jonah Coleman", "pos": "RB", "team": "DEN", "dd": 14, "fp": 10, "pff": None, "value": "Early 2nd · Denver committee"},
    {"name": "Denzel Boston", "pos": "WR", "team": "CLE", "dd": 12, "fp": 12, "pff": None, "value": "Early/mid 2nd"},
    {"name": "Antonio Williams", "pos": "WR", "team": "WAS", "dd": 13, "fp": None, "pff": None, "value": "Mid 2nd"},
    {"name": "Nick Singleton", "pos": "RB", "team": "TEN", "dd": 18, "fp": None, "pff": None, "value": "Mid 2nd committee back"},
    {"name": "Germie Bernard", "pos": "WR", "team": "PIT", "dd": 15, "fp": None, "pff": None, "value": "Mid 2nd"},
    {"name": "Chris Bell", "pos": "WR", "team": "MIA", "dd": 16, "fp": None, "pff": None, "value": "Mid/late 2nd"},
    {"name": "De'Zhaun Stribling", "pos": "WR", "team": "SF", "dd": 17, "fp": None, "pff": None, "value": "Late 2nd"},
    {"name": "Carson Beck", "pos": "QB", "team": "ARI", "dd": None, "fp": 19, "pff": None, "value": "Volatile SF 2nd/3rd · high STD DEV"},
    {"name": "Kaytron Allen", "pos": "RB", "team": "WAS", "dd": None, "fp": None, "pff": None, "value": "Day 3 / 3rd-round dart"},
]

HOT = [
    {"name": "De'Zhaun Stribling", "pos": "WR", "team": "SF", "why": "SI (Aug 25) + FantasyPros (Aug 26): 13 targets, 11-109 in his first two preseason games. Pearsall is out on a PCL; Shanahan is moving him all over the formation.", "src": "Sports Illustrated, FantasyPros"},
    {"name": "Jonah Coleman", "pos": "RB", "team": "DEN", "why": "SI (Aug 25) + FantasyPros: Payton pulled him after one preseason series because he'd already seen enough. Pass-pro trust is the three-down unlock in Denver.", "src": "Sports Illustrated, FantasyPros"},
    {"name": "Parker Washington", "pos": "WR", "team": "JAX", "why": "SI (Aug 25): WR8 over the last five weeks of 2025. Jacksonville is manufacturing touches in space; he is no longer a depth piece.", "src": "Sports Illustrated"},
    {"name": "Rome Odunze", "pos": "WR", "team": "CHI", "why": "PlayerProfiler (Aug 7): cheapest Chicago WR after the Burden/Loveland run-up. WR11 Weeks 1–8 last year before the foot; PP WR19 vs KTC WR20.", "src": "PlayerProfiler"},
    {"name": "Kyle Pitts", "pos": "TE", "team": "ATL", "why": "PlayerProfiler: TE2 finish last year, Stefanski TE volume, still 25. KTC TE8 is a discount on a name who just got paid through 2028.", "src": "PlayerProfiler"},
    {"name": "Zay Flowers", "pos": "WR", "team": "BAL", "why": "PlayerProfiler would take him straight up over KTC WR14 Ladd McConkey. New contract, 1,200 yards on a run-leaning Ravens offense.", "src": "PlayerProfiler"},
    {"name": "Bryce Lance", "pos": "WR", "team": "NO", "why": "SI (Aug 25): Tyson is expected to miss time; Lance went 5-5-2 in joint practice with Shough. Deep-bench buy before the Saints room fills back in.", "src": "Sports Illustrated"},
    {"name": "Jelani Woods", "pos": "TE", "team": "NYJ", "why": "SI (Aug 25): healthier camp, elevated preseason reps, empty middle of the Jets offense. Reclamation TE with size/speed and a clean runway.", "src": "Sports Illustrated"},
    {"name": "Christian Watson", "pos": "WR", "team": "GB", "why": "Sports Arena + Draft Sharks: WR21 in FPPG Weeks 8–18 last year on a 68% route share with Doubs/Wicks gone. Still the buy vs. packed rookie rooms.", "src": "Sports Arena, Draft Sharks"},
    {"name": "Kyler Murray", "pos": "QB", "team": "MIN", "why": "DLF: healthy years were locked top-10 SF QBs; still priced like a mid-1st rookie pick heading into Week 1 in Minnesota.", "src": "Dynasty League Football"},
]
COLD = [
    {"name": "TreVeyon Henderson", "pos": "RB", "team": "NE", "why": "The Athletic (Aug 26): ADP RB12, ranked RB16. Stevenson still has the job; sell the camp premium before a quiet September.", "src": "The Athletic"},
    {"name": "Ladd McConkey", "pos": "WR", "team": "LAC", "why": "PlayerProfiler (Aug 7): KTC WR14 is a ceiling smash. Year-2 dip, McDaniel 12-personnel, Njoku in the building. Flowers/Olave/Smith are the ask.", "src": "PlayerProfiler"},
    {"name": "Jonathan Taylor", "pos": "RB", "team": "IND", "why": "PlayerProfiler: 27, last look at peak. Age-28 lead backs lose ~41% of peak PPR. Contenders hold; everyone else moves him a year early.", "src": "PlayerProfiler"},
    {"name": "Kyren Williams", "pos": "RB", "team": "LAR", "why": "FantasyPros (August): Corum's role keeps growing, Williams turns 26, 2027 cap-cut candidate. Sell the name equity to a contender.", "src": "FantasyPros"},
    {"name": "Kenneth Walker", "pos": "RB", "team": "KC", "why": "FantasyPros (August): Super Bowl MVP + Chiefs lead-back hype is peak value. Durability and a receiving back in the room say timeshare.", "src": "FantasyPros"},
    {"name": "Carnell Tate", "pos": "WR", "team": "TEN", "why": "FantasyPros (Aug 9): dynasty ECR WR14. Titans OL ranked 31st and he was never a 900-yard college WR. Sell the rookie-class premium.", "src": "FantasyPros"},
    {"name": "Ricky Pearsall", "pos": "WR", "team": "SF", "why": "FantasyPros: season-ending PCL, age 27 on return. Clear sell for win-now clubs; the 49ers room already moved on to Stribling.", "src": "FantasyPros"},
    {"name": "RJ Harvey", "pos": "RB", "team": "DEN", "why": "Draft Sharks + SI: Dobbins is back and Coleman just won Payton's trust. Not a locked lead back.", "src": "Draft Sharks, Sports Illustrated"},
    {"name": "Brian Thomas Jr.", "pos": "WR", "team": "JAX", "why": "DLF + SI: Parker Washington is now a foundational piece. ADP still treats BTJ like a locked high WR2.", "src": "DLF, Sports Illustrated"},
    {"name": "Davante Adams", "pos": "WR", "team": "LAR", "why": "The Athletic: 33-year-old coming off a 14-TD outlier. If you roster him, cash to a contender before Week 1.", "src": "The Athletic"},
]


def meta_map(pfn_rows):
    m = {}
    for r in pfn_rows:
        m[norm_name(r["name"])] = r
    return m


def fmt_val(n: int) -> str:
    return f"{int(n):,}"


def attach_values(rows, qb_mult_for_qb: float = 1.0):
    for r in rows:
        mult = qb_mult_for_qb if r.get("pos") == "QB" else 1.0
        r["value"] = bk_value(r.get("bk") or 0, mult)
    return rows


# Future firsts priced as equivalent ranks on the Superflex curve.
DYNASTY_PICKS = [
    ("2027 Early 1st", 8),
    ("2027 Mid 1st", 18),
    ("2027 Late 1st", 28),
    ("2027 Early 2nd", 36),
    ("2027 Mid 2nd", 44),
    ("2027 Late 2nd", 52),
    ("2027 3rd", 68),
    ("2028 Early 1st", 16),
    ("2028 Mid 1st", 26),
    ("2028 Late 1st", 36),
    ("2028 2nd", 54),
    ("2028 3rd", 80),
]


def pick_assets(qb_mult_for_qb: float = 1.0):
    out = []
    for name, rank in DYNASTY_PICKS:
        # Picks are not quarterbacks; always use the raw curve.
        out.append({
            "id": name.lower().replace(" ", "-"),
            "name": name,
            "pos": "PICK",
            "team": "",
            "rank": rank,
            "value": bk_value(rank, 1.0),
            "href": "",
        })
    return out


def is_draft_pick_name(name: str) -> bool:
    n = re.sub(r"\s+", " ", (name or "").strip().lower())
    if re.search(r"\b20\d{2}\b", n) and re.search(r"\b(1st|2nd|3rd|4th|5th|pick)\b", n):
        return True
    return False


def _fill_display_names(rows, pfn_rows, fp_sf, dn_sf, ktc_sf):
    meta = meta_map(pfn_rows)
    bank = list(dn_sf) + list(ktc_sf) + list(fp_sf) + ESPN_KARABELL_SF + DRAFT_SHARKS_SF + ROTOWIRE_SF
    bank_map = {norm_name(n): n for n in bank}
    for r in rows:
        if is_draft_pick_name(r.get("key") or "") or is_draft_pick_name(r.get("name") or ""):
            r["drop"] = True
            continue
        info = meta.get(r["key"], {})
        r["name"] = info.get("name") or r.get("name") or bank_map.get(r["key"]) or r["key"].title()
        r["pos"] = r.get("pos") or info.get("pos") or ""
        r["team"] = r.get("team") or info.get("team") or ""
        r["age"] = r.get("age") or info.get("age") or ""
    return [r for r in rows if not r.get("drop")]


def aggregate(pfn_rows):
    """Super Aggregate (The Keep) plus the long-tape Board. See aggregate_protocol.py."""
    fp_sf = load_rank_names("fp-dynasty-sf") or FANTASYPROS_SF
    dn_sf = load_rank_names("dn-sf") or DYNASTY_NERDS
    ktc_sf = load_rank_names("ktc-sf") or KTC_SF
    core = {
        "PFN (Katz/Soppe)": {norm_name(r["name"]): r["rank"] for r in pfn_rows},
        "Dynasty Nerds": {norm_name(n): r for n, r in dn_sf.items()},
        "FantasyPros ECR": {norm_name(n): r for n, r in fp_sf.items()},
        "KeepTradeCut SF": {norm_name(n): r for n, r in ktc_sf.items()},
        "ESPN (Karabell)": {norm_name(n): r for n, r in as_ranks(ESPN_KARABELL_SF).items()},
        "Draft Sharks": {norm_name(n): r for n, r in as_ranks(DRAFT_SHARKS_SF).items()},
        "RotoWire": {norm_name(n): r for n, r in as_ranks(ROTOWIRE_SF).items()},
    }
    for expert, board in FP_EXPERTS.items():
        core[expert] = {norm_name(n): r for n, r in board.items()}
    meta = meta_map(pfn_rows)
    sources = expand_super_desks(core, meta)
    keep = _fill_display_names(
        rank_rows(sources, meta, require_long=True, limit=None, super_blend=True),
        pfn_rows, fp_sf, dn_sf, ktc_sf,
    )
    long_only = {name: sources[name] for name in LONG_CORE if name in sources}
    board = _fill_display_names(
        rank_rows(long_only, meta, require_long=True, limit=None),
        pfn_rows, fp_sf, dn_sf, ktc_sf,
    )
    keep = keep[:KEEP_N]
    board = board[:BOARD_N]
    for i, r in enumerate(keep, 1):
        r["bk"] = i
    for i, r in enumerate(board, 1):
        r["bk"] = i
    attach_values(keep)
    attach_values(board)
    return keep, board, sources


def redraft_lists():
    karabell = as_ranks(ESPN_KARABELL_FLEX)
    fp_ppr_named = load_rank_names("fp-ppr") or FP_PPR
    fp_ppr = {norm_name(n): r for n, r in fp_ppr_named.items()}
    pfn_meta = {norm_name(r["name"]): r for r in parse_pfn(ROOT / "data/pfn-dynasty.txt")}
    yates_map = {norm_name(n): i for i, (n, _p, _t) in enumerate(YATES_PPR, 1)}
    universe = []
    seen = set()
    for name, pos, team in YATES_PPR:
        k = norm_name(name)
        if k in seen:
            continue
        seen.add(k)
        universe.append((name, pos, team))
    for name, _rk in sorted(fp_ppr_named.items(), key=lambda kv: kv[1]):
        k = norm_name(name)
        if k in seen:
            continue
        info = pfn_meta.get(k) or {}
        pos = info.get("pos") or ""
        team = info.get("team") or ""
        if pos not in ("QB", "RB", "WR", "TE"):
            continue
        seen.add(k)
        universe.append((name, pos, team))
        if len(universe) >= PPR_N:
            break
    spine = [n for n, _rk in sorted(fp_ppr_named.items(), key=lambda kv: kv[1])]
    extra_maps = extra_ppr_maps(spine)
    ppr = []
    for name, pos, team in universe:
        k = norm_name(name)
        fp = fp_ppr.get(k) or FP_PPR.get(name)
        kb = karabell.get(name) or karabell.get(k)
        yates = yates_map.get(k)
        nums = []
        if yates:
            nums.append(float(yates))
        if fp:
            nums.append(float(fp))
        if kb:
            nums.append(float(kb))
        pk = ppr_norm(name)
        for emap in extra_maps.values():
            rk = emap.get(pk) or emap.get(k)
            if rk:
                nums.append(float(rk))
        if not nums:
            continue
        avg = sum(nums) / len(nums)
        ppr.append({
            "bk": 0,
            "name": name,
            "pos": pos,
            "team": team,
            "yates": yates or "-",
            "fp": fp or "-",
            "karabell": kb or "-",
            "n": len(nums),
            "avg": round(avg, 2),
        })
    ppr.sort(key=lambda r: (r["avg"], r["name"]))
    ppr = ppr[:PPR_N]
    for i, r in enumerate(ppr, 1):
        r["bk"] = i
    attach_values(ppr)
    # Standard: bump RB, slight WR/TE tax vs PPR
    std = score_from_ppr(ppr, {"RB": -4.5, "WR": 3.0, "TE": 2.0, "QB": 0.5})
    # Half-PPR sits between full PPR and Standard: half those taxes.
    classic = score_from_ppr(ppr, {"RB": -2.25, "WR": 1.5, "TE": 1.0, "QB": 0.25})
    return ppr, std, classic


def score_from_ppr(ppr, taxes):
    rows = []
    for r in ppr:
        adj = r["avg"] + taxes.get(r["pos"], 0)
        rows.append({**r, "avg": round(adj, 2)})
    rows.sort(key=lambda r: r["avg"])
    out = []
    for i, r in enumerate(rows[:PPR_N], 1):
        out.append({**r, "bk": i})
    attach_values(out)
    return out


def superflex_redraft(keep, ppr):
    """This-year Superflex. Keep supplies the QB tax; PPR supplies the skill board."""
    ppr_by = {norm_name(r["name"]): r for r in ppr}
    keep_by = {r["key"]: r for r in keep}
    keys = list(dict.fromkeys([*keep_by, *ppr_by]))
    scored = []
    for k in keys:
        kr = keep_by.get(k)
        pr = ppr_by.get(k)
        src = kr or pr
        pos = (src or {}).get("pos") or ""
        try:
            age_n = int((src or {}).get("age") or 25)
        except (TypeError, ValueError):
            age_n = 25
        age_adj = (age_n - 25) * (-1.6)
        if age_n <= 22:
            age_adj += 10
        if pos == "QB":
            base = (kr["bk"] if kr else 90) * 0.82
        elif pr:
            base = pr["bk"] * 0.7 + (kr["bk"] if kr else pr["bk"] + 18) * 0.3
        else:
            base = (kr["bk"] if kr else 220) + 40
        scored.append((base + age_adj, k, src, kr, pr))
    scored.sort(key=lambda x: (x[0], x[1]))
    rows = []
    for i, (score, k, src, kr, pr) in enumerate(scored[:BOARD_N], 1):
        rows.append({
            "key": k,
            "name": src.get("name") or k.title(),
            "pos": src.get("pos") or "",
            "team": src.get("team") or "",
            "age": src.get("age") or "",
            "bk": i,
            "keep": kr["bk"] if kr else "",
            "ppr": pr["bk"] if pr else "",
            "avg": round(score, 2),
            "n": (1 if kr else 0) + (1 if pr else 0),
            "ranks": {k: v for k, v in {"Keep SF": kr["bk"] if kr else None, "PPR": pr["bk"] if pr else None}.items() if v},
            "value": bk_value(i),
        })
    return rows


NAV = [
    ("index.html", "Home"),
    ("the-keep.html", "The Keep"),
    ("news.html", "News"),
    ("the-x.html", "The X"),
    ("trade.html", "Trade"),
    ("recent-trades.html", "Deals"),
    ("redraft-superflex.html", "Redraft Superflex"),
    ("the-classic.html", "The Classic"),
    ("redraft-standard.html", "Redraft STD"),
    ("rookies-2026.html", "2026 Rookies"),
    ("hot-n-cold.html", "Hot 'n' Cold"),
    ("board.html", "The Board"),
    ("players/index.html", "Players"),
    ("nfl-schedule.html", "NFL"),
    ("mlb-schedule.html", "MLB"),
]

PLAYER_PAGES = {}  # key -> slug


def slugify(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", norm_name(name))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def nav_href(target: str, depth: int) -> str:
    if depth == 0:
        return target
    if target.startswith("players/"):
        return target[len("players/") :]
    if target.startswith("news/"):
        return target[len("news/") :]
    return "../" + target


def asset(path: str, depth: int) -> str:
    return ("../" * depth) + path


def player_url(name: str, depth: int = 0) -> str | None:
    slug = PLAYER_PAGES.get(norm_name(name))
    if not slug:
        return None
    return f"{slug}.html" if depth else f"players/{slug}.html"


def player_anchor(name: str, depth: int = 0) -> str:
    href = player_url(name, depth)
    if not href:
        return f"<strong>{esc(name)}</strong>"
    return f'<a class="player-link" href="{esc(href)}"><strong>{esc(name)}</strong></a>'


def load_player_media():
    path = ROOT / "data/player_media.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_age_bank():
    """Ages from the last roster/Keep dump, then Sleeper birthdays for new names."""
    bank = {}
    roster = ROOT / "data/player_roster.json"
    if roster.exists():
        try:
            for p in json.loads(roster.read_text()):
                key = p.get("key") or norm_name(p.get("name") or "")
                if key and p.get("age") not in (None, ""):
                    bank[key] = p["age"]
        except Exception:
            pass
    keep = ROOT / "data/the-keep.json"
    if keep.exists():
        try:
            blob = json.loads(keep.read_text())
            for p in blob.get("players") or []:
                key = p.get("key") or norm_name(p.get("name") or "")
                if key and p.get("age") not in (None, "") and key not in bank:
                    bank[key] = p["age"]
        except Exception:
            pass
    try:
        from fetch_player_media import ensure_sleeper, sleeper_index
        if ensure_sleeper():
            for key, rec in sleeper_index().items():
                age = rec.get("age")
                if age not in (None, "") and key not in bank:
                    bank[key] = age
    except Exception:
        pass
    return bank


def apply_media_ages(rows, media, extra=None):
    extra = extra or {}
    for r in rows:
        if r.get("age") not in (None, ""):
            continue
        key = r.get("key") or norm_name(r.get("name") or "")
        age = (media.get(key) or {}).get("age")
        if age in (None, ""):
            age = extra.get(key)
        if age not in (None, ""):
            r["age"] = age


def face_src(r, media, depth=0):
    key = r.get("key") or norm_name(r.get("name") or "")
    img = (media.get(key) or {}).get("image") or "img/logo.jpg"
    return asset(img, depth)


def wordmark():
    return (
        '<span class="word-ball" style="color:#1788c2">BALL</span> '
        '<span class="word-keep" style="color:#c8102e">KEEP</span>'
    )


def masthead(kicker, mark, sub, url="ballkeep.com", logo="img/logo.jpg", alt="Ball Keep circular logo", art="img/mast-ballkeep.jpg"):
    return (
        f'<section class="hero masthead" aria-label="{esc(kicker)}">'
        f'<div class="hero-card">'
        f'<div class="mast-row">'
        f'<img class="mast-mark" src="{esc(logo)}" alt="{esc(alt)}" />'
        f'<div class="mast-copy">'
        f'<p class="mast-kicker">{esc(kicker)}</p>'
        f"<h1>{mark}</h1>"
        f'<span class="mast-rule" aria-hidden="true"></span>'
        f'<p class="mast-sub">{esc(sub)}</p>'
        f'<p class="mast-url">{esc(url)}</p>'
        f"</div>"
        f'<div class="mast-art" aria-hidden="true"><img src="{esc(art)}" alt="" /></div>'
        f"</div></div></section>"
    )


def sources_panel(items, heading="Boards in This Super Aggregate"):
    lis = []
    for name, url, note in items:
        if url:
            lis.append(f'<li><a href="{esc(url)}">{esc(name)}</a> - {esc(note)}</li>')
        else:
            lis.append(f"<li><strong>{esc(name)}</strong> - {esc(note)}</li>")
    return (
        '<section class="sources-box panel">'
        '<p class="kicker">Sources</p>'
        f"<h3>{esc(heading)}</h3>"
        f"<ol>{''.join(lis)}</ol>"
        '<p class="note">Unranked names are skipped in the mean - never treated as 999. '
        "Short expert lists still move the names they actually ranked.</p>"
        "</section>"
    )


PPR_SOURCES = [
    ("Field Yates, ESPN", "https://www.espn.com/fantasy/football/", "2026 full-PPR redraft board, updated Aug 17."),
    ("FantasyPros Redraft ECR", "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php", "Full-PPR expert consensus, Aug 28."),
    ("ESPN - Eric Karabell Flex (no QB)", "https://www.espn.com/fantasy/football/story/_/id/47539664", "PPR skill-player board, Aug 17."),
] + PPR_EXTRA_SOURCES
ROOKIE_SOURCES = [
    ("Dynasty Dealer Superflex rookie board", "", "13-analyst team board, July 30."),
    ("FantasyPros Superflex Rookie ECR", "https://www.fantasypros.com/nfl/rankings/dynasty-rookies-superflex.php", "Expert consensus, Aug 27."),
    ("PFF Superflex Rookie Column", "https://www.pff.com/", "Love / Mendoza / Tate locked 1–2–3."),
]



FB_SEO = {
    "index.html": (
        "Ball Keep | Superflex Dynasty Rankings and Redraft PPR",
        "The Keep is Superflex Dynasty - 32 boards, top 400. The Board is Redraft PPR. BK Value trade calculator, The X, and hourly BK News.",
        "img/hero.jpg",
    ),
    "the-keep.html": (
        "The Keep 2026 Superflex Dynasty Rankings (Top 400) | Ball Keep",
        "Ball Keep Super Aggregate Superflex dynasty top 400, rebuilt August 28, 2026. 50% the four long boards, 50% every other board that ranked the player. Rank 1 is 12,000 BK Value.",
        "img/logo.jpg",
    ),
    "board.html": (
        "The Board - 2026 Redraft PPR Rankings | Ball Keep",
        "The Board is Ball Keep's redraft PPR list. Full-PPR, 1QB, 200 skill players. Thirteen boards: Yates, FantasyPros ECR, Karabell, plus ten more expert and public PPR lists. Kickers and DST omitted.",
        "img/logo.jpg",
    ),
    "the-x.html": (
        "The X - Football Memes from X | Ball Keep",
        "Fun tape, not news. Memes and shitposts pulled from X via Google News. Pictures when the wire carries them.",
        "img/logo.jpg",
    ),
    "redraft-ppr.html": (
        "The Board - 2026 Redraft PPR Rankings | Ball Keep",
        "The Board is Ball Keep's redraft PPR list. Full-PPR, 1QB, 200 skill players. Thirteen PPR boards averaged. Kickers and DST omitted.",
        "img/logo.jpg",
    ),
    "redraft-superflex.html": (
        "2026 Superflex Redraft Rankings | Ball Keep",
        "This-year Superflex redraft. Quarterbacks stay expensive. Built from The Keep SF premium plus the PPR board.",
        "img/logo.jpg",
    ),
    "the-classic.html": (
        "The Classic - 2026 Half-PPR Rankings | Ball Keep",
        "The Classic is Ball Keep's 0.5 PPR redraft list. Same 13-board PPR mean as The Board, then half the Standard tax: RB −2.25, WR +1.5, TE +1, QB +0.25.",
        "img/logo.jpg",
    ),
    "redraft-standard.html": (
        "2026 Fantasy Football Standard Rankings (Top 200) | Ball Keep",
        "Standard (no PPR) redraft board. Same consensus as PPR, then RB −4.5 ranks, WR +3, TE +2. Bijan, Gibbs, and CMC climb.",
        "img/logo.jpg",
    ),
    "rookies-2026.html": (
        "2026 NFL Rookie Superflex Rankings | Ball Keep",
        "Drafted-class Superflex rookie ranks from Dynasty Dealer, FantasyPros Rookie ECR, and PFF. Love, Mendoza, and Tate lock the top.",
        "img/logo.jpg",
    ),
    "hot-n-cold.html": (
        "Dynasty Hot and Cold Board - Buys and Sells | Ball Keep",
        "Ball Keep Hot 'n' Cold: late-August dynasty buys and sells from PlayerProfiler, FantasyPros, SI, and The Athletic, tied to The Keep ranks.",
        "img/logo.jpg",
    ),
    "trade.html": (
        "Fantasy Football Trade Calculator (Superflex, 1QB, PPR) | Ball Keep",
        "Four calculators. Rank becomes BK Value on a decaying curve (12,000 at 1.01). Fair is within 8%. Superflex, 1QB, PPR, and standard.",
        "img/logo.jpg",
    ),
    "recent-trades.html": (
        "Recent Superflex Dynasty Trades | Ball Keep",
        "Type a player. See every Superflex package he actually moved in, with BK Value on both sides.",
        "img/logo.jpg",
    ),
    "news.html": (
        "BK News - NFL Injury, Roster, and Coach Tape | Ball Keep",
        "Hourly football injury, roster, and coach reports clustered from league RSS, Google News, X, and YouTube, linked to Keep player files.",
        "img/logo.jpg",
    ),
    "players/index.html": (
        "NFL Dynasty Player Files - Keep, Redraft, Tape | Ball Keep",
        "Every Keep 400 and Board name: Superflex Keep rank, Redraft PPR Board rank, BK Value, 2025 tape, and BK News hits.",
        "img/logo.jpg",
    ),
    "nfl-schedule.html": (
        "2026 NFL Schedule - All 32 Teams | Ball Keep",
        "Full 2026 NFL regular-season slate. Filter by week or club. Kickoff Wednesday, Sept. 9 in Seattle.",
        "img/logo.jpg",
    ),
    "mlb-schedule.html": (
        "MLB September Schedule - Stretch Run | Ball Keep",
        "September baseball slate on the football boards. Filter by club. Regular season wraps Sunday, Sept. 27, 2026.",
        "img/logo.jpg",
    ),
    "privacy.html": (
        "Privacy Policy | Ball Keep",
        "How Ball Keep, BaseKeep, BasketKeep, and PitchKeep collect and use information, including cookies, analytics, and ads.",
        "img/logo.jpg",
    ),
    "discord.html": (
        "Ball Keep Discord Bot - Ranks, Trades, Tape",
        "The circular mark plus a Discord bot that searches The Keep, runs the trade calculator, drops tape, and can publish the site into a server.",
        "img/logo.jpg",
    ),
    "trade-superflex.html": (
        "Superflex Dynasty Trade Calculator | Ball Keep",
        "Add two sides. Superflex Keep ranks become BK Value (12,000 at 1.01). Fair is within 8%. Future picks map to equivalent ranks.",
        "img/logo.jpg",
    ),
    "trade-sf-redraft.html": (
        "Superflex Redraft Trade Calculator | Ball Keep",
        "Trade calculator on the Redraft Superflex ranks. This-year Superflex. Fair is within 8%.",
        "img/logo.jpg",
    ),
    "trade-1qb.html": (
        "1QB Dynasty Trade Calculator | Ball Keep",
        "Same Superflex ranks, quarterbacks taxed to 38% of BK Value. Fair is within 8%.",
        "img/logo.jpg",
    ),
    "trade-ppr.html": (
        "PPR Redraft Trade Calculator | Ball Keep",
        "Trade calculator on The Board Redraft PPR ranks. Rank becomes BK Value. Fair is within 8%.",
        "img/logo.jpg",
    ),
    "trade-standard.html": (
        "Standard Redraft Trade Calculator | Ball Keep",
        "Trade calculator on the 2026 standard (no PPR) board. Rank becomes BK Value. Fair is within 8%.",
        "img/logo.jpg",
    ),
    "trade-classic.html": (
        "The Classic Half-PPR Trade Calculator | Ball Keep",
        "Trade calculator on The Classic 0.5 PPR ranks. Rank becomes BK Value. Fair is within 8%.",
        "img/logo.jpg",
    ),
}

HOME_FAQ = [
    ("What is Ball Keep?", "The Keep is Superflex Dynasty - 32 boards, top 400. The Board is Redraft PPR for this year. BK Value prices trades. BK News clusters the injury and roster wire every hour."),
    ("How is The Keep ranked?", "Half the vote is the four long Superflex boards. Half is every other board that ranked the player. Unranked names are skipped, never treated as 999."),
    ("What is BK Value?", "Rank 1 is 12,000. The curve decays so mid-board names still trade. Fair means the two sides are within 8%."),
    ("What other sports are on this site?", "BaseKeep is baseball, BasketKeep is basketball, PitchKeep is Premier League. Same rank-to-value idea, separate palettes."),
]
KEEP_FAQ = [
    ("What is The Keep?", "Ball Keep's Superflex Dynasty Super Aggregate. Top 400 names from 32 public boards, rebuilt August 28, 2026."),
    ("How is a Superflex rank different from redraft PPR?", "The Keep prices a second quarterback slot and a long window. The Board next door is this-year Redraft PPR - one QB, a point per catch."),
    ("How does BK Value work on this list?", "The Keep rank becomes BK Value. Rank 1 is 12,000. Ranks 40–80 still sit around 44% and 29% of the 1.01. The Superflex calculator uses this board."),
]
BOARD_FAQ = [
    ("What is The Board?", "Ball Keep's 2026 redraft PPR list. Full-PPR, 1QB, 200 skill players. Thirteen boards: Field Yates, FantasyPros PPR ECR, Eric Karabell Flex, then Derek Brown, Andrew Erickson, Pat Fitzmaurice, Chris Welsh, CBS, Yahoo, Draft Sharks, RotoWire, NFL.com, and 4for4. Kickers and DST omitted."),
    ("How is the rank built?", "The mean of every board that published the name. Unranked on a board is a skip, not a last-place dump. Yates, FantasyPros, and Karabell stay on the table so you can see the long tapes against the mean."),
    ("How is this different from The Keep?", "The Keep is Superflex Dynasty. The Board is this year only, one quarterback, a point per catch."),
    ("Does BK Value use this rank?", "Yes. The PPR calculator prices The Board rank on the same 12,000 curve."),
]
TRADE_FAQ = [
    ("How does the trade calculator work?", "Every name on a Ball Keep list has a rank. That rank becomes BK Value on a decaying curve. Add the numbers on two sides."),
    ("What does fair mean?", "Fair is within 8%. Superflex keeps quarterback price. 1QB taxes passers to 38% of that number."),
    ("Which calculator should I use?", "Superflex Dynasty for two-QB startups. 1QB when a passer is just another starter. Redraft PPR, The Classic (0.5 PPR), or Standard when the deal is for this season only."),
]
NEWS_FAQ = [
    ("Where does BK News come from?", "Hourly clusters from league RSS, Google News, X, and YouTube. Each story is an aggregate with links back to the original boards and to Keep player files."),
    ("How often does the wire refresh?", "The scrape runs every hour. New URLs merge into the cluster; the static pages rebuild when the tape moved."),
    ("Why do stories link to player pages?", "Named Keep, Board, and rookie files sit on the cluster so you can jump from the injury to the rank."),
]

FB_ALSO = {
    "the-keep.html": [
        ("board.html", "The Board", "Redraft PPR, this year."),
        ("redraft-superflex.html", "Redraft Superflex", "Two-QB, this year."),
        ("rookies-2026.html", "2026 Rookies", "Drafted class."),
        ("trade-superflex.html", "Superflex Calculator", "Keep ranks as BK Value."),
        ("players/index.html", "Player Pages", "Every Keep name, tape included."),
        ("hot-n-cold.html", "Hot 'n' Cold", "Buys and sells."),
    ],
    "board.html": [
        ("the-keep.html", "The Keep", "Superflex dynasty, top 400."),
        ("the-classic.html", "The Classic", "Half-PPR redraft."),
        ("redraft-standard.html", "Redraft Standard", "No reception point."),
        ("redraft-superflex.html", "Redraft Superflex", "Two-QB, this year."),
        ("trade-ppr.html", "PPR Calculator", "Board ranks as BK Value."),
        ("players/index.html", "Player Pages", "Tape and plus/minus."),
        ("news.html", "BK News", "Injuries and roster tape."),
    ],
    "the-classic.html": [
        ("board.html", "The Board", "Full-PPR redraft."),
        ("redraft-standard.html", "Redraft Standard", "No reception point."),
        ("trade-classic.html", "Classic Calculator", "0.5 PPR values."),
        ("the-keep.html", "The Keep", "Superflex dynasty."),
        ("players/index.html", "Player Pages", "Keep and Board files."),
    ],
    "redraft-superflex.html": [
        ("the-keep.html", "The Keep", "Superflex dynasty."),
        ("board.html", "The Board", "Redraft PPR."),
        ("trade-sf-redraft.html", "SF Redraft Calculator", "This-year Superflex values."),
        ("rookies-2026.html", "2026 Rookies", "Drafted class."),
    ],
    "redraft-standard.html": [
        ("board.html", "The Board", "Full-PPR redraft."),
        ("the-classic.html", "The Classic", "Half-PPR redraft."),
        ("the-keep.html", "The Keep", "Superflex dynasty."),
        ("trade-standard.html", "Standard Calculator", "No-PPR values."),
        ("players/index.html", "Player Pages", "Keep and Board files."),
    ],
    "rookies-2026.html": [
        ("the-keep.html", "The Keep", "Where the class lands on the 400."),
        ("redraft-superflex.html", "Redraft Superflex", "This-year two-QB board."),
        ("players/index.html", "Player Pages", "Rookie files and tape."),
        ("hot-n-cold.html", "Hot 'n' Cold", "Market tape."),
    ],
    "hot-n-cold.html": [
        ("the-keep.html", "The Keep", "The ranks behind the tape."),
        ("recent-trades.html", "Recent Deals", "Packages that actually closed."),
        ("news.html", "BK News", "Injuries moving the market."),
        ("trade-superflex.html", "Superflex Calculator", "Price the buy."),
    ],
    "trade.html": [
        ("the-keep.html", "The Keep", "Superflex dynasty ranks."),
        ("board.html", "The Board", "Redraft PPR ranks."),
        ("recent-trades.html", "Recent Deals", "Packages that closed."),
        ("players/index.html", "Player Pages", "Every name in the calc."),
    ],
    "news.html": [
        ("the-keep.html", "The Keep", "The ranks the wire moves."),
        ("players/index.html", "Player Pages", "Files named in the tape."),
        ("bb/news.html", "BaseKeep News", "Baseball IL and roster."),
        ("bk/news.html", "BasketKeep News", "NBA injury tape."),
    ],
    "players/index.html": [
        ("the-keep.html", "The Keep", "Superflex dynasty top 400."),
        ("board.html", "The Board", "Redraft PPR."),
        ("news.html", "BK News", "Hourly wire."),
        ("trade.html", "Trade Calculators", "Price any name."),
    ],
    "the-x.html": [
        ("news.html", "BK News", "The actual wire."),
        ("bk/the-x.html", "BasketKeep The X", "NBA memes."),
        ("bb/the-x.html", "BaseKeep The X", "MLB memes."),
        ("pl/the-x.html", "PitchKeep The X", "PL memes."),
    ],
    "nfl-schedule.html": [
        ("the-keep.html", "The Keep", "Dynasty ranks by club."),
        ("news.html", "BK News", "Injuries on the slate."),
        ("mlb-schedule.html", "MLB Schedule", "September baseball."),
    ],
    "mlb-schedule.html": [
        ("bb/index.html", "BaseKeep", "BaseKeep boards."),
        ("bb/the-keep.html", "BB The Keep", "Dynasty baseball 400."),
        ("nfl-schedule.html", "NFL Schedule", "Football slate."),
    ],
}


def page(title, path, body, extra_js="", depth=0, description=None, image=None, doc_title=None,
         crumbs=None, extra_jsonld=None, og_type="website", published=None, modified=None,
         robots=None):
    links = []
    news_here = path == "news.html" or path.startswith("news/")
    for href, label in NAV:
        on = href == path or (href == "news.html" and news_here) or (
            href == "board.html" and path == "redraft-ppr.html"
        )
        cur = ' aria-current="page"' if on else ""
        links.append(f'<a href="{nav_href(href, depth)}"{cur}>{esc(label)}</a>')
    packed = FB_SEO.get(path)
    full_title = doc_title or (packed[0] if packed else f"{title} | Ball Keep")
    desc = description or (packed[1] if packed else f"{title} on Ball Keep. Superflex dynasty rankings, BK Value trade calculator, and BK News. Updated {UPDATED}.")
    img = image or (packed[2] if packed else "img/logo.jpg")
    foot = footer_nav([(nav_href(h, depth), lab) for h, lab in NAV], nav_href(path, depth))
    crumb_html = crumbs or ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
{head_tags(title=full_title, description=desc, canonical=canon(path), image=img, brand="Ball Keep", extra_jsonld=extra_jsonld, og_type=og_type, published=published, modified=modified, robots=robots)}
  <link rel="stylesheet" href="{asset("css/site.css", depth)}?v=41" />
  <link rel="icon" href="{asset("img/logo.jpg", depth)}" />
</head>
<body>
  <div class="wrap">
    <header class="site">
      <a class="brand" href="{nav_href("index.html", depth)}">
        <img src="{asset("img/logo.jpg", depth)}" alt="Ball Keep circular logo" width="56" height="56" />
        <div>
          <p class="brand-title">{wordmark()}</p>
          <p>Dynasty · Redraft</p>
        </div>
      </a>
      <nav>{''.join(links)}</nav>
    </header>
    {sports_top("fb", depth)}
    {crumb_html}
    {body}
    <footer>
      © {date.today().year} Ball Keep · ballkeep.com · Rankings aggregated {UPDATED}. Sources listed at the bottom of each board. Not affiliated with the NFL, MLB, NBA, or Premier League.
      {foot}
      {legal_links(depth)}
      {sports_footer("fb", depth)}
    </footer>
  </div>
    {extra_js}
</body>
</html>
"""


def board_page(title, path, body, extra_js="", extra_jsonld=None):
    extra = also_on_desk(FB_ALSO.get(path) or [])
    ld = [breadcrumb_jsonld([
        ("Ball Keep", "https://ballkeep.com/"),
        (title, canon(path)),
    ])]
    for blob in extra_jsonld or []:
        if blob:
            ld.append(blob)
    return page(
        title,
        path,
        body + extra,
        extra_js,
        crumbs=breadcrumbs([("Ball Keep", "index.html"), (title, None)]),
        extra_jsonld=ld,
    )


def _rank_th(label):
    cls = ""
    if label == "BK Value":
        cls = "c-val"
    elif label == "£":
        cls = "c-price"
    elif label == "Age":
        cls = "c-age"
    elif label not in ("BK", "PK", "Player", "Pos", "Team", "Club"):
        cls = "desk-only"
    attr = f' class="{cls}"' if cls else ""
    return f"<th{attr}>{esc(label)}</th>"


def rank_table(rows, extra_headers=None, extra_cells=None, depth=0, media=None, faces=False, show_age=False, draft_check=False):
    extra_headers = extra_headers or []
    extra_cells = extra_cells or (lambda r: "")
    media = media or {}
    cols = ["BK", "Player", "Pos", "Team"]
    head = "".join(_rank_th(h) for h in cols + extra_headers)
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        age_txt = str(r["age"]) if r.get("age") not in (None, "") else ""
        age_label = f"age {age_txt}" if show_age and age_txt else ""
        age_span = f'<span class="age-desc">{esc(age_label)}</span>' if age_label else ""
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}</div>"
        )
        face = ""
        if faces:
            face = f'<img class="face" src="{esc(face_src(r, media, depth))}" alt="{esc(face_alt(r.get("name")))}" loading="lazy" />'
        off = '<span class="draft-off">Crossed off</span>' if draft_check else ""
        stack = f'<span class="name-stack">{player_anchor(r["name"], depth)}{off}{age_span}{meta}</span>'
        mark = ""
        if draft_check:
            nm = r.get("name") or "player"
            mark = (
                f'<label class="draft-mark">'
                f'<input type="checkbox" class="draft-check" aria-label="Cross off {esc(nm)}">'
                f"</label>"
            )
        dn = rank_search_key(r.get("name"), pos, team)
        body.append(
            f'<tr data-pos="{esc(pos)}" data-name="{dn}">'
            f'<td class="rk c-rank">{r.get("bk","")}</td>'
            f'<td class="c-name">{mark}{face}{stack}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f"{extra_cells(r)}"
            "</tr>"
        )
    bits = ["rank-table"]
    if faces:
        bits.append("faces")
    if draft_check:
        bits.append("has-draft")
    return (
        f'<div class="table-wrap"><table class="{" ".join(bits)}">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def write(path, html_doc):
    dest = ROOT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(strip_em(html_doc))


def news_player_href(player: dict, depth: int = 0) -> str | None:
    slug = player.get("slug") or PLAYER_PAGES.get(player.get("key") or "")
    if not slug:
        slug = PLAYER_PAGES.get(norm_name(player.get("name") or ""))
    if not slug:
        return None
    return f"{'../' * depth}players/{slug}.html"


def news_player_anchor(player: dict, depth: int = 0) -> str:
    name = player.get("name") or player.get("key") or "Player"
    href = news_player_href(player, depth)
    if not href:
        return f"<strong>{esc(name)}</strong>"
    return f'<a class="player-link" href="{esc(href)}"><strong>{esc(name)}</strong></a>'


def news_card(story: dict, depth: int = 0) -> str:
    cat = story.get("category") or "wire"
    label = CATEGORY_LABEL.get(cat, cat.title())
    href = f"{'../' * depth}news/{esc(story['slug'])}.html"
    players = " ".join(
        f'<span class="chip">{esc(p.get("name") or "")}</span>'
        for p in (story.get("players") or [])[:6]
    )
    nsrc = len(story.get("sources") or [])
    kinds = {s.get("kind") for s in story.get("sources") or []}
    bits = [f"{nsrc} source" + ("s" if nsrc != 1 else "")]
    if "x" in kinds:
        bits.append("X")
    if "video" in kinds:
        bits.append("video")
    return (
        f'<a class="news-item tile" href="{href}">'
        f'<div class="news-meta"><span class="kind {esc(cat)}">{esc(label)}</span> '
        f'{esc(news_when(story.get("updated") or story.get("published") or ""))} · {esc(" · ".join(bits))}</div>'
        f'<h3>{esc(story.get("headline") or "Update")}</h3>'
        f'<p>{esc(story.get("blurb") or "")}</p>'
        f'<div class="news-players">{players}</div>'
        f"</a>"
    )


def render_news_pages():
    """Football BK News hub + story files. Baseball lives on BaseKeep."""
    stories = load_news_stories("football")
    (ROOT / "news").mkdir(parents=True, exist_ok=True)
    keep = {f"{s['slug']}.html" for s in stories if s.get("slug")}
    for old in (ROOT / "news").glob("*.html"):
        if old.name not in keep:
            old.unlink()

    cards = "".join(news_card(s) for s in stories) or (
        '<p class="note">The football wire is warming up. The hourly scrape will fill this board.</p>'
    )
    chips = []
    for k, lab in (
        ("all", "All"),
        ("injury", "Injuries"),
        ("roster", "Roster"),
        ("coach", "Coach"),
        ("trade", "Trades"),
        ("practice", "Practice"),
        ("wire", "Wire"),
    ):
        cls = ' class="active"' if k == "all" else ""
        chips.append(f'<button type="button" data-cat="{esc(k)}"{cls}>{esc(lab)}</button>')
    filters = "".join(chips)
    updated = stories[0].get("updated") if stories else ""
    items_json = json.dumps([
        {
            "slug": s.get("slug"),
            "cat": s.get("category") or "wire",
            "html": news_card(s),
        }
        for s in stories
    ]).replace("<", "\\u003c")
    extra = f"""<script>
    const NEWS = {items_json};
    const box = document.getElementById('news-list');
    function show(cat) {{
      const rows = NEWS.filter(s => cat === 'all' || s.cat === cat);
      box.innerHTML = rows.map(s => s.html).join('') || '<p class="note">No stories in this bucket yet.</p>';
    }}
    document.getElementById('news-filters').addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      document.querySelectorAll('#news-filters button').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); show(b.dataset.cat);
    }});
    </script>"""
    body = f"""
    <p class="kicker">BK News · Football · Hourly wire</p>
    <h1>BK News</h1>
    <p class="note">Injuries, roster moves, and coach reports pulled from search and X, then clustered into short stories. Click a row for the aggregate summary, the original articles / X posts / video, and links back to every Ball Keep player page named in the tape. The scrape repeats on its own every hour. Baseball lives on <a href="bb/news.html">BaseKeep</a>. Basketball lives on <a href="bk/news.html">BasketKeep</a>.</p>
    <p class="note">{f"Last cluster {esc(news_when(updated))}." if updated else "Awaiting first successful pull."}</p>
    <div class="filters" id="news-filters">{filters}</div>
    <div class="news-list" id="news-list">{cards}</div>
    {faq_html(NEWS_FAQ, heading="How the football wire works.")}
    {also_on_desk(FB_ALSO["news.html"])}
    """
    write("news.html", page(
        "BK News", "news.html", body, extra,
        crumbs=breadcrumbs([("Ball Keep", "index.html"), ("BK News", None)]),
        extra_jsonld=[
            breadcrumb_jsonld([
                ("Ball Keep", "https://ballkeep.com/"),
                ("BK News", "https://ballkeep.com/news.html"),
            ]),
            faq_jsonld(NEWS_FAQ),
        ],
    ))

    urls = ["https://ballkeep.com/news.html"]
    for s in stories:
        slug = s.get("slug")
        if not slug:
            continue
        cat = s.get("category") or "wire"
        label = CATEGORY_LABEL.get(cat, cat.title())
        sources = s.get("sources") or []
        groups = [("article", "Articles"), ("x", "X"), ("video", "Video")]
        blocks = []
        for kind, heading in groups:
            rows = [src for src in sources if src.get("kind") == kind]
            if not rows:
                continue
            lis = []
            for src in rows:
                pub = src.get("publisher") or ""
                when = news_when(src.get("published") or "")
                snip = src.get("snippet") or ""
                lis.append(
                    "<li class=\"source-row\">"
                    f'<a href="{esc(src.get("url") or "#")}" rel="noopener noreferrer">{esc(src.get("title") or pub or "Source")}</a>'
                    f'<span class="news-meta">{esc(pub)}{" · " + esc(when) if when else ""}</span>'
                    f'{f"<p class=\"note\">{esc(snip)}</p>" if snip else ""}'
                    "</li>"
                )
            blocks.append(f"<h3>{esc(heading)}</h3><ul class=\"source-list\">{''.join(lis)}</ul>")
        source_html = "".join(blocks) or "<p class=\"note\">Sources attached on the next hourly pass.</p>"
        people = s.get("players") or []
        if people:
            plist = "".join(
                f'<a class="tile" href="{esc(news_player_href(p, 1) or "#")}"><h3>{esc(p.get("name") or "")}</h3>'
                f'<p class="note">{esc(p.get("pos") or "")} {esc(p.get("team") or "")}</p></a>'
                for p in people
                if news_player_href(p, 1)
            )
            named = f'<p class="kicker" style="margin-top:22px">Players on this story</p><div class="grid-3">{plist}</div>'
        else:
            named = '<p class="note" style="margin-top:18px">No Ball Keep player page matched this cluster yet.</p>'
        nsrc = len(sources)
        related = related_stories_html(stories, s, lambda st: f"{st['slug']}.html")
        story_body = f"""
    <p class="kicker">BK News · {esc(label)}</p>
    <p class="news-meta">{esc(news_when(s.get("updated") or s.get("published") or ""))} · {nsrc} source{"s" if nsrc != 1 else ""}</p>
    <h1>{esc(s.get("headline") or "Update")}</h1>
    <section class="panel analysis">
      <p class="kicker">Aggregate</p>
      <p>{esc(s.get("summary") or s.get("blurb") or "")}</p>
    </section>
    {named}
    <section class="sources-box panel" style="margin-top:18px">
      <p class="kicker">Tape</p>
      <h3>Links back to the boards</h3>
      {source_html}
    </section>
    {related}
    <p class="note" style="margin-top:18px"><a href="../news.html">All BK News</a> · <a href="../players/index.html">Player pages</a> · <a href="../the-keep.html">The Keep</a></p>
    """
        story_url = f"https://ballkeep.com/news/{slug}.html"
        story_desc = clip(s.get("summary") or s.get("blurb") or s.get("headline") or "BK News football story.")
        write(
            f"news/{slug}.html",
            page(
                s.get("headline") or "BK News",
                f"news/{slug}.html",
                story_body,
                depth=1,
                description=story_desc,
                image="img/logo.jpg",
                crumbs=breadcrumbs([
                    ("Ball Keep", "../index.html"),
                    ("BK News", "../news.html"),
                    (s.get("headline") or "Update", None),
                ]),
                extra_jsonld=[
                    breadcrumb_jsonld([
                        ("Ball Keep", "https://ballkeep.com/"),
                        ("BK News", "https://ballkeep.com/news.html"),
                        (s.get("headline") or "Update", story_url),
                    ]),
                    article_jsonld(
                        s.get("headline") or "BK News",
                        story_url,
                        story_desc,
                        published=s.get("published") or "",
                        modified=s.get("updated") or "",
                        image="img/logo.jpg",
                        brand="Ball Keep",
                        section=label,
                    ),
                ],
                og_type="article",
                published=s.get("published"),
                modified=s.get("updated"),
            ),
        )
        urls.append(f"https://ballkeep.com/news/{slug}.html")
    return urls



def collect_profiles(keep, ppr, std, sf_redraft, classic=None):
    """Union of The Keep top 400, The Board (redraft PPR), Superflex redraft, and Hot/Cold."""
    players = OrderedDict()

    def add(name, pos, team, list_name, rank=None, extra=None, ranks=None, avg=None, n=None, age=None):
        k = norm_name(name)
        if k not in players:
            players[k] = {
                "key": k,
                "slug": slugify(name),
                "name": name,
                "pos": pos or "",
                "team": team or "",
                "age": age or "",
                "lists": {},
                "notes": [],
                "ranks": {},
                "keep_avg": avg,
                "keep_n": n,
            }
        p = players[k]
        if pos and not p["pos"]:
            p["pos"] = pos
        if team and not p["team"]:
            p["team"] = team
        if age and not p["age"]:
            p["age"] = age
        if ranks and not p.get("ranks"):
            p["ranks"] = {src: rk for src, rk in ranks.items() if rk not in (None, "", "-")}
        if avg is not None and p.get("keep_avg") is None:
            p["keep_avg"] = avg
        if n is not None and p.get("keep_n") is None:
            p["keep_n"] = n
        p["lists"][list_name] = rank
        if extra:
            p["notes"].append(extra)

    for r in keep[:KEEP_N]:
        add(r["name"], r["pos"], r["team"], "The Keep", r["bk"],
            f"The Keep #{r['bk']} · average {r['avg']} across {r['n']} Superflex boards",
            ranks=r["ranks"], avg=r["avg"], n=r["n"], age=r.get("age"))
    for r in ppr:
        extra = (
            f"The Board #{r['bk']} Redraft PPR (Yates {r['yates']}"
            + (f", FantasyPros {r['fp']}" if r["fp"] != "-" else "")
            + ")"
        )
        add(r["name"], r["pos"], r["team"], "The Board", r["bk"], extra, age=r.get("age"))
        add(r["name"], r["pos"], r["team"], "Redraft PPR", r["bk"], extra)
    for r in sf_redraft:
        add(r["name"], r["pos"], r["team"], "Redraft Superflex", r["bk"],
            f"Redraft Superflex #{r['bk']}",
            ranks=r.get("ranks"), avg=r.get("avg"), n=r.get("n"), age=r.get("age"))
    for r in std:
        add(r["name"], r["pos"], r["team"], "Redraft Standard", r["bk"],
            f"Redraft Standard #{r['bk']}")
    for r in (classic or []):
        add(r["name"], r["pos"], r["team"], "The Classic", r["bk"],
            f"The Classic #{r['bk']} Half-PPR")
        add(r["name"], r["pos"], r["team"], "Redraft Half-PPR", r["bk"],
            f"The Classic #{r['bk']} Half-PPR")
    for i, r in enumerate(ROOKIES, 1):
        add(r["name"], r["pos"], r["team"], "2026 Rookies", i, r["value"])
    for i, r in enumerate(HOT, 1):
        add(r["name"], r["pos"], r["team"], "Hot", i, f"Hot #{i}: {r['why']} - {r['src']}")
    for i, r in enumerate(COLD, 1):
        add(r["name"], r["pos"], r["team"], "Cold", i, f"Cold #{i}: {r['why']} - {r['src']}")

    PLAYER_PAGES.clear()
    for k, p in players.items():
        PLAYER_PAGES[k] = p["slug"]
    return list(players.values())


def auto_plus_minus(p):
    plus, minus = [], []
    lists = p["lists"]
    if "Hot" in lists:
        plus.append(next((n for n in p["notes"] if n.startswith("Hot")), "On the BK Hot board as a buy."))
    if "Cold" in lists:
        minus.append(next((n for n in p["notes"] if n.startswith("Cold")), "On the BK Cold board as a sell."))
    if "2026 Rookies" in lists and lists["2026 Rookies"] <= 5:
        plus.append(next((n for n in p["notes"] if n in [x["value"] for x in ROOKIES]), "Top-five name in the 2026 rookie class."))
    if "The Keep" not in lists and ("Redraft PPR" in lists or "Redraft Standard" in lists):
        minus.append("On the 2026 redraft board, not The Keep top 400.")
    return plus, minus


def plusminus_html(plus, minus):
    if not plus and not minus:
        return ""
    left = (
        f'<div class="pm plus"><h3>Plus</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in plus)}</ul></div>'
        if plus else ""
    )
    right = (
        f'<div class="pm minus"><h3>Minus</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in minus)}</ul></div>'
        if minus else ""
    )
    return f'<div class="plusminus">{left}{right}</div>'


def take_html(kicker, grafs, limit=2):
    grafs = [g for g in (grafs or []) if g]
    if not grafs:
        return ""
    return (
        f'<section class="panel analysis"><p class="kicker">{esc(kicker)}</p>'
        + "".join(f"<p>{esc(g)}</p>" for g in grafs[:limit])
        + "</section>"
    )


def _fact_cells(items):
    cells = "".join(
        f'<div class="fact"><small>{esc(k)}</small><strong>{esc(v)}</strong></div>'
        for k, v in items if v not in (None, "", "-")
    )
    return f'<div class="facts">{cells}</div>' if cells else ""


def ff_facts(p, college, is_rook):
    lists = p.get("lists") or {}
    items = []
    if is_rook:
        items.append(("Class", "2026 rookie"))
    if p.get("keep_avg") is not None:
        items.append(("Keep avg", p["keep_avg"]))
    if p.get("keep_n"):
        items.append(("# Boards", p["keep_n"]))
    keep = lists.get("The Keep")
    if keep:
        items.append(("BK Value", f"{bk_value(keep):,}"))
    hi, lo = None, None
    ranks = {k: v for k, v in (p.get("ranks") or {}).items() if isinstance(v, (int, float))}
    if ranks:
        hi, lo = min(ranks.values()), max(ranks.values())
        items.append(("Spread", f"{hi}–{lo}"))
    return _fact_cells(items)


def ff_stat_line(p):
    lists = p.get("lists") or {}
    bits = []
    if lists.get("The Keep"):
        bits.append(f"Keep #{lists['The Keep']}")
    if p.get("keep_avg") is not None:
        bits.append(f"avg {p['keep_avg']}")
    if p.get("keep_n"):
        bits.append(f"{p['keep_n']} boards")
    if lists.get("The Keep"):
        bits.append(f"BK {bk_value(lists['The Keep']):,}")
    if lists.get("Redraft PPR"):
        bits.append(f"PPR #{lists['Redraft PPR']}")
    if lists.get("The Classic") or lists.get("Redraft Half-PPR"):
        bits.append(f"Classic #{lists.get('The Classic') or lists.get('Redraft Half-PPR')}")
    if lists.get("Redraft Standard"):
        bits.append(f"STD #{lists['Redraft Standard']}")
    if lists.get("2026 Rookies"):
        bits.append(f"Rookie #{lists['2026 Rookies']}")
    return " · ".join(bits)



def ff_player_seo(p):
    lists = p.get("lists") or {}
    keep = lists.get("The Keep")
    ppr = lists.get("Redraft PPR")
    pos = p.get("pos") or "player"
    team = p.get("team") or ""
    name = p["name"]
    loc = f"{pos} {team}".strip()
    if keep:
        title = f"{name} Superflex Dynasty Rank #{keep} ({loc})"
        desc = (
            f"{name} is Ball Keep Superflex Keep #{keep}, {loc}. "
            f"Average {p.get('keep_avg')} across {p.get('keep_n') or 0} boards. "
            f"BK Value {bk_value(keep):,}. Updated {UPDATED}."
        )
    elif ppr:
        title = f"{name} PPR Rank #{ppr} ({loc})"
        desc = f"{name} ranks #{ppr} on Ball Keep full-PPR redraft ({loc}). Updated {UPDATED}."
    elif lists.get("2026 Rookies"):
        title = f"{name} 2026 Rookie Rank #{lists['2026 Rookies']} ({loc})"
        desc = f"{name} is #{lists['2026 Rookies']} on the Ball Keep 2026 Superflex rookie board ({loc})."
    else:
        title = f"{name} Dynasty File ({loc})"
        desc = f"{name} player file on Ball Keep: dynasty and redraft ranks, board dump, and tape. {loc}."
    return title, clip(desc)


def ff_rank_cards(p):
    lists = p.get("lists") or {}
    items = [
        ("The Keep", lists.get("The Keep")),
        ("The Board", lists.get("The Board") or lists.get("Redraft PPR")),
        ("The Classic", lists.get("The Classic") or lists.get("Redraft Half-PPR")),
        ("SF Redraft", lists.get("Redraft Superflex")),
        ("STD", lists.get("Redraft Standard")),
        ("Rookies", lists.get("2026 Rookies")),
    ]
    cards = []
    for label, rank in items:
        if not rank:
            continue
        cards.append(
            f'<div class="rank-card"><small>{esc(label)}</small>'
            f"<strong>#{rank}</strong><span>BK {bk_value(rank):,}</span></div>"
        )
    return f'<div class="rank-grid">{"".join(cards)}</div>' if cards else ""


def ff_boards_table(p):
    ranks = {k: v for k, v in (p.get("ranks") or {}).items() if isinstance(v, (int, float))}
    if not ranks:
        return ""
    rows = sorted(ranks.items(), key=lambda kv: kv[1])
    vals = [v for _s, v in rows]
    lo, hi = min(vals), max(vals)
    body = []
    for src, rk in rows:
        cls = "hi" if rk == lo else ("lo" if rk == hi and hi != lo else "")
        body.append(f'<tr class="{cls}"><td>{esc(src)}</td><td class="rk">{rk}</td></tr>')
    return (
        '<section class="panel">'
        '<p class="kicker">Every Board</p>'
        f"<h3>Spread {lo}–{hi} · {len(rows)} sources</h3>"
        '<div class="table-wrap"><table class="boards">'
        "<thead><tr><th>Source</th><th>Rank</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div></section>"
    )


def ff_related(profiles, p):
    lists = p.get("lists") or {}
    if "The Keep" in lists:
        board = [x for x in profiles if "The Keep" in (x.get("lists") or {})]
        board.sort(key=lambda x: x["lists"]["The Keep"])
        nearby_label = "On The Keep nearby"
        rank_of = lambda x: x["lists"]["The Keep"]
    elif lists.get("The Board") or lists.get("Redraft PPR"):
        board = [x for x in profiles if (x.get("lists") or {}).get("The Board") or (x.get("lists") or {}).get("Redraft PPR")]
        board.sort(key=lambda x: x["lists"].get("The Board") or x["lists"].get("Redraft PPR") or 999)
        nearby_label = "On The Board nearby"
        rank_of = lambda x: x["lists"].get("The Board") or x["lists"].get("Redraft PPR")
    else:
        board = list(profiles)
        nearby_label = "Nearby on the board"
        rank_of = lambda x: 0
    normed = [{**x, "bk": rank_of(x)} for x in board]
    current = {**p, "bk": rank_of(p)}
    return related_players_html(
        normed,
        current,
        lambda r: f"{r['slug']}.html",
        nearby_label=nearby_label,
        pos_label="Same position",
        team_label="Same club",
    )


def render_player_pages(profiles):
    media = {}
    media_path = ROOT / "data" / "player_media.json"
    if media_path.exists():
        media = json.loads(media_path.read_text())
    out_dir = ROOT / "players"
    out_dir.mkdir(parents=True, exist_ok=True)
    news_by_player = defaultdict(list)
    for story in load_news_stories("football"):
        for pl in story.get("players") or []:
            key = pl.get("key") or norm_name(pl.get("name") or "")
            if key:
                news_by_player[key].append(story)

    cards = []
    missing_copy = []
    keep_html = {"index.html"}
    for p in profiles:
        copy = get_copy(p["key"])
        if not copy.get("grafs"):
            missing_copy.append(p["name"])
        med = media.get(p["key"], {})
        img = med.get("image") or ""
        yt = med.get("youtube_id") or ""
        yt_title = med.get("youtube_title") or "Highlight"
        college = med.get("college") or ""
        is_rook = bool(med.get("is_rookie")) or "2026 Rookies" in p["lists"]

        auto_p, auto_m = auto_plus_minus(p)
        plus = list(dict.fromkeys((copy.get("plus") or []) + auto_p))[:5]
        minus = list(dict.fromkeys((copy.get("minus") or []) + auto_m))[:5]
        chips = []
        for label, key in (("Hot", "Hot"), ("Cold", "Cold")):
            if key in p["lists"]:
                cls = " hot" if key == "Hot" else " cold"
                chips.append(f'<span class="chip{cls}">{esc(label)} #{p["lists"][key]}</span>')
        chip_html = f'<div class="chips">{"".join(chips)}</div>' if chips else ""

        photo = ""
        if img:
            photo = f'<img src="{asset(img, 1)}" alt="{esc(face_alt(p["name"]))}" />'
        else:
            photo = f'<img src="{asset("img/logo.jpg", 1)}" alt="{esc(card_alt(p["name"]))}" />'

        video = ""
        if yt:
            kind = "college" if is_rook else "2025 season"
            video = f"""
    <p class="kicker" style="margin-top:22px">Tape · {esc(kind)}</p>
    <h3>{esc(yt_title)}</h3>
    <div class="video-wrap">
      <iframe src="https://www.youtube-nocookie.com/embed/{esc(yt)}" title="{esc(yt_title)}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen loading="lazy"></iframe>
    </div>"""

        news_hits = news_by_player.get(p["key"]) or []
        news_block = ""
        if news_hits:
            lis = "".join(
                f'<li><a href="../news/{esc(s["slug"])}.html">{esc(s.get("headline") or "Update")}</a> '
                f'<span class="news-meta">{esc(CATEGORY_LABEL.get(s.get("category") or "", ""))} · '
                f'{esc(news_when(s.get("updated") or s.get("published") or ""))}</span></li>'
                for s in news_hits[:5] if s.get("slug")
            )
            news_block = (
                '<p class="kicker" style="margin-top:22px">BK News</p>'
                f'<ul class="source-list">{lis}</ul>'
            )

        body = f"""
    <p class="kicker">Player File · {esc(p["pos"])} {esc(p["team"])}</p>
    <div class="player-hero">
      {photo}
      <div>
        <h1>{esc(p["name"])}</h1>
        <p class="note">{esc(p["pos"])} · {esc(p["team"])}{" · " + esc(str(p["age"])) if p.get("age") else ""}{" · " + esc(college) if college else ""}</p>
        {chip_html}
      </div>
    </div>
    {ff_facts(p, college, is_rook)}
    {ff_rank_cards(p)}
    {take_html("The tape", copy.get("grafs") or [], limit=2)}
    {plusminus_html(plus, minus)}
    {rank_spread_graph(p.get("ranks") or {}, fill="#c8102e")}
    {ff_boards_table(p)}
    {video}
    {news_block}
    {ff_related(profiles, p)}
    <p class="note" style="margin-top:18px"><a href="index.html">All player pages</a> · <a href="../the-keep.html">The Keep</a> · <a href="../board.html">The Board</a> · <a href="../recent-trades.html?q={esc(p["name"])}">Recent deals</a> · <a href="../hot-n-cold.html">Hot 'n' Cold</a> · <a href="../news.html">BK News</a> · <a href="../trade-superflex.html">Trade calculator</a></p>
    """
        seo_title, seo_desc = ff_player_seo(p)
        player_url_abs = f"https://ballkeep.com/players/{p['slug']}.html"
        extra_ld = [
                    breadcrumb_jsonld([
                        ("Ball Keep", "https://ballkeep.com/"),
                        ("Players", "https://ballkeep.com/players/"),
                        (p["name"], player_url_abs),
                    ]),
                    person_jsonld(
                        p["name"],
                        player_url_abs,
                        pos=p.get("pos") or "",
                        team=p.get("team") or "",
                        image=img or "img/logo.jpg",
                        description=seo_desc,
                        sport="American Football",
                    ),
                ]
        if yt:
            extra_ld.append(video_jsonld(
                yt_title, yt, description=seo_desc, brand="Ball Keep",
            ))
        write(
            f"players/{p['slug']}.html",
            page(
                p["name"],
                f"players/{p['slug']}.html",
                body,
                depth=1,
                doc_title=seo_title,
                description=seo_desc,
                image=img or "img/logo.jpg",
                crumbs=breadcrumbs([
                    ("Ball Keep", "../index.html"),
                    ("Players", "index.html"),
                    (p["name"], None),
                ]),
                extra_jsonld=extra_ld,
            ),
        )
        keep_html.add(f"{p['slug']}.html")

        thumb = asset(img, 1) if img else asset("img/logo.jpg", 1)
        cards.append(
            f'<a class="tile player-card" href="{p["slug"]}.html" data-pos="{esc(p.get("pos") or "")}">'
            f'<img src="{thumb}" alt="{esc(face_alt(p["name"]))}" />'
            f'<h3>{esc(p["name"])}</h3>'
            f'<p class="note">{esc(p["pos"])} {esc(p["team"])}</p></a>'
        )

    for old in out_dir.glob("*.html"):
        if old.name not in keep_html:
            old.unlink()

    hub = f"""
    <p class="kicker">Depth Chart · {UPDATED}</p>
    <h1>Player Pages</h1>
    <p class="note">The Keep top 400, The Board (redraft PPR), Superflex redraft, 2026 rookies, and Hot 'n' Cold. Ranks, board dump, tape. Filter by position.</p>
    <p class="note">Position</p>
    <div class="filters" id="hub-pos"><button type="button" class="active" data-pos="all">All</button>
      <button type="button" data-pos="QB">QB</button>
      <button type="button" data-pos="RB">RB</button>
      <button type="button" data-pos="WR">WR</button>
      <button type="button" data-pos="TE">TE</button>
    </div>
    <div class="player-grid">{''.join(cards)}</div>
    {also_on_desk([
        ("../the-keep.html", "The Keep", "Superflex dynasty top 400."),
        ("../board.html", "The Board", "Redraft PPR."),
        ("../news.html", "BK News", "Hourly wire."),
        ("../trade.html", "Trade Calculators", "Price any name."),
    ])}
    """
    hub_js = """<script>
    const box = document.getElementById('hub-pos');
    if (box) box.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const p = b.dataset.pos;
      document.querySelectorAll('.player-grid .player-card').forEach(card => {
        card.style.display = (p === 'all' || card.dataset.pos === p) ? '' : 'none';
      });
    });
    </script>"""
    write("players/index.html", page(
        "Players", "players/index.html", hub, hub_js, depth=1,
        crumbs=breadcrumbs([("Ball Keep", "../index.html"), ("Players", None)]),
        extra_jsonld=[breadcrumb_jsonld([
            ("Ball Keep", "https://ballkeep.com/"),
            ("Players", "https://ballkeep.com/players/"),
        ])],
    ))

    urls = ["https://ballkeep.com/players/"] + [
        f"https://ballkeep.com/players/{p['slug']}.html" for p in profiles
    ]
    if missing_copy:
        print("missing copy", len(missing_copy), "(generic plus/minus used)")
    return urls


def as_trade_players(rows, qb_mult_for_qb=1.0):
    out = []
    for r in rows:
        mult = qb_mult_for_qb if r.get("pos") == "QB" else 1.0
        href = player_url(r["name"], 0) or ""
        out.append({
            "id": slugify(r["name"]),
            "name": r["name"],
            "pos": r.get("pos") or "",
            "team": r.get("team") or "",
            "rank": r["bk"],
            "value": bk_value(r["bk"], mult),
            "href": href,
        })
    return out


def trade_mode_page(mode, payload):
    picks_note = (
        "Future firsts and seconds are priced as equivalent ranks on the same curve."
        if payload.get("picks")
        else "Redraft has no future picks - only the names on this board."
    )
    body = f"""
    <p class="kicker">Trade Calculator · {esc(payload["label"])}</p>
    <h1>{esc(payload["label"])}</h1>
    <p class="note">{esc(payload["blurb"])} {picks_note} Fair means the sides are within 8%.</p>
    <p class="filters">
      <a href="trade.html">All Calculators</a>
      <a href="trade-superflex.html"{' class="active"' if mode == "sf" else ""}>Superflex Dynasty</a>
      <a href="trade-sf-redraft.html"{' class="active"' if mode == "sfr" else ""}>Superflex Redraft</a>
      <a href="trade-1qb.html"{' class="active"' if mode == "oneqb" else ""}>1QB Dynasty</a>
      <a href="trade-ppr.html"{' class="active"' if mode == "ppr" else ""}>Redraft PPR</a>
      <a href="trade-classic.html"{' class="active"' if mode == "classic" else ""}>The Classic</a>
      <a href="trade-standard.html"{' class="active"' if mode == "std" else ""}>Redraft Standard</a>
    </p>
    <div id="trade-app" class="trade-app"></div>
    """
    blob = json.dumps(payload, ensure_ascii=False)
    extra = f"<script>window.BK_TRADE = {blob};</script>\n<script src=\"js/trade.js\"></script>"
    write(payload["file"], page(payload["label"], payload["file"], body, extra))


def write_trade_pages(keep, board, ppr, std, classic=None):
    modes = {
        "sf": {
            "id": "sf",
            "file": "trade-superflex.html",
            "label": "Superflex Dynasty",
            "blurb": "Uses The Keep Superflex Dynasty ranks. Rank 1 is 12,000 BK Value. Quarterbacks keep full Superflex price.",
            "players": as_trade_players(keep),
            "picks": pick_assets(),
        },
        "sfr": {
            "id": "sfr",
            "file": "trade-sf-redraft.html",
            "label": "Superflex Redraft",
            "blurb": "Uses the Redraft Superflex ranks. This-year Superflex. No dynasty pick chips.",
            "players": as_trade_players(board),
            "picks": [],
        },
        "oneqb": {
            "id": "oneqb",
            "file": "trade-1qb.html",
            "label": "1QB Dynasty",
            "blurb": "Same Ball Keep ranks as Superflex Dynasty, but quarterbacks are taxed to 38% of that value because there is no second QB slot.",
            "players": as_trade_players(keep, 0.38),
            "picks": pick_assets(),
        },
        "ppr": {
            "id": "ppr",
            "file": "trade-ppr.html",
            "label": "Redraft PPR",
            "blurb": "Uses The Board Redraft PPR ranks. Same curve, one-year contest, no dynasty pick chips.",
            "players": as_trade_players(ppr),
            "picks": [],
        },
        "classic": {
            "id": "classic",
            "file": "trade-classic.html",
            "label": "The Classic",
            "blurb": "Uses The Classic 0.5 PPR ranks. Half a point per catch. Same curve, no dynasty pick chips.",
            "players": as_trade_players(classic or []),
            "picks": [],
        },
        "std": {
            "id": "std",
            "file": "trade-standard.html",
            "label": "Redraft Standard",
            "blurb": "Uses the Redraft Standard board rank after the PPR-to-Standard positional taxes.",
            "players": as_trade_players(std),
            "picks": [],
        },
    }
    (ROOT / "data/trade-values.json").write_text(json.dumps({
        "updated": UPDATED,
        "algorithm": ALGORITHM,
        "modes": modes,
    }, indent=2, default=str))
    for key, payload in modes.items():
        trade_mode_page(key, payload)

    tiles = [
        ("trade-superflex.html", "Superflex Dynasty", "The Keep ranks. QBs are first-round assets."),
        ("trade-sf-redraft.html", "Superflex Redraft", "Redraft Superflex ranks. This year only."),
        ("trade-1qb.html", "1QB Dynasty", "Same Keep ranks, quarterbacks taxed to 38% of Superflex value."),
        ("trade-ppr.html", "The Board (PPR)", "One-year PPR board. No future picks."),
        ("trade-classic.html", "The Classic (0.5 PPR)", "Half a point per catch. This year only."),
        ("trade-standard.html", "Redraft Standard", "One-year Standard board after the catch-tax."),
        ("recent-trades.html", "Recent Deals", "Type a player. Pull every package on the trade tape."),
    ]
    hub = f"""
    <p class="kicker">Trade Calculators</p>
    <h1>Six Calculators, One Curve</h1>
    <p class="note">Every name on a Ball Keep list has a rank. That rank becomes <strong>BK Value</strong>: rank 1 is 12,000, and the number falls on a decaying curve so the drop from 1 to 2 is larger than 50 to 51. A late first (~rank 28) is about half the 1.01. Rank 80 still holds about 29%. Trade math is just adding those numbers on two sides.</p>
    <p class="note">Use Superflex for two-QB leagues, 1QB when a passer is just another starter, and the redraft calculators when the deal is for this season only.</p>
    <div class="grid" style="margin-top:16px">
      {''.join(f'<a class="tile" href="{h}"><h3>{esc(t)}</h3><p>{esc(p)}</p></a>' for h,t,p in tiles)}
    </div>
    {faq_html(TRADE_FAQ, heading="How BK Value prices a trade.")}
    """
    write("trade.html", board_page(
        "Trade Calculators", "trade.html", hub,
        extra_jsonld=[faq_jsonld(TRADE_FAQ)],
    ))


def write_recent_trades_page(deals):
    payload = json.dumps(deals, ensure_ascii=False)
    nicks = {
        "jsn": "jaxon smith-njigba",
        "jj": "justin jefferson",
        "cmc": "christian mccaffrey",
        "chase": "jamarr chase",
        "sun god": "amon-ra st brown",
        "arsb": "amon-ra st brown",
        "st brown": "amon-ra st brown",
        "btj": "brian thomas",
        "tlaw": "trevor lawrence",
        "bijan": "bijan robinson",
        "gibbs": "jahmyr gibbs",
        "puka": "puka nacua",
        "maye": "drake maye",
        "allen": "josh allen",
        "jeanty": "ashton jeanty",
        "mhj": "marvin harrison",
        "marv": "marvin harrison",
        "ceedee": "ceedee lamb",
        "cd": "ceedee lamb",
        "ajb": "a j brown",
        "bowers": "brock bowers",
        "saquon": "saquon barkley",
        "lamar": "lamar jackson",
        "mahomes": "patrick mahomes",
        "kyler": "kyler murray",
        "ladd": "ladd mcconkey",
        "tet": "tetairoa mcmillan",
        "breece": "breece hall",
        "cmcaffrey": "christian mccaffrey",
    }
    chips = [
        "Josh Allen", "Drake Maye", "Ja'Marr Chase", "Jaxon Smith-Njigba",
        "Jahmyr Gibbs", "Ashton Jeanty", "Brock Bowers", "Christian McCaffrey",
        "A.J. Brown", "Brian Thomas Jr.", "Kyler Murray",
    ]
    chip_html = "".join(
        f'<button type="button" class="deal-chip" data-q="{esc(n)}">{esc(n)}</button>'
        for n in chips
    )
    body = f"""
    <p class="kicker">Trade Tape · {UPDATED}</p>
    <h1>Recent Deals</h1>
    <p class="note">Type a player. Superflex, 1QB, asking prices, and deals that actually closed. BK Value on both sides.</p>
    <div class="trade-search deals-search">
      <label for="deal-q">Player</label>
      <input id="deal-q" type="search" placeholder="JSN, CMC, Sun God, Jeanty…" autocomplete="off" />
      <p class="note" id="deal-status" style="margin:10px 0 0"></p>
      <div class="filters" style="margin-top:12px">
        <button type="button" class="active" data-fmt="all">All formats</button>
        <button type="button" data-fmt="sf">Superflex</button>
        <button type="button" data-fmt="oneqb">1QB</button>
        <button type="button" data-kind="all" class="active">Closed + asking</button>
        <button type="button" data-kind="closed">Closed</button>
        <button type="button" data-kind="asking">Asking price</button>
      </div>
      <p class="note" style="margin-top:8px">Jump</p>
      <div class="filters">{chip_html}</div>
    </div>
    <div id="deal-list"></div>
    """
    extra = f"""<script>
    const DEALS = {payload};
    const NICKS = {json.dumps(nicks)};
    function norm(s) {{
      let n = (s || '').toLowerCase().replace(/[.'’]/g, ' ').replace(/\\b(jr|sr|iii|ii|iv)\\b/g, ' ');
      n = n.replace(/\\s+/g, ' ').trim();
      return NICKS[n] || n;
    }}
    function fmt(n) {{ return (n || 0).toLocaleString(); }}
    function sideHtml(items, q) {{
      return items.map(x => {{
        const hit = q && norm(x.name).includes(q);
        const meta = x.kind === 'pick' ? 'Pick' : ((x.pos || '') + ' ' + (x.team || '')).trim();
        return '<li class="' + (hit ? 'deal-hit' : '') + '"><strong>' + x.name + '</strong>' +
          (meta ? '<small>' + meta + '</small>' : '') +
          '<span class="val">' + fmt(x.value) + '</span></li>';
      }}).join('');
    }}
    let fmtFilter = 'all', kindFilter = 'all';
    function render() {{
      const raw = document.getElementById('deal-q').value;
      const q = norm(raw);
      const rows = DEALS.filter(d => {{
        const okF = fmtFilter === 'all' || d.format_id === fmtFilter;
        const okK = kindFilter === 'all' || d.kind === kindFilter;
        if (!okF || !okK) return false;
        if (!q) return true;
        return d.names.some(n => norm(n).includes(q) || q.includes(norm(n)));
      }});
      const status = document.getElementById('deal-status');
      if (q) {{
        status.textContent = rows.length
          ? rows.length + ' deal' + (rows.length === 1 ? '' : 's') + ' involving ' + raw.trim() + '.'
          : 'Nobody on the tape named ' + raw.trim() + '. Try Chase, Maye, Jeanty, JSN.';
      }} else {{
        status.textContent = rows.length + ' packages on the tape. Newest first.';
      }}
      const root = document.getElementById('deal-list');
      if (!rows.length) {{
        root.innerHTML = '<div class="panel"><p class="note">Empty drawer. Clear the search or pick a chip.</p></div>';
        return;
      }}
      root.innerHTML = rows.map(d => {{
        const cls = d.label === 'Fair Trade' ? 'fair' : (d.label.indexOf('A') >= 0 ? 'a' : 'b');
        const tag = d.kind === 'asking' ? 'Asking price' : 'Closed';
        return '<article class="deal ' + cls + '">' +
          '<header><p class="kicker" style="margin:0">' + d.date + ' · ' + d.format + ' · ' + tag + '</p>' +
          '<h3>' + d.label + '</h3>' +
          '<p class="note">' + d.league + ' · ' + d.source + '</p></header>' +
          '<div class="deal-grid">' +
            '<div class="deal-side"><h4>Side A · ' + fmt(d.total_a) + '</h4><ul>' + sideHtml(d.a, q) + '</ul></div>' +
            '<p class="deal-vs">vs</p>' +
            '<div class="deal-side"><h4>Side B · ' + fmt(d.total_b) + '</h4><ul>' + sideHtml(d.b, q) + '</ul></div>' +
          '</div>' +
          '<p class="deal-blurb">' + d.blurb + '</p>' +
          '<p class="note"><a href="trade-superflex.html">Run it on the calculator</a></p>' +
        '</article>';
      }}).join('');
    }}
    document.getElementById('deal-q').addEventListener('input', render);
    document.querySelectorAll('.deals-search [data-fmt]').forEach(b => b.addEventListener('click', () => {{
      document.querySelectorAll('.deals-search [data-fmt]').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); fmtFilter = b.dataset.fmt; render();
    }}));
    document.querySelectorAll('.deals-search [data-kind]').forEach(b => b.addEventListener('click', () => {{
      document.querySelectorAll('.deals-search [data-kind]').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); kindFilter = b.dataset.kind; render();
    }}));
    document.querySelectorAll('.deal-chip').forEach(b => b.addEventListener('click', () => {{
      document.getElementById('deal-q').value = b.dataset.q; render();
    }}));
    const params = new URLSearchParams(location.search);
    if (params.get('q')) document.getElementById('deal-q').value = params.get('q');
    render();
    </script>"""
    write("recent-trades.html", page("Recent Deals", "recent-trades.html", body, extra))


def _story_when(story: dict) -> str:
    return (story.get("updated") or story.get("published") or "").strip()


def player_image_entries() -> dict:
    specs = [
        (ROOT / "data/player_media.json", "https://ballkeep.com/players/{slug}.html"),
        (ROOT / "data/bb-media.json", "https://ballkeep.com/bb/players/{slug}.html"),
        (ROOT / "data/pl-media.json", "https://ballkeep.com/pl/players/{slug}.html"),
    ]
    out = {}
    for path, tmpl in specs:
        if not path.exists():
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        recs = doc.values() if isinstance(doc, dict) else doc
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            slug = rec.get("slug")
            img = rec.get("image") or ""
            name = rec.get("name") or ""
            if not slug or not img or "logo" in img:
                continue
            loc = tmpl.format(slug=slug)
            out[loc] = {"loc": loc, "image": abs_img(img, img), "image_title": name}
    return out


def merge_sitemap_images(urls: list) -> list:
    images = player_image_entries()
    merged = []
    seen = set()
    for u in urls:
        loc = u.get("loc") if isinstance(u, dict) else u
        if not loc or loc in seen:
            continue
        seen.add(loc)
        if loc in images:
            merged.append(images[loc])
        else:
            merged.append(loc)
    return merged


NEWS_FEEDS = [
    ("football", "Ball Keep", "BK News", "https://ballkeep.com/news.html", "https://ballkeep.com/news/{slug}.html", "feed.xml"),
    ("baseball", "BaseKeep", "BaseKeep News", "https://ballkeep.com/bb/news.html", "https://ballkeep.com/bb/news/{slug}.html", "bb/feed.xml"),
    ("basketball", "BasketKeep", "BasketKeep News", "https://ballkeep.com/bk/news.html", "https://ballkeep.com/bk/news/{slug}.html", "bk/feed.xml"),
    ("soccer", "PitchKeep", "PitchKeep News", "https://ballkeep.com/pl/news.html", "https://ballkeep.com/pl/news/{slug}.html", "pl/feed.xml"),
]


def write_discovery_feeds():
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
    news_entries = []
    for sport, brand, feed_title, hub, tmpl, dest in NEWS_FEEDS:
        stories = load_news_stories(sport)
        items = []
        for s in stories[:40]:
            slug = s.get("slug")
            if not slug:
                continue
            loc = tmpl.format(slug=slug)
            when = _story_when(s)
            items.append({
                "title": s.get("headline") or "Update",
                "link": loc,
                "description": s.get("blurb") or s.get("summary") or "",
                "date": when,
                "guid": loc,
            })
        write(dest, rss_xml(
            title=f"{feed_title} - {brand}",
            link=hub,
            description=f"Hourly {sport} injury, roster, and coach tape from {brand}.",
            items=items,
            self_url=f"https://ballkeep.com/{dest}" if dest != "feed.xml" else "https://ballkeep.com/feed.xml",
        ))
        for s in stories:
            slug = s.get("slug")
            when = _story_when(s)
            if not slug or not when:
                continue
            try:
                dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt < cutoff:
                continue
            news_entries.append({
                "loc": tmpl.format(slug=slug),
                "title": s.get("headline") or "Update",
                "date": when,
                "publication": brand,
            })
    (ROOT / "sitemap-news.xml").write_text(news_sitemap_xml(news_entries))
    return len(news_entries)


def write_not_found_page():
    body = """
    <section class="panel">
      <p class="kicker">404</p>
      <h1>That page is not on this board.</h1>
      <p class="note">The Keep, The Board, BK News, and the other three sports are still here.</p>
      <div class="grid-3">
        <a class="tile" href="index.html"><h3>Ball Keep</h3><p>Superflex dynasty and redraft PPR.</p></a>
        <a class="tile" href="the-keep.html"><h3>The Keep</h3><p>Football top 400.</p></a>
        <a class="tile" href="news.html"><h3>BK News</h3><p>Hourly football wire.</p></a>
        <a class="tile" href="bb/index.html"><h3>BaseKeep</h3><p>Dynasty baseball.</p></a>
        <a class="tile" href="bk/index.html"><h3>BasketKeep</h3><p>Dynasty basketball.</p></a>
        <a class="tile" href="pl/index.html"><h3>PitchKeep</h3><p>Premier League ranks.</p></a>
      </div>
    </section>
    """
    write("404.html", page("Page not found", "404.html", body, robots="noindex, follow"))


def main():
    pfn = parse_pfn(ROOT / "data/pfn-dynasty.txt")
    nfl = parse_nfl_schedule(ROOT / "data/nfl-schedule.txt")
    keep, long_board, sources = aggregate(pfn)
    if len(keep) > KEEP_N:
        keep = keep[:KEEP_N]
    if len(long_board) > BOARD_N:
        long_board = long_board[:BOARD_N]
    ppr, std, classic = redraft_lists()
    media = load_player_media()
    ages = load_age_bank()
    apply_media_ages(keep, media, ages)
    apply_media_ages(long_board, media, ages)
    apply_media_ages(ppr, media, ages)
    apply_media_ages(std, media, ages)
    apply_media_ages(classic, media, ages)
    sf_redraft = superflex_redraft(keep, ppr)
    apply_media_ages(sf_redraft, media, ages)
    board = ppr
    profiles = collect_profiles(keep, ppr, std, sf_redraft, classic)
    apply_media_ages(profiles, media, ages)
    (ROOT / "data" / "player_roster.json").write_text(json.dumps(profiles, indent=2))

    (ROOT / "data/the-keep.json").write_text(json.dumps({
        "updated": UPDATED,
        "sources": list(sources),
        "players": keep,
    }, indent=2))
    (ROOT / "data/board.json").write_text(json.dumps({
        "format": "redraft PPR",
        "updated": UPDATED,
        "players": board,
    }, indent=2))

    write_trade_pages(keep, sf_redraft, ppr, std, classic)
    deals = enrich_deals(keep, bk_value, pick_assets(), norm_name)
    write_recent_trades_page(deals)

    # HOME
    latest_news = load_news_stories("football")[:5]
    extra_news = ""
    if latest_news:
        extra_news = (
            '<div class="news-list">'
            + "".join(news_card(s) for s in latest_news)
            + "</div>"
            '<p class="note" style="margin-top:12px"><a href="news.html">All BK News</a></p>'
        )
    home_body = f"""
    {masthead("Football rankings", wordmark(), "Dynasty · Redraft")}
    <section class="desk-block main home-intro">
      <p class="kicker">Updated {UPDATED}</p>
      <p class="note">The Keep is Superflex Dynasty. The Board is Redraft PPR.</p>
      <div class="home-leads">
        <a class="tile lead keep" href="the-keep.html">
          <h3>The Keep</h3>
          <p class="lead-sub">Dynasty · top 400</p>
          <p>32 boards mashed into one rank.</p>
        </a>
        <a class="tile lead board" href="board.html">
          <h3>The Board</h3>
          <p class="lead-sub">Redraft · PPR</p>
          <p>Full-PPR, this year. Thirteen boards averaged.</p>
        </a>
      </div>
    </section>
    {desk_block("lists", "Lists", "The other boards.", "Redraft, rookies, the market tape, and the slates.", [
        ("redraft-superflex.html", "Redraft Superflex", "Two-QB, this year."),
        ("the-classic.html", "The Classic", "Half-PPR, this year."),
        ("redraft-standard.html", "Redraft Standard", "No reception point."),
        ("rookies-2026.html", "2026 Rookies", "Drafted class."),
        ("hot-n-cold.html", "Hot 'n' Cold", "Buys and sells."),
        ("recent-trades.html", "Recent Deals", "Packages that closed."),
        ("nfl-schedule.html", "NFL Schedule", "2026 week-by-week."),
        ("mlb-schedule.html", "MLB Schedule", "September slate."),
    ])}
    {desk_block("tools", "Tools", "Calculators and files.", "Price a deal or open a player file.", [
        ("trade.html", "Trade Calculators", "Keep, Board, Classic, 1QB, PPR, Standard."),
        ("players/index.html", "Player Pages", "Keep top 400. Tape, plus/minus."),
    ])}
    {desk_block("extra", "Extra", "News and The X.", "Memes and the wire.", [
        ("the-x.html", "The X", "Memes. Pictures on the card."),
        ("news.html", "BK News", "Injuries, roster, coaches."),
    ], extra_news)}
    {faq_html(HOME_FAQ, heading="How Ball Keep works.")}
    """
    write("index.html", page(
        "Home", "index.html", home_body,
        extra_jsonld=[website_jsonld("Ball Keep"), faq_jsonld(HOME_FAQ)],
        modified=LASTMOD,
    ))

    # THE KEEP
    def src_td(r, name):
        v = (r.get("ranks") or {}).get(name)
        return f'<td class="desk-only">{v if v not in (None, "") else "-"}</td>'

    def keep_extra(r):
        return (
            f'<td class="desk-only">{r["avg"]}</td>'
            + f'<td class="desk-only">{r["n"]}</td>'
            + src_td(r, "PFN (Katz/Soppe)")
            + src_td(r, "KeepTradeCut SF")
            +             f'<td class="c-val val">{fmt_val(r["value"])}</td>'
        )
    keep_chips, keep_js = pos_filter("keep-pos")
    keep_body = f"""
    <p class="kicker">Superflex Dynasty · Super Aggregate · {len(KEEP_SOURCES)} boards</p>
    <h1>The Keep</h1>
    <p class="note">This is the big one. Superflex Dynasty. Top 400. {len(KEEP_SOURCES)} boards. Half the vote is the four long boards, half is everyone else. The Board next door is Redraft PPR - this year, one quarterback, a point per catch.</p>
    {rank_search_bar(keep_chips)}
    <div class="panel">{rank_table(keep, ["Super", "Boards", "PFN", "KTC", "BK Value"], keep_extra, media=media, faces=True, show_age=True)}</div>
    {value_bars(keep, 12, "#c8102e", "Keep value graph")}
    {sources_panel(KEEP_SOURCES)}
    {faq_html(KEEP_FAQ, heading="How The Keep is built.")}
    """
    write("the-keep.html", board_page(
        "The Keep", "the-keep.html", keep_body, keep_js,
        extra_jsonld=[
            rank_list_jsonld(
                "The Keep 2026 Superflex Dynasty Rankings",
                "https://ballkeep.com/the-keep.html",
                keep,
                lambda r: f"https://ballkeep.com/players/{slugify(r['name'])}.html",
                description="Superflex dynasty top 400 from 32 boards.",
            ),
            faq_jsonld(KEEP_FAQ),
        ],
    ))

    # REDRAFT
    def ppr_extra(r):
        return (
            f'<td class="desk-only">{r["avg"]}</td>'
            f'<td class="desk-only">{r["n"]}</td>'
            f'<td class="desk-only">{r["yates"]}</td>'
            f'<td class="desk-only">{r["fp"]}</td>'
            f'<td class="desk-only">{r["karabell"]}</td>'
            f'<td class="c-val val">{fmt_val(r["value"])}</td>'
        )
    board_chips, board_js = pos_filter("board-pos")
    ppr_body = f"""
    <p class="kicker">2026 Redraft · PPR · {len(PPR_SOURCES)} boards</p>
    <h1>The Board</h1>
    <p class="note">This is the redraft PPR list. Full-PPR, 1QB, {PPR_N} names. Mean of {len(PPR_SOURCES)} boards: Field Yates, FantasyPros PPR ECR, Eric Karabell Flex, then ten more from Derek Brown, Andrew Erickson, Pat Fitzmaurice, Chris Welsh, CBS, Yahoo, Draft Sharks, RotoWire, NFL.com, and 4for4. Unranked on a board is a skip. Kickers and DST are omitted so this stays a skill-player draft sheet. BK Value uses this list's rank on the same curve as dynasty. Sort by position with the chips.</p>
    {rank_search_bar(board_chips)}
    <div class="panel">{rank_table(ppr, ["Avg", "Boards", "Yates", "FP ECR", "Karabell", "BK Value"], ppr_extra, media=media, faces=True, show_age=True)}</div>
    {value_bars(ppr, 12, "#c8102e", "Board value graph")}
    {sources_panel(PPR_SOURCES, heading="Boards in This Aggregate")}
    {faq_html(BOARD_FAQ, heading="How The Board is built.")}
    """
    write("board.html", board_page(
        "The Board", "board.html", ppr_body, board_js,
        extra_jsonld=[
            rank_list_jsonld(
                "The Board 2026 Redraft PPR Rankings",
                "https://ballkeep.com/board.html",
                ppr,
                lambda r: f"https://ballkeep.com/players/{slugify(r['name'])}.html",
                description="Redraft PPR skill-player board from thirteen public lists.",
            ),
            faq_jsonld(BOARD_FAQ),
        ],
    ))
    write("redraft-ppr.html", page(
        "The Board",
        "redraft-ppr.html",
        '<p class="kicker">Moved</p><h1>The Board</h1>'
        '<p class="note">Redraft PPR now lives on <a href="board.html">The Board</a>.</p>'
        '<p><a class="cta" href="board.html">The Board · Redraft PPR</a></p>',
    ))

    std_chips, std_js = pos_filter("std-pos")
    std_body = f"""
    <p class="kicker">2026 Redraft · Standard</p>
    <h1>Redraft Standard</h1>
    <p class="note">Standard (no extra point per catch) is a different sport than PPR. We start from the PPR consensus above, then apply Ball Keep positional taxes used across major STD vs PPR deltas: running backs −4.5 ranks, receivers +3, tight ends +2, quarterbacks +0.5. Result: Bijan / Gibbs / CMC / Henry / Taylor climb; Chase / Puka / JSN still go early but not as automatic 1.01s. Sort by position with the chips.</p>
    {rank_search_bar(std_chips)}
    <div class="panel">{rank_table(std, ["Adj. Score", "BK Value"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="c-val val">{fmt_val(r["value"])}</td>', media=media, faces=True, show_age=True)}</div>
    {value_bars(std, 12, "#c8102e", "Standard value graph")}
    {sources_panel(PPR_SOURCES + [("Ball Keep Standard Tax", "", "RB −4.5 ranks, WR +3, TE +2, QB +0.5 applied to the PPR consensus.")], heading="Boards in This Aggregate")}
    """
    write("redraft-standard.html", board_page("Redraft Standard", "redraft-standard.html", std_body, std_js))

    classic_chips, classic_js = pos_filter("classic-pos")
    classic_js = classic_js + draft_check_js()
    classic_body = f"""
    <p class="kicker">2026 Redraft · 0.5 PPR</p>
    <h1>The Classic</h1>
    <p class="note">Half-PPR is the format most rooms actually run. We start from the same 13-board PPR mean as The Board, then apply half the Standard tax: running backs −2.25 ranks, receivers +1.5, tight ends +1, quarterbacks +0.25. RBs climb versus full PPR. Chase and Puka still go early, just not as automatic 1.01s. The Board next door is full PPR. Standard is zero. Sort by position with the chips. Check a name when they are off the board in your room. Crossed-off names stay on the list until you refresh.</p>
    {rank_search_bar(classic_chips)}
    <div class="panel">{rank_table(classic, ["Adj. Score", "BK Value"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="c-val val">{fmt_val(r["value"])}</td>', media=media, faces=True, show_age=True, draft_check=True)}</div>
    {value_bars(classic, 12, "#c8102e", "Classic value graph")}
    {sources_panel(PPR_SOURCES + [("Ball Keep Half-PPR Tax", "", "RB −2.25 ranks, WR +1.5, TE +1, QB +0.25 applied to the PPR consensus.")], heading="Boards in This Aggregate")}
    """
    write("the-classic.html", board_page(
        "The Classic", "the-classic.html", classic_body, classic_js,
        extra_jsonld=[
            rank_list_jsonld(
                "The Classic 2026 Half-PPR Rankings",
                "https://ballkeep.com/the-classic.html",
                classic,
                lambda r: f"https://ballkeep.com/players/{slugify(r['name'])}.html",
                description="Redraft 0.5 PPR skill-player board.",
            ),
        ],
    ))

    # ROOKIES
    rook_rows = []
    fp_rook = {norm_name(n): r for n, r in load_rank_names("fp-rookies").items()}
    for r in ROOKIES:
        fp = fp_rook.get(norm_name(r["name"])) or r["fp"]
        nums = [x for x in (r["dd"], fp, r["pff"]) if x]
        avg = round(sum(nums) / len(nums), 2) if nums else 99.0
        rook_rows.append({**r, "bk": 0, "avg": avg, "dd": r["dd"] or "-", "fp": fp or "-", "pff": r["pff"] or "-", "blurb": r["value"]})
    rook_rows.sort(key=lambda r: r["avg"])
    for i, r in enumerate(rook_rows, 1):
        r["bk"] = i
    attach_values(rook_rows)
    rook_body = f"""
    <p class="kicker">2026 NFL Draft Class</p>
    <h1>Notable Drafted Rookies</h1>
    <p class="note">Superflex rookie consensus from Dynasty Dealer (13-analyst team board, July 30), FantasyPros Superflex Rookie ECR (August), and PFF's Superflex rookie column (Love / Mendoza / Tate locked 1-2-3). BK Value uses this rookie-board rank on the same curve as The Keep. The note is startup / rookie-draft language, not salary-cap dollars.</p>
    {rank_search_bar()}
    <div class="panel">{rank_table(rook_rows, ["Avg", "Dealer", "FP", "PFF", "BK Value", "Note"], lambda r: f'<td class="desk-only">{r["avg"]}</td><td class="desk-only">{r["dd"]}</td><td class="desk-only">{r["fp"]}</td><td class="desk-only">{r["pff"]}</td><td class="c-val val">{fmt_val(r["value"])}</td><td class="note desk-only">{esc(r["blurb"])}</td>')}</div>
    {value_bars(rook_rows, 12, "#c8102e", "Rookie value graph")}
    {sources_panel(ROOKIE_SOURCES, heading="Boards in This Aggregate")}
    """
    write("rookies-2026.html", board_page("2026 Rookies", "rookies-2026.html", rook_body))

    # HOT COLD
    def hc_cards(items, cls):
        out = []
        for i, x in enumerate(items, 1):
            out.append(
                f'<article class="tile {cls}"><span class="badge">{i}</span> '
                f'<h3>{player_anchor(x["name"])} <span class="pos {esc(x["pos"])}">{esc(x["pos"])}</span> {esc(x["team"])}</h3>'
                f'<p>{esc(x["why"])}</p><p class="note">Source: {esc(x["src"])}</p></article>'
            )
        return "".join(out)
    hc_body = f"""
    <p class="kicker">Market Tape · {UPDATED}</p>
    <h1>BK Hot 'n' Cold</h1>
    <p class="note">Rising names to Buy and aging / overpriced names to Sell, pulled from PlayerProfiler (Aug 7), FantasyPros dynasty trade columns (Aug 9 and August sell list), Sports Illustrated preseason risers (Aug 25), The Athletic dynasty sells (Aug 26), plus DLF, Sports Arena, and Draft Sharks camp notes.</p>
    <div class="grid">
      <div>
        <h3 class="hc-hot">Hot: Buy</h3>
        {hc_cards(HOT, "hot")}
      </div>
      <div>
        <h3 class="hc-cold">Cold: Sell</h3>
        {hc_cards(COLD, "cold")}
      </div>
    </div>
    {sources_panel([
        ("PlayerProfiler", "https://www.playerprofiler.com/article/dynasty-trade-targets-2026-buy-low-sell-high-before-kickoff/", "Buy low / sell high, Aug 7."),
        ("FantasyPros", "https://www.fantasypros.com/2026/08/14-players-to-sell-in-dynasty-leagues-2026-fantasy-football/", "Dynasty sells and trade-now notes, August."),
        ("Sports Illustrated", "https://www.si.com/onsi/fantasy/rankings/parker-washington-headlines-dynasty-fantasy-football-risers-making-the-biggest-leap-in-2026", "Preseason risers, Aug 25."),
        ("The Athletic", "https://www.nytimes.com/athletic/7538068/2026/08/26/fantasy-football-top-5-dynasty-sells-treveyon-henderson/", "Top dynasty sells, Aug 26."),
        ("Draft Sharks", "https://www.draftsharks.com/dynasty-rankings/superflex", "Camp market notes."),
    ], heading="Boards in This Aggregate")}
    """
    write("hot-n-cold.html", board_page("Hot 'n' Cold", "hot-n-cold.html", hc_body))

    # LONG BOARD
    def board_extra(r):
        return (
            src_td(r, "PFN (Katz/Soppe)")
            + src_td(r, "Dynasty Nerds")
            + src_td(r, "FantasyPros ECR")
            + src_td(r, "KeepTradeCut SF")
            + f'<td class="desk-only">{r["avg"]}</td>'
            + f'<td class="desk-only">{r["n"]}</td>'
            + f'<td class="c-val val">{fmt_val(r["value"])}</td>'
        )
    def board_redraft_extra(r):
        keep_r = r.get("keep") or "-"
        ppr_r = r.get("ppr") or "-"
        return (
            f'<td class="desk-only">{keep_r}</td>'
            f'<td class="desk-only">{ppr_r}</td>'
            f'<td class="desk-only">{r["avg"]}</td>'
            f'<td class="c-val val">{fmt_val(r["value"])}</td>'
        )
    sf_chips, sf_js = pos_filter("sf-pos")
    sf_body = f"""
    <p class="kicker">Superflex Redraft · this year</p>
    <h1>Redraft Superflex</h1>
    <p class="note">This list is Superflex for this season - {len(sf_redraft)} names. The Keep is Superflex Dynasty. The Board is Redraft PPR. Quarterbacks stay expensive because you start two of them. Skill players lean on the PPR board. Use this for redraft startups that start two quarterbacks. Sort by position with the chips.</p>
    {rank_search_bar(sf_chips)}
    <div class="panel">{rank_table(sf_redraft, ["Keep SF", "PPR", "Score", "BK Value"], board_redraft_extra, media=media, faces=True, show_age=True)}</div>
    {value_bars(sf_redraft, 12, "#1e8fc2", "Superflex redraft value graph")}
    {sources_panel([
        ("The Keep Superflex Dynasty", "https://ballkeep.com/the-keep.html", "QB premium and the long Superflex market."),
        ("Field Yates / FantasyPros PPR", "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php", "This-year skill-player board."),
    ], heading="How Superflex Redraft is built")}
    """
    write("redraft-superflex.html", board_page("Redraft Superflex", "redraft-superflex.html", sf_body, sf_js))

    # NFL schedule
    weeks = sorted({g["week"] for g in nfl})
    nfl_js_games = json.dumps(nfl)
    week_btns = "".join(f'<button type="button" data-week="{w}">W{w}</button>' for w in weeks)
    team_btns = "".join(
        f'<button type="button" data-team="{esc(abbr)}">{esc(abbr)}</button>'
        for abbr in sorted(TEAM_BY_ABBR)
    )
    nfl_body = f"""
    <p class="kicker">2026 NFL Regular Season</p>
    <h1>NFL Schedule</h1>
    <p class="note">Full slate from NFL Football Operations (released May 14). Kickoff is Wednesday, Sept. 9 in Seattle. Filter by week or club for the individual team schedule. International sites: Melbourne, Rio, London, Paris, Madrid, Munich, Mexico City.</p>
    <p class="note">Weeks</p>
    <div class="filters" id="weeks"><button type="button" class="active" data-week="all">All</button>{week_btns}</div>
    <p class="note">Teams</p>
    <div class="filters" id="teams"><button type="button" class="active" data-team="all">All clubs</button>{team_btns}</div>
    <div class="panel table-wrap" id="games"></div>
    """
    nfl_js = f"""<script>
    const GAMES = {nfl_js_games};
    const ABBR = {json.dumps(TEAMS)};
    let week = 'all', team = 'all';
    function render() {{
      const rows = GAMES.filter(g => {{
        const wa = ABBR[g.away], wh = ABBR[g.home];
        const okW = week === 'all' || String(g.week) === String(week);
        const okT = team === 'all' || wa === team || wh === team;
        return okW && okT;
      }});
      const body = rows.map(g => {{
        const loc = g.note ? ` (${{g.note}})` : '';
        const line = g.prep === 'at' ? `${{g.away}} at ${{g.home}}` : `${{g.away}} vs ${{g.home}}`;
        return `<tr><td>W${{g.week}}</td><td>${{g.day}}</td><td><strong>${{line}}</strong>${{loc}}</td><td>${{g.time}} ET</td><td>${{g.tv}}</td></tr>`;
      }}).join('');
      document.getElementById('games').innerHTML = `<table><thead><tr><th>Wk</th><th>Day</th><th>Matchup</th><th>Time</th><th>TV</th></tr></thead><tbody>${{body}}</tbody></table>`;
    }}
    function bind(id, key, setter) {{
      document.getElementById(id).addEventListener('click', e => {{
        const b = e.target.closest('button'); if (!b) return;
        document.querySelectorAll('#' + id + ' button').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        setter(b.dataset[key]);
        render();
      }});
    }}
    bind('weeks', 'week', v => week = v);
    bind('teams', 'team', v => team = v);
    render();
    </script>"""
    write("nfl-schedule.html", board_page("NFL Schedule", "nfl-schedule.html", nfl_body, nfl_js))

    # MLB September
    mlb_games = []
    mlb_html = ROOT / "data/mlb-september.html"
    if mlb_html.exists():
        day = ""
        blob = mlb_html.read_text(errors="replace")
        for token in re.finditer(
            r'<h4 class="amazon passion toptop">([^<]+)</h4>|<span class="right devil">([^<]+)</span>\s*<img[^>]+>\s*<span class="small">([A-Z]{2,3})</span>\s*<span[^>]*>@</span>\s*<img[^>]+>\s*<span class="small">([A-Z]{2,3})</span>',
            blob,
        ):
            if token.group(1):
                day = token.group(1).strip()
            elif day:
                mlb_games.append({
                    "day": day,
                    "time": token.group(2).strip(),
                    "away": token.group(3),
                    "home": token.group(4),
                })
    mlb_abbrs = sorted({g["away"] for g in mlb_games} | {g["home"] for g in mlb_games})
    mlb_btns = "".join(f'<button type="button" data-team="{esc(a)}">{esc(a)}</button>' for a in mlb_abbrs)
    mlb_body = f"""
    <p class="kicker">MLB · Stretch Run</p>
    <h1>Baseball Schedules</h1>
    <p class="note">Today is Aug. 20, 2026 - the regular season wraps Sunday, Sept. 27. Below is the full September slate (Fantasy Nerds / league schedule). Filter by club for that team's remaining games. For the live daily tick, use ESPN's MLB scoreboard. Dynasty baseball prices 2027–2031 heavier than this month's box score; redraft baseball is only this month.</p>
    <div class="filters" id="mlb-teams"><button type="button" class="active" data-team="all">All clubs</button>{mlb_btns}</div>
    <div class="panel table-wrap" id="mlb-games"></div>
    """
    mlb_js = f"""<script>
    const MLB = {json.dumps(mlb_games)};
    let team = 'all';
    function render() {{
      const rows = MLB.filter(g => team === 'all' || g.away === team || g.home === team)
        .map(g => `<tr><td>${{g.day}}</td><td><strong>${{g.away}} @ ${{g.home}}</strong></td><td>${{g.time}}</td></tr>`).join('');
      document.getElementById('mlb-games').innerHTML = `<table><thead><tr><th>Date</th><th>Matchup</th><th>Time</th></tr></thead><tbody>${{rows}}</tbody></table>`;
    }}
    document.getElementById('mlb-teams').addEventListener('click', e => {{
      const b = e.target.closest('button'); if (!b) return;
      document.querySelectorAll('#mlb-teams button').forEach(x => x.classList.remove('active'));
      b.classList.add('active'); team = b.dataset.team; render();
    }});
    render();
    </script>"""
    write("mlb-schedule.html", board_page("MLB Schedule", "mlb-schedule.html", mlb_body, mlb_js))

    # Discord
    disc = """
    <div class="panel discord-hero">
      <img src="img/discord.jpg" alt="Ball Keep circular Discord logo" />
      <p class="kicker">Community</p>
      <h1>Ball Keep on Discord</h1>
      <p class="note">Red primary. White BK. Black ring. The bot is Ball Keep in the server: every Keep rank, every player file, every highlight, and the trade calculator - searchable in Discord the same way they are on the site.</p>
      <a class="cta" href="https://github.com/balsalah51/BallKeep/tree/main/bot">Run the Ball Keep bot</a>
    </div>
    <section class="panel" style="margin-top:16px">
      <p class="kicker">Slash Commands</p>
      <h2>Talk to the bot.</h2>
      <p class="note"><code>/player Josh Allen</code> pulls The Keep rank, BK Value, plus/minus, the 2025 clip, and the player page. <code>/trade</code> is the Superflex / 1QB / PPR / Standard calculator. <code>/deals JSN</code> pulls every recent package on the trade tape. <code>/bbplayer Ohtani</code> is the same file on the baseball boards. <code>/plplayer Haaland</code> is the PitchKeep file - The Pitch rank, picture, long take, 2025/26 tape. <code>/video</code> drops the tape. <code>/quiz</code> hides a Keep rank behind a spoiler. <code>/publish</code> writes the whole site into Discord channels so native search works.</p>
      <div class="grid" style="margin-top:14px">
        <article class="tile"><h3>/player</h3><p>Full file: ranks, value, plus/minus, tape, link.</p></article>
        <article class="tile"><h3>/trade</h3><p>Two sides. Same BK Value curve as the site.</p></article>
        <article class="tile"><h3>/deals</h3><p>Type a name. Every recent package on the trade tape.</p></article>
        <article class="tile"><h3>/video</h3><p>2025 NFL or college highlight from the player page.</p></article>
        <article class="tile"><h3>/keep-or-cut</h3><p>Theatrical buy/sell with Hot 'n' Cold and The Keep.</p></article>
        <article class="tile"><h3>/top + /pos</h3><p>Leaderboards, or just the QBs / RBs / WRs / TEs.</p></article>
        <article class="tile"><h3>/quiz + /hottake</h3><p>Guess a Keep rank. Draw a random buy or sell.</p></article>
        <article class="tile"><h3>/start + /picks</h3><p>Redraft start/sit, plus every future-pick value.</p></article>
        <article class="tile"><h3>/bbplayer</h3><p>BaseKeep file: Keep 400, Lineup, Pitchers, redraft.</p></article>
        <article class="tile"><h3>/bbkeep + /bbwire</h3><p>Diamond boards and the longer redraft waiver list.</p></article>
        <article class="tile"><h3>/plplayer</h3><p>PitchKeep file: The Pitch 250, FPL line, long take, tape.</p></article>
        <article class="tile"><h3>/pitch + /pltrade</h3><p>Premier League boards and the PitchKeep calculator.</p></article>
      </div>
    </section>
    """
    write("discord.html", page("Discord", "discord.html", disc))

    x_body = f"""
    <p class="kicker">Fun tape · not news</p>
    <h1>The X</h1>
    <p class="note">Memes, shitposts, and the jokes the football boards actually laugh at. Pulled from X via Google News - pictures when the wire carries them. Baseball and PitchKeep have their own X pages.</p>
    {x_cards("football", 0, esc)}
    <p class="note" style="margin-top:16px"><a href="bk/the-x.html">BasketKeep The X</a> · <a href="bb/the-x.html">Baseball The X</a> · <a href="pl/the-x.html">PitchKeep The X</a></p>
    """
    write("the-x.html", board_page("The X", "the-x.html", x_body))

    privacy = """
    <section class="panel policy">
      <p class="kicker">Legal</p>
      <h1>Privacy Policy</h1>
      <p class="note">Last updated: August 23, 2026</p>
      <p>Ball Keep ("we," "us," or "this site") respects your privacy. This Privacy Policy explains what information we collect when you visit ballkeep.com (and its BaseKeep, BasketKeep, and PitchKeep sections), how we use it, and the choices you have.</p>

      <h3>Information We Collect</h3>
      <p><strong>Automatically collected information.</strong> Like most websites, we automatically collect certain information when you visit, including your IP address, browser type, device type, pages viewed, and time spent on the site. This is collected through cookies, log files, and similar technologies.</p>
      <p><strong>Information you provide.</strong> We do not require account creation or collect personal information such as your name, email address, or payment details through this site.</p>

      <h3>Cookies</h3>
      <p>We use cookies and similar tracking technologies to:</p>
      <ul>
        <li>Understand how visitors use the site (analytics)</li>
        <li>Remember basic preferences</li>
        <li>Support advertising, if and when ads are enabled on the site</li>
      </ul>
      <p>You can disable cookies through your browser settings. Doing so may affect some site functionality.</p>

      <h3>Advertising</h3>
      <p>This site may display advertisements served by third-party providers, including Google AdSense. Google and its partners may use cookies to serve ads based on your prior visits to this site or other websites. You can learn more about how Google uses data and opt out of personalized advertising by visiting <a href="https://adssettings.google.com/" rel="noopener">Google's Ads Settings</a> and reviewing <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">How Google uses information from sites or apps that use our services</a>.</p>

      <h3>Affiliate Links</h3>
      <p>This site may contain affiliate links, including links to sportsbooks, merchandise retailers, or fantasy sports platforms. If you click one of these links and make a purchase or sign up, we may earn a commission at no additional cost to you.</p>

      <h3>News and Rankings Content</h3>
      <p>Our rankings, trade values, and news summaries aggregate publicly available information from multiple sources, which are credited at the bottom of each board or article. We do not collect personal information through this aggregation process.</p>

      <h3>Analytics</h3>
      <p>We may use third-party analytics services (such as Google Analytics) to understand site traffic and usage patterns. These services may collect information such as your IP address and browsing behavior on this site. This data is used in aggregate and is not used to personally identify you.</p>

      <h3>Children's Privacy</h3>
      <p>This site is not directed at children under 13, and we do not knowingly collect personal information from children under 13.</p>

      <h3>Third-Party Links</h3>
      <p>Our site links to third-party content, including news sources, statistics providers, and fantasy platforms. We are not responsible for the privacy practices of these external sites.</p>

      <h3>Changes to This Policy</h3>
      <p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last updated" date.</p>

      <h3>Contact Us</h3>
      <p>If you have questions about this Privacy Policy, please reach out through the contact information listed on this site.</p>
      <p>Ball Keep is not affiliated with the NFL, MLB, NBA, or Premier League.</p>
    </section>
    """
    write("privacy.html", page("Privacy Policy", "privacy.html", privacy))

    player_urls = render_player_pages(profiles)
    news_urls = render_news_pages()
    sitemap = [
        "https://ballkeep.com/",
        "https://ballkeep.com/privacy.html",
        "https://ballkeep.com/the-keep.html",
        "https://ballkeep.com/news.html",
        "https://ballkeep.com/the-x.html",
        "https://ballkeep.com/trade.html",
        "https://ballkeep.com/recent-trades.html",
        "https://ballkeep.com/trade-superflex.html",
        "https://ballkeep.com/trade-sf-redraft.html",
        "https://ballkeep.com/trade-1qb.html",
        "https://ballkeep.com/trade-ppr.html",
        "https://ballkeep.com/trade-classic.html",
        "https://ballkeep.com/trade-standard.html",
        "https://ballkeep.com/the-classic.html",
        "https://ballkeep.com/redraft-ppr.html",
        "https://ballkeep.com/redraft-superflex.html",
        "https://ballkeep.com/redraft-standard.html",
        "https://ballkeep.com/rookies-2026.html",
        "https://ballkeep.com/hot-n-cold.html",
        "https://ballkeep.com/board.html",
        "https://ballkeep.com/nfl-schedule.html",
        "https://ballkeep.com/mlb-schedule.html",
        "https://ballkeep.com/discord.html",
    ] + news_urls[1:] + player_urls
    bb = write_baseball_site()
    sitemap.extend(bb.get("urls") or [])
    bk = write_basket_site()
    sitemap.extend(bk.get("urls") or [])
    pl = write_pitch_site()
    sitemap.extend(pl.get("urls") or [])
    (ROOT / "sitemap.xml").write_text(sitemap_xml(merge_sitemap_images(sitemap), LASTMOD))
    n_news = write_discovery_feeds()
    write_not_found_page()
    (ROOT / "robots.txt").write_text(robots_txt([
        "https://ballkeep.com/sitemap.xml",
        "https://ballkeep.com/sitemap-news.xml",
    ]))

    cat = write_discord_catalog(keep, board, ppr, std, rook_rows, profiles, nfl, mlb_games, deals, bb, pl, bk, sf_redraft, classic)
    print(
        f"Keep {len(keep)} Board {len(board)} (redraft PPR) Superflex redraft {len(sf_redraft)} NFL games {len(nfl)} MLB {len(mlb_games)} "
        f"Players {len(profiles)} News {len(news_urls) - 1} BB Keep {bb['n_keep']} "
        f"BB News {bb.get('n_news', 0)} BK Keep {bk['n_keep']} Pitch {pl['n_pitch']} "
        f"Premier {pl.get('n_premier', 0)} Catalog {cat.name} NewsSitemap {n_news}"
    )


def slim_row(r, extra=()):
    out = {
        "name": r.get("name"),
        "pos": r.get("pos") or "",
        "team": r.get("team") or "",
        "bk": r.get("bk"),
        "avg": r.get("avg"),
        "n": r.get("n"),
        "value": r.get("value"),
    }
    for k in extra:
        if k in r:
            out[k] = r[k]
    return out


def write_discord_catalog(keep, board, ppr, std, rook_rows, profiles, nfl, mlb_games, deals=None, bb=None, pl=None, bk=None, sf_redraft=None, classic=None):
    """One JSON pack the Discord bot reads instead of scraping HTML."""
    media = {}
    media_path = ROOT / "data/player_media.json"
    if media_path.exists():
        media = json.loads(media_path.read_text())
    files = []
    for p in profiles:
        copy = get_copy(p["key"])
        med = media.get(p["key"], {})
        files.append({
            "key": p["key"],
            "slug": p["slug"],
            "name": p["name"],
            "pos": p.get("pos") or "",
            "team": p.get("team") or "",
            "age": p.get("age") or "",
            "full_name": p.get("full_name") or p.get("name") or "",
            "lists": p.get("lists") or {},
            "notes": p.get("notes") or [],
            "ranks": p.get("ranks") or {},
            "keep_avg": p.get("keep_avg"),
            "keep_n": p.get("keep_n"),
            "plus": copy.get("plus") or [],
            "minus": copy.get("minus") or [],
            "grafs": copy.get("grafs") or ([ff_stat_line(p)] if ff_stat_line(p) else []),
            "image": med.get("image") or "",
            "youtube_id": med.get("youtube_id") or "",
            "youtube_title": med.get("youtube_title") or "",
            "youtube_channel": med.get("youtube_channel") or "",
            "college": med.get("college") or "",
            "is_rookie": bool(med.get("is_rookie")),
            "sport": "football",
            "url": f"https://ballkeep.com/players/{p['slug']}.html",
        })
    news_pack = []
    for s in load_news_stories("football"):
        news_pack.append({
            "headline": s.get("headline"),
            "slug": s.get("slug"),
            "blurb": s.get("blurb"),
            "summary": s.get("summary"),
            "category": s.get("category"),
            "updated": s.get("updated"),
            "url": f"https://ballkeep.com/news/{s.get('slug')}.html",
            "players": s.get("players") or [],
            "sources": [
                {"title": src.get("title"), "url": src.get("url"), "kind": src.get("kind"), "publisher": src.get("publisher")}
                for src in (s.get("sources") or [])
            ],
        })
    catalog = {
        "updated": UPDATED,
        "site": "https://ballkeep.com",
        "algorithm": ALGORITHM,
        "sources": [name for name, _url, _note in KEEP_SOURCES],
        "keep": [slim_row(r, ("ranks", "age", "n", "avg")) for r in keep],
        "board_format": "redraft PPR",
        "board": [slim_row(r, ("yates", "fp", "karabell", "age", "n", "avg")) for r in board],
        "ppr": [slim_row(r, ("yates", "fp", "karabell", "age", "n", "avg")) for r in ppr],
        "sf_redraft": [slim_row(r, ("n", "avg", "keep", "ppr")) for r in (sf_redraft or [])],
        "standard": [slim_row(r) for r in std],
        "classic": [slim_row(r) for r in (classic or [])],
        "rookies": [slim_row(r, ("dd", "fp", "pff", "blurb")) for r in rook_rows],
        "hot": HOT,
        "cold": COLD,
        "picks": pick_assets(),
        "deals": deals or [],
        "players": files,
        "nfl": [
            {**g, "away_abbr": TEAMS.get(g["away"], ""), "home_abbr": TEAMS.get(g["home"], "")}
            for g in nfl
        ],
        "mlb": mlb_games,
        "news": news_pack,
    }
    bb = bb or {}
    catalog["bb_keep"] = [slim_row(r, ("age", "group")) for r in bb.get("keep") or []]
    catalog["bb_lineup"] = [slim_row(r, ("age", "group")) for r in bb.get("lineup") or []]
    catalog["bb_pitchers"] = [slim_row(r, ("age", "group")) for r in bb.get("pitchers") or []]
    catalog["bb_saves"] = [slim_row(r) for r in bb.get("saves") or []]
    catalog["bb_svh"] = [slim_row(r) for r in bb.get("svh") or []]
    catalog["bb_redraft"] = [slim_row(r, ("age", "group")) for r in bb.get("redraft") or []]
    catalog["bb_farm"] = [slim_row(r, ("age", "group", "eta", "path", "level", "mlb_g")) for r in bb.get("farm") or []]
    catalog["bb_picks"] = bb.get("picks") or []
    catalog["bb_players"] = bb.get("files") or []
    catalog["bb_waivers_dynasty"] = bb.get("dynasty_waivers") or []
    catalog["bb_waivers_redraft"] = bb.get("redraft_waivers") or []
    catalog["bb_sources"] = bb.get("source_names") or []
    bb_news = []
    for s in bb.get("news") or []:
        bb_news.append({
            "headline": s.get("headline"),
            "slug": s.get("slug"),
            "blurb": s.get("blurb"),
            "summary": s.get("summary"),
            "category": s.get("category"),
            "updated": s.get("updated"),
            "url": f"https://ballkeep.com/bb/news/{s.get('slug')}.html",
            "players": s.get("players") or [],
            "sources": [
                {"title": src.get("title"), "url": src.get("url"), "kind": src.get("kind"), "publisher": src.get("publisher")}
                for src in (s.get("sources") or [])
            ],
        })
    catalog["bb_news"] = bb_news
    pl = pl or {}
    catalog["pl_pitch"] = [slim_row(r, ("age", "group", "price", "sel", "pts", "sleeper_pts", "gls", "ast")) for r in pl.get("pitch") or []]
    catalog["pl_premier"] = [slim_row(r, ("age", "group", "price", "sel", "pts", "sleeper_pts", "gls", "ast", "sleeper_rank", "consensus", "premier_score", "full_name")) for r in pl.get("premier") or []]
    catalog["pl_fwd"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("fwd") or []]
    catalog["pl_mid"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("mid") or []]
    catalog["pl_def"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("def") or []]
    catalog["pl_gkp"] = [slim_row(r, ("age", "group", "price")) for r in pl.get("gkp") or []]
    catalog["pl_players"] = pl.get("files") or []
    catalog["pl_sources"] = pl.get("source_names") or []
    pl_news = []
    for s in pl.get("news") or []:
        pl_news.append({
            "headline": s.get("headline"),
            "slug": s.get("slug"),
            "blurb": s.get("blurb"),
            "category": s.get("category"),
            "updated": s.get("updated"),
            "url": f"https://ballkeep.com/pl/news/{s.get('slug')}.html",
            "players": s.get("players") or [],
        })
    catalog["pl_news"] = pl_news
    bk = bk or {}
    catalog["bk_keep"] = [slim_row(r, ("age", "group", "n", "avg")) for r in bk.get("keep") or []]
    catalog["bk_board"] = [slim_row(r, ("age", "group", "keep")) for r in bk.get("board") or []]
    catalog["bk_guards"] = [slim_row(r, ("age", "group")) for r in bk.get("guards") or []]
    catalog["bk_wings"] = [slim_row(r, ("age", "group")) for r in bk.get("wings") or []]
    catalog["bk_bigs"] = [slim_row(r, ("age", "group")) for r in bk.get("bigs") or []]
    catalog["bk_rookies"] = [slim_row(r, ("age", "blurb")) for r in bk.get("rookies") or []]
    catalog["bk_picks"] = bk.get("picks") or []
    catalog["bk_players"] = bk.get("files") or []
    catalog["bk_waivers_dynasty"] = bk.get("dynasty_waivers") or []
    catalog["bk_waivers_redraft"] = bk.get("redraft_waivers") or []
    catalog["bk_sources"] = bk.get("source_names") or []
    bk_news = []
    for s in bk.get("news") or []:
        bk_news.append({
            "headline": s.get("headline"),
            "slug": s.get("slug"),
            "blurb": s.get("blurb"),
            "summary": s.get("summary"),
            "category": s.get("category"),
            "updated": s.get("updated"),
            "url": f"https://ballkeep.com/bk/news/{s.get('slug')}.html",
            "players": s.get("players") or [],
            "sources": [
                {"title": src.get("title"), "url": src.get("url"), "kind": src.get("kind"), "publisher": src.get("publisher")}
                for src in (s.get("sources") or [])
            ],
        })
    catalog["bk_news"] = bk_news
    dest = ROOT / "data/discord-catalog.json"
    dest.write_text(json.dumps(catalog, indent=2, default=str))
    return dest


if __name__ == "__main__":
    main()
