import typing

import constants
import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/match")


@router.get(
    "/active/{puuid}",
    response_model=models.ActiveMatch,
    status_code=200,
)
async def get_active_game(
    puuid: str,
    region: constants.Region = fastapi.Query(..., description="Region of the player"),
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> models.ActiveMatch:
    logger.info("get_active_game_endpoint_called", puuid=puuid, region=region)

    match_service = service.MatchService(
        redis_client=redis, firestore_client=firestore, riot_api=riot_api
    )
    active_match = await match_service.get_active_match(
        puuid=puuid, region=region.value
    )

    if not active_match:
        raise fastapi.HTTPException(status_code=404, detail="Active match not found")

    return active_match


@router.get(
    "/history/batch/{puuid}",
    response_model=list[models.MatchHistory],
    status_code=200,
)
async def get_match_history_batch(
    puuid: str,
    start: int = fastapi.Query(0, ge=0),
    count: int = fastapi.Query(20, ge=1, le=100),
    region: constants.Region = fastapi.Query(..., description="Region of the player"),
    startTime: typing.Optional[str] = None,
    endTime: typing.Optional[str] = None,
    queue: typing.Optional[str] = None,
    type: typing.Optional[str] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> list[models.MatchHistory]:
    logger.info(
        "get_match_history_batch_endpoint_called",
        puuid=puuid,
        region=region,
        start=start,
        count=count,
        startTime=startTime,
        endTime=endTime,
        queue=queue,
        type=type,
    )

    match_service = service.MatchService(
        redis_client=redis, firestore_client=firestore, riot_api=riot_api
    )
    match_history = await match_service.get_match_history(
        puuid=puuid,
        region=region.value,
        start=start,
        count=count,
        startTime=startTime,
        endTime=endTime,
        queue=queue,
        type=type,
    )

    if not match_history:
        raise fastapi.HTTPException(status_code=404, detail="Match history not found")

    return match_history
