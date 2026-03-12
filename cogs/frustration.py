"""Detects frustrated users and offers AI-powered empathetic help.

v3: Uses Gemini to generate contextual empathetic responses when AI is enabled.
Falls back to random static openers when AI is disabled.

Smart gating:
  - Per-user cooldown (won't re-trigger for same user within 30 minutes)
  - Per-channel cooldown (max once per 5 minutes per channel)
  - Ignores threads and replies
  - Requires minimum message length
"""

import random
import re
import time

import discord
from discord.ext import commands
from config import SUPPORT_CHANNEL_IDS
from emojis import em
from ai.schemas import RouteType

FRUSTRATION_PATTERN = re.compile(
    r"(i.?m so|i.?m really|very|super)?\s*(confused|frustrated|lost|giving up|give up|about to quit)|"
    r"(this is|it.?s)\s*(too hard|too difficult|impossible|make no sense|make any sense)|"
    r"(i don.?t|i cannot|i can.?t)\s*(understand|figure this out|get this to work)|"
    r"i.?ve been trying for (hours|days|a long time)|"
    r"can someone (just )?(please )?(help|explain|hold my hand)",
    re.IGNORECASE,
)

_USER_COOLDOWN = 1800
_CHANNEL_COOLDOWN = 300

# Static fallback openers
_EMPATHY_OPENERS = [
    "Setting up a private server for the first time is definitely tricky, and it's totally normal to feel stuck. There are a lot of moving parts.",
    "Private server setup has a LOT of steps, and it's really common to hit a wall. You're not alone in this.",
    "This stuff can be genuinely confusing — even experienced people struggle with the setup sometimes.",
    "Don't worry, almost everyone gets stuck at some point during setup. That's what this channel is for.",
    "It sounds like you're having a rough time. The good news is most issues have a straightforward fix once you know where to look.",
    "I get it — there are so many things that can go wrong. Let's see if we can narrow it down.",
    "Take a breath! Most of the time it's one small thing that's off. Let me try to help.",
]

_OFFER_TEXT = (
    "If you'd like, I can walk you through finding the problem step-by-step in your DMs, "
    "so you don't have to figure it all out at once."
)


class Frustration(commands.Cog):
    """Detects when a user is frustrated and offers guided help."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._user_cooldowns: dict[int, float] = {}
        self._channel_cooldowns: dict[int, float] = {}

    def _get_router(self):
        return getattr(self.bot, "ai_router", None)

    def _check_cooldowns(self, user_id: int, channel_id: int, now: float) -> bool:
        last_user = self._user_cooldowns.get(user_id, 0)
        if now - last_user < _USER_COOLDOWN:
            return False
        last_channel = self._channel_cooldowns.get(channel_id, 0)
        if now - last_channel < _CHANNEL_COOLDOWN:
            return False
        self._user_cooldowns[user_id] = now
        self._channel_cooldowns[channel_id] = now
        return True

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if SUPPORT_CHANNEL_IDS and message.channel.id not in SUPPORT_CHANNEL_IDS:
            return

        if isinstance(message.channel, discord.Thread):
            return
        if message.reference is not None:
            return

        if len(message.content.split()) < 6:
            return

        if not FRUSTRATION_PATTERN.search(message.content):
            return

        now = time.time()
        if not self._check_cooldowns(message.author.id, message.channel.id, now):
            return

        # Try AI-powered empathetic response
        router = self._get_router()
        if router and router.enabled:
            result = await router.handle_message(
                message, force_route=RouteType.FRUSTRATION
            )
            if result and result.answer_markdown and not result.needs_staff:
                icon = em("lifesaver", "\U0001f6df")
                embed = discord.Embed(
                    title=f"{icon} Need a hand?",
                    description=f"Hi {message.author.mention}, {result.answer_markdown}",
                    color=discord.Color.brand_green(),
                )
                if result.follow_up_question:
                    embed.set_footer(text=result.follow_up_question)
                else:
                    embed.set_footer(text="Click the button below to start a private troubleshooting session.")
                await self._send_with_dm_button(message, embed)
                return

        # Static fallback
        empathy = random.choice(_EMPATHY_OPENERS)
        icon = em("lifesaver", "\U0001f6df")
        embed = discord.Embed(
            title=f"{icon} Need a hand?",
            description=f"Hi {message.author.mention}, {empathy.lower()}\n\n{_OFFER_TEXT}",
            color=discord.Color.brand_green(),
        )
        embed.set_footer(text="Click the button below to start a private troubleshooting session.")
        await self._send_with_dm_button(message, embed)

    async def _send_with_dm_button(self, message: discord.Message, embed: discord.Embed):
        view = discord.ui.View(timeout=120)

        async def launch_dm_guide(interaction: discord.Interaction):
            await interaction.response.send_message(
                "I've sent you a DM! Let's figure this out together.",
                ephemeral=True,
            )
            try:
                dm_channel = await interaction.user.create_dm()
                from cogs.dm_guide import DMStepView, SETUP_STEPS
                step_data = SETUP_STEPS[0]
                icon_dm = em("robot", "\U0001f916")
                dm_embed = discord.Embed(
                    title=f"{icon_dm} {step_data['title']}",
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
            label="Help me step-by-step",
            emoji="\U0001f91d",
            style=discord.ButtonStyle.success,
            custom_id="launch_dm_troubleshooter",
        )
        btn.callback = launch_dm_guide
        view.add_item(btn)

        await message.reply(embed=embed, view=view, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Frustration(bot))
