from config import COLLECTIONS
from tally import send_request
from xml_requests import get_collection_xml
from xml_importer import import_xml
from logger import log_info, log_error
from save_xml import save_xml
from database import get_last_alterid

print("=" * 70)
print("TALLY TO SQL IMPORTER")
print("=" * 70)

for item in COLLECTIONS:

    collection_name = item["collection"]
    table_name = item["table"]
    mode = item["mode"]
    
    last_alterid = get_last_alterid(table_name)
    print(f"\nProcessing : {collection_name}")

    try:

        # ----------------------------------
        # Generate XML Request
        # ----------------------------------

        request_xml = get_collection_xml(
            collection_name=collection_name,
            last_alterid=last_alterid
        )

        print("\nREQUEST XML")
        print("=" * 70)
        print(request_xml)
        print("=" * 70)

        # ----------------------------------
        # Send Request to Tally
        # ----------------------------------

        response_xml = send_request(request_xml)

        # ----------------------------------
        # Save XML
        # ----------------------------------

        save_xml(
            table_name,
            response_xml
        )

        # ----------------------------------
        # Import XML
        # ----------------------------------

        import_xml(
            response_xml,
            table_name,
            mode
        )

        log_info(f"{table_name} Imported Successfully")

        print(f"✓ {table_name} Imported Successfully")

    except Exception as e:

        log_error(f"{table_name} : {str(e)}")

        print(f"✗ Error importing {table_name}")
        print(e)

print("\n" + "=" * 70)
print("ALL COLLECTIONS COMPLETED")
print("=" * 70)