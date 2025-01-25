import typing

import fastapi
from account import functions as account_functions

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/league")


@router.get(
    "/{puuid}",
    response_model=typing.List[models.LeagueEntry],
    status_code=200,
)
async def get_league_entries(
    request: fastapi.Request, puuid: str
) -> typing.List[models.LeagueEntry]:
    httpx_client = request.app.httpx_client

    if (
        account := await account_functions.get_account(
            httpx_client, puuid=puuid, save_account=True
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    league_entries = await functions.get_league_entries(
        httpx_client, account.region, account.id
    )

    return league_entries


@router.get(
    "/leaderboard/{region}", response_model=typing.List[models.LeaderboardEntry]
)
async def get_leaderboard(
    region: str, limit: int = 100, page: int = 1
) -> typing.List[models.LeaderboardEntry]:
    if (leaderboard := functions.get_leaderboard(region, limit, page)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Leaderboard not found")

    return leaderboard
