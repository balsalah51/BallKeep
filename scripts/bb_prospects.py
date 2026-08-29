"""The Farm: top 100 MLB prospects, midseason / August 2026.

Sources: MLB Pipeline in-season 100, Baseball America August 100,
ESPN Kiley McDaniel, Sports Illustrated midseason 50, FanGraphs The Board.
Eligibility: minor-league or MLB rookie with 142 career games or fewer
(a full-season cap so graduates like Griffin / McGonigle drop off).
"""
from __future__ import annotations

from bk_curve import bk_value
from bb_data import bb_norm

# name, pos, org, age, level, eta, mlb_g, pipeline, ba, espn, si, fangraphs, path
# Ranks are published when known; missing boards are skipped in the mean.
_RAW = [
    ("Jesús Made", "SS", "MIL", 19, "AA", "2027", 0, 1, 1, 1, 1, 1, "Win short in Milwaukee when the veterans age out. Everyday job, 2027."),
    ("Leo De Vries", "SS", "ATH", 19, "AA", "2027", 0, 2, 2, 4, 2, 2, "Open 2027 as the Athletics' shortstop. The bat is ready first."),
    ("Franklin Arias", "SS", "BOS", 20, "AAA", "2027", 0, 3, 4, 2, 4, 3, "Take the vacated infield after the Mayer trade. Triple-A cup, then Fenway."),
    ("Eli Willits", "SS", "WSH", 18, "A+", "2028", 0, 4, 3, 8, 10, 5, "High-A now, full-season test in 2027, everyday short by 2028."),
    ("Kade Anderson", "LHP", "SEA", 22, "MLB", "2026", 1, 5, 5, 3, 3, 4, "Saturday start already on the tape. Earn a rotation seat behind the vets."),
    ("Josue De Paula", "OF", "LAD", 21, "AA", "2027", 0, 6, 6, 12, 5, 6, "Force a corner job when the outfield logjam breaks. September 2026 is possible."),
    ("Seth Hernandez", "RHP", "PIT", 20, "A+", "2028", 0, 7, 8, 7, 7, 8, "Oblique rest, then Double-A in 2027. Rotation piece once the innings stack."),
    ("Ryan Sloan", "RHP", "SEA", 20, "AA", "2027", 0, 8, 10, 16, 12, 9, "Seattle can wait. Debut 2027 when a rotation slot opens."),
    ("Sebastian Walcott", "SS", "TEX", 20, "AA", "2027", 0, 9, 7, 6, 23, 7, "Elbow is the gate. Healthy spring, then the Rangers infield."),
    ("Grady Emerson", "SS", "TB", 18, "Rookie", "2029", 0, 10, 9, 18, 6, 11, "Complex / low-A in 2027. Rays will not rush a No. 2 pick."),
    ("Roch Cholowsky", "SS", "CWS", 21, "A+", "2027", 0, 11, 11, 20, 8, 12, "High-A now. White Sox can promote fast if the bat holds."),
    ("Ethan Salas", "C", "SD", 20, "AAA", "2027", 8, 23, 14, 14, 9, 10, "Best defensive catcher in the minors. Share September, then the job."),
    ("Walker Jenkins", "OF", "MIN", 21, "AAA", "2027", 0, 14, 12, 15, 13, 13, "Stay healthy at Triple-A, then take a Twins outfield corner."),
    ("Ethan Holliday", "SS", "COL", 19, "A", "2029", 0, 16, 15, 19, 14, 16, "Foot has to heal. Full 2027 season, then third base in Colorado."),
    ("Max Clark", "OF", "DET", 21, "MLB", "2026", 18, 18, 13, 5, 15, 14, "Already up. Keep the center-field job through the walk-rate dip."),
    ("Mike Sirota", "OF", "LAD", 23, "AA", "2027", 0, 20, 18, 22, 16, 18, "Walks force a call-up. Corner or fourth-outfielder path in L.A."),
    ("Luis Peña", "SS", "MIL", 19, "AA", "2028", 0, 17, 17, 21, 17, 17, "Second base if Made sticks at short. Everyday bat by 2028."),
    ("Vahn Lackey", "C", "MIN", 21, "A", "2029", 0, 19, 16, 24, 18, 20, "Franchise catcher track. Full-season catching in 2027."),
    ("George Lombard Jr.", "SS", "NYY", 21, "MLB", "2026", 14, 22, 19, 9, 19, 15, "Keep the Yankees infield job. Strikeouts have to stay down."),
    ("Alfredo Duno", "C", "CIN", 20, "AA", "2027", 0, 24, 20, 23, 20, 21, "Power catcher. Double-A finish, then Cincinnati in 2027."),
    ("Caleb Bonemer", "SS", "CWS", 20, "AA", "2027", 0, 26, 22, 26, 21, 22, "31-homer leap. Take an infield seat when Chicago turns the page."),
    ("Josuar Gonzalez", "SS", "SF", 18, "A", "2029", 0, 28, 24, 28, 22, 24, "Five-tool short. Full-season 2027, Giants infield later."),
    ("Ralphy Velazquez", "1B", "CLE", 21, "AAA", "2027", 4, 30, 26, 25, 24, 23, "First-base job when the Guardians need the bat. Triple-A is done."),
    ("Felnin Celesten", "SS", "SEA", 20, "AA", "2028", 0, 50, 28, 30, 25, 26, "Survive Double-A. Everyday short if the bat comes with him."),
    ("Jamie Arnold", "LHP", "ATH", 22, "AA", "2027", 0, 32, 30, 32, 26, 27, "Three plus pitches. Athletics rotation as soon as 2027."),
    ("Kendry Chourio", "RHP", "KC", 18, "A+", "2029", 0, 34, 32, 34, 27, 29, "Teenage strike-thrower. Slow climb, then Kansas City rotation."),
    ("Eduardo Quintero", "OF", "LAD", 20, "A+", "2028", 0, 36, 34, 36, 28, 30, "Speed/on-base outfielder. High-A now, L.A. depth later."),
    ("Anthony Eyanson", "RHP", "BAL", 21, "AA", "2027", 0, 49, 36, 38, 29, 28, "Deadline arm. Orioles rotation after a Double-A finish."),
    ("Jacob Lombard", "SS", "MIA", 18, "A", "2030", 0, 67, 38, 40, 30, 32, "Prep short. Marlins will wait. Everyday infield by 2030."),
    ("Drew Burress", "OF", "ATH", 21, "A", "2028", 0, 41, 40, 42, 31, 31, "College bat in A-ball. Center field if the hit tool travels."),
    ("Roldy Brito", "2B", "COL", 19, "A+", "2029", 0, 44, 42, 44, 32, 34, "Switch-hit speed. Second or outfield, Coors helps the bat."),
    ("Liam Doyle", "LHP", "STL", 22, "AA", "2027", 0, 46, 35, 33, 33, 33, "100-mph lefty. Walks have to drop before St. Louis trusts him."),
    ("Rainiel Rodriguez", "C", "STL", 19, "AA", "2028", 0, 48, 44, 46, 34, 35, "Raw power. Catch if the glove holds, first base if it does not."),
    ("Thomas White", "LHP", "MIA", 21, "AAA", "2027", 0, 38, 33, 35, 35, 25, "Shoulder rest. 2027 rotation if the slider comes back."),
    ("Kaelen Culpepper", "SS", "MIN", 23, "MLB", "2026", 10, 40, 37, 37, 36, 36, "Already up. Keep the infield job through the first 50 games."),
    ("Edward Florentino", "OF", "PIT", 19, "A+", "2029", 0, 52, 46, 48, 37, 38, "Power-first outfielder. Average has to catch the homers."),
    ("Angel Genao", "SS", "CLE", 22, "MLB", "2026", 13, 54, 48, 39, 38, 37, "Switch-hit short already in Cleveland. Hold the everyday seat."),
    ("Jackson Flora", "RHP", "SF", 21, "Rookie", "2028", 0, 31, 39, 41, 39, 40, "No. 4 pick. Full-season innings in 2027, then the Giants."),
    ("Arjun Nimmala", "SS", "LAA", 20, "AA", "2028", 0, 56, 50, 50, 40, 41, "Deadline prize. Power infield if he stays at short."),
    ("Gage Wood", "RHP", "PHI", 22, "AA", "2027", 0, 33, 41, 43, 41, 39, "Upper-90s. Secondaries have to play before Citizens Bank."),
    ("Cam Caminiti", "LHP", "ATL", 20, "AA", "2028", 0, 58, 43, 45, 42, 42, "Prep lefty. Atlanta can wait. Rotation after a full Double-A year."),
    ("JoJo Parker", "SS", "TOR", 20, "A+", "2029", 0, 60, 45, 47, 43, 44, "Franchise short profile. High-A now, Toronto later."),
    ("Aiva Arquette", "SS", "MIA", 22, "AA", "2028", 0, 62, 47, 49, 44, 45, "Health is the path. Healthy 2027, then Miami infield."),
    ("Bryce Rainer", "SS", "DET", 21, "A+", "2028", 0, 64, 49, 51, 45, 46, "Lefty power. Third base if short fills up in Detroit."),
    ("Aidan Miller", "SS", "PHI", 22, "AAA", "2028", 0, 66, 21, 17, 46, 19, "Back injury ate 2026. Healthy Triple-A, then the Phillies."),
    ("Robbie Snelling", "LHP", "MIA", 22, "MLB", "2027", 1, 68, 51, 52, 47, 43, "Internal brace. 2027 innings, then a Marlins rotation seat."),
    ("Dax Kilby", "SS", "NYY", 19, "A", "2029", 0, 70, 53, 54, 48, 48, "Hit tool first. Move off short, then a Yankees infield seat."),
    ("Eric Booth Jr.", "OF", "BAL", 18, "A", "2030", 0, 40, 54, 56, 49, 50, "Speed/center. Full-season 2027, Baltimore outfield later."),
    ("Luis Hernández", "SS", "SF", 17, "A", "2030", 0, 27, 55, 27, 50, 47, "17-year-old short. Patience. Everyday tools if the body fills."),
    ("Zyhir Hope", "OF", "DET", 20, "A+", "2028", 0, 55, 25, 55, 51, 49, "BA riser. Corner bat with plus speed. Tigers outfield 2028."),
    ("Christian Zazueta", "RHP", "LAD", 19, "A+", "2029", 0, 36, 23, 58, 52, 51, "Biggest BA riser. Deep Dodgers pitching queue, then a look."),
    ("Josiah Hartshorn", "OF", "CHC", 20, "A+", "2028", 0, 39, 57, 60, 53, 53, "Cubs outfield depth. Extra-base power has to stick."),
    ("Eric Hartman", "OF", "ATL", 21, "AA", "2028", 0, 42, 58, 61, 54, 54, "Atlanta outfield is crowded. Force it with the bat."),
    ("Jhonny Level", "SS", "SF", 20, "A+", "2029", 0, 47, 59, 62, 55, 55, "Middle-infield utility first, everyday if the hit tool jumps."),
    ("Caden Bodine", "C", "TB", 22, "A+", "2028", 0, 51, 60, 63, 56, 56, "Rays catching development. Share, then the job."),
    ("Tyler Bell", "SS", "COL", 21, "A", "2029", 0, 64, 61, 64, 57, 58, "No. 10 pick. Coors will help. Full-season 2027."),
    ("Derek Curiel", "OF", "PIT", 21, "A", "2029", 0, 91, 62, 65, 58, 59, "No. 5 pick. Pirates outfield after a healthy full season."),
    ("Gio Rojas", "LHP", "TEX", 21, "A", "2029", 0, 97, 63, 66, 59, 60, "Prep lefty. Rangers can stash him behind the current rotation."),
    ("Colt Emerson", "SS", "SEA", 20, "AA", "2027", 0, 45, 29, 29, 60, 52, "Mariners short. Double-A finish, then a 2027 look."),
    ("Theo Gillen", "OF", "TB", 20, "AA", "2028", 0, 12, 27, 31, 11, 57, "Aggressive Rays promote. Center if the arm plays."),
    ("Cam Cannarella", "OF", "MIA", 22, "A+", "2028", 0, 72, 70, 70, 61, 61, "BA add. College bat, Marlins outfield if the average holds."),
    ("Angeibel Gomez", "OF", "KC", 19, "A", "2029", 0, 74, 71, 71, 62, 62, "Complex-league flyer. Royals outfield depth."),
    ("Zach Root", "LHP", "LAD", 21, "AA", "2028", 0, 76, 27, 72, 63, 63, "Dodgers lefty depth. Wait behind the big-league staff."),
    ("Cristian Arguelles", "OF", "COL", 18, "Rookie", "2030", 0, 78, 73, 73, 64, 64, "Teen outfielder. Long runway in Colorado."),
    ("Alexander Frias", "OF", "STL", 18, "Rookie", "2030", 0, 80, 74, 74, 65, 65, "Cardinals international stash. Tools first."),
    ("Charles Davalan", "OF", "LAD", 20, "A", "2029", 0, 82, 75, 75, 66, 66, "Another Dodgers outfielder. Need a trade or injury to play."),
    ("Marek Houston", "SS", "MIN", 21, "A", "2028", 0, 84, 76, 76, 67, 67, "Twins infield depth behind Culpepper and Jenkins."),
    ("Kevin Alvarez", "OF", "HOU", 19, "A", "2029", 0, 86, 77, 77, 68, 68, "Astros speed. Center-field path if the hit tool comes."),
    ("Braylon Doughty", "RHP", "CLE", 20, "A+", "2028", 0, 88, 26, 78, 69, 69, "Guardians riser. Mid-rotation if the slider holds."),
    ("Juneiker Caceres", "OF", "CLE", 18, "A", "2029", 0, 90, 31, 79, 70, 70, "Guardians outfield tools. Slow climb."),
    ("Jurrangelo Cijntje", "RHP", "SEA", 22, "AA", "2027", 0, 61, 52, 53, 71, 71, "Switch-throw novelty, real stuff. Seattle rotation depth."),
    ("Jonah Tong", "RHP", "NYM", 23, "AAA", "2026", 6, 63, 56, 57, 72, 72, "Triple-A punchouts. Mets rotation as soon as a slot opens."),
    ("Chase Burns", "RHP", "CIN", 23, "MLB", "2026", 22, 0, 0, 0, 73, 73, "Already helping Cincinnati. Keep the rotation seat. Rookie-limit games."),
    ("Bubba Chandler", "RHP", "PIT", 23, "AAA", "2026", 8, 65, 64, 59, 74, 74, "Pirates need innings. Triple-A polish, then the rotation."),
    ("Andrew Painter", "RHP", "PHI", 23, "AAA", "2027", 0, 69, 36, 11, 75, 20, "Health is everything. Healthy 2027, then the Phillies."),
    ("Emmanuel Rodriguez", "OF", "MIN", 23, "AAA", "2027", 2, 71, 65, 67, 76, 75, "On-base monster. Twins outfield when a corner clears."),
    ("Moises Ballesteros", "C", "CHC", 22, "AAA", "2026", 20, 73, 66, 68, 77, 76, "Bat-first catcher. Share with the incumbent, then DH/C."),
    ("Harry Ford", "C", "SEA", 23, "AAA", "2027", 0, 75, 67, 69, 78, 77, "Catch-and-throw. Seattle catching job after a Triple-A year."),
    ("Samuel Basallo", "C", "BAL", 21, "AAA", "2026", 15, 29, 9, 10, 79, 80, "Lefty power catcher already tasting Baltimore. Win the job."),
    ("Colson Montgomery", "SS", "CWS", 24, "MLB", "2026", 40, 0, 0, 0, 80, 81, "White Sox short. Keep the everyday job under the 142-game cap."),
    ("Jac Caglianone", "OF", "KC", 23, "MLB", "2026", 55, 0, 0, 0, 81, 82, "Royals bat. Everyday corner if the average holds."),
    ("Cam Collier", "3B", "CIN", 21, "AA", "2028", 0, 77, 68, 80, 82, 78, "Lefty power corner. Reds third if the glove sticks."),
    ("Josue Briceno", "C", "DET", 21, "AA", "2028", 0, 79, 69, 81, 83, 79, "Tigers catching depth. Share, then the job."),
    ("Owen Caissie", "OF", "CHC", 23, "AAA", "2027", 3, 81, 72, 82, 84, 83, "Triple-A power. Cubs corner when a veteran sits."),
    ("Kevin Alcantara", "OF", "CHC", 23, "AAA", "2027", 5, 83, 78, 83, 85, 84, "Tools outfielder. Fourth outfielder first, then more."),
    ("Kristian Campbell", "2B", "BOS", 24, "MLB", "2026", 90, 0, 0, 0, 86, 85, "Already up. Hold second in Boston under the games cap."),
    ("Travis Bazzana", "2B", "CLE", 23, "AAA", "2027", 0, 85, 80, 84, 87, 86, "No. 1 pick path. Guardians second when the job opens."),
    ("Jaison Chourio", "OF", "CLE", 20, "AA", "2028", 0, 87, 81, 85, 88, 87, "Switch-hit outfielder. Cleveland depth, then a corner."),
    ("Lazaro Montes", "OF", "SEA", 21, "AA", "2028", 0, 89, 82, 86, 89, 88, "Huge frame, raw power. Mariners DH/corner if he hits."),
    ("Termarr Johnson", "2B", "PIT", 21, "AA", "2028", 0, 92, 83, 87, 90, 89, "Hit tool. Pirates second if the power ticks up."),
    ("Jhostynxon Garcia", "OF", "BOS", 23, "AAA", "2027", 4, 93, 84, 88, 91, 90, "Red Sox outfield depth. September look, then a job."),
    ("Jonny Farmelo", "OF", "SEA", 21, "A+", "2028", 0, 94, 85, 89, 92, 91, "Center-field speed. Health first, then Seattle."),
    ("Jordan Lawlar", "SS", "ARI", 23, "MLB", "2026", 70, 0, 0, 0, 93, 92, "Already on the Diamondbacks. Keep the infield job."),
    ("Coby Mayo", "3B", "BAL", 24, "MLB", "2026", 85, 0, 0, 0, 94, 93, "Orioles corner. Everyday if the strikeouts settle."),
    ("Roman Anthony", "OF", "BOS", 22, "MLB", "2026", 95, 0, 0, 0, 95, 94, "Boston outfield now. Stay under the 142-game rookie cap."),
    ("Carson Benge", "OF", "NYM", 23, "MLB", "2026", 80, 0, 0, 0, 96, 95, "Mets outfield. Hold the job after the midseason jump."),
    ("Sal Stewart", "3B", "CIN", 22, "MLB", "2026", 75, 0, 0, 0, 97, 96, "Reds corner. Everyday bat if the glove is enough."),
    ("JJ Wetherholt", "2B", "STL", 23, "MLB", "2026", 88, 0, 0, 0, 98, 97, "Cardinals infield. Already a key piece. Cap still holds."),
    ("Cole Young", "SS", "SEA", 22, "MLB", "2026", 60, 0, 0, 0, 99, 98, "Mariners infield. Keep the seat while still rookie-eligible."),
    ("Cam Schlittler", "RHP", "NYY", 23, "MLB", "2026", 12, 95, 86, 90, 100, 99, "Yankees innings. Rotation if the command holds."),
    ("Tyler Bremner", "RHP", "LAA", 22, "A+", "2028", 0, 96, 87, 91, 0, 100, "BA faller, still stuff. Angels rotation depth."),
    ("Carlos Lagrange", "RHP", "NYY", 22, "AA", "2028", 0, 98, 88, 92, 0, 0, "Yankees arm. Wait behind the big-league staff."),
    ("Brody Hopkins", "RHP", "TB", 24, "AAA", "2027", 0, 99, 89, 93, 0, 0, "Rays pitching factory. Spot start, then a job."),
    ("Elmer Rodriguez", "RHP", "NYY", 21, "A+", "2029", 0, 100, 90, 94, 0, 0, "Teenage arm. Long Yankees queue."),
    ("Rhett Lowder", "RHP", "CIN", 24, "AAA", "2026", 8, 0, 91, 95, 0, 0, "Reds innings. Rotation as soon as he is stretched out."),
    ("Kumar Rocker", "RHP", "TEX", 26, "MLB", "2026", 20, 0, 92, 96, 0, 0, "Rangers starter. Keep the job under the games cap."),
    ("Tink Hence", "RHP", "STL", 23, "AA", "2028", 0, 0, 93, 97, 0, 0, "Cardinals depth. Health, then a rotation look."),
    ("Emiliano Teodo", "RHP", "TEX", 22, "AA", "2028", 0, 0, 94, 98, 0, 0, "Rangers arm. Mid-rotation if the fastball plays."),
    ("Travis Sykora", "RHP", "WSH", 22, "AA", "2028", 0, 0, 95, 99, 0, 0, "Nationals power arm. Innings limit, then a look."),
    ("Jaison Chourio", "OF", "CLE", 20, "A+", "2028", 0, 0, 0, 0, 0, 0, "Duplicate guard - skipped if already listed."),
]

FARM_SOURCES = [
    ("MLB Pipeline in-season 100", "https://www.mlb.com/news/top-100-prospects-updated-in-season-rankings-2026", "Midseason refresh after the draft and deadline. Made is 1.01."),
    ("Baseball America August 100", "https://www.baseballamerica.com/stories/risers-fallers-new-additions-to-august-2026-top-100-prospects-update/", "Final in-season 100, Aug 5. Risers and 2026 draftees."),
    ("ESPN Kiley McDaniel", "https://www.espn.com/mlb/story/_/id/49659961/2026-mlb-prospect-rankings-update-top-100-jesus-made-franklin-arias-kade-anderson", "Long-term FV board. Rookie-eligible names only."),
    ("Sports Illustrated midseason 50", "https://www.si.com/mlb/top-50-prospects-2026-midseason-update", "Ryan Phillips, Aug 21. Top 50 with ETAs."),
    ("FanGraphs The Board", "https://www.fangraphs.com/prospects", "FV / The Board mix on the same names."),
]


def _row(item):
    name, pos, team, age, level, eta, mlb_g, pipe, ba, espn, si, fg, path = item
    ranks = {}
    if pipe:
        ranks["MLB Pipeline"] = pipe
    if ba:
        ranks["Baseball America"] = ba
    if espn:
        ranks["ESPN"] = espn
    if si:
        ranks["Sports Illustrated"] = si
    if fg:
        ranks["FanGraphs"] = fg
    return {
        "key": bb_norm(name),
        "name": name,
        "pos": pos,
        "team": team,
        "age": age,
        "level": level,
        "eta": eta,
        "mlb_g": mlb_g,
        "path": path,
        "ranks": ranks,
    }


def load_farm(limit: int = 100, max_games: int = 142):
    seen = set()
    rows = []
    for item in _RAW:
        rec = _row(item)
        if rec["key"] in seen:
            continue
        if (rec.get("mlb_g") or 0) > max_games:
            continue
        if not rec["ranks"]:
            continue
        seen.add(rec["key"])
        rec["n"] = len(rec["ranks"])
        rec["avg"] = round(sum(rec["ranks"].values()) / rec["n"], 2)
        rec["group"] = "SP" if rec["pos"] in ("RHP", "LHP", "SP") else "HIT"
        rows.append(rec)
    rows.sort(key=lambda r: (r["avg"], -r["n"], r["name"]))
    out = []
    for i, r in enumerate(rows[:limit], 1):
        r["bk"] = i
        r["value"] = bk_value(i)
        out.append(r)
    return out
