import typing

import account.functions as account_functions
import fastapi

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/match")


@router.get(
    "/active/{region}/{puuid}",
    response_model=typing.Optional[models.ActiveMatch],
    status_code=200,
)
async def get_active_game(
    request: fastapi.Request,
    region: str,
    puuid: str,
) -> typing.Optional[models.ActiveMatch]:

    httpx_client = request.app.httpx_client

    if (
        active_match := await functions.get_active_match(httpx_client, region, puuid)
    ) is not None:
        return active_match

    raise fastapi.HTTPException(status_code=404, detail="Active match not found")


@router.get(
    "/history/{puuid}",
    response_model=typing.List[str],
    status_code=200,
)
async def get_match_history(
    request: fastapi.Request,
    puuid: str,
    startTime: typing.Optional[str] = None,
    endTime: typing.Optional[str] = None,
    queue: typing.Optional[str] = None,
    type: typing.Optional[str] = None,
    start: int = 0,
    count: int = 20,
) -> typing.List[str]:

    httpx_client = request.app.httpx_client

    if (
        account := await account_functions.get_account(httpx_client, puuid=puuid)
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    query_params = {
        "startTime": startTime,
        "endTime": endTime,
        "queue": queue,
        "type": type,
        "start": start,
        "count": count,
    }

    match_history = await functions.get_match_history(
        httpx_client,
        account.region,
        puuid,
        query_params,
    )

    return match_history


@router.get(
    "/history/match-data/{match_id}",
    response_model=models.MatchHistory,
    status_code=200,
)
async def get_match_data(
    request: fastapi.Request, match_id: str
) -> models.MatchHistory:
    httpx_client = request.app.httpx_client

    if (
        match_data := await functions.get_match_data(httpx_client, match_id)
    ) is not None:
        return match_data

    raise fastapi.HTTPException(status_code=404, detail="Match not found")
