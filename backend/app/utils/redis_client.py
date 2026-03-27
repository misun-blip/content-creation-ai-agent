"""
Redis 缓存客户端
提供统一的 Redis 连接管理和缓存操作
"""
import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# --------------- 连接管理 ---------------

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    获取 Redis 客户端实例（单例）。
    连接失败时返回 None 并记录警告，不阻塞应用启动。
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
            retry_on_timeout=True,
        )
        # 测试连接
        _redis_client.ping()
        logger.info("Redis 连接成功: %s", settings.REDIS_URL)
    except Exception as e:
        logger.warning("Redis 连接失败（缓存功能将被禁用）: %s", e)
        _redis_client = None

    return _redis_client


# --------------- 缓存操作 ---------------


def cache_get(key: str) -> Optional[Any]:
    """从缓存中获取值，支持 JSON 反序列化"""
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except (json.JSONDecodeError, redis.RedisError) as e:
        logger.warning("缓存读取失败 key=%s: %s", key, e)
        return None


def cache_set(key: str, value: Any, expire: int = 300) -> bool:
    """设置缓存值，默认过期时间 5 分钟"""
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.setex(key, expire, json.dumps(value, ensure_ascii=False))
        return True
    except redis.RedisError as e:
        logger.warning("缓存写入失败 key=%s: %s", key, e)
        return False


def cache_delete(key: str) -> bool:
    """删除缓存"""
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except redis.RedisError as e:
        logger.warning("缓存删除失败 key=%s: %s", key, e)
        return False


def cache_clear_pattern(pattern: str) -> int:
    """按模式批量删除缓存，返回删除数量"""
    client = get_redis_client()
    if client is None:
        return 0
    try:
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except redis.RedisError as e:
        logger.warning("批量缓存删除失败 pattern=%s: %s", pattern, e)
        return 0
