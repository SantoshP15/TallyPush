from flask import Flask, render_template, jsonify

from config import COLLECTIONS
from tally import send_request
from xml_requests import get_collection_xml
from xml_importer import import_xml

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/sync", methods=["POST"])
def sync():

    try:

        for item in COLLECTIONS:

            collection_name = item["collection"]
            table_name = item["table"]
            mode = item["mode"]
            # key_columns = item["key_columns"]

            request_xml = get_collection_xml(
                collection_name
            )

            response_xml = send_request(
                request_xml
            )

            import_xml(

                response_xml,

                table_name,

                mode

            )

        return jsonify({

            "message": "Synchronization Completed Successfully"

        })

    except Exception as e:

        return jsonify({

            "message": str(e)

        })


if __name__ == "__main__":  
    app.run(debug=True)