from google.cloud import aiplatform


project_id = "tildi-playground-0001"
location = "us-central1" 
bucket_uri = f"gs://{bucket_name}/{destination_blob_name}"

aiplatform.init(project=project_id, location=location)

# Create the index
index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name="vs-quickstart-index",
    contents_delta_uri=bucket_uri,
    dimensions=768,  # Make sure this matches your embedding dimensions
    approximate_neighbors_count=10
)

print(f"Index created: {index.resource_name}")
