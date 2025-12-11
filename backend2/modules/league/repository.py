import typing

import utils

from . import models

CACHE_SETTINGS = {
    "league_entries": {
        "cache_name": "league_entries",
        "ttl": 1800,  # 30 minutes
        "cache_prefix": "league_entries",
    },
    "leaderboard": {
        "cache_name": "leaderboard",
        "ttl": 86400,  # 24 hours
        "cache_prefix": "leaderboard",
    },
}


class LeagueCache:
    def __init__(self):
        self.league_entries_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["league_entries"]["cache_name"],
            ttl=CACHE_SETTINGS["league_entries"]["ttl"],
        )
        self.leaderboard_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["leaderboard"]["cache_name"],
            ttl=CACHE_SETTINGS["leaderboard"]["ttl"],
        )

    def get_league_entries(
        self,
        puuid: str,
    ) -> list[models.LeagueEntry]:
        cache_key = f"{CACHE_SETTINGS['league_entries']['cache_prefix']}:{puuid}"
        cached_data = self.league_entries_cache.get(cache_key)

        if cached_data is not None:
            return [models.LeagueEntry(**entry) for entry in cached_data]

        return []

    def set_league_entries(
        self,
        puuid: str,
        league_entries: list[models.LeagueEntry],
    ) -> None:
        cache_key = f"{CACHE_SETTINGS['league_entries']['cache_prefix']}:{puuid}"
        entries_data = [entry.model_dump() for entry in league_entries]
        self.league_entries_cache.set(cache_key, entries_data)

    def get_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
    ) -> list[models.LeaderboardEntry]:
        cache_key = f"{CACHE_SETTINGS['leaderboard']['cache_prefix']}:leaderboard:{region}:{limit}:{page}"
        cached_data = self.leaderboard_cache.get(cache_key)

        if cached_data is not None:
            return [models.LeaderboardEntry(**entry) for entry in cached_data]

        return []

    def set_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
        leaderboard: list[models.LeaderboardEntry],
    ) -> None:
        cache_key = f"{CACHE_SETTINGS['leaderboard']['cache_prefix']}:leaderboard:{region}:{limit}:{page}"
        leaderboard_data = [entry.model_dump() for entry in leaderboard]
        self.leaderboard_cache.set(cache_key, leaderboard_data)


class LeagueRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.redis_client = redis_client

    async def get_league_entries(
        self,
        puuid: str,
    ) -> list[models.LeagueEntry]:
        redis_key = f"{CACHE_SETTINGS['league_entries']['cache_prefix']}:{puuid}"
        cached_data = await self.redis_client.get_json(redis_key)

        if cached_data is not None:
            return [models.LeagueEntry(**entry) for entry in cached_data]

        return []

    async def set_league_entries(
        self,
        puuid: str,
        league_entries: list[models.LeagueEntry],
    ) -> None:
        redis_key = f"{CACHE_SETTINGS['league_entries']['cache_prefix']}:{puuid}"
        entries_data = [entry.model_dump() for entry in league_entries]
        await self.redis_client.set_json(
            redis_key, entries_data, ex=CACHE_SETTINGS["league_entries"]["ttl"]
        )

    async def get_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
    ) -> list[models.LeaderboardEntry]:
        redis_key = f"{CACHE_SETTINGS['leaderboard']['cache_prefix']}:leaderboard:{region}:{limit}:{page}"
        cached_data = await self.redis_client.get_json(redis_key)

        if cached_data is not None:
            return [models.LeaderboardEntry(**entry) for entry in cached_data]

        return []

    async def set_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
        leaderboard: list[models.LeaderboardEntry],
    ) -> None:
        redis_key = f"{CACHE_SETTINGS['leaderboard']['cache_prefix']}:leaderboard:{region}:{limit}:{page}"
        leaderboard_data = [entry.model_dump() for entry in leaderboard]
        await self.redis_client.set_json(
            redis_key, leaderboard_data, ex=CACHE_SETTINGS["leaderboard"]["ttl"]
        )


class LeagueFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore_client = firestore_client

    async def get_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
    ) -> list[models.LeaderboardEntry]:
        collection_path = f"leaderboard/{region}/CHALLENGER"

        response = await self.firestore_client.query_collection(
            collection=collection_path,
            order_by="rank",
            order_direction="ASCENDING",
            limit=limit,
            offset=(page - 1) * limit,
        )

        return [models.LeaderboardEntry(**doc) for doc in response]
