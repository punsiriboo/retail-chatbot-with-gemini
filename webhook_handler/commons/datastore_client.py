from google.cloud import datastore
from datetime import datetime
from collections import defaultdict


class DatastoreClient:

    def __init__(self):
        self.datastore_client = datastore.Client()

    def add_user_beacon_enter(self, user_id):
        kind = "cj_users_beacons"
        created_ad = datetime.utcnow()
        complete_key = self.datastore_client.key(kind, user_id)
        entity = datastore.Entity(key=complete_key)
        entity.update(
            {
                "user": user_id,
                "action": "beacons_enter",
                "createdAt": created_ad,
            }
        )
        self.datastore_client.put(entity)

    def create_user_action_add_item(self, user_id, item_name, item_price, item_image_url):
        kind = "cj_users_orders"
        created_ad = datetime.utcnow().timestamp()
        complete_key = self.datastore_client.key(kind, user_id)
        entity = datastore.Entity(key=complete_key)
        entity.update(
            {
                "user": user_id,
                "action": "add_items",
                "items": [{"item_name": item_name, "item_price": item_price, "item_image_url":item_image_url}],
                "createdAt": created_ad,
            }
        )
        self.datastore_client.put(entity)

    def get_user_order(self, user_id):
        kind = "cj_users_orders"
        key = self.datastore_client.key(kind, user_id)
        user = self.datastore_client.get(key)

        if user is not None:
            return user
        else:
            return False

    def remove_user_order(self, user_id):
        kind = "cj_users_orders"
        key = self.datastore_client.key(kind, user_id)
        self.datastore_client.delete(key)

    def add_user_items_action(self, user_id, item_name, item_price, item_image_url):
        entity = self.get_user_order(user_id)
        if entity:
            entity["items"].append({"item_name": item_name, "item_price": item_price, "item_image_url":item_image_url})
            self.datastore_client.put(entity)

        else:
            self.create_user_action_add_item(user_id, item_name, item_price, item_image_url)

    def calculate_user_items_in_basket(self, user_id):
        entity = self.get_user_order(user_id)
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

    def create_group_action_add_item(self, group_id, user_id, item_name, item_price):
        kind = "cj_group_orders"
        created_ad = datetime.utcnow()
        complete_key = self.datastore_client.key(kind, f"LINE_GROUP_{group_id}")
        entity = datastore.Entity(key=complete_key)
        entity.update(
            {
                "items": [
                    {
                        "user_id": user_id,
                        "item_name": item_name,
                        "item_price": item_price,
                    }
                ],
                "createdAt": created_ad,
            }
        )
        self.datastore_client.put(entity)
        return entity

    def get_group_order(self, group_id):
        kind = "cj_group_orders"
        key = self.datastore_client.key(kind, f"LINE_GROUP_{group_id}")
        group_data = self.datastore_client.get(key)

        if group_data is not None:
            return group_data
        else:
            return False

    def remove_group_order(self, group_id):
        kind = "cj_group_orders"
        key = self.datastore_client.key(kind, f"LINE_GROUP_{group_id}")
        user = self.datastore_client.get(key)

        if user is not None:
            return user
        else:
            return False

    def add_group_items_action(self, group_id, user_id, item_name, item_price):
        entity = self.get_group_order(group_id)
        if entity:
            entity["items"].append(
                {"user_id": user_id, "item_name": item_name, "item_price": item_price}
            )
            self.datastore_client.put(entity)

        else:
            self.create_group_action_add_item(group_id, user_id, item_name, item_price)

    def calculate_group_items_in_basket(self, group_id):
        # Summary structure
        entity = self.get_group_order(group_id)
        if entity:
            items = entity["items"]

        user_totals = defaultdict(lambda: {"total_items": 0, "total_price": 0.0})

        total_final_price = 0.0
        total_items = 0

        # Temporary storage for grouping
        grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0.0})

        for item in items:
            user_id = item.get("user_id") or item.get("user")
            item_name = item["item_name"]
            item_price = float(item["item_price"])

            # Group items by user and item name
            grouped_items[(user_id, item_name)]["quantity"] += 1
            grouped_items[(user_id, item_name)]["total_price"] += item_price
            grouped_items[(user_id, item_name)]["price"] = item_price

            # Calculate totals per user
            user_totals[user_id]["total_items"] += 1
            user_totals[user_id]["total_price"] += item_price

            # Calculate overall totals
            total_final_price += item_price
            total_items += 1

        # Convert grouped items to user-wise lists
        user_items_summary = defaultdict(list)
        for (user_id, item_name), data in grouped_items.items():
            user_items_summary[user_id].append(
                [
                    item_name,  # Item name
                    data["quantity"],  # Quantity
                    f"{data['total_price']:.2f}",  # Total price per item
                ]
            )

        total_items = str(total_items)
        total_final_price = f"{total_final_price:.2f}"
        return total_items, total_final_price, user_items_summary, user_totals

    def create_group_users(self, group_id, user_id):
        kind = "cj_chat_group"
        complete_key = self.datastore_client.key(kind, group_id)
        entity = datastore.Entity(key=complete_key)
        entity.update(
            {
                "users": [user_id],
            }
        )
        self.datastore_client.put(entity)

    def get_group_users(self, group_id):
        kind = "cj_chat_group"
        key = self.datastore_client.key(kind, group_id)
        group_chat = self.datastore_client.get(key)
        if group_chat is not None:
            return group_chat          
    
    def add_user_to_group(self, group_id, user_id):
        group_chat = self.get_group_users(group_id)
        
        if group_chat:
            users = group_chat['users']
            users.append(user_id)
            group_chat['users'] = list(set(group_chat['users']))
            self.datastore_client.put(group_chat)
        else: 
            self.create_group_users(group_id, user_id)

    def get_cj_membership(self, user_id):
        kind = "CJ_USER"
        key = self.datastore_client.key(kind, user_id)
        member = self.datastore_client.get(key)
        if member is not None:
            return member          
    
        
