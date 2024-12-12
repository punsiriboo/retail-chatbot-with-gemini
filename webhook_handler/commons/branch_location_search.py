import pandas as pd
import math
import json

from linebot.v3.messaging import (
    ReplyMessageRequest,
    TemplateMessage,
    CarouselTemplate,
    CarouselColumn,
    URIAction,
)

with open("privates/data/image_paths.json") as file:
    image_paths = json.load(file)


def calculate_distance(lat1, lng1, lat2, lng2, scale_lat=10, scale_lng=10):
    """Calculates the distance between two points using scaled Euclidean distance.

    Args:
        lat1: Latitude of the first point.
        lng1: Longitude of the first point.
        lat2: Latitude of the second point.
        lng2: Longitude of the second point.
        scale_lat: Scale factor for latitude differences. Defaults to 1.0.
        scale_lng: Scale factor for longitude differences. Defaults to 1.0.

    Returns:
        The scaled Euclidean distance between the two points.
    """
    return math.sqrt((lat1 - lat2) ** 2 * scale_lat + (lng1 - lng2) ** 2 * scale_lng)


def search_closest_branches(event, line_bot_api, user_lat, user_lng, top_n=5):
    """
    Searches for the closest branches to given coordinates.

    Args:
        user_lat: Latitude of the search location.
        user_lng: lnggitude of the search location.
        top_n: Number of closest branches to return.

    Returns:
        Pandas DataFrame containing the top_n closest branches and their distances.
    """
    data = pd.read_json("privates/data/branchs.json")
    data["distance"] = data.apply(
        lambda row: calculate_distance(user_lat, user_lng, row["lat"], row["lng"]),
        axis=1,
    )
    closest_branches = data.sort_values(by="distance").head(top_n)

    carousel_columns = []
    for index, branch in closest_branches.iterrows():
        carousel_columns.append(
            CarouselColumn(
                thumbnail_image_url=branch.get(
                    "image_thumbnail_path",
                    image_paths["branch_search_image"],
                ),
                title=branch["branch"],
                actions=[
                    URIAction(
                        label="CALL ติดต่อสาขา",
                        uri=f"tel:{branch['tel']}",
                    ),
                    URIAction(
                        label="เปิด Google Maps",
                        uri=f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lng}&destination={branch['lat']},{branch['lng']}",
                    ),
                ],
            )
        )
    carousel_template = CarouselTemplate(columns=carousel_columns)
    template_message = TemplateMessage(
        alt_text="สาขา CJ ที่ใกล้เคียง", template=carousel_template
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[template_message])
    )
