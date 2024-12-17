import copy
from urllib.parse import parse_qs
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    TextMessageV2,
    MentionSubstitutionObject,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
    UserMentionTarget
)
from commons.datastore_client import DatastoreClient
from linepay.utils import request_payment


class PostbackHandler:
    def __init__(self, line_bot_api, event):
        self.line_bot_api = line_bot_api
        self.event = event
        self.reply_token = event.reply_token
        self.postback_params = {
            key: value[0] for key, value in parse_qs(event.postback.data).items()
        }
        self.datastore_client = DatastoreClient()
        self.rich_menu_id_config = {
            "main": "richmenu-db38e9f92a3c898106dd4306626c8c75",
            "cj": "richmenu-4c7272287975fafd7d80fc36cbdb9062",
            "nine": "richmenu-ca6673b31843ae20592960f536fc0f5b",
            "uno": "richmenu-d612e6dc259ca897ed5650c60220fed2",
            "ahome": "richmenu-76cfc91852a3582ea42306ede1e5ab5d",
            "bao-cafe": "richmenu-ff6c0ba7302148ce1c0e158a205244e8",
        }

    def show_loading(self):
        self.line_bot_api.show_loading_animation_with_http_info(
            ShowLoadingAnimationRequest(chat_id=self.event.source.user_id)
        )

    def handle_add_item_action(self):
        item_name = self.postback_params.get("item_name")
        item_image_url = self.postback_params.get("item_image_url")
        item_price = self.postback_params.get("item_price")

        user_id = self.event.source.user_id
        if self.event.source.type == "user":
            self.show_loading()
            self.datastore_client.add_user_items_action(
                user_id=user_id, item_name=item_name, item_price=item_price
            )
        elif self.event.source.type == "group":
            self.datastore_client.add_group_items_action(
                group_id=self.event.source.group_id,
                user_id=user_id,
                item_name=item_name,
                item_price=item_price,
            )
        
        flex_add_to_basket = open("templates/flex_add_to_basket.json").read()

        flex_add_to_basket = (
            flex_add_to_basket.replace("<ITEM_NAME>", item_name)
            .replace("<ITEM_IMAGE_URL>", item_image_url)
            .replace("<ITEM_PRICE>", item_price)
        )
        flex_add_to_basket_msg = FlexMessage(
            alt_text=f"สั่งซื้อสินค้า: {item_name}",
            contents=FlexContainer.from_json(flex_add_to_basket),
        )

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.event.reply_token,
                messages=[
                    TextMessage(text="เพิ่มรายการสินค้าเรียบร้อยค่ะ"),
                    flex_add_to_basket_msg,
                ],
            )
        )

    def handle_summary_order_action(self):
        if self.event.source.type == "user":
            user_id = self.event.source.user_id
            self.show_loading()

            sum_total_items, sum_total_price, grouped_items = (
                self.datastore_client.calculate_user_items_in_basket(user_id=user_id)
            )
            
            all_items = []
            box_product_template = open("templates/box_product_info.json").read()
            for item_name, details in grouped_items.items():
                box_product_info = copy.deepcopy(box_product_template)
                item_total_price = f"{details['total_price']:.2f}"
                item_quantity = details['quantity']
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
                alt_text="สรุปการสั้งซื้อสินค้า",
                contents=FlexContainer.from_json(flex_summary_order),
            )

            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.event.reply_token,
                    messages=[
                        flex_summary_order_msg,
                        TextMessage(text="กดจ่ายเงิน หรือพิมพ์คุยกับน้อง CJ เพื่อเพิ่มสินค้าได้ค่ะ"),
                    ],
                )
            )

        elif self.event.source.type == "group":
            group_id = self.event.source.group_id
            total_items, total_final_price, user_items_summary, user_totals = (
                self.datastore_client.calculate_group_items_in_basket(group_id)
            )

            box_product_template = open("templates/box_product_info.json").read()
            per_user_template = open("templates/flex_group_order_per_user_items.json").read()
            flex_group_order_carousel = open(
                "templates/flex_group_order_carousel.json"
            ).read()

            all_user_flex = []
            for user_id, items_list in user_items_summary.items():
                try:   
                    profile = self.line_bot_api.get_group_member_profile(group_id, user_id)
                    user_display_name = profile.display_name
                    user_profile_url = (
                        profile.picture_url
                        if profile.picture_url
                        else "https://storage.googleapis.com/line-cj-demo-chatboot/image/user.png"
                    )
                except Exception as e:
                    print(f"Error fetching LINE profile for user_id {user_id}: {str(e)}")
                    user_display_name = "UNKNOW"
                    user_profile_url = "https://storage.googleapis.com/line-cj-demo-chatboot/image/user.png"

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
                    .replace("<SUM_TOTAL_ITEMS>",sum_total_items)
                    .replace("<SUM_TOTAL_PRICE>", sum_total_price)
                    .replace("<BOX_PRODUCT_INFO_JSON>", box_product_info_json)
                )

                all_user_flex.append(per_user_flex)

            all_user_bubble_json = ",".join(all_user_flex)
            flex_group_order_carousel = (
                flex_group_order_carousel.replace("<ALL_USER_ORDER_BUBBLE_JSON>", all_user_bubble_json)
                .replace("<TOTAL_ITEMS>", total_items)
                .replace("<TOTAL_PRICE>", total_final_price)
            )

            flex_summary_order_msg = FlexMessage(
                alt_text="สรุปการสั้งซื้อสินค้า",
                contents=FlexContainer.from_json(flex_group_order_carousel),
            )

            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.event.reply_token,
                    messages=[
                        flex_summary_order_msg,
                        TextMessage(text="กรุณาเลือกวิธีการจ่ายเงิน หรือพิมพ์คุยกับน้อง CJ เพื่อเพิ่มสินค้าได้ค่ะ"),
                    ],
                )
            )

    def handle_make_user_payment_action(self):
        self.show_loading()

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
                            "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/512x512bb.jpg?alt=media&token=7cfd10b0-6d01-4612-b42e-b1b4d0105acd",
                        },
                        {
                            "name": "\u0E15\u0E38\u0E4A\u0E01\u0E15\u0E32 Sally",
                            "quantity": 1,
                            "price": 150,
                            "imageUrl": "https://firebasestorage.googleapis.com/v0/b/linedeveloper-63341.appspot.com/o/8cd724371a6f169b977684fd69cc2339.jpg?alt=media&token=e2008ff7-1cad-4476-a2e4-cda5f8af6561",
                        },
                    ],
                }
            ],
            "redirectUrls": {
                "confirmUrl": f"https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder",
                "cancelUrl": "https://us-central1-linedeveloper-63341.cloudfunctions.net/confirmOrder",
            },
        }
        result = request_payment(request_detail)
        print(result)

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.event.reply_token,
                messages=[
                    TextMessage(text="ขอบคุณที่ใช้บริการ CJ ค่ะ"),
                ],
            )
        )

    def handle_make_group_payment_action(self):
        type = self.postback_params.get("type")
        group_id = self.event.source.group_id

        if type == "pay_equally":
            total_price = self.postback_params.get("total_price")
            member_count = self.line_bot_api.get_group_member_count(group_id)
            pay_each = float(total_price)/int(member_count.count)
            
            user_ids = self.datastore_client.get_group_users(group_id)
            
            pay_each_user_list = []
            pay_each_box_tamplate = open("templates/pay_each_box_tamplate.json").read()
            for user_id in user_ids:
                line_user_name = self.line_bot_api.get_group_member_profile(group_id, user_id).display_name
                pay_each_box_flex = copy.deepcopy(pay_each_box_tamplate)
                pay_each_box_flex = (
                    pay_each_box_flex.replace("<LINE_USER_NAME>", line_user_name)
                    .replace("<PAY_AMOUNT>", str(pay_each))
                )
                pay_each_user_list.append(pay_each_box_flex)
            
            flex_group_pay = open("templates/flex_group_pay.json").read()
            flex_group_pay = (
                flex_group_pay.replace("<PAY_EACH_USER_TEMPLATE>",",".join(pay_each_user_list))
                .replace("<GROUP_PAY_TYPE>", "เรียกเก็บเงินแบบหารเท่า")
            )
            
            flex_summary_order_msg = FlexMessage(
                alt_text="กรุณากดจ่ายเงิน",
                contents=FlexContainer.from_json(flex_group_pay),
            )   

            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        flex_summary_order_msg,
                        TextMessage(text="กดจ่ายเงิน หรือพิมพ์คุยกับน้อง CJ เพื่อเพิ่มสินค้าได้ค่ะ"),
                    ],
                )
            )
             
        elif type == "select_payer":
            user_ids = self.datastore_client.get_group_users(group_id)
            total_price = self.postback_params.get("total_price")
            quick_reply_items = []
            for user_id in user_ids:
                line_user_name = self.line_bot_api.get_group_member_profile(group_id, user_id).display_name
                quick_reply_items.append(
                    QuickReplyItem(
                        action=PostbackAction(label=line_user_name, data=f"action=group_pay_selected_payer&user_id={user_id}&total_price={total_price}")
                    )
                )
                
            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text="กรุณาเลือกผู้ชำระเงินด้วยค่ะ",
                            quick_reply=QuickReply(items=quick_reply_items)
                        )
                    ]
                )
            )
    
        elif type == "pay_own":
            pass

    def handle_group_pay_select_payer(self):
        group_id = self.event.source.group_id
        user_id = self.postback_params.get("user_id")
        total_price = self.postback_params.get("total_price")

        line_user_name = self.line_bot_api.get_group_member_profile(group_id, user_id).display_name
        pay_each_box_tamplate = open("templates/pay_each_box_tamplate.json").read()
        pay_each_box_flex = copy.deepcopy(pay_each_box_tamplate)
        
        pay_each_box_flex = (
            pay_each_box_flex.replace("<LINE_USER_NAME>", line_user_name)
            .replace("<PAY_AMOUNT>", total_price)
        )
   
        flex_group_pay = open("templates/flex_group_pay.json").read()
        flex_group_pay = (
            flex_group_pay.replace("<PAY_EACH_USER_TEMPLATE>", pay_each_box_flex)
            .replace("<GROUP_PAY_TYPE>", "เรียกเก็บเงินจากตัวแทนกลุ่ม")
        )
        
        flex_summary_order_msg = FlexMessage(
            alt_text="กรุณากดจ่ายเงิน",
            contents=FlexContainer.from_json(flex_group_pay),
        )   

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.reply_token,
                messages=[
                    flex_summary_order_msg,
                    TextMessageV2(
                        text="คุณ {pay_user}, คุณได้เป็นตัวแทนในการจ่ายบิลนี้ พร้อมแล้วกดชำระเงินได้เลยนะค่ะ",
                        substitution={
                            "pay_user": MentionSubstitutionObject(mentionee=UserMentionTarget(userId=user_id))
                        }
                    ),
                ],
            )
        )
    
    def handle_cancle_user_order_action(self):
        user_id = self.event.source.user_id
        if self.event.source.type == "user":
            self.show_loading()
            self.datastore_client.remove_user_order(user_id=user_id)
        elif self.event.source.type == "group":
            self.datastore_client.remove_group_order(group_id=self.event.source.group_id)

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.event.reply_token,
                messages=[
                    TextMessage(text="ยกเลิกกรายการสั้งซื้อปัจุบัันของท่านเรียบร้อยค่ะ"),
                ],
            )
        )

    def handle_cancle_group_order_action(self):
        group_id = self.event.source.group_id
        self.datastore_client.remove_group_order(group_id=group_id)

    def handle_richmenu_switch_action(self):
        menu = self.postback_params.get("menu")
        user_id = self.event.source.user_id
        rich_menu_id = self.rich_menu_id_config[menu]
        self.line_bot_api.link_rich_menu_id_to_user(user_id, rich_menu_id)

    def handle_postback_by_action(self):
        postback_action = self.postback_params.get("action")
        function_map = {
            "add_item": self.handle_add_item_action,
            "summary_order": self.handle_summary_order_action,
            "make_payment": self.handle_make_user_payment_action,
            "make_group_payment": self.handle_make_group_payment_action,
            "richmenuswitch": self.handle_richmenu_switch_action,
            "cancle_user_order": self.handle_cancle_user_order_action,
            "cancle_group_order": self.handle_cancle_group_order_action,
            "group_pay_selected_payer": self.handle_group_pay_select_payer
        }

        if postback_action and postback_action in function_map:
            function_map[postback_action]()
