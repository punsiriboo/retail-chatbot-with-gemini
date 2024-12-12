import sys
import os
import linebot
from linebot.v3.messaging import RichMenuRequest
from linebot.v3.messaging.rest import ApiException
from pprint import pprint

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("credential/line_secret.yml")

configuration = linebot.v3.messaging.Configuration(
    host="https://api.line.me",
    access_token=os.getenv("CHANNEL_ACCESS_TOKEN")
)

api_client = linebot.v3.messaging.ApiClient(configuration) 
api_instance = linebot.v3.messaging.MessagingApi(api_client)

richmenu_json = open("richmenu/richmenu_json/richmenu-main.json").read()
rich_menu_request = RichMenuRequest.from_json(richmenu_json)


api_response = api_instance.create_rich_menu(rich_menu_reques=rich_menu_request,
                                             files="richmenu/richmenu_json/2.jpg")
print("The response of MessagingApi->create_rich_menu:\n")
pprint(api_response)
# except Exception as e:
#     print("Exception when calling MessagingApi->create_rich_menu: %s\n" % e)

# RichMenuIdResponse(rich_menu_id='richmenu-96b2baf4159b57b22ae4b75200079430')