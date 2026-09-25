"""
Retrieval: embed a query, search the Chroma collection, return top-k chunks.
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(__file__).parent / "chroma_db"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "erp_documents"

_model = None
_collection = None


def _load():
    """Lazy-load model/collection once per process instead of per-request."""
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Return the top_k most relevant chunks for a query, each with a
    similarity-style score attached (Chroma returns distance; smaller
    distance = more similar, so we convert it to look like a similarity
    score for readability)."""
    _load()

    query_vec = _model.encode([query], convert_to_numpy=True).tolist()

    results = _collection.query(
        query_embeddings=query_vec,
        n_results=top_k,
    )

    chunks = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
        chunks.append({
            "chunk_id": chunk_id,
            "doc_id": meta["doc_id"],
            "doc_type": meta["doc_type"],
            "text": doc,
            "score": round(1 - dist, 3),
        })
    return chunks
