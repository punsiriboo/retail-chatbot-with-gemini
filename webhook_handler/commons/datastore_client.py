from google.cloud import datastore
from datetime import datetime


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
        kind = "line_user_action"
        key = self.datastore_client.key(kind, user_id)
        user = self.datastore_client.get(key)

        if user is not None:
            return user
        else:
            return False

    def remove_user_action(self, user_id):
        kind = "line_user_action"
        key = self.datastore_client.key(kind, user_id)
        self.datastore_client.delete(key)

    def add_user_items_action(self, user_id, item_name, item_price):
        entity = self.get_user_action(user_id)
        if entity:
            entity['items'].append(
                {"item_name": item_name, "item_price": item_price}
            )
            self.datastore_client.put(entity)
        
        else:
            self.create_user_action_add_item(user_id, item_name, item_price)
