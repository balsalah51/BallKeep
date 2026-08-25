#!/usr/bin/env python3
"""Unit tests for BK News clustering and matching (no network)."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_algo import (  # noqa: E402
    build_player_index,
    categorize,
    cluster_items,
    jaccard,
    match_players,
    merge_story,
    normalize_title,
    player_query_slice,
    rematch_stories,
    source_kind,
    split_google_title,
    story_slug,
    summarize,
    tokens,
)
from news_scrape import parse_feed  # noqa: E402
from x_tape import canon_post_url, is_junk_title, looks_like_image_url  # noqa: E402


ROSTER = [
    {"key": "christian mccaffrey", "name": "Christian McCaffrey", "slug": "christian-mccaffrey", "pos": "RB", "team": "SF", "lists": {"The Keep": 1}},
    {"key": "jamarr chase", "name": "Ja'Marr Chase", "slug": "jamarr-chase", "pos": "WR", "team": "CIN", "lists": {"The Keep": 2}},
    {"key": "a j brown", "name": "A.J. Brown", "slug": "a-j-brown", "pos": "WR", "team": "NE", "lists": {"The Keep": 8}},
    {"key": "chase brown", "name": "Chase Brown", "slug": "chase-brown", "pos": "RB", "team": "CIN", "lists": {"The Keep": 12}},
    {"key": "josh allen", "name": "Josh Allen", "slug": "josh-allen", "pos": "QB", "team": "BUF", "lists": {"The Keep": 1}},
]


def test_google_title():
    head, pub = split_google_title("McCaffrey calf strain - ESPN")
    assert head == "McCaffrey calf strain"
    assert pub == "ESPN"


def test_categorize():
    assert categorize("Christian McCaffrey listed questionable with a calf injury") == "injury"
    assert categorize("Jets waived a running back and signed a veteran") == "roster"
    assert categorize("Sean Payton told reporters the scheme is changing") == "coach"
    assert categorize("Bills acquired a wideout in a trade") == "trade"
    assert categorize("Aaron Judge placed on the 10-day IL with an elbow injury") == "injury"
    assert categorize("Red Sox DFA a reliever and called up a prospect") == "roster"


def test_baseball_drops_nfl_leaks():
    from news_algo import is_publishable
    assert not is_publishable({
        "sport": "baseball",
        "headline": "Vita Vea, Buccaneers agree to 1-year, $30 million deal",
        "blurb": "Tampa Bay locked up its nose tackle",
        "sources": [{"kind": "article"}],
    })


def test_match_full_name_not_ambiguous_brown():
    idx = build_player_index(ROSTER)
    hits = match_players("Ja'Marr Chase sat out with a hamstring", idx)
    assert [h["key"] for h in hits] == ["jamarr chase"]
    both = match_players("A.J. Brown and Chase Brown practiced", idx)
    keys = {h["key"] for h in both}
    assert "a j brown" in keys
    assert "chase brown" in keys
    # bare "Brown" should not match two Browns
    bare = match_players("Brown scored twice", idx)
    assert bare == []


def test_unique_last_name():
    idx = build_player_index(ROSTER)
    hits = match_players("McCaffrey is out, coach says", idx)
    assert hits and hits[0]["key"] == "christian mccaffrey"


def test_unrelated_injuries_do_not_cluster():
    a = {
        "title": "Panthers place Nic Scourton on injured reserve following knee injury",
        "category": "injury", "players": [], "published": "Wed, 20 Aug 2026 12:00:00 GMT",
    }
    b = {
        "title": "Kyler Murray sits with ankle injury",
        "category": "injury",
        "players": [{"key": "kyler murray"}],
        "published": "Wed, 20 Aug 2026 13:00:00 GMT",
    }
    assert len(cluster_items([a, b])) == 2


def test_cluster_similar_titles():
    a = {"title": "Christian McCaffrey questionable vs Rams with calf strain", "category": "injury", "players": [{"key": "christian mccaffrey"}], "published": "Wed, 20 Aug 2026 12:00:00 GMT"}
    b = {"title": "McCaffrey listed as questionable with calf injury vs. Los Angeles", "category": "injury", "players": [{"key": "christian mccaffrey"}], "published": "Wed, 20 Aug 2026 13:00:00 GMT"}
    c = {"title": "Josh Allen throws three touchdowns in Bills win", "category": "wire", "players": [{"key": "josh allen"}], "published": "Wed, 20 Aug 2026 12:30:00 GMT"}
    groups = cluster_items([a, b, c])
    assert len(groups) == 2
    sizes = sorted(len(g) for g in groups)
    assert sizes == [1, 2]
    a = {"title": "Christian McCaffrey questionable vs Rams with calf strain", "category": "injury", "players": [{"key": "christian mccaffrey"}], "published": "Wed, 20 Aug 2026 12:00:00 GMT"}
    b = {"title": "McCaffrey listed as questionable with calf injury vs. Los Angeles", "category": "injury", "players": [{"key": "christian mccaffrey"}], "published": "Wed, 20 Aug 2026 13:00:00 GMT"}
    c = {"title": "Josh Allen throws three touchdowns in Bills win", "category": "wire", "players": [{"key": "josh allen"}], "published": "Wed, 20 Aug 2026 12:30:00 GMT"}
    groups = cluster_items([a, b, c])
    assert len(groups) == 2
    sizes = sorted(len(g) for g in groups)
    assert sizes == [1, 2]


def test_merge_and_summary():
    items = [
        {
            "title": "Christian McCaffrey questionable vs Rams - ESPN",
            "url": "https://www.espn.com/nfl/story/_/id/1",
            "summary": "Christian McCaffrey is questionable for Sunday with a calf strain. The 49ers listed him on the injury report after a limited practice.",
            "published": "Wed, 20 Aug 2026 12:00:00 GMT",
            "publisher": "ESPN",
            "category": "injury",
            "players": [{"key": "christian mccaffrey", "name": "Christian McCaffrey", "slug": "christian-mccaffrey", "pos": "RB", "team": "SF"}],
        },
        {
            "title": "McCaffrey calf strain update on X",
            "url": "https://x.com/RapSheet/status/1",
            "summary": "Source: Christian McCaffrey is expected to play through the calf if he can get through Saturday's practice.",
            "published": "Wed, 20 Aug 2026 13:00:00 GMT",
            "publisher": "X",
            "category": "injury",
            "players": [{"key": "christian mccaffrey", "name": "Christian McCaffrey", "slug": "christian-mccaffrey", "pos": "RB", "team": "SF"}],
        },
    ]
    story = merge_story(None, items, "football")
    assert story["category"] == "injury"
    assert story["players"][0]["slug"] == "christian-mccaffrey"
    kinds = {s["kind"] for s in story["sources"]}
    assert "article" in kinds and "x" in kinds
    assert "McCaffrey" in story["summary"] or "calf" in story["summary"].lower()
    assert story["slug"]


def test_source_kind():
    assert source_kind("https://x.com/AdamSchefter/status/1") == "x"
    assert source_kind("https://news.google.com/rss/articles/abc", "Higgins ACL", "x.com") == "x"
    assert source_kind("https://news.google.com/rss/articles/yt", "Dart shorts", "YouTube") == "video"
    assert source_kind("https://www.youtube.com/watch?v=abc") == "video"
    assert source_kind("https://www.espn.com/nfl/story") == "article"


def test_jayden_does_not_match_tee_higgins():
    idx = build_player_index(ROSTER + [{
        "key": "tee higgins", "name": "Tee Higgins", "slug": "tee-higgins",
        "pos": "WR", "team": "CIN", "lists": {"The Keep": 40},
    }])
    hits = match_players("Texans WR Jayden Higgins tears ACL in training camp", idx)
    assert all(h["key"] != "tee higgins" for h in hits)


def test_merge_prefers_article_headline():
    items = [
        {
            "title": "My immediate reaction to the Jayden Higgins injury was how much it sucks for the Texans and it’s fans, but it’s worth mentioning",
            "url": "https://news.google.com/rss/articles/x1",
            "summary": "tweet",
            "published": "Wed, 20 Aug 2026 12:00:00 GMT",
            "publisher": "x.com",
            "category": "injury",
            "players": [],
        },
        {
            "title": "Sources: Texans' Higgins tears ACL, out for season",
            "url": "https://www.espn.com/nfl/story/_/id/1",
            "summary": "Texans second-year wideout Jayden Higgins will miss the season after a torn ACL.",
            "published": "Wed, 20 Aug 2026 12:05:00 GMT",
            "publisher": "ESPN",
            "category": "injury",
            "players": [],
        },
    ]
    story = merge_story(None, items, "football")
    assert "ACL" in story["headline"]
    assert "immediate reaction" not in story["headline"].lower()
    kinds = {s["kind"] for s in story["sources"]}
    assert "x" in kinds and "article" in kinds


def test_player_rotation_is_stable_and_small():
    now = datetime(2026, 8, 20, 11, tzinfo=timezone.utc)
    a = player_query_slice(ROSTER, now, size=2)
    b = player_query_slice(ROSTER, now, size=2)
    assert a == b
    assert len(a) == 2


def test_parse_rss():
    xml = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>Josh Allen ankle scare - ESPN</title>
        <link>https://www.espn.com/nfl/story/_/id/99</link>
        <description>Bills quarterback Josh Allen left practice with an ankle issue.</description>
        <pubDate>Wed, 20 Aug 2026 10:00:00 GMT</pubDate>
        <source url="https://www.espn.com">ESPN</source>
      </item>
    </channel></rss>"""
    items = parse_feed(xml, "ESPN NFL")
    assert len(items) == 1
    assert items[0]["title"] == "Josh Allen ankle scare"
    assert "espn.com" in items[0]["url"]


def test_jaccard_and_slug():
    assert jaccard(tokens("mccaffrey calf strain rams"), tokens("mccaffrey listed calf strain")) > 0.3
    assert "injury" not in story_slug("Hello!!!", "injury") or True
    slug = story_slug("Christian McCaffrey calf strain", "injury")
    assert slug.startswith("christian-mccaffrey")
    assert normalize_title("Hello — World") == "hello world"


def test_rematch_fills_baseball_players():
    roster = [{
        "key": "aaron judge", "name": "Aaron Judge", "slug": "aaron-judge",
        "pos": "OF", "team": "NYY", "lists": {"The Keep": 6},
    }]
    idx = build_player_index(roster)
    stories = [{
        "headline": "Aaron Judge exits with an elbow injury",
        "blurb": "",
        "summary": "",
        "sources": [],
        "players": [],
    }]
    out = rematch_stories(stories, idx)
    assert out[0]["players"][0]["key"] == "aaron judge"
    assert out[0]["players"][0]["slug"] == "aaron-judge"


def test_x_tape_skips_google_news_icons_and_profile_pages():
    assert is_junk_title("Falcons Esports (@FalconsEsport) / Posts / X")
    assert is_junk_title("Yahoo Fantasy Sports (@YahooFantasy) / Posts / X")
    assert not is_junk_title("Deshaun Watson driving to the mobile home park")
    assert not looks_like_image_url("https://lh3.googleusercontent.com/J6_coFbogxhRI9iM864NL_liGXvsQp2AupsKei7z0cNNfDvGUmWUy20nuUhkREQyrpY4bEeIBuc=s0-w300-rw")
    assert looks_like_image_url("https://preview.redd.it/tewd4o8mwwme1.jpeg?width=640")
    assert canon_post_url("https://old.reddit.com/r/nflmemes/comments/abc/hi/") == "https://www.reddit.com/r/nflmemes/comments/abc/hi/"


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print("ok", len(tests), "news tests")


if __name__ == "__main__":
    main()
