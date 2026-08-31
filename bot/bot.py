#!/usr/bin/env python3
"""Ball Keep Discord desk — rankings, calculator, tape, and a full server publish."""
from __future__ import annotations

import os
import random
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_a, **_k):
        return False

import discord
from discord import app_commands
from discord.ext import commands

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import FORMULA, Catalog, bk_value, load, norm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")

BLUE = 0x1E8FC2
RED = 0xC8102E
GREEN = 0x157A3A
INK = 0x102033
NAVY = 0x0B1F3A
PURPLE = 0x37003C

QUIPS = [
    "Keep the guys who still matter in 2029.",
    "Powder-blue desk. Red ink. No fluff.",
    "If it is not on The Keep, tell us why you still own it.",
    "Superflex makes quarterbacks expensive. That is the point.",
    "A late first is not a 1.01 in a hoodie.",
    "Tape first. ADP later.",
    "Dynasty is a roster you keep. Redraft is a contest you survive.",
    "Fair is within 8%. Feeling is not a unit of value.",
    "Nicknames work. JSN, CMC, Sun God, BTJ, TLaw. You're welcome.",
    "The Keep is a 10-board average. One tweet is not a board.",
    "Publish the desk once. Search Discord forever.",
    "BaseBallKeep is the other door. Navy, cream, 23 boards.",
    "Saves and SV+H are different sports. Use the right bullpen page.",
    "PitchKeep: The Premier, The Pitch, the lists, the files.",
    "Haaland scores. Bruno creates. Sleeper pays both. The rest of the 400 is who you own.",
]


def site_img(path: str) -> str | None:
    if not path:
        return None
    if path.startswith("http"):
        return path
    return "https://ballkeep.com/" + path.lstrip("/")


def fmt(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return "—"


class Desk:
    def __init__(self):
        self.cat = load()

    def reload(self):
        self.cat = Catalog()
        return self.cat.updated


desk = Desk()


def player_embed(discord, p: dict):
    lists = p.get("lists") or {}
    baseball = p.get("sport") == "baseball" or "BB Keep" in lists
    soccer = p.get("sport") == "soccer" or "The Pitch" in lists or "The Premier" in lists
    if soccer:
        keep = lists.get("The Pitch") or p.get("bk")
    elif baseball:
        keep = lists.get("BB Keep")
    else:
        keep = lists.get("The Keep") or p.get("bk")
    value = p.get("value") or (bk_value(keep) if keep else None)
    if soccer:
        color = PURPLE
    elif baseball:
        color = NAVY
    else:
        color = {"QB": RED, "RB": GREEN, "WR": BLUE, "TE": 0xC9A227, "PICK": 0x888888}.get(p.get("pos"), INK)
    bits = [x for x in (p.get("pos") or "", p.get("team") or "", f"age {p['age']}" if p.get("age") else "", p.get("college") or "") if x]
    title = f"{p.get('name')} · {' · '.join(bits)}"
    desc = (p.get("grafs") or [random.choice(QUIPS)])[0][:400]
    emb = discord.Embed(title=title, description=desc, color=color, url=p.get("url") or "https://ballkeep.com")
    if soccer and keep:
        price = f" · £{p['price']}m" if p.get("price") else ""
        prem = lists.get("The Premier")
        label = "The Premier" if prem else "The Pitch"
        shown = prem or keep
        emb.add_field(name=label, value=f"#{shown} · avg {p.get('keep_avg') or p.get('avg') or '—'} · {fmt(value)} BK{price}", inline=True)
        if prem and keep and prem != keep:
            emb.add_field(name="The Pitch", value=f"#{keep}", inline=True)
    elif baseball and keep:
        emb.add_field(name="BB Keep", value=f"#{keep} · avg {p.get('keep_avg') or p.get('avg') or '—'} · {fmt(value)} BK", inline=True)
    elif keep:
        emb.add_field(name="The Keep", value=f"#{keep} · avg {p.get('keep_avg') or p.get('avg') or '—'} · {fmt(value)} BK", inline=True)
    if lists.get("The Lineup"):
        emb.add_field(name="The Lineup", value=f"#{lists['The Lineup']}", inline=True)
    if lists.get("BK Pitchers"):
        emb.add_field(name="Pitchers", value=f"#{lists['BK Pitchers']}", inline=True)
    if lists.get("BB Redraft"):
        emb.add_field(name="BB Redraft", value=f"#{lists['BB Redraft']}", inline=True)
    if lists.get("Attack"):
        emb.add_field(name="Attack", value=f"#{lists['Attack']}", inline=True)
    if lists.get("Midfield"):
        emb.add_field(name="Midfield", value=f"#{lists['Midfield']}", inline=True)
    if lists.get("Defence"):
        emb.add_field(name="Defence", value=f"#{lists['Defence']}", inline=True)
    if lists.get("Keepers"):
        emb.add_field(name="Keepers", value=f"#{lists['Keepers']}", inline=True)
    if lists.get("The Board") or (p.get("bk") and not keep and not baseball and not soccer):
        board_rk = lists.get("The Board") or p.get("bk")
        emb.add_field(name="The Board", value=f"#{board_rk}", inline=True)
    if lists.get("Redraft PPR"):
        emb.add_field(name="PPR", value=f"#{lists['Redraft PPR']}", inline=True)
    if lists.get("Redraft Standard"):
        emb.add_field(name="Standard", value=f"#{lists['Redraft Standard']}", inline=True)
    if lists.get("2026 Rookies"):
        emb.add_field(name="Rookies", value=f"#{lists['2026 Rookies']}", inline=True)
    if lists.get("Hot"):
        emb.add_field(name="🔥 Hot", value=f"Buy #{lists['Hot']}", inline=True)
    if lists.get("Cold"):
        emb.add_field(name="❄️ Cold", value=f"Sell #{lists['Cold']}", inline=True)
    hit = p.get("hit") or {}
    pit = p.get("pit") or {}
    if hit.get("g"):
        emb.add_field(
            name="2026 bat",
            value=f"{hit.get('avg') or '—'} / {hit.get('hr') or 0} HR / {hit.get('sb') or 0} SB / {hit.get('ops') or '—'} OPS · {hit.get('g')} G",
            inline=False,
        )
    if pit.get("ip") or pit.get("g"):
        emb.add_field(
            name="2026 arm",
            value=f"{pit.get('era') or '—'} ERA · {pit.get('whip') or '—'} WHIP · {pit.get('so') or 0} K in {pit.get('ip') or '—'} IP",
            inline=False,
        )
    if soccer and (p.get("pts") or p.get("gls") is not None):
        bits_pl = []
        if p.get("pts") not in (None, ""):
            bits_pl.append(f"{p['pts']} pts")
        if p.get("gls") not in (None, ""):
            bits_pl.append(f"{p['gls']} G")
        if p.get("ast") not in (None, ""):
            bits_pl.append(f"{p['ast']} A")
        if bits_pl:
            emb.add_field(name="2025/26 FPL", value=" · ".join(str(x) for x in bits_pl), inline=False)
    bits_bio = []
    if p.get("bats") or p.get("throws"):
        bits_bio.append(f"B/T {p.get('bats') or '—'}{p.get('throws') or ''}")
    if p.get("height"):
        bits_bio.append(str(p["height"]) + (f" / {p['weight']} lbs" if p.get("weight") else ""))
    if p.get("debut"):
        bits_bio.append(f"debut {str(p['debut'])[:4]}")
    if p.get("birth_city") or p.get("birth_country"):
        bits_bio.append(", ".join(x for x in (p.get("birth_city"), p.get("birth_country")) if x))
    if bits_bio:
        emb.add_field(name="File", value=" · ".join(bits_bio)[:1024], inline=False)
    plus = p.get("plus") or []
    minus = p.get("minus") or []
    if plus:
        emb.add_field(name="Plus", value="\n".join(f"• {x}" for x in plus[:4])[:1024], inline=False)
    if minus:
        emb.add_field(name="Minus", value="\n".join(f"• {x}" for x in minus[:4])[:1024], inline=False)
    ranks = p.get("ranks") or {}
    if ranks:
        bits_r = " · ".join(f"{s} {v}" for s, v in sorted(ranks.items(), key=lambda kv: kv[1])[:8])
        emb.add_field(name="Boards", value=bits_r[:1024], inline=False)
    notes = p.get("notes") or []
    if notes:
        emb.add_field(name="Desk notes", value=" · ".join(str(n) for n in notes[:4])[:1024], inline=False)
    thumb = site_img(p.get("image") or "")
    if thumb:
        emb.set_thumbnail(url=thumb)
    yt = desk.cat.youtube(p)
    if yt:
        emb.add_field(name="Tape", value=f"[{p.get('youtube_title') or 'Watch the clip'}]({yt})", inline=False)
    emb.set_footer(text=f"Ball Keep · {desk.cat.updated} · {random.choice(QUIPS)}")
    return emb


def list_embed(discord, title, rows, color=BLUE):
    body = "\n".join(
        f"**{r.get('bk')}.** {r.get('name')} · {r.get('pos','')} {r.get('team','')} · `{fmt(r.get('value'))}`"
        for r in rows
    )
    emb = discord.Embed(title=title, description=body[:4000], color=color)
    emb.set_footer(text=f"Ball Keep · {desk.cat.updated}")
    return emb


def trade_embed(discord, result: dict):
    color = GREEN if result["label"] == "Fair Trade" else (BLUE if "A" in result["label"] else RED)

    def side(items):
        if not items:
            return "_empty_"
        lines = []
        for x in items:
            meta = "Pick" if x.get("kind") == "pick" else f"{x.get('pos','')} {x.get('team','')} · #{x.get('rank') or '—'}"
            lines.append(f"**{x['name']}** · {meta} · `{fmt(x['value'])}`")
        return "\n".join(lines)

    emb = discord.Embed(
        title=f"Trade Calculator · {result['label']}",
        description=f"**{fmt(result['total_a'])}** vs **{fmt(result['total_b'])}** · "
                    f"{'A +' + fmt(result['diff']) if result['diff'] > 0 else 'B +' + fmt(-result['diff']) if result['diff'] < 0 else 'Even'}",
        color=color,
    )
    emb.add_field(name="Side A", value=side(result["a"]), inline=True)
    emb.add_field(name="Side B", value=side(result["b"]), inline=True)
    if result["missing"]:
        emb.add_field(name="Could not find", value=", ".join(result["missing"]), inline=False)
    emb.set_footer(text="Fair = within 8% · same curve as ballkeep.com/trade.html")
    return emb


def build_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!bk ", "!keep ", "!"), intents=intents, help_command=None)

    BOARDS = [
        app_commands.Choice(name="The Keep (Superflex)", value="keep"),
        app_commands.Choice(name="The Fence (IDP)", value="fence"),
        app_commands.Choice(name="The Board", value="board"),
        app_commands.Choice(name="Redraft PPR", value="ppr"),
        app_commands.Choice(name="The Classic", value="classic"),
        app_commands.Choice(name="Redraft Standard", value="standard"),
        app_commands.Choice(name="2026 Rookies", value="rookies"),
    ]
    MODES = [
        app_commands.Choice(name="Superflex Dynasty", value="sf"),
        app_commands.Choice(name="1QB Dynasty", value="oneqb"),
        app_commands.Choice(name="Redraft PPR", value="ppr"),
        app_commands.Choice(name="The Classic", value="classic"),
        app_commands.Choice(name="Redraft Standard", value="std"),
    ]
    POSITIONS = [
        app_commands.Choice(name="Quarterback", value="QB"),
        app_commands.Choice(name="Running Back", value="RB"),
        app_commands.Choice(name="Wide Receiver", value="WR"),
        app_commands.Choice(name="Tight End", value="TE"),
        app_commands.Choice(name="Defensive Line", value="DL"),
        app_commands.Choice(name="Linebacker", value="LB"),
        app_commands.Choice(name="Defensive Back", value="DB"),
    ]
    BB_BOARDS = [
        app_commands.Choice(name="The Keep (overall dynasty 300)", value="bbkeep"),
        app_commands.Choice(name="The Lineup (hitters)", value="lineup"),
        app_commands.Choice(name="BK's Pitchers", value="pitchers"),
        app_commands.Choice(name="Bullpen Saves", value="saves"),
        app_commands.Choice(name="Bullpen SV+H", value="svh"),
        app_commands.Choice(name="Redraft ROS", value="bbredraft"),
    ]
    BB_MODES = [
        app_commands.Choice(name="Dynasty Overall", value="bbkeep"),
        app_commands.Choice(name="Dynasty Lineup", value="bblineup"),
        app_commands.Choice(name="Dynasty Pitchers", value="bbpitchers"),
        app_commands.Choice(name="Redraft", value="bbredraft"),
        app_commands.Choice(name="Bullpen Saves", value="bbsaves"),
        app_commands.Choice(name="Bullpen SV+H", value="bbsvh"),
    ]
    PL_BOARDS = [
        app_commands.Choice(name="The Premier (hybrid 400)", value="premier"),
        app_commands.Choice(name="The Pitch (Sleeper BPL 2025)", value="pitch"),
        app_commands.Choice(name="Attack", value="attack"),
        app_commands.Choice(name="Midfield", value="midfield"),
        app_commands.Choice(name="Defence", value="defence"),
        app_commands.Choice(name="Keepers", value="keepers"),
    ]
    PL_MODES = [
        app_commands.Choice(name="The Premier", value="plpremier"),
        app_commands.Choice(name="The Pitch", value="plpitch"),
        app_commands.Choice(name="Attack", value="plfwd"),
        app_commands.Choice(name="Midfield", value="plmid"),
        app_commands.Choice(name="Defence", value="pldef"),
        app_commands.Choice(name="Keepers", value="plgkp"),
    ]

    async def ac_player(interaction: discord.Interaction, current: str):
        q = current.strip() if current else ""
        if len(q) < 1:
            rows = desk.cat.raw.get("keep") or []
            return [app_commands.Choice(name=r["name"], value=r["name"]) for r in rows[:20]]
        hits = desk.cat.find(q, limit=20, sport="football")
        return [app_commands.Choice(name=h["name"], value=h["name"]) for h in hits if h.get("name")]

    async def ac_bb(interaction: discord.Interaction, current: str):
        q = current.strip() if current else ""
        if len(q) < 1:
            rows = desk.cat.raw.get("bb_keep") or []
            return [app_commands.Choice(name=r["name"], value=r["name"]) for r in rows[:20]]
        hits = desk.cat.find(q, limit=20, sport="baseball")
        return [app_commands.Choice(name=h["name"], value=h["name"]) for h in hits if h.get("name")]

    async def ac_pl(interaction: discord.Interaction, current: str):
        q = current.strip() if current else ""
        if len(q) < 1:
            rows = desk.cat.raw.get("pl_pitch") or []
            return [app_commands.Choice(name=r["name"], value=r["name"]) for r in rows[:20]]
        hits = desk.cat.find(q, limit=20, sport="soccer")
        return [app_commands.Choice(name=h["name"], value=h["name"]) for h in hits if h.get("name")]

    @bot.event
    async def on_ready():
        guild_id = os.getenv("DISCORD_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        else:
            await bot.tree.sync()
        print(f"Ball Keep desk online as {bot.user} · catalog {desk.cat.updated}")

    @bot.tree.command(name="desk", description="What is Ball Keep, and which slash commands live here?")
    async def desk_cmd(interaction: discord.Interaction):
        emb = discord.Embed(
            title="BALL KEEP desk",
            description="A powder-blue Superflex shop. Rankings from 10 public boards, "
                        "BK Value on a decaying curve, player files with 2025 tape, "
                        "and four trade calculators.\n\n" + random.choice(QUIPS),
            color=BLUE,
            url="https://ballkeep.com",
        )
        emb.add_field(
            name="Look someone up",
            value="`/player` `/search` `/rank` `/top` `/pos` `/compare` `/stack` `/random` `/quiz`",
            inline=False,
        )
        emb.add_field(
            name="Make a deal",
            value="`/trade` `/value` `/picks` `/formula` `/deals`  ·  `/deals JSN`",
            inline=False,
        )
        emb.add_field(
            name="The rest of the site",
            value="`/video` `/hot` `/cold` `/hottake` `/rookies` `/keep-or-cut` `/start` `/nfl` `/mlb` `/publish`",
            inline=False,
        )
        emb.add_field(
            name="BaseBallKeep",
            value="`/bbplayer Ohtani` `/bbkeep` `/bbtrade` `/bbwire` · navy desk at ballkeep.com/bb",
            inline=False,
        )
        emb.add_field(
            name="PitchKeep",
            value="`/plplayer Haaland` `/pitch` `/pltrade` · purple desk at ballkeep.com/pl",
            inline=False,
        )
        emb.set_thumbnail(url="https://ballkeep.com/img/logo.jpg")
        emb.set_footer(text=f"Updated {desk.cat.updated} · ballkeep.com")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="player", description="Full Ball Keep player file: ranks, BK Value, plus/minus, tape")
    @app_commands.describe(name="Player name or nickname (JSN, CMC, Sun God, BTJ…)")
    @app_commands.autocomplete(name=ac_player)
    async def player_cmd(interaction: discord.Interaction, name: str):
        p = desk.cat.one(name, sport="football") or desk.cat.one(name)
        if not p:
            await interaction.response.send_message(f"Not on the desk: **{name}**. Try `/search` or `/bbplayer`.", ephemeral=True)
            return
        rich = desk.cat.by_key.get(p.get("key") or norm(p.get("name", "")))
        await interaction.response.send_message(embed=player_embed(discord, rich or p))

    @bot.tree.command(name="search", description="Search every Ball Keep list")
    @app_commands.describe(query="Name, team, or nickname")
    async def search_cmd(interaction: discord.Interaction, query: str):
        hits = desk.cat.find(query, limit=10)
        if not hits:
            await interaction.response.send_message(f"No hits for **{query}**.", ephemeral=True)
            return
        lines = []
        for h in hits:
            lists = h.get("lists") or {}
            keep = lists.get("The Keep") or h.get("bk")
            lines.append(f"**{h['name']}** · {h.get('pos','')} {h.get('team','')} · Keep #{keep or '—'}")
        emb = discord.Embed(title=f"Search · {query}", description="\n".join(lines), color=BLUE)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="rank", description="One player's rank on a specific Ball Keep list")
    @app_commands.describe(name="Player", board="Which list")
    @app_commands.autocomplete(name=ac_player)
    @app_commands.choices(board=BOARDS)
    async def rank_cmd(interaction: discord.Interaction, name: str, board: app_commands.Choice[str]):
        row = desk.cat.board_row(name, board.value)
        if not row:
            await interaction.response.send_message(f"**{name}** is not on {board.name}.", ephemeral=True)
            return
        emb = discord.Embed(
            title=f"{row['name']} · {board.name}",
            description=f"**#{row.get('bk')}** · {row.get('pos')} {row.get('team')} · BK Value `{fmt(row.get('value'))}`",
            color=RED,
            url="https://ballkeep.com",
        )
        if row.get("avg"):
            emb.add_field(name="Average", value=str(row["avg"]))
        if row.get("ranks"):
            emb.add_field(name="By board", value="\n".join(f"{k}: {v}" for k, v in sorted(row["ranks"].items(), key=lambda kv: kv[1]))[:1024], inline=False)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="top", description="Leaderboard from any Ball Keep list")
    @app_commands.describe(board="Which list", count="How many names (default 15, max 25)")
    @app_commands.choices(board=BOARDS)
    async def top_cmd(interaction: discord.Interaction, board: app_commands.Choice[str], count: int = 15):
        rows = desk.cat.list_for(board.value)[: max(1, min(count, 25))]
        await interaction.response.send_message(embed=list_embed(discord, board.name, rows, RED if board.value == "keep" else BLUE))

    @bot.tree.command(name="trade", description="Ball Keep trade calculator using BK Value from our lists")
    @app_commands.describe(
        mode="Which calculator",
        side_a="Comma-separated names and picks",
        side_b="Comma-separated names and picks",
    )
    @app_commands.choices(mode=MODES)
    async def trade_cmd(interaction: discord.Interaction, mode: app_commands.Choice[str], side_a: str, side_b: str):
        result = desk.cat.trade(mode.value, side_a, side_b)
        await interaction.response.send_message(embed=trade_embed(discord, result))

    @bot.tree.command(name="deals", description="Recent Superflex packages involving a player")
    @app_commands.describe(name="Player or nickname. Leave blank for the newest deals.")
    @app_commands.autocomplete(name=ac_player)
    async def deals_cmd(interaction: discord.Interaction, name: Optional[str] = None):
        rows = desk.cat.deals_for(name or "")
        if not rows:
            await interaction.response.send_message(
                f"No packages on the tape for **{name}**. Try `/deals JSN`.",
                ephemeral=True,
            )
            return
        title = f"Recent deals · {name}" if name else "Recent deals"
        emb = discord.Embed(
            title=title,
            description=f"{len(rows)} package{'s' if len(rows) != 1 else ''} on the desk tape. Same log as ballkeep.com/recent-trades.html",
            color=BLUE,
            url="https://ballkeep.com/recent-trades.html" + (f"?q={name}" if name else ""),
        )
        for d in rows[:8]:
            def bits(side):
                return ", ".join(x["name"] for x in side)
            tag = "asking" if d.get("kind") == "asking" else "closed"
            emb.add_field(
                name=f"{d.get('date')} · {d.get('format')} · {d.get('label')} ({tag})",
                value=f"**A** {bits(d.get('a') or [])} `{fmt(d.get('total_a'))}`\n"
                      f"**B** {bits(d.get('b') or [])} `{fmt(d.get('total_b'))}`\n"
                      f"{(d.get('blurb') or '')[:180]}",
                inline=False,
            )
        emb.set_footer(text=random.choice(QUIPS))
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="value", description="BK Value for a player or pick on a calculator")
    @app_commands.describe(name="Player or pick (2027 Mid 1st)", mode="Calculator")
    @app_commands.autocomplete(name=ac_player)
    @app_commands.choices(mode=MODES)
    async def value_cmd(interaction: discord.Interaction, name: str, mode: Optional[app_commands.Choice[str]] = None):
        mode_v = mode.value if mode else "sf"
        asset = desk.cat.resolve_asset(name, mode_v)
        if not asset:
            await interaction.response.send_message(f"No value for **{name}**.", ephemeral=True)
            return
        emb = discord.Embed(
            title=f"{asset['name']} · {fmt(asset['value'])} BK",
            description=f"{asset.get('pos')} {asset.get('team')} · rank {asset.get('rank')} on the {mode_v} curve.",
            color=BLUE,
        )
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="video", description="2025 NFL or college highlight from the player page")
    @app_commands.describe(name="Player")
    @app_commands.autocomplete(name=ac_player)
    async def video_cmd(interaction: discord.Interaction, name: str):
        p = desk.cat.one(name)
        rich = desk.cat.by_key.get((p or {}).get("key") or norm(name))
        target = rich or p
        if not target:
            await interaction.response.send_message(f"No file for **{name}**.", ephemeral=True)
            return
        yt = desk.cat.youtube(target)
        if not yt:
            await interaction.response.send_message(f"**{target.get('name')}** is on the desk but the tape drawer is empty.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"**{target.get('name')}** · {target.get('youtube_title') or 'highlight'}\n{yt}"
        )

    @bot.tree.command(name="hot", description="BK Hot board — names to buy")
    async def hot_cmd(interaction: discord.Interaction):
        lines = [f"**{i}. {x['name']}** ({x['pos']} {x['team']})\n{x['why']}" for i, x in enumerate(desk.cat.raw["hot"], 1)]
        emb = discord.Embed(title="🔥 Hot — Buy", description="\n\n".join(lines)[:4000], color=RED)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="cold", description="BK Cold board — names to sell")
    async def cold_cmd(interaction: discord.Interaction):
        lines = [f"**{i}. {x['name']}** ({x['pos']} {x['team']})\n{x['why']}" for i, x in enumerate(desk.cat.raw["cold"], 1)]
        emb = discord.Embed(title="❄️ Cold — Sell", description="\n\n".join(lines)[:4000], color=BLUE)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="rookies", description="2026 drafted rookie Superflex board")
    async def rookies_cmd(interaction: discord.Interaction):
        rows = desk.cat.raw.get("rookies") or []
        body = "\n".join(
            f"**{r['bk']}. {r['name']}** · {r.get('pos')} {r.get('team')} · `{fmt(r.get('value'))}` · {r.get('blurb') or ''}"
            for r in rows
        )
        emb = discord.Embed(title="2026 Rookies", description=body[:4000], color=GREEN)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="compare", description="Two players, side by side, Keep + PPR + value")
    @app_commands.describe(a="Player A", b="Player B")
    @app_commands.autocomplete(a=ac_player)
    @app_commands.autocomplete(b=ac_player)
    async def compare_cmd(interaction: discord.Interaction, a: str, b: str):
        pa, pb = desk.cat.one(a), desk.cat.one(b)
        if not pa or not pb:
            await interaction.response.send_message("Need two names the desk actually has.", ephemeral=True)
            return

        def blurb(p):
            lists = p.get("lists") or {}
            keep = lists.get("The Keep") or "—"
            return (
                f"{p.get('pos')} {p.get('team')}\n"
                f"Keep #{keep} · `{fmt(bk_value(lists.get('The Keep')))}`\n"
                f"PPR #{lists.get('Redraft PPR') or '—'} · STD #{lists.get('Redraft Standard') or '—'}"
            )

        emb = discord.Embed(title=f"{pa['name']} vs {pb['name']}", color=INK)
        emb.add_field(name=pa["name"], value=blurb(pa), inline=True)
        emb.add_field(name=pb["name"], value=blurb(pb), inline=True)
        ka = (pa.get("lists") or {}).get("The Keep") or 99
        kb = (pb.get("lists") or {}).get("The Keep") or 99
        winner = pa["name"] if ka < kb else pb["name"]
        emb.set_footer(text=f"The Keep prefers {winner}. {random.choice(QUIPS)}")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="keep-or-cut", description="Theatrical buy/sell using Hot, Cold, and The Keep")
    @app_commands.describe(name="Player")
    @app_commands.autocomplete(name=ac_player)
    async def koc_cmd(interaction: discord.Interaction, name: str):
        p = desk.cat.one(name)
        if not p:
            await interaction.response.send_message("Not on the desk.", ephemeral=True)
            return
        lists = p.get("lists") or {}
        keep = lists.get("The Keep")
        if lists.get("Hot"):
            verdict, color, line = "KEEP — actually, BUY", RED, "On the Hot board. Do not get cute."
        elif lists.get("Cold"):
            verdict, color, line = "CUT — sell the name", BLUE, "On the Cold board. Cash it before the tape does."
        elif keep and keep <= 15:
            verdict, color, line = "KEEP forever", RED, "Superflex first-rounder. You are not 'selling high.'"
        elif keep and keep <= 40:
            verdict, color, line = "KEEP", BLUE, "Core piece. Only move him for a clear overpay."
        elif keep:
            verdict, color, line = "LEAN CUT", INK, "In the 100, not in the foundation. Price him, don't marry him."
        else:
            verdict, color, line = "CUT / stash", INK, "Not on The Keep top 100. Fun, not a building block."
        graf = (p.get("grafs") or [line])[0][:400]
        emb = discord.Embed(title=f"{p['name']} · {verdict}", description=f"{line}\n\n{graf}", color=color, url=p.get("url"))
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="random", description="Random player file off the desk")
    async def random_cmd(interaction: discord.Interaction):
        p = random.choice(desk.cat.players)
        await interaction.response.send_message(content=f"The desk shuffled the stack.", embed=player_embed(discord, p))

    @bot.tree.command(name="stack", description="Every name from a team on The Keep / a board")
    @app_commands.describe(team="NFL abbreviation (BUF, NE, DAL…)", board="Which list")
    @app_commands.choices(board=BOARDS)
    async def stack_cmd(interaction: discord.Interaction, team: str, board: Optional[app_commands.Choice[str]] = None):
        b = board.value if board else "keep"
        rows = desk.cat.team_players(team, b)
        if not rows:
            await interaction.response.send_message(f"No {team.upper()} names on that list.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=list_embed(discord, f"{team.upper()} stack · {b}", rows[:25], BLUE)
        )

    @bot.tree.command(name="nfl", description="2026 NFL slate for a team or week")
    @app_commands.describe(team="BUF, NE, DAL…", week="Week number")
    async def nfl_cmd(interaction: discord.Interaction, team: Optional[str] = None, week: Optional[int] = None):
        team_u = desk.cat.nfl_abbr(team) if team else ""
        rows = desk.cat.nfl_games(team_u or None, week)
        if not rows:
            rows = desk.cat.nfl_games(week=1)[:16]
        if not rows:
            await interaction.response.send_message("No games matched. Try `BUF` or `week:1`.", ephemeral=True)
            return
        label = team_u or (f"Week {week}" if week else "NFL slate")
        body = "\n".join(
            f"W{g.get('week')} {g.get('day','')} · **{g.get('away')} {g.get('prep','at')} {g.get('home')}** · {g.get('time')} {g.get('tv','')}"
            for g in rows[:20]
        )
        emb = discord.Embed(title=f"NFL · {label}", description=body[:4000], color=BLUE, url="https://ballkeep.com/nfl-schedule.html")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="mlb", description="September MLB games for a club")
    @app_commands.describe(team="NYY, LAD, BOS…")
    async def mlb_cmd(interaction: discord.Interaction, team: str):
        t = desk.cat.mlb_abbr(team)
        rows = desk.cat.mlb_games(t)
        if not rows:
            await interaction.response.send_message(f"No September games for **{t}** in the catalog.", ephemeral=True)
            return
        body = "\n".join(f"{g.get('day')} · **{g.get('away')} @ {g.get('home')}** · {g.get('time')}" for g in rows[:20])
        emb = discord.Embed(title=f"MLB · {t}", description=body[:4000], color=RED, url="https://ballkeep.com/mlb-schedule.html")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="picks", description="Future-pick BK Values on the Superflex curve")
    async def picks_cmd(interaction: discord.Interaction):
        picks = desk.cat.raw.get("picks") or []
        body = "\n".join(f"**{p['name']}** · rank {p['rank']} · `{fmt(p['value'])}`" for p in picks)
        emb = discord.Embed(
            title="Trade-block picks",
            description=body[:4000],
            color=RED,
            url="https://ballkeep.com/trade.html",
        )
        emb.set_footer(text="Same ranks as the dynasty calculators. A late first is not a 1.01 in a hoodie.")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="pos", description="Top names at a position on any Ball Keep list")
    @app_commands.describe(position="QB / RB / WR / TE", board="Which list", count="How many (max 20)")
    @app_commands.choices(position=POSITIONS, board=BOARDS)
    async def pos_cmd(
        interaction: discord.Interaction,
        position: app_commands.Choice[str],
        board: Optional[app_commands.Choice[str]] = None,
        count: int = 12,
    ):
        b = board.value if board else "keep"
        rows = desk.cat.pos_top(position.value, b, max(1, min(count, 20)))
        if not rows:
            await interaction.response.send_message(f"No {position.value}s on that list.", ephemeral=True)
            return
        title = f"{position.name}s · {board.name if board else 'The Keep'}"
        await interaction.response.send_message(embed=list_embed(discord, title, rows, RED if position.value == "QB" else BLUE))

    @bot.tree.command(name="quiz", description="Guess a Keep rank. Spoiler to cheat.")
    async def quiz_cmd(interaction: discord.Interaction):
        pool = (desk.cat.raw.get("keep") or [])[:60]
        p = random.choice(pool)
        clues = []
        if p.get("pos"):
            clues.append(p["pos"])
        if p.get("team"):
            clues.append(p["team"])
        if p.get("age"):
            clues.append(f"age {p['age']}")
        emb = discord.Embed(
            title="Keep quiz",
            description=(
                f"Where does **{p['name']}** sit on The Keep?\n"
                f"{' · '.join(clues)}\n\n"
                f"Reveal when you are ready: ||**#{p['bk']}** · `{fmt(p.get('value'))}` BK||\n\n"
                f"{random.choice(QUIPS)}"
            ),
            color=RED,
        )
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="formula", description="How BK Value turns a rank into a trade number")
    async def formula_cmd(interaction: discord.Interaction):
        samples = [1, 8, 18, 28, 36, 50, 75, 100]
        lines = [f"Rank **{r}** → `{fmt(bk_value(r))}`" for r in samples]
        emb = discord.Embed(
            title="BK Value",
            description=(
                f"`{FORMULA}`\n"
                "Rank 1 is **12,000**. 1QB taxes quarterbacks to **38%** of Superflex.\n"
                "Fair trade = the two sides within **8%**.\n\n" + "\n".join(lines)
            ),
            color=BLUE,
            url="https://ballkeep.com/trade.html",
        )
        emb.set_footer(text=desk.cat.raw.get("algorithm") or "")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="hottake", description="Random Hot or Cold name, with the actual desk note")
    async def hottake_cmd(interaction: discord.Interaction):
        if random.random() < 0.5:
            x = random.choice(desk.cat.raw["hot"])
            title, color, stamp = f"🔥 BUY · {x['name']}", RED, "Hot board"
        else:
            x = random.choice(desk.cat.raw["cold"])
            title, color, stamp = f"❄️ SELL · {x['name']}", BLUE, "Cold board"
        emb = discord.Embed(
            title=title,
            description=f"{x['pos']} {x['team']}\n\n{x['why']}\n\n{random.choice(QUIPS)}",
            color=color,
        )
        emb.set_footer(text=f"{stamp} · {x.get('src') or 'Ball Keep'} · {desk.cat.updated}")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="start", description="Who to start this week — redraft PPR, with Keep as a tiebreak")
    @app_commands.describe(a="Player A", b="Player B")
    @app_commands.autocomplete(a=ac_player)
    @app_commands.autocomplete(b=ac_player)
    async def start_cmd(interaction: discord.Interaction, a: str, b: str):
        pa, pb = desk.cat.one(a), desk.cat.one(b)
        if not pa or not pb:
            await interaction.response.send_message("Need two names the desk actually has.", ephemeral=True)
            return

        def ppr_rank(p):
            lists = p.get("lists") or {}
            return lists.get("Redraft PPR") or 999

        def keep_rank(p):
            lists = p.get("lists") or {}
            return lists.get("The Keep") or p.get("bk") or 999

        ra, rb = ppr_rank(pa), ppr_rank(pb)
        winner = pa if ra < rb else pb
        loser = pb if winner is pa else pa
        if ra == rb:
            winner = pa if keep_rank(pa) <= keep_rank(pb) else pb
            loser = pb if winner is pa else pa
            why = "PPR is tied. The Keep breaks it."
        else:
            why = "Redraft PPR is the start/sit board. Dynasty is the marriage."
        emb = discord.Embed(
            title=f"Start {winner['name']}",
            description=f"{why}\n\nSit **{loser['name']}** unless the matchup is a cartoon.",
            color=GREEN,
        )
        emb.add_field(name=pa["name"], value=f"PPR #{ppr_rank(pa) if ppr_rank(pa) != 999 else '—'} · Keep #{keep_rank(pa)}", inline=True)
        emb.add_field(name=pb["name"], value=f"PPR #{ppr_rank(pb) if ppr_rank(pb) != 999 else '—'} · Keep #{keep_rank(pb)}", inline=True)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="sources", description="30+ Super Aggregate desks inside The Keep")
    async def sources_cmd(interaction: discord.Interaction):
        src = desk.cat.raw.get("sources") or []
        emb = discord.Embed(
            title=f"Super Aggregate · {len(src)} desks",
            description="\n".join(f"• {s}" for s in src),
            color=INK,
        )
        emb.set_footer(text=desk.cat.updated)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="bbplayer", description="BaseBallKeep file: Keep 400, Lineup, Pitchers, redraft")
    @app_commands.describe(name="Baseball player (Ohtani, Judge, PCA, Skenes…)")
    @app_commands.autocomplete(name=ac_bb)
    async def bbplayer_cmd(interaction: discord.Interaction, name: str):
        p = desk.cat.one(name, sport="baseball")
        if not p:
            await interaction.response.send_message(f"Not on BaseBallKeep: **{name}**.", ephemeral=True)
            return
        files = {norm(x.get("name", "")): x for x in desk.cat.raw.get("bb_players") or []}
        rich = files.get(norm(p.get("name", ""))) or p
        rich = {**rich, "sport": "baseball"}
        await interaction.response.send_message(embed=player_embed(discord, rich))

    @bot.tree.command(name="bbkeep", description="A BaseBallKeep board: Keep, Lineup, Pitchers, bullpen, redraft")
    @app_commands.describe(board="Which diamond list", count="How many names (default 15, max 25)")
    @app_commands.choices(board=BB_BOARDS)
    async def bbkeep_cmd(interaction: discord.Interaction, board: app_commands.Choice[str], count: int = 15):
        rows = desk.cat.list_for(board.value)[: max(1, min(count, 25))]
        if not rows:
            await interaction.response.send_message("That baseball board is empty. Rebuild the site catalog.", ephemeral=True)
            return
        await interaction.response.send_message(embed=list_embed(discord, f"BaseBallKeep · {board.name}", rows, NAVY))

    @bot.tree.command(name="bbtrade", description="BaseBallKeep trade calculator — same BK Value curve")
    @app_commands.describe(mode="Which diamond calculator", side_a="Names, comma-separated", side_b="Names, comma-separated")
    @app_commands.choices(mode=BB_MODES)
    async def bbtrade_cmd(interaction: discord.Interaction, mode: app_commands.Choice[str], side_a: str, side_b: str):
        result = desk.cat.trade(mode.value, side_a, side_b)
        emb = trade_embed(discord, result)
        emb.set_footer(text="Fair = within 8% · same curve as ballkeep.com/bb/trade.html")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="bbwire", description="BaseBallKeep waiver adds — dynasty stash vs the longer redraft wire")
    @app_commands.describe(kind="Dynasty (short) or redraft (longer, higher priority)")
    @app_commands.choices(kind=[
        app_commands.Choice(name="Dynasty stashes", value="dynasty"),
        app_commands.Choice(name="Redraft priority 1–50", value="redraft"),
    ])
    async def bbwire_cmd(interaction: discord.Interaction, kind: app_commands.Choice[str]):
        key = "bb_waivers_redraft" if kind.value == "redraft" else "bb_waivers_dynasty"
        rows = desk.cat.raw.get(key) or []
        if not rows:
            await interaction.response.send_message("Waiver lists missing. Rebuild the catalog.", ephemeral=True)
            return
        lines = [f"**P{x['pri']}. {x['name']}** · {x.get('pos','')} {x.get('team','')} — {x.get('why')}" for x in rows]
        # Discord field limit; split into chunks
        body = "\n\n".join(lines)
        emb = discord.Embed(
            title=f"BaseBallKeep Wire · {kind.name}",
            description=body[:4000],
            color=NAVY if kind.value == "dynasty" else 0xC8102E,
            url="https://ballkeep.com/bb/waivers-redraft.html" if kind.value == "redraft" else "https://ballkeep.com/bb/waivers-dynasty.html",
        )
        if len(body) > 4000:
            emb.add_field(name="More", value=body[4000:5000] or "Full list on the site.", inline=False)
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="plplayer", description="PitchKeep file: The Premier hybrid 400, Sleeper BPL 2025, tape")
    @app_commands.describe(name="Premier League player (Haaland, Bruno, Saka, Semenyo…)")
    @app_commands.autocomplete(name=ac_pl)
    async def plplayer_cmd(interaction: discord.Interaction, name: str):
        p = desk.cat.one(name, sport="soccer")
        if not p:
            await interaction.response.send_message(f"Not on PitchKeep: **{name}**.", ephemeral=True)
            return
        files = {norm(x.get("name", "")): x for x in desk.cat.raw.get("pl_players") or []}
        rich = files.get(norm(p.get("name", ""))) or p
        rich = {**rich, "sport": "soccer"}
        await interaction.response.send_message(embed=player_embed(discord, rich))

    @bot.tree.command(name="pitch", description="A PitchKeep board: The Premier, The Pitch, Attack, Midfield, Defence, Keepers")
    @app_commands.describe(board="Which Premier League list", count="How many names (default 15, max 25)")
    @app_commands.choices(board=PL_BOARDS)
    async def pitch_cmd(interaction: discord.Interaction, board: app_commands.Choice[str], count: int = 15):
        rows = desk.cat.list_for(board.value)[: max(1, min(count, 25))]
        if not rows:
            await interaction.response.send_message("That PitchKeep board is empty. Rebuild the site catalog.", ephemeral=True)
            return
        await interaction.response.send_message(embed=list_embed(discord, f"PitchKeep · {board.name}", rows, PURPLE))

    @bot.tree.command(name="pltrade", description="PitchKeep trade calculator — same BK Value curve")
    @app_commands.describe(mode="Which PitchKeep calculator", side_a="Names, comma-separated", side_b="Names, comma-separated")
    @app_commands.choices(mode=PL_MODES)
    async def pltrade_cmd(interaction: discord.Interaction, mode: app_commands.Choice[str], side_a: str, side_b: str):
        result = desk.cat.trade(mode.value, side_a, side_b)
        emb = trade_embed(discord, result)
        emb.color = PURPLE
        emb.set_footer(text="Fair = within 8% · same curve as ballkeep.com/pl/trade.html")
        await interaction.response.send_message(embed=emb)

    @bot.tree.command(name="reload", description="Reload discord-catalog.json after a site rebuild (admin)")
    @app_commands.default_permissions(manage_guild=True)
    async def reload_cmd(interaction: discord.Interaction):
        when = desk.reload()
        await interaction.response.send_message(f"Catalog reloaded · **{when}** · {len(desk.cat.players)} player files.")

    @bot.tree.command(name="publish", description="Write the entire Ball Keep site into this server as searchable channels (admin)")
    @app_commands.default_permissions(manage_guild=True)
    async def publish_cmd(interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Run this in a server.", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        from publish import publish as do_publish

        async def progress(msg):
            try:
                await interaction.followup.send(msg, ephemeral=True)
            except discord.HTTPException:
                pass

        try:
            await do_publish(interaction.guild, desk.cat, progress=progress)
            await interaction.followup.send(
                "The desk is in the server. Look for the **BALL KEEP DESK** category. "
                "Discord search now hits Keep ranks, player files, and tape."
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "I need **Manage Channels** and **Send Messages** to publish the desk."
            )

    @bot.command(name="help")
    async def prefix_help(ctx: commands.Context):
        await ctx.reply(
            "**Ball Keep desk** — try `/desk` for the full menu.\n"
            "`!bk player maye` · `!bk video jsn` · `!bk trade Allen vs Bijan`\n"
            "`!bk top keep` · `who is Drake Maye` · `trade Allen for Bijan` · `start Gibbs or Jeanty`"
        )

    @bot.command(name="player")
    async def prefix_player(ctx: commands.Context, *, name: str):
        p = desk.cat.one(name)
        if not p:
            await ctx.reply(f"Not on the desk: {name}")
            return
        rich = desk.cat.by_key.get(p.get("key") or norm(p.get("name", ""))) or p
        await ctx.reply(embed=player_embed(discord, rich))

    @bot.command(name="video")
    async def prefix_video(ctx: commands.Context, *, name: str):
        p = desk.cat.one(name)
        yt = desk.cat.youtube(p) if p else None
        if not yt:
            await ctx.reply(f"No tape for **{name}**.")
            return
        await ctx.reply(f"**{p.get('name')}** · {p.get('youtube_title') or 'highlight'}\n{yt}")

    @bot.command(name="trade")
    async def prefix_trade(ctx: commands.Context, *, blob: str):
        parts = re.split(r"\b(?:vs|versus|for)\b", blob, maxsplit=1, flags=re.I)
        if len(parts) != 2:
            await ctx.reply("Use `!bk trade Allen, 2027 Mid 1st vs Bijan, Chase`")
            return
        result = desk.cat.trade("sf", parts[0], parts[1])
        await ctx.reply(embed=trade_embed(discord, result))

    @bot.command(name="top")
    async def prefix_top(ctx: commands.Context, board: str = "keep"):
        rows = desk.cat.list_for(board)[:15]
        label = {"keep": "The Keep", "board": "The Board", "ppr": "Redraft PPR", "classic": "The Classic", "standard": "Redraft Standard", "rookies": "2026 Rookies"}.get(board.lower(), board)
        await ctx.reply(embed=list_embed(discord, label, rows, RED if board.lower() in ("keep", "sf") else BLUE))

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            await bot.process_commands(message)
            return
        text = message.content.strip()
        low = text.lower()
        if low.startswith(("who is ", "who's ", "who is the ")):
            q = re_name(low)
            if q:
                p = desk.cat.one(q)
                if p:
                    rich = desk.cat.by_key.get(p.get("key") or norm(p.get("name", ""))) or p
                    await message.reply(embed=player_embed(discord, rich))
                    return
        m = re.search(r"^trade (.+?) (?:for|vs|versus) (.+?)[\?]?$", low)
        if m:
            result = desk.cat.trade("sf", m.group(1), m.group(2))
            await message.reply(embed=trade_embed(discord, result))
            return
        m = re.search(r"^(?:start|sit) (.+?) or (.+?)[\?]?$", low)
        if m:
            pa, pb = desk.cat.one(m.group(1)), desk.cat.one(m.group(2))
            if pa and pb:
                ra = (pa.get("lists") or {}).get("Redraft PPR") or 999
                rb = (pb.get("lists") or {}).get("Redraft PPR") or 999
                winner = pa if ra <= rb else pb
                await message.reply(f"Start **{winner['name']}**. PPR #{min(ra, rb) if min(ra, rb) != 999 else '—'} beats the other name.")
                return
        m = re.search(r"^video (?:of |on )?(.+?)[\?]?$", low)
        if m:
            p = desk.cat.one(m.group(1))
            yt = desk.cat.youtube(p) if p else None
            if yt:
                await message.reply(f"**{p.get('name')}**\n{yt}")
                return
        await bot.process_commands(message)

    return bot


def re_name(low: str) -> str:
    import re as _re
    m = _re.search(r"who(?:'s| is)(?: the)? (.+?)(?:\?|$)", low)
    return (m.group(1) if m else "").replace(" on the keep", "").strip()


def main():
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        sys.stderr.write(
            "Set DISCORD_TOKEN in .env (see bot/.env.example).\n"
            "Create an application at https://discord.com/developers/applications\n"
        )
        sys.exit(1)
    bot = build_bot()
    bot.run(token)


if __name__ == "__main__":
    main()
