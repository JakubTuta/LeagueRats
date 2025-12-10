import typing

import utils

from . import models, repository


class ChampionService:
    def __init__(
        self,
        firestore: utils.FirestoreClient,
        redis: utils.RedisClient,
    ):
        self.firestore = firestore
        self.redis = redis

        self.cache_repo = repository.ChampionsCache()
        self.redis_repo = repository.ChampionsRedis(redis)
        self.firestore_repo = repository.ChampionsFirestore(firestore)

    async def get_champions_names(self) -> dict[int, models.ChampionName]:
        cache_champions = self.cache_repo.get_all_champions_names()

        if cache_champions:
            return cache_champions

        redis_champions = await self.redis_repo.get_all_champions_names()

        if redis_champions:
            self.cache_repo.set_all_champions_names(redis_champions)
            return redis_champions

        firestore_champions = await self.firestore_repo.get_all_champions_names()

        if firestore_champions:
            await self.redis_repo.set_all_champions_names(firestore_champions)
            self.cache_repo.set_all_champions_names(firestore_champions)
            return firestore_champions

        return {}

    async def get_champion_stats(
        self, champion_id: int
    ) -> typing.Optional[models.ChampionStats]:
        cache_champion_stats = self.cache_repo.get_champion_stats(champion_id)

        if cache_champion_stats is not None:
            return cache_champion_stats

        redis_champion_stats = await self.redis_repo.get_champion_stats(champion_id)

        if redis_champion_stats is not None:
            self.cache_repo.set_champion_stats(champion_id, redis_champion_stats)
            return redis_champion_stats

        firestore_champion_stats = await self.firestore_repo.get_champion_stats(champion_id)

        if firestore_champion_stats is not None:
            await self.redis_repo.set_champion_stats(champion_id, firestore_champion_stats)
            self.cache_repo.set_champion_stats(champion_id, firestore_champion_stats)
            return firestore_champion_stats

        return None

    async def get_champion_matches(
        self,
        champion_id: int,
        start_after: str | None = None,
        limit: int = 10,
        lane: str | None = None,
        versus: str | None = None,
    ) -> list[models.ChampionHistory]:
        cache_champion_matches = self.cache_repo.get_champion_matches(
            champion_id=champion_id,
            limit=limit,
            lane=lane,
            versus=versus,
        )

        if cache_champion_matches:
            return cache_champion_matches

        redis_champion_matches = await self.redis_repo.get_champion_matches(
            champion_id=champion_id,
            limit=limit,
            lane=lane,
            versus=versus,
        )

        if redis_champion_matches:
            self.cache_repo.set_champion_matches(
                champion_id=champion_id,
                champion_matches=redis_champion_matches,
                limit=limit,
                lane=lane,
                versus=versus,
            )
            return redis_champion_matches

        firestore_champion_matches = await self.firestore_repo.get_champion_matches(
            champion_id=champion_id,
            start_after=start_after,
            limit=limit,
            lane=lane,
            versus=versus,
        )

        if firestore_champion_matches:
            await self.redis_repo.set_champion_matches(
                champion_id=champion_id,
                champion_matches=firestore_champion_matches,
                limit=limit,
                lane=lane,
                versus=versus,
            )
            self.cache_repo.set_champion_matches(
                champion_id=champion_id,
                champion_matches=firestore_champion_matches,
                limit=limit,
                lane=lane,
                versus=versus,
            )
            return firestore_champion_matches

        return []

    async def get_champion_positions(
        self,
        http: utils.HTTPClient,
        champion_ids: list[int],
    ) -> dict[str, str]:
        cache_champion_positions = self.cache_repo.get_champion_positions()

        if cache_champion_positions:
            return {
                str(champion_id): cache_champion_positions.get(str(champion_id), "TOP")
                for champion_id in champion_ids
            }

        redis_champion_positions = await self.redis_repo.get_champion_positions()

        if redis_champion_positions:
            self.cache_repo.set_champions_positions(redis_champion_positions)
            return {
                str(champion_id): redis_champion_positions.get(str(champion_id), "TOP")
                for champion_id in champion_ids
            }

        request_url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

        try:
            response = await http.get(request_url)
            champion_data = response.json().get("data", None)
        except Exception:
            return {}

        if champion_data is None:
            return {}

        champion_positions = {
            str(champion_id): self._find_highest_playrate_role(
                champion_data, str(champion_id)
            )
            for champion_id in champion_ids
        }

        if champion_positions:
            await self.redis_repo.set_champions_positions(champion_positions)
            self.cache_repo.set_champions_positions(champion_positions)
            return champion_positions

        return {}

    async def get_champions_mastery(
        self,
        puuid: str,
        region: str,
        riot_api_client: utils.RiotAPIClient,
    ) -> list[models.ChampionMastery]:
        cache_champions_mastery = self.cache_repo.get_champions_mastery(puuid)

        if cache_champions_mastery:
            return cache_champions_mastery

        redis_champions_mastery = await self.redis_repo.get_champions_mastery(puuid)

        if redis_champions_mastery:
            self.cache_repo.set_champions_mastery(puuid, redis_champions_mastery)
            return redis_champions_mastery

        mapped_region = self._map_region(region)

        if mapped_region is None:
            return []

        response = await riot_api_client.get(
            mapped_region,
            f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}",
        )

        if response:
            champions_mastery = [
                models.ChampionMastery(**item)  # pyright: ignore[reportCallIssue]
                for item in response
            ]

            if champions_mastery:
                await self.redis_repo.set_champions_mastery(puuid, champions_mastery)
                self.cache_repo.set_champions_mastery(puuid, champions_mastery)
                return champions_mastery

        return []

    def _find_highest_playrate_role(self, champion_data: dict, champion_id: str) -> str:
        roles = champion_data.get(champion_id, None)

        if not roles:
            return "TOP"

        return max(roles.items(), key=lambda x: x[1].get("playRate", 0))[0]

    def _map_region(self, region: str) -> typing.Optional[str]:
        region_mapping = {
            "euw": "euw1",
            "eune": "eun1",
            "na": "na1",
            "kr": "kr",
            "br": "br1",
            "jp": "jp1",
            "lan": "la1",
            "las": "la2",
            "oce": "oc1",
            "ph": "ph2",
            "ru": "ru",
            "sg": "sg2",
            "th": "th2",
            "tr": "tr1",
            "tw": "tw2",
            "vn": "vn2",
            "me": "me1",
        }

        return region_mapping.get(region.lower(), None)
