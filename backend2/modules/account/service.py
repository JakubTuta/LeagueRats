import asyncio
import typing

import constants
import utils

from . import models, repository


class AccountService:
    def __init__(
        self,
        firestore: utils.FirestoreClient,
        redis: utils.RedisClient,
        riot_api: utils.RiotAPIClient,
    ):
        self.firestore = firestore
        self.redis = redis
        self.riot_api = riot_api

        self.cache_repo = repository.AccountCache()
        self.redis_repo = repository.AccountRedis(redis)
        self.firestore_repo = repository.AccountFirestore(firestore)

    async def get_account(
        self,
        puuid: typing.Optional[str],
        username: typing.Optional[str],
        tag: typing.Optional[str],
        region: typing.Optional[str],
    ) -> typing.Optional[models.Account]:
        normalized_region = region.upper() if region else None

        if account := self.cache_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=normalized_region,
        ):
            return account

        if account := await self.redis_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=normalized_region,
        ):
            self.cache_repo.set_account(account=account)
            return account

        if account := await self.firestore_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=normalized_region,
        ):
            await self.redis_repo.set_account(account=account)
            self.cache_repo.set_account(account=account)
            return account

        if (
            response := await self._fetch_account_from_api(
                puuid=puuid,
                region=normalized_region,
                username=username,
                tag=tag,
            )
        ) is not None:
            await self.firestore_repo.set_account(account=response)
            await self.redis_repo.set_account(account=response)
            self.cache_repo.set_account(account=response)
            return response

        return None

    async def get_accounts_in_all_regions(
        self,
        username: str,
        tag: str,
    ) -> dict[str, typing.Optional[models.Account]]:
        tasks = [
            self.get_account(puuid=None, username=username, tag=tag, region=region)
            for region in constants.REGIONS
        ]

        accounts = await asyncio.gather(*tasks)
        accounts_in_all_regions = dict(zip(constants.REGIONS, accounts))

        return accounts_in_all_regions

    async def _fetch_account_from_api(
        self,
        puuid: typing.Optional[str],
        region: typing.Optional[str],
        username: typing.Optional[str],
        tag: typing.Optional[str],
    ) -> typing.Optional[models.Account]:
        if region is None:
            return None

        continent_region = self._map_region_to_continent(region)
        platform_region = self._map_region_to_platform(region)

        if continent_region is None or platform_region is None:
            return None

        if platform_region not in self.riot_api.BASE_URLS:
            return None

        account_url = "/riot/account/v1/accounts"

        if puuid is not None:
            account_url += f"/by-puuid/{puuid}"
        elif username is not None and tag is not None:
            account_url += f"/by-riot-id/{username}/{tag}"
        else:
            return None

        try:
            account_response = await self.riot_api.get(continent_region, account_url)
            if account_response is None or not isinstance(account_response, dict):
                return None

            fetched_puuid = account_response.get("puuid")
            if not fetched_puuid:
                return None
        except Exception:
            return None

        try:
            summoner_url = f"/lol/summoner/v4/summoners/by-puuid/{fetched_puuid}"
            summoner_response = await self.riot_api.get(platform_region, summoner_url)

            if summoner_response is None:
                return None
        except Exception:
            return None

        account = models.Account(
            **account_response, region=region  # pyright: ignore[reportCallIssue]
        )
        return account

    def _map_region_to_continent(self, region: str) -> typing.Optional[str]:
        return constants.REGION_TO_CONTINENT.get(region)

    def _map_region_to_platform(self, region: str) -> typing.Optional[str]:
        return constants.REGION_TO_PLATFORM.get(region.lower())
