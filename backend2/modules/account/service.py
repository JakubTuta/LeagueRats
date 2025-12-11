import asyncio
import typing

import utils

import constants

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
        if account := self.cache_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
        ):
            return account

        if account := await self.redis_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
        ):
            self.cache_repo.set_account(account=account)
            return account

        if account := await self.firestore_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=region,
        ):
            await self.redis_repo.set_account(account=account)
            self.cache_repo.set_account(account=account)
            return account

        if (
            response := await self._fetch_account_from_api(
                puuid=puuid,
                region=region,
                username=username,
                tag=tag,
            )
        ) is not None:
            account = models.Account(**response)  # pyright: ignore[reportCallIssue]
            await self.firestore_repo.set_account(account=account)
            await self.redis_repo.set_account(account=account)
            self.cache_repo.set_account(account=account)
            return account

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
        if region is None or (mapped_region := self._map_region(region)) is None:
            return None

        request_url = "/riot/account/v1/accounts"

        if puuid is not None:
            request_url += f"/by-puuid/{puuid}"

        elif username is not None and tag is not None:
            request_url += f"/by-riot-id/{username}/{tag}"

        else:
            return None

        if (
            response := await self.riot_api.get(mapped_region, request_url)
        ) is not None:
            account = models.Account(**response)  # pyright: ignore[reportCallIssue]
            return account

    def _map_region(self, region: str) -> typing.Optional[str]:
        return constants.REGION_TO_CONTINENT.get(region.lower())
