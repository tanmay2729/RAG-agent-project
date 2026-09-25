"""
Ingestion pipeline: load documents -> chunk -> embed -> store in Chroma.

Run: python -m app.ingest
Produces: a persistent Chroma collection under app/chroma_db/

Everything here is free: sentence-transformers runs locally (no API calls,
no cost), and Chroma is a local, open-source vector store (no hosting fees).
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

DATA_PATH = Path(__file__).parent.parent / "data" / "sample_docs.json"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
CHROMA_DIR.mkdir(exist_ok=True)

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, free, CPU-friendly, runs locally
COLLECTION_NAME = "erp_documents"
CHUNK_SIZE = 300       # characters per chunk
CHUNK_OVERLAP = 50     # overlap between consecutive chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Fixed-size character chunking with overlap. Simple and easy to explain;
    documents here are short so most will end up as a single chunk anyway."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def load_documents() -> list[dict]:
    return json.loads(DATA_PATH.read_text())


def build_chunks(docs: list[dict]) -> list[dict]:
    """Turn each document into one or more chunk records, keeping a link
    back to the parent document id and type for traceability."""
    chunk_records = []
    for doc in docs:
        pieces = chunk_text(doc["text"])
        for idx, piece in enumerate(pieces):
            chunk_records.append({
                "chunk_id": f"{doc['id']}-{idx}",
                "doc_id": doc["id"],
                "doc_type": doc["type"],
                "text": piece,
            })
    return chunk_records


def main():
    print("Loading documents...")
    docs = load_documents()

    print("Chunking...")
    chunks = build_chunks(docs)
    print(f"{len(docs)} documents -> {len(chunks)} chunks")

    print(f"Loading embedding model: {EMBED_MODEL_NAME}")
    model = SentenceTransformer(EMBED_MODEL_NAME)

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    print("Writing to Chroma...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # Fresh collection each time we re-ingest, so re-running this script doesn't duplicate entries
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{"doc_id": c["doc_id"], "doc_type": c["doc_type"]} for c in chunks],
    )

    print(f"Saved {collection.count()} chunks to Chroma collection '{COLLECTION_NAME}' at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
