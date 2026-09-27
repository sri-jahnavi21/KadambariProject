from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    status: str  # "ALLOW" | "BLOCK" | "FLAG"
    triggered_categories: List[str] = []
