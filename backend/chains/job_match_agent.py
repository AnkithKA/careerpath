import os
import json
import requests

from backend.utils.embeddings import get_embedding_model
from backend.utils.pinecone_manager import upsert_job, query_jobs
from backend.utils.redis_client import redis_client

# =====================================
# CONFIG
# =====================================
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

embedding_model = get_embedding_model()

# =====================================
# REDIS CACHE HELPERS
# =====================================
def _get_cached_jobs(cache_key: str):
    try:
        data = redis_client.get(f"jobs:{cache_key}")
        return json.loads(data) if data else None
    except Exception as e:
        print(f"[redis] Cache read failed: {e}")
        return None


def _set_cached_jobs(cache_key: str, jobs: list, ttl: int = 60 * 60 * 12):
    try:
        redis_client.setex(
            f"jobs:{cache_key}",
            ttl,
            json.dumps(jobs, ensure_ascii=False)
        )
    except Exception as e:
        print(f"[redis] Cache write failed: {e}")


# =====================================
# FETCH JOBS FROM API
# =====================================
def fetch_real_jobs(
    role: str,
    location: str = "us",
    pages: int = 1,
    date_posted: str = "all"
):
    """Fetch live jobs using the JSearch API with filters."""
    print(
        f"[job_fetch] Fetching jobs for '{role}' "
        f"in {location} (date={date_posted}, pages={pages})"
    )

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
            print(
                f"[job_fetch] API error {response.status_code}: "
                f"{response.text[:150]}"
            )
            return []

        jobs = response.json().get("data", [])
        print(f"[job_fetch] ✅ Retrieved {len(jobs)} jobs from API.")
        return jobs

    except Exception as e:
        print(f"[job_fetch] ❌ Request failed: {e}")
        return []


# =====================================
# MAIN PIPELINE
# =====================================
def get_best_job_matches(
    role: str,
    country: str = "us",
    remote: bool = False,
    date_posted: str = "all",
    pages: int = 1
):
    """
    Fetch, embed, cache (Redis), and return best-matching jobs using Pinecone.
    """

    cache_key = f"{role.lower()}_{country}_{remote}_{date_posted}_{pages}"

    # ---------- 1️⃣ CHECK REDIS CACHE ----------
    cached = _get_cached_jobs(cache_key)
    if cached:
        print(f"[redis] Reusing cached jobs for {cache_key}")
        return cached

    print(
        f"[job_match_agent] Fetching new jobs for '{role}' "
        f"in {country} (remote={remote}, date={date_posted})"
    )

    # ---------- 2️⃣ FETCH JOBS ----------
    jobs = fetch_real_jobs(
        role,
        location=country,
        pages=pages,
        date_posted=date_posted
    )

    # ---------- 3️⃣ FALLBACK ----------
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
        _set_cached_jobs(cache_key, fallback)
        return fallback

    # ---------- 4️⃣ REMOTE FILTER ----------
    if remote:
        before = len(jobs)
        jobs = [
            j for j in jobs
            if "remote" in (
                (j.get("job_title", "") + j.get("job_description", "")).lower()
            )
        ]
        print(
            f"[job_match_agent] Filtered remote jobs: "
            f"{len(jobs)} of {before}"
        )

    # ---------- 5️⃣ UPSERT INTO PINECONE ----------
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

    # ---------- 6️⃣ QUERY PINECONE ----------
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

    # ---------- 7️⃣ SAVE TO REDIS ----------
    _set_cached_jobs(cache_key, results)
    print(f"[job_match_agent] ✅ Returning {len(results)} best matches (cached).")

    return results


def clear_job_cache():
    """Clear ALL job-related Redis cache."""
    try:
        keys = redis_client.keys("jobs:*")
        if keys:
            redis_client.delete(*keys)
        print("[redis] Cleared all job search cache.")
    except Exception as e:
        print(f"[redis] Cache clear failed: {e}")
