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
    print("ok", cat.updated, "players", len(cat.players), "keep", len(cat.raw["keep"]))
    print("trade", t2["label"], t2["total_a"], "vs", t2["total_b"])
    print("norm jsn", norm("JSN"))
    print("picks", len(cat.raw["picks"]), "nfl", len(cat.raw["nfl"]), "mlb", len(cat.raw["mlb"]))


if __name__ == "__main__":
    main()
