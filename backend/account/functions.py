import typing

import database.database as database
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx

from . import models


def get_account_from_database(
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    summoner_id: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> typing.Optional[models.Account]:
    collection = database.get_collection("accounts")

    if puuid is not None:
        account_doc = collection.document(puuid).get()

    elif summoner_id is not None:
        account_doc = collection.where("summoner_id", "==", summoner_id).get()

    elif username is not None and tag is not None and region is not None:
        account_doc = (
            collection.where("username", "==", username)
            .where("tag", "==", tag)
            .where("region", "==", region)
            .get()
        )

    else:
        return None

    if not account_doc.exists:
        return None

    model = models.Account(**account_doc.to_dict())

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
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
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
            client, region, account_details["puuid"]
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

    db_functions.add_document("accounts", model.model_dump())

    return model
