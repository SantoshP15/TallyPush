COLUMN_MAPPINGS = {

    # -------------------------------------------------
    # Sales Inventory
    # -------------------------------------------------

    "SalesInventory": {

        "DATE": "VOUCHERDATE",
        "STKNAME": "STOCKITEMNAME",
        "STKQTY": "STOCKQTY",
        "MSTID": "MASTERID",
        "MYGSTRATE": "GSTRATE",
        "CMPNAME": "COMPANYNAME",
        "ALTID": "AlterID"  

    },

    # -------------------------------------------------
    # Sales Ledger
    # -------------------------------------------------

    "SalesLedger": {

        "DATE": "VOUCHERDATE",
        "CMPNAME": "COMPANYNAME",
        "ALTID": "AlterID"  

    },

    # -------------------------------------------------
    # Purchase Inventory
    # -------------------------------------------------

    "PurchaseInventory": {

        "DATE": "VOUCHERDATE",
        "STKNAME": "STOCKITEMNAME",
        "STKQTY": "STOCKQTY",
        "MSTID": "MASTERID",
        "MYGSTRATE": "GSTRATE",
        "CMPNAME": "COMPANYNAME"

    },

    # -------------------------------------------------
    # Purchase Ledger
    # -------------------------------------------------

    "PurchaseLedger": {

        "DATE": "VOUCHERDATE",
        "CMPNAME": "COMPANYNAME"

    },

    # -------------------------------------------------
    # Ledgerwise Daybook
    # -------------------------------------------------

    "LedgerwiseDayBook": {

        "VCHDATE": "VOUCHERDATE",
        "VCHNUMBER": "VOUCHERNUMBER"

    },

    # -------------------------------------------------
    # Ledger Opening Balance
    # -------------------------------------------------

    "LedgerOpeningBalance": {

    },

    # -------------------------------------------------
    # Aura Sales
    # -------------------------------------------------

    "AuraAllSales": {

        "VCHDT": "VOUCHERDATE"

    },

    # -------------------------------------------------
    # Aura Purchase
    # -------------------------------------------------

    "AuraAllPurchase": {

        "VCHDT": "VOUCHERDATE"

    }

}