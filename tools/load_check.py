"""Load every cog into a real nextcord Bot and report the command surface.

Run this after any change that touches imports, cog structure, or the
EXTENSIONS list in main.py. It catches import-time errors (missing imports,
circular imports, syntax mistakes introduced by a refactor) that a plain
`python -m compileall` cannot, because it actually executes module bodies
and registers cogs the way main.py does at startup.

It does not exercise interactive flows (select menus, modals, button
callbacks) — those only run against a live Discord interaction. See
tools/exercise_db.py for a runtime check of the database layer, and
README.md's "Known rough edges" for what remains unverified.

    MONGODB_URI='mongodb://127.0.0.1:27017/?directConnection=true' \
        python3 tools/load_check.py
"""

import os
import sys
import traceback
from pathlib import Path

os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:27017/shopmanager_loadcheck?directConnection=true")
os.environ.setdefault("DISCORD_TOKEN", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.chdir(Path(__file__).resolve().parents[1])

import main as shopmain  # noqa: E402


def main() -> int:
    bot = shopmain.bot
    failed = 0
    for ext in shopmain.EXTENSIONS:
        try:
            bot.load_extension(ext)
        except Exception:
            failed += 1
            print(f"FAIL {ext}")
            traceback.print_exc()

    cmds = sorted(c.name for c in bot.get_all_application_commands())
    print(f"\ncogs loaded: {len(bot.cogs)}  failed: {failed}")
    print(f"application commands: {len(cmds)}: {' '.join(cmds)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
