
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models as rest
from server.service.qdrant_svc import qdrant_client

load_dotenv()
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")


def clear_collection():
    """
    Remove all points (vectors + payloads) inside the collection
    but keep the collection structure.
    """
    qdrant_client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=rest.FilterSelector(
            filter=rest.Filter(must=[]) 
        )
    )
    return (f"Cleared all data in collection '{COLLECTION_NAME}'")

if __name__ == "__main__":
    data = clear_collection()
    print(data)