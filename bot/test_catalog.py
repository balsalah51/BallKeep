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
    assert len(cat.raw["board"]) == 500, f"board {len(cat.raw.get('board') or [])}"
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
    assert premier[2]["name"] == "Antoine Semenyo"
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
    assert (board0.get("n") or 0) <= 4, board0
    print("ok", cat.updated, "players", len(cat.players), "keep", len(cat.raw["keep"]), "bb", len(bb), "pitch", len(pitch))
    print("trade", t2["label"], t2["total_a"], "vs", t2["total_b"])
    print("norm jsn", norm("JSN"))
    print("picks", len(cat.raw["picks"]), "nfl", len(cat.raw["nfl"]), "mlb", len(cat.raw["mlb"]))


if __name__ == "__main__":
    main()
