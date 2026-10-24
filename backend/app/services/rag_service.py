import os
import time
from typing import Optional
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from ..core.config import settings

from .cache_service import get_cached_response, set_cached_response, clear_cache
from .hybrid_retriever import BM25Retriever, reciprocal_rank_fusion
from .evaluation_service import evaluate_faithfulness

CHROMA_PERSIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
COLLECTION_NAME = "documind_docs"

# Global in-memory cache of Document objects for BM25 indexing
_cached_documents = []
_bm25_retriever = None

def get_embeddings():
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

def get_vector_store():
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

def _refresh_bm25_index():
    global _bm25_retriever, _cached_documents
    try:
        vector_store = get_vector_store()
        all_docs_data = vector_store._collection.get()
        if all_docs_data and all_docs_data.get("documents"):
            docs = []
            for text, meta in zip(all_docs_data["documents"], all_docs_data["metadatas"]):
                docs.append(Document(page_content=text, metadata=meta or {}))
            _cached_documents = docs
            _bm25_retriever = BM25Retriever(_cached_documents)
        else:
            _bm25_retriever = None
    except Exception:
        _bm25_retriever = None

def process_pdf_file(file: UploadFile) -> int:
    global _cached_documents, _bm25_retriever
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    file.file.seek(0)
    content = file.file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    reader = PdfReader(file_path)
    documents = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={"page": i + 1, "source": file.filename}
                )
            )
    
    if not documents:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    vector_store = get_vector_store()
    
    # Clean out any old version of this exact document before adding new chunks
    try:
        existing = vector_store._collection.get(where={"source": file.filename})
        if existing and existing.get("ids"):
            vector_store._collection.delete(ids=existing["ids"])
    except Exception:
        pass

    vector_store.add_documents(chunks)
    
    # Rebuild BM25 index
    _refresh_bm25_index()
    clear_cache()
    
    return len(chunks)

def query_rag_engine(query: str, document_filter: Optional[str] = None):
    global _bm25_retriever
    start_time = time.time()
    
    # ========================================================
    # 🎯 UPGRADE 3: Semantic & Exact Cache Check (<50ms)
    # ========================================================
    cached_result = get_cached_response(query, doc_filter=document_filter)
    if cached_result:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "answer": cached_result["answer"],
            "sources": cached_result["sources"],
            "evaluation": {
                "faithfulness_score": cached_result.get("faithfulness_score", 1.0),
                "grounded_verdict": cached_result.get("grounded_verdict", "FAITHFUL"),
                "reasoning": "Retrieved from Semantic Response Cache (0 LLM tokens consumed).",
                "retrieval_method": "Semantic Cache Hit",
                "latency_ms": latency_ms,
                "cached": True
            }
        }

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {
            "answer": "GEMINI_API_KEY is missing in backend/.env file. Please add your key to proceed.",
            "sources": [],
            "evaluation": None
        }

    try:
        vector_store = get_vector_store()
        doc_count = vector_store._collection.count()
        if doc_count == 0:
            return {
                "answer": "Please upload a document first before asking questions!",
                "sources": [],
                "evaluation": None
            }
        
        # ========================================================
        # 🎯 UPGRADE 1: Hybrid Retrieval with Document-Level Scoping
        # ========================================================
        # 1. Dense retrieval via ChromaDB with optional metadata filter
        where_clause = {"source": document_filter} if document_filter else None
        dense_docs = vector_store.similarity_search(query, k=8, filter=where_clause)
        
        # 2. Sparse retrieval via BM25Okapi with document_filter
        if _bm25_retriever is None:
            _refresh_bm25_index()
            
        sparse_docs = _bm25_retriever.search(query, top_k=8, document_filter=document_filter) if _bm25_retriever else []
        
        # 3. Reciprocal Rank Fusion (RRF) Re-ranking
        if sparse_docs:
            top_docs = reciprocal_rank_fusion(dense_docs, sparse_docs, k=60, top_n=4)
            retrieval_method = f"Hybrid (BM25 + ChromaDB RRF){f' [{document_filter}]' if document_filter else ''}"
        else:
            top_docs = dense_docs[:4]
            retrieval_method = f"Dense Vector Search{f' [{document_filter}]' if document_filter else ''}"

        if not top_docs:
            doc_msg = f" in '{document_filter}'" if document_filter else ""
            return {
                "answer": f"No relevant content found{doc_msg} for your query.",
                "sources": [],
                "evaluation": None
            }
            
        context = "\n\n".join([
            f"--- Source: {doc.metadata.get('source', 'Document')} | Page {doc.metadata.get('page', 1)} ---\n" + doc.page_content
            for doc in top_docs
        ])

        sources = [
            {
                "page": int(doc.metadata.get("page", 1)),
                "source": str(doc.metadata.get("source", "Unknown")),
                "snippet": doc.page_content[:150] + "..."
            }
            for doc in top_docs
        ]

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key
        )
        
        system_scope = f" Answer strictly based on the document '{document_filter}'." if document_filter else ""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are DocuMind AI, an intelligent, reliable document assistant.{system_scope} "
                       "Answer the user's question concisely, clearly, and accurately based ONLY on the provided context below. "
                       "Do NOT mention or hallucinate details from other documents. "
                       "Use formatted markdown with bolding, lists, or code blocks where appropriate for clarity. "
                       "If the information is not present in the context, politely state that you cannot find it in the uploaded document.\n\n"
                       "Context from PDF documents:\n{context}"),
            ("human", "{question}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        response_text = chain.invoke({"context": context, "question": query})
        
        # ========================================================
        # 🎯 UPGRADE 2: Automated Faithfulness & Hallucination Guardrail
        # ========================================================
        context_chunks_text = [doc.page_content for doc in top_docs]
        eval_result = evaluate_faithfulness(
            query=query,
            answer=response_text,
            context_chunks=context_chunks_text,
            api_key=api_key
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        evaluation_meta = {
            "faithfulness_score": eval_result["score"],
            "grounded_verdict": eval_result["verdict"],
            "reasoning": eval_result["reasoning"],
            "retrieval_method": retrieval_method,
            "latency_ms": latency_ms,
            "cached": False
        }

        # Cache the validated response for future identical queries with document scoping
        set_cached_response(
            query=query,
            answer=response_text,
            sources=sources,
            doc_filter=document_filter,
            faithfulness_score=eval_result["score"],
            grounded_verdict=eval_result["verdict"],
            latency_ms=latency_ms
        )
        
        return {
            "answer": response_text,
            "sources": sources,
            "evaluation": evaluation_meta
        }
    except Exception as e:
        return {
            "answer": f"Error querying document: {str(e)}",
            "sources": [],
            "evaluation": None
        }
