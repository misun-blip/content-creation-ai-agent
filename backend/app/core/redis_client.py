"""
Redis 缓存客户端
提供异步 get/set/delete 操作，支持 JSON 序列化和 TTL 过期
"""

import json
import logging
from typing import Optional, Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建异步 Redis 连接
redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    """获取 Redis 连接（懒初始化）"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            # 测试连接
            await redis_client.ping()
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.warning(f"Redis 连接失败，缓存功能将被禁用: {e}")
            redis_client = None
    return redis_client


async def get_cache(key: str) -> Optional[Any]:
    """
    从 Redis 获取缓存数据（自动反序列化 JSON）
    连接失败或 key 不存在时返回 None（不影响正常业务）
    """
    try:
        client = await get_redis()
        if client is None:
            return None
        value = await client.get(key)
        if value is not None:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Redis GET 失败 (key={key}): {e}")
    return None


async def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """
    写入缓存（自动序列化为 JSON）
    ttl: 过期时间（秒），默认 5 分钟
    """
    try:
        client = await get_redis()
        if client is None:
            return False
        await client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
        return True
    except Exception as e:
        logger.warning(f"Redis SET 失败 (key={key}): {e}")
        return False


async def delete_cache(key: str) -> bool:
    """删除缓存"""
    try:
        client = await get_redis()
        if client is None:
            return False
        await client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis DELETE 失败 (key={key}): {e}")
        return False


async def delete_cache_pattern(pattern: str) -> int:
    """按模式批量删除缓存（如 dashboard:* ）"""
    try:
        client = await get_redis()
        if client is None:
            return 0
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await client.delete(*keys)
        return len(keys)
    except Exception as e:
        logger.warning(f"Redis DELETE PATTERN 失败 (pattern={pattern}): {e}")
        return 0


async def close_redis():
    """关闭 Redis 连接（应用关闭时调用）"""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
        logger.info("Redis 连接已关闭")
