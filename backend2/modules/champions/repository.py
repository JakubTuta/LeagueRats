import typing

import utils

from . import models

CACHE_SETTINGS = {
    "champion_names": {
        "cache_name": "champion_names",
        "ttl": 86400,  # 24 hours
        "cache_prefix": "champion_names",
    },
    "champion_stats": {
        "cache_name": "champion_stats",
        "ttl": 3600,  # 1 hour
        "cache_prefix": "champion_stats",
    },
    "champion_matches": {
        "cache_name": "champion_matches",
        "ttl": 1800,  # 30 minutes
        "cache_prefix": "champion_matches",
    },
    "champion_positions": {
        "cache_name": "champion_positions",
        "ttl": 86400,  # 24 hours
        "cache_prefix": "champion_positions",
    },
    "champion_mastery": {
        "cache_name": "champion_mastery",
        "ttl": 86400,  # 24 hours
        "cache_prefix": "champion_mastery",
    },
}


class ChampionsCache:
    def __init__(self):
        self.cache_champions_names = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["champion_names"]["cache_name"],
            ttl=CACHE_SETTINGS["champion_names"]["ttl"],
        )

        self.cache_champions_stats = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["champion_stats"]["cache_name"],
            ttl=CACHE_SETTINGS["champion_stats"]["ttl"],
        )

        self.cache_champions_matches = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["champion_matches"]["cache_name"],
            ttl=CACHE_SETTINGS["champion_matches"]["ttl"],
        )

        self.cache_champions_positions = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["champion_positions"]["cache_name"],
            ttl=CACHE_SETTINGS["champion_positions"]["ttl"],
        )

        self.cache_champion_mastery = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["champion_mastery"]["cache_name"],
            ttl=CACHE_SETTINGS["champion_mastery"]["ttl"],
        )

    def get_all_champions_names(self) -> dict[int, models.ChampionName]:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        cached_data = self.cache_champions_names.get(f"{cache_prefix}:all")

        if cached_data is not None:
            return cached_data

        return {}

    def get_champion_name(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionName]:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        cached_data = self.cache_champions_names.get(f"{cache_prefix}:{champion_id}")

        if cached_data is not None:
            return cached_data

        return None

    def set_all_champions_names(
        self, champions: dict[int, models.ChampionName]
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        self.cache_champions_names.set(f"{cache_prefix}:all", champions)

        for champion_id, champion in champions.items():
            self.set_champion_name(champion_id, champion)

    def set_champion_name(
        self, champion_id: int, champion: models.ChampionName
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        self.cache_champions_names.set(f"{cache_prefix}:{champion_id}", champion)

    def get_champion_stats(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionStats]:
        cache_prefix = (
            f"{CACHE_SETTINGS['champion_stats']['cache_prefix']}:{champion_id}"
        )
        cached_data = self.cache_champions_stats.get(cache_prefix)

        if cached_data is not None:
            return cached_data

        return None

    def set_champion_stats(
        self, champion_id: int, champion_stats: models.ChampionStats
    ) -> None:
        cache_prefix = (
            f"{CACHE_SETTINGS['champion_stats']['cache_prefix']}:{champion_id}"
        )
        self.cache_champions_stats.set(cache_prefix, champion_stats)

    def get_champion_matches(
        self,
        champion_id: int,
        limit: int,
        lane: typing.Optional[str] = None,
        versus: typing.Optional[str] = None,
    ) -> list[models.ChampionHistory]:
        cache_prefix = f"{CACHE_SETTINGS['champion_matches']['cache_prefix']}:{champion_id}:{limit}"

        if lane:
            cache_prefix += f":{lane}"

        if versus:
            cache_prefix += f":{versus}"

        cached_data = self.cache_champions_matches.get(cache_prefix)

        if cached_data is not None:
            return cached_data

        return []

    def set_champion_matches(
        self,
        champion_id: int,
        champion_matches: list[models.ChampionHistory],
        limit: int,
        lane: typing.Optional[str] = None,
        versus: typing.Optional[str] = None,
    ) -> None:
        cache_prefix = f"{CACHE_SETTINGS['champion_matches']['cache_prefix']}:{champion_id}:{limit}"

        if lane:
            cache_prefix += f":{lane}"

        if versus:
            cache_prefix += f":{versus}"

        self.cache_champions_matches.set(cache_prefix, champion_matches)

    def get_champion_positions(self) -> dict[str, str]:
        cache_prefix = CACHE_SETTINGS["champion_positions"]["cache_prefix"]
        data = self.cache_champions_positions.get(f"{cache_prefix}:all")

        return data or {}

    def set_champions_positions(
        self,
        champion_data: dict[str, str],
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_positions"]["cache_prefix"]

        self.cache_champions_positions.set(f"{cache_prefix}:all", champion_data)

    def get_champions_mastery(self, puuid: str) -> list[models.ChampionMastery]:
        cache_prefix = f"{CACHE_SETTINGS['champion_mastery']['cache_prefix']}:{puuid}"
        cached_data = self.cache_champion_mastery.get(cache_prefix)

        if cached_data is not None:
            return cached_data

        return []

    def set_champions_mastery(
        self, puuid: str, champion_mastery: list[models.ChampionMastery]
    ) -> None:
        cache_prefix = f"{CACHE_SETTINGS['champion_mastery']['cache_prefix']}:{puuid}"
        self.cache_champion_mastery.set(cache_prefix, champion_mastery)


class ChampionsRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.redis_client = redis_client

    async def get_all_champions_names(self) -> dict[int, models.ChampionName]:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        cached_data = await self.redis_client.get_json(f"{cache_prefix}:all")

        if cached_data is not None:
            return cached_data

        return {}

    async def get_champion_name(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionName]:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        cached_data = await self.redis_client.get_json(f"{cache_prefix}:{champion_id}")

        if cached_data is not None:
            return cached_data

        return None

    async def set_champion_name(
        self, champion_id: int, champion: models.ChampionName
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        await self.redis_client.set_json(
            f"{cache_prefix}:{champion_id}",
            champion.model_dump(mode="json"),
            ex=CACHE_SETTINGS["champion_names"]["ttl"],
        )

    async def set_all_champions_names(
        self, champions: dict[int, models.ChampionName]
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_names"]["cache_prefix"]
        serialized_champions = {
            str(champion_id): champion.model_dump(mode="json")
            for champion_id, champion in champions.items()
        }
        await self.redis_client.set_json(
            f"{cache_prefix}:all",
            serialized_champions,
            ex=CACHE_SETTINGS["champion_names"]["ttl"],
        )

    async def get_champion_stats(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionStats]:
        cache_prefix = (
            f"{CACHE_SETTINGS['champion_stats']['cache_prefix']}:{champion_id}"
        )
        cached_data = await self.redis_client.get_json(cache_prefix)

        if cached_data is not None:
            return cached_data

        return None

    async def set_champion_stats(
        self, champion_id: int, champion_stats: models.ChampionStats
    ) -> None:
        cache_prefix = (
            f"{CACHE_SETTINGS['champion_stats']['cache_prefix']}:{champion_id}"
        )
        await self.redis_client.set_json(
            cache_prefix,
            champion_stats.model_dump(mode="json"),
            ex=CACHE_SETTINGS["champion_stats"]["ttl"],
        )

    async def get_champion_matches(
        self,
        champion_id: int,
        limit: int,
        lane: typing.Optional[str] = None,
        versus: typing.Optional[str] = None,
    ) -> list[models.ChampionHistory]:
        cache_prefix = f"{CACHE_SETTINGS['champion_matches']['cache_prefix']}:{champion_id}:{limit}"

        if lane:
            cache_prefix += f":{lane}"

        if versus:
            cache_prefix += f":{versus}"

        cached_data = await self.redis_client.get_json(cache_prefix)

        if cached_data is not None:
            return cached_data

        return []

    async def set_champion_matches(
        self,
        champion_id: int,
        champion_matches: list[models.ChampionHistory],
        limit: int,
        lane: typing.Optional[str] = None,
        versus: typing.Optional[str] = None,
    ) -> None:
        cache_prefix = f"{CACHE_SETTINGS['champion_matches']['cache_prefix']}:{champion_id}:{limit}"

        if lane:
            cache_prefix += f":{lane}"

        if versus:
            cache_prefix += f":{versus}"

        await self.redis_client.set_json(
            cache_prefix,
            [match.model_dump(mode="json") for match in champion_matches],
            ex=CACHE_SETTINGS["champion_matches"]["ttl"],
        )

    async def get_champion_positions(self) -> dict[str, str]:
        cache_prefix = CACHE_SETTINGS["champion_positions"]["cache_prefix"]
        data = await self.redis_client.get_json(f"{cache_prefix}:all")

        return data or {}

    async def set_champions_positions(
        self,
        champion_data: dict[str, str],
    ) -> None:
        cache_prefix = CACHE_SETTINGS["champion_positions"]["cache_prefix"]

        await self.redis_client.set_json(
            f"{cache_prefix}:all",
            champion_data,
            ex=CACHE_SETTINGS["champion_positions"]["ttl"],
        )

    async def get_champions_mastery(
        self,
        puuid: str,
    ) -> list[models.ChampionMastery]:
        cache_prefix = f"{CACHE_SETTINGS['champion_mastery']['cache_prefix']}:{puuid}"
        cached_data = await self.redis_client.get_json(cache_prefix)

        if cached_data is not None:
            return cached_data

        return []

    async def set_champions_mastery(
        self, puuid: str, champion_mastery: list[models.ChampionMastery]
    ) -> None:
        cache_prefix = f"{CACHE_SETTINGS['champion_mastery']['cache_prefix']}:{puuid}"
        await self.redis_client.set_json(
            cache_prefix,
            list(map(lambda x: x.model_dump(mode="json"), champion_mastery)),
            ex=CACHE_SETTINGS["champion_mastery"]["ttl"],
        )


class ChampionsFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore_client = firestore_client

    async def get_all_champions_names(self) -> dict[int, models.ChampionName]:
        collection_name = "help"
        document_name = "champions"

        document = await self.firestore_client.get_document(
            collection_name, document_name
        )

        if document is None:
            return {}

        champions = {
            int(champion_id): models.ChampionName(**data)
            for champion_id, data in document.items()
        }

        return champions

    async def set_all_champions_names(
        self, champions: dict[int, models.ChampionName]
    ) -> None:
        collection_name = "help"
        document_name = "champions"

        data = {
            str(champion_id): champion.model_dump(mode="json")
            for champion_id, champion in champions.items()
        }

        await self.firestore_client.set_document(collection_name, document_name, data)

    async def get_champion_stats(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionStats]:
        collection_name = "champion_history"
        document_name = str(champion_id)

        document = await self.firestore_client.get_document(
            collection_name, document_name
        )

        if document is None:
            return None

        champion_stats = models.ChampionStats(**document)
        return champion_stats

    async def set_champion_stats(
        self, champion_id: int, champion_stats: models.ChampionStats
    ) -> None:
        collection_name = "champion_history"
        document_name = str(champion_id)

        data = champion_stats.model_dump(mode="json")

        await self.firestore_client.set_document(collection_name, document_name, data)

    async def get_champion_matches(
        self,
        champion_id: int,
        start_after: typing.Optional[str] = None,
        limit: int = 10,
        lane: typing.Optional[str] = None,
        versus: typing.Optional[str] = None,
    ) -> list[models.ChampionHistory]:
        collection_name = f"champion_history/{str(champion_id)}/matches"

        documents = await self.firestore_client.query_collection(
            collection_name,
            start_after=start_after,
            limit=limit,
            lane=lane,
            enemy=int(versus) if versus is not None else None,
            order_by="match.info.gameStartTimestamp",
            order_direction="DESCENDING",
        )

        matches = [models.ChampionHistory(**document) for document in documents]

        return matches

    async def get_champion_match(
        self,
        champion_id: int,
        match_id: str,
    ) -> typing.Optional[models.ChampionHistory]:
        collection_name = f"champion_history/{champion_id}/matches"
        document_name = match_id

        document = await self.firestore_client.get_document(
            collection_name, document_name
        )

        if document is None:
            return None

        champion_match = models.ChampionHistory(**document)
        return champion_match

    async def set_champion_matches(
        self,
        champion_id: int,
        champion_matches: list[models.ChampionHistory],
    ) -> None:
        collection_name = f"champion_history/{champion_id}/matches"

        documents = {
            match.match.metadata.matchId: match.model_dump(mode="json")
            for match in champion_matches
        }

        await self.firestore_client.batch_set(collection_name, documents)

    async def set_champion_match(
        self,
        champion_id: int,
        champion_match: models.ChampionHistory,
    ) -> None:
        collection_name = f"champion_history/{champion_id}/matches"
        document_name = champion_match.match.metadata.matchId
        data = champion_match.model_dump(mode="json")
        await self.firestore_client.set_document(collection_name, document_name, data)
