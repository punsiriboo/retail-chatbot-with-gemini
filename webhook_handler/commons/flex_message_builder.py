import copy

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexContainer,
    FlexMessage,
    FlexCarousel,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    LocationAction,
)
from commons.datastore_client import DatastoreClient


def build_products_search_result_carousel(
    line_bot_api, event, response_dict, search_query, additional_explain=None
):
    with open("templates/flex_product_bubble.json") as file:
        product_bubble_temple = file.read()
        summary_text = response_dict["summary"]["summaryText"]

    result_products_list = []
    with open("templates/flex_product_bubble.json") as file:
        product_bubble_temple = file.read()

    for idx, result in enumerate(response_dict["results"]):
        product_name = result["document"]["structData"]["name"]
        product_price = result["document"]["structData"]["price"]
        product_image_url = result["document"]["structData"]["image_url"]
        product_sku = result["document"]["structData"]["sku"]

        product_bubble_json = (
            product_bubble_temple.replace("<PRODUCT_NAME>", product_name)
            .replace("<PRODUCT_PRICE>", str(product_price))
            .replace("<PRODUCT_IMAGE_URL>", product_image_url)
            .replace("<PRODUCT_SKU>", str(product_sku))
            .replace("<PRODUCT_NUMBER>", str(idx + 1))
        )

        result_products_list.append(FlexContainer.from_json(product_bubble_json))

    carousel_flex_message = FlexMessage(
        alt_text=f"ผลการค้นหาสินค้า: {search_query}",
        contents=FlexCarousel(
            type="carousel",
            contents=result_products_list,
        ),
    )

    messages_list = [
        TextMessage(text=summary_text),
        carousel_flex_message,
        TextMessage(
            text="คุณสามารถกดเพิ่มสินค้าในตระกร้าได้ สอบถามเกี่ยวกับสินค้าอื่นได้ หรือค้นหาสาขาใกล้เคียงได้เลยค่ะ",
            quick_reply=QuickReply(
                items=[
                    QuickReplyItem(
                        action=MessageAction(label="คุยกับน้อง CJ", text="คุยกับน้อง CJ")
                    ),
                    QuickReplyItem(action=LocationAction(label="ค้นหาสาขาใกล้เคียง")),
                ]
            ),
        ),
    ]
    if additional_explain:
        messages_list.insert(0, TextMessage(text=additional_explain))

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=messages_list)
    )


def build_flex_user_order_summary(sum_total_items, sum_total_price, grouped_items):
    all_items = []
    box_product_template = open("templates/box_product_info.json").read()
    for item_name, details in grouped_items.items():
        box_product_info = copy.deepcopy(box_product_template)
        item_total_price = f"{details['total_price']:.2f}"
        item_quantity = details["quantity"]
        box_product_info = box_product_info.replace(
            "<ITEM_NAME>", f"{item_name} - จำนวน: {item_quantity}"
        ).replace("<ITEM_TOTAL_PRICE>", item_total_price)

        all_items.append(box_product_info)

    box_product_info_json = ",".join(all_items)
    flex_summary_order = open("templates/flex_summary_order.json").read()
    flex_summary_order = (
        flex_summary_order.replace("<BOX_PRODUCT_INFO_JSON>", box_product_info_json)
        .replace("<SUM_TOTAL_ITEMS>", sum_total_items)
        .replace("<SUM_TOTAL_PRICE>", sum_total_price)
    )

    flex_summary_order_msg = FlexMessage(
        alt_text="สรุปการสั่งซื้อสินค้า",
        contents=FlexContainer.from_json(flex_summary_order),
    )

    return flex_summary_order_msg


def build_flex_group_order_summary(
    line_bot_api,
    group_id,
    total_items,
    total_final_price,
    user_items_summary,
    user_totals,
):
    box_product_template = open("templates/box_product_info.json").read()
    per_user_template = open("templates/flex_group_order_per_user_items.json").read()
    flex_group_order_carousel = open("templates/flex_group_order_carousel.json").read()

    all_user_flex = []
    for user_id, items_list in user_items_summary.items():
        try:
            profile = line_bot_api.get_group_member_profile(group_id, user_id)
            user_display_name = profile.display_name
            user_profile_url = (
                profile.picture_url
                if profile.picture_url
                else "https://storage.googleapis.com/line-cj-demo-chatboot/image/user.png"
            )
        except Exception as e:
            print(f"Error fetching LINE profile for user_id {user_id}: {str(e)}")
            user_display_name = "UNKNOW"
            user_profile_url = (
                "https://storage.googleapis.com/line-cj-demo-chatboot/image/user.png"
            )

        all_items = []
        for item in items_list:
            box_product_info = copy.deepcopy(box_product_template)
            item_name = item[0]
            item_quantity = item[1]
            item_total_price = item[2]
            box_product_info = box_product_info.replace(
                "<ITEM_NAME>", f"{item_name} - จำนวน: {item_quantity}"
            ).replace("<ITEM_TOTAL_PRICE>", item_total_price)

            all_items.append(box_product_info)

        box_product_info_json = ",".join(all_items)
        sum_total_items = str(user_totals[user_id]["total_items"])
        sum_total_price = f"{user_totals[user_id]['total_price']:.2f}"
        

        per_user_flex = copy.deepcopy(per_user_template)
        per_user_flex = (
            per_user_flex.replace("<USER_DISPLAY_NAME>", user_display_name)
            .replace("<USER_PROFILE_URL>", user_profile_url)
            .replace("<SUM_TOTAL_ITEMS>", sum_total_items)
            .replace("<SUM_TOTAL_PRICE>", sum_total_price)
            .replace("<BOX_PRODUCT_INFO_JSON>", box_product_info_json)
        )
        
        all_user_flex.append(per_user_flex)

    all_user_bubble_json = ",".join(all_user_flex)
    flex_group_order_carousel = (
        flex_group_order_carousel.replace(
            "<ALL_USER_ORDER_BUBBLE_JSON>", all_user_bubble_json
        )
        .replace("<TOTAL_ITEMS>", total_items)
        .replace("<TOTAL_PRICE>", total_final_price)
    )

    flex_summary_order_msg = FlexMessage(
        alt_text="สรุปการสั่งซื้อสินค้า",
        contents=FlexContainer.from_json(flex_group_order_carousel),
    )
    
    datastore_client = DatastoreClient()
    datastore_client.create_group_pay_own(group_id=group_id, user_totals=user_totals)

    return flex_summary_order_msg
