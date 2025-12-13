import typing

import utils

from . import models

CACHE_SETTINGS = {
    "cache_name": "account",
    "ttl": 86400,  # 24 hours
    "cache_prefix": "account",
}


class AccountCache:
    def __init__(self):
        self.cache_prefix = CACHE_SETTINGS["cache_prefix"]
        self.cache_account = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["cache_name"],
            ttl=CACHE_SETTINGS["ttl"],
        )

    def get_account(
        self,
        puuid: typing.Optional[str],
        username: typing.Optional[str],
        tag: typing.Optional[str],
        region: typing.Optional[str],
    ) -> typing.Optional[models.Account]:
        if puuid is not None:
            cache_key = f"{self.cache_prefix}:puuid:{puuid}"
        elif username is not None and tag is not None and region is not None:
            cache_key = f"{self.cache_prefix}:username:{username}#{tag}:region={region.upper()}"
        else:
            return None

        cached_data = self.cache_account.get(cache_key)
        if cached_data is not None:
            return models.Account(**cached_data)

        return None

    def set_account(self, account: models.Account) -> None:
        account_data = account.model_dump(mode='json')

        cache_key_puuid = f"{self.cache_prefix}:puuid:{account.puuid}"
        self.cache_account.set(cache_key_puuid, account_data)

        cache_key_username = f"{self.cache_prefix}:username:{account.gameName}#{account.tagLine}:region={account.region.upper()}"
        self.cache_account.set(cache_key_username, account_data)


class AccountRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.cache_prefix = CACHE_SETTINGS["cache_prefix"]
        self.redis_client = redis_client

    async def get_account(
        self,
        puuid: typing.Optional[str],
        username: typing.Optional[str],
        tag: typing.Optional[str],
        region: typing.Optional[str],
    ) -> typing.Optional[models.Account]:
        if puuid is not None:
            redis_key = f"{self.cache_prefix}:puuid:{puuid}"
        elif username is not None and tag is not None and region is not None:
            redis_key = f"{self.cache_prefix}:username:{username}#{tag}:region={region.upper()}"
        else:
            return None

        cached_data = await self.redis_client.get_json(redis_key)
        if cached_data is not None:
            return models.Account(**cached_data)

        return None

    async def set_account(self, account: models.Account) -> None:
        account_data = account.model_dump(mode='json')
        ttl = CACHE_SETTINGS["ttl"]

        redis_key_puuid = f"{self.cache_prefix}:puuid:{account.puuid}"
        await self.redis_client.set_json(redis_key_puuid, account_data, ex=ttl)

        redis_key_username = f"{self.cache_prefix}:username:{account.gameName}#{account.tagLine}:region={account.region.upper()}"
        await self.redis_client.set_json(redis_key_username, account_data, ex=ttl)


class AccountFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore_client = firestore_client

    async def get_account(
        self,
        puuid: typing.Optional[str],
        username: typing.Optional[str],
        tag: typing.Optional[str],
        region: typing.Optional[str],
    ) -> typing.Optional[models.Account]:
        account_data = None

        if puuid is not None:
            account_data = await self.firestore_client.get_document(
                collection="accounts", document_id=puuid
            )

        elif username is not None and tag is not None and region is not None:
            query_filters = [
                ("gameName", "==", username),
                ("tagLine", "==", tag),
                ("region", "==", region.upper()),
            ]
            account_data_list = await self.firestore_client.query_collection(
                collection="accounts", filters=query_filters
            )
            account_data = account_data_list[0] if account_data_list else None

        else:
            return None

        if account_data is not None:
            return models.Account(**account_data)

        return None

    async def set_account(self, account: models.Account) -> None:
        await self.firestore_client.set_document(
            collection="accounts",
            document_id=account.puuid,
            data={**account.model_dump(mode='json'), "region": account.region.upper()},
        )
