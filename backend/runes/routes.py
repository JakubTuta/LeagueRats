import typing

import fastapi

from . import functions, models

router = fastapi.APIRouter(prefix="/v2/runes")


@router.get("/", response_model=typing.List[models.Rune], status_code=200)
async def get_all_runes() -> typing.List[models.Rune]:
    if (runes := functions.get_runes_info()) is None:
        raise fastapi.HTTPException(status_code=404, detail="Runes not found")

    return runes
