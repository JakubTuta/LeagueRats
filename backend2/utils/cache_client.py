import typing

import cachetools

TTL_CACHES: dict[str, "TTLCacheClient"] = {}
LRU_CACHES: dict[str, "LRUCacheClient"] = {}


class TTLCacheClient:
    """Time-based cache for data with known expiry"""

    def __init__(self, max_size: int, ttl: int):
        self._cache = cachetools.TTLCache(maxsize=max_size, ttl=ttl)

    def get(self, key: str) -> typing.Optional[typing.Any]:
        return self._cache.get(key)

    def set(self, key: str, value: typing.Any) -> None:
        self._cache[key] = value

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)


class LRUCacheClient:
    """LRU cache for most-recently-used data"""

    def __init__(self, max_size: int):
        self._cache = cachetools.LRUCache(maxsize=max_size)

    def get(self, key: str) -> typing.Optional[typing.Any]:
        return self._cache.get(key)

    def set(self, key: str, value: typing.Any) -> None:
        self._cache[key] = value

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)


def get_ttl_cache_client(name: str, max_size=1000, ttl=300) -> TTLCacheClient:
    global TTL_CACHES

    if name not in TTL_CACHES:
        TTL_CACHES[name] = TTLCacheClient(max_size=max_size, ttl=ttl)

    return TTL_CACHES[name]


def get_lru_cache_client(name: str, max_size=1000) -> LRUCacheClient:
    global LRU_CACHES

    if name not in LRU_CACHES:
        LRU_CACHES[name] = LRUCacheClient(max_size=max_size)

    return LRU_CACHES[name]


def clear_all_ttl_caches() -> None:
    global TTL_CACHES
    for cache in TTL_CACHES.values():
        cache.clear()


def clear_all_lru_caches() -> None:
    global LRU_CACHES
    for cache in LRU_CACHES.values():
        cache.clear()


def clear_all_caches() -> None:
    clear_all_ttl_caches()
    clear_all_lru_caches()
