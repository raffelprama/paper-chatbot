from typing import Optional
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    response: str

class MemoryClearResponse(BaseModel):
    status: str
    detail: Optional[str] = None


