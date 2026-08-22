# Ball Keep

Static site for [ballkeep.com](https://ballkeep.com), published from this repository root on GitHub Pages.

Powder-blue **FootKeep** desk. Navy-and-cream **BaseKeep**, hardwood **BasketKeep**, and purple **PitchKeep** through the sport pills.

## Football
- **The Keep** — Superflex Dynasty Super Aggregate top 400 (30+ desks; 50% the four long boards, 50% every other desk that ranked the player). The big draw.
- **The Board** — Superflex Redraft. This-year Superflex: Keep QB premium plus the PPR board, kids taxed. The next draw.
- **The X** — fun tape from X, not news
- **Trade Calculators** — Superflex Dynasty, 1QB Dynasty, Redraft PPR, Redraft Standard. Rank on each list becomes BK Value.
- **Recent Deals** — type a player, get every Superflex/1QB package on the desk tape
- Redraft PPR / Redraft Standard (200 names)
- 2026 drafted rookies
- BK Hot 'n' Cold
- **Player Pages** — every Keep 400 name, plus redraft, rookies, and Hot/Cold: ranks, board dump, a headshot, and a 2025 NFL (or college) highlight when we have the tape
- **BK News** — football injuries, roster moves, and coach reports scraped hourly from league RSS, Google News, X (`site:x.com`), and YouTube, then clustered into short stories with an aggregate summary and source links
- NFL 2026 schedules (all 32 teams)
- MLB September stretch-run schedules
- Discord mark **and Discord bot** (`bot/`)

## BaseKeep (`/bb`)
Separate sport, separate palette. Footer crossover only — baseball does not live in the football nav.

- **The Keep** — overall dynasty top 400, 23-board aggregate (RotoGraphs + The Dynasty Guru long boards, plus compiled expert slices)
- **BK News** — live at `bb/news.html`. Same hourly pipeline as football: IL, roster, DFA/call-up, and manager tape, clustered with links back to Keep player files
- **The Lineup** — dynasty hitters only (the bats on the long boards, up to 400)
- **BK's Pitchers** — top 150 overall dynasty pitchers
- **BK's Bullpen** — top 100 relievers for **saves**, and a second page for **saves + holds**
- **Redraft** — rest-of-season 400
- **Trade calculators** — Keep, Lineup, Pitchers, Redraft, Saves, SV+H. Same BK Value curve.
- **Dynasty Wire** — 15 stashes (short on purpose)
- **Redraft Wire** — priority 1–50, longer and louder
- **Player files** — Keep 400, one cream card each

## BasketKeep (`/bk`)
Separate sport, separate palette. Hardwood orange and night. Footer / header crossover only.

- **The Keep** — dynasty basketball top 400, 18-board aggregate
- **The Board** — this-year redraft (veterans climb, kids pay a tax)
- **Guards / Wings / Bigs** — position boards stripped from The Keep
- **Rookies** — compiled 2026 class plus the sophomores still priced like kids
- **BK News** — live at `bk/news.html`. Same hourly pipeline: injury, roster, coach tape
- **The X** — NBA memes
- **Trade calculators** — Keep and Board. Same BK Value curve.
- **Wires** — 15 dynasty stashes, redraft priority 1–50
- **Player files** — Keep 400, one hardwood card each

## PitchKeep (`/pl`)
Separate sport, separate palette. Premier League purple, pitch green, gold. Footer crossover only.

- **The Pitch** — overall Premier League top 400, ranked on **Sleeper BPL 2025** default soccer scoring applied to 2025/26 counting stats (goals, assists, CS, GA, cards, saves, penalties, tackles, CBI). FPL price / ownership / ICT and the short expert tapes still sit on every player file.
- **Attack / Midfield / Defence / Keepers** — position boards re-ranked on the same Sleeper points
- **Trade calculators** — Pitch, Attack, Midfield, Defence, Keepers. Same BK Value curve.
- **Player files** — every Pitch 400 name: headshot, Sleeper points, 2025/26 line, every board, YouTube tape

## BK Value
`value = round(12000 * exp(-0.0165 * (rank - 1)) / rank**0.18)`

Rank 1 is 12,000. 1QB Dynasty uses the same Superflex ranks but taxes quarterbacks to 38% of that number. Future picks on the dynasty calculators map to equivalent ranks on the curve. Fair trade = sides within 8%.

## Rebuild
```bash
python3 scripts/refresh_ranks.py
python3 scripts/news_scrape.py --sport all
python3 scripts/build_site.py
python3 bot/test_catalog.py
```

## BK News
Football news is live at `news.html`. Baseball news is live at `bb/news.html`. Basketball news is live at `bk/news.html`. Each hour GitHub Actions runs `scripts/news_scrape.py`:

1. Pull a small set of league RSS wires (ESPN, CBS, Yahoo, PFT, FantasyPros, RotoWire for football; ESPN/CBS/Yahoo/RotoWire for MLB).
2. Run a handful of Google News topic queries (injury, roster, coach/manager, practice, trade).
3. Pull X and video via Google News `site:x.com` / `site:youtube.com` — no X login and no HTML scrape of x.com.
4. Rotate eight Keep player-name queries so the full desk is covered across a day without hammering search.
5. Hash every URL, skip ones already in `data/news/state.json`, cluster the rest, and merge into `data/news/football.json`, `data/news/baseball.json`, `data/news/soccer.json`, or `data/news/basketball.json`.
6. Rebuild the static site and commit if anything changed.

```bash
python3 scripts/test_news.py
python3 scripts/news_scrape.py --sport football
python3 scripts/news_scrape.py --sport baseball
python3 scripts/news_scrape.py --sport basketball
python3 scripts/build_site.py
```

Scheduled runs need **Settings → Actions → General → Workflow permissions → Read and write** so the hourly job can push refreshed pages to the GitHub Pages branch.

Football rankings last aggregated August 21, 2026 from FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN (Eric Karabell Superflex + Flex, Field Yates), Draft Sharks, RotoWire, Dynasty Dealer, PFF, and X ranks from Derek Brown, Andrew Erickson, and Pat Fitzmaurice.

Baseball rankings last aggregated August 21, 2026 from RotoGraphs (Aug 14 model), The Dynasty Guru points Top 500 (Aug 10), plus compiled slices of FantasyPros, ESPN, Razzball, Pitcher List, RotoWire, CBS, NFBC, Ottoneu, BP, The Athletic, DLB, Dynasty Dugout, Fantasy Baseballers, FanGraphs The Board, Baseball America, MLB Pipeline, Mastersball, Four-Seam/Sekulski, Yahoo, ATC ROS, and Enos Slaughter. Closer charts: FantasyPros Aug 20 + ESPN reliever depth.

Unranked names are skipped in the mean — never treated as 999.

Premier League rankings last aggregated August 21, 2026 from official FPL 2025/26 points, 2026/27 prices, Gameweek 1 ownership, ICT, xGI, EP, and form, plus compiled slices of Premier League Scout, Fantasy Football Fix, Yahoo, Football Faithful, Fantasy Football Hub, Fantasy Football Scout, The Athletic, Sky, BBC, ESPN, WhoScored, SofaScore, Understat, FPL Draft, Planet FPL, and LiveFPL.

## Discord bot
The bot reads `data/discord-catalog.json` (emitted by the rebuild). Setup: [bot/README.md](bot/README.md).

`/bbplayer` `/bbkeep` `/bbtrade` `/bbwire` search the diamond desk.

`/plplayer` `/pitch` `/pltrade` search PitchKeep.
