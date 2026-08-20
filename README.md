# Ball Keep

Static site for [ballkeep.com](https://ballkeep.com), published from this repository root on GitHub Pages.

Powder-blue football desk. Navy-and-cream **BaseBallKeep** through the footer button.

## Football
- **The Keep** — Superflex dynasty top 300 (daily keystone)
- **Trade Calculators** — Superflex Dynasty, 1QB Dynasty, Redraft PPR, Redraft Standard. Rank on each list becomes BK Value.
- **Recent Deals** — type a player, get every Superflex/1QB package on the desk tape
- Redraft PPR / Redraft Standard
- 2026 drafted rookies
- BK Hot 'n' Cold
- The Board (long proprietary aggregate)
- **Player Pages** — every Keep 300 name, plus redraft top 50, rookies, and Hot/Cold: plus/minus, a few paragraphs, a headshot, and a 2025 NFL (or college) highlight when we have the tape
- **BK News** — football injuries, roster moves, and coach reports scraped hourly from league RSS, Google News, X (`site:x.com`), and YouTube, then clustered into short stories with an aggregate summary and source links
- NFL 2026 schedules (all 32 teams)
- MLB September stretch-run schedules
- Discord mark **and Discord bot** (`bot/`)

## BaseBallKeep (`/bb`)
Separate sport, separate palette. Footer crossover only — baseball does not live in the football nav.

- **The Keep** — overall dynasty top 300, 23-board aggregate (RotoGraphs + The Dynasty Guru long boards, plus compiled expert slices)
- **BK News** — live at `bb/news.html`. Same hourly pipeline as football: IL, roster, DFA/call-up, and manager tape, clustered with links back to Keep player files
- **The Lineup** — dynasty hitters only
- **BK's Pitchers** — top 100 overall dynasty pitchers
- **BK's Bullpen** — top 100 relievers for **saves**, and a second page for **saves + holds**
- **Redraft** — rest-of-season 300
- **Trade calculators** — Keep, Lineup, Pitchers, Redraft, Saves, SV+H. Same BK Value curve.
- **Dynasty Wire** — 15 stashes (short on purpose)
- **Redraft Wire** — priority 1–50, longer and louder
- **Player files** — Keep 300, one cream card each

## PitchKeep (`/pl`)
Separate sport, separate palette. Premier League purple, pitch green, gold. Footer crossover only.

- **The Pitch** — overall Premier League top 250, 24-board FPL super-aggregate (official FPL points / price / ownership / ICT / xGI plus compiled August expert slices)
- **Attack / Midfield / Defence / Keepers** — position boards re-ranked among themselves
- **Trade calculators** — Pitch, Attack, Midfield, Defence, Keepers. Same BK Value curve.
- **Player files** — every Pitch 250 name: headshot, 2025/26 FPL line, long take, every board, YouTube tape

## BK Value
`value = round(12000 * exp(-0.0165 * (rank - 1)) / rank**0.18)`

Rank 1 is 12,000. 1QB Dynasty uses the same Superflex ranks but taxes quarterbacks to 38% of that number. Future picks on the dynasty calculators map to equivalent ranks on the curve. Fair trade = sides within 8%.

## Rebuild
```bash
python3 scripts/refresh_ranks.py
python3 scripts/news_scrape.py --sport both
python3 scripts/build_site.py
python3 bot/test_catalog.py
```

## BK News
Football news is live at `news.html`. Baseball news is live at `bb/news.html`. Each hour GitHub Actions runs `scripts/news_scrape.py`:

1. Pull a small set of league RSS wires (ESPN, CBS, Yahoo, PFT, FantasyPros, RotoWire for football; ESPN/CBS/Yahoo/RotoWire for MLB).
2. Run a handful of Google News topic queries (injury, roster, coach/manager, practice, trade).
3. Pull X and video via Google News `site:x.com` / `site:youtube.com` — no X login and no HTML scrape of x.com.
4. Rotate eight Keep player-name queries so the full desk is covered across a day without hammering search.
5. Hash every URL, skip ones already in `data/news/state.json`, cluster the rest, and merge into `data/news/football.json` or `data/news/baseball.json`.
6. Rebuild the static site and commit if anything changed.

```bash
python3 scripts/test_news.py
python3 scripts/news_scrape.py --sport football
python3 scripts/news_scrape.py --sport baseball
python3 scripts/build_site.py
```

Scheduled runs need **Settings → Actions → General → Workflow permissions → Read and write** so the hourly job can push refreshed pages to the GitHub Pages branch.

Football rankings last aggregated August 20, 2026 from FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN (Eric Karabell Superflex + Flex, Field Yates), Draft Sharks, RotoWire, Dynasty Dealer, PFF, and X ranks from Derek Brown, Andrew Erickson, and Pat Fitzmaurice.

Baseball rankings last aggregated August 20, 2026 from RotoGraphs (Aug 14 model), The Dynasty Guru points Top 500 (Aug 10), plus compiled slices of FantasyPros, ESPN, Razzball, Pitcher List, RotoWire, CBS, NFBC, Ottoneu, BP, The Athletic, DLB, Dynasty Dugout, Fantasy Baseballers, FanGraphs The Board, Baseball America, MLB Pipeline, Mastersball, Four-Seam/Sekulski, Yahoo, ATC ROS, and Enos Slaughter. Closer charts: FantasyPros Aug 20 + ESPN reliever depth.

Unranked names are skipped in the mean — never treated as 999.

Premier League rankings last aggregated August 20, 2026 from official FPL 2025/26 points, 2026/27 prices, Gameweek 1 ownership, ICT, xGI, EP, and form, plus compiled slices of Premier League Scout, Fantasy Football Fix, Yahoo, Football Faithful, Fantasy Football Hub, Fantasy Football Scout, The Athletic, Sky, BBC, ESPN, WhoScored, SofaScore, Understat, FPL Draft, Planet FPL, and LiveFPL.

## Discord bot
The bot reads `data/discord-catalog.json` (emitted by the rebuild). Setup: [bot/README.md](bot/README.md).

`/bbplayer` `/bbkeep` `/bbtrade` `/bbwire` search the diamond desk.

`/plplayer` `/pitch` `/pltrade` search PitchKeep.
