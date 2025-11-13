"""
Cache Manager Service
=====================
Handles caching of frequently accessed spatial data and API responses.
"""

import json
import logging
from functools import wraps
import hashlib
import config

logger = logging.getLogger(__name__)

# Simple in-memory cache (replace with Redis for production)
_cache = {}


class CacheManager:
    """
    Cache manager for spatial data and API responses.
    """

    def __init__(self, cache_type='simple', default_timeout=300):
        """
        Initialize cache manager.

        Args:
            cache_type (str): Type of cache ('simple', 'redis')
            default_timeout (int): Default cache timeout in seconds
        """
        self.cache_type = cache_type
        self.default_timeout = default_timeout

        if cache_type == 'redis':
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    db=config.REDIS_DB,
                    decode_responses=True
                )
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis not available, falling back to simple cache: {e}")
                self.cache_type = 'simple'

    def generate_key(self, prefix, *args, **kwargs):
        """
        Generate a cache key from arguments.

        Args:
            prefix (str): Key prefix
            *args, **kwargs: Arguments to include in key

        Returns:
            str: Generated cache key
        """
        # Create a string representation of arguments
        key_parts = [prefix]

        for arg in args:
            key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")

        key_str = '|'.join(key_parts)

        # Hash for consistent key length
        key_hash = hashlib.md5(key_str.encode()).hexdigest()

        return f"{prefix}:{key_hash}"

    def get(self, key):
        """
        Get value from cache.

        Args:
            key (str): Cache key

        Returns:
            Any: Cached value or None
        """
        try:
            if self.cache_type == 'redis':
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return _cache.get(key)

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key, value, timeout=None):
        """
        Set value in cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            timeout (int, optional): Timeout in seconds
        """
        try:
            timeout = timeout or self.default_timeout

            if self.cache_type == 'redis':
                self.redis_client.setex(
                    key,
                    timeout,
                    json.dumps(value)
                )
            else:
                # Simple in-memory cache (no expiration in this basic version)
                _cache[key] = value

            logger.debug(f"Cached key: {key}")

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key):
        """
        Delete key from cache.

        Args:
            key (str): Cache key
        """
        try:
            if self.cache_type == 'redis':
                self.redis_client.delete(key)
            else:
                _cache.pop(key, None)

            logger.debug(f"Deleted cache key: {key}")

        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def clear(self):
        """
        Clear all cache.
        """
        try:
            if self.cache_type == 'redis':
                self.redis_client.flushdb()
            else:
                _cache.clear()

            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Cache clear error: {e}")


# Global cache instance
cache_manager = CacheManager(
    cache_type=config.CACHE_TYPE,
    default_timeout=config.CACHE_DEFAULT_TIMEOUT
)


def cached(timeout=None, key_prefix='cache'):
    """
    Decorator to cache function results.

    Args:
        timeout (int, optional): Cache timeout in seconds
        key_prefix (str): Prefix for cache key

    Usage:
        @cached(timeout=300, key_prefix='disaster_zones')
        def get_disaster_zones():
            # expensive operation
            return data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager.generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result

            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result, timeout)

            return result

        return wrapper
    return decorator


def invalidate_cache(key_prefix):
    """
    Invalidate all cache keys with given prefix.

    Args:
        key_prefix (str): Cache key prefix to invalidate
    """
    try:
        if cache_manager.cache_type == 'redis':
            # Delete all keys matching pattern
            pattern = f"{key_prefix}:*"
            keys = cache_manager.redis_client.keys(pattern)
            if keys:
                cache_manager.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys with prefix: {key_prefix}")
        else:
            # For simple cache, clear all (no pattern matching)
            keys_to_delete = [k for k in _cache.keys() if k.startswith(key_prefix)]
            for key in keys_to_delete:
                _cache.pop(key, None)
            logger.info(f"Invalidated {len(keys_to_delete)} cache keys")

    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")


# TODO: Add more cache utilities:
# - cache_geojson() - Specific caching for GeoJSON data
# - cache_warming() - Pre-populate cache with frequently accessed data
# - cache_stats() - Get cache hit/miss statistics
# - adaptive_timeout() - Adjust timeout based on data volatility
