import requests
import os
import sys

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("credential/line_secret.yml")

def upload_rich_menu_images(rich_menu_data):
    """Uploads images to rich menus using a list of dictionaries.

    Args:
        rich_menu_data: A list of dictionaries, where each dictionary contains:
            - 'rich_menu_id': The ID of the rich menu.
            - 'image_path': The path to the image file.
    """

    access_token = os.getenv("CHANNEL_ACCESS_TOKEN")  # Retrieve from environment variables
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'image/jpeg'  # Adjust if using different image types
    }

    for item in rich_menu_data:
        rich_menu_id = item['rich_menu_id']
        image_path = item['image_path']
        url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
        try:
            with open(image_path, "rb") as image_file:
                response = requests.post(url, headers=headers, data=image_file)
                response.raise_for_status()  # Raise an exception for bad status codes
                print(f"Successfully uploaded image for rich menu {rich_menu_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image for rich menu {rich_menu_id}: {e}")
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
        except KeyError as e:
            print(f"Error: Missing key in rich_menu_data: {e}")



# Example usage:
rich_menu_data = [
    {'rich_menu_id': "richmenu-xxxxxxxxxxxxxxxxx", 'image_path': "richmenu/richmenu_contents/images/main.jpg"},
    {'rich_menu_id': "richmenu-yyyyyyyyyyyyyyyyy", 'image_path': "richmenu/richmenu_contents/images/cj.jpg"},
    {'rich_menu_id': "richmenu-yyyyyyyyyyyyyyyyy", 'image_path': "richmenu/richmenu_contents/images/nine.jpg"},
    {'rich_menu_id': "richmenu-yyyyyyyyyyyyyyyyy", 'image_path': "richmenu/richmenu_contents/images/uno.jpg"},
    {'rich_menu_id': "richmenu-yyyyyyyyyyyyyyyyy", 'image_path': "richmenu/richmenu_contents/images/ahome.jpg"},
    {'rich_menu_id': "richmenu-yyyyyyyyyyyyyyyyy", 'image_path': "richmenu/richmenu_contents/images/bao-cafe.jpg"},
] 

upload_rich_menu_images(rich_menu_data)