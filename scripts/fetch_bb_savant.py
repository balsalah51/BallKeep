#!/usr/bin/env python3
"""Pull Baseball Savant percentile ranks (Starcast) for the Keep 400."""
from __future__ import annotations

import csv
import io
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bb-savant.json"
UA = "Mozilla/5.0 (compatible; BallKeep/1.0; +https://ballkeep.com)"
YEARS = (2026, 2025)


def get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def percentile_csv(kind: str, year: int) -> list[dict]:
    url = (
        "https://baseballsavant.mlb.com/leaderboard/percentile-rankings"
        f"?type={kind}&year={year}&csv=true"
    )
    raw = get(url).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))


def slim(row: dict, year: int) -> dict:
    out = {"year": year, "player_name": (row.get("player_name") or "").strip()}
    for k, v in row.items():
        if k in ("player_name", "player_id", "year"):
            continue
        v = (v or "").strip()
        if v == "":
            continue
        try:
            out[k] = int(float(v))
        except ValueError:
            out[k] = v
    return out


def is_full(rec: dict, kind: str) -> bool:
    if kind == "batter":
        return rec.get("xwoba") not in (None, "")
    return rec.get("xera") not in (None, "") or rec.get("xwoba") not in (None, "")


def merge_kind(kind: str) -> dict:
    by_id: dict[str, dict] = {}
    for year in YEARS:
        rows = percentile_csv(kind, year)
        print(kind, year, len(rows))
        for row in rows:
            pid = str(row.get("player_id") or "").strip()
            if not pid:
                continue
            rec = slim(row, year)
            prev = by_id.get(pid)
            if not prev:
                by_id[pid] = rec
                continue
            if is_full(prev, kind):
                continue
            if is_full(rec, kind) or len(rec) > len(prev):
                by_id[pid] = rec
    return by_id


def main():
    batters = merge_kind("batter")
    pitchers = merge_kind("pitcher")
    payload = {
        "updated": "August 20, 2026",
        "source": "https://baseballsavant.mlb.com/leaderboard/percentile-rankings",
        "batters": batters,
        "pitchers": pitchers,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(
        "wrote", OUT.name,
        "batters", len(batters),
        "full", sum(1 for v in batters.values() if is_full(v, "batter")),
        "pitchers", len(pitchers),
        "full", sum(1 for v in pitchers.values() if is_full(v, "pitcher")),
    )


if __name__ == "__main__":
    main()
