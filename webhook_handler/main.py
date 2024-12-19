import os
import functions_framework

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
    BeaconEvent,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    MemberJoinedEvent,
)

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    StickerMessage,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest,
    MentionSubstitutionObject,
    TextMessageV2,
    UserMentionTarget,
)


from commons.gcs_utils import upload_blob_from_memory
from commons.branch_location_search import search_closest_branches
from commons.gemini_image_understanding import gemini_describe_image
from commons.vertex_agent_search import vertex_search_retail_products
from commons.flex_message_builder import build_products_search_result_carousel
from commons.audio_to_text import transcribe

from commons.handler_text import handle_text_by_keyword
from commons.handler_postback import PostbackHandler
from commons.handler_beacon import handle_beacon_by_user_profile
from commons.datastore_client import DatastoreClient


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

    image_description = gemini_describe_image(
        user_id=event.source.user_id,
        message_id=event.message.id,
    )

    if image_description:
        response_dict = vertex_search_retail_products(
            image_description["product_description"]
        )
        build_products_search_result_carousel(
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
    posback_handler = PostbackHandler(line_bot_api, event)
    posback_handler.handle_postback_by_action()


@handler.add(BeaconEvent)
def handle_beacon(event: BeaconEvent):
    handle_beacon_by_user_profile(event, line_bot_api)


@handler.add(FollowEvent)
def handle_follow(event):
    print("Got Follow event:" + event.source.user_id)
    flex_temple = open("templates/static/about_cj_more.json").read()
    profile = line_bot_api.get_profile(user_id=event.source.user_id)
    if event.follow.is_unblocked:
        text_message = TextMessage(
            text="สวัสดีค่ะ คุณ "
            + profile.display_name
            + " ยินดีต้อนรับกลับเข้าสู่แชทบอทของ​ CJ MORE! อีกครั้งนะค่ะ\n\nแชทบอท 'น้อง CJ' 👧🏻 จะขอเป็นผู้ช่วยของคุณในการ Shopping แนะนำสินค้าของเรา"
        )

    else:
        text_message = TextMessage(
            text="สวัสดีค่ะ คุณ "
            + profile.display_name
            + " ยินดีต้อนรับสู่​ CR MORE! แชทบอท 'น้อง CJ' 👧🏻 \nจะขอเป็นผู้ช่วยของคุณในการ Shopping แนะนำสินค้าของเรา เพราะเราเป็นมากกว่ามากกว่าซูเปอร์มาร์เก็ต"
        )

    static_flex_message = FlexMessage(
        alt_text="สวัสดีค่ะ ยินดีต้อนรับสู่​ CJ MORE!",
        contents=FlexContainer.from_json(flex_temple),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                text_message,
                static_flex_message,
            ],
        )
    )


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print("Got Unfollow event:" + event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    flex_temple = open("templates/static/nong_cj_feature.json").read()

    static_flex_message = FlexMessage(
        alt_text="สวัสดีค่ะ ยินดีต้อนรับสู่​ CJ MORE!",
        contents=FlexContainer.from_json(flex_temple),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="สวัสดีค่ะ น้อง CJ ยินดีให้บริการ 👧🏻\n คุณสามารถพิมพ์ #ค้นหาตามด้วยชื่อสินค้า\nค้นหา และshoping สินค้าแบบกลุ่มได้ค่ะ"
                ),
                static_flex_message,
            ],
        )
    )


@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    joined_members = event.joined.members
    print(joined_members)
    user_id = joined_members[0].user_id
    
    group_id = event.source.group_id
    datastore_client = DatastoreClient()
    datastore_client.add_user_to_group(group_id, user_id)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessageV2(
                    text="สวัสดีค่ะ คุณ {new_group_member}, ยินดีต้อนรับเข้ากลุ่ม หาต้องการสั่งซื็อสินค้าแบบกลุ่ม สามารถพิมพ์ #ค้นหาตามด้วยชื่อสินค้า หรือส่งรูปสินค้าได้เลยค่ะ",
                    substitution={
                        "new_group_member": MentionSubstitutionObject(
                            mentionee=UserMentionTarget(group_id, user_id)
                        )
                    },
                )
            ],
        )
    )
