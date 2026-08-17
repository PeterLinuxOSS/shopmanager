from pymongo import MongoClient

import config

# The shop's own database.
cluster = MongoClient(config.MONGODB_URI)

# A second cluster belonging to the CommendBot deployment, shared so the shop
# can sell commends against an existing CommendBot balance. Optional: without
# COMMENDBOT_MONGODB_URI the CommendBot-backed collections are unavailable and
# only the standalone shop features work.
commendbot = MongoClient(config.COMMENDBOT_MONGODB_URI) if config.COMMENDBOT_MONGODB_URI else None


class db:
    # --- CommendBot's database (read/write across services) ---------------
    users_database = commendbot["usersdb"] if commendbot else None
    balancesdb = users_database["balancesdb"] if commendbot else None
    usersdb = users_database["usersdb"] if commendbot else None
    servers = commendbot["servers"] if commendbot else None
    blacklistdb = servers["blacklistdb"] if commendbot else None
    slotsdb = servers["commendbotstatus"] if commendbot else None
    subdb = servers["sub"] if commendbot else None

    # --- the shop's own database ------------------------------------------
    db = cluster[config.MONGODB_DATABASE]
    ticketsdb = db["ticketsdb"]
    embedstylesdb = db["embed-styles"]
    guildsdb = db["guildsdb"]
    headcategorysdb = db["head-categorys"]
    subcategoriesdb = db["sub-categorys"]
    paymentsdb = db["payments"]
    productsdb = db["products"]
    globalchecker = db["globalchecker"]
    refreshview = db["refreshview"]
    goodsdb = db["goodsdb"]
    keysdb = db["keysdb"]
    ranksvrai = db["ranksvar"]
    timedb = db["timedb"]
    subkeys = db["keyssub"]
