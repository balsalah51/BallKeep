"""Additional ranking sources, August 2026.

Only published boards. Short lists still count: unranked names are skipped
in the mean, not treated as 999.
"""

# ESPN - Eric Karabell Superflex PPR, updated Aug 17, 2026
# https://www.espn.com/fantasy/football/story/_/id/47539664
ESPN_KARABELL_SF = [
    "Josh Allen", "Lamar Jackson", "Jalen Hurts", "Joe Burrow", "Drake Maye",
    "Jayden Daniels", "Ja'Marr Chase", "Puka Nacua", "Jaxon Smith-Njigba", "Amon-Ra St. Brown",
    "Jahmyr Gibbs", "Bijan Robinson", "Jonathan Taylor", "Brock Purdy", "Patrick Mahomes",
    "De'Von Achane", "Dak Prescott", "CeeDee Lamb", "Justin Jefferson", "Drake London",
    "James Cook", "Derrick Henry", "Chase Brown", "Trey McBride", "Brock Bowers",
    "Christian McCaffrey", "Jaxson Dart", "Justin Herbert", "Matthew Stafford", "Trevor Lawrence",
    "Caleb Williams", "Bo Nix", "Ashton Jeanty", "Saquon Barkley", "Omarion Hampton",
    "Nico Collins", "Chris Olave", "Garrett Wilson", "A.J. Brown", "George Pickens",
    "Kyler Murray", "Tyler Shough", "Baker Mayfield", "Jared Goff", "Josh Jacobs",
    "Breece Hall", "Kenneth Walker", "Javonte Williams", "Jeremiyah Love", "Kyren Williams",
    "Zay Flowers", "DeVonta Smith", "Davante Adams", "Tetairoa McMillan", "Tee Higgins",
    "Rashee Rice", "Emeka Egbuka", "Ladd McConkey", "Terry McLaurin", "Jameson Williams",
    "Jaylen Waddle", "Travis Etienne", "Quinshon Judkins", "Cam Skattebo", "C.J. Stroud",
    "Jordan Love", "Daniel Jones", "Sam Darnold", "Malik Willis", "D'Andre Swift",
    "Jadarian Price", "Bhayshul Tuten", "David Montgomery", "Colston Loveland", "Tyler Warren",
    "Harold Fannin", "Malik Nabers", "Mike Evans", "Stefon Diggs", "Rhamondre Stevenson",
    "TreVeyon Henderson", "Bucky Irving", "Kenneth Gainwell", "DJ Moore", "Rome Odunze",
    "Luther Burden", "Tony Pollard", "Jaylen Warren", "Rico Dowdle", "Aaron Jones",
    "Courtland Sutton", "Carnell Tate", "Bryce Young", "Cam Ward", "Sam LaPorta",
    "Tucker Kraft", "George Kittle", "Jonathon Brooks", "Chuba Hubbard", "Kyle Pitts",
    "Travis Kelce", "Michael Pittman", "DK Metcalf", "Marvin Harrison", "Michael Wilson",
    "Christian Watson", "Matthew Golden", "Rachaad White", "J.K. Dobbins", "Kyle Monangai",
    "Blake Corum", "RJ Harvey", "Parker Washington", "Jakobi Meyers", "Fernando Mendoza",
    "Aaron Rodgers", "Geno Smith", "Alec Pierce", "Josh Downs", "Jordyn Tyson",
    "Wan'Dale Robinson", "Brian Thomas", "Tyjae Spears", "Alvin Kamara", "Jordan Addison",
    "Khalil Shakir", "Xavier Worthy", "Chris Godwin", "Quentin Johnston", "Mark Andrews",
    "Jake Ferguson", "Dallas Goedert", "Deebo Samuel", "Jayden Reed", "Jacoby Brissett",
    "Tua Tagovailoa", "Michael Penix", "Deshaun Watson", "Shedeur Sanders", "Makai Lemon",
    "KC Concepcion", "Denzel Boston", "De'Zhaun Stribling", "Jordan Mason", "Isiah Pacheco",
    "Tyler Allgeier", "Romeo Doubs", "Jerry Jeudy", "Rashid Shaheed", "Jalen Coker",
    "Jayden Higgins", "Zach Charbonnet", "Woody Marks", "T.J. Hockenson", "Dalton Kincaid",
    "Kenyon Sadiq", "Isaiah Likely", "Jalen McMillan", "Calvin Ridley", "Tre Tucker",
    "Malik Washington", "Adonai Mitchell", "Juwan Johnson", "Hunter Henry", "Jacory Croskey-Merritt",
    "Chris Rodriguez", "Carson Beck", "Kirk Cousins", "J.J. McCarthy", "Rashod Bateman",
    "Jalen Nailor", "Dontayvion Wicks", "Pat Freiermuth", "Brenton Strange", "Dalton Schultz",
    "Caleb Douglas", "Jauan Jennings", "Ja'Kobi Lane", "Germie Bernard", "Travis Hunter",
    "Tank Dell", "Justice Hill", "Samaje Perine", "Braelon Allen", "Tank Bigsby",
    "Dylan Sampson", "Tyrone Tracy", "Brian Robinson", "Keaton Mitchell", "Jalen Tolbert",
    "Chris Bell", "Tre' Harris", "Cooper Kupp", "Jahan Dotson", "Gunnar Helm",
    "Oronde Gadsden", "Chig Okonkwo", "Greg Dulcich", "Mike Gesicki", "AJ Barner",
]

# ESPN Karabell Flex (no QB) - extra PPR redraft source, Aug 17 2026
ESPN_KARABELL_FLEX = [
    "Ja'Marr Chase", "Puka Nacua", "Jaxon Smith-Njigba", "Amon-Ra St. Brown", "Jahmyr Gibbs",
    "Bijan Robinson", "Jonathan Taylor", "De'Von Achane", "CeeDee Lamb", "Justin Jefferson",
    "Drake London", "James Cook", "Derrick Henry", "Chase Brown", "Trey McBride",
    "Brock Bowers", "Christian McCaffrey", "Ashton Jeanty", "Saquon Barkley", "Omarion Hampton",
    "Nico Collins", "Chris Olave", "Garrett Wilson", "A.J. Brown", "George Pickens",
    "Josh Jacobs", "Breece Hall", "Kenneth Walker", "Javonte Williams", "Jeremiyah Love",
    "Kyren Williams", "Zay Flowers", "DeVonta Smith", "Davante Adams", "Tetairoa McMillan",
    "Tee Higgins", "Rashee Rice", "Emeka Egbuka", "Ladd McConkey", "Terry McLaurin",
    "Jameson Williams", "Jaylen Waddle", "Travis Etienne", "Quinshon Judkins", "Cam Skattebo",
    "D'Andre Swift", "Jadarian Price", "Bhayshul Tuten", "David Montgomery", "Colston Loveland",
    "Tyler Warren", "Harold Fannin", "Malik Nabers", "Mike Evans", "Stefon Diggs",
    "Rhamondre Stevenson", "TreVeyon Henderson", "Bucky Irving", "Kenneth Gainwell", "DJ Moore",
    "Rome Odunze", "Luther Burden", "Tony Pollard", "Jaylen Warren", "Rico Dowdle",
    "Aaron Jones", "Courtland Sutton", "Carnell Tate", "Sam LaPorta", "Tucker Kraft",
    "George Kittle", "Jonathon Brooks", "Chuba Hubbard", "Kyle Pitts", "Travis Kelce",
    "Michael Pittman", "DK Metcalf", "Marvin Harrison", "Michael Wilson", "Christian Watson",
    "Matthew Golden", "Rachaad White", "J.K. Dobbins", "Kyle Monangai", "Blake Corum",
    "RJ Harvey", "Parker Washington", "Jakobi Meyers", "Alec Pierce", "Josh Downs",
    "Jordyn Tyson", "Wan'Dale Robinson", "Brian Thomas", "Tyjae Spears", "Alvin Kamara",
    "Jordan Addison", "Khalil Shakir", "Xavier Worthy", "Chris Godwin", "Quentin Johnston",
]

# Draft Sharks Dynasty Superflex, Aug 12 2026 (public top 25)
# https://www.draftsharks.com/dynasty-rankings/superflex
DRAFT_SHARKS_SF = [
    "Josh Allen", "Drake Maye", "Jayden Daniels", "Lamar Jackson", "Joe Burrow",
    "Caleb Williams", "Bijan Robinson", "Patrick Mahomes", "Ja'Marr Chase", "Justin Herbert",
    "Jalen Hurts", "Jahmyr Gibbs", "Jeremiyah Love", "Jonathan Taylor", "Trevor Lawrence",
    "Justin Jefferson", "Ashton Jeanty", "Jaxon Smith-Njigba", "Omarion Hampton", "Puka Nacua",
    "CeeDee Lamb", "Malik Nabers", "Amon-Ra St. Brown", "Drake London", "Brock Purdy",
]

# RotoWire Superflex, Aug 14 2026. Names mapped from the published team/pos board
# plus named ranks in the buy-low table.
# https://www.rotowire.com/football/article/2026-dynasty-superflex-rankings-buy-low-values-adp-127901
ROTOWIRE_SF = [
    "Josh Allen", "Drake Maye", "Ja'Marr Chase", "Jahmyr Gibbs", "Bijan Robinson",
    "Puka Nacua", "Lamar Jackson", "Jaxon Smith-Njigba", "Amon-Ra St. Brown", "Patrick Mahomes",
    "Jayden Daniels", "Joe Burrow", "Justin Jefferson", "Malik Nabers", "Caleb Williams",
    "Drake London", "Justin Herbert", "Trevor Lawrence", "CeeDee Lamb", "Ashton Jeanty",
    "De'Von Achane", "Jalen Hurts", "Bo Nix", "Jeremiyah Love", "Jaxson Dart",
    "Brock Bowers", "Tetairoa McMillan", "Nico Collins", "Trey McBride", "Omarion Hampton",
    "Brock Purdy", "Dak Prescott", "George Pickens", "Colston Loveland", "Emeka Egbuka",
    "Jordan Love", "Luther Burden", "Fernando Mendoza", "Jonathan Taylor", "Zay Flowers",
    "James Cook", "DeVonta Smith", "Ladd McConkey", "Chris Olave", "Carnell Tate",
    "Jordyn Tyson", "Christian McCaffrey", "Jared Goff", "Cam Ward", "Kenneth Walker",
]


def as_ranks(names):
    return {n: i for i, n in enumerate(names, 1)}
