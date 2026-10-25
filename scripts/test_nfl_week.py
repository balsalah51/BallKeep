#!/usr/bin/env python3
from datetime import date, datetime, timezone

from nfl_week import (
    current_week,
    hours_ago,
    is_in_current_week,
    live_week,
    news_cutoff,
    stamp_updated,
    week_href,
    week_label,
    week_start,
)


def test_calendar_week():
    assert current_week(date(2026, 9, 10)) == 1
    assert current_week(date(2026, 10, 17)) == 6
    assert current_week(date(2026, 10, 25)) == 7
    assert live_week(date(2026, 10, 25)) == 7


def test_week_hrefs():
    assert week_href("dst", 7) == "week7-dst.html"
    assert week_href("matchups", 6) == "week6-matchups.html"
    assert week_label(7) == "Week 7"
    assert week_start(7) == date(2026, 10, 21)


def test_news_cutoff():
    cut = news_cutoff(7)
    assert cut.date() == date(2026, 10, 20)
    assert is_in_current_week("2026-10-22T12:00:00Z", 7)
    assert not is_in_current_week("2026-09-01T12:00:00Z", 7)


def test_hours_ago():
    now = datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc)
    assert abs(hours_ago("2026-10-25T04:00:00Z", now) - 12.0) < 0.01
    human, iso = stamp_updated()
    assert iso
    assert human


def test_week7_slate():
    from week7_boards import WEEK7_GAMES, week7_matchups
    assert len(WEEK7_GAMES) == 14
    rows = week7_matchups()
    assert rows[0]["key"] == "NE@CHI"
    assert all(not r.get("pick") for r in rows)


if __name__ == "__main__":
    test_calendar_week()
    test_week_hrefs()
    test_news_cutoff()
    test_hours_ago()
    test_week7_slate()
    print("ok test_nfl_week")
