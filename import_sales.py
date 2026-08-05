from lxml import etree
import pyodbc
from datetime import datetime
import re

# ---------------------------------------
# SQL Server Connection
# ---------------------------------------
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-2I29RMG\SQLEXPRESS01;"
    r"DATABASE=AdventureWorks2022;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

# ---------------------------------------
# Read XML
# ---------------------------------------
with open("sales_response.xml", "r", encoding="utf-8", errors="ignore") as f:
    xml = f.read()

# ---------------------------------------
# Clean Tally XML
# ---------------------------------------

# Remove invalid XML entities like &#4;
xml = re.sub(r'&#\d+;', '', xml)

# Remove illegal control characters
xml = ''.join(
    ch for ch in xml
    if ch in '\t\n\r' or ord(ch) >= 32
)

# ---------------------------------------
# Parse XML
# ---------------------------------------
parser = etree.XMLParser(recover=True)

root = etree.fromstring(
    xml.encode("utf-8"),
    parser
)

# ---------------------------------------
# Find Vouchers
# ---------------------------------------
vouchers = root.xpath("//VOUCHER")

print(f"Found {len(vouchers)} vouchers")

# ---------------------------------------
# Import
# ---------------------------------------
for voucher in vouchers:

    date = voucher.findtext("DATE")
    voucher_no = voucher.findtext("VOUCHERNUMBER")
    party = voucher.findtext("PARTYNAME")
    party_ledger = voucher.findtext("PARTYLEDGERNAME")

    if date:
        try:
            date = datetime.strptime(date, "%Y%m%d").date()
        except:
            date = None

    inventory = voucher.findall("ALLINVENTORYENTRIES.LIST")

    if not inventory:

        cursor.execute("""
        INSERT INTO SalesRegister
        (
            VoucherDate,
            VoucherNo,
            PartyName,
            PartyLedger,
            StockItem,
            Qty,
            Rate,
            Amount
        )
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            date,
            voucher_no,
            party,
            party_ledger,
            None,
            None,
            None,
            0
        )
        )

    else:

        for item in inventory:

            stock = item.findtext("STOCKITEMNAME")
            qty = item.findtext("BILLEDQTY")
            rate = item.findtext("RATE")
            amount = item.findtext("AMOUNT")

            try:
                amount = float(amount)
            except:
                amount = 0

            cursor.execute("""
            INSERT INTO SalesRegister
            (
                VoucherDate,
                VoucherNo,
                PartyName,
                PartyLedger,
                StockItem,
                Qty,
                Rate,
                Amount
            )
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                date,
                voucher_no,
                party,
                party_ledger,
                stock,
                qty,
                rate,
                amount
            )
            )

conn.commit()

print("Import Completed Successfully")

cursor.close()
conn.close()