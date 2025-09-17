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
    try:
        result = process_pdfs_to_qdrant(payload.dir)
        return QdrantIngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=QdrantListResponse)
def list_qdrant(limit: int = 50):
    try:
        items_raw = read_collection(limit=limit)
        items = [QdrantListResponseItem(**it) for it in items_raw]
        return QdrantListResponse(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data", response_model=QdrantDeleteResponse)
def delete_by_id(payload: QdrantDeleteByIdRequest):
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
    try:
        collection = os.environ.get("COLLECTION_NAME")
        qdrant_client.delete(
            collection_name=collection,
            points_selector=rest.FilterSelector(filter=rest.Filter(must=[])),
        )
        return QdrantDeleteResponse(status="ok", detail=f"Cleared collection '{collection}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


