"""Guided troubleshooter — interactive button-driven flows + AI-backed freeform diagnosis.

v3: Adds an AI-powered freeform troubleshooting option alongside the existing decision tree.
When AI is enabled, users can describe their problem in natural language and get contextual help.
The static decision tree remains available as the primary structured path.
"""

import discord
from discord import app_commands
from discord.ext import commands
from emojis import em
from ai.schemas import RouteType


# ── Decision tree structure ─────────────────────────────────────────
# Each node: {prompt, options: [{label, emoji, next_node | answer}]}

TREES = {
    "cant_connect": {
        "prompt": "What happens when you try to connect?",
        "options": [
            {
                "label": "Server unreachable / won't connect",
                "emoji": "\U0001f6ab",
                "next_node": "cant_reach",
            },
            {
                "label": "Wrong version / build mismatch",
                "emoji": "\U0001f504",
                "answer": (
                    "**Build Mismatch — Your WoW client updated but your server didn't.**\n\n"
                    "This is the #1 most common issue. When Blizzard pushes a retail "
                    "update, your Battle.net client auto-updates but your private server "
                    "still expects the old build.\n\n"
                    "**Fix:**\n"
                    "1. Use `/buildcheck` to see the latest required build number\n"
                    "2. Go to the TrinityCore GitHub \u2192 `sql/updates/auth/master/`\n"
                    "3. Download the newest `.sql` file \u2014 it updates `build_info` and auth keys\n"
                    "4. Run it against your **auth** database (HeidiSQL, MySQL CLI, etc.)\n"
                    "5. Restart **bnetserver** and **worldserver**\n"
                    "6. If Arctium also complains, grab the latest Arctium build from their Discord"
                ),
            },
            {
                "label": "Stuck at loading screen",
                "emoji": "\u23f3",
                "answer": (
                    "**Stuck at Loading Screen \u2014 Usually a map data problem.**\n\n"
                    "Your server can't find the map/vmap/mmap files it needs for the zone "
                    "you're loading into.\n\n"
                    "**Fix:**\n"
                    "1. Make sure you've extracted all 4 data sets (in order):\n"
                    "   `mapextractor` \u2192 `vmapextractor` \u2192 `vmap4assembler` \u2192 `mmaps_generator`\n"
                    "2. The output folders (`maps/`, `vmaps/`, `mmaps/`) must be in your server directory\n"
                    "3. Check `worldserver.conf` \u2014 `DataDir` must point to the folder containing those\n"
                    "4. If you recently updated your WoW client, you need to **re-extract everything**\n"
                    "5. Restart worldserver after fixing"
                ),
            },
            {
                "label": "Disconnected after character select",
                "emoji": "\u26a0\ufe0f",
                "answer": (
                    "**Disconnected After Character Select:**\n\n"
                    "The server accepted your login but crashed or rejected you when loading "
                    "your character.\n\n"
                    "**Try these in order:**\n"
                    "1. **Try a new character** \u2014 if a fresh character works, the old one has "
                    "corrupted data\n"
                    "2. **Check Server.log** \u2014 look for errors around the disconnect time\n"
                    "3. **Check if WoW is still downloading** \u2014 some zones crash if not 100% downloaded\n"
                    "4. **Verify extractors** \u2014 missing vmaps/mmaps for the character's zone will crash\n"
                    "5. If it happens with ALL characters, post your Server.log in #troubleshooting"
                ),
            },
        ],
    },
    "cant_reach": {
        "prompt": "Are you connecting locally or remotely?",
        "options": [
            {
                "label": "Locally (same computer)",
                "emoji": "\U0001f4bb",
                "answer": (
                    "**Local Connection Troubleshooting:**\n\n"
                    "1. **Both servers must be running**: open bnetserver **and** worldserver\n"
                    "2. **Antivirus / Windows Defender**: If a server immediately closes, your AV likely deleted the `.exe`\n"
                    "3. **Realmlist check**: `realmlist` table address should be `127.0.0.1`\n"
                    "4. **Arctium Launcher**: pointed at `127.0.0.1` (requires AVX2 CPU)\n"
                    "5. **Ports**: `1119` (BNet) and `8085` (World) must be free\n"
                    "6. **bnetserver.conf**: `LoginREST.ExternalAddress` and `LocalAddress` = `127.0.0.1`"
                ),
            },
            {
                "label": "Remotely (different computer / LAN)",
                "emoji": "\U0001f310",
                "answer": (
                    "**Remote Connection Troubleshooting:**\n\n"
                    "1. Port forward on router: `1119` and `8085`\n"
                    "2. `auth.realmlist` address = host's **public IP**\n"
                    "3. `bnetserver.conf` \u2192 `LoginREST.ExternalAddress` = public IP\n"
                    "4. Windows Firewall: allow inbound on both ports\n"
                    "5. For **LAN**: use host's local IP (192.168.x.x), no port forwarding needed\n\n"
                    "*Test:* `telnet <host-ip> 1119` from client machine"
                ),
            },
        ],
    },
    "game_issues": {
        "prompt": "What kind of in-game issue are you experiencing?",
        "options": [
            {
                "label": "NPC / creature is missing or broken",
                "emoji": "\U0001f9df",
                "answer": (
                    "**Missing or Broken NPC:**\n\n"
                    "Some NPCs, quests, and events aren't implemented yet.\n\n"
                    "**Check:**\n"
                    "1. **Phased?** Try `.mod phase <id>` or relog\n"
                    "2. **Respawn timer** \u2014 NPC might be dead\n"
                    "3. **Look it up**: `/creature <name>` for Wowhead link\n\n"
                    "Report in #bug-reports with NPC name, zone, and expected behavior."
                ),
            },
            {
                "label": "Spell / ability not working",
                "emoji": "\u26a1",
                "answer": (
                    "**Spell or Ability Not Working:**\n\n"
                    "**Try:**\n"
                    "1. **Relog** \u2014 fixes aura state issues\n"
                    "2. **Check talents** \u2014 ensure spec is properly applied\n"
                    "3. **`.unaura all`** \u2014 clears stuck auras\n"
                    "4. **Look it up**: `/spell <name>` for Wowhead reference\n\n"
                    "Report in #bug-reports with spell name, class/spec, and what happened vs expected."
                ),
            },
            {
                "label": "Quest is broken or won't progress",
                "emoji": "\u2757",
                "answer": (
                    "**Quest Issues:**\n\n"
                    "**Try:**\n"
                    "1. **Abandon and re-accept**\n"
                    "2. **Check prerequisites**\n"
                    "3. **Relog** for phase issues\n"
                    "4. **GM commands**: `.quest complete <id>` or `.quest remove <id>`\n\n"
                    "Report in #bug-reports with quest name and Wowhead link."
                ),
            },
            {
                "label": "Transmog / appearance issue",
                "emoji": "\U0001f455",
                "answer": (
                    "**Transmog / Appearance Issues:**\n\n"
                    "The transmog system is actively in development for 12.x.\n\n"
                    "**Known limitations:**\n"
                    "\u2022 Some appearances may not display correctly\n"
                    "\u2022 Outfit saving/loading may have edge cases\n"
                    "\u2022 Hidden appearances need specific items\n\n"
                    "Report in #bug-reports with item, slot, and screenshot."
                ),
            },
        ],
    },
    "setup_help": {
        "prompt": "What part of setup do you need help with?",
        "options": [
            {
                "label": "First-time server setup",
                "emoji": "\U0001f680",
                "next_node": "first_time_setup",
            },
            {
                "label": "MySQL / database issues",
                "emoji": "\U0001f4be",
                "answer": (
                    "**MySQL / Database Troubleshooting:**\n\n"
                    "1. **Won't start?** Check port 3306 conflict. Launch UniServerZ as Admin.\n"
                    "2. **Access denied?** Default creds: `root` / `admin`. "
                    "Check worldserver.conf `LoginDatabaseInfo` format: `\"127.0.0.1;3306;root;admin;world\"`\n"
                    "3. **SQL errors?** Apply files in date order. 'Table exists' = safe to ignore."
                ),
            },
            {
                "label": "Map / data extraction",
                "emoji": "\U0001f5c2\ufe0f",
                "answer": (
                    "**Map Extraction:**\n\n"
                    "Run 4 extractors from WoW `_retail_` dir, in order:\n"
                    "1. `mapextractor.exe`\n"
                    "2. `vmapextractor.exe`\n"
                    "3. `vmap4assembler.exe`\n"
                    "4. `mmaps_generator.exe` (takes 1-2+ hours)\n\n"
                    "Copy `maps/`, `vmaps/`, `mmaps/` to server dir. Set `DataDir` in conf."
                ),
            },
            {
                "label": "Building from source (advanced)",
                "emoji": "\U0001f528",
                "answer": (
                    "**Building from Source:**\n\n"
                    "Prerequisites: VS 2022+, CMake 3.25+, OpenSSL 3.x (full, not Light), MySQL 8.0+\n\n"
                    "1. Clone TrinityCore repo\n"
                    "2. CMake configure (set `OPENSSL_ROOT_DIR`, use `lib/VC/x64/MD/`)\n"
                    "3. Build in Release or RelWithDebInfo\n"
                    "4. Set up databases, extract maps, configure, run"
                ),
            },
        ],
    },
    "first_time_setup": {
        "prompt": "How are you setting up your server?",
        "options": [
            {
                "label": "Using a repack (pre-built)",
                "emoji": "\U0001f4e6",
                "answer": (
                    "**Repack Setup Checklist:**\n\n"
                    "1. Extract to path with no spaces (e.g. `C:\\TrinityCore\\`)\n"
                    "2. Start MySQL (UniServerZ \u2192 Start MySQL)\n"
                    "3. Import databases (auth, world, characters, hotfixes)\n"
                    "4. Extract maps (4 extractors from WoW _retail_)\n"
                    "5. Edit worldserver.conf (DataDir, MySQL creds)\n"
                    "6. Start bnetserver then worldserver\n"
                    "7. Create account: `bnetaccount create email password`\n"
                    "8. Set GM: `account set gmlevel email 3 -1`\n"
                    "9. Launch via Arctium at 127.0.0.1"
                ),
            },
            {
                "label": "Building from source",
                "emoji": "\U0001f4bb",
                "answer": (
                    "**Building from source** is the advanced path.\n\n"
                    "Best guide: https://trinitycore.info/en/install/requirements\n\n"
                    "1. Install prerequisites (VS2022+, CMake, OpenSSL 3.x, MySQL 8.0+)\n"
                    "2. Clone repo, run CMake, build in VS\n"
                    "3. Set up databases, extract maps, configure and run\n\n"
                    "Come back and use `/troubleshoot` if you get stuck!"
                ),
            },
        ],
    },
}

ROOT_OPTIONS = [
    ("cant_connect", "I can't connect to the server", "\U0001f50c"),
    ("game_issues", "Something in-game is broken", "\U0001f3ae"),
    ("setup_help", "I need setup / install help", "\U0001f680"),
]


class TreeButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, tree_key: str | None = None, answer: str | None = None):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.secondary)
        self.tree_key = tree_key
        self.answer_text = answer

    async def callback(self, interaction: discord.Interaction):
        if self.answer_text:
            icon = em("fix", "\U0001f527")
            embed = discord.Embed(
                title=f"{icon} Troubleshooting",
                description=self.answer_text,
                color=discord.Color.green(),
            )
            embed.set_footer(text="Still stuck? Ask in #troubleshooting and a human will help!")
            await interaction.response.edit_message(embed=embed, view=None)
        elif self.tree_key and self.tree_key in TREES:
            node = TREES[self.tree_key]
            view = TreeView(node)
            icon = em("fix", "\U0001f527")
            embed = discord.Embed(
                title=f"{icon} Troubleshooter",
                description=node["prompt"],
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=view)


class TreeView(discord.ui.View):
    def __init__(self, node: dict):
        super().__init__(timeout=120)
        for opt in node["options"]:
            self.add_item(TreeButton(
                label=opt["label"],
                emoji=opt["emoji"],
                tree_key=opt.get("next_node"),
                answer=opt.get("answer"),
            ))

        back_btn = discord.ui.Button(
            label="Back to Start",
            emoji="\U0001f519",
            style=discord.ButtonStyle.secondary,
            row=3,
            custom_id="troubleshooter_back_btn",
        )

        async def back_callback(interaction: discord.Interaction):
            icon = em("fix", "\U0001f527")
            embed = discord.Embed(
                title=f"{icon} DraconicWoW Troubleshooter",
                description="What kind of problem are you having?",
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Select an option below to start")
            await interaction.response.edit_message(embed=embed, view=RootView())

        back_btn.callback = back_callback
        self.add_item(back_btn)


class RootView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for key, label, emoji_str in ROOT_OPTIONS:
            self.add_item(TreeButton(
                label=label,
                emoji=emoji_str,
                tree_key=key,
            ))


class AskAIModal(discord.ui.Modal, title="Describe your problem"):
    """Modal for freeform AI troubleshooting."""

    problem = discord.ui.TextInput(
        label="What's going wrong?",
        style=discord.TextStyle.paragraph,
        placeholder="Describe your issue in detail — what you tried, what happened, error messages...",
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        router = getattr(interaction.client, "ai_router", None)
        if not router or not router.enabled:
            await interaction.followup.send(
                "AI support is currently offline. Please describe your issue in #troubleshooting and a human will help!",
                ephemeral=True,
            )
            return

        # Create a minimal message-like object for the router
        result = await router.handle_admin_test(RouteType.TROUBLESHOOT, str(self.problem))

        if result and result.answer_markdown and not result.needs_staff:
            icon = em("fix", "\U0001f527")
            embed = discord.Embed(
                title=f"{icon} AI Troubleshooting",
                description=result.answer_markdown,
                color=discord.Color.green(),
            )
            if result.follow_up_question:
                embed.set_footer(text=result.follow_up_question)
            else:
                embed.set_footer(text="Still stuck? Ask in #troubleshooting for human help!")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(
                "I wasn't able to diagnose that from the description. "
                "Please ask in #troubleshooting with any error messages or log files!",
                ephemeral=True,
            )


class Troubleshooter(commands.Cog):
    """Interactive guided troubleshooter with optional AI freeform support."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="troubleshoot", description="Interactive guided troubleshooter for common issues")
    async def troubleshoot(self, interaction: discord.Interaction):
        icon = em("fix", "\U0001f527")
        embed = discord.Embed(
            title=f"{icon} DraconicWoW Troubleshooter",
            description="What kind of problem are you having?",
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Select an option below to start")

        view = RootView()

        # Add AI freeform button if AI is available
        router = getattr(self.bot, "ai_router", None)
        if router and router.enabled:
            ai_btn = discord.ui.Button(
                label="Describe my problem (AI)",
                emoji="\U0001f9e0",
                style=discord.ButtonStyle.primary,
                row=2,
            )

            async def ai_callback(btn_interaction: discord.Interaction):
                await btn_interaction.response.send_modal(AskAIModal())

            ai_btn.callback = ai_callback
            view.add_item(ai_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Troubleshooter(bot))
