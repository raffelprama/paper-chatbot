from typing import Optional, List
from pydantic import BaseModel, Field


class QdrantIngestRequest(BaseModel):
    dir: str = Field(..., description="Directory path containing PDFs or a single PDF path")


class QdrantIngestResponse(BaseModel):
    success: bool
    message: str
    documents_processed: int
    chunks_created: int
    points_inserted: int
    errors: List[str] = []


class QdrantListResponseItem(BaseModel):
    id: str
    payload: dict
    vector_length: int


class QdrantListResponse(BaseModel):
    items: List[QdrantListResponseItem]


class QdrantDeleteByIdRequest(BaseModel):
    id: str


class QdrantDeleteResponse(BaseModel):
    status: str
    detail: Optional[str] = None


