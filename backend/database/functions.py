import typing

import account.models as account_models

from . import database


def clear_collection(collection_name: str):
    firestore_client = database.get_firestore_client()

    if firestore_client is None:
        return

    collection_ref = firestore_client.collection(collection_name)
    docs = collection_ref.stream()

    for doc in docs:
        doc.reference.delete()


def is_document_in_collection(collection_name: str, document_id: str) -> bool:
    collection = database.get_collection(collection_name)
    document = collection.document(document_id)

    return document.get().exists


def add_or_update_document(
    collection_name: str, document_data: dict, document_id: typing.Optional[str] = None
):
    collection = database.get_collection(collection_name)

    if document_id is not None:
        document = collection.document(document_id)
        document.set(document_data)

        return

    if (puuid := document_data.get("puuid", None)) is not None:
        document = collection.document(puuid)
        document.set(document_data)

        return

    collection.add(document_data)


def get_document(collection_name: str, document_id: str) -> typing.Optional[dict]:
    collection = database.get_collection(collection_name)
    document_ref = collection.document(document_id)
    document = document_ref.get()

    return document.to_dict() if document.exists else None


def get_pro_team_documents(
    region: typing.Literal["LEC", "LCS", "LPL", "LCK"], team: str
) -> typing.List[typing.Dict[str, typing.Any]]:
    firestore_client = database.get_firestore_client()

    if firestore_client is None:
        return []

    player_docs = firestore_client.collection(f"pro_players/{region}/{team}").stream()

    return [player.to_dict() for player in player_docs]


def save_leaderboard_accounts(
    region: str, rank: str, accounts: typing.List[account_models.LeaderboardAccount]
):
    firestore_client = database.get_firestore_client()

    if firestore_client is None:
        return

    collection_ref = firestore_client.collection(f"leaderboard/{region}/{rank}")

    for account in accounts:
        if account.puuid:
            collection_ref.document(account.puuid).set(account.model_dump())
