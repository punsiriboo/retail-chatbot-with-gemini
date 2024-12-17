import json
from commons.vertex_agent_search import vertex_search_retail_products
from commons.dialogflowcx_answer import detect_intent_text
from commons.flex_message_builder import build_flex_carousel_message
from config.keyword_to_flex_mapping import keyword_flex_temple_config as flex_temple_config

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
)


class TextKeywordHandler:
    def __init__(self, line_bot_api, event):
        self.line_bot_api = line_bot_api
        self.event = event
        self.reply_token = event.reply_token
        self.user_id = event.source.user_id if event.source.type == "user" else None

    def handle_coupon_search(self):
        with open("privates/data/coupons.json") as file:
            coupons_data = json.load(file)
        
        list_img_carousel_column = [
            ImageCarouselColumn(
                image_url=campaign["image_thumbnail_path"],
                action=PostbackAction(label="เก็บคูปอง", data="ping", text="ping"),
            )
            for campaign in coupons_data["campaigns"][:10]
        ]
        
        image_carousel_template = ImageCarouselTemplate(columns=list_img_carousel_column)
        template_message = TemplateMessage(
            alt_text="คูปองสินค้า CJ", template=image_carousel_template
        )
        
        self.line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=self.reply_token, messages=[template_message])
        )

    def handle_branch_search(self):
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
                            label="Share location", uri="https://line.me/R/nv/location/"
                        ),
                    )
                ],
            ),
        )

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.reply_token,
                messages=[FlexMessage(alt_text="กรุณากด share location", contents=bubble)],
            )
        )

    def handle_talk_to_cj(self):
        flex_temple = open("templates/static/nong_cj_feature.json").read()
        static_flex_message = FlexMessage(
            alt_text="สวัสดีค่ะ ยินดีต้อนรับสู่​ CJ MORE!",
            contents=FlexContainer.from_json(flex_temple),
        )
        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.reply_token,
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

    def handle_return_static_flex(self, template_name):
        print("handle_return_static_flex: " + template_name)
        with open(f"templates/static/{template_name}.json") as file:
            flex_temple = file.read()

        static_flex_message = FlexMessage(
            alt_text=template_name,
            contents=FlexContainer.from_json(flex_temple),
        )

        self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=self.reply_token,
                messages=[static_flex_message],
            )
        )

    def handle_search_query(self, search_query):
        response_dict = vertex_search_retail_products(search_query)
        build_flex_carousel_message(
            line_bot_api=self.line_bot_api,
            event=self.event,
            response_dict=response_dict,
            search_query=search_query,
        )

    def handle_text_by_keyword(self):
        text = self.event.message.text

        function_map = {
            "คูปองส่วนลด": self.handle_coupon_search,
            "ค้นหาสาขา": self.handle_branch_search,
            "คุยกับน้อง CJ": self.handle_talk_to_cj,
        }

        if text in function_map:
            function_map[text]()
        elif text in flex_temple_config:
            template_name = flex_temple_config[text]
            self.handle_return_static_flex(template_name)
        elif text.startswith("#ค้นหา"):
            search_query = text[len("#ค้นหา"):].strip()
            self.handle_search_query(search_query)
        else:
            response_text = detect_intent_text(text=text, session_id=self.user_id)
            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[TextMessage(text=response_text)],
                )
            )
