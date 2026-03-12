"""FAQ auto-responder — pattern-matches support questions and replies with varied responses.

Smart gating prevents over-firing:
  - Only responds to messages that look like questions or help requests
  - Ignores replies (user is already in a conversation)
  - Ignores threads (someone is already helping)
  - Global per-channel rate limit (max 2 bot responses per 3 minutes)
  - Per-FAQ cooldown (same FAQ won't fire twice in 5 minutes per channel)

Response variety:
  - Each FAQ has 3 answer variants (concise, friendly, diagnostic)
  - Random opener + variant + closer = 500+ combos per FAQ entry
"""

import json
import logging
import re
import time
from collections import Counter
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from config import SUPPORT_CHANNEL_IDS, GITHUB_REPO, GITHUB_AUTH_SQL_PATH
from emojis import em
from response_pool import pick_response

log = logging.getLogger(__name__)

_FAQ_PATH = Path(__file__).parent.parent / "data" / "faq_responses.json"
_STATS_PATH = Path(__file__).parent.parent / "data" / "faq_stats.json"

# Signals that a message is a question or help request (not casual chat)
_QUESTION_SIGNALS = re.compile(
    r"(?:^|\b)(?:how|what|where|why|when|can|do|does|is|should|would|could|any(?:one|body))\b"
    r"|[?]"
    r"|(?:help|stuck|confused|lost|broken|issue|problem|error|fix|trouble|wrong|crash|fail|please|need)"
    r"|(?:i\s*(?:can.?t|cannot|don.?t|am\s*(?:not|unable)))",
    re.IGNORECASE,
)

# Global rate limit: max responses per channel in a time window
_GLOBAL_RATE_LIMIT = 2       # max bot responses
_GLOBAL_RATE_WINDOW = 180    # per 3 minutes
_FAQ_COOLDOWN_SECS = 300     # per-FAQ cooldown (5 min)


def _load_faq() -> list[dict]:
    with open(_FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_stats() -> Counter:
    try:
        with open(_STATS_PATH, "r", encoding="utf-8") as f:
            return Counter(json.load(f))
    except Exception:
        return Counter()


def _save_stats(stats: Counter):
    _STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(dict(stats), f, indent=2)


class FAQResponder(commands.Cog):
    """Watches support channels and auto-answers common questions with varied responses."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.faq_entries = _load_faq()
        for entry in self.faq_entries:
            entry["_compiled"] = re.compile(entry["pattern"], re.IGNORECASE)
            # Support both old "response" (string) and new "responses" (list) format
            if "responses" not in entry:
                entry["responses"] = [entry.get("response", "")]
        # Per-FAQ cooldown: (channel_id, faq_id) -> last trigger timestamp
        self._cooldowns: dict[tuple[int, str], float] = {}
        # Global channel rate: channel_id -> list of timestamps
        self._channel_timestamps: dict[int, list[float]] = {}
        self._stats: Counter = _load_stats()
        log.info("FAQResponder loaded %d FAQ entries", len(self.faq_entries))

    def _check_faq_cooldown(self, channel_id: int, faq_id: str, now: float) -> bool:
        """Returns True if this specific FAQ can fire (not on cooldown)."""
        key = (channel_id, faq_id)
        last = self._cooldowns.get(key, 0)
        if now - last < _FAQ_COOLDOWN_SECS:
            return False
        self._cooldowns[key] = now
        return True

    def _check_global_rate(self, channel_id: int, now: float) -> bool:
        """Returns True if we haven't hit the global rate limit for this channel."""
        timestamps = self._channel_timestamps.get(channel_id, [])
        # Prune old timestamps
        timestamps = [t for t in timestamps if now - t < _GLOBAL_RATE_WINDOW]
        self._channel_timestamps[channel_id] = timestamps
        if len(timestamps) >= _GLOBAL_RATE_LIMIT:
            return False
        timestamps.append(now)
        return True

    @staticmethod
    def _looks_like_question(content: str) -> bool:
        """Check if the message looks like a question or help request, not casual chat."""
        # Must have at least 5 words
        if len(content.split()) < 5:
            return False
        return bool(_QUESTION_SIGNALS.search(content))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots, DMs
        if message.author.bot or not message.guild:
            return

        # Only respond in configured support channels
        if SUPPORT_CHANNEL_IDS and message.channel.id not in SUPPORT_CHANNEL_IDS:
            return

        # Don't interrupt threads — someone is already helping
        if isinstance(message.channel, discord.Thread):
            return

        # Don't interrupt replies — user is in a conversation
        if message.reference is not None:
            return

        content = message.content
        if len(content) < 10:
            return

        # Must look like a question or help request
        if not self._looks_like_question(content):
            return

        now = time.time()

        # Check global rate limit first
        if not self._check_global_rate(message.channel.id, now):
            return

        for entry in self.faq_entries:
            if entry["_compiled"].search(content):
                faq_id = entry["id"]
                if not self._check_faq_cooldown(message.channel.id, faq_id, now):
                    continue

                # Build a varied response
                opener, core_answer, closer = pick_response(
                    entry["responses"], entry["title"]
                )

                emoji = em("faq", "\u2753")
                embed = discord.Embed(
                    description=f"{opener}\n\n{core_answer}",
                    color=discord.Color.blue(),
                )
                embed.set_footer(text=f"*{closer}*")

                view = discord.ui.View(timeout=120)

                async def launch_dm_callback(interaction: discord.Interaction):
                    await interaction.response.send_message(
                        "I've sent you a DM! Let's figure this out together.",
                        ephemeral=True,
                    )
                    try:
                        dm_cog = self.bot.get_cog("DMGuide")
                        if dm_cog:
                            dm_channel = await interaction.user.create_dm()
                            from cogs.dm_guide import DMStepView, SETUP_STEPS

                            step_data = SETUP_STEPS[0]
                            icon = em("robot", "\U0001f916")
                            dm_embed = discord.Embed(
                                title=f"{icon} {step_data['title']}",
                                description=step_data["desc"],
                                color=discord.Color.blue(),
                            )
                            await dm_channel.send(embed=dm_embed, view=DMStepView(0))
                    except discord.Forbidden:
                        await interaction.followup.send(
                            "I tried to DM you, but your privacy settings are blocking DMs!",
                            ephemeral=True,
                        )

                btn = discord.ui.Button(
                    label="Still stuck? Help me!",
                    emoji="\U0001f198",
                    style=discord.ButtonStyle.danger,
                    custom_id="launch_dm_troubleshooter_faq",
                )
                btn.callback = launch_dm_callback
                view.add_item(btn)

                await message.reply(embed=embed, view=view, mention_author=False)
                self._stats[faq_id] += 1
                _save_stats(self._stats)
                log.info(
                    "FAQ '%s' triggered by %s in #%s (total: %d)",
                    faq_id, message.author, message.channel, self._stats[faq_id],
                )
                return  # Only one FAQ per message

    @app_commands.command(
        name="faqstats",
        description="Show which FAQ topics trigger most often (admin only)",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def faq_stats(self, interaction: discord.Interaction):
        if not self._stats:
            await interaction.response.send_message(
                "No FAQ stats yet.", ephemeral=True
            )
            return

        title_map = {e["id"]: e["title"] for e in self.faq_entries}
        lines = []
        total = sum(self._stats.values())
        for faq_id, count in self._stats.most_common():
            title = title_map.get(faq_id, faq_id)
            pct = count / total * 100 if total else 0
            lines.append(f"**{count}x** -- {title} ({pct:.0f}%)")

        icon = em("faq", "\u2753")
        embed = discord.Embed(
            title=f"{icon} FAQ Trigger Stats",
            description="\n".join(lines) + f"\n\n**Total triggers:** {total}",
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Stats persist across bot restarts")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FAQResponder(bot))
