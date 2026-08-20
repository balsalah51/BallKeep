#!/usr/bin/env python3
"""SEO helper tests. No network, no full site rebuild."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo import (  # noqa: E402
    abs_asset,
    canonical,
    clip_desc,
    head_tags,
    json_ld_tag,
    news_ld,
    page_meta,
    person_ld,
    player_description,
    share_bar,
    sitemap_url,
    website_ld,
)


def test_canonical_home():
    assert canonical("index.html") == "https://ballkeep.com/"
    assert canonical("index.html", "bb") == "https://ballkeep.com/bb/"
    assert canonical("index.html", "pl") == "https://ballkeep.com/pl/"


def test_canonical_nested():
    assert canonical("players/josh-allen.html") == "https://ballkeep.com/players/josh-allen.html"
    assert canonical("players/shohei-ohtani.html", "bb") == "https://ballkeep.com/bb/players/shohei-ohtani.html"
    assert canonical("the-pitch.html", "pl") == "https://ballkeep.com/pl/the-pitch.html"


def test_home_title_is_not_home():
    title, desc = page_meta("index.html", "fb", "Home")
    assert "Home" not in title
    assert "Dynasty" in title
    assert "trade" in desc.lower() or "Trade" in desc


def test_player_title():
    title, _ = page_meta("players/josh-allen.html", "fb", "Josh Allen")
    assert title.startswith("Josh Allen")
    assert "Dynasty" in title
    assert "Ball Keep" in title


def test_player_description():
    d = player_description("Josh Allen", "QB", "BUF", 1, "football")
    assert "Josh Allen" in d
    assert "#1" in d
    assert "Ball Keep" in d


def test_head_has_og_and_canonical():
    html = head_tags(
        desk="fb",
        path="the-keep.html",
        fallback_title="The Keep",
        css_href="css/site.css",
        icon_href="img/logo.jpg",
    )
    assert 'rel="canonical" href="https://ballkeep.com/the-keep.html"' in html
    assert 'property="og:title"' in html
    assert 'name="twitter:card"' in html
    assert "Superflex Dynasty Top 400" in html
    assert html.count("<title>") == 1


def test_news_head_uses_blurb():
    html = head_tags(
        desk="fb",
        path="news/tyler-warren.html",
        fallback_title="Colts TE Tyler Warren injures groin",
        css_href="../css/site.css",
        icon_href="../img/logo.jpg",
        description="Warren joins Alec Pierce as two important Colts dealing with injuries.",
        og_type="article",
        published="2026-08-20T15:10:00Z",
        json_ld=news_ld(
            "Colts TE Tyler Warren injures groin",
            "https://ballkeep.com/news/tyler-warren.html",
            "Warren joins Alec Pierce.",
            "2026-08-20T15:10:00Z",
        ),
    )
    assert "Warren joins Alec Pierce" in html
    assert 'property="og:type" content="article"' in html
    assert "NewsArticle" in html
    assert "article:published_time" in html


def test_share_bar_encodes():
    bar = share_bar("https://ballkeep.com/the-keep.html", "The Keep — Superflex")
    assert "reddit.com/submit" in bar
    assert "x.com/intent/tweet" in bar
    assert "share-copy" in bar


def test_abs_asset_strips_dots():
    assert abs_asset("../img/players/josh-allen.png") == "https://ballkeep.com/img/players/josh-allen.png"


def test_clip_desc():
    assert clip_desc("short") == "short"
    long = "word " * 80
    out = clip_desc(long, 40)
    assert len(out) <= 40
    assert out.endswith("…")


def test_json_ld_escapes_script():
    tag = json_ld_tag({"name": "</script>"})
    assert "</script>" not in tag.replace("</script>", "", 1) or "\\u003c" in tag
    assert "\\u003c" in tag


def test_website_ld_and_person():
    site = website_ld("fb")
    assert site["@type"] == "WebSite"
    person = person_ld("Josh Allen", "https://ballkeep.com/players/josh-allen.html", "https://ballkeep.com/img/logo.jpg")
    assert person["@type"] == "Person"


def test_sitemap_url():
    row = sitemap_url("https://ballkeep.com/", lastmod="2026-08-20", priority="1.0")
    assert "<loc>https://ballkeep.com/</loc>" in row
    assert "<lastmod>2026-08-20</lastmod>" in row
    assert "<priority>1.0</priority>" in row


def test_empty_tracking_omitted():
    html = head_tags(
        desk="bb",
        path="index.html",
        fallback_title="Home",
        css_href="../css/bb.css",
        icon_href="../img/bb-logo.jpg",
    )
    assert "googletagmanager" not in html
    assert "adsbygoogle" not in html
    assert "BaseBallKeep" in html
    assert 'rel="canonical" href="https://ballkeep.com/bb/"' in html


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} tests")
