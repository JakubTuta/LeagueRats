import asyncio
import typing

import database.database as database
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx
from google.cloud.firestore_v1.base_query import FieldFilter

from . import models


async def get_account(
    client: httpx.AsyncClient,
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    summoner_id: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
    save_account: bool = False,
) -> typing.Optional[models.Account]:
    if account := get_account_from_database(
        region=region,
        username=username,
        tag=tag,
        summoner_id=summoner_id,
        puuid=puuid,
    ):
        return account

    if region is None:
        return None

    if account := await get_account_from_api(
        client,
        region,
        username=username,
        tag=tag,
        puuid=puuid,
        save_account=save_account,
    ):
        return account

    return None


def get_account_from_database(
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    summoner_id: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> typing.Optional[models.Account]:
    collection = database.get_collection("accounts")

    if collection is None:
        return None

    if puuid is not None:
        account_doc = collection.document(puuid).get()

    elif summoner_id is not None:
        docs = collection.where(
            filter=FieldFilter("summoner_id", "==", summoner_id)
        ).get()

        account_doc = docs[0] if len(docs) else None

    elif username is not None and tag is not None and region is not None:
        docs = (
            collection.where(filter=FieldFilter("username", "==", username))
            .where(filter=FieldFilter("tag", "==", tag))
            .where(filter=FieldFilter("region", "==", region))
            .get()
        )

        account_doc = docs[0] if len(docs) else None

    else:
        return None

    if (
        account_doc is None
        or not account_doc.exists
        or (account_data := account_doc.to_dict()) is None
    ):
        return None

    model_data = {
        "gameName": account_data.get("gameName", ""),
        "tagLine": account_data.get("tagLine", ""),
        "puuid": account_data.get("puuid", ""),
        "region": account_data.get("region", ""),
        "accountId": account_data.get("accountId", ""),
        "id": account_data.get("id", ""),
        "profileIconId": account_data.get("profileIconId", ""),
        "summonerLevel": account_data.get("summonerLevel", ""),
    }
    model = models.Account(**model_data)

    return model


async def _get_account_details(
    client: httpx.AsyncClient,
    region: str,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> typing.Optional[typing.Dict[str, str]]:
    if region is None or (row_regions := regions.get_region(region)) is None:
        return None

    request_region = row_regions[2].lower()
    request_url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts"

    if puuid is not None:
        request_url += f"/by-puuid/{puuid}"

    elif username is not None and tag is not None:
        request_url += f"/by-riot-id/{username}/{tag}"

    else:
        return None

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return response.json()

    except:
        pass


async def _get_summoner_details(
    client: httpx.AsyncClient,
    region: str,
    puuid: str,
) -> typing.Optional[typing.Dict[str, str]]:
    if (row_regions := regions.get_region(region)) is None:
        return None

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return response.json()

    except:
        pass


async def get_account_from_api(
    client: httpx.AsyncClient,
    region: typing.Optional[str],
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
    save_account: bool = False,
) -> typing.Optional[models.Account]:
    if region is None:
        return None

    if (
        account_details := await _get_account_details(
            client, region, username=username, tag=tag, puuid=puuid
        )
    ) is None:
        return None

    if (
        summoner_details := await _get_summoner_details(
            client, region, account_details.get("puuid", "")
        )
    ) is None:
        return None

    model_data = {
        "gameName": account_details.get("gameName"),
        "tagLine": account_details.get("tagLine"),
        "puuid": account_details.get("puuid"),
        "region": region,
        "accountId": summoner_details.get("accountId"),
        "id": summoner_details.get("id"),
        "profileIconId": summoner_details.get("profileIconId"),
        "summonerLevel": summoner_details.get("summonerLevel"),
    }

    model = models.Account(**model_data)

    if save_account:
        db_functions.add_or_update_document("accounts", model.model_dump())

    return model


async def get_accounts_in_all_regions(
    client: httpx.AsyncClient,
    username: str,
    tag: str,
) -> typing.Dict[str, typing.Optional[models.Account]]:
    request_regions = regions.get_region_column(0)

    tasks = [
        get_account(client, region, username=username, tag=tag, save_account=True)
        for region in request_regions
    ]

    results = await asyncio.gather(*tasks)

    found_accounts = {}
    for result in results:
        if result is not None:
            found_accounts[result.region] = result

    for region in request_regions:
        if region not in found_accounts:
            found_accounts[region] = None

    return found_accounts


async def create_account(
    client: httpx.AsyncClient,
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> typing.Optional[models.Account]:
    if account := get_account_from_database(
        region=region, username=username, tag=tag, puuid=puuid
    ):
        return account

    if account := await get_account_from_api(
        client, region, username=username, tag=tag, puuid=puuid, save_account=True
    ):
        return account

    return None
