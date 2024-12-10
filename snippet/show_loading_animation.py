import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ShowLoadingAnimationRequest,
)


YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
LINE_USER_ID = os.environ["LINE_USER_ID"]

configuration = Configuration(
    access_token=YOUR_CHANNEL_ACCESS_TOKEN,
)

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

line_bot_api.show_loading_animation_with_http_info(
    ShowLoadingAnimationRequest(chat_id=LINE_USER_ID)
)