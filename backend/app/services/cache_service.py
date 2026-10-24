import sqlite3
import os
import json
import time
from typing import Optional, Dict, Any, List

CACHE_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "cache.db")
)

def init_cache():
    """Initializes the SQLite cache table if it doesn't already exist and handles schema migration."""
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semantic_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_filter TEXT DEFAULT '__all__',
            query_normalized TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT NOT NULL,
            faithfulness_score REAL,
            grounded_verdict TEXT,
            latency_ms REAL,
            created_at REAL
        )
    """)
    # Check if doc_filter column exists in legacy tables
    cursor.execute("PRAGMA table_info(semantic_cache)")
    columns = [col[1] for col in cursor.fetchall()]
    if "doc_filter" not in columns:
        try:
            cursor.execute("ALTER TABLE semantic_cache ADD COLUMN doc_filter TEXT DEFAULT '__all__'")
        except Exception:
            pass
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON semantic_cache(doc_filter, query_normalized)")
    conn.commit()
    conn.close()

init_cache()

def normalize_query(query: str) -> str:
    """Normalizes query by stripping, lowercasing, and normalizing whitespace."""
    return " ".join(query.strip().lower().split())

def get_cached_response(query: str, doc_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Checks the cache for an exact normalized match scoped to the document filter."""
    try:
        norm = normalize_query(query)
        filter_val = doc_filter or "__all__"
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT answer, sources, faithfulness_score, grounded_verdict 
            FROM semantic_cache 
            WHERE doc_filter = ? AND query_normalized = ? 
            ORDER BY id DESC LIMIT 1
            """,
            (filter_val, norm)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "answer": row[0],
                "sources": json.loads(row[1]),
                "faithfulness_score": row[2],
                "grounded_verdict": row[3],
                "cached": True
            }
        return None
    except Exception:
        return None

def set_cached_response(
    query: str,
    answer: str,
    sources: List[Dict[str, Any]],
    doc_filter: Optional[str] = None,
    faithfulness_score: Optional[float] = None,
    grounded_verdict: Optional[str] = None,
    latency_ms: Optional[float] = None
):
    """Caches query answer and evaluation metadata scoped to doc filter."""
    try:
        norm = normalize_query(query)
        filter_val = doc_filter or "__all__"
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO semantic_cache (
                doc_filter, query_normalized, answer, sources, faithfulness_score, grounded_verdict, latency_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filter_val,
                norm,
                answer,
                json.dumps(sources),
                faithfulness_score,
                grounded_verdict,
                latency_ms,
                time.time()
            )
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def clear_cache():
    """Clears the cache."""
    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM semantic_cache")
        conn.commit()
        conn.close()
    except Exception:
        pass
