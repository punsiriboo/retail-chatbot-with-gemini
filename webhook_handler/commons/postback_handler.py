from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)


def handle_add_item_action(event, line_bot_api, postback_params):
    item_name = postback_params.get("item_name")
    item_image_url = postback_params.get("item_image_url")
    item_price = postback_params.get("item_price")
    flex_add_to_basket = open("templates/flex_add_to_basket.json").read()
    flex_add_to_basket = (
        flex_add_to_basket.replace("<PRODUCT_NAME>", item_name)
        .replace("<PRODUCT_IMAGE_URL>", item_image_url)
        .replace("<PRODUCT_PRICE>", item_price)
    )
    flex_add_to_basket_msg = FlexMessage(
        alt_text=f"สั่งซื้อสินค้า: {item_name}",
        contents=FlexContainer.from_json(flex_add_to_basket),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="เพิ่มรายการสินค้าเรียบร้อยค่ะ"),
                flex_add_to_basket_msg,
            ],
        )
    )


def handle_summary_order_action(event, line_bot_api, postback_params):
    item_name = postback_params.get("item_name")
    item_price = postback_params.get("item_price")

    box_product_info = open("templates/box_product_info.json").read()
    flex_summary_order = open("templates/flex_summary_order.json").read()
    box_product_info = box_product_info.replace("<PRODUCT_NAME>", item_name).replace(
        "<PRODUCT_PRICE>", item_price
    )
    flex_summary_order = flex_summary_order.replace(
        "<BOX_PRODUCT_INFO_JSON>", box_product_info
    )
    flex_summary_order_msg = FlexMessage(
        alt_text="สรุปการสั้งซื้อสินค้า",
        contents=FlexContainer.from_json(flex_summary_order),
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


def handle_make_payment_action(event, line_bot_api, postback_params):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="ขอบคุณที่ใช้บริการ CJ ค่ะ"),
            ],
        )
    )


def handle_postback_by_action(event, line_bot_api, postback_action, postback_params):

    function_map = {
        "add_item": handle_add_item_action,
        "summary_order": handle_summary_order_action,
        "make_payment": handle_make_payment_action,
    }
    if (postback_action is not None) and (postback_action in function_map):
        function_map[postback_action](event, line_bot_api, postback_params)