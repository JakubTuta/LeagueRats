import typing

import pro_players.models as pro_players_models
from google.cloud.firestore_v1.types.write import WriteResult

from . import database


def add_or_update_document(
    collection_name: str, document_data: dict, document_id: typing.Optional[str] = None
) -> None | WriteResult | typing.Tuple[typing.Any, typing.Any]:
    if (collection := database.get_collection(collection_name)) is None:
        return

    if document_id is not None:
        document = collection.document(document_id)
        created_document = document.set(document_data)

        return created_document

    if (puuid := document_data.get("puuid", None)) is not None:
        document = collection.document(puuid)
        created_document = document.set(document_data)

        return created_document

    created_document = collection.add(document_data)

    return created_document


def get_document(
    collection_name: str, document_id: str
) -> typing.Optional[typing.Union[list, dict]]:
    if (collection := database.get_collection(collection_name)) is None:
        return None

    document_ref = collection.document(document_id)
    document = document_ref.get()

    return document.to_dict() if document.exists else None


def delete_document(collection_name: str, document_id: str) -> bool:
    if (collection := database.get_collection(collection_name)) is None:
        return False

    if not (document := collection.document(document_id)).get().exists:
        return False

    document.delete()

    return True


def get_pro_team_documents(
    region: typing.Literal["LEC", "LCS", "LPL", "LCK"], team: str
) -> typing.List[pro_players_models.ProPlayer]:
    if (collection := database.get_collection(f"pro_players/{region}/{team}")) is None:
        return []

    player_docs = collection.stream()

    return [pro_players_models.ProPlayer(**player.to_dict()) for player in player_docs]
