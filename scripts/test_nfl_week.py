#!/usr/bin/env python3
"""Calendar week: Wednesday roll, America/New_York, clamps, stable URLs."""
import json
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from nfl_week import (
    WEEK_SHIFT,
    current_week,
    football_nav_groups,
    hours_ago,
    is_in_current_week,
    live_week,
    news_cutoff,
    stamp_updated,
    today_et,
    week_href,
    week_label,
    week_start,
)

ET = ZoneInfo("America/New_York")


def test_wednesday_roll():
    assert WEEK_SHIFT == 1
    assert current_week(date(2026, 9, 10)) == 1  # Thu kickoff
    assert current_week(date(2026, 9, 15)) == 1  # Tue
    assert current_week(date(2026, 9, 16)) == 2  # Wed
    assert current_week(date(2026, 10, 20)) == 6  # Tue
    assert current_week(date(2026, 10, 21)) == 7  # Wed
    assert current_week(date(2026, 10, 25)) == 7  # Sun
    assert live_week(date(2026, 10, 25)) == 7


def test_clamps():
    assert current_week(date(2026, 9, 9)) == 1
    assert current_week(date(2026, 8, 1)) == 1
    assert current_week(date(2027, 2, 1)) == 18
    assert current_week(date(2027, 12, 31)) == 18


def test_eastern_not_utc():
    # 03:30 UTC Wednesday is still Tuesday night in New York (EDT, UTC-4).
    late_tue = datetime(2026, 10, 21, 3, 30, tzinfo=timezone.utc)
    assert today_et(late_tue) == date(2026, 10, 20)
    assert current_week(late_tue) == 6
    # 04:30 UTC Wednesday is 12:30 AM Wednesday in New York.
    early_wed = datetime(2026, 10, 21, 4, 30, tzinfo=timezone.utc)
    assert today_et(early_wed) == date(2026, 10, 21)
    assert current_week(early_wed) == 7
    # After DST ends, midnight Eastern is 05:00 UTC.
    est_edge = datetime(2026, 11, 11, 4, 30, tzinfo=timezone.utc)
    assert today_et(est_edge) == date(2026, 11, 10)
    assert current_week(datetime(2026, 11, 11, 5, 15, tzinfo=timezone.utc)) >= 1


def test_stable_urls():
    sun = date(2026, 10, 25)
    assert week_href("dst", 7, today=sun) == "week-dst.html"
    assert week_href("kickers", 7, today=sun) == "week-kickers.html"
    assert week_href("matchups", 7, today=sun) == "week-matchups.html"
    assert week_href("matchups", 6, today=sun) == "week6-matchups.html"
    assert week_href("dst", 6, today=sun) == "week6-dst.html"
    # The Wednesday the clock moves to week 8, week 7 becomes an archive URL.
    wed8 = date(2026, 10, 28)
    assert current_week(wed8) == 8
    assert week_href("dst", today=wed8) == "week-dst.html"
    assert week_href("dst", 7, today=wed8) == "week7-dst.html"
    assert week_label(7) == "Week 7"
    assert week_start(7) == date(2026, 10, 21)
    assert week_start(2) == date(2026, 9, 16)


def test_news_cutoff():
    cut = news_cutoff(7)
    assert cut.date() == date(2026, 10, 20)
    assert is_in_current_week("2026-10-22T12:00:00Z", 7)
    assert not is_in_current_week("2026-09-01T12:00:00Z", 7)
    assert not is_in_current_week("2026-10-07T16:00:00Z", 7)


def test_stamp_uses_data_timestamp():
    now = datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc)
    assert abs(hours_ago("2026-10-25T04:00:00Z", now) - 12.0) < 0.01
    human, iso = stamp_updated("2026-10-17T21:37:00Z")
    assert human == "October 17, 2026"
    assert iso == "2026-10-17"
    # 02:00 UTC is still the previous evening in New York.
    human_et, iso_et = stamp_updated("2026-10-18T02:00:00Z")
    assert human_et == "October 17, 2026"
    assert iso_et == "2026-10-17"


def test_tuesday_scrape_matches_the_nav():
    """The Monday/Tuesday job stamps current_week(), the same clock as the nav.

    Tuesday 14:00 UTC is 10:00 AM Eastern in October, still the week that
    opened the previous Wednesday. Wednesday 00:00 Eastern moves the nav.
    meta.json stays on Tuesday's number until the next scrape. The daily
    rebuild runs scrape_weekly.py --if-behind so that gap closes at 1:15 AM.
    """
    from scrape_weekly import resolve_scrape_week

    tue = date(2026, 10, 20)
    wed = date(2026, 10, 21)
    assert resolve_scrape_week(["scrape_weekly.py"], tue) == live_week(tue)
    assert resolve_scrape_week(["scrape_weekly.py"], wed) == live_week(wed)
    assert live_week(wed) == live_week(tue) + 1
    tue_job = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
    assert resolve_scrape_week(["scrape_weekly.py"], tue_job) == live_week(tue_job)
    assert resolve_scrape_week(["scrape_weekly.py", "4"], tue) == 4
    daily = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily-rebuild.yml"
    assert "--if-behind" in daily.read_text()


def test_nav_links_the_stable_week_urls():
    """The live slate in the nav is week-*.html. weekN-*.html is a redirect stub."""
    groups = football_nav_groups()
    week = next(items for key, _label, items in groups if key == "week")
    hrefs = [item[0] for item in week]
    assert hrefs == [
        "weekly.html",
        "week-dst.html",
        "week-kickers.html",
        "week-matchups.html",
        "waiver.html",
        "injuries.html",
    ]
    root = Path(__file__).resolve().parents[1]
    live = live_week()
    banned = (
        f"week{live}-dst.html",
        f"week{live}-kickers.html",
        f"week{live}-matchups.html",
    )
    home = (root / "index.html").read_text()
    stream_at = home.find('class="desk-block week"')
    mine_at = home.find('class="desk-block mine"')
    stream = home[stream_at:mine_at]
    assert 'href="week-dst.html"' in stream
    assert 'href="week-kickers.html"' in stream
    assert 'href="week-matchups.html"' in stream
    assert "This week" in stream
    for name in banned:
        assert f'href="{name}"' not in home
        assert f'href="../{name}"' not in home
        stub = root / name
        assert stub.exists()
        body = stub.read_text()
        assert 'http-equiv="refresh"' in body
        assert f"week-{name.split('-', 1)[1]}" in body
        assert f'href="{name}"' not in body
    sitemap = (root / "sitemap.xml").read_text()
    for name in banned:
        assert name not in sitemap


def test_jobs_do_not_pin_the_live_week():
    """A rollover must not fail CI. Archive modules may name a past week."""
    root = Path(__file__).resolve().parents[1]
    pinned = []
    pin = re.compile(r"week_num\(\)\s*==\s*\d+")
    for path in (root / ".github" / "workflows").glob("*.yml"):
        text = path.read_text()
        if pin.search(text) or re.search(r"scrape_weekly\.py\s+\d+", text):
            pinned.append(str(path.relative_to(root)))
    for path in (root / "scripts").glob("test_*.py"):
        if pin.search(path.read_text()):
            pinned.append(str(path.relative_to(root)))
    assert pinned == []


def test_ranks_job_uses_a_mocked_week():
    """The Monday/Tuesday job writes the week it was given, not a baked-in number."""
    import scrape_weekly as sw

    calls = []

    def fp(week):
        calls.append(("fp", week))
        return 4

    def week_arg(week):
        calls.append(("week", week))

    def noarg():
        calls.append(("plain", None))

    def injuries():
        calls.append(("inj", None))
        return 12

    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        with patch.object(sw, "OUT", out), \
             patch.object(sw, "scrape_fp_weekly", fp), \
             patch.object(sw, "scrape_fourfor4", week_arg), \
             patch.object(sw, "scrape_sleeper_usage", week_arg), \
             patch.object(sw, "scrape_fp_stats", noarg), \
             patch.object(sw, "scrape_espn_adp", noarg), \
             patch.object(sw, "scrape_espn_injuries", injuries):
            assert sw.run_ranks(15) == 0
            meta = json.loads((out / "meta.json").read_text())
            assert meta["week"] == 15
            assert ("fp", 15) in calls
            assert calls.count(("week", 15)) == 2
            assert not (out / "fp-ecr-qb.json").exists()
            calls.clear()
            (out / "meta.json").unlink()
            with patch.object(sw, "scrape_fp_weekly", lambda week: 1), \
                 patch.object(sw, "scrape_espn_injuries", lambda: 0):
                assert sw.run_ranks(15) == 1
            assert not (out / "meta.json").exists()

    ran = []
    with patch.object(sw, "run_ranks", lambda week: ran.append(week) or 0), \
         patch.object(sys, "argv", ["scrape_weekly.py", "3"]):
        assert sw.main() == 0
    assert ran == [3]

    ran.clear()
    with patch.object(sw, "calendar_is_ahead", lambda today=None: False), \
         patch.object(sw, "run_ranks", lambda week: ran.append(week) or 0), \
         patch.object(sys, "argv", ["scrape_weekly.py", "--if-behind"]):
        assert sw.main() == 0
    assert ran == []

    ran.clear()
    with patch.object(sw, "calendar_is_ahead", lambda today=None: True), \
         patch.object(sw, "current_week", lambda today=None: 11), \
         patch.object(sw, "meta_week", lambda: 10), \
         patch.object(sw, "run_ranks", lambda week: ran.append(week) or 0), \
         patch.object(sys, "argv", ["scrape_weekly.py", "--if-behind"]):
        assert sw.main() == 0
    assert ran == [11]


def test_failure_alert_names_the_scheduled_jobs():
    from job_alert import WATCHED, issue_body, issue_title
    wf = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "alert-on-failure.yml"
    text = wf.read_text()
    for name in WATCHED:
        assert name in text
    assert "issues: write" in text
    assert "workflow_dispatch" in text
    assert issue_title("BK News") == "Ball Keep job failed: BK News"
    assert "check_freshness.py" in issue_body("BK News", "https://example.test/run", "failure")
    assert "Close it" in issue_body("BK News", "", "failure", test=True)


def test_week7_slate():
    from week7_boards import WEEK7_GAMES, week7_matchups
    assert len(WEEK7_GAMES) == 14
    rows = week7_matchups()
    assert rows[0]["key"] == "NE@CHI"
    assert all(not r.get("pick") for r in rows)


if __name__ == "__main__":
    test_wednesday_roll()
    test_clamps()
    test_eastern_not_utc()
    test_stable_urls()
    test_news_cutoff()
    test_stamp_uses_data_timestamp()
    test_tuesday_scrape_matches_the_nav()
    test_nav_links_the_stable_week_urls()
    test_jobs_do_not_pin_the_live_week()
    test_ranks_job_uses_a_mocked_week()
    test_failure_alert_names_the_scheduled_jobs()
    test_week7_slate()
    print("ok test_nfl_week")
