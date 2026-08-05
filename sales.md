<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Sales Vouchers</ID>
    </HEADER>

    <BODY>
        <DESC>

            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>

            <TDL>
                <TDLMESSAGE>

                    <COLLECTION NAME="Sales Vouchers">
                        <TYPE>Voucher</TYPE>

                        <FILTERS>SalesFilter</FILTERS>

                        <FETCH>
                            DATE,
                            VOUCHERNUMBER,
                            PARTYLEDGERNAME,
                            VOUCHERTYPENAME,
                            REFERENCE,
                            NARRATION,
                            ALLINVENTORYENTRIES.*,
                            ALLLEDGERENTRIES.*
                        </FETCH>

                    </COLLECTION>

                    <SYSTEM TYPE="Formulae" NAME="SalesFilter">
                        $VoucherTypeName = "Sales"
                    </SYSTEM>

                </TDLMESSAGE>
            </TDL>

        </DESC>
    </BODY>
</ENVELOPE>