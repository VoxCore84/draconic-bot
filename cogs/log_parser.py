"""Parses uploaded .conf and .log files — local analysis + optional AI summary.

v3: After local pattern matching, can optionally send parsed findings to Gemini
for a more detailed summary. AI summary is additive — local parsing always runs first.
"""

import logging
import re

import discord
from discord.ext import commands
from config import SUPPORT_CHANNEL_IDS
from emojis import em
from ai.schemas import RouteType

log = logging.getLogger(__name__)


class LogParser(commands.Cog):
    """Parses uploaded .conf and .log files to help users automatically."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _get_router(self):
        return getattr(self.bot, "ai_router", None)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return

        if SUPPORT_CHANNEL_IDS and message.channel.id not in SUPPORT_CHANNEL_IDS:
            return

        for attachment in message.attachments:
            fname = attachment.filename.lower()
            if fname == "worldserver.conf":
                await self.parse_config(message, attachment)
                return
            elif fname in ("server.log", "crash.log", "crash.txt", "dberrors.log"):
                await self.parse_log(message, attachment)
                return

    async def parse_config(self, message: discord.Message, attachment: discord.Attachment):
        """Validates worldserver.conf for common beginner mistakes."""
        file_bytes = await attachment.read()
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return

        errors = []

        if 'DataDir = "."' not in content and "DataDir = '.'" not in content:
            datadir_match = re.search(r"^DataDir\s*=\s*([^\n]+)", content, re.MULTILINE)
            if datadir_match:
                errors.append(
                    f"**Maps Folder (`DataDir`)**: Yours is set to `{datadir_match.group(1)}`. "
                    'Unless you know exactly what you are doing, set it to `DataDir = "."`.'
                )

        if "127.0.0.1;3306;trinity;trinity" in content:
            errors.append(
                "**Database Password**: Using default TrinityCore password. "
                "If using UniServerZ, change to `127.0.0.1;3306;root;admin;auth` (and world/characters)."
            )

        if errors:
            icon = em("page", "\U0001f4c4")
            desc = (
                f"Hey {message.author.mention}, I checked your config and found some issues:\n\n"
                + "\n\n".join(errors)
            )

            # Optional AI summary for richer advice
            router = self._get_router()
            if router and router.enabled:
                ai_context = f"Config file analysis found these issues:\n" + "\n".join(errors)
                ai_context += f"\n\nFull config excerpt (first 2000 chars):\n{content[:2000]}"
                result = await router.handle_admin_test(RouteType.LOG_SUMMARY, ai_context)
                if result and result.answer_markdown and result.confidence >= 0.70:
                    desc += f"\n\n**AI Analysis:**\n{result.answer_markdown}"

            embed = discord.Embed(
                title=f"{icon} Config File Review",
                description=desc[:4000],
                color=discord.Color.yellow(),
            )
            await message.reply(embed=embed)
        else:
            await message.add_reaction("\u2705")

    async def parse_log(self, message: discord.Message, attachment: discord.Attachment):
        """Analyzes Server.log / crash logs for known error patterns."""
        file_bytes = await attachment.read()
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return

        findings = []

        # Pattern matching for known crashes
        if "Could not connect to MySQL" in content or ("DatabasePool" in content and "NOT opened" in content):
            findings.append(
                "**Database Connection Failed!** "
                "MySQL isn't running or the server can't connect. "
                "Start MySQL (UniServerZ green button) and check port 3306."
            )

        if "Assertion failed" in content and ("InitMap" in content or "GridMap" in content):
            findings.append(
                "**Missing Map Files!** "
                "Run the 4 extractors in your WoW _retail_ folder and copy maps/vmaps/mmaps to server dir."
            )
        elif "Map file" in content and "does not exist" in content:
            findings.append(
                "**Missing Map Files!** "
                "Map data is missing. Extract maps from your WoW client."
            )

        if "Missing auth seed" in content or "Client build" in content:
            findings.append(
                "**Build Mismatch!** "
                "Your WoW client updated. Apply the latest auth SQL update and restart."
            )

        if "bind failed" in content or "Address already in use" in content:
            findings.append(
                "**Port In Use!** "
                "Another server or program is using the port. Close duplicate instances."
            )

        if findings:
            icon = em("mag", "\U0001f50d")
            desc = f"Hey {message.author.mention}, I found these issues in your log:\n\n"
            desc += "\n\n".join(f"\u2022 {f}" for f in findings)

            # Optional AI summary
            router = self._get_router()
            if router and router.enabled:
                # Send parsed findings + raw excerpt for AI to summarize
                ai_context = "Log analysis found:\n" + "\n".join(findings)
                # Include some raw log context (last 2000 chars or around error lines)
                ai_context += f"\n\nRaw log excerpt (last 2000 chars):\n{content[-2000:]}"
                result = await router.handle_admin_test(RouteType.LOG_SUMMARY, ai_context)
                if result and result.answer_markdown and result.confidence >= 0.70:
                    desc += f"\n\n**AI Summary:**\n{result.answer_markdown}"

            embed = discord.Embed(
                title=f"{icon} Log Analysis",
                description=desc[:4000],
                color=discord.Color.red(),
            )
            await message.reply(embed=embed)
        else:
            # No known patterns — if AI is enabled, try a general summary
            router = self._get_router()
            if router and router.enabled and len(content) > 100:
                ai_context = f"User uploaded a log file ({attachment.filename}). No known error patterns matched. Raw content (last 3000 chars):\n{content[-3000:]}"
                result = await router.handle_admin_test(RouteType.LOG_SUMMARY, ai_context)
                if result and result.answer_markdown and result.confidence >= 0.70:
                    icon = em("mag", "\U0001f50d")
                    embed = discord.Embed(
                        title=f"{icon} AI Log Analysis",
                        description=f"Hey {message.author.mention}, I didn't find any obvious known issues, but here's what the AI noticed:\n\n{result.answer_markdown}",
                        color=discord.Color.orange(),
                    )
                    await message.reply(embed=embed)
                    return

            await message.add_reaction("\U0001f440")  # Eyes: looked but nothing obvious


async def setup(bot: commands.Bot):
    await bot.add_cog(LogParser(bot))
