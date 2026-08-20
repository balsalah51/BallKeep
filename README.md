# Ball Keep

Static site for [ballkeep.com](https://ballkeep.com), published from this repository root on GitHub Pages.

## Pages
- **The Keep** — Superflex dynasty top 100 (daily keystone)
- **Trade Calculators** — Superflex Dynasty, 1QB Dynasty, Redraft PPR, Redraft Standard. Rank on each list becomes BK Value.
- Redraft PPR / Redraft Standard
- 2026 drafted rookies
- BK Hot 'n' Cold
- The Board (long proprietary aggregate)
- **Player Pages** — every top-50 name from those lists, plus rookies and Hot/Cold: plus/minus, a few paragraphs, a headshot, and a 2025 NFL (or college) highlight
- NFL 2026 schedules (all 32 teams)
- MLB September stretch-run schedules
- Discord mark

## BK Value
`value = round(12000 * exp(-0.0165 * (rank - 1)) / rank**0.18)`

Rank 1 is 12,000. 1QB Dynasty uses the same Superflex ranks but taxes quarterbacks to 38% of that number. Future picks on the dynasty calculators map to equivalent ranks on the curve.

## Rebuild
```bash
python3 scripts/build_site.py
```

Rankings last aggregated August 20, 2026 from FantasyPros, PFN, Dynasty Nerds, KeepTradeCut, ESPN (Eric Karabell Superflex + Flex, Field Yates), Draft Sharks, RotoWire, Dynasty Dealer, PFF, and X ranks from Derek Brown, Andrew Erickson, and Pat Fitzmaurice.
