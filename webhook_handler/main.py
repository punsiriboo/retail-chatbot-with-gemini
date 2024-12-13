import os
import functions_framework
from urllib.parse import parse_qs

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    AudioMessageContent,
    PostbackEvent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    StickerMessage,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest,
)


from commons.gcs_utils import upload_blob_from_memory
from commons.text_handler import handle_text_by_keyword
from commons.branch_location_search import search_closest_branches
from commons.gemini_image_understanding import gemini_describe_image
from commons.vertex_agent_search import vertex_search_retail_products
from commons.flex_message_builder import build_flex_carousel_message
from commons.audio_to_text import transcribe
from commons.postback_handler import handle_postback_by_action


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]


configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN,
)
handler = WebhookHandler(CHANNEL_SECRET)

# Create a global API client instance
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
line_bot_blob_api = MessagingApiBlob(api_client)


@functions_framework.http
def callback(request):
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    handle_text_by_keyword(event, line_bot_api)


@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )

    message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
    upload_blob_from_memory(
        contents=message_content,
        user_id=event.source.user_id,
        message_id=event.message.id,
        type="image",
    )

    json, image_description = gemini_describe_image(
        user_id=event.source.user_id,
        message_id=event.message.id,
    )

    if image_description:
        line_bot_api.push_message(
            PushMessageRequest(
                to=event.source.user_id,
                messages=[TextMessage(text=str(json))],
            )
        )

        response_dict = vertex_search_retail_products(
            image_description["product_description"]
        )
        build_flex_carousel_message(
            line_bot_api=line_bot_api,
            event=event,
            response_dict=response_dict,
            search_query=image_description["product_description"],
            additional_explain=image_description["explaination"],
        )


@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    audio_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
    upload_blob_from_memory(
        contents=audio_content,
        user_id=event.source.user_id,
        message_id=event.message.id,
        type="audio",
    )

    text = transcribe(content=audio_content)
    print("Audio" + text)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, messages=[TextMessage(text="audio sent ;0")]
        )
    )


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )

    latitude = event.message.latitude
    longitude = event.message.longitude
    search_closest_branches(
        user_lat=latitude, user_lng=longitude, event=event, line_bot_api=line_bot_api
    )


@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                StickerMessage(
                    package_id=event.message.package_id,
                    sticker_id=event.message.sticker_id,
                )
            ],
        )
    )


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    postback_params = {
        key: value[0] for key, value in parse_qs(event.postback.data).items()
    }
    postback_action = postback_params.get("action")
    handle_postback_by_action(event, line_bot_api, postback_action, postback_params)
