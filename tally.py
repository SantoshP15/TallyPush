import requests
from config import TALLY_URL


def send_request(xml):

    print("=" * 80)
    print("SENDING REQUEST TO TALLY")
    print("=" * 80)

    response = requests.post(
        TALLY_URL,
        data=xml.encode("utf-8"),
        headers={"Content-Type": "text/xml"},
        timeout=300
    )

    print("=" * 80)
    print("STATUS CODE :", response.status_code)
    print("=" * 80)

    print(response.text[:1000])

    return response.text