from google.cloud import datastore
import json

# Initialize Datastore client globally
client = datastore.Client()

def datastore_handler(request):
    """
    Cloud Function to handle Datastore actions: insert, get, update.
    Includes CORS headers to allow cross-origin requests.
    """
    # Handle preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    # Initialize response headers for CORS
    headers = {
        'Access-Control-Allow-Origin': '*',  # Allow all origins
        'Content-Type': 'application/json'
    }

    # Parse incoming JSON request
    request_json = request.get_json(silent=True)

    if not request_json:
        return ("Invalid request: JSON body required", 400, headers)

    # Extract required fields
    action = request_json.get("action")
    kind = request_json.get("kind")
    key_id = request_json.get("id")
    data = request_json.get("data")
    
    print(f"Request: {request_json}")

    if not action or not kind:
        return ("Missing 'action' or 'kind' in the request body", 400, headers)

    # Perform actions
    if action == "insert":
        return insert_entity(kind, key_id, data, headers)
    elif action == "get":
        return get_entity(kind, key_id, headers)
    elif action == "update":
        return update_entity(kind, key_id, data, headers)
    else:
        return (f"Invalid action '{action}'", 400, headers)


def insert_entity(kind, key_id, data, headers):
    """Insert a new entity into Datastore."""
    if not data:
        return ("'data' field is required for insert action", 400, headers)

    key = client.key(kind, key_id)
    entity = datastore.Entity(key=key)
    entity.update(data)
    client.put(entity)

    return (json.dumps({"message": f"Entity inserted into kind '{kind}'"}), 200, headers)

def get_entity(kind, key_id, headers):
    """Retrieve an entity from Datastore."""
    if not key_id:
        return ("'id' field is required for get action", 400, headers)

    key = client.key(kind, key_id)
    entity = client.get(key)

    if entity:
        return (json.dumps(dict(entity)), 200, headers)
    else:
        return (f"Entity with ID '{key_id}' not found in kind '{kind}'", 404, headers)

def update_entity(kind, key_id, data, headers):
    """Update an existing entity."""
    if not key_id or not data:
        return ("'id' and 'data' fields are required for update action", 400, headers)

    key = client.key(kind, key_id)
    entity = client.get(key)

    if not entity:
        return (f"Entity with ID '{key_id}' not found in kind '{kind}'", 404, headers)

    entity.update(data)
    client.put(entity)

    return (json.dumps({"message": f"Entity with ID '{key_id}' updated"}), 200, headers)
