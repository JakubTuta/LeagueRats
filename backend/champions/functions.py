import typing

import database.database as db
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx
import match.models as match_models

from . import models


def get_champions() -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]:
    response = db_functions.get_document("help", "champions")

    if not isinstance(response, dict):
        return None

    return response


def get_champion_stats(champion_id: str) -> typing.Optional[typing.Dict[str, int]]:
    response = db_functions.get_document("champion_history", champion_id)

    if not isinstance(response, dict):
        return None

    return {
        "games": response.get("games", 0),
        "wins": response.get("wins", 0),
        "losses": response.get("losses", 0),
    }


def get_champion_matches(
    champion_id: str,
    start_after: typing.Optional[str],
    limit: int,
    lane: typing.Optional[str],
    versus: typing.Optional[str],
) -> typing.Optional[typing.List[models.ChampionHistory]]:
    collection = db.get_collection(f"champion_history/{champion_id}/matches")

    if collection is None:
        return None

    query = collection.order_by("match.info.gameStartTimestamp", direction="DESCENDING")

    if start_after is not None and (
        (start_after_match := collection.document(start_after).get()).exists
    ):
        query = query.start_after(start_after_match)

    if lane is not None:
        query = query.where("lane", "==", lane.upper())

    if versus is not None:
        query = query.where("enemy", "==", int(versus))

    query = query.limit(limit)

    matches = [models.ChampionHistory(**match.to_dict()) for match in query.stream()]

    return matches[:limit] if matches else None


def find_highest_playrate_role(champion_data: dict, champion_id: str) -> str:
    roles = champion_data.get(champion_id, None)

    if not roles:
        return "TOP"

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
) -> typing.Optional[typing.Dict[str, str]]:
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
