#!/usr/bin/env python3
"""SEO helpers: related news, crumbs, sitemap, story cards."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo import (  # noqa: E402
    nearby_window,
    path_crumbs,
    related_names,
    related_news,
    same_field,
    sitemap_xml,
    story_card,
)


def test_related_news_prefers_shared_players():
    stories = [
        {"slug": "a", "category": "injury", "players": [{"key": "jamarr chase"}], "headline": "A"},
        {"slug": "b", "category": "roster", "players": [{"key": "jamarr chase"}], "headline": "B"},
        {"slug": "c", "category": "injury", "players": [{"key": "other"}], "headline": "C"},
        {"slug": "d", "category": "wire", "players": [], "headline": "D"},
    ]
    current = stories[0]
    related = related_news(stories, current, n=3)
    slugs = [s["slug"] for s in related]
    assert slugs[0] == "b", slugs
    assert "a" not in slugs
    assert "c" in slugs


def test_nearby_and_same_field():
    rows = [
        {"key": "a", "team": "BAL", "pos": "WR", "name": "A"},
        {"key": "b", "team": "BAL", "pos": "RB", "name": "B"},
        {"key": "c", "team": "CIN", "pos": "WR", "name": "C"},
        {"key": "d", "team": "BAL", "pos": "WR", "name": "D"},
    ]
    mates = same_field(rows, rows[0], "team", limit=4)
    assert [r["key"] for r in mates] == ["b", "d"]
    pos = same_field(rows, rows[0], "pos", limit=4)
    assert [r["key"] for r in pos] == ["c", "d"]
    assert [r["key"] for r in nearby_window(rows, 1, 1)] == ["a", "c"]


def test_crumbs_skip_home():
    assert path_crumbs("index.html", "Home", home_href="index.html", players_href="players/index.html", news_href="news.html") == []
    player = path_crumbs(
        "players/zay-flowers.html",
        "Zay Flowers Superflex Dynasty Rank #50 (WR BAL)",
        home_href="../index.html",
        players_href="index.html",
        news_href="../news.html",
    )
    assert player[0] == ("../index.html", "Home")
    assert player[1] == ("index.html", "Players")
    assert player[-1][0] == ""


def test_related_names_and_story_card():
    html = related_names("Same team", [("zay-flowers.html", "Zay Flowers", "#50")])
    assert 'href="zay-flowers.html"' in html
    assert "Zay Flowers" in html
    card = story_card(
        href="news/foo.html",
        category="injury",
        label="Injury",
        when="Aug 26",
        headline="Update",
        blurb="Blurb",
        player_html='<a class="chip" href="players/a.html">A</a>',
        nsrc=2,
        kinds={"x"},
    )
    assert "<article" in card
    assert 'href="news/foo.html"' in card
    assert 'href="players/a.html"' in card
    assert card.count("<a ") >= 2


def test_sitemap_has_lastmod():
    xml = sitemap_xml(["https://ballkeep.com/", "https://ballkeep.com/the-keep.html"], lastmod="2026-08-27")
    assert "<lastmod>2026-08-27</lastmod>" in xml
    assert "<priority>1.0</priority>" in xml


if __name__ == "__main__":
    test_related_news_prefers_shared_players()
    test_nearby_and_same_field()
    test_crumbs_skip_home()
    test_related_names_and_story_card()
    test_sitemap_has_lastmod()
    print("ok")
