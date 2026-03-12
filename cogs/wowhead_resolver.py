"""Wowhead link resolver — auto-detects wowhead URLs and embeds a clean preview.

Rate-limited: max 1 resolution per channel per 2 minutes to avoid noise.
"""

import logging
import time

import discord
from discord.ext import commands

from config import SUPPORT_CHANNEL_IDS, CHANNEL_BUGREPORT
from wowhead import extract_wowhead_links
from emojis import em

log = logging.getLogger(__name__)

_CHANNEL_COOLDOWN = 120  # seconds

ENTITY_LABELS = {
    "spell": "Spell",
    "item": "Item",
    "npc": "NPC",
    "quest": "Quest",
    "object": "Object",
    "achievement": "Achievement",
    "zone": "Zone",
}


class WowheadResolver(commands.Cog):
    """Auto-detects wowhead.com links and embeds a clean summary."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._channel_cooldowns: dict[int, float] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Only resolve in support/bug channels
        target_channels = SUPPORT_CHANNEL_IDS | ({CHANNEL_BUGREPORT} if CHANNEL_BUGREPORT else set())
        if target_channels and message.channel.id not in target_channels:
            return

        # Don't resolve in threads (keeps thread noise down)
        if isinstance(message.channel, discord.Thread):
            return

        links = extract_wowhead_links(message.content)
        if not links:
            return

        # Per-channel cooldown
        now = time.time()
        last = self._channel_cooldowns.get(message.channel.id, 0)
        if now - last < _CHANNEL_COOLDOWN:
            return
        self._channel_cooldowns[message.channel.id] = now

        # Limit to 3 links per message to avoid spam
        links = links[:3]
        lines = []

        for entity_type, entity_id in links:
            label = ENTITY_LABELS.get(entity_type, entity_type.title())
            icon = em("lookup", "\U0001f50d")
            url = f"https://www.wowhead.com/{entity_type}={entity_id}"
            lines.append(f"{icon} **{label}** `{entity_id}` -- [View on Wowhead]({url})")

        if not lines:
            return

        embed = discord.Embed(
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"{em('watch', chr(0x1f441) + chr(0xfe0f))} Wowhead link detected")
        await message.reply(embed=embed, mention_author=False)
        log.info("Resolved %d wowhead links for %s", len(lines), message.author)


async def setup(bot: commands.Bot):
    await bot.add_cog(WowheadResolver(bot))
