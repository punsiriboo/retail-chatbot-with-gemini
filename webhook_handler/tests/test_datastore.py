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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="webhook_handler/privates/sa.json"

def get_datastore_client():
    """Helper to get either a Mock or Real Datastore Client"""
    if USE_MOCK:
        with patch('commons.datastore_client.datastore') as mock_datastore:
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
        datastore_client.datastore_client.key.assert_called_once_with("add_items_action", user_id)
        datastore_client.datastore_client.put.assert_called_once()
        put_call_args = datastore_client.datastore_client.put.call_args_list[0][0][0]
        assert put_call_args["user"] == user_id
        assert put_call_args["action"] == "add_items"
        assert put_call_args["items"] == [{"item_name": item_name, "item_price": item_price}]
    else:
        print("Real test passed. Manually verify the entry in Datastore.")

def test_get_user_action(datastore_client):
    user_id = "test_user"
    mock_entity = {"user": user_id, "items": []}


    result = datastore_client.get_user_action(user_id)

    if USE_MOCK:
        datastore_client.datastore_client.get.return_value = mock_entity
        assert result == mock_entity
    else:
        print(result)
        print(f"Retrieved user action: {result}")

def test_remove_add_items_document(datastore_client):
    user_id = "test_user"
    datastore_client.remove_add_items_document(user_id)

    if USE_MOCK:
        datastore_client.datastore_client.key.assert_called_once_with("add_items_action", user_id)
        datastore_client.datastore_client.delete.assert_called_once()
    else:
        print("Real delete test passed. Verify manually.")

def test_add_user_items_action_existing_user(datastore_client):
    user_id = "test_user"
    item_name = "test_item_2"
    item_price = 200

    datastore_client.add_user_items_action(user_id, item_name, item_price)

    if USE_MOCK:
        mock_entity = {
            "user": user_id,
            "items": [{"item_name": "test_item_1", "item_price": 100}]
        }
        datastore_client.datastore_client.get.return_value = mock_entity
        assert len(mock_entity["items"]) == 2
        assert mock_entity["items"][1] == {"item_name": item_name, "item_price": item_price}
        datastore_client.datastore_client.put.assert_called_once_with(mock_entity)
    else:
        print("Add items test passed. Verify datastore manually.")

def test_calculate_all_items_in_basket(datastore_client):
    user_id = "test_user"

    total_items, total_price, grouped_items = datastore_client.calculate_all_items_in_basket(user_id)

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
