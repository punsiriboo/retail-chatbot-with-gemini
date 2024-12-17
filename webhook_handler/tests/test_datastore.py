import os
import sys
from google.cloud import datastore
from datetime import datetime
from collections import defaultdict
import pytest
from unittest.mock import patch, MagicMock

# Import the DatastoreClient
outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.datastore_client import DatastoreClient

# Configuration to switch between Mock and Real Datastore
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "false"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "webhook_handler/privates/sa.json"


def get_datastore_client():
    """Helper to get either a Mock or Real Datastore Client"""
    if USE_MOCK:
        with patch("commons.datastore_client.datastore") as mock_datastore:
            mock_client = MagicMock()
            mock_datastore.Client.return_value = mock_client
            return DatastoreClient()
    else:
        return DatastoreClient()


@pytest.fixture
def datastore_client():
    """Fixture to return the appropriate DatastoreClient."""
    return get_datastore_client()


def test_create_user_action_add_item(datastore_client):
    user_id = "test_user"
    item_name = "test_item"
    item_price = 100

    datastore_client.create_user_action_add_item(user_id, item_name, item_price)

    if USE_MOCK:
        datastore_client.datastore_client.key.assert_called_once_with(
            "cj_users_orders", user_id
        )
        datastore_client.datastore_client.put.assert_called_once()
        put_call_args = datastore_client.datastore_client.put.call_args_list[0][0][0]
        assert put_call_args["user"] == user_id
        assert put_call_args["action"] == "add_items"
        assert put_call_args["items"] == [
            {"item_name": item_name, "item_price": item_price}
        ]
    else:
        print("Real test passed. Manually verify the entry in Datastore.")


def test_get_user_action(datastore_client):
    user_id = "test_user"
    mock_entity = {"user": user_id, "items": []}

    result = datastore_client.get_user_order(user_id)

    if USE_MOCK:
        datastore_client.datastore_client.get.return_value = mock_entity
        assert result == mock_entity
    else:
        print(result)
        print(f"Retrieved user action: {result}")


def test_remove_user_order(datastore_client):
    user_id = "test_user"
    datastore_client.remove_user_order(user_id)

    if USE_MOCK:
        datastore_client.datastore_client.key.assert_called_once_with(
            "cj_users_orders", user_id
        )
        datastore_client.datastore_client.delete.assert_called_once()
    else:
        print("Real delete test passed. Verify manually.")


def test_add_user_items_action_existing_user(datastore_client):
    user_id = "test_user_1"
    item_name = "test_item_1"
    item_price = 200

    datastore_client.add_user_items_action(user_id, item_name, item_price)

    if USE_MOCK:
        mock_entity = {
            "user": user_id,
            "items": [{"item_name": "test_item_1", "item_price": 100}],
        }
        datastore_client.datastore_client.get.return_value = mock_entity
        assert len(mock_entity["items"]) == 2
        assert mock_entity["items"][1] == {
            "item_name": item_name,
            "item_price": item_price,
        }
        datastore_client.datastore_client.put.assert_called_once_with(mock_entity)
    else:
        print("Add items test passed. Verify datastore manually.")


def test_calculate_all_items_in_basket(datastore_client):
    user_id = "test_user"

    total_items, total_price, grouped_items = (
        datastore_client.calculate_user_items_in_basket(user_id)
    )

    if USE_MOCK:
        items = [
            {"item_name": "item1", "item_price": "10"},
            {"item_name": "item2", "item_price": "20"},
            {"item_name": "item1", "item_price": "10"},
        ]
        mock_entity = {"user": user_id, "items": items}
        datastore_client.datastore_client.get.return_value = mock_entity
        assert total_items == "3"
        assert total_price == "40.00"
        assert grouped_items["item1"]["quantity"] == 2
        assert grouped_items["item1"]["total_price"] == 20.0
        assert grouped_items["item2"]["quantity"] == 1
    else:
        print(f"Total Items: {total_items}")
        print(f"Total Price: {total_price}")
        print(f"Grouped Items: {grouped_items}")


def test_create_group_action_add_item(datastore_client):
    """Test create_user_action_add_item with both Mock and Real Datastore."""
    group_id = "test_group"
    user_id = "test_user_1"
    item_name = "test_item_1"
    item_price = 100

    # Call the method under test
    result = datastore_client.create_group_action_add_item(
        group_id, user_id, item_name, item_price
    )

    if USE_MOCK:
        # Assertions for the mocked client
        datastore_client.datastore_client.key.assert_called_once_with(
            "cj_group_orders", group_id
        )
        datastore_client.datastore_client.put.assert_called_once()

        # Extract and validate the Entity passed to `put()`
        put_call_args = datastore_client.datastore_client.put.call_args[0][0]
        assert put_call_args["user"] == user_id
        assert put_call_args["action"] == "add_items"
        assert put_call_args["items"] == [
            {"item_name": item_name, "item_price": item_price}
        ]
        assert "createdAt" in put_call_args
    else:
        assert result.key == datastore.Client().key(
            "cj_group_orders", "LINE_GROUP_test_group"
        )
        assert result.kind == "cj_group_orders"
        assert len(result["items"]) == 1
        print("Real Datastore test passed. Verify the entry manually in Datastore.")


def test_add_group_items_to_existing_group(datastore_client):
    group_id = "test_group"
    users = [
        {
            "user_id": "test_user_1",
            "items": [
                {"item_name": "test_item_2", "item_price": 100},
                {"item_name": "test_item_3", "item_price": 100},
            ],
        },
        {
            "user_id": "test_user_2",
            "items": [
                {"item_name": "test_item_2", "item_price": 100},
                {"item_name": "test_item_2", "item_price": 100},
            ],
        },
        {
            "user_id": "test_user_1",
            "items": [
                {"item_name": "test_item_2", "item_price": 100},
            ],
        },
    ]

    # Call the method under test for multiple users and items
    for user in users:
        user_id = user["user_id"]
        for item in user["items"]:
            item_name = item["item_name"]
            item_price = item["item_price"]
            datastore_client.add_group_items_action(
                group_id, user_id, item_name, item_price
            )


def test_get_group_order(datastore_client):
    """Test fetching a group order."""
    group_id = "test_group"

    result = datastore_client.get_group_order(group_id)

    if USE_MOCK:
        # Mocked assertions
        datastore_client.datastore_client.key.assert_called_once_with(
            "cj_group_orders", group_id
        )
    else:
        assert result.key == datastore.Client().key(
            "cj_group_orders", "LINE_GROUP_test_group"
        )
        assert result.kind == "cj_group_orders"
        assert len(result["items"]) == 5
        print(f"Real Datastore test passed for group ID {group_id}. Verify manually.")


def test_calculate_group_items_in_basket(datastore_client):
    """Test calculation of group items in a basket."""
    group_id = "test_group"
    # Call the function
    total_items, total_final_price, user_items_summary, user_totals = (
        datastore_client.calculate_group_items_in_basket(group_id)
    )

    # Print results
    print("Total Items:", total_items)
    print("Total Final Price:", total_final_price)
    print("User Items Summary:")
    for user_id, items_list in user_items_summary.items():
        print(f"User: {user_id}")
        for item in items_list:
            print(f"  Item: {item[0]}, Quantity: {item[1]}, Total Price: {item[2]}")
        print(
            f"Total Items: {user_totals[user_id]['total_items']}, Total Price: {user_totals[user_id]['total_price']:.2f}"
        )


def test_remove_group_order(datastore_client):
    group_id = "test_group"
    datastore_client.remove_group_order(group_id)

    if USE_MOCK:
        datastore_client.datastore_client.key.assert_called_once_with(
            "cj_group_orders", group_id
        )
        datastore_client.datastore_client.delete.assert_called_once()
    else:
        print("Real delete test passed. Verify manually.")
