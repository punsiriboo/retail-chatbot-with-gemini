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
group_id = "C8f983564d0bb8b0ee3e30e4eab0806b3"  # str | ID of a group

try:
    # api_response = api_instance.get_group_member_count(group_id)
    # pprint(api_response.count)
    
    # api_response = api_instance.get_group_members_ids(group_id)
    # pprint(api_response)
    group_id = "C8f983564d0bb8b0ee3e30e4eab0806b3"
    users = ['U851fc04bfa20819fd5b5c942329b5ac8', 'U9d6fa7597c45108192f4e0acf8c31f44', 'U77643c7eee83c7b712ab0e3567f3ca38']
    for u in users:
        profile = api_instance.get_group_member_profile(group_id, u).display_name
        print(profile)
except Exception as e:
    print("Exception when calling MessagingApi->get_rich_menu: %s\n" % e)
