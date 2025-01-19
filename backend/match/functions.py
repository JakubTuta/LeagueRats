import typing

import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx

from . import models


async def get_active_match(
    client: httpx.AsyncClient, region: str, puuid: str
) -> typing.Optional[models.ActiveMatch]:
    if (row_regions := regions.get_region(region)) is None:
        return None

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            model = models.ActiveMatch(**response.json())
            print(model)

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

            return model

    except Exception as e:
        pass
