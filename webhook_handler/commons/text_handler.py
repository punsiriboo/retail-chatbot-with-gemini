import json

from commons.vertex_agent_search import vertex_search_retail_products
from commons.dialogflowcx_answer import detect_intent_text
from commons.flex_message_builder import build_flex_carousel_message

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    MessageAction,
    URIAction,
    PostbackAction,
    CameraAction,
    CameraRollAction,
    ShowLoadingAnimationRequest,
)


with open("privates/data/image_paths.json") as file:
    image_paths = json.load(file)


def handle_coupon_search(line_bot_api, reply_token):
    with open("privates/data/coupons.json") as file:
        coupons_data = json.load(file)
    list_img_carousel_column = []
    for campaign in coupons_data["campaigns"][:10]:
        img_carousel_column = ImageCarouselColumn(
            image_url=campaign["image_thumbnail_path"],
            action=PostbackAction(label="เก็บคูปอง", data="ping", text="ping"),
        )
        list_img_carousel_column.append(img_carousel_column)

    image_carousel_template = ImageCarouselTemplate(columns=list_img_carousel_column)
    template_message = TemplateMessage(
        alt_text="คูปองสินค้า CJ", template=image_carousel_template
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[template_message])
    )


def handle_branch_search(line_bot_api, reply_token):
    bubble = FlexBubble(
        direction="ltr",
        hero=FlexImage(
            url=image_paths["location_service"],
            size="full",
            aspect_ratio="20:13",
            aspect_mode="cover",
        ),
        body=FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="ค้นหาสาขา CJ Express", weight="bold", size="md"),
            ],
        ),
        footer=FlexBox(
            layout="vertical",
            spacing="sm",
            contents=[
                FlexButton(
                    style="primary",
                    height="sm",
                    color="#2E7B22FF",
                    action=URIAction(
                        label="Share loaction", uri="https://line.me/R/nv/location/"
                    ),
                )
            ],
        ),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="กรุณากด share location", contents=bubble)],
        )
    )


def handle_talk_to_cj(line_bot_api, reply_token):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                TextMessage(
                    text="สวัสดีค่ะ ยินดีต้อนรับสู่ร้านค้า​ CJ MORE มีอะไรให้ช่วยเหลือไหมคะ? คุณสามารถพิมพ์สอบถามเกี่ยวกับ CJ หรือ พิมพ์ #ค้นหา ตามด้วยชื่อสินค้าได้เลยตค่ะ เช่น #ค้นหาน้ำดื่ม"
                ),
            ],
        )
    )


def handle_return_static_flex(line_bot_api, reply_token, template_name):
    with open(f"templates/static/{template_name}.json") as file:
        flex_temple = file.read()

    static_flex_message = FlexMessage(
        alt_text=template_name,
        contents=FlexContainer.from_json(flex_temple),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                static_flex_message,
            ],
        )
    )


def handle_text_by_keyword(event, line_bot_api):
    text = event.message.text
    reply_token = event.reply_token
    function_map = {
        "ค้นหาคูปองส่วนลด": handle_coupon_search,
        "ค้นหาสาขา": handle_branch_search,
        "คุยกับน้อง CJ": handle_talk_to_cj,
        "[CJ] ลดสนั้น 7 วัน": handle_return_static_flex(
            line_bot_api, reply_token, "seven_days_discount"
        ),
        "[CJ] สินค้าลดกระหน่ำ 7 วัน" : handle_return_static_flex(
            line_bot_api, reply_token, "seven_days_discount_product"
        ),
        "[CJ] 2024 Recap": handle_return_static_flex(
            line_bot_api, reply_token, "recap_2024"
        ),
        "[Nine] โปรไฟลุก": handle_return_static_flex(
            line_bot_api, reply_token, "nine_hot_promotion"
        ),
        "[Nine] ไอเทมหน้าหนาว": handle_return_static_flex(
            line_bot_api, reply_token, "nine_winner"
        ),
        "[Nine] ติดตามข่าวสาร": handle_return_static_flex(
            line_bot_api, reply_token, "nine_news"
        ),
        "[Nine] หมอลำเฟส": handle_return_static_flex(
            line_bot_api, reply_token, "nine_dancing_fastival"
        ),
        "[UNO] Power Puff Girls": handle_return_static_flex(
            line_bot_api, reply_token, "uno_power_puff_girls"
        ),
        "[UNO] Claim Free Bag": handle_return_static_flex(
            line_bot_api, reply_token, "uno_claim_free_bag"
        ),
        "[UNO] 12.12 Sale": handle_return_static_flex(
            line_bot_api, reply_token, "uno_12_12_sale"
        ),
        "UNO] XMas Party": handle_return_static_flex(
            line_bot_api, reply_token, "uno_marry_xmas"
        ),
        "[BAO] MarryXMas": handle_return_static_flex(
            line_bot_api, reply_token, "bao_marry_xmas"
        ),
        "[BAO] Drink Menu": handle_return_static_flex(
            line_bot_api, reply_token, "bao_drink_menu"
        ),
        "[BAO] Chocolate Dubai": handle_return_static_flex(
            line_bot_api, reply_token, "bao_chocolate_dubai"
        ),
        "[BAO] Duo yummy": handle_return_static_flex(
            line_bot_api, reply_token, "bao_duo_yummy"
        ),
        "[AHOME] ติดตามข่าวสาร": handle_return_static_flex(
            line_bot_api, reply_token, "ahome_news"
        ),
        "[AHOME] Toy Story": handle_return_static_flex(
            line_bot_api, reply_token, "ahome_toy_story"
        ),
        "[AHOME] เครื่องใช้ไฟฟ้าในบ้าน": handle_return_static_flex(
            line_bot_api, reply_token, "ahome_in_house_product"
        ),
        "[AHOME] Car Lover Promotion": handle_return_static_flex(
            line_bot_api, reply_token, "ahome_car_lover_promotion"
        ),
        
    }
    if text in function_map:
        function_map[text](line_bot_api, reply_token)

    elif text.startswith("#ค้นหา"):
        search_query = text[len("#ค้นหา") :].strip()
        response_dict = vertex_search_retail_products(search_query)
        build_flex_carousel_message(
            line_bot_api=line_bot_api,
            event=event,
            response_dict=response_dict,
            search_query=search_query,
        )
    else:
        response_text = detect_intent_text(text=text, session_id=event.source.user_id)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)],
            )
        )
