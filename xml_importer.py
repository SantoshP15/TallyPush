from lxml import etree
import re

from datetime import datetime

from database import get_connection
from column_mapping import COLUMN_MAPPINGS


# ==========================================
# Clean XML
# ==========================================

def clean_xml(xml):

    xml = re.sub(r'&#\d+;', '', xml)

    xml = ''.join(

        ch for ch in xml

        if ch in '\t\r\n' or ord(ch) >= 32

    )

    return xml


# ==========================================
# Parse XML
# ==========================================

def parse_xml(xml):

    parser = etree.XMLParser(

        recover=True,
        encoding="utf-8"

    )

    root = etree.fromstring(

        xml.encode("utf-8"),
        parser

    )

    return root


# ==========================================
# XML OBJECT -> Dictionary
# ==========================================

def object_to_dict(obj):

    record = {}

    for child in obj:

        # Ignore Nested Collections
        if len(child):

            continue

        tag = child.tag.upper()

        value = child.text

        if value is not None:

            value = value.strip()

        else:

            value = None

        record[tag] = value

    return record


# ==========================================
# SQL Columns
# ==========================================

def get_table_columns(cursor, table_name):

    cursor.execute("""

        SELECT COLUMN_NAME

        FROM INFORMATION_SCHEMA.COLUMNS

        WHERE TABLE_NAME = ?

    """, table_name)

    return [

        row[0].upper()

        for row in cursor.fetchall()

    ]


# ==========================================
# Convert Values
# ==========================================

def convert_value(db_column, value):

    if value is None or value == "":

        return None

    db_column = db_column.upper()

    # ------------------------
    # Dates
    # ------------------------

    if "DATE" in db_column:

        try:

            return datetime.strptime(

                value,
                "%Y%m%d"

            ).date()

        except:

            return value

    # ------------------------
    # Numbers
    # ------------------------

    if db_column in (

        "AMOUNT",
        "RATE",
        "STOCKQTY",
        "ALTQTY",
        "GSTRATE",
        "ALTERID"

    ):

        number = re.findall(

            r"-?\d+\.?\d*",
            str(value)

        )

        if number:

            try:

                if db_column == "ALTERID":

                    return int(number[0])

                return float(number[0])

            except:

                pass

    return value


# ==========================================
# Prepare Record
# ==========================================

def prepare_record(

        record,
        table_name,
        sql_columns

):

    mapping = COLUMN_MAPPINGS.get(

        table_name,

        {}

    )

    columns = []

    values = []

    for key, value in record.items():

        db_column = mapping.get(

            key,

            key

        )

        if db_column.upper() not in sql_columns:

            continue

        value = convert_value(

            db_column,

            value

        )

        # Avoid duplicate columns

        if db_column.upper() in [

            c.upper()

            for c in columns

        ]:

            continue

        columns.append(db_column)

        values.append(value)

    return columns, values

# ==========================================
# Insert Record
# ==========================================

def insert_record(
        cursor,
        table_name,
        columns,
        values
):

    placeholders = ",".join(["?"] * len(values))

    sql = f"""
    INSERT INTO {table_name}
    ({",".join(columns)})
    VALUES
    ({placeholders})
    """

    cursor.execute(sql, values)


# ==========================================
# Delete Voucher
# ==========================================

def delete_masterid(
        cursor,
        table_name,
        master_id
):

    cursor.execute(

        f"""
        DELETE FROM {table_name}
        WHERE MasterID = ?
        """,

        master_id

    )


# ==========================================
# Sync Record
# ==========================================

def sync_record(

        cursor,
        table_name,
        columns,
        values,
        mode="UPSERT",
        processed_masterids=None

):

    # ----------------------------------
    # INSERT MODE
    # ----------------------------------

    if mode.upper() == "INSERT":

        insert_record(

            cursor,
            table_name,
            columns,
            values

        )

        return "INSERT"

    # ----------------------------------
    # REFRESH MODE
    # ----------------------------------

    if mode.upper() == "REFRESH":

        insert_record(

            cursor,
            table_name,
            columns,
            values

        )

        return "INSERT"

    # ----------------------------------
    # UPSERT MODE
    # ----------------------------------

    if "MASTERID" not in [c.upper() for c in columns]:

        insert_record(

            cursor,
            table_name,
            columns,
            values

        )

        return "INSERT"

    master_index = [

        c.upper()

        for c in columns

    ].index("MASTERID")

    master_id = values[master_index]

    # Delete voucher only once
    if master_id not in processed_masterids:

        delete_masterid(

            cursor,
            table_name,
            master_id

        )

        processed_masterids.add(master_id)

    # Insert every row
    insert_record(

        cursor,
        table_name,
        columns,
        values

    )

    return "INSERT"# ==========================================
# Import XML
# ==========================================

def import_xml(

        xml,
        table_name,
        mode="UPSERT"

):

    # ----------------------------
    # Clean XML
    # ----------------------------

    xml = clean_xml(xml)

    # ----------------------------
    # Parse XML
    # ----------------------------

    root = parse_xml(xml)

    # ----------------------------
    # Find Objects
    # ----------------------------

    objects = root.xpath("//OBJECT")

    print(f"\nObjects Found : {len(objects)}")

    if len(objects) == 0:

        print("No Records Found")

        return

    # ----------------------------
    # Database Connection
    # ----------------------------

    conn = get_connection()

    cursor = conn.cursor()

    # ----------------------------
    # Refresh Mode
    # ----------------------------

    if mode.upper() == "REFRESH":

        print(f"Refreshing {table_name}...")

        cursor.execute(

            f"DELETE FROM {table_name}"

        )

        conn.commit()

    # ----------------------------
    # SQL Columns
    # ----------------------------

    sql_columns = get_table_columns(

        cursor,
        table_name

    )

    inserted = 0

    # ----------------------------
    # Keeps track of deleted vouchers
    # ----------------------------


    # ----------------------------
    # Loop through XML Objects
    # ----------------------------

    processed_masterids = set()

    for obj in objects:

        try:

            record = object_to_dict(obj)

            columns, values = prepare_record(
                record,
                table_name,
                sql_columns
            )

            if len(columns) == 0:
                continue

            master_index = [
                c.upper()
                for c in columns
            ].index("MASTERID")

            master_id = values[master_index]

            if master_id not in processed_masterids:

                delete_masterid(
                    cursor,
                    table_name,
                    master_id
                )

                processed_masterids.add(master_id)

            insert_record(
                cursor,
                table_name,
                columns,
                values
            )

            inserted += 1

        except Exception as e:

            print(f"Error in MasterID : {master_id}")

            print(e)

            conn.rollback()


    # ----------------------------
    # Commit
    # ----------------------------

    conn.commit()

    cursor.close()

    conn.close()

    # ----------------------------
    # Summary
    # ----------------------------

    print("\n------------------------------------")

    print(f"Table     : {table_name}")

    print(f"Imported  : {inserted}")

    print("------------------------------------")

    print("Import Completed Successfully\n")