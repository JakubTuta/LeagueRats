import typing

import constants
import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/pro-players")


@router.get(
    "/players",
    response_model=(dict[str, dict[str, list[models.ProPlayer]]]),
    status_code=200,
)
async def get_pro_players(
    region: typing.Optional[typing.Literal["LCK", "LEC", "LCS", "LPL"]] = None,
    team: typing.Optional[str] = None,
    player: typing.Optional[str] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> dict[str, dict[str, typing.List[models.ProPlayer]]]:
    """
    Query patterns:
    - No params: Get all players (all regions, all teams)
    - ?region=LCK: Get all teams in LCK
    - ?region=LCK&team=T1: Get all players in T1
    - ?region=LCK&team=T1&player=faker: Get specific player (use /players/{region}/{team}/{player} instead)
    """
    logger.info(
        "get_pro_players_endpoint_called",
        region=region,
        team=team,
        player=player,
    )

    if player and not (region and team):
        raise fastapi.HTTPException(
            status_code=400,
            detail="Player parameter requires both region and team parameters",
        )

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    result = await pro_player_service.get_players(
        region=region, team=team, player=player
    )

    if not result:
        raise fastapi.HTTPException(status_code=404, detail="Players not found")

    return result


@router.post(
    "/players",
    response_model=models.ProPlayer,
    status_code=201,
)
async def create_pro_player(
    player: models.ProPlayer,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    region: typing.Optional[constants.Region] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> models.ProPlayer:
    logger.info(
        "create_pro_player_endpoint_called",
        player=player.player,
        team=player.team,
        region=player.region,
    )

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    created_player = await pro_player_service.create_or_update_player(
        player=player,
        riot_api=riot_api,
        username=username,
        tag=tag,
        region=region.value if region else None,
    )

    return created_player


@router.put(
    "/players/transfer",
    response_model=models.ProPlayer,
    status_code=200,
)
async def transfer_player(
    player: str = fastapi.Query(..., description="Player name"),
    from_team: str = fastapi.Query(..., description="Source team", alias="fromTeam"),
    to_team: str = fastapi.Query(..., description="Destination team", alias="toTeam"),
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> models.ProPlayer:
    logger.info(
        "transfer_player_endpoint_called",
        player=player,
        from_team=from_team,
        to_team=to_team,
    )

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    if (
        transferred_player := await pro_player_service.transfer_player(
            player_name=player, from_team=from_team, to_team=to_team
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Player not found")

    return transferred_player


@router.get(
    "/account-names",
    response_model=typing.Dict[str, typing.Dict[str, str]],
    status_code=200,
)
async def get_account_names(
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> typing.Dict[str, typing.Dict[str, str]]:
    """Get pro player account names mapping."""
    logger.info("get_account_names_endpoint_called")

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    account_names = await pro_player_service.get_account_names()

    if not account_names:
        raise fastapi.HTTPException(status_code=404, detail="Account names not found")

    return account_names


@router.get(
    "/live-streams/{live}",
    response_model=typing.Dict[str, typing.Dict[str, str]],
    status_code=200,
)
async def get_live_streams(
    live: bool,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> typing.Dict[str, typing.Dict[str, str]]:
    """Get live or not-live streams based on path parameter."""
    logger.info("get_live_streams_endpoint_called", live=live)

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    streams = await pro_player_service.get_live_streams(live=live)

    if not streams:
        raise fastapi.HTTPException(status_code=404, detail="Live streams not found")

    return streams


@router.get(
    "/history-stats/{team}/{player}",
    response_model=typing.Dict[int, models.ChampionStats],
    status_code=200,
)
async def get_pro_player_history_stats(
    team: str,
    player: str,
    amount: int = fastapi.Query(
        20, ge=1, le=100, description="Number of matches to analyze"
    ),
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> typing.Dict[int, models.ChampionStats]:
    """Get aggregated champion statistics from a pro player's recent match history."""
    logger.info(
        "get_pro_player_history_stats_endpoint_called",
        team=team,
        player=player,
        amount=amount,
    )

    pro_player_service = service.ProPlayerService(firestore=firestore, redis=redis)

    history_stats = await pro_player_service.get_player_history_stats(
        team=team, player=player, amount=amount, riot_api=riot_api
    )

    if not history_stats:
        raise fastapi.HTTPException(
            status_code=404, detail="Player history stats not found"
        )

    return history_stats
