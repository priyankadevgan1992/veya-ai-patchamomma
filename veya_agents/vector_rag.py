import sqlite3
import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "veya_data", "veya_app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def init_vector_memory_table():
    """Initializes the Vector RAG Memory Table in SQLite."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vector_memories (
            doc_id TEXT PRIMARY KEY,
            internal_uuid TEXT NOT NULL,
            category TEXT NOT NULL,
            document_text TEXT NOT NULL,
            metadata_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(internal_uuid) REFERENCES twin_profiles(internal_uuid)
        )
    """)
    conn.commit()
    conn.close()

class VeyaRAGVectorStore:
    """
    Veya RAG Vector Engine:
    Stores episodic and factual user memories into SQLite and performs
    high-speed cosine similarity retrieval to ground agent reasoning.
    """

    def __init__(self):
        init_vector_memory_table()

    def store_memory(self, internal_uuid: str, text: str, category: str = "CONVERSATION", metadata: Dict[str, Any] = None) -> str:
        """Stores a new memory node into the user's vector store."""
        doc_id = f"mem_{os.urandom(6).hex()}"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vector_memories (doc_id, internal_uuid, category, document_text, metadata_json)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, internal_uuid, category, text, json.dumps(metadata or {})))
        conn.commit()
        conn.close()
        return doc_id

    def retrieve_relevant_context(self, internal_uuid: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves top-k most relevant historical context and life facts
        matching the query using vector cosine similarity.
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT doc_id, category, document_text, metadata_json, timestamp FROM vector_memories WHERE internal_uuid = ?", (internal_uuid,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not rows:
            return []

        documents = [r["document_text"] for r in rows]
        
        # Build Vector Index & Compute Cosine Similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([query] + documents)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Rank documents
            ranked_indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in ranked_indices[:top_k]:
                score = float(similarities[idx])
                if score > 0.05: # Relevance threshold
                    item = rows[idx]
                    item["similarity_score"] = round(score, 3)
                    results.append(item)
            return results
        except Exception:
            return rows[:top_k]

# Global Vector Store Instance
vector_store = VeyaRAGVectorStore()
