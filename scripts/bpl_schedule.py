"""2026/27 Premier League slate for the football and PitchKeep schedule pages.

Fixtures from the NBC Sports release (June 19 list, updated through matchweek 9).
Kickoff times are ET when the wire published them. Played games carry a score.
"""
from __future__ import annotations

CLUBS = {
    "ARS": "Arsenal",
    "AVL": "Aston Villa",
    "BOU": "Bournemouth",
    "BRE": "Brentford",
    "BHA": "Brighton",
    "CHE": "Chelsea",
    "COV": "Coventry City",
    "CRY": "Crystal Palace",
    "EVE": "Everton",
    "FUL": "Fulham",
    "HUL": "Hull City",
    "IPS": "Ipswich Town",
    "LEE": "Leeds United",
    "LIV": "Liverpool",
    "MCI": "Manchester City",
    "MUN": "Manchester United",
    "NEW": "Newcastle",
    "NFO": "Nottingham Forest",
    "SUN": "Sunderland",
    "TOT": "Tottenham",
}

# week, day, time ET, home, away, score (home-away) or ""
_RAW = [
    # Matchweek 1
    (1, "Friday, Aug 21", "Final", "ARS", "COV", "3-0"),
    (1, "Saturday, Aug 22", "Final", "HUL", "MUN", "2-0"),
    (1, "Saturday, Aug 22", "Final", "EVE", "CRY", "2-0"),
    (1, "Saturday, Aug 22", "Final", "IPS", "SUN", "2-1"),
    (1, "Saturday, Aug 22", "Final", "NFO", "LEE", "0-1"),
    (1, "Saturday, Aug 22", "Final", "BRE", "TOT", "3-0"),
    (1, "Sunday, Aug 23", "Final", "BHA", "AVL", "4-0"),
    (1, "Sunday, Aug 23", "Final", "MCI", "BOU", "2-1"),
    (1, "Sunday, Aug 23", "Final", "NEW", "LIV", "2-2"),
    (1, "Monday, Aug 24", "Final", "FUL", "CHE", "2-3"),
    # Matchweek 2
    (2, "Friday, Aug 28", "Final", "CRY", "MCI", "1-4"),
    (2, "Saturday, Aug 29", "Final", "LIV", "NFO", "2-2"),
    (2, "Saturday, Aug 29", "Final", "BOU", "EVE", "1-1"),
    (2, "Saturday, Aug 29", "Final", "COV", "HUL", "0-1"),
    (2, "Saturday, Aug 29", "Final", "TOT", "NEW", "0-2"),
    (2, "Sunday, Aug 30", "9:00 AM", "CHE", "BHA", ""),
    (2, "Sunday, Aug 30", "9:00 AM", "LEE", "BRE", ""),
    (2, "Sunday, Aug 30", "9:00 AM", "SUN", "FUL", ""),
    (2, "Sunday, Aug 30", "11:30 AM", "MUN", "IPS", ""),
    (2, "Monday, Aug 31", "3:00 PM", "AVL", "ARS", ""),
    # Matchweek 3
    (3, "Friday, Sep 4", "3:00 PM", "IPS", "LIV", ""),
    (3, "Saturday, Sep 5", "7:30 AM", "NEW", "BOU", ""),
    (3, "Saturday, Sep 5", "10:00 AM", "BRE", "SUN", ""),
    (3, "Saturday, Sep 5", "10:00 AM", "BHA", "LEE", ""),
    (3, "Saturday, Sep 5", "10:00 AM", "FUL", "CRY", ""),
    (3, "Saturday, Sep 5", "10:00 AM", "MCI", "COV", ""),
    (3, "Saturday, Sep 5", "10:00 AM", "NFO", "TOT", ""),
    (3, "Saturday, Sep 5", "12:30 PM", "HUL", "AVL", ""),
    (3, "Sunday, Sep 6", "9:00 AM", "EVE", "MUN", ""),
    (3, "Sunday, Sep 6", "11:30 AM", "ARS", "CHE", ""),
    # Matchweek 4
    (4, "Saturday, Sep 12", "10:00 AM", "BOU", "BRE", ""),
    (4, "Saturday, Sep 12", "10:00 AM", "AVL", "NFO", ""),
    (4, "Saturday, Sep 12", "10:00 AM", "CHE", "HUL", ""),
    (4, "Saturday, Sep 12", "10:00 AM", "CRY", "IPS", ""),
    (4, "Saturday, Sep 12", "10:00 AM", "LIV", "FUL", ""),
    (4, "Saturday, Sep 12", "12:30 PM", "TOT", "EVE", ""),
    (4, "Saturday, Sep 12", "3:00 PM", "SUN", "ARS", ""),
    (4, "Sunday, Sep 13", "9:00 AM", "COV", "BHA", ""),
    (4, "Sunday, Sep 13", "11:30 AM", "MUN", "MCI", ""),
    (4, "Monday, Sep 14", "3:00 PM", "LEE", "NEW", ""),
    # Matchweek 5
    (5, "Friday, Sep 18", "3:00 PM", "BRE", "CHE", ""),
    (5, "Saturday, Sep 19", "7:30 AM", "TOT", "AVL", ""),
    (5, "Saturday, Sep 19", "10:00 AM", "BHA", "ARS", ""),
    (5, "Saturday, Sep 19", "10:00 AM", "EVE", "IPS", ""),
    (5, "Saturday, Sep 19", "10:00 AM", "LEE", "CRY", ""),
    (5, "Saturday, Sep 19", "10:00 AM", "MCI", "SUN", ""),
    (5, "Saturday, Sep 19", "10:00 AM", "NEW", "HUL", ""),
    (5, "Saturday, Sep 19", "12:30 PM", "NFO", "COV", ""),
    (5, "Sunday, Sep 20", "9:00 AM", "BOU", "LIV", ""),
    (5, "Sunday, Sep 20", "11:30 AM", "FUL", "MUN", ""),
    # Matchweek 6 (after the international break)
    (6, "Saturday, Oct 10", "7:30 AM", "ARS", "LEE", ""),
    (6, "Saturday, Oct 10", "10:00 AM", "AVL", "BRE", ""),
    (6, "Saturday, Oct 10", "10:00 AM", "CHE", "BOU", ""),
    (6, "Saturday, Oct 10", "10:00 AM", "IPS", "FUL", ""),
    (6, "Saturday, Oct 10", "10:00 AM", "SUN", "BHA", ""),
    (6, "Saturday, Oct 10", "12:30 PM", "MUN", "TOT", ""),
    (6, "Sunday, Oct 11", "9:00 AM", "CRY", "NFO", ""),
    (6, "Sunday, Oct 11", "9:00 AM", "HUL", "EVE", ""),
    (6, "Sunday, Oct 11", "11:30 AM", "LIV", "MCI", ""),
    (6, "Monday, Oct 12", "3:00 PM", "COV", "NEW", ""),
    # Matchweek 7
    (7, "Saturday, Oct 17", "7:30 AM", "EVE", "CHE", ""),
    (7, "Saturday, Oct 17", "10:00 AM", "BRE", "LIV", ""),
    (7, "Saturday, Oct 17", "10:00 AM", "FUL", "HUL", ""),
    (7, "Saturday, Oct 17", "10:00 AM", "MCI", "IPS", ""),
    (7, "Saturday, Oct 17", "12:30 PM", "NEW", "AVL", ""),
    (7, "Sunday, Oct 18", "9:00 AM", "BOU", "SUN", ""),
    (7, "Sunday, Oct 18", "9:00 AM", "BHA", "CRY", ""),
    (7, "Sunday, Oct 18", "9:00 AM", "LEE", "MUN", ""),
    (7, "Sunday, Oct 18", "11:30 AM", "NFO", "ARS", ""),
    (7, "Monday, Oct 19", "3:00 PM", "TOT", "COV", ""),
    # Matchweek 8
    (8, "Friday, Oct 23", "3:00 PM", "IPS", "NFO", ""),
    (8, "Saturday, Oct 24", "7:30 AM", "AVL", "MCI", ""),
    (8, "Saturday, Oct 24", "10:00 AM", "ARS", "EVE", ""),
    (8, "Saturday, Oct 24", "10:00 AM", "COV", "FUL", ""),
    (8, "Saturday, Oct 24", "10:00 AM", "LIV", "BHA", ""),
    (8, "Saturday, Oct 24", "12:30 PM", "CHE", "TOT", ""),
    (8, "Sunday, Oct 25", "9:00 AM", "CRY", "NEW", ""),
    (8, "Sunday, Oct 25", "9:00 AM", "HUL", "BRE", ""),
    (8, "Sunday, Oct 25", "9:00 AM", "MUN", "BOU", ""),
    (8, "Sunday, Oct 25", "11:30 AM", "SUN", "LEE", ""),
    # Matchweek 9
    (9, "Saturday, Oct 31", "7:30 AM", "CHE", "MUN", ""),
    (9, "Saturday, Oct 31", "10:00 AM", "BOU", "LEE", ""),
    (9, "Saturday, Oct 31", "10:00 AM", "BRE", "NFO", ""),
    (9, "Saturday, Oct 31", "10:00 AM", "COV", "SUN", ""),
    (9, "Saturday, Oct 31", "10:00 AM", "HUL", "IPS", ""),
    (9, "Saturday, Oct 31", "10:00 AM", "MCI", "BHA", ""),
    (9, "Saturday, Oct 31", "12:30 PM", "TOT", "CRY", ""),
    (9, "Sunday, Nov 1", "9:00 AM", "AVL", "FUL", ""),
    (9, "Sunday, Nov 1", "11:30 AM", "LIV", "ARS", ""),
    (9, "Monday, Nov 2", "3:00 PM", "NEW", "EVE", ""),
]

# Remaining matchweeks: home, away pairs in NBC release order (Saturday unless noted).
_LATER = {
    10: [("ARS", "HUL"), ("BHA", "BRE"), ("CRY", "LIV"), ("EVE", "COV"), ("FUL", "NEW"),
         ("IPS", "BOU"), ("LEE", "TOT"), ("MUN", "AVL"), ("NFO", "MCI"), ("SUN", "CHE")],
    11: [("BOU", "NFO"), ("AVL", "SUN"), ("BRE", "EVE"), ("CHE", "LEE"), ("COV", "CRY"),
         ("HUL", "BHA"), ("LIV", "MUN"), ("MCI", "FUL"), ("NEW", "ARS"), ("TOT", "IPS")],
    12: [("ARS", "MCI"), ("BHA", "NEW"), ("CRY", "HUL"), ("EVE", "LIV"), ("FUL", "BOU"),
         ("IPS", "AVL"), ("LEE", "COV"), ("MUN", "BRE"), ("NFO", "CHE"), ("SUN", "TOT")],
    13: [("BOU", "BHA"), ("AVL", "EVE"), ("BRE", "ARS"), ("CHE", "CRY"), ("COV", "IPS"),
         ("HUL", "NFO"), ("LIV", "SUN"), ("MCI", "LEE"), ("NEW", "MUN"), ("TOT", "FUL")],
    14: [("BOU", "HUL"), ("AVL", "CRY"), ("BRE", "MCI"), ("CHE", "LIV"), ("EVE", "FUL"),
         ("LEE", "IPS"), ("MUN", "COV"), ("NEW", "SUN"), ("NFO", "BHA"), ("TOT", "ARS")],
    15: [("ARS", "BOU"), ("BHA", "EVE"), ("COV", "AVL"), ("CRY", "MUN"), ("FUL", "BRE"),
         ("HUL", "TOT"), ("IPS", "NEW"), ("LIV", "LEE"), ("MCI", "CHE"), ("SUN", "NFO")],
    16: [("BOU", "COV"), ("ARS", "MUN"), ("BRE", "NEW"), ("BHA", "IPS"), ("CHE", "AVL"),
         ("LEE", "FUL"), ("LIV", "TOT"), ("MCI", "HUL"), ("NFO", "EVE"), ("SUN", "CRY")],
    17: [("AVL", "LEE"), ("COV", "CHE"), ("CRY", "ARS"), ("EVE", "SUN"), ("FUL", "BHA"),
         ("HUL", "LIV"), ("IPS", "BRE"), ("MUN", "NFO"), ("NEW", "MCI"), ("TOT", "BOU")],
    18: [("AVL", "LIV"), ("COV", "BRE"), ("CRY", "BOU"), ("EVE", "MCI"), ("FUL", "ARS"),
         ("HUL", "LEE"), ("IPS", "CHE"), ("MUN", "SUN"), ("NEW", "NFO"), ("TOT", "BHA")],
    19: [("BOU", "AVL"), ("ARS", "IPS"), ("BRE", "CRY"), ("BHA", "MUN"), ("CHE", "NEW"),
         ("LEE", "EVE"), ("LIV", "COV"), ("MCI", "TOT"), ("NFO", "FUL"), ("SUN", "HUL")],
    20: [("ARS", "BRE"), ("BHA", "BOU"), ("CRY", "CHE"), ("EVE", "AVL"), ("FUL", "TOT"),
         ("IPS", "COV"), ("LEE", "MCI"), ("MUN", "NEW"), ("NFO", "HUL"), ("SUN", "LIV")],
    21: [("BOU", "IPS"), ("AVL", "MUN"), ("BRE", "BHA"), ("CHE", "SUN"), ("COV", "EVE"),
         ("HUL", "ARS"), ("LIV", "CRY"), ("MCI", "NFO"), ("NEW", "FUL"), ("TOT", "LEE")],
    22: [("ARS", "NEW"), ("BHA", "MCI"), ("CRY", "TOT"), ("EVE", "BRE"), ("FUL", "AVL"),
         ("IPS", "HUL"), ("LEE", "CHE"), ("MUN", "LIV"), ("NFO", "BOU"), ("SUN", "COV")],
    23: [("BOU", "FUL"), ("AVL", "IPS"), ("BRE", "MUN"), ("CHE", "NFO"), ("COV", "LEE"),
         ("HUL", "CRY"), ("LIV", "EVE"), ("MCI", "ARS"), ("NEW", "BHA"), ("TOT", "SUN")],
    24: [("ARS", "LIV"), ("BHA", "HUL"), ("CRY", "COV"), ("EVE", "NEW"), ("FUL", "MCI"),
         ("IPS", "TOT"), ("LEE", "BOU"), ("MUN", "CHE"), ("NFO", "BRE"), ("SUN", "AVL")],
    25: [("AVL", "BOU"), ("COV", "LIV"), ("CRY", "BRE"), ("EVE", "LEE"), ("FUL", "NFO"),
         ("HUL", "SUN"), ("IPS", "ARS"), ("MUN", "BHA"), ("NEW", "CHE"), ("TOT", "MCI")],
    26: [("BOU", "CRY"), ("ARS", "FUL"), ("BRE", "COV"), ("BHA", "TOT"), ("CHE", "IPS"),
         ("LEE", "AVL"), ("LIV", "HUL"), ("MCI", "NEW"), ("NFO", "MUN"), ("SUN", "EVE")],
    27: [("AVL", "CHE"), ("COV", "BOU"), ("CRY", "SUN"), ("EVE", "NFO"), ("FUL", "LEE"),
         ("HUL", "MCI"), ("IPS", "BHA"), ("MUN", "ARS"), ("NEW", "BRE"), ("TOT", "LIV")],
    28: [("BOU", "TOT"), ("ARS", "CRY"), ("BRE", "IPS"), ("BHA", "FUL"), ("CHE", "COV"),
         ("LEE", "HUL"), ("LIV", "AVL"), ("MCI", "EVE"), ("NFO", "NEW"), ("SUN", "MUN")],
    29: [("BOU", "NEW"), ("AVL", "HUL"), ("CHE", "ARS"), ("COV", "MCI"), ("CRY", "FUL"),
         ("LEE", "BHA"), ("LIV", "IPS"), ("MUN", "EVE"), ("SUN", "BRE"), ("TOT", "NFO")],
    30: [("ARS", "SUN"), ("BRE", "BOU"), ("BHA", "COV"), ("EVE", "TOT"), ("FUL", "LIV"),
         ("HUL", "CHE"), ("IPS", "CRY"), ("MCI", "MUN"), ("NEW", "LEE"), ("NFO", "AVL")],
    31: [("BOU", "MCI"), ("AVL", "BHA"), ("CHE", "FUL"), ("COV", "ARS"), ("CRY", "EVE"),
         ("LEE", "NFO"), ("LIV", "NEW"), ("MUN", "HUL"), ("SUN", "IPS"), ("TOT", "BRE")],
    32: [("ARS", "AVL"), ("BRE", "LEE"), ("BHA", "CHE"), ("EVE", "BOU"), ("FUL", "SUN"),
         ("HUL", "COV"), ("IPS", "MUN"), ("MCI", "CRY"), ("NEW", "TOT"), ("NFO", "LIV")],
    33: [("BOU", "ARS"), ("AVL", "COV"), ("BRE", "FUL"), ("CHE", "MCI"), ("EVE", "BHA"),
         ("LEE", "LIV"), ("MUN", "CRY"), ("NEW", "IPS"), ("NFO", "SUN"), ("TOT", "HUL")],
    34: [("ARS", "TOT"), ("BHA", "NFO"), ("COV", "MUN"), ("CRY", "AVL"), ("FUL", "EVE"),
         ("HUL", "BOU"), ("IPS", "LEE"), ("LIV", "CHE"), ("MCI", "BRE"), ("SUN", "NEW")],
    35: [("BOU", "MUN"), ("BRE", "AVL"), ("BHA", "SUN"), ("EVE", "HUL"), ("FUL", "IPS"),
         ("LEE", "ARS"), ("MCI", "LIV"), ("NEW", "COV"), ("NFO", "CRY"), ("TOT", "CHE")],
    36: [("ARS", "NFO"), ("AVL", "NEW"), ("CHE", "EVE"), ("COV", "TOT"), ("CRY", "BHA"),
         ("HUL", "FUL"), ("IPS", "MCI"), ("LIV", "BRE"), ("MUN", "LEE"), ("SUN", "BOU")],
    37: [("BOU", "CHE"), ("BRE", "HUL"), ("BHA", "LIV"), ("EVE", "ARS"), ("FUL", "COV"),
         ("LEE", "SUN"), ("MCI", "AVL"), ("NEW", "CRY"), ("NFO", "IPS"), ("TOT", "MUN")],
    38: [("ARS", "BHA"), ("AVL", "TOT"), ("CHE", "BRE"), ("COV", "NFO"), ("CRY", "LEE"),
         ("HUL", "NEW"), ("IPS", "EVE"), ("LIV", "BOU"), ("MUN", "FUL"), ("SUN", "MCI")],
}

_LATER_DAY = {
    13: ("Wednesday, Dec 2", "3:00 PM"),
    17: ("Saturday, Dec 26", ""),
    18: ("Wednesday, Dec 30", "3:00 PM"),
    19: ("Saturday, Jan 2", ""),
    20: ("Wednesday, Jan 6", "3:00 PM"),
    25: ("Wednesday, Feb 10", "3:00 PM"),
    28: ("Wednesday, Mar 3", "3:00 PM"),
    37: ("Sunday, May 23", ""),
    38: ("Sunday, May 30", ""),
}


def bpl_games():
    games = []
    for week, day, time, home, away, score in _RAW:
        games.append({
            "week": week,
            "day": day,
            "time": time,
            "home": CLUBS[home],
            "away": CLUBS[away],
            "home_abbr": home,
            "away_abbr": away,
            "score": score,
        })
    for week, pairs in _LATER.items():
        day, time = _LATER_DAY.get(week, ("Saturday", ""))
        for home, away in pairs:
            games.append({
                "week": week,
                "day": day,
                "time": time,
                "home": CLUBS[home],
                "away": CLUBS[away],
                "home_abbr": home,
                "away_abbr": away,
                "score": "",
            })
    return games


def bpl_weeks():
    return sorted({g["week"] for g in bpl_games()})


def bpl_schedule_parts(esc, json_mod):
    """HTML body + filter JS. `esc` and `json` come from the site builders."""
    games = bpl_games()
    weeks = bpl_weeks()
    week_btns = "".join(f'<button type="button" data-week="{w}">MW{w}</button>' for w in weeks)
    team_btns = "".join(
        f'<button type="button" data-team="{esc(abbr)}">{esc(abbr)}</button>'
        for abbr in sorted(CLUBS)
    )
    body = f"""
    <p class="kicker">2026/27 Premier League</p>
    <h1>BPL Schedule</h1>
    <p class="note">Full 38-matchweek slate from the June 19 fixture release. Kickoff is ET when the wire posted a time. Played games show the score. Filter by matchweek or club. Arsenal opened at home against Coventry on Friday, Aug 21. The last Sunday is May 30, 2027.</p>
    <p class="note">Matchweeks</p>
    <div class="filters" id="bpl-weeks"><button type="button" class="active" data-week="all">All</button>{week_btns}</div>
    <p class="note">Clubs</p>
    <div class="filters" id="bpl-teams"><button type="button" class="active" data-team="all">All clubs</button>{team_btns}</div>
    <div class="panel table-wrap" id="bpl-games"></div>
    """
    js = f"""<script>
    const BPL = {json_mod.dumps(games)};
    let week = 'all', team = 'all';
    function render() {{
      const rows = BPL.filter(g => {{
        const okW = week === 'all' || String(g.week) === String(week);
        const okT = team === 'all' || g.home_abbr === team || g.away_abbr === team;
        return okW && okT;
      }});
      const body = rows.map(g => {{
        const line = g.score
          ? `${{g.home}} ${{g.score}} ${{g.away}}`
          : `${{g.away}} at ${{g.home}}`;
        const when = g.time ? g.time : '';
        return `<tr><td>MW${{g.week}}</td><td>${{g.day}}</td><td><strong>${{line}}</strong></td><td>${{when}}</td></tr>`;
      }}).join('');
      document.getElementById('bpl-games').innerHTML = `<table><thead><tr><th>Wk</th><th>Day</th><th>Matchup</th><th>Time ET</th></tr></thead><tbody>${{body}}</tbody></table>`;
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
    bind('bpl-weeks', 'week', v => week = v);
    bind('bpl-teams', 'team', v => team = v);
    render();
    </script>"""
    return body, js
