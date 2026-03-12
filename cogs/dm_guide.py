import discord
from discord.ext import commands
from emojis import em

# Flow steps for the Setup Wizard
SETUP_STEPS = [
    {
        "title": "Welcome to DraconicWoW Setup!",
        "desc": "Setting up a private server for the first time is hard! That's why I'm here. This is a 1-on-1 step-by-step tour.\n\nFirst, do you have your **Retail World of Warcraft** installed and updated via Battle.net? And did you set the Game Settings (Language/Speech) to **English** in Battle.net?",
        "options": [
            {"label": "Yes, installed & English!", "next": 1, "style": discord.ButtonStyle.success},
            {"label": "No/How do I do that?", "next": "fail_wow", "style": discord.ButtonStyle.danger}
        ]
    },
    {
        "title": "Step 2: Database & Config File",
        "desc": "Great! Next, you need your database running, and your game pointed to your server.\n\nOpen `UniServerZ` and click **Start MySQL**. Then, go to your WoW folder and open `_retail_/WTF/Config.wtf` in Notepad. Did you change the `SET portal` line to `SET portal \"127.0.0.1\"`?",
        "options": [
            {"label": "Yes, MySQL is on & Config saved!", "next": 2, "style": discord.ButtonStyle.success},
            {"label": "I'm lost / MySQL is red", "next": "fail_mysql", "style": discord.ButtonStyle.danger}
        ]
    },
    {
        "title": "Step 3: Extracting Maps",
        "desc": "Almost done. The server needs to know where the walls are.\n\nYou must copy the 4 extractors (`mapextractor.exe`, `vmapextractor.exe`, `vmap4assembler.exe`, `mmaps_generator.exe`) into your **Retail WoW** folder and run them. Did you do that, and then **move** the generated `maps`, `vmaps`, and `mmaps` folders back into your server folder?",
        "options": [
            {"label": "Yes! Extracted and moved.", "next": 3, "style": discord.ButtonStyle.success},
            {"label": "I got an error / skipped it", "next": "fail_maps", "style": discord.ButtonStyle.danger}
        ]
    },
    {
        "title": "Step 4: Launching the Server",
        "desc": "You are ready! Open your server folder and double-click `bnetserver.exe` and `worldserver.exe`.\n\nThey should open two black windows. Do they both say 'Ready' at the bottom?",
        "options": [
            {"label": "Yes, both ready!", "next": 4, "style": discord.ButtonStyle.success},
            {"label": "One crashed instantly", "next": "fail_crash", "style": discord.ButtonStyle.danger}
        ]
    },
    {
        "title": "You did it!",
        "desc": "Congratulations! Your server is running!\n\nFinally, download the **Arctium Launcher**. Put the `Arctium WoW Launcher.exe` file directly into your `_retail_` folder, exactly next to the normal `wow.exe` file. Double-click Arctium to play!",
        "options": [
            {"label": "Awesome, thanks!", "next": "end", "style": discord.ButtonStyle.primary}
        ]
    }
]

# Error branches
FAIL_BRANCHES = {
    "fail_wow": "You must install the game first! Open Battle.net, search for World of Warcraft, and click Install. Before hitting play, click the gear icon next to Play, go to Game Settings, and change 'Text & Spoken Language' to English! Come back when it's done.",
    "fail_mysql": "If MySQL turns red, it means another database is running secretly in the background on port 3306! Open Task Manager and look for 'mysqld.exe' and end task. For the Config.wtf file, just open it in regular Notepad and edit the word 'US' or 'EU' to '127.0.0.1'!",
    "fail_maps": "These can take hours! But you *must* do it. Copy those 4 .exe files directly into your `World of Warcraft/_retail_` folder and double click them in order. Then move the output folders back to your repack directory.",
    "fail_crash": "If it crashed instantly, it's usually because your Antivirus deleted a file, or you forgot to copy the maps over! Try dropping your `worldserver.conf` or `Server.log` file directly into the #troubleshooting channel so I can read it for you."
}

class DMStepView(discord.ui.View):
    def __init__(self, step_idx: int | str):
        super().__init__(timeout=300)
        self.step_idx = step_idx
        
        # Build buttons dynamically based on step index (or fail string)
        if isinstance(step_idx, int):
            step_data = SETUP_STEPS[step_idx]
            for opt in step_data["options"]:
                self.add_item(WizardButton(
                    label=opt["label"],
                    next_step=opt["next"],
                    style=opt["style"]
                ))
        else:
            # It's an end state or fail branch, just add a Close button
            self.add_item(WizardButton(
                label="Okay, got it!",
                next_step="end",
                style=discord.ButtonStyle.secondary
            ))

class WizardButton(discord.ui.Button):
    def __init__(self, label: str, next_step: int | str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.next_step = next_step

    async def callback(self, interaction: discord.Interaction):
        # End state
        if self.next_step == "end":
            embed = discord.Embed(
                title="\U0001f389 You're all set!",
                description="This Setup Wizard is closing. If you need help again, just ask in the server!",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        # Fail branch
        if isinstance(self.next_step, str):
            icon = em("fix", "\U0001f527")
            embed = discord.Embed(
                title=f"{icon} Let's fix that!",
                description=FAIL_BRANCHES[self.next_step],
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=DMStepView(self.next_step))
            return
            
        # Normal next step
        step_data = SETUP_STEPS[self.next_step]
        icon = em("robot", "\U0001f916")
        embed = discord.Embed(
            title=f"{icon} {step_data['title']}",
            description=step_data['desc'],
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=DMStepView(self.next_step))


class DMGuide(commands.Cog):
    """Offers a DM-based setup wizard."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Let user request setup directly
        if message.content.lower().startswith("!setup"):
            try:
                dm_channel = await message.author.create_dm()
                step_data = SETUP_STEPS[0]
                icon = em("robot", "\U0001f916")
                embed = discord.Embed(
                    title=f"{icon} {step_data['title']}",
                    description=step_data['desc'],
                    color=discord.Color.blue()
                )
                await dm_channel.send(embed=embed, view=DMStepView(0))
                await message.add_reaction("\U0001f389") # Tada
            except discord.Forbidden:
                await message.reply("I can't DM you! Please enable DMs from server members.")

async def setup(bot: commands.Bot):
    await bot.add_cog(DMGuide(bot))
