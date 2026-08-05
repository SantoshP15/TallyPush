from datetime import date


def format_date(value):

    if isinstance(value, date):
        return value.strftime("%Y%m%d")

    return str(value)


def get_collection_xml(
        collection_name,
        last_alterid=0,
        from_date="20230401",
        to_date="20240331"
):

    from_date = format_date(from_date)
    to_date = format_date(to_date)

    return f"""
<ENVELOPE>

    <HEADER>

        <VERSION>1</VERSION>

        <TALLYREQUEST>EXPORT</TALLYREQUEST>

        <TYPE>COLLECTION</TYPE>

        <ID>{collection_name}</ID>

    </HEADER>

    <BODY>

        <DESC>

            <STATICVARIABLES>

                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>

                <SVFROMDATE TYPE="DATE">{from_date}</SVFROMDATE>

                <SVTODATE TYPE="DATE">{to_date}</SVTODATE>

                <mylastaltid>{last_alterid}</mylastaltid>

            </STATICVARIABLES>

        </DESC>

    </BODY>

</ENVELOPE>
"""