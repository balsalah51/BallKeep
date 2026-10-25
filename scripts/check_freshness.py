#!/usr/bin/env python3
"""Fail the workflow when ranks or the football wire are older than a threshold.

The pages may already show an honest stamp. This makes the Actions run red
so a stale scrape is not quiet.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nfl_week import hours_ago, live_week, ranks_scraped_iso  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks-hours", type=float, default=96)
    ap.add_argument("--news-hours", type=float, default=30)
    ap.add_argument("--news-required", action="store_true")
    args = ap.parse_args()
    problems = []
    rank_hours = hours_ago(ranks_scraped_iso())
    if rank_hours is None:
        problems.append("ranks have no scraped timestamp")
    elif rank_hours > args.ranks_hours:
        problems.append(f"ranks are {rank_hours:.1f}h old (limit {args.ranks_hours:g}h)")
    news_path = ROOT / "data" / "news" / "football.json"
    news_updated = ""
    if news_path.exists():
        try:
            news_updated = json.loads(news_path.read_text()).get("updated") or ""
        except json.JSONDecodeError:
            news_updated = ""
    news_hours = hours_ago(news_updated)
    week = live_week()
    if 1 <= week <= 18 and (args.news_required or news_hours is None or news_hours > args.news_hours):
        if news_hours is None:
            problems.append("football news has no updated timestamp")
        elif news_hours > args.news_hours:
            problems.append(f"football news is {news_hours:.1f}h old (limit {args.news_hours:g}h)")
    if problems:
        print("STALE:", "; ".join(problems))
        return 1
    print(f"fresh ranks={rank_hours} news={news_hours} week={week}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
