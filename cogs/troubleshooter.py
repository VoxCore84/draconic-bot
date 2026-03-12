"""Guided troubleshooter — interactive button-driven flows for DraconicWoW issues."""

import discord
from discord import app_commands
from discord.ext import commands
from emojis import em


# ── Decision tree structure ─────────────────────────────────────────
# Each node: {prompt, options: [{label, emoji, next_node | answer}]}
# If "answer" is present, that's a leaf node with the final response.
# If "next_node" is present, drill deeper.

TREES = {
    # ── Connection Issues ──────────────────────────────────────────
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
                    "2. Go to the TrinityCore GitHub → `sql/updates/auth/master/`\n"
                    "3. Download the newest `.sql` file — it updates `build_info` and auth keys\n"
                    "4. Run it against your **auth** database (HeidiSQL, MySQL CLI, etc.)\n"
                    "5. Restart **bnetserver** and **worldserver**\n"
                    "6. If Arctium also complains, grab the latest Arctium build from their Discord"
                ),
            },
            {
                "label": "Stuck at loading screen",
                "emoji": "\u23f3",
                "answer": (
                    "**Stuck at Loading Screen — Usually a map data problem.**\n\n"
                    "Your server can't find the map/vmap/mmap files it needs for the zone "
                    "you're loading into.\n\n"
                    "**Fix:**\n"
                    "1. Make sure you've extracted all 4 data sets (in order):\n"
                    "   `mapextractor` → `vmapextractor` → `vmap4assembler` → `mmaps_generator`\n"
                    "2. The output folders (`maps/`, `vmaps/`, `mmaps/`) must be in your server directory\n"
                    "3. Check `worldserver.conf` — `DataDir` must point to the folder containing those\n"
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
                    "1. **Try a new character** — if a fresh character works, the old one has "
                    "corrupted data (imported from a different core or incompatible build)\n"
                    "2. **Check Server.log** — look for errors or crash dumps around the disconnect time\n"
                    "3. **Check if WoW is still downloading** — if Battle.net says \"Playable\" but "
                    "isn't 100% downloaded, some zones will crash. Wait for the full download\n"
                    "4. **Verify extractors** — missing vmaps/mmaps for the character's zone will crash\n"
                    "5. If it happens with ALL characters, it's a server-side data issue — "
                    "post your Server.log in #troubleshooting"
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
                    "   (two separate console windows — both should show \"ready\" messages)\n"
                    "2. **Antivirus / Windows Defender**: If a server immediately closes, your AV likely deleted the `.exe`. Add exceptions for your server folder.\n"
                    "3. **Realmlist check**: In your `auth` database, the `realmlist` table's "
                    "address should be `127.0.0.1`\n"
                    "4. **Arctium Launcher**: Make sure it's pointed at `127.0.0.1`\n"
                    "   *(Note: Arctium requires a CPU that supports AVX2 instructions (Intel mid-2013+). Older CPUs will not launch Arctium!)*\n"
                    "5. **Ports**: Make sure nothing else is using these:\n"
                    "   \u2022 `1119` — BNet authentication\n"
                    "   \u2022 `8085` — Worldserver\n"
                    "6. **Check bnetserver.conf**: `LoginREST.ExternalAddress` and "
                    "`LoginREST.LocalAddress` should both be `127.0.0.1`"
                ),
            },
            {
                "label": "Remotely (different computer / LAN)",
                "emoji": "\U0001f310",
                "answer": (
                    "**Remote Connection Troubleshooting:**\n\n"
                    "1. The host machine needs **port forwarding** on their router:\n"
                    "   \u2022 `1119` — BNet authentication\n"
                    "   \u2022 `8085` — Worldserver\n"
                    "2. `auth.realmlist` address must be the **host's public IP** (not 127.0.0.1)\n"
                    "3. `bnetserver.conf` → `LoginREST.ExternalAddress` = host's public IP\n"
                    "4. Windows Firewall on the host must **allow inbound** on those ports\n"
                    "5. Arctium Launcher on the client → pointed to host's public IP\n"
                    "6. For **LAN only** (same network): use the host's LAN IP (e.g. 192.168.x.x) "
                    "instead of public IP, no port forwarding needed\n\n"
                    "*Quick test:* From the client machine, open Command Prompt and type "
                    "`telnet <host-ip> 1119` — if it connects, the port is reachable."
                ),
            },
        ],
    },

    # ── In-Game Issues ─────────────────────────────────────────────
    "game_issues": {
        "prompt": "What kind of in-game issue are you experiencing?",
        "options": [
            {
                "label": "NPC / creature is missing or broken",
                "emoji": "\U0001f9df",
                "answer": (
                    "**Missing or Broken NPC:**\n\n"
                    "Private servers don't have 100% of retail content — some NPCs, "
                    "quests, and events aren't implemented yet.\n\n"
                    "**What to check:**\n"
                    "1. **Is it phased?** — Some NPCs only appear in certain phases. "
                    "Try `.mod phase <id>` or `.tele <zone>` to change your phase/zone\n"
                    "2. **Respawn timer** — The NPC might be dead. Use `.npc add` (GM only) or wait\n"
                    "3. **Look it up**: Use `/creature <name>` to get a Wowhead link and verify "
                    "the NPC exists in the expected location\n\n"
                    "**If it's genuinely missing**, report it in #bug-reports with:\n"
                    "\u2022 The NPC name and/or Wowhead link\n"
                    "\u2022 The zone/coordinates where it should be\n"
                    "\u2022 What you expected to happen"
                ),
            },
            {
                "label": "Spell / ability not working",
                "emoji": "\u26a1",
                "answer": (
                    "**Spell or Ability Not Working:**\n\n"
                    "Many spells are scripted manually in private servers. Some may be "
                    "missing handlers or have incorrect values.\n\n"
                    "**What to try:**\n"
                    "1. **Relog** — some aura/spell state issues fix themselves on relog\n"
                    "2. **Check talents** — make sure the talent/spec is properly applied\n"
                    "3. **Use `.unaura all`** — clears stuck auras that might be interfering\n"
                    "4. **Look it up**: Use `/spell <name>` to verify on Wowhead what it should do\n\n"
                    "**Report it** in #bug-reports with:\n"
                    "\u2022 The spell name and Wowhead link\n"
                    "\u2022 What happened vs what should happen\n"
                    "\u2022 Your class/spec"
                ),
            },
            {
                "label": "Quest is broken or won't progress",
                "emoji": "\u2757",
                "answer": (
                    "**Quest Issues:**\n\n"
                    "Quests are one of the most complex systems — many retail quests require "
                    "scripted events, phasing, and cutscenes that may not be implemented.\n\n"
                    "**What to try:**\n"
                    "1. **Abandon and re-accept** — sometimes quest state gets corrupted\n"
                    "2. **Check prerequisites** — some quests require earlier quests completed first\n"
                    "3. **Phase issues** — the quest objective might be in a different phase. "
                    "Try logging out and back in\n"
                    "4. **GM commands** (if available):\n"
                    "   \u2022 `.quest complete <id>` to force-complete\n"
                    "   \u2022 `.quest remove <id>` then re-accept\n\n"
                    "**Report it** in #bug-reports with the quest name and Wowhead link."
                ),
            },
            {
                "label": "Transmog / appearance issue",
                "emoji": "\U0001f455",
                "answer": (
                    "**Transmog / Appearance Issues:**\n\n"
                    "The transmog/wardrobe system is actively being developed for the "
                    "12.x client and may have visual glitches or missing features.\n\n"
                    "**Known limitations:**\n"
                    "\u2022 Some appearances may not display correctly\n"
                    "\u2022 Outfit saving/loading may have edge cases\n"
                    "\u2022 Hidden appearances work but may need specific items\n\n"
                    "**If you find a bug**, report it in #bug-reports with:\n"
                    "\u2022 What you tried to transmog (item + slot)\n"
                    "\u2022 What happened vs what should happen\n"
                    "\u2022 A screenshot if possible"
                ),
            },
        ],
    },

    # ── Setup Help ─────────────────────────────────────────────────
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
                    "1. **MySQL won't start?**\n"
                    "   \u2022 Check if another MySQL is running on port 3306 (Task Manager → mysqld.exe)\n"
                    "   \u2022 If using UniServerZ, launch it as **Administrator**\n"
                    "   \u2022 Check the MySQL error log in the data folder\n\n"
                    "2. **\"Access denied\" or connection errors?**\n"
                    "   \u2022 Default creds for most repacks: `root` / `admin`\n"
                    "   \u2022 In worldserver.conf, check `LoginDatabaseInfo`, `WorldDatabaseInfo`, etc.\n"
                    "   \u2022 Format: `\"127.0.0.1;3306;root;admin;world\"`\n\n"
                    "3. **SQL update errors?**\n"
                    "   \u2022 Apply SQL files **in date order** — don't skip any\n"
                    "   \u2022 'Table already exists' = you applied it twice (safe to ignore)\n"
                    "   \u2022 'Unknown column' = you missed an earlier update\n"
                    "   \u2022 When in doubt: drop and recreate the database, apply all from scratch"
                ),
            },
            {
                "label": "Map / data extraction",
                "emoji": "\U0001f5c2\ufe0f",
                "answer": (
                    "**Map Extraction Guide:**\n\n"
                    "You need to run **4 extractors** from your WoW client directory "
                    "(where WoW.exe lives), in this exact order:\n\n"
                    "1. `mapextractor.exe` — base terrain maps\n"
                    "2. `vmapextractor.exe` — visual/collision maps\n"
                    "3. `vmap4assembler.exe` — assembles vmaps (run AFTER step 2)\n"
                    "4. `mmaps_generator.exe` — movement/pathfinding maps (**takes 1-2+ hours**)\n\n"
                    "**After extraction:**\n"
                    "\u2022 Copy `maps/`, `vmaps/`, `mmaps/` to your server directory\n"
                    "\u2022 Set `DataDir` in worldserver.conf to point there\n"
                    "\u2022 After a WoW client update, **re-extract everything**\n\n"
                    "**Normal warnings:** `Can't open WDT` / `FILE_NOT_FOUND` during vmap "
                    "extraction are fine — those are unused test maps."
                ),
            },
            {
                "label": "Building from source (advanced)",
                "emoji": "\U0001f528",
                "answer": (
                    "**Building TrinityCore from Source:**\n\n"
                    "**Prerequisites:**\n"
                    "\u2022 Visual Studio 2022+ with C++ desktop workload\n"
                    "\u2022 CMake 3.25+\n"
                    "\u2022 OpenSSL 3.x (Win64, full — not Light)\n"
                    "\u2022 MySQL 8.0+ or MariaDB\n"
                    "\u2022 Git\n\n"
                    "**Steps:**\n"
                    "1. Clone: `git clone https://github.com/TrinityCore/TrinityCore.git`\n"
                    "2. Configure: `cmake -B build -S . -G \"Visual Studio 17 2022\" -A x64`\n"
                    "3. Set `OPENSSL_ROOT_DIR` → your OpenSSL path (use `lib/VC/x64/MD/`)\n"
                    "4. Open `build/TrinityCore.sln` in Visual Studio\n"
                    "5. Build in **Release** or **RelWithDebInfo** mode\n"
                    "6. Output binaries are in `build/bin/`\n\n"
                    "**Common pitfall:** OpenSSL link errors — make sure you're using the "
                    "**MD** (not MT) libraries from `lib/VC/x64/MD/`."
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
                    "1. **Extract the repack** to a folder with no spaces in the path "
                    "(e.g., `C:\\TrinityCore\\`)\n"
                    "2. **Start MySQL** — most repacks include UniServerZ or similar. "
                    "Launch it first and click \"Start MySQL\"\n"
                    "3. **Import databases** — the repack should include SQL files. "
                    "Run them against MySQL to create the `auth`, `world`, `characters`, "
                    "and `hotfixes` databases\n"
                    "4. **Extract maps** — run the 4 extractors from your WoW directory "
                    "(see Map Extraction option)\n"
                    "5. **Configure**: Edit `worldserver.conf` — set `DataDir`, MySQL credentials, ports\n"
                    "6. **Start servers**: Run `bnetserver.exe` then `worldserver.exe`\n"
                    "7. **Create account** in bnetserver console: "
                    "`account create test@test.com mypassword`\n"
                    "8. **Set GM**: `account set gmlevel test@test.com 3 -1`\n"
                    "9. **Launch WoW** via Arctium Launcher pointed at `127.0.0.1`\n"
                    "10. Log in with your bnet email + password"
                ),
            },
            {
                "label": "Building from source",
                "emoji": "\U0001f4bb",
                "answer": (
                    "**Building from source** is the advanced path. You'll need Visual Studio, "
                    "CMake, OpenSSL, and MySQL installed.\n\n"
                    "The best guide is the official TrinityCore wiki:\n"
                    "https://trinitycore.info/en/install/requirements\n\n"
                    "**Quick overview:**\n"
                    "1. Install all prerequisites (VS2022+, CMake, OpenSSL 3.x, MySQL 8.0+)\n"
                    "2. Clone the repo\n"
                    "3. Run CMake to generate the solution\n"
                    "4. Build in Visual Studio\n"
                    "5. Set up databases (worldserver auto-applies updates on first run)\n"
                    "6. Extract maps from your WoW client\n"
                    "7. Configure and run\n\n"
                    "If you run into issues at any step, come back and use `/troubleshoot` "
                    "or ask in #troubleshooting!"
                ),
            },
        ],
    },
}

# Top-level menu
ROOT_OPTIONS = [
    ("cant_connect", "I can't connect to the server", "\U0001f50c"),
    ("game_issues", "Something in-game is broken", "\U0001f3ae"),
    ("setup_help", "I need setup / install help", "\U0001f680"),
]


class TreeButton(discord.ui.Button):
    """A button that either shows an answer or drills into a sub-tree."""

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
    """A view with buttons for a tree node's options."""

    def __init__(self, node: dict):
        super().__init__(timeout=120)
        for opt in node["options"]:
            self.add_item(TreeButton(
                label=opt["label"],
                emoji=opt["emoji"],
                tree_key=opt.get("next_node"),
                answer=opt.get("answer"),
            ))
        
        # Add a "Back to Start" button that returns to the root menu
        back_btn = discord.ui.Button(
            label="Back to Start",
            emoji="\U0001f519",  # BACK arrow emoji
            style=discord.ButtonStyle.secondary,
            row=3,  # Put it on a lower row so it's separated
            custom_id="troubleshooter_back_btn"
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

    async def on_timeout(self):
        # Disable all buttons when the view times out
        for child in self.children:
            child.disabled = True
        
        # We need the original message to edit it, but the interaction might not be accessible here cleanly 
        # without storing the message from the callback. Since context isn't passed explicitly,
        # Discord handles the UI disabling but we should at least log or handle if we had the message obj.
        pass


class RootView(discord.ui.View):
    """Top-level view for the troubleshooter."""

    def __init__(self):
        super().__init__(timeout=120)
        for key, label, emoji_str in ROOT_OPTIONS:
            self.add_item(TreeButton(
                label=label,
                emoji=emoji_str,
                tree_key=key,
            ))
            
    async def on_timeout(self):
        # Allow UI to timeout gracefully
        pass


class Troubleshooter(commands.Cog):
    """Interactive guided troubleshooter for DraconicWoW issues."""

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
        await interaction.response.send_message(embed=embed, view=RootView(), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Troubleshooter(bot))
