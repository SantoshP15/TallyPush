import requests
import xml.etree.ElementTree as ET

with open("sales.xml", "r", encoding="utf-8") as f:
    xml = f.read()

response = requests.post(
    "http://localhost:9000",
    data=xml.encode("utf-8"),
    headers={"Content-Type": "text/xml"}
)

print("Status Code:", response.status_code)

# Save response
with open("sales_response.xml", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Response saved to sales_response.xml")