import asyncio
import typing

import utils

from . import models, repository

REGIONS = [
    "euw",
    "eune",
    "na",
    "kr",
    "br",
    "jp",
    "lan",
    "las",
    "oce",
    "ph",
    "ru",
    "sg",
    "th",
    "tr",
    "tw",
    "vn",
    "me",
]

REGION_MAPPING = {
    "euw": "europe",
    "euw1": "europe",
    "eune": "europe",
    "eun1": "europe",
    "na": "americas",
    "na1": "americas",
    "kr": "asia",
    "br": "americas",
    "br1": "americas",
    "jp": "asia",
    "jp1": "asia",
    "lan": "americas",
    "la1": "americas",
    "las": "americas",
    "la2": "americas",
    "oce": "asia",
    "oc1": "asia",
    "ph": "asia",
    "ph2": "asia",
    "ru": "europe",
    "sg": "asia",
    "sg2": "asia",
    "th": "asia",
    "th2": "asia",
    "tr": "europe",
    "tr1": "europe",
    "tw": "asia",
    "tw2": "asia",
    "vn": "asia",
    "vn2": "asia",
    "me": "europe",
    "me1": "europe",
}


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
            self.cache_repo.set_account(account)
            return account

        if account := await self.firestore_repo.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=region,
        ):
            await self.redis_repo.set_account(account)
            self.cache_repo.set_account(account)
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
            await self.firestore_repo.set_account(account)
            await self.redis_repo.set_account(account)
            self.cache_repo.set_account(account)
            return account

        return None

    async def get_accounts_in_all_regions(
        self,
        username: str,
        tag: str,
    ) -> dict[str, typing.Optional[models.Account]]:
        tasks = [
            self.get_account(puuid=None, username=username, tag=tag, region=region)
            for region in REGIONS
        ]

        accounts = await asyncio.gather(*tasks)
        accounts_in_all_regions = dict(zip(REGIONS, accounts))

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
        return REGION_MAPPING.get(region.lower())
