import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ShowLoadingAnimationRequest,
)


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
LINE_USER_ID = os.environ["LINE_USER_ID"]

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN,
)

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

line_bot_api.show_loading_animation_with_http_info(
    ShowLoadingAnimationRequest(chat_id=LINE_USER_ID)
)
