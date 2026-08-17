"""Central configuration for ShopManager.

Everything that used to be hardcoded — credentials, Discord snowflakes and
branding — is read from the environment here (see ``.env.example``). The
defaults are the values of the original ``gameboosting.top`` deployment and are
only useful as a reference for how the bot was wired up; point them at your own
guild before running.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _str(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _int(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


def _int_list(name: str, default: tuple[int, ...] = ()) -> list[int]:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return list(default)
    return [int(part) for part in raw.replace(",", " ").split()]


# --------------------------------------------------------------------------
# Credentials
# --------------------------------------------------------------------------

DISCORD_TOKEN = _str("DISCORD_TOKEN")

# The shop's own database.
MONGODB_URI = _str("MONGODB_URI")
MONGODB_DATABASE = _str("MONGODB_DATABASE", "shopmanagerv2")

# A second, separate cluster belonging to the CommendBot deployment
# (github.com/PeterLinuxOSS/commendbot). ShopManager reads customer balances,
# the blacklist and slot state from it so commends can be sold and paid for
# with an existing CommendBot balance. Leave empty to run the shop standalone;
# the CommendBot-backed product types will not work without it.
COMMENDBOT_MONGODB_URI = _str("COMMENDBOT_MONGODB_URI")

REQUIRED_SETTINGS = ("DISCORD_TOKEN", "MONGODB_URI")


def validate() -> None:
    """Raise if a setting the bot cannot run without is missing."""
    missing = [name for name in REQUIRED_SETTINGS if not globals().get(name)]
    if missing:
        raise RuntimeError(
            "Missing required configuration: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill it in."
        )


# --------------------------------------------------------------------------
# Discord
# --------------------------------------------------------------------------

OWNER_ID = _int("OWNER_ID", 640961296665149440)
COMMAND_PREFIX = _str("COMMAND_PREFIX", "s!")

# Guilds that receive guild-scoped (instantly synced) slash commands.
TESTING_GUILD_IDS = _int_list(
    "TESTING_GUILD_IDS",
    (952938661014544414, 835787802151092234, 812256537934036993),
)
# Guild the bot reports into on startup.
MAIN_GUILD_ID = _int("MAIN_GUILD_ID", 949746802163326998)
# Guild whose IDs the per-cog owner commands are scoped to.
STAFF_GUILD_ID = _int("STAFF_GUILD_ID", 835787802151092234)

# --- log channels -----------------------------------------------------
# Closed-ticket transcripts.
TRANSCRIPT_LOG_CHANNEL_ID = _int("TRANSCRIPT_LOG_CHANNEL_ID", 894605598371495937)
# Owner-facing firehose for joins, leaves and setup events.
OWNER_LOG_CHANNEL_ID = _int("OWNER_LOG_CHANNEL_ID", 937734062230106152)
# Completed orders.
ORDER_LOG_CHANNEL_ID = _int("ORDER_LOG_CHANNEL_ID", 992906519165284362)


# --------------------------------------------------------------------------
# Branding
# --------------------------------------------------------------------------

BRAND_NAME = _str("BRAND_NAME", "ShopManager")
BRAND_URL = _str("BRAND_URL", "https://example.com")
BRAND_LOGO_URL = _str("BRAND_LOGO_URL", "")
BRAND_FOOTER = _str("BRAND_FOOTER", f"powered by {BRAND_NAME}")
BRAND_COLOR = _int("BRAND_COLOR", 0x0A8F82)


# --------------------------------------------------------------------------
# Custom emoji
# --------------------------------------------------------------------------
# These lived in the original support guild. Replace with your own or with
# plain unicode — the strings are inlined into embeds as-is.

EMOJI_YES = _str("EMOJI_YES", "<:yes:904125024477278210>")
EMOJI_NO = _str("EMOJI_NO", "<:no:904125314983145572>")
EMOJI_WAIT = _str("EMOJI_WAIT", "<a:wait:930490650401603645>")
EMOJI_PAYPAL = _str("EMOJI_PAYPAL", "<:paypal:907635702085353492>")
EMOJI_ADD = _str("EMOJI_ADD", "<:add:967124092840988702>")

# CS:GO competitive ranks, indexed the same way as utils.variables.nranks
# (0 = unranked). Used by the rank-boost product type.
RANK_EMOJIS: dict[int, str] = {
    0: "unranked",
    1: "<:s1:1018129516587139143>",
    2: "<:s2:1018129518822694923>",
    3: "<:s3:1018129520492019796>",
    4: "<:s4:1018129522475946035>",
    5: "<:se:1018129525202231387>",
    6: "<:sem:1018129526649262082>",
    7: "<:gn1:1018130667369930852>",
    8: "<:gn2:1018130668821168129>",
    9: "<:gn3:1018130672885436467>",
    10: "<:gn4:1018130674848382986>",
    11: "<:mg1:1018131271253241926>",
    12: "<:mg2:1018131272909996102>",
    13: "<:mge:1018131274562547712>",
    14: "<:dmg:1018131773378527302>",
    15: "<:le:1018131795612540948>",
    16: "<:lem:1018131797294469170>",
    17: "<:smfc:1018131816542109696>",
    18: "<:ge:1018131831620653096>",
}

RANK_LABELS: dict[int, str] = {
    1: "Silver I",
    2: "Silver II",
    3: "Silver III",
    4: "Silver IV",
    5: "Silver Elite",
    6: "Silver Elite Master",
    7: "Gold Nova I",
    8: "Gold Nova II",
    9: "Gold Nova III",
    10: "Gold Nova Master",
    11: "Master Guardian I",
    12: "Master Guardian II",
    13: "Master Guardian Elite",
    14: "Distinguished Master Guardian",
    15: "Legendary Eagle",
    16: "Legendary Eagle Master",
    17: "Supreme Master First Class",
    18: "The Global Elite",
}

# Category-number select options above 10 (1-10 use the standard Discord
# keycap emoji inline, which need no configuration).
CATEGORY_NUMBER_EMOJIS: dict[int, str] = {
    11: _str("CATEGORY_EMOJI_11", "<:11:966440104564490330>"),
    12: _str("CATEGORY_EMOJI_12", "<:12:966440605024681994>"),
    13: _str("CATEGORY_EMOJI_13", "<:13:966440815977189376>"),
    14: _str("CATEGORY_EMOJI_14", "<:14:966440948680773643>"),
    15: _str("CATEGORY_EMOJI_15", "<:15:966441081271091340>"),
}

# Discord user ID of the CommendBot bot account, mentioned so a customer knows
# where to check a shared balance. The original source referenced two
# different snowflakes for what reads as the same purpose in two messages;
# preserved as two separate settings rather than assumed to be one account.
COMMENDBOT_BOT_ID_GIFT_NOTICE = _int("COMMENDBOT_BOT_ID_GIFT_NOTICE", 1134090688200462396)
COMMENDBOT_BOT_ID_BALANCE_ALERT = _int("COMMENDBOT_BOT_ID_BALANCE_ALERT", 937729933571149847)


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------
# Tutorial screenshots and banners that were hotlinked from Discord CDN
# attachments. Those links expire; re-host them and point these at your copies.

IMAGE_SETUP_TUTORIAL = _str("IMAGE_SETUP_TUTORIAL", "")
IMAGE_PRODUCT_TUTORIAL = _str("IMAGE_PRODUCT_TUTORIAL", "")
IMAGE_STYLE_TUTORIAL = _str("IMAGE_STYLE_TUTORIAL", "")
IMAGE_WARNING_ICON = _str("IMAGE_WARNING_ICON", "")
IMAGE_STANDARD_BANNER = _str("IMAGE_STANDARD_BANNER", "")


# --------------------------------------------------------------------------
# Legacy branding substitution
# --------------------------------------------------------------------------
# Copy baked into embeds still carries the original brand. Rather than rewrite
# every literal, these are rewritten at import time; anything not listed is
# left alone.

LEGACY_BRANDING: dict[str, str] = {
    "https://gameboosting.top": BRAND_URL,
    "powered by gameboosting.top": BRAND_FOOTER,
    "gamesboosting.top": BRAND_NAME,
    "gameboosting.top": BRAND_NAME,
    "r4p Services": BRAND_NAME,
}


def apply_branding(value):
    """Recursively replace legacy brand literals inside strings/lists/dicts."""
    if isinstance(value, str):
        for old, new in LEGACY_BRANDING.items():
            if old in value:
                value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [apply_branding(item) for item in value]
    if isinstance(value, tuple):
        return tuple(apply_branding(item) for item in value)
    if isinstance(value, dict):
        return {key: apply_branding(item) for key, item in value.items()}
    return value
