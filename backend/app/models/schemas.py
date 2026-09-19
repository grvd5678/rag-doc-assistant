from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    page: int
    source: str
    snippet: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

class UploadResponse(BaseModel):
    message: str