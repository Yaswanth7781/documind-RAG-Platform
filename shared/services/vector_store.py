import os
from fastapi import HTTPException

# ---- Configuration ----
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documind-index-1024")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing. Pinecone is now the only supported vector DB.")

# Lazy Singleton
_pc_index = None
_pc_client = None

def get_pinecone_client():
    global _pc_client
    if _pc_client is None:
        from pinecone import Pinecone
        _pc_client = Pinecone(api_key=PINECONE_API_KEY)
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

def search_similar_with_metadata(query: str, n_results: int = 3):
    """
    Returns text chunks AND metadata from Pinecone using Inference API.
    """
    pc = get_pinecone_client()
    pc_index = get_pinecone_index()
    
    # Remote query embedding
    response = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={"input_type": "query"}
    )
    query_embedding = response[0]['values']
    
    results = pc_index.query(
        vector=query_embedding,
        top_k=n_results,
        include_metadata=True
    )
    
    docs = [match["metadata"]["text"] for match in results.get("matches", [])]
    metas = [match["metadata"] for match in results.get("matches", [])]
    scores = [match["score"] for match in results.get("matches", [])]
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
                for doc_id in ids:
                    if "-p" in doc_id:
                        # Extract the filename prefix: e.g. "authservice.pdf" from "authservice.pdf-p1-c0"
                        filename = doc_id.rsplit("-p", 1)[0]
                        unique_sources.add(filename)
                    else:
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
            if "metadata" in match and "source" in match["metadata"]:
                unique_sources.add(match["metadata"]["source"])
        return list(unique_sources)
    except Exception as e:
        print(f"Pinecone Sync Error: {e}")
        return []

def delete_document(filename: str):
    """Deletes all chunks associated with a specific document."""
    pc_index = get_pinecone_index()
    try:
        pc_index.delete(filter={"source": filename})
    except Exception as e:
        print(f"Failed to delete document {filename}: {e}")
