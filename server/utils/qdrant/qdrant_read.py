from qdrant_client import QdrantClient
# from server.service.llm_svc import llm
import os
from dotenv import load_dotenv
from server.service.qdrant_svc import qdrant_client

load_dotenv()
collection = os.environ.get("COLLECTION_NAME")


def read_collection(limit: int = 50):
    points, _ = qdrant_client.scroll(
        collection_name=collection,
        limit=limit,
        with_payload=True,
        with_vectors=True
    )

    results = []
    for p in points:
        results.append({
            "id": p.id,
            "payload": p.payload,
            "vector_length": len(p.vector) if p.vector is not None else 0
        })
    return results


if __name__ == "__main__":
    data = read_collection(limit=50)
    print(data)
