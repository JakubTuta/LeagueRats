import typing

import fastapi

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/pro-players")


@router.get(
    "/accounts/",
    response_model=typing.Dict[str, typing.Dict[str, typing.List[models.ProPlayer]]],
    status_code=200,
)
async def get_all_pro_players() -> (
    typing.Dict[str, typing.Dict[str, typing.List[models.ProPlayer]]]
):
    if (players := await functions.get_all_players()) == []:
        raise fastapi.HTTPException(status_code=404, detail="Players not found")

    return players


@router.post("/accounts/", response_model=models.ProPlayer, status_code=201)
async def create_pro_player(
    request: fastapi.Request,
    player: models.ProPlayer,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    region: typing.Optional[str] = None,
) -> models.ProPlayer:
    client = request.app.state.httpx_client

    account_data = None
    if username is not None and tag is not None and region is not None:
        account_data = {
            "username": username,
            "tag": tag,
            "region": region,
        }

    await functions.create_or_update_player(client, player, account_data)

    return player


@router.get(
    "/accounts/{region}",
    response_model=typing.Dict[str, typing.List[models.ProPlayer]],
    status_code=200,
)
async def get_pro_players(
    region: str,
) -> typing.Dict[str, typing.List[models.ProPlayer]]:
    if (players := await functions.get_players_for_region(region)) == {}:
        raise fastapi.HTTPException(status_code=404, detail="Region not found")

    return players


@router.get(
    "/accounts/{region}/{team}",
    response_model=typing.List[models.ProPlayer],
    status_code=200,
)
async def get_pro_players_by_team(
    region: str, team: str
) -> typing.List[models.ProPlayer]:
    if (players := await functions.get_players_for_team(region, team)) == []:
        raise fastapi.HTTPException(status_code=404, detail="Team not found")

    return players


@router.get(
    "/accounts/{region}/{team}/{player}",
    response_model=models.ProPlayer,
    status_code=200,
)
async def get_pro_player(region: str, team: str, player: str) -> models.ProPlayer:
    if (found_player := await functions.get_player(region, team, player)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Player not found")

    return found_player


@router.get(
    "/account-names",
    response_model=typing.Dict[str, typing.Dict[str, str]],
    status_code=200,
)
async def get_pro_account_names() -> typing.Dict[str, typing.Dict[str, str]]:
    if (account_names := functions.get_account_names()) is None or account_names == {}:
        raise fastapi.HTTPException(status_code=404, detail="Account names not found")

    return account_names


@router.get(
    "/bootcamp/leaderboard",
    response_model=typing.List[models.BootcampAccount],
    status_code=200,
)
async def get_bootcamp_accounts() -> typing.List[models.BootcampAccount]:
    if (accounts := functions.get_bootcamp_accounts()) == []:
        raise fastapi.HTTPException(
            status_code=404, detail="Bootcamp accounts not found"
        )

    return accounts


@router.get(
    "/live-streams",
    response_model=typing.Dict[str, typing.Dict[str, str]],
    status_code=200,
)
async def get_live_streams() -> typing.Dict[str, typing.Dict[str, str]]:
    if (streams := functions.get_live_streams()) is None or streams == {}:
        raise fastapi.HTTPException(status_code=404, detail="Live streams not found")

    return streams


@router.get(
    "/not-live-streams",
    response_model=typing.Dict[str, typing.Dict[str, str]],
    status_code=200,
)
async def get_not_live_streams() -> typing.Dict[str, typing.Dict[str, str]]:
    if (streams := functions.get_not_live_streams()) is None or streams == {}:
        raise fastapi.HTTPException(
            status_code=404, detail="Not live streams not found"
        )

    return streams


@router.put(
    "/transfer/{player}/from/{fromTeam}/to/{toTeam}",
    response_model=models.ProPlayer,
    status_code=200,
)
async def transfer_player(player: str, fromTeam: str, toTeam: str) -> models.ProPlayer:
    if (
        updated_player := await functions.transfer_player(player, fromTeam, toTeam)
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Player not found")

    return updated_player


@router.get(
    "/history-stats/{team}/{player}",
    response_model=typing.Dict[int, models.ChampionStats],
    status_code=200,
)
async def get_pro_player_history_stats(
    request: fastapi.Request, team: str, player: str, amount: int = 20
) -> typing.Dict[int, models.ChampionStats]:
    httpx_client = request.app.state.httpx_client

    if (
        history_stats := await functions.get_player_history_stats(
            httpx_client, team, player, amount
        )
    ) == {}:
        raise fastapi.HTTPException(
            status_code=404, detail="Player history stats not found"
        )

    return history_stats
