"""Stamp the Ball Keep desk into a Discord server as searchable channels."""
from __future__ import annotations

import asyncio

import discord

from catalog import FORMULA, Catalog

CATEGORY = "BALL KEEP DESK"
CHANNELS = [
    ("desk", "how to search the desk and what BK Value means"),
    ("the-keep", "superflex dynasty top 400"),
    ("the-board", "long proprietary aggregate"),
    ("redraft-ppr", "2026 full-PPR board"),
    ("redraft-std", "2026 standard board"),
    ("rookies-2026", "drafted rookie consensus"),
    ("hot-n-cold", "buys and sells"),
    ("trade-block", "calculator notes and pick values"),
    ("recent-deals", "desk tape of recent superflex packages"),
    ("tape", "2025 and college highlight links"),
    ("nfl-slate", "2026 nfl schedule, every week"),
    ("mlb-slate", "september baseball, every club"),
    ("sources", "the 30+ super aggregate desks inside the keep"),
    ("player-files", "every football player page, plus/minus, and ranks"),
    ("bb-keep", "baseball dynasty top 400"),
    ("bb-lineup", "dynasty hitters only"),
    ("bb-pitchers", "top 100 dynasty pitchers"),
    ("bb-bullpen", "saves and sv+h relief lists"),
    ("bb-redraft", "baseball rest-of-season board"),
    ("bb-waivers", "dynasty stashes and the longer redraft wire"),
    ("the-premier", "premier league hybrid 400 · sleeper + every board"),
    ("the-pitch", "premier league top 400 · sleeper bpl 2025"),
    ("pl-attack", "fpl forwards"),
    ("pl-midfield", "fpl midfield"),
    ("pl-defence", "fpl defenders"),
    ("pl-keepers", "fpl goalkeepers"),
    ("pl-files", "pitchkeep player files with tape"),
]


def _chunks(rows, n=20):
    for i in range(0, len(rows), n):
        yield rows[i : i + n]


def _line(r):
    val = r.get("value")
    val_s = f" · `{int(val):,}`" if val else ""
    return f"**{r.get('bk','')}.** {r.get('name')} · {r.get('pos','')} {r.get('team','')}{val_s}"


async def _get_or_create_category(guild: discord.Guild) -> discord.CategoryChannel:
    for c in guild.categories:
        if c.name.upper() == CATEGORY:
            return c
    return await guild.create_category(CATEGORY, reason="Ball Keep desk publish")


async def _get_or_create_text(guild, category, name, topic) -> discord.TextChannel:
    for ch in guild.text_channels:
        if ch.name == name and ch.category_id == category.id:
            return ch
    return await guild.create_text_channel(name, category=category, topic=topic, reason="Ball Keep desk publish")


async def _wipe(ch: discord.TextChannel, limit=200):
    try:
        await ch.purge(limit=limit, bulk=True)
    except discord.Forbidden:
        async for msg in ch.history(limit=limit):
            try:
                await msg.delete()
            except discord.HTTPException:
                break


async def _post_list(ch, title, rows, cat: Catalog, extra=""):
    await ch.send(
        f"**{title}** · updated {cat.updated}\n{extra}\n"
        f"Search this channel for a name. Or run `/player` anywhere."
    )
    for group in _chunks(rows, 20):
        body = "\n".join(_line(r) for r in group)
        await ch.send(body)
        await asyncio.sleep(1.05)


async def publish(guild: discord.Guild, cat: Catalog, progress=None):
    """Create/update the Ball Keep category and write every list into it."""
    category = await _get_or_create_category(guild)
    channels = {}
    for name, topic in CHANNELS:
        channels[name] = await _get_or_create_text(guild, category, name, topic)

    async def note(msg):
        if progress:
            await progress(msg)

    desk = channels["desk"]
    await _wipe(desk)
    await desk.send(
        "**Welcome to the Ball Keep desk.**\n"
        "This category is a carbon copy of ballkeep.com so Discord search works.\n\n"
        f"Ranks last aggregated **{cat.updated}**.\n"
        "BK Value formula: rank 1 = **12,000**. "
        f"`{FORMULA}`\n"
        "1QB taxes quarterbacks to 38% of Superflex value.\n\n"
        "**Slash commands (work in every channel)**\n"
        "`/player` `/search` `/top` `/rank` `/pos` `/trade` `/deals` `/value` `/picks` `/formula` "
        "`/video` `/hot` `/cold` `/hottake` `/rookies` `/compare` `/keep-or-cut` `/start` "
        "`/quiz` `/nfl` `/mlb` `/random` `/stack` `/desk` `/bbplayer` `/bbkeep` `/bbtrade` `/bbwire` "
        "`/plplayer` `/pitch` `/pltrade`\n\n"
        "Try: `/player Josh Allen` · `/bbplayer Ohtani` · `/plplayer Haaland` · "
        "`/trade Superflex Allen, 2027 Mid 1st vs Bijan, Chase` · "
        "`/video Drake Maye` · `who is JSN` · `trade Allen for Bijan`"
    )
    await note("Desk intro posted.")

    await _wipe(channels["the-keep"])
    await _post_list(
        channels["the-keep"],
        "The Keep - Superflex Dynasty Top 400",
        cat.raw["keep"],
        cat,
        "Super Aggregate of 30+ desks. 50% long boards, 50% the rest. Top 400.",
    )
    await note("The Keep posted.")

    await _wipe(channels["the-board"])
    await _post_list(
        channels["the-board"],
        "The Board - Redraft PPR",
        cat.raw["board"],
        cat,
        "Redraft PPR. Field Yates, FantasyPros PPR ECR, Karabell Flex.",
    )
    await note("The Board posted.")

    await _wipe(channels["redraft-ppr"])
    await _post_list(channels["redraft-ppr"], "Redraft PPR", cat.raw["ppr"], cat)
    await _wipe(channels["redraft-std"])
    await _post_list(channels["redraft-std"], "Redraft Standard", cat.raw["standard"], cat)
    await note("Redraft boards posted.")

    await _wipe(channels["rookies-2026"])
    rook_extra = "\n".join(
        f"**{r['bk']}. {r['name']}** ({r.get('pos')} {r.get('team')}) · {r.get('blurb') or ''}"
        for r in cat.raw.get("rookies") or []
    )
    await channels["rookies-2026"].send(f"**2026 Rookies** · {cat.updated}\n{rook_extra[:1900]}")
    await note("Rookies posted.")

    await _wipe(channels["hot-n-cold"])
    hot = "\n".join(f"**HOT {i}. {x['name']}** ({x['pos']} {x['team']}) - {x['why']}" for i, x in enumerate(cat.raw["hot"], 1))
    cold = "\n".join(f"**COLD {i}. {x['name']}** ({x['pos']} {x['team']}) - {x['why']}" for i, x in enumerate(cat.raw["cold"], 1))
    await channels["hot-n-cold"].send(f"🔥 **Hot - Buy**\n{hot}")
    await channels["hot-n-cold"].send(f"❄️ **Cold - Sell**\n{cold}")
    await note("Hot 'n' Cold posted.")

    await _wipe(channels["trade-block"])
    picks = "\n".join(f"**{p['name']}** · rank {p['rank']} · `{p['value']:,}`" for p in cat.raw.get("picks") or [])
    await channels["trade-block"].send(
        "**Trade Block**\nSame calculator as ballkeep.com/trade.html\n"
        "Use `/trade` with two comma-separated sides.\n\n"
        f"**Future picks (Superflex curve)**\n{picks}"
    )

    await _wipe(channels["recent-deals"])
    deals = cat.raw.get("deals") or []
    await channels["recent-deals"].send(
        f"**Recent deals** · {len(deals)} packages on the desk tape.\n"
        "Search this channel for a name, or `/deals JSN` anywhere.\n"
        "https://ballkeep.com/recent-trades.html"
    )
    for d in deals:
        a = ", ".join(x["name"] for x in d.get("a") or [])
        b = ", ".join(x["name"] for x in d.get("b") or [])
        tag = "asking" if d.get("kind") == "asking" else "closed"
        await channels["recent-deals"].send(
            f"**{d.get('date')} · {d.get('format')} · {d.get('label')}** ({tag})\n"
            f"A: {a} · `{int(d.get('total_a') or 0):,}`\n"
            f"B: {b} · `{int(d.get('total_b') or 0):,}`\n"
            f"{d.get('blurb') or ''}"
        )
        await asyncio.sleep(1.05)
    await note("Recent deals posted.")

    await _wipe(channels["tape"])
    clips = [p for p in cat.players if p.get("youtube_id")]
    await channels["tape"].send(f"**Tape drawer** · {len(clips)} clips from player pages.")
    for group in _chunks(clips, 15):
        lines = []
        for p in group:
            lines.append(f"**{p['name']}** - {p.get('youtube_title') or 'highlight'} - https://www.youtube.com/watch?v={p['youtube_id']}")
        await channels["tape"].send("\n".join(lines))
        await asyncio.sleep(1.05)
    await note("Tape posted.")

    await _wipe(channels["nfl-slate"])
    by_week = {}
    for g in cat.raw.get("nfl") or []:
        by_week.setdefault(g.get("week"), []).append(g)
    await channels["nfl-slate"].send(
        f"**NFL 2026 slate** · {len(cat.raw.get('nfl') or [])} games · {len(by_week)} weeks.\n"
        "Search a team name in this channel, or `/nfl team:BUF`."
    )
    for week in sorted(k for k in by_week if k is not None):
        rows = by_week[week]
        for i, group in enumerate(_chunks(rows, 16)):
            body = "\n".join(
                f"W{g['week']} {g.get('day','')} · **{g.get('away')} {g.get('prep','at')} {g.get('home')}** · {g.get('time')} {g.get('tv','')}"
                for g in group
            )
            title = f"**NFL Week {week}**" if i == 0 else f"**NFL Week {week}** (cont.)"
            await channels["nfl-slate"].send(f"{title}\n{body}")
            await asyncio.sleep(0.9)
    await channels["nfl-slate"].send("Full slate: https://ballkeep.com/nfl-schedule.html")
    await note("NFL slate posted.")

    await _wipe(channels["mlb-slate"])
    mlb = cat.raw.get("mlb") or []
    await channels["mlb-slate"].send(
        f"**MLB September** · {len(mlb)} games in the catalog.\n"
        "Filter live with `/mlb yankees` · site: https://ballkeep.com/mlb-schedule.html"
    )
    by_day = {}
    for g in mlb:
        by_day.setdefault(g.get("day") or "TBD", []).append(g)
    for day in list(by_day)[:40]:
        rows = by_day[day]
        body = "\n".join(f"**{g.get('away')} @ {g.get('home')}** · {g.get('time')}" for g in rows)
        await channels["mlb-slate"].send(f"**{day}**\n{body[:1800]}")
        await asyncio.sleep(0.85)
    await note("MLB slate posted.")

    await _wipe(channels["sources"])
    src = cat.raw.get("sources") or []
    await channels["sources"].send(
        f"**Super Aggregate desks inside The Keep** · {cat.updated}\n"
        + "\n".join(f"• {s}" for s in src)
        + f"\n\n{cat.raw.get('algorithm') or ''}\n"
        "Long core is half the Super. Same desks, same numbers as ballkeep.com."
    )

    files = [p for p in cat.players if p.get("sport") != "baseball"]
    await _wipe(files_ch := channels["player-files"], limit=400)
    await files_ch.send(
        f"**Player files** · {len(files)} football names from The Keep 400, redraft, rookies, and Hot/Cold.\n"
        "Each message is a searchable file. `/player` is faster if you already know the name. "
        "Baseball files live on ballkeep.com/bb and `/bbplayer`."
        " PitchKeep files live on ballkeep.com/pl and `/plplayer`."
    )
    for p in files:
        lists = p.get("lists") or {}
        chips = " · ".join(f"{k} #{v}" for k, v in lists.items())
        plus = "; ".join(p.get("plus") or [])[:400]
        minus = "; ".join(p.get("minus") or [])[:400]
        yt = f"https://www.youtube.com/watch?v={p['youtube_id']}" if p.get("youtube_id") else "no clip yet"
        graf = (p.get("grafs") or ["See the site file."])[0][:500]
        msg = (
            f"**{p['name']}** · {p.get('pos')} {p.get('team')} · {p.get('url')}\n"
            f"{chips}\n"
            f"Plus: {plus or '-'}\n"
            f"Minus: {minus or '-'}\n"
            f"{graf}\n"
            f"Tape: {yt}"
        )
        await files_ch.send(msg[:1900])
        await asyncio.sleep(1.05)

    await _wipe(channels["bb-keep"])
    await _post_list(
        channels["bb-keep"],
        "BaseBallKeep - The Keep (dynasty 300)",
        cat.raw.get("bb_keep") or [],
        cat,
        "23-board baseball aggregate. Navy desk at https://ballkeep.com/bb/the-keep.html",
    )
    await _wipe(channels["bb-lineup"])
    await _post_list(channels["bb-lineup"], "The Lineup - dynasty hitters", cat.raw.get("bb_lineup") or [], cat)
    await _wipe(channels["bb-pitchers"])
    await _post_list(channels["bb-pitchers"], "BK's Pitchers - top 100", cat.raw.get("bb_pitchers") or [], cat)
    await _wipe(channels["bb-bullpen"])
    await channels["bb-bullpen"].send("**BK's Bullpen** · Saves first, then SV+H. Different sport.")
    await _post_list(channels["bb-bullpen"], "Saves", cat.raw.get("bb_saves") or [], cat)
    await _post_list(channels["bb-bullpen"], "Saves + Holds", cat.raw.get("bb_svh") or [], cat)
    await _wipe(channels["bb-redraft"])
    await _post_list(channels["bb-redraft"], "Baseball redraft ROS", cat.raw.get("bb_redraft") or [], cat)
    await _wipe(channels["bb-waivers"])
    dyn = "\n".join(
        f"**P{x['pri']}. {x['name']}** ({x.get('pos')} {x.get('team')}) - {x.get('why')}"
        for x in (cat.raw.get("bb_waivers_dynasty") or [])
    )
    await channels["bb-waivers"].send(f"**Dynasty wire** (short on purpose)\n{dyn[:1900]}")
    for i, chunk in enumerate(_chunks(cat.raw.get("bb_waivers_redraft") or [], 12)):
        body = "\n".join(
            f"**P{x['pri']}. {x['name']}** ({x.get('pos')} {x.get('team')}) - {x.get('why')}"
            for x in chunk
        )
        title = "**Redraft wire** (longer, higher priority)" if i == 0 else "**Redraft wire** (cont.)"
        await channels["bb-waivers"].send(f"{title}\n{body[:1900]}")
        await asyncio.sleep(1.05)
    await note("BaseBallKeep boards posted.")

    await _wipe(channels["the-premier"])
    await _post_list(
        channels["the-premier"],
        "PitchKeep - The Premier (hybrid 400: 50% Sleeper BPL 2025, 50% every other board)",
        cat.raw.get("pl_premier") or [],
        cat,
        "The Premier. 50% Sleeper, 50% the other boards. https://ballkeep.com/pl/the-premier.html",
    )
    await _wipe(channels["the-pitch"])
    await _post_list(
        channels["the-pitch"],
        "PitchKeep - The Pitch (Premier League top 400, Sleeper BPL 2025)",
        cat.raw.get("pl_pitch") or [],
        cat,
        "Sleeper-only counting board. Purple desk at https://ballkeep.com/pl/the-pitch.html",
    )
    await _wipe(channels["pl-attack"])
    await _post_list(channels["pl-attack"], "Attack - forwards", cat.raw.get("pl_fwd") or [], cat)
    await _wipe(channels["pl-midfield"])
    await _post_list(channels["pl-midfield"], "Midfield", cat.raw.get("pl_mid") or [], cat)
    await _wipe(channels["pl-defence"])
    await _post_list(channels["pl-defence"], "Defence", cat.raw.get("pl_def") or [], cat)
    await _wipe(channels["pl-keepers"])
    await _post_list(channels["pl-keepers"], "Keepers", cat.raw.get("pl_gkp") or [], cat)
    pl_files = cat.raw.get("pl_players") or []
    await _wipe(channels["pl-files"], limit=400)
    await channels["pl-files"].send(
        f"**PitchKeep player files** · {len(pl_files)} names from The Premier 400.\n"
        "`/plplayer Haaland` is faster if you already know the name. "
        "Site files live at https://ballkeep.com/pl/players/"
    )
    for p in pl_files:
        lists = p.get("lists") or {}
        chips = " · ".join(f"{k} #{v}" for k, v in lists.items())
        plus = "; ".join(p.get("plus") or [])[:400]
        minus = "; ".join(p.get("minus") or [])[:400]
        yt = f"https://www.youtube.com/watch?v={p['youtube_id']}" if p.get("youtube_id") else "no clip yet"
        graf = (p.get("grafs") or ["See the site file."])[0][:500]
        msg = (
            f"**{p['name']}** · {p.get('pos')} {p.get('team')} · {p.get('url')}\n"
            f"{chips}\n"
            f"Plus: {plus or '-'}\n"
            f"Minus: {minus or '-'}\n"
            f"{graf}\n"
            f"Tape: {yt}"
        )
        await channels["pl-files"].send(msg[:1900])
        await asyncio.sleep(1.05)
    await note("PitchKeep boards posted. Desk is live.")
    return channels
