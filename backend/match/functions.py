import asyncio
import datetime
import typing

import account.functions as account_functions
import account.models as account_models
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx
import match.models as match_models

from . import models


async def get_active_match(
    client: httpx.AsyncClient, puuid: str
) -> typing.Optional[models.ActiveMatch]:
    if (account := await account_functions.get_account(client, puuid=puuid)) is None:
        return None

    if (row_regions := regions.get_region(account.region)) is None:
        return None

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            model = models.ActiveMatch(**response.json())

            return model

    except:
        pass


async def get_match_history(
    client: httpx.AsyncClient,
    region: str,
    puuid: str,
    query_params: typing.Dict[str, typing.Union[str, int, None]],
) -> typing.List[str]:
    if (row_regions := regions.get_region(region)) is None:
        return []

    request_region = row_regions[2].lower()

    string_params = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    request_url = f"https://{request_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?{string_params}"
    print(request_url)
    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return response.json()

    except:
        pass

    return []


async def get_match_data(
    client: httpx.AsyncClient,
    match_id: str,
) -> typing.Optional[models.MatchHistory]:
    region = match_id.split("_")[0]
    if (row_regions := regions.get_region(region)) is None:
        return None

    request_region = row_regions[2].lower()
    request_url = (
        f"https://{request_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    )

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            model = models.MatchHistory(**response.json())

            db_functions.add_or_update_document(
                "match_history",
                model.model_dump(),
                document_id=model.metadata.matchId,
            )

            return model

    except:
        pass


async def get_ranked_matches_from_period(
    client: httpx.AsyncClient, account: account_models.Account, hours: int
) -> typing.List[match_models.MatchHistory]:
    now = datetime.datetime.now()
    past = now - datetime.timedelta(hours=hours)

    match_ids_query_params = {
        "count": 100,
        "queue": 420,
        "type": "ranked",
        "startTime": int(past.timestamp()),
        "endTime": int(now.timestamp()),
    }

    match_ids = await get_match_history(
        client, account.region, account.puuid, match_ids_query_params
    )

    jobs = [get_match_data(client, match_id) for match_id in match_ids]

    responses = await asyncio.gather(*jobs)

    matches = list(filter(None, responses))

    return matches
