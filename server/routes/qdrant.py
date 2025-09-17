from fastapi import APIRouter, HTTPException
from typing import List
from qdrant_client import models as rest

from server.schema.qdrant import (
    QdrantIngestRequest,
    QdrantIngestResponse,
    QdrantListResponse,
    QdrantListResponseItem,
    QdrantDeleteByIdRequest,
    QdrantDeleteResponse,
)
from server.utils.qdrant.qdrant_insert import process_pdfs_to_qdrant
from server.utils.qdrant.qdrant_read import read_collection
from server.service.qdrant_svc import qdrant_client
import os


router = APIRouter(prefix="/qdrant", tags=["qdrant"])


@router.post("/data", response_model=QdrantIngestResponse)
def ingest_qdrant(payload: QdrantIngestRequest):
    """
    Ingest PDF documents into Qdrant.

    Request body:
      - dir (str): Absolute path INSIDE the container to a single PDF file
        or a directory containing PDF files.

    Important path note:
      - The application runs with WORKDIR "/opt/app".
      - If you use the provided Dockerfile/Compose, the canonical
        resource location is "/opt/app/resource".
      - Example valid inputs:
          {"dir": "/opt/app/resource/task.pdf"}
          {"dir": "/opt/app/resource/papers"}

    Returns a summary of processed documents and inserted points.
    """
    try:
        result = process_pdfs_to_qdrant(payload.dir)
        return QdrantIngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=QdrantListResponse)
def list_qdrant(limit: int = 50):
    """
    List stored vectors/documents from the configured Qdrant collection.

    Query params:
      - limit (int): Maximum number of records to return. Default 50.
    """
    try:
        items_raw = read_collection(limit=limit)
        items = [QdrantListResponseItem(**it) for it in items_raw]
        return QdrantListResponse(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data", response_model=QdrantDeleteResponse)
def delete_by_id(payload: QdrantDeleteByIdRequest):
    """
    Delete a single point/document by its Qdrant point ID.

    Request body:
      - id (str): The point ID to delete.
    """
    try:
        collection = os.environ.get("COLLECTION_NAME")
        qdrant_client.delete(
            collection_name=collection,
            points_selector=rest.PointIdsList(points=[payload.id]),
        )
        return QdrantDeleteResponse(status="ok", detail=f"Deleted id={payload.id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data/all", response_model=QdrantDeleteResponse)
def delete_all():
    """
    Remove all points (vectors and payloads) in the configured collection.
    The collection itself remains and can be reused for new inserts.
    """
    try:
        collection = os.environ.get("COLLECTION_NAME")
        qdrant_client.delete(
            collection_name=collection,
            points_selector=rest.FilterSelector(filter=rest.Filter(must=[])),
        )
        return QdrantDeleteResponse(status="ok", detail=f"Cleared collection '{collection}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


