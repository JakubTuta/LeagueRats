import typing

import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx

from . import models


def find_highest_playrate_role(
    champion_data: dict, champion_id: str
) -> typing.Optional[str]:
    roles = champion_data.get(champion_id, None)

    if not roles:
        return None

    highest_playrate_role = list(roles.keys())[0]
    highest_playrate = 0

    for role, stats in roles.items():
        play_rate = stats.get("playRate", 0)
        if play_rate > highest_playrate:
            highest_playrate = play_rate
            highest_playrate_role = role

    return highest_playrate_role


async def get_champion_positions(
    client: httpx.AsyncClient, champion_ids: typing.List[str]
) -> typing.Optional[typing.Dict[str, typing.Optional[str]]]:
    champion_data_request_url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

    try:
        response = await client.get(champion_data_request_url)

        champion_data = response.json().get("data", None)

    except:
        return None

    if champion_data is None:
        return None

    champion_positions = {
        champion_id: find_highest_playrate_role(champion_data, champion_id)
        for champion_id in champion_ids
    }

    return champion_positions


async def get_champion_mastery(
    client: httpx.AsyncClient,
    puuid: str,
    region: str,
) -> typing.List[models.ChampionMastery]:
    if (row_regions := regions.get_region(region)) is None:
        return []

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return [models.ChampionMastery(**champion) for champion in response.json()]

    except:
        pass

    return []
