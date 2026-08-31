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
    rank_search_bar,
    rank_search_key,
    draft_check_js,
    strip_em,
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
    assert "Also on this board" in html
    assert "this desk" not in html
    assert strip_em("The Board \u2014 2026") == "The Board - 2026"
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
    assert "ca-pub-1074015774205047" in html
    assert "pagead2.googlesyndication.com" in html
    assert "adsbygoogle.js" in html
    from seo import ads_txt, ADSENSE_CLIENT
    assert ADSENSE_CLIENT == "ca-pub-1074015774205047"
    assert ads_txt().startswith("google.com, pub-1074015774205047, DIRECT,")


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


def test_rank_search_bar():
    html = rank_search_bar('<div class="filters" id="keep-pos"></div>')
    assert 'class="rank-bar"' in html
    assert 'class="rank-search-input"' in html
    assert 'type="search"' in html
    assert "Find a player" in html
    assert "applyRankFilter" in html
    assert "keep-pos" in html
    assert rank_search_key("Josh Allen", "QB", "BUF") == "josh allen qb buf"
    assert "&#x27;" in rank_search_key("Ja'Marr Chase")


def test_ppr_extra_boards():
    from ppr_boards import PPR_EXTRA_SOURCES, extra_ppr_maps
    spine = ["Ja'Marr Chase", "Jahmyr Gibbs", "Puka Nacua", "Bijan Robinson"]
    maps = extra_ppr_maps(spine)
    assert len(PPR_EXTRA_SOURCES) == 10
    assert len(maps) == 10
    for label, _url, _note in PPR_EXTRA_SOURCES:
        assert label in maps
        assert maps[label]


def test_draft_check_js():
    html = draft_check_js()
    assert "draft-check" in html
    assert "crossed-off" in html
    assert "localStorage" not in html
    assert "sessionStorage" not in html


def test_classic_draft_check_table():
    from build_site import rank_table
    rows = [{"name": "Jahmyr Gibbs", "pos": "RB", "team": "DET", "bk": 1}]
    on = rank_table(rows, draft_check=True)
    off = rank_table(rows)
    assert 'class="draft-check"' in on
    assert "Crossed off" in on
    assert "has-draft" in on
    assert 'aria-label="Cross off Jahmyr Gibbs"' in on
    assert 'class="draft-check"' not in off
    assert "has-draft" not in off


def test_pos_filter_chips():
    from build_site import pos_filter
    chips, js = pos_filter("board-pos")
    assert 'id="board-pos"' in chips
    assert 'data-pos="QB"' in chips
    assert 'data-pos="RB"' in chips
    assert "applyRankFilter" in js


def test_dst_and_kicker_boards():
    from special_teams import dst_board, kicker_board
    dst = dst_board()
    assert len(dst) == 32
    assert dst[0]["name"] == "Houston Texans"
    assert dst[0]["bk"] == 1
    assert dst[0]["n"] >= 5
    kickers = kicker_board()
    assert len(kickers) == 25
    assert kickers[0]["name"] == "Brandon Aubrey"
    assert kickers[0]["bk"] == 1


def test_bpl_slate():
    from bpl_schedule import CLUBS, bpl_games
    games = bpl_games()
    assert len(games) == 380
    assert len(CLUBS) == 20
    assert games[0]["home"] == "Arsenal"
    assert games[0]["score"] == "3-0"
    weeks = {g["week"] for g in games}
    assert weeks == set(range(1, 39))
    assert all(g["home_abbr"] in CLUBS and g["away_abbr"] in CLUBS for g in games)


def test_half_ppr_classic_tax():
    from build_site import score_from_ppr
    ppr = [
        {"name": "A", "pos": "RB", "avg": 10, "yates": 1, "fp": 1, "karabell": 1, "n": 3, "team": "BUF"},
        {"name": "B", "pos": "WR", "avg": 10, "yates": 2, "fp": 2, "karabell": 2, "n": 3, "team": "CIN"},
    ]
    classic = score_from_ppr(ppr, {"RB": -2.25, "WR": 1.5, "TE": 1.0, "QB": 0.25})
    assert classic[0]["name"] == "A"
    assert classic[0]["avg"] == 7.75
    assert classic[1]["avg"] == 11.5


def test_farm_top_100():
    from bb_prospects import FARM_SOURCES, load_farm
    farm = load_farm()
    assert len(farm) == 100
    assert len(FARM_SOURCES) == 5
    assert farm[0]["name"] == "Jesús Made"
    assert farm[0]["bk"] == 1
    assert all((r.get("mlb_g") or 0) <= 142 for r in farm)
    assert all(r.get("eta") for r in farm)
    assert all(r.get("path") for r in farm)
    assert all(r.get("ranks") for r in farm)
    keys = [r["key"] for r in farm]
    assert len(keys) == len(set(keys))


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} tests passed")
