import typing

import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/champions")


@router.get(
    "/list",
    response_model=dict[int, models.ChampionName],
    status_code=200,
)
async def list_champions(
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> dict[int, models.ChampionName]:
    logger.info("list_champions_endpoint_called")

    champion_service = service.ChampionService(firestore=firestore, redis=redis)
    champions = await champion_service.get_champions_names()

    if not champions:
        raise fastapi.HTTPException(status_code=404, detail="No champions found")

    return champions


@router.get(
    "/{champion_id}/stats",
    response_model=models.ChampionStats,
    status_code=200,
)
async def get_champion_stats(
    champion_id: int,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> models.ChampionStats:
    logger.info("get_champion_stats_endpoint_called", champion_id=champion_id)

    champion_service = service.ChampionService(firestore=firestore, redis=redis)
    champion_stats = await champion_service.get_champion_stats(champion_id)

    if champion_stats is None:
        raise fastapi.HTTPException(status_code=404, detail="Champion stats not found")

    return champion_stats


@router.get(
    "/{champion_id}/matches",
    response_model=list[models.ChampionHistory],
    status_code=200,
)
async def get_champion_matches(
    champion_id: int,
    start_after: typing.Optional[str] = None,
    limit: int = fastapi.Query(10, ge=1, le=100),
    lane: typing.Optional[str] = None,
    versus: typing.Optional[str] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> list[models.ChampionHistory]:
    logger.info(
        "get_champion_matches_endpoint_called",
        champion_id=champion_id,
        limit=limit,
        lane=lane,
        versus=versus,
    )

    champion_service = service.ChampionService(firestore=firestore, redis=redis)
    champion_matches = await champion_service.get_champion_matches(
        champion_id, start_after, limit, lane, versus
    )

    if not champion_matches:
        raise fastapi.HTTPException(
            status_code=404, detail="Champion matches not found"
        )

    return champion_matches


@router.get(
    "/positions/{champion_ids}",
    response_model=dict[str, str],
    status_code=200,
)
async def get_champion_positions(
    champion_ids: str,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    http: utils.HTTPClient = fastapi.Depends(utils.get_http_client),
) -> dict[str, str]:
    logger.info("get_champion_positions_endpoint_called", champion_ids=champion_ids)

    champion_id_list = []
    for champion_id in champion_ids.split("."):
        try:
            champion_id_list.append(int(champion_id))
        except ValueError:
            raise fastapi.HTTPException(
                status_code=400, detail=f"Invalid champion ID: {champion_id}"
            )

    if not champion_id_list:
        raise fastapi.HTTPException(
            status_code=400, detail="At least one valid champion ID must be provided"
        )

    champion_service = service.ChampionService(redis=redis, firestore=firestore)
    champion_positions = await champion_service.get_champion_positions(
        http=http, champion_ids=champion_id_list
    )

    if not champion_positions:
        raise fastapi.HTTPException(
            status_code=404, detail="Champion positions not found"
        )

    return champion_positions


@router.get(
    "/mastery/{puuid}",
    response_model=list[models.ChampionMastery],
    status_code=200,
)
async def get_champions_mastery(
    puuid: str,
    region: typing.Optional[str] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api_client: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> list[models.ChampionMastery]:
    logger.info("get_champions_mastery_endpoint_called", puuid=puuid, region=region)

    if region is None:
        raise fastapi.HTTPException(
            status_code=400, detail="Region query parameter is required"
        )

    champion_service = service.ChampionService(firestore=firestore, redis=redis)
    champions_mastery = await champion_service.get_champions_mastery(
        puuid, region, riot_api_client
    )

    if not champions_mastery:
        raise fastapi.HTTPException(
            status_code=404, detail="Champion mastery not found"
        )

    return champions_mastery
