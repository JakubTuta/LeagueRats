import constants as shared_constants
import utils

from . import models, repository


class LeagueService:
    def __init__(
        self,
        redis_client: utils.RedisClient,
        firestore_client: utils.FirestoreClient,
    ):
        self.redis = redis_client
        self.firestore = firestore_client

        self.cache_repo = repository.LeagueCache()
        self.redis_repo = repository.LeagueRedis(redis_client)
        self.firestore_repo = repository.LeagueFirestore(firestore_client)

    async def fetch_league_entries(
        self,
        puuid: str,
        region: str,
        riot_api: utils.RiotAPIClient,
    ) -> list[models.LeagueEntry]:
        cached_league_entries = self.cache_repo.get_league_entries(puuid=puuid)

        if cached_league_entries:
            return cached_league_entries

        redis_league_entries = await self.redis_repo.get_league_entries(puuid=puuid)

        if redis_league_entries:
            self.cache_repo.set_league_entries(
                puuid=puuid, league_entries=redis_league_entries
            )
            return redis_league_entries

        league_entries = await self._fetch_league_entries(
            puuid=puuid, region=region, riot_api=riot_api
        )
        if league_entries:
            await self.redis_repo.set_league_entries(
                puuid=puuid, league_entries=league_entries
            )
            self.cache_repo.set_league_entries(
                puuid=puuid, league_entries=league_entries
            )
            return league_entries

        return []

    async def get_leaderboard(
        self,
        region: str,
        limit: int,
        page: int,
    ) -> list[models.LeaderboardEntry]:
        cached_leaderboard = self.cache_repo.get_leaderboard(
            region=region, limit=limit, page=page
        )

        if cached_leaderboard:
            return cached_leaderboard

        redis_leaderboard = await self.redis_repo.get_leaderboard(
            region=region, limit=limit, page=page
        )

        if redis_leaderboard:
            self.cache_repo.set_leaderboard(
                region=region, limit=limit, page=page, leaderboard=redis_leaderboard
            )
            return redis_leaderboard

        firestore_leaderboard = await self.firestore_repo.get_leaderboard(
            region=region, limit=limit, page=page
        )

        if firestore_leaderboard:
            await self.redis_repo.set_leaderboard(
                region=region, limit=limit, page=page, leaderboard=firestore_leaderboard
            )
            self.cache_repo.set_leaderboard(
                region=region, limit=limit, page=page, leaderboard=firestore_leaderboard
            )
            return firestore_leaderboard

        return []

    async def _fetch_league_entries(
        self, puuid: str, region: str, riot_api: utils.RiotAPIClient
    ) -> list[models.LeagueEntry]:
        if (
            mapped_region := shared_constants.REGION_TO_PLATFORM.get(region.lower())
        ) is None:
            return []

        request_url = f"/lol/league/v4/entries/by-puuid/{puuid}"

        if response := await riot_api.get(
            mapped_region,
            request_url,
        ):
            return [
                models.LeagueEntry(**entry)  # pyright: ignore[reportCallIssue]
                for entry in response
            ]

        return []
