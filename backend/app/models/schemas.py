from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str

class SourceItem(BaseModel):
    page: int
    source: str
    snippet: str

class EvaluationMeta(BaseModel):
    faithfulness_score: Optional[float] = 1.0
    grounded_verdict: Optional[str] = "FAITHFUL"
    reasoning: Optional[str] = None
    retrieval_method: Optional[str] = "Hybrid (BM25 + ChromaDB RRF)"
    latency_ms: Optional[float] = None
    cached: Optional[bool] = False

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    evaluation: Optional[EvaluationMeta] = None

class UploadResponse(BaseModel):
    message: str
