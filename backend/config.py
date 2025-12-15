import os
from dotenv import load_dotenv

load_dotenv()

# === GOOGLE CONFIG ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# === PINECONE CONFIG ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east1-gcp")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "careerpath-job-index")

if not GOOGLE_API_KEY:
    raise ValueError("🚨 GOOGLE_API_KEY not found in .env file")
# ==============================
# REDIS CONFIG
# ==============================
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("🚨 REDIS_URL not found in .env file")

# Optional: Redis behavior tuning
REDIS_DEFAULT_TTL = int(os.getenv("REDIS_DEFAULT_TTL", 60 * 60 * 24))  # 24 hours