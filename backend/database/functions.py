import typing

import league.models as league_models
import pro_players.models as pro_players_models
from google.cloud import firestore
from google.cloud.firestore_v1.types.write import WriteResult

from . import database


def clear_collection(collection_name: str):
    if (collection := database.get_collection(collection_name)) is None:
        return

    docs = collection.stream()

    for doc in docs:
        doc.reference.delete()


def is_document_in_collection(collection_name: str, document_id: str) -> bool:
    if (collection := database.get_collection(collection_name)) is None:
        return False

    document = collection.document(document_id)

    return document.get().exists


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


def rename_collection(old_collection_name: str, new_collection_name: str) -> None:
    if (old_collection := database.get_collection(old_collection_name)) is None:
        return

    if (new_collection := database.get_collection(new_collection_name)) is None:
        return

    docs = old_collection.stream()

    for doc in docs:
        new_collection.document(doc.id).set(doc.to_dict())
        doc.reference.delete()


def get_pro_team_documents(
    region: typing.Literal["LEC", "LCS", "LPL", "LCK"], team: str
) -> typing.List[pro_players_models.ProPlayer]:
    if (collection := database.get_collection(f"pro_players/{region}/{team}")) is None:
        return []

    player_docs = collection.stream()

    return [pro_players_models.ProPlayer(**player.to_dict()) for player in player_docs]


def save_leaderboard_accounts(
    region: str, rank: str, accounts: typing.List[league_models.LeaderboardEntry]
):
    if (collection := database.get_collection(f"leaderboard/{region}/{rank}")) is None:
        return

    for account in accounts:
        if account.puuid:
            collection.document(account.puuid).set(account.model_dump())


def update_champion_history(all_champions_data: dict):
    if (collection := database.get_collection("champion_history")) is None:
        return

    for champion_id, champion_data in all_champions_data.items():
        champion_reference = collection.document(str(champion_id))
        champion_document = champion_reference.get()

        if (
            champion_document.exists
            and (document_data := champion_document.to_dict()) is not None
        ):
            document_data.update(
                {
                    "games": firestore.Increment(champion_data["stats"]["games"]),
                    "wins": firestore.Increment(champion_data["stats"]["wins"]),
                    "losses": firestore.Increment(champion_data["stats"]["losses"]),
                }
            )

        else:
            champion_reference.set(champion_data["stats"])

        champion_matches_collection = database.get_collection(
            f"champion_history/{str(champion_id)}/matches"
        )

        if champion_matches_collection is not None:
            for match in champion_data["matches"]:
                champion_matches_collection.document(
                    match["match"]["metadata"]["matchId"]
                ).set(match)
