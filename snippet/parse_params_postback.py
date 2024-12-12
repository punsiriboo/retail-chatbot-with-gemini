from urllib.parse import parse_qs

# Example query string
query_string = "action=add_item&item_id=<PRODUCT_SKU>"

# Parse the query string into a dictionary
params_dict = {key: value[0] for key, value in parse_qs(query_string).items()}

print(params_dict["item_id"])
