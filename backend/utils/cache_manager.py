import json
import os

CACHE_FILE = "backend/data_cache.json"

def load_cache():
    """Load cache from file."""
    if not os.path.exists(CACHE_FILE):
        return {"jd_cache": {}, "learning_cache": {}}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"jd_cache": {}, "learning_cache": {}}


def save_cache(cache_data):
    """Save cache to file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=4, ensure_ascii=False)


def get_cached_jd(role):
    """Fetch JD if it exists in cache."""
    cache = load_cache()
    return cache["jd_cache"].get(role.lower())


def set_cached_jd(role, jd_text):
    """Save JD for a role."""
    cache = load_cache()
    cache["jd_cache"][role.lower()] = jd_text
    save_cache(cache)


def get_cached_learning(skill):
    """Fetch learning path for a skill."""
    cache = load_cache()
    return cache["learning_cache"].get(skill.lower())


def set_cached_learning(skill, roadmap):
    """Save learning path for a skill."""
    cache = load_cache()
    cache["learning_cache"][skill.lower()] = roadmap
    save_cache(cache)
