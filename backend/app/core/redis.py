import redis
from app.core.config import settings
# core.config에서 settings 인스턴스 가져와서

# 실제 redis에 넣기. (보안문제)
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)