from google.cloud import storage
from embedding_client import get_image_embedding_from_gcs_object
import csv


IMAGE_SET_BUCKET_NAME = "coca-embedding-test-images"

gcsBucket = storage.Client().get_bucket(IMAGE_SET_BUCKET_NAME)

with open("image_embedding.csv", "w") as f:
    csvWriter = csv.writer(f)
    csvWriter.writerow(["gcsUri", "embedding"])
    for blob in gcsBucket.list_blobs():
        gcsUri = "gs://" + IMAGE_SET_BUCKET_NAME + "/" + blob.name
        print("Processing {}".format(gcsUri))
        embedding = get_image_embedding_from_gcs_object(
            IMAGE_SET_BUCKET_NAME, blob.name
        )
        csvWriter.writerow([gcsUri, str(embedding)])
