import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

def tokenize(text: str) -> List[str]:
    """Lightweight whitespace and alphanumeric tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())

def reciprocal_rank_fusion(
    dense_results: List[Document],
    sparse_results: List[Document],
    k: int = 60,
    top_n: int = 4
) -> List[Document]:
    """
    Applies Reciprocal Rank Fusion (RRF) to combine dense vector rankings and BM25 sparse rankings.
    Formula: RRF_score(d) = sum( 1 / (k + rank_i(d)) ) for each retriever i
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    def get_doc_id(doc: Document) -> str:
        # Unique doc id based on source, page, and chunk content prefix
        src = doc.metadata.get("source", "doc")
        page = doc.metadata.get("page", 1)
        prefix = doc.page_content[:40]
        return f"{src}_{page}_{prefix}"

    # Rank dense results
    for rank, doc in enumerate(dense_results):
        doc_id = get_doc_id(doc)
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    # Rank sparse BM25 results
    for rank, doc in enumerate(sparse_results):
        doc_id = get_doc_id(doc)
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    # Sort descending by RRF score
    sorted_doc_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [doc_map[doc_id] for doc_id in sorted_doc_ids[:top_n]]

class BM25Retriever:
    """In-memory BM25 index built dynamically over the active collection chunks."""
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.corpus = [tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    def search(self, query: str, top_k: int = 10) -> List[Document]:
        if not self.bm25 or not self.documents:
            return []
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        # Return only documents with a positive BM25 score
        return [self.documents[i] for i in top_indices if scores[i] > 0]
