import os
import vertexai
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from google.cloud import storage

# https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-multimodal-embeddings
GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
GCS_BUCKET = os.environ["GCS_BUCKET"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "privates/sa.json"


vertexai.init(project=GCP_PROJECT_ID, location="us-central1")

client = storage.Client()
bucket = client.bucket(GCS_BUCKET)
folder_prefix = "cj-product-images/"

blobs = bucket.list_blobs(prefix=folder_prefix)

# create empt data frame
import pandas as pd

df = pd.DataFrame(columns=["id", "embedding"])


for blob in blobs:
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    image = Image.load_from_file(f"gs://{GCS_BUCKET}/{folder_prefix}/{blob.name}")
    embeddings = model.get_embedding(
        text=None, image=image, embedding_dimension=128
    ).image_embedding

    df_new = pd.DataFrame({"id": [blob.name], "embedding": [embeddings]})
    df = pd.concat([df, df_new], ignore_index=True)

jsonl_string = df[["id", "embedding"]].to_json(orient="records", lines=True)
with open("questions.json", "w") as f:
    f.write(jsonl_string)
