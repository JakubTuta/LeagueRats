import typing

import database.functions as db_functions

from . import models


def get_runes_info() -> typing.Optional[typing.List[models.Rune]]:
    document = db_functions.get_document("help", "runes1")

    if not isinstance(document, dict):
        return None

    return [models.Rune(**rune) for rune in document.get("data", [])]
