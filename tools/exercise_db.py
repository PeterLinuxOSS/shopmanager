"""Exercise the motor-based DB layer and pure helpers against a real MongoDB.

Unlike tools/load_check.py (import-time only), this actually calls the code:
real find_one/update_one/insert_one/delete_one round trips, a find() consumed
via async-for and one via to_list(), the if/else-then-shared-loop pattern from
cogs/setup.py (two branches assign the same variable name from
db.productsdb.find(...), then a single loop below consumes whichever ran —
exactly the shape that broke a first draft of the sync-to-async migration),
and the pure helpers in utils/variables.py.

Writes to and clears a scratch collection set; point MONGODB_URI at a
throwaway database.

    MONGODB_URI='mongodb://127.0.0.1:27017/shopmanager_test?directConnection=true' \
        python3 tools/exercise_db.py
"""

import asyncio
import os
import sys
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:27017/shopmanager_test?directConnection=true")
os.environ.setdefault("DISCORD_TOKEN", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.chdir(Path(__file__).resolve().parents[1])

from utils import db, is_int, is_number, millify, remove_exponent, round_up, word_count  # noqa: E402

results = []


def record(label, passed, detail=""):
    results.append((label, passed))
    print(f"  {'ok  ' if passed else 'FAIL'}  {label}{f': {detail}' if detail else ''}")


def check(label, condition, detail=""):
    try:
        record(label, bool(condition), detail)
    except Exception as exc:
        record(label, False, repr(exc))


async def if_else_shared_loop(branch: str):
    """Reproduces cogs/setup.py's real if/else-into-one-loop shape exactly."""
    if branch == "a":
        products = db.productsdb.find({"headcategory": "cat-a"})
    else:
        products = db.productsdb.find({"headcategory": "cat-b"})

    seen = []
    async for value_value in products:
        seen.append(value_value["name"])
    return seen


async def main():
    # --- pure helpers, no DB needed ------------------------------------------
    check("is_int('42')", is_int("42") is True)
    check("is_int('abc')", is_int("abc") is False)
    check("is_number('3.5')", is_number("3.5") is True)
    check("round_up(1.201, 2)", round_up(1.201, 2) == 1.21)
    check("remove_exponent", remove_exponent(Decimal("2.50")) == Decimal("2.5"))
    check("millify(1234567)", millify(1234567) == "1M", millify(1234567))
    check("word_count", word_count("a b a") == {"a": 2, "b": 1})

    # --- DB round trip --------------------------------------------------------
    await db.goodsdb.delete_many({})
    await db.productsdb.delete_many({})

    try:
        r = await db.goodsdb.insert_one({"label": "Test Good", "stock": 5})
        record("insert_one", True, f"_id {r.inserted_id}")
    except Exception as exc:
        record("insert_one", False, repr(exc))

    try:
        doc = await db.goodsdb.find_one({"label": "Test Good"})
        record("find_one", doc is not None and doc["stock"] == 5)
    except Exception as exc:
        record("find_one", False, repr(exc))

    try:
        await db.goodsdb.update_one({"label": "Test Good"}, {"$inc": {"stock": -1}})
        doc = await db.goodsdb.find_one({"label": "Test Good"})
        record("update_one", doc["stock"] == 4)
    except Exception as exc:
        record("update_one", False, repr(exc))

    try:
        n = await db.goodsdb.count_documents({})
        record("count_documents", n == 1, str(n))
    except Exception as exc:
        record("count_documents", False, repr(exc))

    try:
        for d in (
            {"headcategory": "cat-a", "name": "Product A1"},
            {"headcategory": "cat-a", "name": "Product A2"},
            {"headcategory": "cat-b", "name": "Product B1"},
        ):
            await db.productsdb.insert_one(d)
        names = sorted(
            p["name"] for p in
            await db.productsdb.find({"headcategory": "cat-a"}).to_list(length=None)
        )
        record("find().to_list()", names == ["Product A1", "Product A2"], str(names))
    except Exception as exc:
        record("find().to_list()", False, repr(exc))

    try:
        seen_a = await if_else_shared_loop("a")
        seen_b = await if_else_shared_loop("b")
        record(
            "if/else shared async-for loop",
            sorted(seen_a) == ["Product A1", "Product A2"] and seen_b == ["Product B1"],
            f"a={seen_a} b={seen_b}",
        )
    except Exception as exc:
        record("if/else shared async-for loop", False, repr(exc))

    try:
        r = await db.goodsdb.delete_one({"label": "Test Good"})
        record("delete_one", r.deleted_count == 1)
    except Exception as exc:
        record("delete_one", False, repr(exc))

    await db.goodsdb.delete_many({})
    await db.productsdb.delete_many({})

    passed = sum(1 for _, p in results if p)
    print(f"\npassed: {passed}   failed: {len(results) - passed}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
