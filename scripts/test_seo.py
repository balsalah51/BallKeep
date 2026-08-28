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
    faq_html,
    faq_jsonld,
    footer_nav,
    head_tags,
    item_list_jsonld,
    news_sitemap_xml,
    related_players_html,
    related_stories_html,
    robots_txt,
    rss_xml,
    sitemap_xml,
    video_jsonld,
    website_jsonld,
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
    obj = article_jsonld("Chase injured", "https://ballkeep.com/news/x.html", "Summary here", published="2026-08-26", section="Injury")
    assert obj["@type"] == "NewsArticle"
    assert obj["datePublished"] == "2026-08-26"
    assert obj["inLanguage"] == "en-US"
    assert obj["isAccessibleForFree"] is True
    assert obj["articleSection"] == "Injury"
    assert obj["publisher"]["logo"]["url"] == "https://ballkeep.com/img/logo.jpg"


def test_google_head_tags():
    html = head_tags(
        title="The Keep",
        description="Superflex dynasty top 400.",
        canonical="https://ballkeep.com/the-keep.html",
        image="img/logo.jpg",
        brand="Ball Keep",
    )
    assert "max-image-preview:large" in html
    assert 'name="googlebot"' in html
    assert 'property="og:locale"' in html
    assert "fonts.googleapis.com" in html
    assert "application/rss+xml" in html
    assert "https://ballkeep.com/feed.xml" in html
    assert "img/logo.jpg" in html


def test_item_list_faq_video():
    ld = item_list_jsonld("The Keep", "https://ballkeep.com/the-keep.html", [
        ("Josh Allen", "https://ballkeep.com/players/josh-allen.html"),
        ("Drake Maye", "https://ballkeep.com/players/drake-maye.html"),
        ("Bijan Robinson", "https://ballkeep.com/players/bijan-robinson.html"),
    ])
    assert ld["@type"] == "ItemList"
    assert ld["numberOfItems"] == 3
    faq = faq_jsonld([("What is BK Value?", "Rank 1 is 12,000."), ("What is fair?", "Within 8%.")])
    assert faq["@type"] == "FAQPage"
    html = faq_html([("What is BK Value?", "Rank 1 is 12,000.")])
    assert "<details>" in html
    vid = video_jsonld("Josh Allen highlights", "2kwY6ve5E88")
    assert vid["@type"] == "VideoObject"
    assert "2kwY6ve5E88" in vid["embedUrl"]


def test_news_sitemap_rss_robots():
    xml = news_sitemap_xml([{
        "loc": "https://ballkeep.com/news/chase.html",
        "title": "Chase injured",
        "date": "2026-08-26T13:21:21Z",
        "publication": "Ball Keep",
    }])
    assert "xmlns:news=" in xml
    assert "Chase injured" in xml
    rss = rss_xml(
        title="BK News",
        link="https://ballkeep.com/news.html",
        description="Hourly wire",
        items=[{"title": "Chase", "link": "https://ballkeep.com/news/chase.html", "description": "Knee", "date": "2026-08-26T13:21:21Z"}],
        self_url="https://ballkeep.com/feed.xml",
    )
    assert "<rss version=" in rss
    assert "Chase" in rss
    bots = robots_txt(["https://ballkeep.com/sitemap.xml", "https://ballkeep.com/sitemap-news.xml"])
    assert "Googlebot" in bots
    assert "sitemap-news.xml" in bots


def test_sitemap_images_and_website():
    xml = sitemap_xml([
        "https://ballkeep.com/",
        {"loc": "https://ballkeep.com/players/josh-allen.html", "image": "https://ballkeep.com/img/players/josh-allen.png", "image_title": "Josh Allen"},
    ], "2026-08-27")
    assert "xmlns:image=" in xml
    assert "josh-allen.png" in xml
    site = website_jsonld("Ball Keep")
    assert site["@type"] == "WebSite"
    assert site["url"] == "https://ballkeep.com"


def test_clip():
    assert len(clip("word " * 80, 168)) <= 168


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} tests passed")
