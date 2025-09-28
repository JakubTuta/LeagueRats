import typing

import database.database as db
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx

from . import models


async def get_league_entries(
    client: httpx.AsyncClient,
    region: str,
    puuid: str,
) -> typing.List[models.LeagueEntry]:
    if (row_regions := regions.get_region(region)) is None:
        return []

    request_region = row_regions[1].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"

    try:
        response = await client.get(request_url, headers=riot_api.get_headers())

        if response.status_code == 200:
            return [models.LeagueEntry(**entry) for entry in response.json()]

    except:
        pass

    return []


def get_leaderboard(
    region: str, limit: int = 100, page: int = 1
) -> typing.Optional[typing.List[models.LeaderboardEntry]]:
    collection = db.get_collection(f"leaderboard/{region}/CHALLENGER")

    if collection is None:
        return None

    query = (
        collection.order_by("rank", direction="ASCENDING")
        .limit(limit)
        .offset((page - 1) * limit)
    )

    return [models.LeaderboardEntry(**doc.to_dict()) for doc in query.stream()]
