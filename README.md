# DraconicBot

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue) ![License: MIT](https://img.shields.io/github/license/VoxCore84/draconic-bot) ![GitHub release](https://img.shields.io/github/v/release/VoxCore84/draconic-bot)

Discord support bot for TrinityCore-based WoW private servers. Auto-answers FAQs, parses uploaded logs, monitors builds, moderates chat, and provides interactive troubleshooting -- all without manual intervention.

## Features

- **FAQ auto-responder** -- regex pattern matching with cooldowns, stats tracking, and response variety
- **Interactive troubleshooter** -- button-driven decision trees for common issues
- **Log parser** -- auto-analyzes uploaded `.conf` and `.log` files
- **Build watchdog** -- monitors TrinityCore GitHub for new commits, posts to announcements
- **Auto-moderation** -- spam detection, invite filtering, new account alerts
- **Wowhead lookups** -- `/spell`, `/item`, `/creature`, `/area`, `/faction` slash commands
- **Bug triage** -- auto-categorizes bug reports, creates threads, detects duplicates
- **Frustrated user detection** -- identifies struggling users and offers DM help
- **Verification panel** -- button-based role assignment for new members
- **GM command reference** -- `/gmcommand` knowledge base search

## Quick Start

```bash
# Clone
git clone https://github.com/VoxCore84/draconic-bot.git
cd draconic-bot

# Configure
cp .env.example .env
# Edit .env with your Discord bot token and channel IDs

# Install
pip install -r requirements.txt

# Run
python -m .
```

## Configuration

All configuration is via environment variables in `.env`. See `.env.example` for all options.

Key settings:
- `DISCORD_TOKEN` -- your bot token from the Discord Developer Portal
- `GUILD_ID` -- your Discord server ID
- Channel IDs for FAQ, announcements, bug reports, etc.

## Cogs (15 active)

| Cog | Commands | Description |
|-----|----------|-------------|
| help | `/help` | Interactive category dropdown |
| faq | `/faqstats` | Auto-answers common questions |
| lookups | `/spell`, `/item`, `/creature`, `/area`, `/faction` | Wowhead link generators |
| triage | -- | Bug categorization and threading |
| troubleshooter | `/troubleshoot` | Interactive decision-tree troubleshooter |
| frustration | -- | Frustrated user detection |
| log_parser | -- | Auto-parse uploaded config/log files |
| dm_guide | `!setup` | Step-by-step DM setup wizard |
| diagnoser | `/diagnose` | Sends diagnostic script |
| sme_kb | `/gmcommand` | GM command knowledge base |
| watchdog | `/buildcheck` | TrinityCore build monitor |
| changelog | -- | Hourly commit feed |
| automod | -- | Spam and invite filtering |
| welcome_role | `/verifypanel` | Button-based verification |
| about | `/about` | Bot version and uptime |
| announce | `/announce` | Admin announcement embeds |

## Deployment

See `deploy/README_DEPLOY.md` for full Oracle Cloud deployment guide with Docker, systemd, and SSH setup.

```bash
# Docker
cd deploy
docker compose up -d

# Or systemd
sudo cp deploy/draconic.service /etc/systemd/system/
sudo systemctl enable --now draconic-bot
```

## Customization

- **FAQ entries**: Edit `data/faq_responses.json`
- **GM commands**: Edit `data/gm_commands.json`
- **Troubleshoot trees**: Edit decision trees in `cogs/troubleshooter.py`
- **Custom emojis**: Drop PNGs in `data/emojis/` (auto-uploaded on first run)

## Requirements

- Python 3.12+
- discord.py 2.4+
- A Discord bot token with Message Content Intent enabled

## License

MIT
