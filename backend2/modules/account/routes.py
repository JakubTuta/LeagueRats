import typing

import fastapi
import structlog
import utils

from . import models, service

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter(prefix="/v2/account")


@router.get(
    "/",
    response_model=models.Account,
    status_code=200,
)
async def get_account(
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> models.Account:
    logger.info(
        "get_account_endpoint_called",
        region=region,
        username=username,
        tag=tag,
        puuid=puuid,
    )

    account_service = service.AccountService(firestore, redis, riot_api)
    if (
        account := await account_service.get_account(
            puuid=puuid,
            username=username,
            tag=tag,
            region=region,
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    return account


@router.get(
    "/all-regions/{username}/{tag}",
    response_model=dict[str, typing.Optional[models.Account]],
    status_code=200,
)
async def get_accounts_in_all_regions(
    username: str,
    tag: str,
    redis: utils.RedisClient = fastapi.Depends(utils.get_redis_client),
    firestore: utils.FirestoreClient = fastapi.Depends(utils.get_firestore_client),
    riot_api: utils.RiotAPIClient = fastapi.Depends(utils.get_riot_api_client),
) -> dict[str, typing.Optional[models.Account]]:
    logger.info(
        "get_accounts_in_all_regions_endpoint_called",
        username=username,
        tag=tag,
    )

    account_service = service.AccountService(firestore, redis, riot_api)
    accounts_in_all_regions = await account_service.get_accounts_in_all_regions(
        username=username,
        tag=tag,
    )

    if not accounts_in_all_regions:
        raise fastapi.HTTPException(
            status_code=404, detail="Accounts not found in any region"
        )

    return accounts_in_all_regions
