import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv(override=True)

# ---- Configuration ----
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documind-index-1024")

# Lazy Singleton
_pc_index = None
_pc_client = None

def get_pinecone_client():
    global _pc_client
    api_key = os.getenv("PINECONE_API_KEY") or PINECONE_API_KEY
    if not api_key:
        raise ValueError("PINECONE_API_KEY is missing. Pinecone is now the required vector DB.")
    if _pc_client is None:
        from pinecone import Pinecone
        _pc_client = Pinecone(api_key=api_key)
    return _pc_client

def get_pinecone_index():
    global _pc_index
    if _pc_index is None:
        from pinecone import ServerlessSpec
        pc = get_pinecone_client()
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_INDEX_NAME, 
                dimension=1024,  # multilingual-e5-large uses 1024 dimensions
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
            )
        _pc_index = pc.Index(PINECONE_INDEX_NAME)
    return _pc_index

def add_texts(texts: list[str], metadatas: list[dict], ids: list[str]):
    """
    Adds text chunks into Pinecone using remote Serverless Inference.
    """
    pc = get_pinecone_client()
    pc_index = get_pinecone_index()
    
    vectors = []
    batch_size = 50  # Pinecone inference supports up to ~96 per batch
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        
        # Remote Embedding generation (no local download)
        response = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=batch_texts,
            parameters={"input_type": "passage", "truncate": "END"}
        )
        
        embeddings = [item['values'] for item in response]
        
        batch_vectors = []
        for j in range(len(batch_texts)):
            batch_vectors.append({
                "id": batch_ids[j],
                "values": embeddings[j],
                "metadata": {**batch_metas[j], "text": batch_texts[j]}
            })
            
        # Upsert
        pc_index.upsert(vectors=batch_vectors)

import re

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

def tokenize_text(text: str) -> list[str]:
    """Tokenize string into lowercase terms for BM25 ranking."""
    return re.findall(r'\w+', text.lower())

def search_similar_with_metadata(query: str, n_results: int = 3, hybrid: bool = True):
    """
    Performs Hybrid Search (BM25 Lexical Keyword + Pinecone Dense Semantic Vector Search)
    fused with Reciprocal Rank Fusion (RRF).
    """
    pc = get_pinecone_client()
    pc_index = get_pinecone_index()
    
    # 1. Remote query embedding via Pinecone inference API
    response = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={"input_type": "query"}
    )
    query_embedding = response[0]['values']
    
    # Fetch candidate pool for RRF re-ranking (e.g., top 15 candidates)
    candidate_k = max(n_results * 5, 15)
    results = pc_index.query(
        vector=query_embedding,
        top_k=candidate_k,
        include_metadata=True
    )
    
    matches = results.get("matches", [])
    if not matches:
        return [], [], []
    
    raw_docs = [match["metadata"]["text"] for match in matches if "metadata" in match and "text" in match["metadata"]]
    raw_metas = [match["metadata"] for match in matches if "metadata" in match and "text" in match["metadata"]]
    raw_scores = [match["score"] for match in matches if "metadata" in match and "text" in match["metadata"]]
    
    if not raw_docs:
        return [], [], []
        
    if not hybrid or not HAS_BM25 or len(raw_docs) <= 1:
        return raw_docs[:n_results], raw_metas[:n_results], raw_scores[:n_results]
    
    # 2. BM25 Lexical Keyword Search Scoring
    tokenized_corpus = [tokenize_text(doc) for doc in raw_docs]
    tokenized_query = tokenize_text(query)
    
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Ranks for Dense Vector Search (0-indexed)
    vector_ranks = list(range(len(raw_docs)))
    
    # Ranks for BM25 (sort indices descending by score)
    bm25_indices_sorted = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
    bm25_ranks = {idx: rank for rank, idx in enumerate(bm25_indices_sorted)}
    
    # 3. Reciprocal Rank Fusion (RRF)
    # RRF_Score(d) = alpha / (60 + rank_vector) + (1 - alpha) / (60 + rank_bm25)
    k_rrf = 60
    alpha = 0.5
    rrf_scores = []
    
    for i in range(len(raw_docs)):
        v_rank = vector_ranks[i]
        b_rank = bm25_ranks[i]
        rrf = (alpha / (k_rrf + v_rank + 1)) + ((1 - alpha) / (k_rrf + b_rank + 1))
        rrf_scores.append(rrf)
    
    # Combine and sort by final RRF score descending
    combined = list(zip(rrf_scores, raw_docs, raw_metas, raw_scores))
    combined.sort(key=lambda x: x[0], reverse=True)
    
    top_items = combined[:n_results]
    docs = [item[1] for item in top_items]
    metas = [item[2] for item in top_items]
    # Retain dense vector score for similarity threshold verification
    scores = [item[3] for item in top_items]
    
    return docs, metas, scores

def search_similar(query: str, n_results: int = 3) -> list[str]:
    """Legacy endpoint, returning only document text."""
    docs, _, _ = search_similar_with_metadata(query, n_results)
    return docs

def get_all_documents():
    """Gets all unique document filenames."""
    pc_index = get_pinecone_index()
    try:
        unique_sources = set()
        # 1. Attempt to list all record IDs (recommended for serverless indexes)
        try:
            for ids in pc_index.list():
                for item in ids:
                    doc_id = item.id if hasattr(item, "id") else str(item)
                    if "-p" in doc_id:
                        # Extract the filename prefix: e.g. "authservice.pdf" from "authservice.pdf-p1-c0"
                        filename = doc_id.rsplit("-p", 1)[0]
                        if filename.lower().endswith(".pdf"):
                            unique_sources.add(filename)
                    else:
                        if doc_id.lower().endswith(".pdf"):
                            unique_sources.add(doc_id)
            if unique_sources:
                return list(unique_sources)
        except Exception as list_err:
            print(f"Pinecone list() failed, falling back to query: {list_err}")

        # 2. Fallback: Query using a non-zero vector to avoid 400 Bad Request
        results = pc_index.query(
            vector=[0.1] * 1024,
            top_k=10000,
            include_metadata=True
        )
        for match in results.get("matches", []):
            metadata = match.get("metadata") if hasattr(match, "get") else getattr(match, "metadata", None)
            if metadata and "source" in metadata:
                source = metadata["source"]
                if source.lower().endswith(".pdf"):
                    unique_sources.add(source)
        return list(unique_sources)
    except Exception as e:
        print(f"Pinecone Sync Error: {e}")
        raise RuntimeError(f"Could not list uploaded documents from Pinecone: {e}") from e

def delete_document(filename: str):
    """Deletes all chunks associated with a specific document."""
    pc_index = get_pinecone_index()
    try:
        pc_index.delete(filter={"source": filename})
    except Exception as e:
        print(f"Failed to delete document {filename}: {e}")
        raise RuntimeError(f"Could not delete document {filename} from Pinecone: {e}") from e
