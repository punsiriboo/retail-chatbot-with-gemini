import json
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mocked external libraries or functions
class Lah:
    def __init__(self):
        self.req = None

    def setrequest(self, req):
        self.req = req

    def eventtype(self):
        return self.req.get_json().get("eventType", "")

    def userId(self):
        return self.req.get_json().get("userId", "")

    def replyToken(self):
        return self.req.get_json().get("replyToken", "")

    def message(self):
        return self.req.get_json().get("message", {})

    def reply(self, reply_token, payload):
        # Mocked reply functionality
        print("Reply sent to LINE:", payload)
        return jsonify({"status": "replied"})

lah = Lah()

# Mocked header generator
def genHeader(channel_id, channel_secret, path_url, body, nonce):
    if not isinstance(body, str):
        body = json.dumps(body)
    data = f"{channel_secret}{path_url}{body}{nonce}"
    signature = hmac.new(
        channel_secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).digest()
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    return {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": channel_id,
        "X-LINE-Authorization-Nonce": nonce,
        "X-LINE-Authorization": encoded_signature
    }

# Payload creator mock
class PayloadCreator:
    @staticmethod
    def startpay(payment_url):
        return {
            "type": "template",
            "altText": "กรุณาชำระเงิน",
            "template": {
                "type": "buttons",
                "text": "คลิกเพื่อชำระเงิน",
                "actions": [{
                    "type": "uri",
                    "label": "ชำระเงิน",
                    "uri": payment_url
                }]
            }
        }

    @staticmethod
    def checkout():
        return {
            "type": "template",
            "altText": "ยืนยันการสั่งซื้อ",
            "template": {
                "type": "confirm",
                "text": "คุณต้องการยืนยันการสั่งซื้อหรือไม่?",
                "actions": [
                    {"type": "message", "label": "ยืนยัน", "text": "Checkout"},
                    {"type": "message", "label": "ยกเลิก", "text": "Cancel"}
                ]
            }
        }

payloadcreator = PayloadCreator()
channelId = "YOUR_CHANNEL_ID"
channelSecret = "YOUR_CHANNEL_SECRET"
baseUrl = "YOUR_BASE_URL"

@app.route('/webhook', methods=['POST'])
def webhook():
    lah.setrequest(request)
    payload = []
    
    if lah.eventtype() == "postback":
        pathUrl = "/v3/payments/request"
        nonce = str(uuid.uuid4())
        body = {
            "amount": 250,
            "currency": "THB",
            "orderId": "001A",
            "packages": [
                {
                    "id": "01A",
                    "amount": 250,
                    "name": "Toy Package",
                    "products": [
                        {
                            "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Cony",
                            "quantity": 1,
                            "price": 100,
                            "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/512x512bb.jpg?alt=media&token=7cfd10b0-6d01-4612-b42e-b1b4d0105acd"
                        },
                        {
                            "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Sally",
                            "quantity": 1,
                            "price": 150,
                            "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/8cd724371a6f169b977684fd69cc2339.jpg?alt=media&token=e2008ff7-1cad-4476-a2e4-cda5f8af6561"
                        }
                    ]
                }
            ],
            "redirectUrls": {
                "confirmUrl": f"https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder?userID={lah.userId()}",
                "cancelUrl": "https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder"
            }
        }
        
        header = genHeader(channelId, channelSecret, pathUrl, body, nonce)
        print(header)
        try:
            response = requests.post(f"{baseUrl}{pathUrl}", headers=header, json=body)
            response_data = response.json()
            payment_url = response_data["info"]["paymentUrl"]["web"]
            payload = [payloadcreator.startpay(payment_url)]
            lah.reply(lah.replyToken(), payload)
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "error", "message": str(e)})
    else:
        if lah.message().get("text") == "Checkout":
            payload = [
                {
                    "type": "text",
                    "text": "\u0E19\u0E35\u0E48\u0E04\u0E37\u0E2D\u0E23\u0E32\u0E22\u0E01\u0E32\u0E23\u0E2A\u0E31\u0E48\u0E07\u0E0B\u0E37\u0E49\u0E2D\u0E02\u0E2D\u0E07\u0E04\u0E38\u0E13 \u0E2B\u0E32\u0E01\u0E23\u0E32\u0E22\u0E01\u0E23\u0E39\u0E13\u0E0A\u0E33\u0E23\u0E30\u0E40\u0E07\u0E34\u0E19\u0E14\u0E49\u0E27\u0E22 Rabbit LINE Pay"
                },
                payloadcreator.checkout()
            ]
        else:
            payload = [{
                "type": "text",
                "text": "\u0E44\u0E21\u0E48\u0E40\u0E02\u0E49\u0E32\u0E43\u0E08\u0E04\u0E23\u0E31\u0E1A\u0E1A"
            }]
        
        try:
            lah.reply(lah.replyToken(), payload)
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
