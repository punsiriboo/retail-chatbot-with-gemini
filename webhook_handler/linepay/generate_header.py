import uuid
import hmac
import hashlib
import base64
import json

def generate_nonce():
    return str(uuid.uuid4())

def gen_header(channel_id, channel_secret, url, request_detail, nonce):
    if not isinstance(request_detail, str):
        request_detail = json.dumps(request_detail)  # Convert to JSON string if not already a string
    
    # Combine data as per the specified format
    data = f"{channel_secret}{url}{request_detail}{nonce}"
    
    # Generate HMAC SHA256 signature
    signature = hmac.new(
        key=channel_secret.encode('utf-8'),
        msg=data.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Encode the signature in base64
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    
    # Return the required headers
    return {
        "Content-Type": "application/json",
        "X-LINE-ChannelId": channel_id,
        "X-LINE-Authorization-Nonce": nonce,
        "X-LINE-Authorization": encoded_signature
    }

# Example usage
paynonce = generate_nonce()
channel_id = "2006680425"
channel_secret = "54c3aefd19225d8c05e5445902bf9461"
url = "https://sandbox-api-pay.line.me"
request_detail = {"key": "value"}  # Replace with actual request detail

headers = gen_header(channel_id, channel_secret, url, request_detail, paynonce)
print(headers)