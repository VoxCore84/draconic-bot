"""AI admin commands — health, stats, toggle, reload, test."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from ai.schemas import RouteType

log = logging.getLogger(__name__)


class AIAdmin(commands.Cog):
    """Admin-only AI management commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _get_router(self):
        from ai.router import AIRouter
        return getattr(self.bot, "ai_router", None)

    @app_commands.command(name="ai_status", description="Show AI system status (admin only)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai_status(self, interaction: discord.Interaction):
        router = self._get_router()
        if not router:
            await interaction.response.send_message("AI router not initialized.", ephemeral=True)
            return

        health = await router.provider.healthcheck()
        daily_spend = router.metrics.get_daily_spend()
        monthly_spend = router.metrics.get_monthly_spend()
        kb_count = len(router.kb.get_all_sections())
        sessions = router.sessions.active_count

        from ai.settings import AI_DAILY_HARD_CAP_USD, AI_MONTHLY_SOFT_CAP_USD

        status_emoji = "\u2705" if router.enabled else "\u274c"
        health_emoji = "\u2705" if health.available else "\u274c"

        embed = discord.Embed(
            title="AI System Status",
            color=discord.Color.green() if router.enabled and health.available else discord.Color.red(),
        )
        embed.add_field(name="Enabled", value=f"{status_emoji} {router.enabled}", inline=True)
        embed.add_field(name="Provider", value=f"{health_emoji} Gemini ({'OK' if health.available else health.error})", inline=True)
        embed.add_field(name="Provider Latency", value=f"{health.latency_ms}ms", inline=True)
        embed.add_field(name="Daily Spend", value=f"${daily_spend:.4f} / ${AI_DAILY_HARD_CAP_USD:.2f}", inline=True)
        embed.add_field(name="Monthly Spend", value=f"${monthly_spend:.4f} / ${AI_MONTHLY_SOFT_CAP_USD:.2f}", inline=True)
        embed.add_field(name="KB Sections", value=str(kb_count), inline=True)
        embed.add_field(name="Active Sessions", value=str(sessions), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ai_stats", description="Show AI usage statistics (admin only)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai_stats(self, interaction: discord.Interaction):
        router = self._get_router()
        if not router:
            await interaction.response.send_message("AI router not initialized.", ephemeral=True)
            return

        stats_24h = router.metrics.get_stats_24h()
        stats_30d = router.metrics.get_stats_30d()
        route_breakdown = router.metrics.get_route_breakdown()

        embed = discord.Embed(title="AI Usage Statistics", color=discord.Color.blue())

        # 24h stats
        lines_24h = [
            f"**Requests:** {stats_24h['requests']}",
            f"**Spend:** ${stats_24h['spend_usd']:.4f}",
            f"**Avg Latency:** {stats_24h['avg_latency_ms']}ms",
            f"**Errors:** {stats_24h['errors']}",
            f"**Fallbacks:** {stats_24h['fallbacks']}",
            f"**Handoffs:** {stats_24h['handoffs']}",
        ]
        embed.add_field(name="Last 24 Hours", value="\n".join(lines_24h), inline=True)

        # 30d stats
        lines_30d = [
            f"**Requests:** {stats_30d['requests']}",
            f"**Spend:** ${stats_30d['spend_usd']:.4f}",
            f"**Avg Latency:** {stats_30d['avg_latency_ms']}ms",
            f"**Errors:** {stats_30d['errors']}",
        ]
        embed.add_field(name="Last 30 Days", value="\n".join(lines_30d), inline=True)

        # Route breakdown
        if route_breakdown:
            route_lines = [f"**{route}:** {count}" for route, count in sorted(route_breakdown.items())]
            embed.add_field(name="Today by Route", value="\n".join(route_lines), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ai_toggle", description="Enable or disable AI responses (admin only)")
    @app_commands.describe(state="on or off")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai_toggle(self, interaction: discord.Interaction, state: str):
        router = self._get_router()
        if not router:
            await interaction.response.send_message("AI router not initialized.", ephemeral=True)
            return

        enabled = state.lower() in ("on", "true", "enable", "yes", "1")
        router.toggle(enabled)
        emoji = "\u2705" if enabled else "\u274c"
        await interaction.response.send_message(
            f"{emoji} AI responses **{'enabled' if enabled else 'disabled'}**.",
            ephemeral=True,
        )

    @app_commands.command(name="ai_reload_kb", description="Reload the AI knowledge base (admin only)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai_reload_kb(self, interaction: discord.Interaction):
        router = self._get_router()
        if not router:
            await interaction.response.send_message("AI router not initialized.", ephemeral=True)
            return

        router.reload_kb()
        count = len(router.kb.get_all_sections())
        await interaction.response.send_message(
            f"\u2705 Knowledge base reloaded. **{count}** sections loaded.",
            ephemeral=True,
        )

    @app_commands.command(name="ai_test", description="Test AI response for a route (admin only)")
    @app_commands.describe(
        route="Route type: faq, troubleshoot, frustration, gm_kb, log_summary",
        text="Test prompt to send to AI",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai_test(self, interaction: discord.Interaction, route: str, text: str):
        router = self._get_router()
        if not router:
            await interaction.response.send_message("AI router not initialized.", ephemeral=True)
            return

        try:
            route_type = RouteType(route)
        except ValueError:
            valid = ", ".join(r.value for r in RouteType)
            await interaction.response.send_message(
                f"Invalid route. Valid routes: {valid}", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        result = await router.handle_admin_test(route_type, text)

        embed = discord.Embed(
            title=f"AI Test — {route_type.value}",
            color=discord.Color.green() if result.confidence >= 0.70 else discord.Color.orange(),
        )
        embed.add_field(name="Model", value=result.model_used, inline=True)
        embed.add_field(name="Confidence", value=f"{result.confidence:.2f}", inline=True)
        embed.add_field(name="Latency", value=f"{result.latency_ms}ms", inline=True)
        embed.add_field(name="Tokens", value=f"In: {result.input_tokens} / Out: {result.output_tokens}", inline=True)
        embed.add_field(name="Needs Staff", value=str(result.needs_staff), inline=True)
        embed.add_field(name="KB Sections", value=", ".join(result.used_kb_sections) or "None", inline=True)

        # Truncate answer for embed
        answer = result.answer_markdown[:1900] if result.answer_markdown else "*No answer*"
        embed.add_field(name="Response", value=answer, inline=False)

        if result.error:
            embed.add_field(name="Error", value=result.error, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIAdmin(bot))
