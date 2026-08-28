#!/usr/bin/env python3
"""SEO helper checks — related links, breadcrumbs, titles, sitemap."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo import (  # noqa: E402
    also_on_desk,
    article_jsonld,
    breadcrumb_jsonld,
    breadcrumbs,
    branded,
    clip,
    face_alt,
    footer_nav,
    related_players_html,
    related_stories_html,
    sitemap_xml,
)


def test_branded_titles():
    assert branded("The Keep", "Ball Keep") == "The Keep | Ball Keep"
    assert branded("Home", "Ball Keep") != "Home"
    assert "Untitled" not in branded("The Keep 2026 Superflex Dynasty Rankings (Top 400)", "Ball Keep")


def test_face_alt():
    assert face_alt("Zay Flowers") == "Zay Flowers headshot"
    assert face_alt("") == "Player headshot"


def test_related_players():
    rows = [
        {"key": "a", "name": "A", "pos": "WR", "team": "BAL", "bk": 1},
        {"key": "b", "name": "B", "pos": "RB", "team": "KC", "bk": 2},
        {"key": "c", "name": "C", "pos": "TE", "team": "SF", "bk": 3},
        {"key": "d", "name": "D", "pos": "WR", "team": "CIN", "bk": 4},
        {"key": "e", "name": "E", "pos": "QB", "team": "BAL", "bk": 40},
    ]
    html = related_players_html(rows, rows[0], lambda r: f"{r['key']}.html")
    assert "related-players" in html
    assert "b.html" in html
    assert "Same club" in html
    assert "e.html" in html
    assert "Same position" in html
    assert "d.html" in html
    assert "a.html" not in html


def test_related_stories():
    stories = [
        {"slug": "one", "headline": "Chase injury", "category": "injury", "players": [{"key": "chase"}], "updated": "2026-08-26"},
        {"slug": "two", "headline": "Chase practice", "category": "practice", "players": [{"key": "chase"}], "updated": "2026-08-27"},
        {"slug": "three", "headline": "Unrelated", "category": "wire", "players": [{"key": "other"}], "updated": "2026-08-25"},
    ]
    html = related_stories_html(stories, stories[0], lambda s: f"{s['slug']}.html")
    assert "two.html" in html
    assert "one.html" not in html
    assert "Chase practice" in html


def test_breadcrumbs_and_footer():
    html = breadcrumbs([("Ball Keep", "index.html"), ("Players", "players/index.html"), ("Zay Flowers", None)])
    assert "crumbs" in html
    assert 'href="index.html"' in html
    assert "Zay Flowers" in html
    ld = breadcrumb_jsonld([
        ("Ball Keep", "https://ballkeep.com/"),
        ("Players", "https://ballkeep.com/players/"),
    ])
    assert ld["@type"] == "BreadcrumbList"
    nav = footer_nav([("index.html", "Home"), ("the-keep.html", "The Keep")], "index.html")
    assert "The Keep" in nav
    assert "Home" not in nav


def test_also_on_desk_and_sitemap():
    html = also_on_desk([("board.html", "The Board", "Redraft PPR.")])
    assert "board.html" in html
    xml = sitemap_xml(["https://ballkeep.com/", "https://ballkeep.com/the-keep.html"], "2026-08-27")
    assert "<lastmod>2026-08-27</lastmod>" in xml
    assert xml.count("<url>") == 2


def test_article_schema():
    obj = article_jsonld("Chase injured", "https://ballkeep.com/news/x.html", "Summary here", published="2026-08-26")
    assert obj["@type"] == "NewsArticle"
    assert obj["datePublished"] == "2026-08-26"


def test_clip():
    assert len(clip("word " * 80, 168)) <= 168


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} tests passed")
