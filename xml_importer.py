from lxml import etree
import re

# ==========================================
# Clean Tally XML
# ==========================================

def clean_xml(xml):

    # Remove invalid XML entities like &#4;
    xml = re.sub(r'&#\d+;', '', xml)

    # Remove illegal control characters
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
# Convert XML Object to Dictionary
# ==========================================

def object_to_dict(obj):

    record = {}

    for child in obj:

        # Ignore nested collections for now
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
from database import get_connection
from column_mapping import COLUMN_MAPPINGS
from datetime import datetime


# ==========================================
# Get SQL Table Columns
# ==========================================

def get_table_columns(cursor, table_name):

    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
    """, table_name)

    return [row[0].upper() for row in cursor.fetchall()]


# ==========================================
# Convert XML Value
# ==========================================

def convert_value(db_column, value):

    if value is None or value == "":
        return None

    db_column = db_column.upper()

    # -------------------------
    # Date Columns
    # -------------------------

    if "DATE" in db_column:

        try:
            return datetime.strptime(
                value,
                "%Y%m%d"
            ).date()

        except:
            return value

    # -------------------------
    # Numeric Columns
    # -------------------------

    if db_column in (
        "AMOUNT",
        "RATE",
        "STOCKQTY",
        "ALTQTY",
        "GSTRATE"
    ):

        numbers = re.findall(
            r"-?\d+\.?\d*",
            value
        )

        if numbers:

            try:
                return float(numbers[0])
            except:
                pass

    return value


# ==========================================
# Prepare Record
# ==========================================
def prepare_record(record, table_name, sql_columns):

    mapping = COLUMN_MAPPINGS.get(
        table_name,
        {}
    )

    columns = []
    values = []

    for key, value in record.items():

        # XML Tag -> SQL Column
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

        # Avoid duplicate SQL columns
        if db_column.upper() in [
            c.upper()
            for c in columns
        ]:
            continue

        columns.append(db_column)
        values.append(value)

    return columns, values
# ==========================================
# Check Existing Record
# ==========================================

def record_exists(cursor, table_name, master_id):

    cursor.execute(
        f"""
        SELECT AlterID
        FROM {table_name}
        WHERE MasterID = ?
        """,
        master_id
    )

    return cursor.fetchone()


# ==========================================
# Insert Record
# ==========================================

def insert_record(cursor, table_name, columns, values):

    placeholders = ",".join(["?"] * len(values))

    sql = f"""
    INSERT INTO {table_name}
    ({",".join(columns)})
    VALUES
    ({placeholders})
    """

    cursor.execute(sql, values)


# ==========================================
# Update Record
# ==========================================

def update_record(cursor, table_name, columns, values):

    master_id = None

    set_clause = []
    update_values = []

    for column, value in zip(columns, values):

        if column.upper() == "MASTERID":

            master_id = value
            continue

        set_clause.append(f"{column}=?")
        update_values.append(value)

    update_values.append(master_id)

    sql = f"""
    UPDATE {table_name}
    SET
        {",".join(set_clause)}
    WHERE MasterID = ?
    """

    cursor.execute(sql, update_values)


# ==========================================
# Sync Record
# ==========================================

def sync_record(
        cursor,
        table_name,
        columns,
        values,
        mode="UPSERT"
):

    # ----------------------------------
    # INSERT ONLY
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
    # UPSERT
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

    row = record_exists(
        cursor,
        table_name,
        master_id
    )

    # New Record
    if row is None:

        insert_record(
            cursor,
            table_name,
            columns,
            values
        )

        return "INSERT"

    # No AlterID -> Skip
    if "ALTERID" not in [c.upper() for c in columns]:

        return "SKIP"

    alter_index = [
        c.upper()
        for c in columns
    ].index("ALTERID")

    xml_alter = str(values[alter_index])

    sql_alter = str(row[0])

    # Updated Record
    if xml_alter != sql_alter:

        update_record(
            cursor,
            table_name,
            columns,
            values
        )

        return "UPDATE"

    return "SKIP"
# ==========================================
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

        print("No Records Found.")

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

        cursor.execute(f"DELETE FROM {table_name}")

        conn.commit()

    # ----------------------------
    # SQL Columns
    # ----------------------------

    sql_columns = get_table_columns(
        cursor,
        table_name
    )

    inserted = 0
    updated = 0
    skipped = 0

    # ----------------------------
    # Loop Through Objects
    # ----------------------------

    for obj in objects:

        record = object_to_dict(obj)
        # print(record)
        # break   
        columns, values = prepare_record(

            record,
            table_name,
            sql_columns

        )

        if len(columns) == 0:

            continue

        action = sync_record(

            cursor,
            table_name,
            columns,
            values,
            mode

        )

        if action == "INSERT":

            inserted += 1

        elif action == "UPDATE":

            updated += 1

        else:

            skipped += 1

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

    print(f"Inserted  : {inserted}")

    print(f"Updated   : {updated}")

    print(f"Skipped   : {skipped}")

    print("------------------------------------")

    print("Import Completed Successfully\n")