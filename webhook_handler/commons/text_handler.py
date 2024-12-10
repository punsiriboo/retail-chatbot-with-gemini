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


def handle_text_by_keyword(event, line_bot_api):
    text = event.message.text

    if text == "ค้นหาคูปองส่วนลด":
        with open("privates/data/coupons.json") as file:
            coupons_data = json.load(file)
        list_img_carousel_column = []
        for campaign in coupons_data["campaigns"][:10]:
            img_carousel_column = ImageCarouselColumn(
                image_url=campaign["image_thumbnail_path"],
                action=PostbackAction(label="เก็บคูปอง", data="ping", text="ping"),
            )
            list_img_carousel_column.append(img_carousel_column)

        image_carousel_template = ImageCarouselTemplate(
            columns=list_img_carousel_column
        )
        template_message = TemplateMessage(
            alt_text="คูปองสินค้า CJ", template=image_carousel_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[template_message]
            )
        )

    elif text == "ค้นหาสาขา":
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
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(alt_text="กรุณากด share location", contents=bubble)
                ],
            )
        )

    elif text == "ค้นหาสินค้า":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="คุณสามารถพิมพ์ชื่อสินค้าที่ต้องการ หรือ ส่งรูปสินค้าที่ต้องการค้นหาได้",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(action=CameraAction(label="ถ่ายรูปภาพ")),
                                QuickReplyItem(
                                    action=CameraRollAction(label="ส่งรูปภาพ")
                                ),
                            ]
                        ),
                    )
                ],
            )
        )

    elif text == "คุยกับน้อง CJ":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="สวัสดีค่ะ ยินดีต้อนรับสู่ร้านค้า​ CJ MORE มีอะไรให้ช่วยเหลือไหมคะ? คุณสามารถพิมพ์สอบถามเกี่ยวกับ CJ หรือ พิมพ์ #ค้นหา ตามด้วยชื่อสินค้าได้เลยตค่ะ เช่น #ค้นหาน้ำดื่ม"
                    ),
                ],
            )
        )

    elif text == "อยากรู้เกี่ยวกับแอคเน่แอดมอยส์เจอร์โลชั่น":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="แอคเน่แอดมอยส์เจอร์โลชั่นเป็นโลชั่นบำรุงผิวหน้าที่ช่วยเพิ่มความชุ่มชื้น ให้แก้ผิวและปกป้องผิวจากความแห้งกร้าน โดยไม่ก่อให้เกิดการอุดตันรูขุมขน มีส่วนผสมของ Acnecare Bio ที่ถูกพัฒนาเป็นพิเศษสำหรับผิวเป็นสิวง่าย ช่วยควบคุมการผลิตน้ำมัน และยังมีส่วนผสมของ Salicylic Acid และ Glycolic Acid ที่ช่วยปรับสภาพผิวให้รู้สึกได้ถึงผิวที่เรียบเนียน"
                    )
                ],
            )
        )

    elif text == "show_loading_animation":
        line_bot_api.show_loading_animation_with_http_info(
            ShowLoadingAnimationRequest(chat_id=event.source.user_id)
        )
        line_bot_api.show_loading_animation_with_http_info(
            ShowLoadingAnimationRequest(chat_id=event.source.user_id)
        )

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
