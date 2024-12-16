import pandas as pd
import math

from linebot.v3.messaging import (
    ReplyMessageRequest,
    FlexContainer,
    FlexMessage,
    FlexCarousel,
)


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

    result_branch_list = []
    with open("templates/flex_branch_bubble.json") as file:
        branch_bubble_temple = file.read()

    for index, branch in closest_branches.iterrows():
        title = branch["branch"]
        distance = branch["distance"]
        phone_number = branch["tel"]
        map_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lng}&destination={branch['lat']},{branch['lng']}"

        branch_bubble_json = (
            branch_bubble_temple.replace("<BRANCH_NAME>", title)
            .replace("<BRANCH_DISTANCE>", f"{distance:.2f} กม.")
            .replace("<BRANCH_PHONE_NUMBER>", phone_number)
            .replace("<BRANCH_MAP_URL>", map_url)
        )

        result_branch_list.append(FlexContainer.from_json(branch_bubble_json))

    carousel_flex_message = FlexMessage(
        alt_text="สาขา CJ ที่ใกล้เคียง",
        contents=FlexCarousel(
            type="carousel",
            contents=result_branch_list,
        ),
    )

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, messages=[carousel_flex_message]
        )
    )
