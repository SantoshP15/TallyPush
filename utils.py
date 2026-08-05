import os

from config import SAVE_XML, XML_FOLDER


def save_xml(table_name, xml):

    if not SAVE_XML:
        return

    if not os.path.exists(XML_FOLDER):
        os.makedirs(XML_FOLDER)

    file_path = os.path.join(
        XML_FOLDER,
        f"{table_name}.xml"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(xml)