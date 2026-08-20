# Ball Keep

Static site for [ballkeep.com](https://ballkeep.com), published from this repository root on GitHub Pages.

## Pages
- **The Keep** — Superflex dynasty top 100 (daily keystone)
- **Trade Calculators** — Superflex Dynasty, 1QB Dynasty, Redraft PPR, Redraft Standard. Rank on each list becomes BK Value.
- **Recent Deals** — type a player, get every Superflex/1QB package on the desk tape
- Redraft PPR / Redraft Standard
- 2026 drafted rookies
- BK Hot 'n' Cold
- The Board (long proprietary aggregate)
- **Player Pages** — every top-50 name from those lists, plus rookies and Hot/Cold: plus/minus, a few paragraphs, a headshot, and a 2025 NFL (or college) highlight
- **BK News** — football injuries, roster moves, and coach reports scraped hourly from league RSS, Google News, X (`site:x.com`), and YouTube, then clustered into short stories with an aggregate summary and source links
- NFL 2026 schedules (all 32 teams)
- MLB September stretch-run schedules
- Discord mark **and Discord bot** (`bot/`) — slash commands for ranks, trade calculator, videos, plus `/publish` to write the whole site into a server

## BK Value
`value = round(12000 * exp(-0.0165 * (rank - 1)) / rank**0.18)`

Rank 1 is 12,000. 1QB Dynasty uses the same Superflex ranks but taxes quarterbacks to 38% of that number. Future picks on the dynasty calculators map to equivalent ranks on the curve.

## Rebuild
```bash
python3 scripts/build_site.py
```

## BK News
Football news is live at `news.html`. Each hour GitHub Actions runs `scripts/news_scrape.py`:

1. Pull a small set of NFL RSS wires (ESPN, CBS, Yahoo, PFT, FantasyPros, RotoWire).
2. Run a handful of Google News topic queries (injury, roster, coach, practice, trade).
3. Pull X and video via Google News `site:x.com` / `site:youtube.com` — no X login and no HTML scrape of x.com.
4. Rotate eight Keep player-name queries so the full desk is covered across a day without hammering search.
5. Hash every URL, skip ones already in `data/news/state.json`, cluster the rest, and merge into `data/news/football.json`.
6. Rebuild the static site and commit if anything changed.

Baseball uses the same pipeline (`data/news/baseball.json`) but is **not published** until `PUBLISH_BASEBALL_NEWS` is flipped in `scripts/build_site.py`.

```bash
python3 scripts/test_news.py
python3 scripts/news_scrape.py --sport football
python3 scripts/build_site.py
```

Scheduled runs need **Settings → Actions → General → Workflow permissions → Read and write** so the hourly job can push refreshed pages to the GitHub Pages branch.

Rankings last aggregated August 20, 2026 from FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN (Eric Karabell Superflex + Flex, Field Yates), Draft Sharks, RotoWire, Dynasty Dealer, PFF, and X ranks from Derek Brown, Andrew Erickson, and Pat Fitzmaurice.

## Discord bot
The bot reads `data/discord-catalog.json` (emitted by the rebuild). Setup: [bot/README.md](bot/README.md).
