"""Single source of truth for the live NFL week.

Calendar week is derived from the 2026 kickoff Thursday. Live nav, home
cards, and news recency all read this module. Existing weekN-*.html URLs
stay on disk as finished cards.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEASON = 2026
KICKOFF = date(2026, 9, 10)
META = ROOT / "data" / "weekly" / "meta.json"


def current_week(today: date | None = None) -> int:
    """NFL-style week. Rolls Wednesday. Clamped 1-18."""
    today = today or date.today()
    if today < KICKOFF:
        return 1
    week = 1 + ((today - KICKOFF).days + 3) // 7
    return min(18, max(1, week))


def live_week(today: date | None = None) -> int:
    """Date is the source of truth, not a stale meta.json."""
    return current_week(today)


def week_start(week: int | None = None, today: date | None = None) -> date:
    """Wednesday that opens this NFL week."""
    w = week or live_week(today)
    return KICKOFF + timedelta(days=(w - 1) * 7 - 1)


def week_href(kind: str, week: int | None = None) -> str:
    w = week or live_week()
    return {
        "dst": f"week{w}-dst.html",
        "kickers": f"week{w}-kickers.html",
        "matchups": f"week{w}-matchups.html",
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


def stamp_updated(scraped: str | None = None) -> tuple[str, str]:
    """Human UPDATED and ISO LASTMOD from this build's clock."""
    now = datetime.now(timezone.utc)
    human = f"{MONTHS[now.month - 1]} {now.day}, {now.year}"
    return human, now.strftime("%Y-%m-%d")


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
    return max(0.0, (now - dt).total_seconds() / 3600.0)


def news_cutoff(week: int | None = None, today: date | None = None) -> datetime:
    """Drop items older than the Wednesday that opened this week, minus one day."""
    start = week_start(week, today) - timedelta(days=1)
    return datetime(start.year, start.month, start.day, tzinfo=timezone.utc)


def is_in_current_week(value: str | None, week: int | None = None) -> bool:
    dt = parse_scraped(value)
    if not dt:
        return False
    return dt >= news_cutoff(week)


def football_nav_groups(week: int | None = None) -> list:
    w = week or live_week()
    return [
        ("rankings", "Rankings", [
            ("index.html", "Home"),
            ("the-keep.html", "Keep · Dynasty SF"),
            ("board.html", "Board · Redraft PPR"),
            ("the-classic.html", "Classic · Half-PPR"),
            ("redraft-superflex.html", "Redraft Superflex"),
            ("defenses.html", "The D · DST"),
            ("kickers.html", "Kickers"),
            ("the-fence.html", "Fence · Superflex + IDP"),
        ]),
        ("week", "This Week", [
            ("weekly.html", "Weekly"),
            (f"week{w}-dst.html", f"Week {w} DST"),
            (f"week{w}-kickers.html", f"Week {w} K"),
            (f"week{w}-matchups.html", f"Week {w} Predictions"),
            ("waiver.html", "Waivers"),
            ("injuries.html", "Injuries"),
        ]),
        ("tools", "Tools", [
            ("trade.html", "Trade"),
            ("the-handcuff.html", "Handcuff · RB handcuffs"),
            ("adp.html", "ADP"),
            ("the-method.html", "Method"),
        ]),
        ("mine", "My Team", [
            ("league.html", "My Team"),
        ]),
        ("reading", "Reading", [
            ("articles.html", "Articles"),
            ("news.html", "News"),
            ("the-x.html", "The X · Memes"),
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
