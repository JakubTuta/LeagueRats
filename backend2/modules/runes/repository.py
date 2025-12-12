import typing

import utils

from . import models

CACHE_SETTINGS = {
    "runes": {
        "cache_name": "runes",
        "ttl": 86400,
        "cache_prefix": "runes",
    }
}


class RunesCache:
    def __init__(self):
        self.cache_prefix = CACHE_SETTINGS["runes"]["cache_prefix"]
        self.runes_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["runes"]["cache_name"],
            ttl=CACHE_SETTINGS["runes"]["ttl"],
        )

    def get_runes(self) -> typing.Optional[list[models.Rune]]:
        cache_key = f"{self.cache_prefix}:all"
        cached_data = self.runes_cache.get(cache_key)
        if cached_data:
            return [models.Rune(**rune) for rune in cached_data]
        return None

    def set_runes(self, runes: list[models.Rune]) -> None:
        cache_key = f"{self.cache_prefix}:all"
        self.runes_cache.set(cache_key, [rune.model_dump() for rune in runes])


class RunesRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.redis_client = redis_client
        self.cache_prefix = CACHE_SETTINGS["runes"]["cache_prefix"]

    async def get_runes(self) -> typing.Optional[list[models.Rune]]:
        redis_key = f"{self.cache_prefix}:all"
        cached_data = await self.redis_client.get_json(redis_key)
        if cached_data:
            return [models.Rune(**rune) for rune in cached_data]
        return None

    async def set_runes(self, runes: list[models.Rune]) -> None:
        redis_key = f"{self.cache_prefix}:all"
        ttl = CACHE_SETTINGS["runes"]["ttl"]
        await self.redis_client.set_json(
            redis_key, [rune.model_dump() for rune in runes], ex=ttl
        )


class RunesFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore_client = firestore_client

    async def get_runes(self) -> typing.Optional[list[models.Rune]]:
        document = await self.firestore_client.get_document(
            collection="help", document_id="runes1"
        )

        if not isinstance(document, dict):
            return None

        runes_data = document.get("data", [])
        if not runes_data:
            return None

        return [models.Rune(**rune) for rune in runes_data]
