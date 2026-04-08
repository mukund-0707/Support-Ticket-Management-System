import json
from fastapi.encoders import jsonable_encoder
from utils.redis_connection import redis_client


async def get_cache(key: str):
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def set_cache(key: str, value, expire: int = 60):
    await redis_client.set(key, json.dumps(jsonable_encoder(value)), ex=expire)


async def delete_pattern(pattern: str):
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
