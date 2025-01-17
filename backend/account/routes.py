import typing

import fastapi

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/account")


@router.get("/", response_model=models.Account)
async def get_account(
    request: fastapi.Request,
    region: typing.Optional[str] = None,
    username: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
    puuid: typing.Optional[str] = None,
) -> models.Account:
    if database_account := functions.get_account_from_database(
        region=region, username=username, tag=tag, puuid=puuid
    ):
        return database_account

    try:
        httpx_client = request.app.httpx_client
        if api_account := await functions.get_account_from_api(
            httpx_client,
            region=region,
            username=username,
            tag=tag,
            puuid=puuid,
        ):
            return api_account

        raise fastapi.HTTPException(status_code=404, detail="Account not found")

    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
