import typing

import fastapi

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/account")


@router.get(
    "/",
    response_model=models.Account,
    status_code=200,
)
async def get_account(
    request: fastapi.Request,
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> models.Account:

    httpx_client = request.app.httpx_client

    if (
        account := await functions.get_account(
            httpx_client,
            region=region,
            username=username,
            tag=tag,
            puuid=puuid,
            save_account=True,
        )
    ) is not None:
        return account

    raise fastapi.HTTPException(status_code=404, detail="Account not found")


@router.post("/", response_model=models.Account, status_code=201)
async def create_account(
    request: fastapi.Request,
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> models.Account:

    httpx_client = request.app.httpx_client

    if (
        created_account := await functions.get_account(
            httpx_client,
            region=region,
            username=username,
            tag=tag,
            puuid=puuid,
            save_account=True,
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    return created_account


@router.get(
    "/all-regions/{username}/{tag}",
    response_model=typing.Dict[str, typing.Optional[models.Account]],
    status_code=200,
)
async def get_accounts_in_all_regions(
    request: fastapi.Request,
    username: str,
    tag: str,
) -> typing.Dict[str, typing.Optional[models.Account]]:

    httpx_client = request.app.httpx_client

    found_accounts = await functions.get_accounts_in_all_regions(
        httpx_client, username, tag
    )

    return found_accounts
