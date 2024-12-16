from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)


def handle_beacon_by_user_profile(event, line_bot_api):
    if event.beacon.type == "enter":
        # event.beacon.hwid
        # event.beacon.dm
        print("handle_return_static_flex: beacon_say_hello")
        with open("templates/static/beacon_say_hello.json") as file:
            flex_temple = file.read()

        static_flex_message = FlexMessage(
            alt_text="ยินดีต้องรับสู่ CJ สาขาบ้านบีท",
            contents=FlexContainer.from_json(flex_temple),
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="""สวัสดีค่ะ ยินดีต้องรับสู่ CJ สาขาบ้านบีท\n
                                อย่าลืมตรวจสอบคูปองที่มี และส่วนลดเพื่อการ Shopping ที่มากกว่าที่ CJ"""),
                    static_flex_message,
                ],
            )
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Got beacon event. hwid={}, device_message(hex string)={}".format(
                            event.beacon.hwid, event.beacon.dm
                        )
                    )
                ],
            )
        )
        