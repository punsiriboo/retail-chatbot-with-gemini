import sys
import os
import linebot.v3.messaging
from pprint import pprint

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("credential/line_secret.yml")

configuration = linebot.v3.messaging.Configuration(
    host="https://api.line.me", access_token=os.getenv("CHANNEL_ACCESS_TOKEN")
)

api_client = linebot.v3.messaging.ApiClient(configuration)
api_instance = linebot.v3.messaging.MessagingApi(api_client)
rich_menu_id = "richmenu-db38e9f92a3c898106dd4306626c8c75"  # str | ID of a rich menu

try:
    # api_response = api_instance.get_rich_menu_alias_list()
    # pprint(api_response)
    
    api_response = api_instance.get_rich_menu(rich_menu_id)
    pprint(api_response)
    print("The response of MessagingApi->get_rich_menu:\n")
    
    api_response = api_instance.set_default_rich_menu(rich_menu_id)
    pprint(api_response)

except Exception as e:
    print("Exception when calling MessagingApi->get_rich_menu: %s\n" % e)
