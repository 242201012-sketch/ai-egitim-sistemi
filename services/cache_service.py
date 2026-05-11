import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


# 🔑 CACHE GET
def get_cache(key: str):
    return redis_client.get(key)


# 💾 CACHE SET
def set_cache(key: str, value: str, expire=3600):
    redis_client.set(key, value, ex=expire)

    def delete_user_cache(username: str):
        keys = redis_client.keys(f"{username}:*")
        if keys:
            redis_client.delete(*keys)