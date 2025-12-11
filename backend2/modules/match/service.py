import asyncio
import typing

import constants as shared_constants
import utils

from . import models, repository


class MatchService:
    def __init__(
        self,
        redis_client: utils.RedisClient,
        firestore_client: utils.FirestoreClient,
        riot_api: utils.RiotAPIClient,
    ):
        self.redis = redis_client
        self.firestore = firestore_client
        self.riot_api = riot_api

        self.cache_repo = repository.MatchCache()
        self.redis_repo = repository.MatchRedis(redis_client)
        self.firestore_repo = repository.MatchFirestore(firestore_client)

    async def get_active_match(
        self,
        puuid: str,
        region: str,
    ) -> models.ActiveMatch | None:
        cached_active_match = self.cache_repo.get_active_match(puuid=puuid)

        if cached_active_match:
            return cached_active_match

        redis_active_match = await self.redis_repo.get_active_match(puuid=puuid)

        if redis_active_match:
            self.cache_repo.set_active_match(
                puuid=puuid, active_match=redis_active_match
            )
            return redis_active_match

        active_match = await self._fetch_active_match(puuid=puuid, region=region)

        if active_match:
            await self.redis_repo.set_active_match(
                puuid=puuid, active_match=active_match
            )
            self.cache_repo.set_active_match(puuid=puuid, active_match=active_match)
            return active_match

    async def get_match_history(
        self,
        puuid: str,
        start: int,
        count: int,
        region: str,
        startTime: typing.Optional[str] = None,
        endTime: typing.Optional[str] = None,
        queue: typing.Optional[str] = None,
        type: typing.Optional[str] = None,
    ) -> list[models.MatchHistory]:
        """
        Fetch match history with multi-layer caching strategy:
        L1 (In-memory) → L2 (Redis) → L3 (Firestore) → L4 (Riot API)
        """
        match_ids = await self._fetch_match_history_ids(
            puuid=puuid,
            region=region,
            start=start,
            count=count,
            startTime=startTime,
            endTime=endTime,
            queue=queue,
            type=type,
        )

        if not match_ids:
            return []

        fetched_matches: dict[str, models.MatchHistory] = {}
        missing_matches = match_ids

        cached_match_histories = self.cache_repo.get_match_history(match_ids=match_ids)
        fetched_matches.update(cached_match_histories)
        missing_matches = [
            match_id for match_id in missing_matches if match_id not in fetched_matches
        ]

        if not missing_matches:
            return [fetched_matches[match_id] for match_id in match_ids]

        redis_match_histories = await self.redis_repo.get_match_history(
            match_ids=missing_matches
        )
        fetched_matches.update(redis_match_histories)
        missing_matches = [
            match_id for match_id in missing_matches if match_id not in fetched_matches
        ]

        if not missing_matches:
            self.cache_repo.set_match_history(
                match_histories=list(redis_match_histories.values())
            )
            return [fetched_matches[match_id] for match_id in match_ids]

        firestore_match_histories = await self.firestore_repo.get_match_history(
            match_ids=missing_matches
        )
        fetched_matches.update(firestore_match_histories)
        missing_matches = [
            match_id for match_id in missing_matches if match_id not in fetched_matches
        ]

        if not missing_matches:
            await self.redis_repo.set_match_history(
                match_histories=list(firestore_match_histories.values())
            )
            self.cache_repo.set_match_history(
                match_histories=list(firestore_match_histories.values())
            )
            return [fetched_matches[match_id] for match_id in match_ids]

        fetched_match_histories = await self._fetch_match_data_batch(
            match_ids=missing_matches,
            region=region,
        )
        fetched_matches.update(fetched_match_histories)
        if fetched_match_histories:
            await self.redis_repo.set_match_history(
                match_histories=list(fetched_match_histories.values())
            )
            self.cache_repo.set_match_history(
                match_histories=list(fetched_match_histories.values())
            )
            await self.firestore_repo.set_match_history(
                match_histories=list(fetched_match_histories.values())
            )

        return [
            fetched_matches[match_id]
            for match_id in match_ids
            if match_id in fetched_matches
        ]

    async def _fetch_active_match(
        self,
        puuid: str,
        region: str,
    ) -> models.ActiveMatch | None:
        if (
            mapped_region := shared_constants.REGION_TO_PLATFORM.get(region.lower())
        ) is None:
            return None

        active_game_data = await self.riot_api.get(
            region=mapped_region,
            endpoint=f"/lol/spectator/v5/active-games/by-summoner/{puuid}",
        )

        if not active_game_data:
            return None

        active_match = models.ActiveMatch(
            **active_game_data  # pyright: ignore[reportCallIssue]
        )

        return active_match

    async def _fetch_match_history_ids(
        self,
        puuid: str,
        region: str,
        start: int,
        count: int,
        startTime: typing.Optional[str] = None,
        endTime: typing.Optional[str] = None,
        queue: typing.Optional[str] = None,
        type: typing.Optional[str] = None,
    ) -> list[str]:
        if (
            mapped_region := shared_constants.REGION_TO_CONTINENT.get(region.lower())
        ) is None:
            return []

        params = {
            "start": start,
            "count": count,
            "startTime": startTime,
            "endTime": endTime,
            "queue": queue,
            "type": type,
        }
        params = {k: v for k, v in params.items() if v is not None}

        match_ids_data = await self.riot_api.get(
            region=mapped_region,
            endpoint=f"/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params=params,
        )

        if not match_ids_data:
            return []

        return match_ids_data  # pyright: ignore[reportReturnType]

    async def _fetch_match_data_batch(
        self,
        match_ids: list[str],
        region: str,
    ) -> dict[str, models.MatchHistory]:
        fetched_matches = {}

        fetch_tasks = [
            self._fetch_match_data(match_id=match_id, region=region)
            for match_id in match_ids
        ]
        results = await asyncio.gather(*fetch_tasks)

        for match_id, match_history in zip(match_ids, results):
            if match_history:
                fetched_matches[match_id] = match_history

        return fetched_matches

    async def _fetch_match_data(
        self,
        match_id: str,
        region: str,
    ) -> models.MatchHistory | None:
        if (
            mapped_region := shared_constants.REGION_TO_CONTINENT.get(region.lower())
        ) is None:
            return None

        match_data = await self.riot_api.get(
            region=mapped_region,
            endpoint=f"/lol/match/v5/matches/{match_id}",
        )

        if not match_data:
            return None

        match_history = models.MatchHistory(
            **match_data  # pyright: ignore[reportCallIssue]
        )

        return match_history
