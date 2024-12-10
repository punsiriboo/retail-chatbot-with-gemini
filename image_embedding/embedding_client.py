import base64
import typing
from google.cloud import storage
from google.cloud import aiplatform
from google.protobuf import struct_pb2

PROJECT_ID = "quiet-platform-437913-f0"


# Inspired from https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple.
class EmbeddingResponse(typing.NamedTuple):
    text_embedding: typing.Sequence[float]
    image_embedding: typing.Sequence[float]


class EmbeddingPredictionClient:
    """Wrapper around Prediction Service Client."""

    def __init__(
        self,
        project: str,
        location: str = "us-central1",
        api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com",
    ):
        client_options = {"api_endpoint": api_regional_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=client_options
        )
        self.location = location
        self.project = project

    def _get_embedding_response(
        self, text: str = None, image_bytes: bytes = None
    ) -> aiplatform.gapic.types.PredictResponse:
        """Gets embedding response from the prediction service."""
        if not text and not image_bytes:
            raise ValueError("At least one of text or image_bytes must be specified.")

        instance = struct_pb2.Struct()
        if text:
            instance.fields["text"].string_value = text

        if image_bytes:
            encoded_content = base64.b64encode(image_bytes).decode("utf-8")
            image_struct = instance.fields["image"].struct_value
            image_struct.fields["bytesBase64Encoded"].string_value = encoded_content

        instances = [instance]
        endpoint = (
            f"projects/{self.project}/locations/{self.location}"
            "/publishers/google/models/multimodalembedding@001"
        )
        return self.client.predict(endpoint=endpoint, instances=instances)

    def get_embedding(
        self, text: str = None, image_bytes: bytes = None
    ) -> EmbeddingResponse:
        """Gets text embedding or image embedding from the prediction service."""
        response = self._get_embedding_response(text, image_bytes)

        text_embedding = (
            [v for v in response.predictions[0]["textEmbedding"]] if text else None
        )
        image_embedding = (
            [v for v in response.predictions[0]["imageEmbedding"]]
            if image_bytes
            else None
        )

        return EmbeddingResponse(
            text_embedding=text_embedding, image_embedding=image_embedding
        )


client = EmbeddingPredictionClient(project=PROJECT_ID)


def get_image_embedding_from_image_content(content: bytes) -> typing.Sequence[float]:
    """Extracts image embedding from image content."""
    return client.get_embedding(text=None, image_bytes=content).image_embedding


def get_image_embedding_from_gcs_object(
    gcs_bucket: str, gcs_object: str
) -> typing.Sequence[float]:
    """Fetches image from GCS and extracts image embedding."""
    client = storage.Client()
    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(gcs_object)

    with blob.open("rb") as f:
        return get_image_embedding_from_image_content(f.read())


def get_image_embedding_from_file(file_path: str) -> typing.Sequence[float]:
    """Reads image from file and extracts image embedding."""
    with open(file_path, "rb") as f:
        return get_image_embedding_from_image_content(f.read())


def get_text_embedding(text: str) -> typing.Sequence[float]:
    """Extracts text embedding from text."""
    return client.get_embedding(text=text, image_bytes=None).text_embedding


from pandas.io.parsers.readers import ParserBase
import time
import re
import cv2


def searchImagesByEmbedding(
    start_time, embedding, search_backend_function, num_neighbors=3
):
    neighbors, distances = search_backend_function(embedding, num_neighbors)
    end = time.time()

    gcsClient = storage.Client()
    for id, dist in zip(neighbors, distances):
        print(f"docid:{id} dist:{dist} gcsUri:{df.gcsUri[id]}")
        # Display the image
        gcsUri = df.gcsUri[id]
        m = re.search("gs://([^/]*)/([^$]*)", gcsUri)
        imageBlob = gcsClient.get_bucket(m[1]).blob(m[2])
        tmpFilename = "/tmp/tmp_image"
        imageBlob.download_to_filename(tmpFilename)
        image = cv2.imread(tmpFilename, -1)
        cv2_imshow(image)

    print("Latency (ms):", 1000 * (end - start_time))


def searchImagesByText(query, search_backend_function, num_neighbors=3):
    start_time = time.time()
    query_embedding = getTextEmbedding(query)
    return searchImagesByEmbedding(start_time, query_embedding, search_backend_function)


def searchImagesByUploadedImages(search_backend_function, num_neighbors=3):
    uploaded = files.upload()
    for filename in uploaded.keys():
        print("Searching images similar to {}".format(filename))
        image = cv2.imread(filename, -1)
        cv2_imshow(image)
        start_time = time.time()
        image_embedding = getImageEmbeddingFromFile(filename)
        searchImagesByEmbedding(
            start_time, image_embedding, search_backend_function, num_neighbors
        )
