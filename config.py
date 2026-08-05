# ==========================================
# SQL Server Configuration
# ==========================================

SERVER = r"DESKTOP-2I29RMG\SQLEXPRESS01"
DATABASE = "AdventureWorks2022"

# Windows Authentication
TRUSTED_CONNECTION = "yes"

# ==========================================
# Tally Configuration
# ==========================================

TALLY_URL = "http://localhost:9000"

# ==========================================
# XML Configuration
# ==========================================

XML_ENCODING = "utf-8"

# Save XML responses for debugging
SAVE_XML = True

# Folder where XML responses are stored
XML_FOLDER = "responses"

# ==========================================
# Logging
# ==========================================
import os
LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "sync.log")

# ==========================================
# Sync Behaviour
# ==========================================

# INSERT  -> Insert only
# UPSERT  -> Insert + Update using MasterID & AlterID
# REFRESH -> Delete all and Import again

DEFAULT_SYNC_MODE = "UPSERT"

# ==========================================
# Collection Configuration
# ==========================================

COLLECTIONS = [

    {
        "collection": "SalesInventoryDetails_coll",
        "table": "SalesInventory",
        "mode": "UPSERT",
        "key_columns": ["MasterID", "StockItemName"]
        
    },

    {
        "collection": "SalesLedgerDetails_collSrc",
        "table": "SalesLedger",
        "mode": "UPSERT",
        "key_columns": ["MasterID"]
    },

    # {
    #     "collection": "PurchaseInventoryDetails_coll",
    #     "table": "PurchaseInventory",
    #     "mode": "UPSERT"
    # },

    # {
    #     "collection": "PurchaseLedgerDetails_collSrc",
    #     "table": "PurchaseLedger",
    #     "mode": "UPSERT"
    # },

    # {
    #     "collection": "TallyLedgewiseDayBookColl",
    #     "table": "LedgerwiseDayBook",
    #     "mode": "UPSERT"
    # },

    # {
    #     "collection": "LedgerOpBalMainColl",
    #     "table": "LedgerOpeningBalance",
    #     "mode": "REFRESH"
    # },

    # {
    #     "collection": "AuraAllSalesColl_Src",
    #     "table": "AuraAllSales",
    #     "mode": "UPSERT"
    # },

    # {
    #     "collection": "AuraAllPurchaseColl_Src",
    #     "table": "AuraAllPurchase",
    #     "mode": "UPSERT"
    # }

]