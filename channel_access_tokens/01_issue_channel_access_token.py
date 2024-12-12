import sys
import os
import linebot.v3.oauth
from pprint import pprint

configuration = linebot.v3.oauth.Configuration(host="https://api.line.me")
api_client = linebot.v3.oauth.ApiClient(configuration)

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("credential/line_secret.yml")


api_instance = linebot.v3.oauth.ChannelAccessToken(api_client)
grant_type = "client_credentials"  # str | `client_credentials`
client_id = os.getenv("CHANNEL_ID")  # str | Channel ID.
client_secret = os.getenv("CHANNEL_SECRET")  # str | Channel secret.

try:
    api_response = api_instance.issue_channel_token(
        grant_type,
        client_id,
        client_secret,
    )
    print("The response of ChannelAccessToken->_issue_channel_access_token:\n")
    pprint(api_response)
except Exception as e:
    print(
        "Exception when calling ChannelAccessToken->_issue_channel_access_token: %s\n"
        % e
    )
