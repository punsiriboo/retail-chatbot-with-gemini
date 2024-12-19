from datetime import datetime
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)

from commons.datastore_client import DatastoreClient


def handle_beacon_by_user_profile(event, line_bot_api):
    datastore_client = DatastoreClient()
    if event.beacon.type == "enter":
        # event.beacon.hwid
        # event.beacon.dm
        datastore_client.add_user_beacon_enter(user_id=event.source.user_id)
        profile = line_bot_api.get_profile(user_id=event.source.user_id)
        user_name = profile.display_name
    
        print("handle_return_static_flex: beacon_say_hello")
        with open("templates/static/beacon_say_hello.json") as file:
            flex_temple = file.read()

        static_flex_message = FlexMessage(
            alt_text="ยินดีต้องรับสู่ CJ สาขาบ้านบีท",
            contents=FlexContainer.from_json(flex_temple),
        )

        personalized_flex_msg = get_flex_by_member_segment(user_id=event.source.user_id)
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"[LINE BEACON] สวัสดีค่ะ คุณ {user_name}\nยินดีต้องรับสู่ CJ สาขาบ้านบีทนะคะ\n\nอย่าลืมตรวจสอบคูปองที่มี และส่วนลดเพื่อการ Shopping ที่มากกว่าที่ CJ"
                    ),
                    static_flex_message,
                    TextMessage(
                        text=f"พิเศษสำหรับคุณ {user_name}เท่านั้น\n\nเรามีโปรโมชั่นแนะนำดังนี้ค่ะ"
                    ),
                    personalized_flex_msg
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

def get_flex_by_member_segment(user_id):
    datastore_client = DatastoreClient()

    member = datastore_client.get_cj_membership(user_id)
    
    if not member:
        flex_msg = open("templates/static/cj_register_sabai_card.json").read()
    else:
        dob = datetime.strptime(member["dob"], "%Y-%m-%d")
        today = datetime.today()
        member_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if (member_age > 30) and (member['gender'] == 'male'):
            flex_msg = open("templates/static/ahome_car_lover_promotion.json").read()
        elif (member_age > 30)and (member['gender'] == 'female'):
            flex_msg = open("templates/static/nine_winner.json").read()
        elif (member_age <= 30) and (member['gender'] == 'male'):
            flex_msg = open("templates/static/ahome_toy_story.json").read()
        elif (member_age <= 30) and (member['gender'] == 'female'):
            flex_msg = open("templates/static/uno_power_puff_girls.json").read()

            
    return FlexMessage(
        alt_text="personalized_message_from_beacon",
        contents=FlexContainer.from_json(flex_msg),
    
    )
