"""Entry point: python -m discord_bot"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

# Ensure the bot directory is on sys.path so bare imports (config, bot, cogs.*)
# work regardless of what directory the process was launched from.
_BOT_DIR = str(Path(__file__).resolve().parent)
if _BOT_DIR not in sys.path:
    sys.path.insert(0, _BOT_DIR)
os.chdir(_BOT_DIR)

# --- Logging: both console AND rotating file ---
_LOG_DIR = Path(__file__).parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "draconic_bot.log"

_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler
_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_fmt)

# Rotating file handler: 5 MB per file, keep 3 backups
_file = logging.handlers.RotatingFileHandler(
    _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8",
)
_file.setFormatter(_fmt)

# Attach handlers directly to root logger (basicConfig is a no-op if
# the root logger was already configured by an import, e.g. discord.py).
_root = logging.getLogger()
_root.setLevel(logging.INFO)
_root.addHandler(_console)
_root.addHandler(_file)

# Suppress noisy discord.py gateway logs
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)

from config import DISCORD_TOKEN
from bot import DraconicBot

if not DISCORD_TOKEN or DISCORD_TOKEN == "your_token_here":
    print("ERROR: Set DISCORD_TOKEN in .env")
    print("       Copy .env.example to .env and fill in your bot token.")
    sys.exit(1)

bot = DraconicBot()
bot.run(DISCORD_TOKEN)
