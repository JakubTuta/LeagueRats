import typing

import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/runes")


@router.get("/", response_model=typing.List[models.Rune], status_code=200)
async def get_all_runes(
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
) -> typing.List[models.Rune]:
    """Get all runes information."""
    logger.info("get_all_runes_endpoint_called")

    runes_service = service.RunesService(firestore=firestore, redis=redis)

    runes = await runes_service.get_runes()

    if not runes:
        raise fastapi.HTTPException(status_code=404, detail="Runes not found")

    return runes
