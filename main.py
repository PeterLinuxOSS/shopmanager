"""ShopManager entry point.

Loads the cogs, wires up the owner-only reload command and starts the bot.
"""

import logging
import os
from itertools import cycle
from pathlib import Path

import nextcord
from nextcord import Embed, Interaction, SlashOption
from nextcord.ext import application_checks
from nextcord.ext.commands import Bot

import config

config.validate()

CWD = Path(__file__).resolve().parent
VERSION = "6.3.2"

# nextcord at DEBUG writes every gateway event to disk; the original shipped
# that way and left a 22 MB log behind. INFO by default, override with LOG_LEVEL.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "nextcord.log")

logger = logging.getLogger("nextcord")
logger.setLevel(LOG_LEVEL)
_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8", mode="a")
_handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(_handler)

intents = nextcord.Intents.all()
bot = Bot(
    command_prefix=config.COMMAND_PREFIX,
    case_insensitive=True,
    owner_id=config.OWNER_ID,
    intents=intents,
)
bot.pause = True
bot.version = VERSION
bot.statuses = cycle([config.BRAND_NAME, "/help | 0 guilds", "Freemium Bot"])
bot.slotsready = False

# Listed explicitly rather than globbing ./cogs, so a stray module in the
# directory cannot be loaded as an extension by accident. Comment a line out to
# disable that feature.
EXTENSIONS = (
    "cogs.bot_tasks",
    "cogs.commands",
    "cogs.events",
    "cogs.headcategory",
    "cogs.helpers",
    "cogs.order",
    "cogs.setup",
    "cogs.setup_products",
    "cogs.setup_style",
    "cogs.subcategory",
    "cogs.ticket",
    "cogs.ui",
)


def load_extensions() -> None:
    for extension in EXTENSIONS:
        bot.load_extension(extension)
        print(f"loaded {extension}")


@bot.event
async def on_ready():
    print(f"ShopManager {VERSION} ready as {bot.user}")


@bot.slash_command(name="reload", guild_ids=config.TESTING_GUILD_IDS)
@application_checks.is_owner()
async def reload(
    interaction: Interaction,
    extension: str = SlashOption(name="extension", description="extension name(.py)"),
):
    bot.reload_extension(f"cogs.{extension}")
    await interaction.send(
        embed=Embed(
            title="Reload",
            description=f"{extension} successfully reloaded",
            color=0xFF00C8,
        )
    )


if __name__ == "__main__":
    load_extensions()
    bot.run(config.DISCORD_TOKEN)
