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
- NFL 2026 schedules (all 32 teams)
- MLB September stretch-run schedules
- Discord mark **and Discord bot** (`bot/`)

## BaseBallKeep (`/bb`)
Separate sport, separate palette. Footer crossover only — baseball does not live in the football nav.

- **The Keep** — overall dynasty top 300, 23-board aggregate (RotoGraphs + The Dynasty Guru long boards, plus compiled expert slices)
- **The Lineup** — dynasty hitters only
- **BK's Pitchers** — top 100 overall dynasty pitchers
- **BK's Bullpen** — top 100 relievers for **saves**, and a second page for **saves + holds**
- **Redraft** — rest-of-season 300
- **Trade calculators** — Keep, Lineup, Pitchers, Redraft, Saves, SV+H. Same BK Value curve.
- **Dynasty Wire** — 15 stashes (short on purpose)
- **Redraft Wire** — priority 1–50, longer and louder
- **Player files** — Keep 300, one cream card each

## BK Value
`value = round(12000 * exp(-0.0165 * (rank - 1)) / rank**0.18)`

Rank 1 is 12,000. 1QB Dynasty uses the same Superflex ranks but taxes quarterbacks to 38% of that number. Future picks on the dynasty calculators map to equivalent ranks on the curve. Fair trade = sides within 8%.

## Rebuild
```bash
python3 scripts/build_site.py
```

Football rankings last aggregated August 20, 2026 from FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN (Eric Karabell Superflex + Flex, Field Yates), Draft Sharks, RotoWire, Dynasty Dealer, PFF, and X ranks from Derek Brown, Andrew Erickson, and Pat Fitzmaurice.

Baseball rankings last aggregated August 20, 2026 from RotoGraphs (Aug 14 model), The Dynasty Guru points Top 500 (Aug 10), plus compiled slices of FantasyPros, ESPN, Razzball, Pitcher List, RotoWire, CBS, NFBC, Ottoneu, BP, The Athletic, DLB, Dynasty Dugout, Fantasy Baseballers, FanGraphs The Board, Baseball America, MLB Pipeline, Mastersball, Four-Seam/Sekulski, Yahoo, ATC ROS, and Enos Slaughter. Closer charts: FantasyPros Aug 20 + ESPN reliever depth.

Unranked names are skipped in the mean — never treated as 999.

## Discord bot
The bot reads `data/discord-catalog.json` (emitted by the rebuild). Setup: [bot/README.md](bot/README.md).

`/bbplayer` `/bbkeep` `/bbtrade` `/bbwire` search the diamond desk.
