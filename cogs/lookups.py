"""Slash commands for looking up spells, items, creatures, areas, factions via Wowhead."""

import discord
import urllib.parse
from discord import app_commands
from discord.ext import commands
from emojis import em

WOWHEAD_BASE = "https://www.wowhead.com"


def _wowhead_url(entity_type: str, query: str) -> tuple[str, bool]:
    """Build a Wowhead URL. Returns (url, is_direct_id)."""
    if query.strip().isdigit():
        return f"{WOWHEAD_BASE}/{entity_type}={query.strip()}", True
    else:
        # Wowhead search URL
        safe_query = urllib.parse.quote_plus(query.strip())
        return f"{WOWHEAD_BASE}/search?q={safe_query}", False


class Lookups(commands.Cog):
    """Slash commands for game data lookups via Wowhead."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="spell", description="Look up a spell on Wowhead by ID or name")
    @app_commands.describe(query="Spell ID or name to search for")
    @app_commands.checks.cooldown(5, 30.0, key=lambda i: i.user.id)
    async def spell_lookup(self, interaction: discord.Interaction, query: str):
        url, is_id = _wowhead_url("spell", query)
        if is_id:
            desc = f"**Spell {query}**: [{query}]({url})"
        else:
            desc = f"**Search results for** \"{query}\":\n[View on Wowhead]({url})"
        embed = discord.Embed(
            title=f"{em('spell', chr(0x26a1))} Spell Lookup",
            description=desc,
            color=discord.Color.purple(),
        )
        embed.set_footer(text=f"{em('lookup', chr(0x1f50d))} Source: Wowhead")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="item", description="Look up an item on Wowhead by ID or name")
    @app_commands.describe(query="Item ID or name to search for")
    @app_commands.checks.cooldown(5, 30.0, key=lambda i: i.user.id)
    async def item_lookup(self, interaction: discord.Interaction, query: str):
        url, is_id = _wowhead_url("item", query)
        if is_id:
            desc = f"**Item {query}**: [{query}]({url})"
        else:
            desc = f"**Search results for** \"{query}\":\n[View on Wowhead]({url})"
        embed = discord.Embed(
            title=f"{em('item', chr(0x1f6e1) + chr(0xfe0f))} Item Lookup",
            description=desc,
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"{em('lookup', chr(0x1f50d))} Source: Wowhead")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="creature", description="Look up a creature/NPC on Wowhead by ID or name")
    @app_commands.describe(query="Creature/NPC ID or name to search for")
    @app_commands.checks.cooldown(5, 30.0, key=lambda i: i.user.id)
    async def creature_lookup(self, interaction: discord.Interaction, query: str):
        url, is_id = _wowhead_url("npc", query)
        if is_id:
            desc = f"**NPC {query}**: [{query}]({url})"
        else:
            desc = f"**Search results for** \"{query}\":\n[View on Wowhead]({url})"
        embed = discord.Embed(
            title=f"{em('dragon', chr(0x1f409))} Creature Lookup",
            description=desc,
            color=discord.Color.orange(),
        )
        embed.set_footer(text=f"{em('lookup', chr(0x1f50d))} Source: Wowhead")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="area", description="Look up a zone/area on Wowhead by ID or name")
    @app_commands.describe(query="Area/zone ID or name to search for")
    @app_commands.checks.cooldown(5, 30.0, key=lambda i: i.user.id)
    async def area_lookup(self, interaction: discord.Interaction, query: str):
        if query.strip().isdigit():
            url = f"{WOWHEAD_BASE}/zone={query.strip()}"
            desc = f"**Zone {query}**: [{query}]({url})"
        else:
            safe_query = urllib.parse.quote_plus(query.strip())
            url = f"{WOWHEAD_BASE}/search?q={safe_query}"
            desc = f"**Search results for** \"{query}\":\n[View on Wowhead]({url})"
        embed = discord.Embed(
            title=f"{em('cat_zones', chr(0x1f5fa) + chr(0xfe0f))} Area Lookup",
            description=desc,
            color=discord.Color.teal(),
        )
        embed.set_footer(text=f"{em('lookup', chr(0x1f50d))} Source: Wowhead")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="faction", description="Look up a faction on Wowhead by ID or name")
    @app_commands.describe(query="Faction ID or name to search for")
    @app_commands.checks.cooldown(5, 30.0, key=lambda i: i.user.id)
    async def faction_lookup(self, interaction: discord.Interaction, query: str):
        url, is_id = _wowhead_url("faction", query)
        if is_id:
            desc = f"**Faction {query}**: [{query}]({url})"
        else:
            desc = f"**Search results for** \"{query}\":\n[View on Wowhead]({url})"
        embed = discord.Embed(
            title=f"{em('cat_factions', chr(0x2694) + chr(0xfe0f))} Faction Lookup",
            description=desc,
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"{em('lookup', chr(0x1f50d))} Source: Wowhead")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Lookups(bot))
