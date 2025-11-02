import typing

import fastapi
from account import functions as account_functions

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/champions")


@router.get(
    "/", response_model=typing.Dict[str, typing.Dict[str, str]], status_code=200
)
async def get_champions() -> typing.Dict[str, typing.Dict[str, str]]:
    if (champions := functions.get_champions()) is None:
        raise fastapi.HTTPException(status_code=404, detail="Champions not found")

    return champions


@router.get(
    "/{champion_id}/stats", response_model=typing.Dict[str, int], status_code=200
)
async def get_champion_stats(champion_id: str) -> typing.Dict[str, int]:
    if (champion_stats := functions.get_champion_stats(champion_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Champion stats not found")

    return champion_stats


@router.get(
    "/{champion_id}/matches",
    response_model=typing.Optional[typing.List[models.ChampionHistory]],
    status_code=200,
)
async def get_champion_matches(
    champion_id: str,
    startAfter: typing.Optional[str] = None,
    limit: int = 10,
    lane: typing.Optional[str] = None,
    versus: typing.Optional[str] = None,
) -> typing.List[models.ChampionHistory]:
    if (
        champion_matches := functions.get_champion_matches(
            champion_id, startAfter, limit, lane, versus
        )
    ) is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Champion matches not found"
        )

    return champion_matches


@router.get(
    "/positions/{champion_ids}",
    response_model=typing.Dict[str, str],
    status_code=200,
)
async def get_champion_positions(
    request: fastapi.Request, champion_ids: str
) -> typing.Dict[str, str]:
    if not "." in champion_ids:
        raise fastapi.HTTPException(
            status_code=400, detail='Champion ids must be separated by a "."'
        )

    split_champion_ids = champion_ids.split(".")
    client = request.app.state.httpx_client

    if (
        champion_positions := await functions.get_champion_positions(
            client, split_champion_ids
        )
    ) is None:
        raise fastapi.HTTPException(status_code=500, detail="Internal server error")

    return champion_positions


@router.get(
    "/mastery/{puuid}",
    response_model=typing.List[models.ChampionMastery],
    status_code=200,
)
async def get_champion_mastery(
    request: fastapi.Request, puuid: str
) -> typing.List[models.ChampionMastery]:
    httpx_client = request.app.state.httpx_client

    if (
        account := await account_functions.get_account(
            httpx_client, puuid=puuid, save_account=True
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    mastery = await functions.get_champion_mastery(httpx_client, puuid, account.region)

    return mastery
