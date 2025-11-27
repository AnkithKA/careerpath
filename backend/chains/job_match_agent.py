import os
import json
import requests
from backend.utils.pinecone_manager import upsert_job, query_jobs
from backend.utils.embeddings import get_embedding_model

# Load environment keys
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
CACHE_FILE = "backend/data/job_cache.json"

embedding_model = get_embedding_model()
_job_cache = {}

# =====================================
# LOAD CACHE FROM DISK
# =====================================
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            _job_cache = json.load(f)
            print(f"[cache] Loaded {_job_cache.keys().__len__()} job search entries from disk.")
    except Exception:
        _job_cache = {}
else:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def _save_job_cache():
    """Persist job cache to local file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_job_cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[cache] Save failed: {e}")


# =====================================
# FETCH JOBS FROM API
# =====================================
def fetch_real_jobs(role: str, location: str = "us", pages: int = 1, date_posted: str = "all"):
    """Fetch live jobs using the JSearch API with filters."""
    print(f"[job_fetch] Fetching jobs for '{role}' in {location} (date={date_posted}, pages={pages})")

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    params = {
        "query": f"{role} jobs",
        "page": "1",
        "num_pages": str(pages),
        "country": location,
        "date_posted": date_posted
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code != 200:
            print(f"[job_fetch] API error {response.status_code}: {response.text[:150]}")
            return []
        data = response.json()
        jobs = data.get("data", [])
        print(f"[job_fetch] ✅ Retrieved {len(jobs)} jobs from API.")
        return jobs
    except Exception as e:
        print(f"[job_fetch] ❌ Request failed: {e}")
        return []


# =====================================
# MAIN PIPELINE
# =====================================
def get_best_job_matches(role: str, country="us", remote=False, date_posted="all", pages=1):
    """Fetch, embed, and return best job matches using Pinecone."""
    cache_key = f"{role.lower()}_{country}_{remote}_{date_posted}_{pages}"

    # ✅ Check Cache
    if cache_key in _job_cache:
        print(f"[cache] Reusing cached jobs for {cache_key}")
        return _job_cache[cache_key]

    print(f"[job_match_agent] Fetching new jobs for '{role}' in {country} (remote={remote}, date={date_posted})")
    jobs = fetch_real_jobs(role, location=country, pages=pages, date_posted=date_posted)

    if not jobs:
        print("[job_match_agent] ❌ No jobs fetched. Returning fallback job.")
        fallback = [
            {
                "title": f"{role} (Example Role)",
                "company": "AI Labs",
                "description": "Develop and deploy ML models on cloud platforms.",
                "link": "https://example.com/apply",
                "score": 0.65
            }
        ]
        _job_cache[cache_key] = fallback
        _save_job_cache()
        return fallback

    # --- Apply remote filter if requested ---
    if remote:
        before = len(jobs)
        jobs = [
            j for j in jobs
            if "remote" in (j.get("job_title", "").lower() + j.get("job_description", "").lower())
        ]
        print(f"[job_match_agent] Filtered remote jobs: {len(jobs)} of {before}")

    # --- Upsert job embeddings into Pinecone ---
    for job in jobs:
        title = job.get("job_title", "")
        company = job.get("employer_name", "")
        desc = job.get("job_description", "")
        link = job.get("job_apply_link", "")
        text = f"{title} {desc}".strip()

        if not text:
            continue

        try:
            vector = embedding_model.encode([text])[0].tolist()
            metadata = {
                "title": title,
                "company": company,
                "description": desc,
                "link": link
            }
            upsert_job(f"{company}_{title}", text, metadata)
        except Exception as e:
            print(f"[embedding error] {e}")
            continue

    # --- Query Pinecone for best semantic matches ---
    pinecone_results = query_jobs(role)

    results = []
    for match in pinecone_results:
        results.append({
            "title": match["metadata"].get("title"),
            "company": match["metadata"].get("company"),
            "description": match["metadata"].get("description"),
            "link": match["metadata"].get("link"),
            "score": round(match["score"], 2)
        })

    # ✅ Save to cache (both memory + file)
    _job_cache[cache_key] = results
    _save_job_cache()

    print(f"[job_match_agent] ✅ Returning {len(results)} best matches (cached).")
    return results

def clear_job_cache():
    """Clear all cached job data."""
    global _job_cache
    _job_cache = {}
    _save_job_cache()
    print("[cache] Cleared all job search cache.")
