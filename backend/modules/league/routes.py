import constants
import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/league")


@router.get(
    "/{puuid}",
    response_model=list[models.LeagueEntry],
    status_code=200,
)
async def get_league_entries(
    puuid: str,
    region: constants.Region = fastapi.Query(..., description="Region of the player"),
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> list[models.LeagueEntry]:
    logger.info("get_league_entries_endpoint_called", puuid=puuid, region=region)

    league_service = service.LeagueService(
        redis_client=redis, firestore_client=firestore
    )
    league_entries = await league_service.fetch_league_entries(
        puuid=puuid, region=region.value, riot_api=riot_api
    )

    if not league_entries:
        raise fastapi.HTTPException(status_code=404, detail="League entries not found")

    return league_entries


@router.get(
    "/leaderboard/{region}",
    response_model=list[models.LeaderboardEntry],
    status_code=200,
)
async def get_leaderboard(
    region: constants.Region,
    limit: int = fastapi.Query(100, ge=1, le=500),
    page: int = fastapi.Query(1, ge=1),
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> list[models.LeaderboardEntry]:
    logger.info(
        "get_leaderboard_endpoint_called", region=region, limit=limit, page=page
    )

    league_service = service.LeagueService(
        redis_client=redis, firestore_client=firestore
    )
    leaderboard = await league_service.get_leaderboard(
        region=region.value, limit=limit, page=page
    )

    logger.info("leaderboard", leaderboard=leaderboard)

    if not leaderboard:
        raise fastapi.HTTPException(status_code=404, detail="Leaderboard not found")

    return leaderboard
