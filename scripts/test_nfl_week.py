#!/usr/bin/env python3
"""Calendar week: Wednesday roll, America/New_York, clamps, stable URLs."""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from nfl_week import (
    WEEK_SHIFT,
    current_week,
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
    test_week7_slate()
    print("ok test_nfl_week")
