from google.cloud import datastore
from datetime import datetime
from collections import defaultdict


class DatastoreClient:

    def __init__(self):
        self.datastore_client = datastore.Client()

    def create_user_action_add_item(self, user_id, item_name, item_price):
        kind = "add_items_action"
        created_ad = datetime.utcnow().timestamp()
        complete_key = self.datastore_client.key(kind, user_id)
        entity = datastore.Entity(key=complete_key)
        entity.update(
            {
                "user": user_id,
                "action": "add_items",
                "items": [{"item_name": item_name, "item_price": item_price}],
                "createdAt": created_ad,
            }
        )
        self.datastore_client.put(entity)

    def get_user_action(self, user_id):
        kind = "add_items_action"
        key = self.datastore_client.key(kind, user_id)
        user = self.datastore_client.get(key)

        if user is not None:
            return user
        else:
            return False

    def remove_add_items_document(self, user_id):
        kind = "add_items_action"
        key = self.datastore_client.key(kind, user_id)
        self.datastore_client.delete(key)

    def add_user_items_action(self, user_id, item_name, item_price):
        entity = self.get_user_action(user_id)
        if entity:
            entity["items"].append({"item_name": item_name, "item_price": item_price})
            self.datastore_client.put(entity)

        else:
            self.create_user_action_add_item(user_id, item_name, item_price)

    def calculate_all_items_in_basket(self, user_id):
        entity = self.get_user_action(user_id)
        if entity:
            items = entity["items"]
            # Grouping items
            grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0.0})

            total_final_price = 0.0
            total_items = 0

            for item in items:
                name = item["item_name"]
                price = float(item["item_price"])
                grouped_items[name]["price"] = price
                grouped_items[name]["quantity"] += 1
                grouped_items[name]["total_price"] += price
                total_final_price += price
                total_items += 1

            total_items = str(total_items)
            total_final_price = f"{total_final_price:.2f}"
            return total_items, total_final_price, grouped_items
