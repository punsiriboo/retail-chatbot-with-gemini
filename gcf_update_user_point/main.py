import os
import json
from google.cloud import datastore
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    FlexMessage,
    FlexContainer,
)


def handler_request(request):
    # Initialize response headers for CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',  # Allow all origins
        'Content-Type': 'application/json'
    }

    request_json = request.get_json(silent=True)
    print(str(request_json))
    
    if not request_json:
        return ("Invalid request: JSON body required", 400, headers)

    refer_name = update_user_point(request_json)
    return (json.dumps({"message": "Success", "referedUser":refer_name }), 200, headers)
    

def update_user_point(request_json):
    CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
    configuration = Configuration(
        access_token=CHANNEL_ACCESS_TOKEN,
    )
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)

    # Extract required fields
    type = request_json.get("type")

    if type == "referal":
        
        user_id = request_json.get("user_id")
        refer_id = request_json.get("refer_id")
        
        update_entity(refer_id)
        refer_profile = line_bot_api.get_profile(user_id=refer_id)
        profile = line_bot_api.get_profile(user_id=user_id)

        flex_msg = open("templates/sabai_card_refer_success.json").read()
        flex_msg = flex_msg.replace("<YOUR_FRIEND_NAME>", profile.display_name)

        flex_refer_succuss = FlexMessage(
            alt_text="คุณได้รับแต้มจากการแนะนำเพื่อน",
            contents=FlexContainer.from_json(flex_msg),
        )
        line_bot_api.push_message(
            PushMessageRequest(
                to=refer_id,
                messages=[flex_refer_succuss],
            )
        )
        return refer_profile.display_name
        
       

def update_entity(refer_id):
    """Update an existing entity."""
    datastore_client = datastore.Client()
    with datastore_client.transaction():
        key = datastore_client.key("CJ_USER", refer_id)
        entity = datastore_client.get(key)
        print(entity)
        if entity:  # If entity exists
            if 'point' in entity:
                entity['point'] += 10
            else:
                entity['point'] = 10  
        datastore_client.put(entity)
