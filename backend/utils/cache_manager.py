import json
from backend.utils.redis_client import redis_client

# ======================
# JOB DESCRIPTION CACHE
# ======================
def get_cached_jd(role: str):
    return redis_client.get(f"jd:{role.lower()}")

def set_cached_jd(role: str, jd_text: str, ttl=60 * 60 * 24 * 30):
    redis_client.setex(
        f"jd:{role.lower()}",
        ttl,
        jd_text
    )

# ======================
# LEARNING PATH CACHE
# ======================
def get_cached_learning(skill: str):
    data = redis_client.get(f"learning:{skill.lower()}")
    return json.loads(data) if data else None

def set_cached_learning(skill: str, roadmap: dict, ttl=60 * 60 * 24 * 60):
    redis_client.setex(
        f"learning:{skill.lower()}",
        ttl,
        json.dumps(roadmap)
    )
