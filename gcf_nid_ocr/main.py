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

    try:
        # Parse incoming JSON request
        request_json = request.get_json(silent=True)

        if not request_json:
            return ("Invalid request: JSON body required", 400, headers)

        # Extract required fields
        image_base64 = request_json.get("image_base64")


    except Exception as e:
        return (f"Error: {str(e)}", 500, headers)