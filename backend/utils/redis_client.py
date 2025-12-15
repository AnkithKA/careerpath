import redis
from backend.config import REDIS_URL

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# Startup sanity check
try:
    redis_client.ping()
    print("[redis] Connected successfully")
except Exception as e:
    raise RuntimeError(f"[redis] Connection failed: {e}")
