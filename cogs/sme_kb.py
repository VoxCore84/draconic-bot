"""SME Knowledge Base — GM command lookups with AI-powered answers.

v3: When AI is enabled, uses Gemini + knowledge base for richer GM command answers.
Falls back to static JSON search when AI is disabled.
"""

import json
import logging
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands
from ai.schemas import RouteType

log = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"


class SMEKnowledgeBase(commands.Cog):
    """GM command knowledge base with optional AI-powered answers."""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = _DATA_DIR / "gm_commands.json"
        self.kb = self._load_kb()

    def _get_router(self):
        return getattr(self.bot, "ai_router", None)

    def _load_kb(self):
        if not self.db_path.exists():
            return []
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("gm_commands", [])

    @app_commands.command(name="gmcommand", description="Ask DraconicBot what a GM command does!")
    @app_commands.describe(query="The command name (e.g. '.additem' or 'teleport')")
    async def gm_command(self, interaction: discord.Interaction, query: str):
        """Searches for GM command info — AI-powered when available, static fallback otherwise."""

        query_word = query.lower().strip()

        # Try AI path first
        router = self._get_router()
        if router and router.enabled:
            await interaction.response.defer()
            result = await router.handle_admin_test(RouteType.GM_KB, f"GM command: {query}")
            if result and result.answer_markdown and result.confidence >= 0.70:
                embed = discord.Embed(
                    title="\U0001f4da GM Command Help",
                    description=result.answer_markdown,
                    color=discord.Color.gold(),
                )
                if result.confidence < 0.85:
                    embed.set_footer(text="AI-powered answer \u2014 verify with the wiki for exact syntax")
                else:
                    embed.set_footer(text="AI-powered answer")
                await interaction.followup.send(embed=embed)
                return

        # Static fallback
        if interaction.response.is_done():
            send = interaction.followup.send
        else:
            await interaction.response.defer()
            send = interaction.followup.send

        matches = []
        for cmd in self.kb:
            if query_word in cmd["name"].lower() or query_word in cmd["description"].lower():
                matches.append(cmd)

        if not matches:
            await send(
                f"\u274c I don't know any GM command matching `{query}`.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="\U0001f4da GM Commands",
            color=discord.Color.gold(),
        )

        for cmd in matches[:3]:
            embed.add_field(
                name=cmd["name"],
                value=f"**Syntax:** `{cmd.get('syntax', cmd['name'])}`\n**Description:** {cmd['description']}",
                inline=False,
            )

        if len(matches) > 3:
            embed.set_footer(text=f"Found {len(matches) - 3} more matches. Try being more specific.")

        await send(embed=embed)


async def setup(bot):
    await bot.add_cog(SMEKnowledgeBase(bot))
