#!/usr/bin/env python3
"""Smoke-test catalog search and trade math without Discord."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import Catalog, bk_value, compact, norm


def main():
    cat = Catalog()
    assert cat.raw["keep"][0]["name"] == "Josh Allen"
    assert bk_value(1) == 12000
    assert bk_value(40) == 5333
    assert bk_value(80) == 3469
    assert bk_value(28) == 6186
    assert "0.0085" in cat.raw.get("algorithm", "")
    assert "0.13" in cat.raw.get("algorithm", "")
    assert cat.raw["keep"][39]["value"] == bk_value(40)
    assert cat.raw["keep"][79]["value"] == bk_value(80)
    assert cat.one("jsn")["name"] == "Jaxon Smith-Njigba"
    assert cat.one("sun god")["name"].startswith("Amon-Ra")
    assert cat.one("cmc")["name"] == "Christian McCaffrey"
    assert cat.one("btj")["name"].startswith("Brian Thomas")
    assert cat.one("tlaw")["name"] == "Trevor Lawrence"
    allen = cat.resolve_asset("Josh Allen", "sf")
    assert allen["value"] == 12000
    qb1 = cat.resolve_asset("Josh Allen", "oneqb")
    assert qb1["value"] < allen["value"]
    assert qb1["value"] == bk_value(1, 0.38)
    t = cat.trade("sf", "Josh Allen", "Bijan Robinson")
    assert t["label"] in {"Fair Trade", "Side A Wins", "Side B Wins"}
    assert t["total_a"] == allen["value"]
    pick = cat.resolve_asset("2027 Mid 1st", "sf")
    assert pick and pick["kind"] == "pick"
    assert cat.resolve_asset("27 mid 1st", "sf")["name"] == "2027 Mid 1st"
    t2 = cat.trade("sf", "Josh Allen, 2027 Mid 1st", "Bijan, Ja'Marr Chase")
    assert not t2["missing"], t2["missing"]
    assert cat.youtube(cat.one("Josh Allen"))
    assert cat.pos_top("QB", "keep")[0]["pos"] == "QB"
    assert cat.team_players("bills", "keep")
    assert cat.nfl_abbr("pats") == "NE"
    assert cat.mlb_abbr("yankees") == "NYY"
    assert cat.mlb_games("yankees")
    assert cat.nfl_games("BUF", week=1)
    assert compact("2027 Mid 1st") == compact("27 mid 1st")
    assert norm("JSN") == "jaxon smith-njigba"
    hits = cat.find("chase", limit=3)
    assert hits and "Chase" in hits[0]["name"]
    jsn_deals = cat.deals_for("jsn")
    assert jsn_deals, "expected JSN on the desk tape"
    assert all(any("Smith-Njigba" in n or "Jaxon" in n for n in d["names"]) for d in jsn_deals)
    assert cat.deals_for("sun god") or cat.deals_for("st brown")
    assert len(cat.deals_for("")) >= 20
    assert len(cat.raw["keep"]) == 400
    assert cat.raw.get("board_format") == "redraft PPR", cat.raw.get("board_format")
    assert len(cat.raw["board"]) == 200, f"board {len(cat.raw.get('board') or [])}"
    assert cat.raw["board"][0]["name"] == cat.raw["ppr"][0]["name"]
    assert 400 <= len(cat.raw.get("sf_redraft") or []) <= 500, f"sf_redraft {len(cat.raw.get('sf_redraft') or [])}"
    bb = cat.raw.get("bb_keep") or []
    assert len(bb) == 400, f"bb keep {len(bb)}"
    assert cat.one("ohtani", sport="baseball")["name"] == "Shohei Ohtani"
    assert cat.one("caminero", sport="baseball")["name"] == "Junior Caminero"
    assert cat.one("pca", sport="baseball")["name"].startswith("Pete Crow")
    assert len(cat.raw.get("bb_pitchers") or []) == 150
    assert len(cat.raw.get("bb_saves") or []) == 100
    assert len(cat.raw.get("bb_svh") or []) == 100
    assert 350 <= len(cat.raw.get("bb_lineup") or []) <= 400
    assert len(cat.raw.get("bb_redraft") or []) == 400
    assert len(cat.raw.get("bb_waivers_dynasty") or []) == 15
    assert len(cat.raw.get("bb_waivers_redraft") or []) == 50
    assert cat.raw.get("news"), "expected football BK News in the catalog"
    tbb = cat.trade("bbkeep", "Shohei Ohtani", "Junior Caminero")
    assert tbb["label"] in {"Fair Trade", "Side A Wins", "Side B Wins"}
    assert tbb["total_a"] and tbb["total_b"]
    assert not tbb["missing"], tbb["missing"]
    root = Path(__file__).resolve().parents[1]
    ohtani_html = (root / "bb/players/shohei-ohtani.html").read_text()
    assert "Starcast" in ohtani_html
    assert "baseballsavant.mlb.com" in ohtani_html
    assert "spray" in ohtani_html.lower()
    assert "Pitch chart" in ohtani_html
    caminero_html = (root / "bb/players/junior-caminero.html").read_text()
    assert "Hits spray chart" in caminero_html
    skenes_html = (root / "bb/players/paul-skenes.html").read_text()
    assert "Pitch chart" in skenes_html
    pitch = cat.raw.get("pl_pitch") or []
    assert len(pitch) == 400, f"pitch {len(pitch)}"
    assert pitch[0]["name"] == "Erling Haaland"
    assert pitch[1]["name"] == "Bruno Fernandes"
    premier = cat.raw.get("pl_premier") or []
    assert len(premier) == 400, f"premier {len(premier)}"
    assert premier[0]["name"] == "Erling Haaland"
    assert premier[1]["name"] == "Bruno Fernandes"
    by_name = {r["name"]: r["bk"] for r in premier}
    assert by_name.get("Cole Palmer", 999) <= 25, by_name.get("Cole Palmer")
    assert by_name.get("Florian Wirtz", 999) <= 40, by_name.get("Florian Wirtz")
    assert by_name.get("Alexander Isak", 999) <= 50, by_name.get("Alexander Isak")
    assert by_name.get("Bukayo Saka", 999) <= 20, by_name.get("Bukayo Saka")
    assert len(cat.raw.get("pl_sources") or []) >= 25
    assert premier[0].get("age"), "Premier list needs ages"
    assert "Haaland" in (premier[0].get("full_name") or "")
    files = cat.raw.get("pl_players") or []
    haaland = next(p for p in files if p["name"] == "Erling Haaland")
    assert len(haaland.get("grafs") or []) >= 5, "premier files need five grafs"
    assert haaland.get("image"), "Haaland needs a photo"
    assert haaland.get("full_name")
    assert haaland.get("age")
    assert cat.raw["keep"][0].get("age"), "Football The Keep needs age"
    assert sum(1 for r in cat.raw["keep"] if r.get("age")) == 400, "Football The Keep needs age on every row"
    assert cat.raw["bb_keep"][0].get("age"), "Baseball The Keep needs age"
    assert sum(1 for r in cat.raw["bb_keep"] if r.get("age")) == 400
    assert cat.one("haaland", sport="soccer")["name"] == "Erling Haaland"
    assert cat.one("bruno", sport="soccer")["name"] == "Bruno Fernandes"
    assert cat.one("saka", sport="soccer")["name"] == "Bukayo Saka"
    assert cat.one("vvd", sport="soccer")["name"] == "Virgil van Dijk"
    assert cat.one("declan rice", sport="soccer")["name"] == "Declan Rice"
    assert cat.one("rice", sport="football")["name"] == "Rashee Rice"
    assert len(cat.raw.get("pl_fwd") or []) >= 40
    assert len(cat.raw.get("pl_mid") or []) == 150
    assert len(cat.raw.get("pl_def") or []) == 120
    assert len(cat.raw.get("pl_gkp") or []) >= 30
    assert 400 <= len(cat.raw.get("pl_players") or []) <= 420
    tpl = cat.trade("plpitch", "Bruno Fernandes", "Erling Haaland")
    assert tpl["label"] in {"Fair Trade", "Side A Wins", "Side B Wins"}
    tprem = cat.trade("plpremier", "Bruno Fernandes", "Erling Haaland")
    assert tprem["label"] in {"Fair Trade", "Side A Wins", "Side B Wins"}
    assert not tprem["missing"], tprem["missing"]
    assert tpl["total_a"] and tpl["total_b"]
    assert not tpl["missing"], tpl["missing"]
    assert len(cat.raw.get("sources") or []) >= 30, "The Keep Super Aggregate needs 30+ desks"
    keep0 = cat.raw["keep"][0]
    board0 = cat.raw["board"][0]
    assert (keep0.get("n") or 0) >= 10, keep0
    assert board0.get("yates") or board0.get("fp") or board0.get("karabell"), board0
    assert (board0.get("n") or 0) >= 10, board0
    classic = cat.raw.get("classic") or []
    assert len(classic) == 200, f"classic {len(classic)}"
    assert classic[0].get("bk") == 1
    assert keep0["name"] != board0["name"] or board0.get("yates") == 1
    farm = cat.raw.get("bb_farm") or []
    assert len(farm) == 100, f"bb farm {len(farm)}"
    assert farm[0]["name"] == "Jesús Made"
    assert all((r.get("mlb_g") or 0) <= 142 for r in farm)
    assert all(r.get("eta") for r in farm)
    assert all(r.get("path") for r in farm)
    assert cat.one("jesus made", sport="baseball")["name"] == "Jesús Made"
    bk = cat.raw.get("bk_keep") or []
    assert len(bk) == 400, f"bk keep {len(bk)}"
    assert bk[0]["name"] == "Victor Wembanyama"
    assert cat.one("wembanyama", sport="basketball")["name"] == "Victor Wembanyama"
    assert cat.one("luka", sport="basketball")["name"] == "Luka Doncic"
    assert cat.one("jokic", sport="basketball")["name"] == "Nikola Jokic"
    assert 200 <= len(cat.raw.get("bk_board") or []) <= 250
    assert len(cat.raw.get("bk_waivers_dynasty") or []) == 15
    assert len(cat.raw.get("bk_waivers_redraft") or []) == 50
    assert cat.raw["bk_keep"][0].get("age"), "BasketKeep The Keep needs age"
    tbk = cat.trade("bkkeep", "Victor Wembanyama", "Luka Doncic")
    assert tbk["label"] in {"Fair Trade", "Side A Wins", "Side B Wins"}
    assert tbk["total_a"] and tbk["total_b"]
    assert not tbk["missing"], tbk["missing"]
    wemby_html = (root / "bk/players/victor-wembanyama.html").read_text()
    assert "The Keep" in wemby_html
    print("ok", cat.updated, "players", len(cat.players), "keep", len(cat.raw["keep"]), "bb", len(bb), "bk", len(bk), "pitch", len(pitch))
    print("trade", t2["label"], t2["total_a"], "vs", t2["total_b"])
    print("norm jsn", norm("JSN"))
    print("picks", len(cat.raw["picks"]), "nfl", len(cat.raw["nfl"]), "mlb", len(cat.raw["mlb"]))

    root = Path(__file__).resolve().parents[1]

    def html_of(rel: str) -> str:
        p = root / rel
        assert p.exists(), f"missing {rel}"
        return p.read_text(encoding="utf-8")

    def page_title(html: str) -> str:
        return html.split("<title>", 1)[1].split("</title>", 1)[0]

    def meta_desc(html: str) -> str:
        return html.split('name="description" content="', 1)[1].split('"', 1)[0]

    keep_html = html_of("the-keep.html")
    keep_title = page_title(keep_html)
    assert "Superflex" in keep_title, keep_title
    assert 'property="og:title"' in keep_html
    assert "bar-chart" in keep_html
    generic = "Ball Keep dynasty and redraft rankings, trade calculators, schedules, and market notes."
    assert generic not in keep_html

    allen = html_of("players/josh-allen.html")
    allen_title = page_title(allen)
    assert "Rank #1" in allen_title, allen_title
    assert generic not in meta_desc(allen)
    assert "bar-chart" in allen
    assert "<h1>Josh Allen</h1>" in allen

    pitch_html = html_of("pl/the-pitch.html")
    pitch_title = page_title(pitch_html)
    assert "Sleeper" in pitch_title, pitch_title
    assert "bar-chart" in pitch_html
    assert "PitchKeep Premier League rankings. The Pitch top 400" not in pitch_html

    haaland = html_of("pl/players/erling-haaland.html")
    haaland_title = page_title(haaland)
    assert "Pitch" in haaland_title or "317" in haaland_title, haaland_title
    assert "bar-chart" in haaland
    assert "<h1>Erling Haaland</h1>" in haaland

    ohtani = html_of("bb/players/shohei-ohtani.html")
    assert "Rank #" in page_title(ohtani)
    assert "bar-chart" in ohtani

    home = html_of("index.html")
    assert "Superflex Dynasty" in home
    assert "Redraft PPR" in home
    assert "sports-top" in home
    assert "BasketKeep" in home
    assert "BaseKeep" in home
    assert "PitchKeep" in home
    assert "Ball Keep Football" not in home
    assert "FootKeep" not in home
    assert "BaseBallKeep" not in home
    assert 'class="desk-block extra"' in home
    assert "home-intro" in home
    assert "The Keep is Superflex Dynasty. The Board is Redraft PPR." in home
    assert "Dynasty · Redraft" in home
    assert "Superflex Dynasty · Superflex Redraft" not in home
    assert "Kids pay a tax" not in home
    assert "kids pay a tax" not in home
    assert "Redraft Superflex" in home
    assert 'href="redraft-superflex.html"' in home
    assert "hero-lead" not in home
    assert '<section class="hero' in home
    assert 'class="hero masthead"' in home
    assert "Football rankings" in home
    assert "Football desk" not in home
    assert "mast-art" in home
    assert "mast-ballkeep.jpg" in home
    assert 'class="mast-mark"' in home
    assert "background-image:url" not in home
    assert "home-leads" in home
    lists_at = home.find('class="desk-block lists"')
    tools_at = home.find('class="desk-block tools"')
    extra_at = home.find('class="desk-block extra"')
    assert 0 < lists_at < tools_at < extra_at
    assert 'href="trade.html"' in home[tools_at:extra_at]
    assert "Player Pages" in home[tools_at:extra_at]
    assert "Trade Calculators" not in home[home.find("home-intro"):lists_at]
    assert "this desk" not in home
    assert "\u2014" not in home
    assert "On this board" in home
    assert "32 boards mashed" in home
    hc = html_of("hot-n-cold.html")
    assert "this desk" not in hc
    assert "\u2014" not in hc
    assert 'class="hc-cold"' in hc
    assert 'class="tile cold"' in hc or "tile cold" in hc
    assert 'href="privacy.html"' in home
    for x_path in ("the-x.html", "bb/the-x.html", "bk/the-x.html", "pl/the-x.html"):
        x_html = html_of(x_path)
        assert "x-card" in x_html, x_path
        assert "x-tape" in x_html, x_path
        assert "No pictures on the tape yet" not in x_html
        assert x_html.count("x-card") >= 20, x_path
    privacy = html_of("privacy.html")
    assert "Privacy Policy" in page_title(privacy)
    assert "Google AdSense" in privacy
    assert "adssettings.google.com" in privacy
    assert "policies.google.com/technologies/partner-sites" in privacy
    assert "BaseKeep" in privacy
    assert "BasketKeep" in privacy
    assert "PitchKeep" in privacy
    assert "Kids pay a tax" not in privacy
    assert "the-ones.html" not in home
    assert "The Ones" not in home
    assert 'href="discord.html"' not in home
    assert "Big draw" not in home
    css = Path("css/site.css").read_text()
    assert "a.sport-switch.bk" in css
    assert "background: #1a1208" in css
    assert "color: #f4a259" in css
    assert "border: 3px solid #e87722" in css
    assert "background: #0b1f3a" in css
    assert "background: #37003c" in css
    assert "background: #d6ebf7" in css
    assert "box-shadow:0 0 0 3px #c8102e" not in home
    assert "style=\"color:#1788c2\"" in home
    assert "font-size: 40px" in css
    assert ".home-intro" in css
    assert "--powder-ink" in css
    assert ".tile.cold h3" in css
    assert "height: 120px" in css
    assert "grid-template-columns: 72px minmax(0, 1fr) 200px" in css
    assert "object-fit: contain" in css
    assert ".hero.masthead .mast-art { display: none; }" in css
    for sport_css in ("css/bb.css", "css/bk.css", "css/pl.css"):
        sport = Path(sport_css).read_text()
        assert "height: 120px" in sport, sport_css
        assert "grid-template-columns: 72px minmax(0, 1fr) 200px" in sport, sport_css
        assert "object-fit: contain" in sport, sport_css
        assert "max-width: 34%" not in sport, sport_css
        assert ".hero.masthead .mast-art { display: none; }" in sport, sport_css
    board_html = html_of("board.html")
    assert "2026 Redraft · PPR" in board_html
    assert "<h1>The Board</h1>" in board_html
    assert "redraft ppr" in board_html.lower()
    assert "13 boards" in board_html
    assert "Derek Brown" in board_html
    assert "4for4" in board_html
    classic_html = html_of("the-classic.html")
    assert "<h1>The Classic</h1>" in classic_html
    assert "0.5 PPR" in classic_html or "Half-PPR" in classic_html
    assert "the-classic.html" in html_of("index.html")
    assert "Kids pay a tax" not in board_html
    assert "kids pay a tax" not in board_html
    assert "The tax is" not in board_html
    sf_html = html_of("redraft-superflex.html")
    assert "<h1>Redraft Superflex</h1>" in sf_html
    assert "Superflex Redraft" in sf_html
    assert "Kids pay a tax" not in sf_html
    stub = html_of("redraft-ppr.html")
    assert "board.html" in stub
    assert "The Board" in stub
    bb_home = html_of("bb/index.html")
    assert "BallKeep" in bb_home
    assert "FootKeep" not in bb_home
    assert "BaseKeep" in page_title(bb_home) or "BASE" in bb_home
    assert "BaseBallKeep" not in bb_home
    assert "The Diamond" in bb_home
    assert "Redraft ranking" in bb_home
    assert "the-diamond.html" in bb_home
    assert "The Farm" in bb_home
    assert "the-farm.html" in bb_home
    assert 'href="../privacy.html"' in bb_home
    assert 'class="hero masthead"' in bb_home
    assert "Baseball rankings" in bb_home
    assert "Baseball desk" not in bb_home
    assert 'class="mast-mark"' in bb_home
    assert "mast-art" in bb_home
    assert "mast-ballkeep.jpg" in bb_home
    assert "background-image:url" not in bb_home
    lineup = html_of("bb/the-lineup.html")
    assert "page-label" in lineup
    assert "bb-lineup.jpg" not in lineup
    assert "bb-pitch.jpg" not in html_of("bb/pitchers.html")
    assert "bb-bullpen.jpg" not in html_of("bb/bullpen.html")
    diamond = html_of("bb/the-diamond.html")
    assert "The Diamond" in page_title(diamond) or "<h1>The Diamond</h1>" in diamond
    assert "Redraft ranking" in diamond
    farm_html = html_of("bb/the-farm.html")
    assert "<h1>The Farm</h1>" in farm_html
    assert "Arrival" in farm_html
    assert "path to playtime" in farm_html.lower()
    assert "Jesús Made" in farm_html or "Jesus Made" in farm_html
    assert "142" in farm_html
    assert "MLB Pipeline" in farm_html
    assert farm_html.count('class="face"') >= 80
    made = html_of("bb/players/jesus-made.html")
    assert "Arrival" in made
    assert "The Farm" in made
    assert "waivers-dynasty.html" not in bb_home
    assert "waivers-redraft.html" not in bb_home
    assert "Dynasty Wire" not in bb_home
    assert "Redraft Wire" not in bb_home
    bk_home = html_of("bk/index.html")
    assert "BasketKeep" in page_title(bk_home) or "BASKET" in bk_home
    assert "BallKeep" in bk_home
    assert "FootKeep" not in bk_home
    assert "the-keep.html" in bk_home
    assert "board.html" in bk_home
    assert 'href="../privacy.html"' in bk_home
    assert 'class="hero masthead"' in bk_home
    assert "Basketball rankings" in bk_home
    assert "Basketball desk" not in bk_home
    assert "mast-art" in bk_home
    assert "mast-ballkeep.jpg" in bk_home
    assert "background-image:url" not in bk_home
    assert "hero-lead" not in bk_home
    pl_home = html_of("pl/index.html")
    assert 'href="../privacy.html"' in pl_home
    assert 'class="hero masthead"' in pl_home
    assert "Premier League rankings" in pl_home
    assert "Premier League desk" not in pl_home
    assert "mast-art" in pl_home
    assert "mast-ballkeep.jpg" in pl_home
    assert "background-image:url" not in pl_home
    bk_keep = html_of("bk/the-keep.html")
    assert "Victor Wembanyama" in bk_keep
    assert "bar-chart" in bk_keep
    wemby = html_of("bk/players/victor-wembanyama.html")
    assert "The minus is the price" not in wemby
    assert "Someone in your room already knows the rank" not in wemby
    assert "blocks" in wemby.lower()
    embiid = html_of("bk/players/joel-embiid.html")
    assert "The minus is the price" not in embiid
    assert "On The Keep. That is already a rostered name" not in embiid
    assert not (root / "the-ones.html").exists()
    assert 'href="discord.html"' not in html_of("the-keep.html")

    rank_pages = (
        "the-keep.html",
        "board.html",
        "redraft-standard.html",
        "the-classic.html",
        "redraft-superflex.html",
        "rookies-2026.html",
        "bk/the-keep.html",
        "bk/board.html",
        "bk/guards.html",
        "bk/wings.html",
        "bk/bigs.html",
        "bb/the-keep.html",
        "bb/the-lineup.html",
        "bb/pitchers.html",
        "bb/bullpen.html",
        "bb/bullpen-holds.html",
        "bb/the-diamond.html",
        "bb/the-farm.html",
        "pl/the-premier.html",
        "pl/the-pitch.html",
        "pl/attack.html",
        "pl/midfield.html",
        "pl/defence.html",
        "pl/keepers.html",
    )
    for rel in rank_pages:
        page = html_of(rel)
        assert 'class="rank-search-input"' in page, rel
        assert "applyRankFilter" in page, rel
        assert "data-name=" in page, rel
        assert "Find a player" in page, rel
    assert "rank-search-input" not in html_of("index.html")
    assert "rank-search-input" not in html_of("news.html")
    assert "rank-search-input" not in html_of("the-x.html")
    assert ".rank-search" in Path("css/site.css").read_text()
    assert ".rank-search" in Path("css/bk.css").read_text()
    assert ".rank-search" in Path("css/bb.css").read_text()
    assert ".rank-search" in Path("css/pl.css").read_text()
    keep_html = html_of("the-keep.html")
    assert 'id="keep-pos"' in keep_html
    assert 'data-name="josh allen' in keep_html
    assert "rank-search-input" in keep_html
    assert keep_html.find("rank-search-input") < keep_html.find("keep-pos")
    for rel, box in (
        ("board.html", "board-pos"),
        ("the-classic.html", "classic-pos"),
        ("redraft-standard.html", "std-pos"),
        ("redraft-superflex.html", "sf-pos"),
    ):
        page = html_of(rel)
        assert f'id="{box}"' in page, rel
        assert 'data-pos="RB"' in page, rel
        assert 'data-pos="WR"' in page, rel
        assert page.find("rank-search-input") < page.find(box)


if __name__ == "__main__":
    main()
