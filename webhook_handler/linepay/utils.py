import hmac
import hashlib
import json
import base64
import uuid
import jsonify
import requests
from typing import Any, Dict

LINE_PAY_CHANNEL_ID = "2006680425"
LINE_PAY_CHANNEL_SECRET = "54c3aefd19225d8c05e5445902bf9461"
LINE_PAY_URL = "https://sandbox-api-pay.line.me"

path_url = "/v3/payments/request"
    
    
def generate_line_pay_headers(
    channel_id: str,
    channel_secret: str,
    path_url: str,
    body: Any,
) -> Dict[str, str]:
    """
    Generate request headers for LINE API with HMAC-SHA256 signature.

    Args:
        channel_id (str): The LINE Channel ID.
        channel_secret (str): The LINE Channel Secret key.
        path_url (str): The URL path for the request.
        body (Any): The request body (dict or string).

    Returns:
        Dict[str, str]: A dictionary of HTTP headers.
    """
    # Ensure body is JSON string
    if not isinstance(body, str):
        body = json.dumps(body, separators=(",", ":"))

    # Create the data to sign
    nonce = str(uuid.uuid4())
    data_to_sign = f"{channel_secret}{path_url}{body}{nonce}"

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        channel_secret.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha256
    ).digest()

    # Encode signature in Base64
    encoded_signature = base64.b64encode(signature).decode("utf-8")

    # Return the constructed headers
    return {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": channel_id,
        "X-LINE-Authorization-Nonce": nonce,
        "X-LINE-Authorization": encoded_signature
    }

def request_payment(detail):
    
    header = generate_line_pay_headers(
        channel_id=LINE_PAY_CHANNEL_ID,
        channel_secret=LINE_PAY_CHANNEL_SECRET,
        path_url=path_url,
        body=detail,
    )
    try:
        response = requests.post(f"{LINE_PAY_URL}{path_url}", headers=header, json=detail)
        response_data = response.json()
        payment_url = response_data["info"]["paymentUrl"]["web"]
        print(payment_url)
        return jsonify({"status": "success"})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)})

# channel_id = "2006680425"
# channel_secret = "54c3aefd19225d8c05e5445902bf9461"
# url = "https://sandbox-api-pay.line.me"
# request_detail = body = {
#             "amount": 250,
#             "currency": "THB",
#             "orderId": "001A",
#             "packages": [
#                 {
#                     "id": "01A",
#                     "amount": 250,
#                     "name": "Toy Package",
#                     "products": [
#                         {
#                             "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Cony",
#                             "quantity": 1,
#                             "price": 100,
#                             "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/512x512bb.jpg?alt=media&token=7cfd10b0-6d01-4612-b42e-b1b4d0105acd"
#                         },
#                         {
#                             "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Sally",
#                             "quantity": 1,
#                             "price": 150,
#                             "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/8cd724371a6f169b977684fd69cc2339.jpg?alt=media&token=e2008ff7-1cad-4476-a2e4-cda5f8af6561"
#                         }
#                     ]
#                 }
#             ],
#             "redirectUrls": {
#                 "confirmUrl": f"https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder",
#                 "cancelUrl": "https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder"
#             }
#         }

# headers = generate_line_pay_headers(channel_id, channel_secret, url, request_detail)
# print(headers)