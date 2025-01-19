import typing

import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx

from . import models


async def get_league_entries(
    client: httpx.AsyncClient,
    region: str,
    encrypted_summoner_id: str,
) -> typing.List[models.LeagueEntry]:
    if (row_regions := regions.get_region(region)) is None:
        return []

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return [models.LeagueEntry(**entry) for entry in response.json()]

    except:
        pass

    return []
