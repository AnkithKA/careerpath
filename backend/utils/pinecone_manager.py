from pinecone import Pinecone, ServerlessSpec
from backend.config import (
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_INDEX_NAME
)
from backend.utils.embeddings import get_embedding_model

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
embedding_model = get_embedding_model()

# Create index if it doesn't exist
def init_pinecone_index():
    existing_indexes = [i["name"] for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"[pinecone] Creating new index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384,  # for all-MiniLM-L6-v2 (SBERT)
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    else:
        print(f"[pinecone] Index '{PINECONE_INDEX_NAME}' already exists.")

    return pc.Index(PINECONE_INDEX_NAME)

# Get index reference
index = init_pinecone_index()

# ---------------------------
# Utility Functions
# ---------------------------

def upsert_job(job_id: str, job_text: str, metadata: dict):
    """Store a job posting in Pinecone with its embedding."""
    vector = embedding_model.encode([job_text])[0].tolist()
    index.upsert(vectors=[{
        "id": job_id,
        "values": vector,
        "metadata": metadata
    }])
    print(f"[pinecone] Upserted job: {job_id}")

def query_jobs(query_text: str, top_k: int = 5):
    """Query top K jobs similar to query_text."""
    query_vector = embedding_model.encode([query_text])[0].tolist()
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return results.matches
