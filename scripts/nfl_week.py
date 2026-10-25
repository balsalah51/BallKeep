"""Single source of truth for the live NFL week.

Calendar week is derived from the 2026 kickoff Thursday. The week rolls
Wednesday morning in America/New_York: the offset is +1. An offset of +3
rolls Monday and was the bug. Live nav, home cards, and news recency all
read this module. Current-week pages use stable filenames (week-dst.html).
Finished weeks stay at weekN-*.html.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SEASON = 2026
KICKOFF = date(2026, 9, 10)
META = ROOT / "data" / "weekly" / "meta.json"
ET = ZoneInfo("America/New_York")
# +1 rolls the week on Wednesday. +3 rolls it on Monday.
WEEK_SHIFT = 1

STABLE_WEEK = {
    "dst": "week-dst.html",
    "kickers": "week-kickers.html",
    "matchups": "week-matchups.html",
}


def today_et(today: date | datetime | None = None) -> date:
    """Calendar date in America/New_York. GitHub Actions clocks are UTC."""
    if today is None:
        return datetime.now(ET).date()
    if isinstance(today, datetime):
        if today.tzinfo is None:
            today = today.replace(tzinfo=timezone.utc)
        return today.astimezone(ET).date()
    return today


def current_week(today: date | datetime | None = None) -> int:
    """NFL week. Rolls Wednesday in America/New_York. Clamped 1-18."""
    today = today_et(today)
    if today < KICKOFF:
        return 1
    week = 1 + ((today - KICKOFF).days + WEEK_SHIFT) // 7
    return min(18, max(1, week))


def live_week(today: date | datetime | None = None) -> int:
    """Date is the source of truth, not a stale meta.json."""
    return current_week(today)


def week_start(week: int | None = None, today: date | datetime | None = None) -> date:
    """Wednesday that opens this NFL week."""
    w = week or live_week(today)
    return KICKOFF + timedelta(days=(w - 1) * 7 - 1)


def numbered_week_href(kind: str, week: int) -> str:
    return {
        "dst": f"week{week}-dst.html",
        "kickers": f"week{week}-kickers.html",
        "matchups": f"week{week}-matchups.html",
    }[kind]


def week_href(kind: str, week: int | None = None, today: date | datetime | None = None) -> str:
    """Stable URL for the live week. Older weeks keep weekN-*.html."""
    live = live_week(today)
    w = live if week is None else week
    if kind in STABLE_WEEK and w == live:
        return STABLE_WEEK[kind]
    if kind in STABLE_WEEK:
        return numbered_week_href(kind, w)
    return {
        "weekly": "weekly.html",
        "waiver": "waiver.html",
        "injuries": "injuries.html",
    }[kind]


def week_label(week: int | None = None) -> str:
    return f"Week {week or live_week()}"


MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def ranks_scraped_iso() -> str | None:
    if not META.exists():
        return None
    try:
        return json.loads(META.read_text()).get("scraped") or None
    except json.JSONDecodeError:
        return None


def stamp_updated(scraped: str | None = None) -> tuple[str, str]:
    """Human date and ISO date from a real scrape timestamp, in Eastern time.

    Pass scraped= to override. The default reads data/weekly/meta.json.
    """
    raw = ranks_scraped_iso() if scraped is None else scraped
    dt = parse_scraped(raw) if raw else None
    if dt is None:
        dt = datetime.now(ET)
    local = dt.astimezone(ET)
    human = f"{MONTHS[local.month - 1]} {local.day}, {local.year}"
    return human, local.strftime("%Y-%m-%d")


def ranks_are_stale(max_hours: float = 96, now: datetime | None = None) -> bool:
    hours = hours_ago(ranks_scraped_iso(), now)
    return hours is None or hours > max_hours


def parse_scraped(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def hours_ago(value: str | None, now: datetime | None = None) -> float | None:
    dt = parse_scraped(value)
    if not dt:
        return None
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return max(0.0, (now - dt).total_seconds() / 3600.0)


def news_cutoff(week: int | None = None, today: date | datetime | None = None) -> datetime:
    """Drop items older than the Tuesday before the Wednesday that opened this week."""
    start = week_start(week, today) - timedelta(days=1)
    return datetime(start.year, start.month, start.day, tzinfo=timezone.utc)


def is_in_current_week(value: str | None, week: int | None = None) -> bool:
    dt = parse_scraped(value)
    if not dt:
        return False
    return dt >= news_cutoff(week)


def football_nav_groups(week: int | None = None) -> list:
    """Header and footer.

    The live slate is week-dst.html, week-kickers.html, and week-matchups.html.
    weekN-*.html for that same week is only a redirect for old bookmarks, so
    the nav never links there.
    """
    w = week or live_week()
    if w == live_week():
        dst, kickers, matchups = (
            STABLE_WEEK["dst"],
            STABLE_WEEK["kickers"],
            STABLE_WEEK["matchups"],
        )
    else:
        dst = numbered_week_href("dst", w)
        kickers = numbered_week_href("kickers", w)
        matchups = numbered_week_href("matchups", w)
    return [
        ("rankings", "Rankings", [
            ("index.html", "Home"),
            ("the-keep.html", "Keep · Dynasty SF"),
            ("board.html", "Board · Redraft PPR"),
            ("the-classic.html", "Classic · Half-PPR"),
            ("redraft-superflex.html", "Redraft Superflex"),
            ("defenses.html", "The D", "Team defenses"),
            ("kickers.html", "Kickers"),
            ("the-fence.html", "The Fence", "Superflex and IDP"),
        ]),
        ("week", "This Week", [
            ("weekly.html", "Weekly"),
            (dst, f"{week_label(w)} DST"),
            (kickers, f"{week_label(w)} K"),
            (matchups, f"{week_label(w)} Predictions"),
            ("waiver.html", "Waivers"),
            ("injuries.html", "Injuries"),
        ]),
        ("tools", "Tools", [
            ("trade.html", "Trade"),
            ("the-handcuff.html", "The Handcuff", "Running back backups"),
            ("adp.html", "ADP"),
            ("the-method.html", "Method"),
        ]),
        ("mine", "My Team", [
            ("league.html", "My Team"),
        ]),
        ("reading", "Reading", [
            ("articles.html", "Articles"),
            ("news.html", "News"),
            ("the-x.html", "The X", "Memes"),
            ("touches.html", "Touches"),
            ("players/index.html", "Players"),
            ("hot-n-cold.html", "Hot 'n' Cold"),
            ("the-recap.html", "Week 1 Recap"),
            ("the-market.html", "Week 1 Market"),
        ]),
        ("sports", "Other Sports", [
            ("nfl-schedule.html", "NFL"),
            ("mlb-schedule.html", "MLB"),
            ("bpl-schedule.html", "BPL"),
            ("bb/index.html", "BaseKeep"),
            ("bk/index.html", "BasketKeep"),
            ("pl/index.html", "PitchKeep"),
        ]),
    ]
