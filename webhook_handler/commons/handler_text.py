import json
from commons.vertex_agent_search import vertex_search_retail_products
from commons.dialogflowcx_answer import detect_intent_text
from commons.flex_message_builder import build_products_search_result_carousel
from commons.datastore_client import DatastoreClient

from config.keyword_to_flex_mapping import (
    keyword_flex_temple_config as flex_temple_config,
)
from commons.flex_message_builder import build_flex_user_order_summary

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    FlexMessage,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexButton,
    FlexContainer,
    URIAction,
    PostbackAction,
    QuickReplyItem,
    QuickReply,
    MessageAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
)


def handle_coupon_search(line_bot_api, event, text):
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
        ReplyMessageRequest(reply_token=event.reply_token, messages=[template_message])
    )


def handle_branch_search(line_bot_api, event, text):
    bubble = FlexBubble(
        direction="ltr",
        hero=FlexImage(
            url="https://storage.googleapis.com/line-cj-demo-chatboot/image/branch-search.png",
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
            messages=[FlexMessage(alt_text="กรุณากด share location", contents=bubble)],
        )
    )


def handle_talk_to_cj(line_bot_api, event, text):
    flex_temple = open("templates/static/nong_cj_feature.json").read()
    static_flex_message = FlexMessage(
        alt_text="สวัสดีค่ะ ยินดีต้อนรับสู่​ CJ MORE!",
        contents=FlexContainer.from_json(flex_temple),
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                static_flex_message,
                TextMessage(
                    text="สวัสดีค่ะ ยินดีต้อนรับสู่ร้านค้า​ CJ MORE มีอะไรให้ช่วยเหลือไหมคะ?"
                    + "\n\nคุณสามารถพิมพ์สอบถามเกี่ยวกับ CJ หรือ พิมพ์ #ค้นหา ตามด้วยชื่อสินค้าได้เลยตค่ะ เช่น #ค้นหาน้ำดื่ม"
                    + "\nหรือสามารถคุยเล่นทั่วไปสอบถามน้อง CJ ได้เลยค่ะ"
                ),
            ],
        )
    )


def handle_return_static_flex(line_bot_api, event, template_name):

    print("handle_return_static_flex: " + template_name)
    with open(f"templates/static/{template_name}.json") as file:
        flex_temple = file.read()

    static_flex_message = FlexMessage(
        alt_text=template_name,
        contents=FlexContainer.from_json(flex_temple),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                static_flex_message,
            ],
        )
    )


def handle_nong_cj_leave_group(line_bot_api, event, text):
    if event.source.type == "group":
        line_bot_api.leave_group(event.source.group_id)
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Feature นี้ใช้ได้ เมื่อเชิญ น้อง​​ CJ เข้ากลุ่มแล้วเท่านั้นค่ะ"),
                ],
            )
        )


def handle_search_example(line_bot_api, event, text):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="พิมพ์ว่า #ค้นหา ตามด้วยสินค้าได้เลย เช่น #ค้นหาลิปมัน"),
            ],
        )
    )


def handle_calling_nong_cj(line_bot_api, event, text):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="อยากให้น้อง CJ ช่วยอะไรดีค่ะ",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyItem(
                                action=MessageAction(
                                    label="ดูโปรล่าสุด", text="[CJ] สินค้าลดกระหน่ำ 7 วัน"
                                )
                            ),
                            QuickReplyItem(
                                action=MessageAction(
                                    label="ค้นหาคูปองส่วนลด", text="ค้นหาคูปองส่วนลด"
                                )
                            ),
                            QuickReplyItem(
                                action=CameraAction(label="ส่งรูปสินค้าที่ต้องการค้นหา")
                            ),
                            QuickReplyItem(
                                action=CameraRollAction(label="ถ่ายรูปสินค้าที่ต้องการค้นหา")
                            ),
                            QuickReplyItem(action=LocationAction(label="ค้นหาสาขา")),
                        ]
                    ),
                )
            ],
        )
    )


def handle_my_basket_check(line_bot_api, event, text):
    datastore_client = DatastoreClient()
    order = datastore_client.get_user_order(user_id=event.source.user_id)
    if order:
        total_items, total_final_price, grouped_items = (
            datastore_client.calculate_user_items_in_basket(
                user_id=event.source.user_id
            )
        )
        flex_summary_order_msg = build_flex_user_order_summary(
            total_items, total_final_price, grouped_items
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    flex_summary_order_msg,
                    TextMessage(text="กดจ่ายเงิน หรือพิมพ์คุยกับน้อง CJ เพื่อเพิ่มสินค้าได้ค่ะ"),
                ],
            )
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="คุณยังไม่มีรายการสั่งซื้อในตระกร้าค่ะ",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label="พิมพ์เพื่อค้นหาสินค้า",
                                        text="ลองค้นหาสินค้ากับน้อง CJ",
                                    )
                                ),
                                QuickReplyItem(
                                    action=CameraAction(label="ส่งรูปสินค้าที่ต้องการค้นหา")
                                ),
                                QuickReplyItem(
                                    action=CameraRollAction(
                                        label="ถ่ายรูปสินค้าที่ต้องการค้นหา"
                                    )
                                ),
                            ]
                        ),
                    ),
                ],
            )
        )
        
def handle_done_register_member(line_bot_api, event, text):
    template_name = "nine_hot_promotion"
    with open(f"templates/static/{template_name}.json") as file:
        flex_temple = file.read()

    static_flex_message = FlexMessage(
        alt_text=template_name,
        contents=FlexContainer.from_json(flex_temple),
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="ขอบคุณที่สมัครสมาชิกสบายการ์ดนะคะ คุณสามารถดูส่วนลดล่าสุด และ shopping กับเราได้เลยค่ะ",
                ),
                static_flex_message
            ],
        )
    )
    
def handle_text_by_keyword(event, line_bot_api):
    text = event.message.text
    function_map = {
        "คูปองส่วนลด": handle_coupon_search,
        "ค้นหาคูปอง": handle_coupon_search,
        "ค้นหาสาขา": handle_branch_search,
        "คุยกับน้อง CJ": handle_talk_to_cj,
        "#น้องCJออกไป": handle_nong_cj_leave_group,
        "ลองค้นหาสินค้ากับน้อง CJ": handle_search_example,
        "น้อง​ CJ": handle_calling_nong_cj,
        "น้อง​CJ": handle_calling_nong_cj,
        "ตระกร้าของฉัน": handle_my_basket_check,
        "CJ_MEMBER:สมัครสมาชิก CJ สำเร็จแล้วค่ะ": handle_done_register_member,
    }
    if text in function_map:
        function_map[text](line_bot_api, event, text)

    elif text in flex_temple_config:
        template_name = flex_temple_config[text]
        handle_return_static_flex(line_bot_api, event, template_name)

    elif text.startswith("#ค้นหา"):
        search_query = text[len("#ค้นหา") :].strip()
        response_dict = vertex_search_retail_products(search_query)
        build_products_search_result_carousel(
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
