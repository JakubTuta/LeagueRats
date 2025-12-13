import typing

import utils

from . import models

CACHE_SETTINGS = {
    "active_match": {
        "cache_name": "active_match",
        "ttl": 600,  # 10 minutes
        "cache_prefix": "active_match",
    },
    "match_history": {
        "cache_name": "match_history",
        "ttl": 43200,  # 12 hours
        "cache_prefix": "match_history",
    },
}


class MatchCache:
    def __init__(self):
        self.active_match_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["active_match"]["cache_name"],
            ttl=CACHE_SETTINGS["active_match"]["ttl"],
        )
        self.match_history_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["match_history"]["cache_name"],
            ttl=CACHE_SETTINGS["match_history"]["ttl"],
        )

    def get_active_match(
        self,
        puuid: str,
    ) -> models.ActiveMatch | None:
        cache_key = f"{CACHE_SETTINGS['active_match']['cache_prefix']}:{puuid}"
        cached_data = self.active_match_cache.get(cache_key)

        if cached_data is not None:
            return models.ActiveMatch(**cached_data)

        return None

    def set_active_match(
        self,
        puuid: str,
        active_match: models.ActiveMatch,
    ) -> None:
        cache_key = f"{CACHE_SETTINGS['active_match']['cache_prefix']}:{puuid}"
        active_match_data = active_match.model_dump(mode='json')
        self.active_match_cache.set(cache_key, active_match_data)

    def get_match_history(
        self,
        match_ids: list[str],
    ) -> dict[str, models.MatchHistory]:
        cache_prefix = CACHE_SETTINGS["match_history"]["cache_prefix"]

        match_history = {}
        for match_id in match_ids:
            cache_key = f"{cache_prefix}:{match_id}"
            cached_data = self.match_history_cache.get(cache_key)
            if cached_data is not None:
                match_history[match_id] = models.MatchHistory(**cached_data)

        return match_history

    def set_match_history(
        self,
        match_histories: list[models.MatchHistory],
    ) -> None:
        cache_prefix = CACHE_SETTINGS["match_history"]["cache_prefix"]

        for match_history in match_histories:
            cache_key = f"{cache_prefix}:{match_history.metadata.matchId}"
            match_history_data = match_history.model_dump(mode='json')
            self.match_history_cache.set(cache_key, match_history_data)


class MatchRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.redis = redis_client

    async def get_active_match(
        self,
        puuid: str,
    ) -> models.ActiveMatch | None:
        redis_key = f"{CACHE_SETTINGS['active_match']['cache_prefix']}:{puuid}"
        data = await self.redis.get_json(redis_key)

        if data is not None:
            return models.ActiveMatch(**data)

        return None

    async def set_active_match(
        self,
        puuid: str,
        active_match: models.ActiveMatch,
    ) -> None:
        redis_key = f"{CACHE_SETTINGS['active_match']['cache_prefix']}:{puuid}"
        active_match_data = active_match.model_dump(mode='json')
        await self.redis.set_json(
            redis_key,
            active_match_data,
            ex=CACHE_SETTINGS["active_match"]["ttl"],
        )

    async def get_match_history(
        self,
        match_ids: list[str],
    ) -> dict[str, models.MatchHistory]:
        redis_keys = [
            f"{CACHE_SETTINGS['match_history']['cache_prefix']}:{match_id}"
            for match_id in match_ids
        ]
        cached_data = await self.redis.get_many_json(*redis_keys)

        match_history = {
            match_id: models.MatchHistory(**data)
            for match_id, data in zip(match_ids, cached_data)
            if data is not None
        }

        return match_history

    async def set_match_history(
        self,
        match_histories: list[models.MatchHistory],
    ) -> None:
        redis_data = {
            f"{CACHE_SETTINGS['match_history']['cache_prefix']}:{match_history.metadata.matchId}": match_history.model_dump(mode='json')
            for match_history in match_histories
        }

        await self.redis.set_many_json(
            redis_data,
            ex=CACHE_SETTINGS["match_history"]["ttl"],
        )


class MatchFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore = firestore_client

    async def get_match_history(
        self,
        match_ids: list[str],
    ) -> dict[str, models.MatchHistory]:
        collection_name = "match_history"

        documents = await self.firestore.batch_get(
            collection=collection_name,
            document_ids=match_ids,
        )

        return {
            doc["metadata"]["matchId"]: models.MatchHistory(**doc)
            for doc in documents
            if doc is not None
        }

    async def set_match_history(
        self,
        match_histories: list[models.MatchHistory],
    ) -> None:
        collection_name = "match_history"

        batch_data = {
            match_history.metadata.matchId: match_history.model_dump(mode='json')
            for match_history in match_histories
        }

        await self.firestore.batch_set(
            collection=collection_name,
            documents=batch_data,
        )
