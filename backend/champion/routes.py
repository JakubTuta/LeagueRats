import typing

import fastapi
from account import functions as account_functions

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/champions")


@router.get(
    "/positions/{champion_ids}",
    response_model=typing.Optional[typing.Dict[str, typing.Optional[str]]],
    status_code=200,
)
async def get_champion_positions(request: fastapi.Request, champion_ids: str):
    if not "." in champion_ids:
        raise fastapi.HTTPException(
            status_code=400, detail='Champion ids must be separated by a "."'
        )

    split_champion_ids = champion_ids.split(".")
    client = request.app.httpx_client

    if (
        champion_positions := await functions.get_champion_positions(
            client, split_champion_ids
        )
    ) is None:
        raise fastapi.HTTPException(status_code=500, detail="Internal server error")

    return champion_positions


@router.get(
    "/mastery/{puuid}",
    # response_model=typing.List[models.ChampionMastery],
    status_code=200,
)
async def get_champion_mastery(
    request: fastapi.Request, puuid: str
) -> typing.List[models.ChampionMastery]:
    httpx_client = request.app.httpx_client

    if (
        account := await account_functions.get_account(
            httpx_client, puuid=puuid, save_account=True
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    mastery = await functions.get_champion_mastery(httpx_client, puuid, account.region)

    return mastery
