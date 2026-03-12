"""DraconicBot — main bot class."""

import logging
import time

import discord
from discord.ext import commands
from emojis import load_app_emojis
from config import (
    CHANNEL_TROUBLESHOOTING, CHANNEL_BUGREPORT, CHANNEL_TWW,
    CHANNEL_GENERAL, CHANNEL_ANNOUNCEMENTS, SUPPORT_CHANNEL_IDS,
)

log = logging.getLogger(__name__)

BOT_VERSION = "3.0.0"

COGS = [
    "cogs.help",
    "cogs.faq",
    "cogs.lookups",
    "cogs.triage",
    "cogs.troubleshooter",
    "cogs.frustration",
    "cogs.log_parser",
    "cogs.dm_guide",
    "cogs.diagnoser",
    "cogs.sme_kb",
    "cogs.watchdog",
    "cogs.changelog",
    "cogs.automod",
    "cogs.welcome_role",
    "cogs.about",
    "cogs.announce",
    "cogs.ai_admin",
]


class DraconicBot(commands.Bot):
    """DraconicWoW support bot with AI-powered FAQ, lookups, triage, and build monitoring."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )
        self.start_time = time.time()
        self.ai_router = None

    async def setup_hook(self):
        """Load all cogs, initialize AI router, and sync slash commands."""
        # Initialize AI router
        self._init_ai_router()

        for cog_path in COGS:
            try:
                await self.load_extension(cog_path)
                log.info("Loaded cog: %s", cog_path)
            except Exception:
                log.exception("Failed to load cog: %s", cog_path)

        synced = await self.tree.sync()
        log.info("Synced %d slash commands", len(synced))

    def _init_ai_router(self):
        """Initialize the AI router if AI is enabled."""
        from ai.settings import AI_ENABLED
        if AI_ENABLED:
            try:
                from ai.router import AIRouter
                self.ai_router = AIRouter()
                log.info("AI router initialized (enabled)")
            except Exception:
                log.exception("Failed to initialize AI router — AI features disabled")
                self.ai_router = None
        else:
            log.info("AI router not initialized (AI_ENABLED=false)")

    async def on_ready(self):
        log.info("Bot ready: %s (ID: %s)", self.user, self.user.id)
        log.info("Connected to %d guild(s)", len(self.guilds))

        await load_app_emojis(self)
        self._validate_config()

        ai_status = "enabled" if self.ai_router and self.ai_router.enabled else "disabled"
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"/help | AI {ai_status}",
            )
        )

    def _validate_config(self):
        channel_map = {
            "CHANNEL_TROUBLESHOOTING": CHANNEL_TROUBLESHOOTING,
            "CHANNEL_BUGREPORT": CHANNEL_BUGREPORT,
            "CHANNEL_TWW": CHANNEL_TWW,
            "CHANNEL_GENERAL": CHANNEL_GENERAL,
            "CHANNEL_ANNOUNCEMENTS": CHANNEL_ANNOUNCEMENTS,
        }
        missing = [name for name, cid in channel_map.items() if not cid]
        if missing:
            log.warning(
                "Unconfigured channels (set in .env): %s — some features will be disabled",
                ", ".join(missing),
            )
        if not SUPPORT_CHANNEL_IDS:
            log.warning("No support channels configured — FAQ and wowhead resolver will be inactive")

        # Validate AI config
        if self.ai_router:
            from ai.settings import AI_ALLOWED_CHANNEL_IDS
            if not AI_ALLOWED_CHANNEL_IDS:
                log.warning("AI_ALLOWED_CHANNEL_IDS not set — AI will respond in all support channels")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        log.exception("Command error in %s: %s", ctx.command, error)
