import copy

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest,
)

from commons.datastore_client import DatastoreClient
from linepay.utils import request_payment


def handle_add_item_action(event, line_bot_api, postback_params):
    datastore_client = DatastoreClient()

    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )

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
    user_id = event.source.user_id
    if event.source.type == "user":
        datastore_client.add_user_items_action(
            user_id=user_id, item_name=item_name, item_price=item_price
        )
    elif event.source.type == "group":
        datastore_client.add_group_items_action(
            group_id=event.source.group_id,
            user_id=user_id, item_name=item_name, item_price=item_price
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
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )

    datastore_client = DatastoreClient()
    
    user_id = event.source.user_id
    group_id = event.source.group_id
    
    if event.source.type == "user":
        total_items, total_final_price, grouped_items = (
            datastore_client.calculate_user_items_in_basket(user_id=user_id)
        )    
    elif event.source.type == "group":
        total_items, total_final_price, grouped_items = (
            datastore_client.calculate_group_items_in_basket(group_id=group_id)
        )

    all_items_box = []
    box_product_template = open("templates/box_product_info.json").read()

    for item_name, details in grouped_items.items():
        box_product_info = copy.deepcopy(box_product_template)
        box_product_info = box_product_info.replace(
            "<PRODUCT_NAME>", f"{item_name} - จำนวน: {details['quantity']}"
        ).replace("<PRODUCT_PRICE>", f"{details['total_price']:.2f}")

        all_items_box.append(box_product_info)

    all_items_box_str = ",".join(all_items_box)
    flex_summary_order = open("templates/flex_summary_order.json").read()
    flex_summary_order = (
        flex_summary_order.replace("<BOX_PRODUCT_INFO_JSON>", all_items_box_str)
        .replace("<SUM_TOTAL_ITEMS>", total_items)
        .replace("<SUM_TOTAL_PRICE>", total_final_price)
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

    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    
    request_detail = {
                "amount": 250,
                "currency": "THB",
                "orderId": "001A",
                "packages": [
                    {
                        "id": "01A",
                        "amount": 250,
                        "name": "Toy Package",
                        "products": [
                            {
                                "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Cony",
                                "quantity": 1,
                                "price": 100,
                                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/512x512bb.jpg?alt=media&token=7cfd10b0-6d01-4612-b42e-b1b4d0105acd"
                            },
                            {
                                "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Sally",
                                "quantity": 1,
                                "price": 150,
                                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/8cd724371a6f169b977684fd69cc2339.jpg?alt=media&token=e2008ff7-1cad-4476-a2e4-cda5f8af6561"
                            }
                        ]
                    }
                ],
                "redirectUrls": {
                    "confirmUrl": f"https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder",
                    "cancelUrl": "https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder"
                }
            }
    result = request_payment(request_detail)
    print(result)   

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="ขอบคุณที่ใช้บริการ CJ ค่ะ"),
            ],
        )
    )
   


def handle_cancle_order_action(event, line_bot_api, postback_params):
    datastore_client = DatastoreClient()

    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    user_id = event.source.user_id
    if event.source.type == "user":
        datastore_client.remove_user_order(user_id=user_id)
    elif event.source.type == "group":
        datastore_client.remove_group_order(group_id=event.source.group_id)

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="ยกเลิกกรายการสั้งซื้อปัจุบัันของท่านเรียบร้อยค่ะ"),
            ],
        )
    )
                            
def handle_richmenu_switch_action(event, line_bot_api, postback_params):
    menu = postback_params.get("menu")
    user_id = event.source.user_id
    rich_menu_id_config = {
        "main": "richmenu-db38e9f92a3c898106dd4306626c8c75",
        "cj": "richmenu-4c7272287975fafd7d80fc36cbdb9062",
        "nine": "richmenu-ca6673b31843ae20592960f536fc0f5b",
        "uno": "richmenu-d612e6dc259ca897ed5650c60220fed2",
        "ahome": "richmenu-76cfc91852a3582ea42306ede1e5ab5d",
        "bao-cafe": "richmenu-ff6c0ba7302148ce1c0e158a205244e8",
    }
    rich_menu_id = rich_menu_id_config[menu]
    line_bot_api.link_rich_menu_id_to_user(user_id, rich_menu_id)


def handle_postback_by_action(event, line_bot_api, postback_action, postback_params):

    function_map = {
        "add_item": handle_add_item_action,
        "summary_order": handle_summary_order_action,
        "make_payment": handle_make_payment_action,
        "richmenuswitch": handle_richmenu_switch_action,
        "cancle_order": handle_cancle_order_action
    }
    if (postback_action is not None) and (postback_action in function_map):
        function_map[postback_action](event, line_bot_api, postback_params)
